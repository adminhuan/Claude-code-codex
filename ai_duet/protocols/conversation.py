"""
对话协议和状态管理
按照Codex建议实现严格的JSON协议约束
"""
import json
import jsonschema
from enum import Enum
from typing import TypedDict, List, Optional, Dict, Any, Union
from dataclasses import dataclass


class Phase(str, Enum):
    """对话阶段状态机 - 严格枚举"""
    ANALYSIS = "analysis"
    PROPOSAL = "proposal"
    IMPLEMENT = "implement"
    REVIEW = "review"
    FINALIZE = "finalize"


class FinishStatus(str, Enum):
    """完成状态 - 严格枚举"""
    NONE = "none"
    HANDOFF = "handoff"  # 交给对方继续
    FINAL = "final"      # 最终完成


class ToolCall(TypedDict):
    """工具调用结构 - 严格约束"""
    name: str
    args: Dict[str, Any]


class AgentReply(TypedDict, total=False):
    """代理回复的标准化结构 - 严格schema"""
    phase: str  # "analysis", "proposal", "implement", "review", "finalize"
    message: str
    tool_calls: List[ToolCall]  # 可空但类型固定
    finish: str  # "none", "handoff", "final"
    critiques: str  # 单一字符串而非列表


# JSON Schema定义 - 强制验证
AGENT_REPLY_SCHEMA = {
    "type": "object",
    "properties": {
        "phase": {
            "type": "string",
            "enum": ["analysis", "proposal", "implement", "review", "finalize"]
        },
        "message": {
            "type": "string",
            "maxLength": 500  # Codex建议的长度限制
        },
        "tool_calls": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "args": {"type": "object"}
                },
                "required": ["name", "args"],
                "additionalProperties": False
            }
        },
        "finish": {
            "type": "string",
            "enum": ["none", "handoff", "final"]
        },
        "critiques": {
            "type": "string",
            "maxLength": 200
        }
    },
    "required": ["phase", "message", "finish"],
    "additionalProperties": False
}


def validate_agent_reply(reply_data: Dict[str, Any]) -> AgentReply:
    """
    严格验证代理回复格式
    按照Codex建议：只允许符合schema的JSON，解析失败要有降级处理
    """
    try:
        # 1. JSON schema验证
        jsonschema.validate(reply_data, AGENT_REPLY_SCHEMA)

        # 2. 类型转换和标准化
        validated_reply: AgentReply = {
            "phase": reply_data["phase"],  # Keep as string for consistency
            "message": reply_data["message"].strip(),
            "finish": reply_data["finish"]  # Keep as string for consistency
        }

        # 3. 可选字段处理
        if "tool_calls" in reply_data:
            validated_reply["tool_calls"] = reply_data["tool_calls"]
        else:
            validated_reply["tool_calls"] = []

        if "critiques" in reply_data and reply_data["critiques"].strip():
            validated_reply["critiques"] = reply_data["critiques"].strip()

        return validated_reply

    except jsonschema.ValidationError as e:
        raise ValueError(f"JSON schema验证失败: {e.message}")
    except ValueError as e:
        raise ValueError(f"枚举值验证失败: {str(e)}")


def create_error_reply(error_msg: str, current_phase: str = "analysis") -> AgentReply:
    """
    创建错误回复 - 用于降级处理
    """
    return {
        "phase": current_phase,
        "message": f"[系统错误] {error_msg[:400]}",
        "tool_calls": [],
        "finish": "handoff",
        "critiques": "请修正回复格式为有效JSON"
    }


@dataclass
class Turn:
    """单轮对话记录"""
    role: str  # "executor" | "reviewer" | "facilitator"
    agent_type: str  # "openai" | "claude"
    reply: AgentReply
    tool_results: Optional[List[Dict[str, Any]]] = None
    token_count: Optional[int] = None
    duration: Optional[float] = None


@dataclass
class OrchestratorPrompt:
    """发送给代理的标准化提示"""
    task: str
    role: str
    current_phase: str  # "analysis", "proposal", "implement", "review", "finalize"
    transcript: List[Turn]
    context: Dict[str, Any]


class StateMachine:
    """
    状态机管理器 - 按Codex建议实现确定性状态转换
    移除启发式判断，由状态机决定谁发言和状态转换
    """

    def __init__(self):
        self.current_phase = "analysis"
        self.current_speaker = "executor"  # 默认执行者开始

    def next_state(self, current_reply: AgentReply, current_speaker: str) -> tuple[str, str]:
        """
        确定性状态转换 - 移除启发式判断
        返回: (下一阶段, 下一发言者)
        """
        current_phase = current_reply["phase"]
        finish_status = current_reply["finish"]

        # 如果标记为最终完成，保持当前状态
        if finish_status == "final":
            return current_phase, current_speaker

        # 确定性状态转换规则
        phase_rules = {
            "analysis": self._handle_analysis_phase,
            "proposal": self._handle_proposal_phase,
            "implement": self._handle_implement_phase,
            "review": self._handle_review_phase,
            "finalize": self._handle_finalize_phase
        }

        handler = phase_rules.get(current_phase, self._default_transition)
        return handler(current_reply, current_speaker)

    def _handle_analysis_phase(self, reply: AgentReply, speaker: str) -> tuple[str, str]:
        """分析阶段 -> 提案阶段"""
        if speaker == "executor":
            # 执行者分析完成，转到提案阶段，继续由执行者主导
            return "proposal", "executor"
        else:
            # 审核者参与分析，转给执行者做提案
            return "proposal", "executor"

    def _handle_proposal_phase(self, reply: AgentReply, speaker: str) -> tuple[str, str]:
        """提案阶段 -> 实现阶段或审核"""
        finish = reply["finish"]

        if speaker == "executor":
            if finish == "handoff":
                # 执行者提交提案，交给审核者审核
                return "proposal", "reviewer"
            else:
                # 执行者继续，进入实现阶段
                return "implement", "executor"
        else:  # reviewer
            if finish == "handoff":
                # 审核完成，进入实现阶段
                return "implement", "executor"
            else:
                # 审核继续
                return "proposal", "executor"

    def _handle_implement_phase(self, reply: AgentReply, speaker: str) -> tuple[str, str]:
        """实现阶段 -> 审核阶段"""
        if speaker == "executor":
            # 执行者实现完成，交给审核者审核
            return "review", "reviewer"
        else:
            # 审核者在实现阶段的建议，回给执行者
            return "implement", "executor"

    def _handle_review_phase(self, reply: AgentReply, speaker: str) -> tuple[str, str]:
        """审核阶段 -> 最终化或回到实现"""
        finish = reply["finish"]

        if speaker == "reviewer":
            if finish == "handoff":
                # 审核通过，进入最终化
                return "finalize", "executor"
            else:
                # 审核不通过，回到实现阶段
                return "implement", "executor"
        else:
            # 执行者响应审核意见
            return "implement", "executor"

    def _handle_finalize_phase(self, reply: AgentReply, speaker: str) -> tuple[str, str]:
        """最终化阶段 - 保持当前状态"""
        return "finalize", speaker

    def _default_transition(self, reply: AgentReply, speaker: str) -> tuple[str, str]:
        """默认转换 - 切换发言者"""
        next_speaker = "reviewer" if speaker == "executor" else "executor"
        return reply["phase"], next_speaker


class ConversationManager:
    """对话管理器 - 集成状态机和滑动窗口"""

    def __init__(self, max_turns: int = 10, window_size: int = 6):
        self.transcript: List[Turn] = []
        self.state_machine = StateMachine()
        self.max_turns = max_turns
        self.window_size = window_size
        self.running_summary = ""
        self.total_tokens = 0

    @property
    def current_phase(self) -> str:
        """当前阶段"""
        return self.state_machine.current_phase

    @property
    def current_speaker(self) -> str:
        """当前发言者"""
        return self.state_machine.current_speaker

    def can_continue(self) -> bool:
        """检查是否可以继续对话"""
        if len(self.transcript) >= self.max_turns:
            return False

        # 检查最后一轮是否表示完成
        if self.transcript:
            last_turn = self.transcript[-1]
            if last_turn.reply["finish"] == "final":
                return False

        return True

    def add_turn(self, turn: Turn):
        """添加新的对话轮次"""
        self.transcript.append(turn)

        # 更新token统计
        if turn.token_count:
            self.total_tokens += turn.token_count

        # 状态机转换 - 传入正确的角色参数
        next_phase, next_speaker = self.state_machine.next_state(turn.reply, turn.role)
        self.state_machine.current_phase = next_phase
        self.state_machine.current_speaker = next_speaker

        # 滑动窗口摘要
        if len(self.transcript) > self.window_size:
            self._update_running_summary()

    def _update_running_summary(self):
        """
        更新运行摘要 - 按Codex建议保留关键信息
        保留：约束/决策/待办/证据
        """
        if len(self.transcript) % 4 == 0:  # 每4轮摘要一次
            key_points = []

            # 提取关键决策和约束
            for turn in self.transcript[-self.window_size:]:
                message = turn.reply["message"].lower()

                # 识别决策点
                if any(keyword in message for keyword in ["决定", "选择", "采用", "实现", "approve", "通过"]):
                    key_points.append(f"决策-{turn.role}: {turn.reply['message'][:100]}")

                # 识别约束条件
                if any(keyword in message for keyword in ["必须", "不能", "限制", "要求", "constraint"]):
                    key_points.append(f"约束-{turn.role}: {turn.reply['message'][:100]}")

                # 识别待办事项
                if any(keyword in message for keyword in ["需要", "应该", "建议", "todo", "next"]):
                    key_points.append(f"待办-{turn.role}: {turn.reply['message'][:100]}")

            # 更新摘要
            if key_points:
                self.running_summary = "\n".join(key_points[-8:])  # 保留最近8个关键点

    def get_context_for_agent(self, role: str) -> Dict[str, Any]:
        """为特定角色准备上下文"""
        return {
            "current_phase": self.current_phase,
            "turn_count": len(self.transcript),
            "max_turns": self.max_turns,
            "running_summary": self.running_summary,
            "total_tokens": self.total_tokens,
            "last_critique": self._get_last_critique_for_role(role),
            "recent_decisions": self._get_recent_decisions()
        }

    def _get_last_critique_for_role(self, role: str) -> Optional[str]:
        """获取针对特定角色的最后一个评审意见"""
        for turn in reversed(self.transcript):
            if turn.role != role and turn.reply.get("critiques"):
                return turn.reply["critiques"]
        return None

    def _get_recent_decisions(self) -> List[str]:
        """获取最近的决策点"""
        decisions = []
        for turn in self.transcript[-3:]:  # 最近3轮
            if turn.reply["finish"] != FinishStatus.NONE:
                decisions.append(f"{turn.role}: {turn.reply['message'][:80]}")
        return decisions

    def get_windowed_transcript(self) -> List[Turn]:
        """
        获取窗口化的对话历史
        实现滑动窗口 + 运行摘要机制
        """
        if len(self.transcript) <= self.window_size:
            return self.transcript
        else:
            # 返回最近的对话 + 摘要作为上下文
            return self.transcript[-self.window_size:]