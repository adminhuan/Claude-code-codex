"""
Claude agent implementations (clean, sandbox unified via utils.safety)
"""
from typing import Dict, Any, List
import anthropic

from .base_agent import RetryableAgent
from ..protocols.conversation import OrchestratorPrompt
from ..protocols.roles import get_role_prompt, Role, TaskType
from ..utils.safety import get_sandbox, ToolSandbox


class ClaudeAgent(RetryableAgent):
    """Claude API agent enforcing JSON replies"""

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20240620", temperature: float = 0.4, base_url: str = None):
        super().__init__(model)
        # 支持自定义API端点
        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
        self.client = anthropic.AsyncAnthropic(**client_kwargs)
        self.model = model
        self.temperature = temperature

    async def _raw_generate(self, prompt: OrchestratorPrompt) -> str:
        role = Role(prompt.role)
        task_type = self._infer_task_type(prompt.task)
        role_prompt = get_role_prompt(role, task_type)

        system_prompt = self._build_system_prompt(role_prompt)
        user_prompt = self._build_user_prompt(prompt)

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            temperature=self.temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": [{"type": "text", "text": user_prompt}]}],
        )

        response_text = ""
        for block in response.content:
            if block.type == "text":
                response_text += block.text

        if hasattr(response, "usage"):
            self.token_count += response.usage.input_tokens + response.usage.output_tokens

        return response_text

    def _infer_task_type(self, task: str) -> TaskType:
        t = task.lower()
        if any(k in t for k in ["调试", "debug", "修复", "bug", "错误"]):
            return TaskType.DEBUG
        if any(k in t for k in ["审查", "review", "检查", "评估"]):
            return TaskType.REVIEW
        if any(k in t for k in ["设计", "design", "架构", "方案"]):
            return TaskType.DESIGN
        return TaskType.IMPLEMENT


class ClaudeCodeAgent(ClaudeAgent):
    """Claude agent with tool-aware prompting (tools executed by orchestrator)."""

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20240620",
                 temperature: float = 0.4, enable_tools: bool = False, base_url: str = None):
        super().__init__(api_key, model, temperature, base_url)
        self.enable_tools = enable_tools
        self.tool_call_count = 0

    async def _raw_generate(self, prompt: OrchestratorPrompt) -> str:
        role = Role(prompt.role)
        task_type = self._infer_task_type(prompt.task)
        role_prompt = get_role_prompt(role, task_type)
        if self.enable_tools:
            role_prompt += self._get_tool_instructions()

        system_prompt = self._build_system_prompt(role_prompt)
        user_prompt = self._build_user_prompt(prompt)

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            temperature=self.temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": [{"type": "text", "text": user_prompt}]}],
        )

        response_text = ""
        for block in response.content:
            if block.type == "text":
                response_text += block.text

        if hasattr(response, "usage"):
            self.token_count += response.usage.input_tokens + response.usage.output_tokens

        return response_text

    def _get_tool_instructions(self) -> str:
        return (
            "\nYou can request tools via 'tool_calls' (JSON):\n"
            "- fs_read: {\"name\": \"fs_read\", \"args\": {\"path\": \"file path\"}}\n"
            "- fs_write: {\"name\": \"fs_write\", \"args\": {\"path\": \"file path\", \"content\": \"text\"}}\n"
            "- fs_list: {\"name\": \"fs_list\", \"args\": {\"path\": \"dir path\"}}\n"
            "- run_command: {\"name\": \"run_command\", \"args\": {\"command\": \"command\"}}\n"
            "Rules: request tools via 'tool_calls'; do not inline long outputs in 'message'."
        )


class ClaudeAgentWithSandbox(ClaudeCodeAgent):
    """Claude agent that can execute tools via unified sandbox if needed."""

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20240620",
                 temperature: float = 0.4, sandbox_dir: str = "/tmp/ai_duet_sandbox", base_url: str = None):
        super().__init__(api_key, model, temperature, enable_tools=True, base_url=base_url)
        self.sandbox: ToolSandbox = get_sandbox(sandbox_dir)

    async def execute_tools(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for tool_call in tool_calls:
            self.tool_call_count += 1
            result = await self.sandbox.execute_tool(
                tool_call.get("name", ""), tool_call.get("args", {})
            )
            results.append({
                "tool": tool_call.get("name", ""),
                "args": tool_call.get("args", {}),
                "result": result,
                "summary": result.get("summary", "tool executed"),
            })
        return results

    def get_stats(self) -> Dict[str, Any]:
        stats = super().get_stats()
        stats["tool_call_count"] = self.tool_call_count
        stats["sandbox_enabled"] = True
        return stats
