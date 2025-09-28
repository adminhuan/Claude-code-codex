"""
Conversation logging utilities (clean ASCII, schema-aligned)
"""
import json
import time
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

from ..protocols.conversation import Turn, AgentReply, Phase, FinishStatus


class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"


class ConversationLogger:
    """Pretty console logger + transcript persistence"""

    def __init__(self, output_dir: str = "./ai_duet_outputs", verbose: bool = False):
        self.output_dir = Path(output_dir)
        self.verbose = verbose
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.start_time = time.time()

        # Ensure directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "transcripts").mkdir(exist_ok=True)
        (self.output_dir / "logs").mkdir(exist_ok=True)

    def log_task_start(self, task: str, config: Dict[str, Any]):
        print(f"\n{Colors.BOLD}{Colors.BLUE}=== Start AI Duet Collaboration ==={Colors.RESET}")
        print(f"{Colors.CYAN}Task: {task}{Colors.RESET}")
        print(f"{Colors.DIM}Session: {self.session_id}{Colors.RESET}")

        if self.verbose:
            print(f"\n{Colors.DIM}Config:")
            for key, value in config.items():
                print(f"  {key}: {value}")
            print(f"{Colors.RESET}")

    def log_turn(self, turn: Turn, turn_number: int):
        role_info = self._get_role_display(turn.role, turn.agent_type)

        print(f"\n{Colors.BOLD}--- Turn {turn_number} ---{Colors.RESET}")
        print(f"{role_info['color']}{role_info['icon']} {role_info['display']} ({turn.agent_type}){Colors.RESET}")

        # Phase/finish formatting (support Enum or str)
        phase = turn.reply.get("phase")
        if isinstance(phase, Phase):
            phase_str = phase.value
        else:
            phase_str = str(phase)
        finish = turn.reply.get("finish")
        if isinstance(finish, FinishStatus):
            finish_str = finish.value
        else:
            finish_str = str(finish)

        phase_color = self._get_phase_color(phase_str)
        finish_color = self._get_finish_color(finish_str)
        print(f"Phase: {phase_color}{phase_str}{Colors.RESET} | Status: {finish_color}{finish_str}{Colors.RESET}")

        message = turn.reply.get("message", "")
        if not self.verbose and len(message) > 200:
            message = message[:200] + "..."
        print(f"\n{Colors.WHITE}{message}{Colors.RESET}")

        tool_calls = turn.reply.get("tool_calls") or []
        if tool_calls:
            print(f"\n{Colors.YELLOW}Tool calls:{Colors.RESET}")
            for tool_call in tool_calls:
                name = tool_call.get("name")
                args = tool_call.get("args", {})
                print(f"  - {name}: {args}")

        if turn.tool_results:
            print(f"\n{Colors.GREEN}Tool results:{Colors.RESET}")
            for result in turn.tool_results:
                summary = result.get("summary", "(no summary)")
                print(f"  - {summary}")

        critiques = turn.reply.get("critiques")
        if critiques:
            print(f"\n{Colors.MAGENTA}Critiques:{Colors.RESET}")
            print(f"  {critiques}")

        if self.verbose and (turn.token_count or turn.duration):
            stats = []
            if turn.token_count:
                stats.append(f"tokens: {turn.token_count}")
            if turn.duration:
                stats.append(f"time: {turn.duration:.2f}s")
            print(f"\n{Colors.DIM}Stats: {', '.join(stats)}{Colors.RESET}")

    def log_conversation_end(self, transcript: List[Turn], final_result: str | None = None):
        duration = time.time() - self.start_time
        total_tokens = sum((t.token_count or 0) for t in transcript)

        print(f"\n{Colors.BOLD}{Colors.GREEN}=== Collaboration Finished ==={Colors.RESET}")
        print(f"{Colors.DIM}Turns: {len(transcript)}")
        print(f"Duration: {duration:.2f}s")
        print(f"Tokens: {total_tokens}{Colors.RESET}")

        if final_result:
            print(f"\n{Colors.BOLD}Final Result:{Colors.RESET}")
            print(f"{Colors.WHITE}{final_result}{Colors.RESET}")

        print(f"\n{Colors.DIM}Artifacts saved to: {self.output_dir}{Colors.RESET}")

    def log_error(self, error: str, context: str = ""):
        print(f"\n{Colors.BG_RED}{Colors.WHITE} ERROR {Colors.RESET} {Colors.RED}{error}{Colors.RESET}")
        if context:
            print(f"{Colors.DIM}Context: {context}{Colors.RESET}")

    def log_warning(self, warning: str):
        print(f"{Colors.YELLOW}Warning: {warning}{Colors.RESET}")

    def save_transcript(self, transcript: List[Turn], task: str, final_result: str | None = None):
        data: Dict[str, Any] = {
            "session_id": self.session_id,
            "task": task,
            "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
            "end_time": datetime.now().isoformat(),
            "final_result": final_result,
            "turns": []
        }

        for i, turn in enumerate(transcript, start=1):
            reply = dict(turn.reply)
            if isinstance(reply.get("phase"), Phase):
                reply["phase"] = reply["phase"].value
            if isinstance(reply.get("finish"), FinishStatus):
                reply["finish"] = reply["finish"].value

            data["turns"].append({
                "turn_number": i,
                "role": turn.role,
                "agent_type": turn.agent_type,
                "reply": reply,
                "tool_results": turn.tool_results,
                "token_count": turn.token_count,
                "duration": turn.duration
            })

        transcript_file = self.output_dir / "transcripts" / f"{self.session_id}.json"
        with open(transcript_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        readable_file = self.output_dir / "transcripts" / f"{self.session_id}_readable.txt"
        with open(readable_file, "w", encoding="utf-8") as f:
            f.write("AI Duet Transcript\n")
            f.write(f"Session: {self.session_id}\n")
            f.write(f"Task: {task}\n")
            f.write(f"Start: {data['start_time']}\n")
            f.write(f"End: {data['end_time']}\n")
            f.write("=" * 50 + "\n\n")

            for i, turn in enumerate(transcript, start=1):
                role_info = self._get_role_display(turn.role, turn.agent_type)
                phase = turn.reply.get("phase")
                phase_str = phase.value if isinstance(phase, Phase) else str(phase)
                finish = turn.reply.get("finish")
                finish_str = finish.value if isinstance(finish, FinishStatus) else str(finish)
                f.write(f"Turn {i} - {role_info['display']} ({turn.agent_type})\n")
                f.write(f"Phase: {phase_str} | Status: {finish_str}\n")
                f.write(f"Message: {turn.reply.get('message','')}\n")

                if turn.reply.get("tool_calls"):
                    f.write(f"Tool calls: {turn.reply['tool_calls']}\n")

                if turn.reply.get("critiques"):
                    f.write(f"Critiques: {turn.reply['critiques']}\n")

                f.write("\n" + "-" * 30 + "\n\n")

            if final_result:
                f.write(f"Final:\n{final_result}\n")

    def _get_role_display(self, role: str, agent_type: str) -> Dict[str, str]:
        mapping = {
            "executor": {"icon": "🔧", "display": "Executor", "color": Colors.GREEN},
            "reviewer": {"icon": "👁", "display": "Reviewer", "color": Colors.BLUE},
            "facilitator": {"icon": "🎯", "display": "Facilitator", "color": Colors.MAGENTA},
        }
        config = mapping.get(role, {"icon": "•", "display": role, "color": Colors.WHITE})

        if agent_type == "claude":
            config["color"] = Colors.CYAN
        elif agent_type == "openai":
            config["color"] = Colors.YELLOW
        return config

    def _get_phase_color(self, phase: str) -> str:
        colors = {
            "analysis": Colors.YELLOW,
            "proposal": Colors.BLUE,
            "implement": Colors.GREEN,
            "review": Colors.MAGENTA,
            "finalize": Colors.CYAN,
        }
        return colors.get(phase, Colors.WHITE)

    def _get_finish_color(self, finish: str) -> str:
        colors = {
            "none": Colors.DIM,
            "handoff": Colors.YELLOW,
            "final": Colors.GREEN,
        }
        return colors.get(finish, Colors.WHITE)

