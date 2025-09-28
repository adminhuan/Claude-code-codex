"""
OpenAI代理实现
按照Codex建议实现严格的JSON协议
"""
import asyncio
from typing import Optional, Dict, Any
import openai
from .base_agent import RetryableAgent
from ..protocols.conversation import OrchestratorPrompt, AgentReply
from ..protocols.roles import get_role_prompt, Role, TaskType


class OpenAIAgent(RetryableAgent):
    """OpenAI API代理 - 强制JSON输出"""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini", temperature: float = 0.4, base_url: Optional[str] = None):
        super().__init__(model)
        # 支持自定义API端点
        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
        self.client = openai.AsyncOpenAI(**client_kwargs)
        self.model = model
        self.temperature = temperature

    async def _raw_generate(self, prompt: OrchestratorPrompt) -> str:
        """
        原始生成方法 - 实现BaseAgent抽象方法
        """
        # 构建角色提示
        role = Role(prompt.role)
        task_type = self._infer_task_type(prompt.task)
        role_prompt = get_role_prompt(role, task_type)

        # 构建消息
        system_prompt = self._build_system_prompt(role_prompt)
        user_prompt = self._build_user_prompt(prompt)

        # 调用OpenAI API
        call_params = {
            "model": self.model,
            "temperature": self.temperature,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 1000,  # 降低token消耗
            "timeout": 30.0
        }

        # 对于支持JSON模式的模型，强制JSON输出
        if "gpt-4" in self.model or "gpt-3.5" in self.model:
            call_params["response_format"] = {"type": "json_object"}

        response = await self.client.chat.completions.create(**call_params)

        # 提取回复内容
        response_text = response.choices[0].message.content or ""

        # 更新token计数
        if hasattr(response, 'usage'):
            self.token_count += response.usage.total_tokens

        return response_text

    def _infer_task_type(self, task: str) -> TaskType:
        """根据任务描述推断任务类型"""
        task_lower = task.lower()

        if any(keyword in task_lower for keyword in ["调试", "debug", "修复", "bug", "错误"]):
            return TaskType.DEBUG
        elif any(keyword in task_lower for keyword in ["审查", "review", "检查", "评估"]):
            return TaskType.REVIEW
        elif any(keyword in task_lower for keyword in ["设计", "design", "架构", "方案"]):
            return TaskType.DESIGN
        elif any(keyword in task_lower for keyword in ["实现", "implement", "开发", "编写"]):
            return TaskType.IMPLEMENT
        else:
            return TaskType.IMPLEMENT  # 默认为实现任务


class OpenAIAgentWithRetry(OpenAIAgent):
    """
    带高级重试机制的OpenAI代理
    实现Codex建议的退火和自修复策略
    """

    async def _raw_generate(self, prompt: OrchestratorPrompt) -> str:
        """
        带退火策略的生成方法
        """
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                # 调整温度：重试时降低随机性
                adjusted_temperature = max(0.1, self.temperature - (attempt * 0.2))

                # 构建角色提示
                role = Role(prompt.role)
                task_type = self._infer_task_type(prompt.task)
                role_prompt = get_role_prompt(role, task_type)

                # 重试时强化JSON要求
                if attempt > 0:
                    role_prompt += f"\n\n重试第{attempt + 1}次：必须严格返回JSON格式，上次格式有误。"

                # 构建消息
                system_prompt = self._build_system_prompt(role_prompt)
                user_prompt = self._build_user_prompt(prompt)

                # 重试时简化上下文
                if attempt > 1:
                    user_prompt = self._simplify_prompt(prompt)

                call_params = {
                    "model": self.model,
                    "temperature": adjusted_temperature,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "max_tokens": 800 if attempt > 0 else 1000,  # 重试时减少token
                    "timeout": 30.0
                }

                # 强制JSON模式
                if "gpt-4" in self.model or "gpt-3.5" in self.model:
                    call_params["response_format"] = {"type": "json_object"}

                response = await self.client.chat.completions.create(**call_params)
                response_text = response.choices[0].message.content or ""

                # 更新token计数
                if hasattr(response, 'usage'):
                    self.token_count += response.usage.total_tokens

                return response_text

            except Exception as e:
                if attempt == max_attempts - 1:
                    raise e

                # 指数退避
                await asyncio.sleep(1 * (2 ** attempt))

        raise Exception("OpenAI调用失败，已达最大重试次数")

    def _simplify_prompt(self, prompt: OrchestratorPrompt) -> str:
        """
        简化版用户提示 - 用于重试场景
        """
        return f"""任务: {prompt.task}
角色: {prompt.role}
阶段: {prompt.current_phase.value}

简要说明: 仅返回JSON格式回复，包含phase, message, finish字段。
消息限制在200字符内。

请返回JSON:"""


class OpenAIProviderWithFallback(OpenAIAgentWithRetry):
    """
    带降级策略的OpenAI代理
    实现多模型fallback机制
    """

    def __init__(self, api_key: str, primary_model: str = "gpt-4o-mini",
                 fallback_model: str = "gpt-3.5-turbo", temperature: float = 0.4, base_url: Optional[str] = None):
        super().__init__(api_key, primary_model, temperature, base_url)
        self.fallback_model = fallback_model
        self.fallback_used = False

    async def _raw_generate(self, prompt: OrchestratorPrompt) -> str:
        """
        带模型降级的生成方法
        """
        try:
            # 首先尝试主模型
            return await super()._raw_generate(prompt)

        except Exception as primary_error:
            try:
                # 降级到备用模型
                self.fallback_used = True
                original_model = self.model
                self.model = self.fallback_model

                result = await super()._raw_generate(prompt)

                # 恢复原模型设置
                self.model = original_model
                return result

            except Exception as fallback_error:
                # 两个模型都失败
                raise Exception(f"主模型失败: {primary_error}; 备用模型失败: {fallback_error}")

    def get_stats(self) -> Dict[str, Any]:
        """获取代理统计信息"""
        stats = super().get_stats()
        stats["fallback_used"] = self.fallback_used
        stats["fallback_model"] = self.fallback_model
        return stats