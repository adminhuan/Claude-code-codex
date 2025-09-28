"""
基础代理抽象类
定义所有代理的标准接口
按照Codex建议实现严格的JSON协议约束
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import json
import re
import asyncio
from ..protocols.conversation import (
    OrchestratorPrompt,
    AgentReply,
    validate_agent_reply,
    create_error_reply,
    AGENT_REPLY_SCHEMA,
    Phase
)


class BaseAgent(ABC):
    """所有代理的基础抽象类 - 强制JSON协议"""

    def __init__(self, model_name: str = ""):
        self.model_name = model_name
        self.token_count = 0
        self.retry_count = 0
        self.max_retries = 3

    @abstractmethod
    async def _raw_generate(self, prompt: OrchestratorPrompt) -> str:
        """
        原始生成方法 - 子类实现
        返回模型的原始文本输出
        """
        pass

    async def generate(self, prompt: OrchestratorPrompt) -> AgentReply:
        """
        生成回复的核心方法 - 带错误处理和重试
        Args:
            prompt: 标准化的协调器提示
        Returns:
            AgentReply: 严格验证的结构化回复
        """
        for attempt in range(self.max_retries):
            try:
                # 1. 获取原始输出
                raw_response = await self._raw_generate(prompt)

                # 2. 解析为JSON
                parsed_json = self._extract_json(raw_response)

                # 3. 严格验证
                validated_reply = validate_agent_reply(parsed_json)

                return validated_reply

            except Exception as e:
                self.retry_count += 1

                # 最后一次尝试失败，返回错误回复
                if attempt == self.max_retries - 1:
                    return create_error_reply(
                        f"代理生成失败（尝试{self.max_retries}次）: {str(e)}",
                        prompt.current_phase
                    )

                # 准备重试 - 降低温度和简化提示
                await asyncio.sleep(0.5 * (attempt + 1))  # 指数退避

        # 理论上不会到达这里
        return create_error_reply("意外错误", prompt.current_phase)

    def _extract_json(self, response_text: str) -> Dict[str, Any]:
        """
        从响应中提取JSON - 支持多种格式
        """
        cleaned = response_text.strip()

        # 1. 尝试提取JSON代码块
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', cleaned, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # 2. 尝试找到第一个 { 到最后一个 } 的内容
            start = cleaned.find('{')
            end = cleaned.rfind('}')
            if start != -1 and end != -1 and end > start:
                json_str = cleaned[start:end+1]
            else:
                # 3. 整个响应可能就是JSON
                json_str = cleaned

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON解析失败: {str(e)}。原始响应: {response_text[:200]}...")

    def _build_system_prompt(self, role_prompt: str) -> str:
        """构建系统提示 - 强制JSON输出"""
        base_system = f"""你是一个协作AI代理。必须严格按照JSON格式回复，否则被驳回重试。

JSON Schema (严格遵循):
{json.dumps(AGENT_REPLY_SCHEMA, indent=2, ensure_ascii=False)}

关键要求:
1. 回复必须是有效的JSON格式，不包含任何其他文本
2. 必须包含所有必需字段：phase, message, finish
3. message字段限制在500字符以内
4. 只使用指定的枚举值
5. 不要解释或添加注释，只返回JSON

示例有效回复:
{{
    "phase": "analysis",
    "message": "已分析问题，发现需要优化算法复杂度",
    "tool_calls": [],
    "finish": "handoff",
    "critiques": "请审查这个分析是否准确"
}}"""

        return f"{base_system}\n\n{role_prompt}"

    def _build_user_prompt(self, prompt: OrchestratorPrompt) -> str:
        """构建用户提示 - 减少上下文爆炸"""
        # 格式化对话历史（滑动窗口）
        transcript_text = self._format_transcript_window(prompt.transcript)

        # 构建紧凑的上下文信息
        context_text = self._format_context_compact(prompt.context)

        user_prompt = f"""任务: {prompt.task}

你的角色: {prompt.role}
当前阶段: {prompt.current_phase.value}

{context_text}

最近对话:
{transcript_text}

请仅返回符合schema的JSON回复，无其他文本:"""

        return user_prompt

    def _format_transcript_window(self, transcript) -> str:
        """格式化对话历史 - 窗口化显示"""
        if not transcript:
            return "(对话开始)"

        # 只显示最近3轮，避免上下文爆炸
        recent_turns = transcript[-3:]
        formatted = []

        for i, turn in enumerate(recent_turns):
            role_icon = "🔧" if turn.role == "executor" else "👁" if turn.role == "reviewer" else "🎯"
            message = turn.reply['message'][:150] + "..." if len(turn.reply['message']) > 150 else turn.reply['message']
            formatted.append(f"{role_icon} {turn.role}: {message}")

            # 显示工具结果摘要
            if turn.tool_results:
                tool_summary = f"[工具: {len(turn.tool_results)}个结果]"
                formatted.append(f"   └── {tool_summary}")

        return "\n".join(formatted)

    def _format_context_compact(self, context: Dict[str, Any]) -> str:
        """格式化上下文信息 - 紧凑显示"""
        parts = []

        # 关键信息优先
        if context.get("running_summary"):
            summary = context["running_summary"][:200] + "..." if len(context["running_summary"]) > 200 else context["running_summary"]
            parts.append(f"关键摘要: {summary}")

        if context.get("last_critique"):
            critique = context["last_critique"][:100] + "..." if len(context["last_critique"]) > 100 else context["last_critique"]
            parts.append(f"最近审核: {critique}")

        # 统计信息
        stats = f"进度: {context.get('turn_count', 0)}/{context.get('max_turns', 10)} 轮"
        if context.get('total_tokens'):
            stats += f" | Tokens: {context['total_tokens']}"
        parts.append(stats)

        return "\n".join(parts) if parts else ""

    def get_stats(self) -> Dict[str, Any]:
        """获取代理统计信息"""
        return {
            "model_name": self.model_name,
            "total_tokens": self.token_count,
            "retry_count": self.retry_count
        }


class RetryableAgent(BaseAgent):
    """
    支持错误恢复的代理基类
    实现Codex建议的纠错与恢复机制
    """

    async def generate_with_recovery(self, prompt: OrchestratorPrompt) -> AgentReply:
        """
        带纠错回合的生成方法
        """
        # 首次尝试
        result = await self.generate(prompt)

        # 如果是错误回复，尝试自修复
        if "[系统错误]" in result["message"]:
            recovery_prompt = self._create_recovery_prompt(prompt, result["message"])
            result = await self.generate(recovery_prompt)

        return result

    def _create_recovery_prompt(self, original_prompt: OrchestratorPrompt, error_msg: str) -> OrchestratorPrompt:
        """
        创建恢复提示 - 引导模型自修复
        """
        recovery_context = original_prompt.context.copy()
        recovery_context["error_feedback"] = f"上次回复格式错误: {error_msg}。请严格按JSON schema返回。"

        return OrchestratorPrompt(
            task=original_prompt.task,
            role=original_prompt.role,
            current_phase=original_prompt.current_phase,
            transcript=original_prompt.transcript,
            context=recovery_context
        )