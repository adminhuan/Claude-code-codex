"""
AI Duet main orchestrator
Implements core collaboration logic with fixed architecture issues
"""
import asyncio
import argparse
import time
from typing import Dict, Optional
from pathlib import Path

from .protocols.conversation import ConversationManager, Turn, OrchestratorPrompt, Phase, FinishStatus
from .agents.openai_agent import OpenAIAgent, OpenAIProviderWithFallback
from .agents.claude_agent import ClaudeAgent, ClaudeAgentWithSandbox
from .utils.config import DuetConfig, load_config_from_env, update_config_from_args, validate_config, print_config
from .utils.logger import ConversationLogger
from .utils.safety import get_sandbox


class DuetOrchestrator:
    """Collaboration orchestrator with fixed state machine integration"""

    def __init__(self, config: DuetConfig):
        self.config = config
        self.conversation = ConversationManager(
            max_turns=config.max_turns,
            window_size=config.max_turns // 2
        )
        self.logger = ConversationLogger(config.output_dir, config.verbose)

        # Initialize agents with correct class names
        self.agents = self._create_agents()

        # Role assignment - maps provider to role
        self.role_assignment = {
            "claude": config.claude_role,
            "openai": config.openai_role
        }

        # Provider assignment - maps role to provider
        self.provider_assignment = {
            config.claude_role: "claude",
            config.openai_role: "openai"
        }

        # Initialize sandbox if needed
        if config.enable_file_ops:
            self.sandbox = get_sandbox(
                config.sandbox_dir or "/tmp/ai_duet_sandbox",
                config.project_root
            )
        else:
            self.sandbox = None

        # Statistics
        self.total_tokens = 0

    def _create_agents(self) -> Dict[str, any]:
        """Create agent instances with correct class names"""
        agents = {}

        # Create OpenAI agent with fallback mechanism
        agents["openai"] = OpenAIProviderWithFallback(
            api_key=self.config.openai.api_key,
            primary_model=self.config.openai.model,
            fallback_model="gpt-3.5-turbo",
            temperature=self.config.openai.temperature,
            base_url=self.config.openai.base_url
        )

        # Create Claude agent with sandbox if needed
        if self.config.enable_file_ops:
            agents["claude"] = ClaudeAgentWithSandbox(
                api_key=self.config.claude.api_key,
                model=self.config.claude.model,
                temperature=self.config.claude.temperature,
                sandbox_dir=self.config.sandbox_dir or "/tmp/ai_duet_sandbox",
                base_url=self.config.claude.base_url
            )
        else:
            agents["claude"] = ClaudeAgent(
                api_key=self.config.claude.api_key,
                model=self.config.claude.model,
                temperature=self.config.claude.temperature,
                base_url=self.config.claude.base_url
            )

        return agents

    async def run_duet(self, task: str) -> Dict[str, any]:
        """Run collaboration conversation with fixed state machine"""
        # Log task start
        self.logger.log_task_start(task, {
            "claude_role": self.config.claude_role,
            "openai_role": self.config.openai_role,
            "task_type": self.config.task_type,
            "max_turns": self.config.max_turns,
            "enable_file_ops": self.config.enable_file_ops
        })

        # Start with state machine's initial speaker
        current_role = self.conversation.current_speaker
        current_provider = self.provider_assignment[current_role]
        turn_number = 0

        try:
            while self.conversation.can_continue():
                turn_number += 1

                # Check budget limit
                if self.total_tokens >= self.config.max_budget_tokens:
                    self.logger.log_warning(f"Reached token budget limit ({self.config.max_budget_tokens})")
                    break

                # Generate current turn response
                turn = await self._generate_turn(task, current_provider, current_role, turn_number)

                if turn is None:
                    self.logger.log_error("Failed to generate response", f"Turn {turn_number}")
                    break

                # Add turn to conversation (this will update state machine)
                self.conversation.add_turn(turn)
                self.logger.log_turn(turn, turn_number)

                # Update statistics
                if turn.token_count:
                    self.total_tokens += turn.token_count

                # Check if conversation is finished
                if turn.reply["finish"] == "final":
                    break

                # Get next speaker from state machine
                current_role = self.conversation.current_speaker
                current_provider = self.provider_assignment[current_role]

            # Extract final result
            final_result = self._extract_final_result()

            # Log conversation end
            self.logger.log_conversation_end(self.conversation.transcript, final_result)

            # Save transcript
            if self.config.save_transcript:
                self.logger.save_transcript(self.conversation.transcript, task, final_result)

            return {
                "success": True,
                "final_result": final_result,
                "turns": len(self.conversation.transcript),
                "total_tokens": self.total_tokens,
                "transcript": self.conversation.transcript
            }

        except Exception as e:
            self.logger.log_error(f"Collaboration error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "turns": len(self.conversation.transcript),
                "total_tokens": self.total_tokens
            }

    async def _generate_turn(self, task: str, provider: str, role: str, turn_number: int) -> Optional[Turn]:
        """Generate single conversation turn"""
        start_time = time.time()

        try:
            # Get agent and role
            agent = self.agents[provider]

            # Build prompt
            prompt = OrchestratorPrompt(
                task=task,
                role=role,
                current_phase=self.conversation.current_phase,
                transcript=self.conversation.get_windowed_transcript(),
                context=self.conversation.get_context_for_agent(role)
            )

            # Dry run mode
            if self.config.enable_dry_run:
                return self._create_mock_turn(provider, role, turn_number)

            # Generate response
            reply = await agent.generate(prompt)

            # Create turn record
            duration = time.time() - start_time
            turn = Turn(
                role=role,
                agent_type=provider,
                reply=reply,
                token_count=getattr(agent, 'token_count', None),
                duration=duration
            )

            # Execute tool calls if present and enabled
            if reply.get("tool_calls") and self.sandbox:
                turn.tool_results = await self._execute_tools(reply["tool_calls"])

            return turn

        except Exception as e:
            self.logger.log_error(f"Failed to generate turn {turn_number}: {str(e)}")
            return None

    def _create_mock_turn(self, provider: str, role: str, turn_number: int) -> Turn:
        """Create mock turn for dry run mode"""
        mock_reply = {
            "phase": self.conversation.current_phase,
            "message": f"[Dry run] Turn {turn_number} mock response from {role}",
            "tool_calls": [],
            "finish": "final" if turn_number >= 3 else "handoff",
            "critiques": ""
        }

        return Turn(
            role=role,
            agent_type=provider,
            reply=mock_reply,
            token_count=100,  # Mock token consumption
            duration=1.0
        )

    async def _execute_tools(self, tool_calls: list) -> list:
        """Execute tool calls through unified sandbox"""
        results = []

        if not self.sandbox:
            return results

        for tool_call in tool_calls:
            try:
                result = await self.sandbox.execute_tool(
                    tool_call.get("name", ""),
                    tool_call.get("args", {})
                )

                results.append({
                    "tool": tool_call.get("name", ""),
                    "args": tool_call.get("args", {}),
                    "result": result,
                    "summary": result.get("summary", f"{tool_call.get('name', 'tool')} executed")
                })

            except Exception as e:
                results.append({
                    "tool": tool_call.get("name", "unknown"),
                    "error": str(e),
                    "summary": f"Tool execution failed: {str(e)[:50]}"
                })

        return results

    def _extract_final_result(self) -> Optional[str]:
        """Extract final result from conversation"""
        if not self.conversation.transcript:
            return None

        # Look for final-marked replies
        for turn in reversed(self.conversation.transcript):
            if turn.reply["finish"] == "final":
                message = turn.reply["message"]
                # Extract FINAL: marked content
                if "FINAL:" in message:
                    final_part = message.split("FINAL:", 1)[1].strip()
                    return final_part
                return message

        # Return last turn's message if no final marker
        return self.conversation.transcript[-1].reply["message"]


def create_cli_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser"""
    parser = argparse.ArgumentParser(
        description="AI Duet - Claude Code and OpenAI Collaboration System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m ai_duet "optimize this sorting algorithm" --claude-role executor --openai-role reviewer
  python -m ai_duet "debug login issue" --type debug --with-files --project-root ./src
  python -m ai_duet "design user management system" --type design --max-turns 15 --verbose
        """
    )

    parser.add_argument("task", help="Task description for collaboration")

    # Role configuration
    parser.add_argument("--claude-role", choices=["executor", "reviewer", "facilitator"],
                       default="executor", help="Claude's role (default: executor)")
    parser.add_argument("--openai-role", choices=["executor", "reviewer", "facilitator"],
                       default="reviewer", help="OpenAI's role (default: reviewer)")

    # Task configuration
    parser.add_argument("--type", choices=["debug", "review", "design", "implement"],
                       default="implement", help="Task type (default: implement)")
    parser.add_argument("--max-turns", type=int, default=10, help="Maximum conversation turns (default: 10)")
    parser.add_argument("--first", choices=["claude", "openai"], default="claude",
                       help="First speaker (default: claude)")

    # Model configuration
    parser.add_argument("--openai-model", help="OpenAI model name")
    parser.add_argument("--claude-model", help="Claude model name")
    parser.add_argument("--temperature", type=float, help="Generation temperature (0.0-1.0)")

    # File operations
    parser.add_argument("--with-files", action="store_true", help="Enable file operations")
    parser.add_argument("--project-root", help="Project root directory path")

    # Output control
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode (no actual API calls)")
    parser.add_argument("--budget", type=int, help="Token budget limit")

    # Configuration viewing
    parser.add_argument("--print-config", action="store_true", help="Print configuration and exit")

    return parser


async def async_main():
    """Main async function"""
    parser = create_cli_parser()
    args = parser.parse_args()

    try:
        # Load configuration
        config = load_config_from_env()
        config = update_config_from_args(config, vars(args))

        # Print configuration if requested
        if args.print_config:
            print_config(config)
            return

        # Validate configuration
        if not validate_config(config):
            return

        # Create orchestrator
        orchestrator = DuetOrchestrator(config)

        # Run collaboration
        result = await orchestrator.run_duet(args.task)

        # Output result
        if result["success"]:
            print(f"\nCollaboration completed successfully!")
            if result.get("final_result"):
                print(f"Final result: {result['final_result']}")
        else:
            print(f"\nCollaboration failed: {result.get('error', 'Unknown error')}")

    except KeyboardInterrupt:
        print(f"\n\nUser interrupted operation")
    except Exception as e:
        print(f"\nError occurred: {str(e)}")


if __name__ == "__main__":
    asyncio.run(async_main())