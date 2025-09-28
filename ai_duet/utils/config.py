"""
Configuration management and CLI integration (clean ASCII)
"""
import os
from dataclasses import dataclass
from typing import Optional, Dict, Any
from pathlib import Path


@dataclass
class AgentConfig:
    api_key: str
    model: str
    temperature: float = 0.4
    max_tokens: int = 1500
    base_url: Optional[str] = None  # 自定义API端点


@dataclass
class DuetConfig:
    # API settings
    openai: AgentConfig
    claude: AgentConfig

    # Roles and task type
    claude_role: str = "executor"  # executor | reviewer | facilitator
    openai_role: str = "reviewer"
    task_type: str = "implement"  # debug | review | design | implement

    # Conversation
    max_turns: int = 10
    first_speaker: str = "claude"  # claude | openai (reserved)

    # File operations
    enable_file_ops: bool = False
    project_root: Optional[str] = None
    sandbox_dir: Optional[str] = None

    # Output/diagnostics
    verbose: bool = False
    save_transcript: bool = True
    output_dir: str = "./ai_duet_outputs"

    # Budget and modes
    max_budget_tokens: int = 50000
    enable_dry_run: bool = False


def load_config_from_env() -> DuetConfig:
    """Load configuration from environment variables."""
    openai_key = os.getenv("OPENAI_API_KEY")
    claude_key = os.getenv("ANTHROPIC_API_KEY")

    if not openai_key:
        raise ValueError("Missing OPENAI_API_KEY")
    if not claude_key:
        raise ValueError("Missing ANTHROPIC_API_KEY")

    config = DuetConfig(
        openai=AgentConfig(
            api_key=openai_key,
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.4")),
            max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "1500")),
            base_url=os.getenv("OPENAI_BASE_URL"),  # 支持自定义端点
        ),
        claude=AgentConfig(
            api_key=claude_key,
            model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20240620"),
            temperature=float(os.getenv("ANTHROPIC_TEMPERATURE", "0.4")),
            max_tokens=int(os.getenv("ANTHROPIC_MAX_TOKENS", "1500")),
            base_url=os.getenv("ANTHROPIC_BASE_URL"),  # 支持自定义端点
        ),
        claude_role=os.getenv("CLAUDE_ROLE", "executor"),
        openai_role=os.getenv("OPENAI_ROLE", "reviewer"),
        task_type=os.getenv("TASK_TYPE", "implement"),
        max_turns=int(os.getenv("MAX_TURNS", "10")),
        first_speaker=os.getenv("FIRST_SPEAKER", "claude"),
        enable_file_ops=os.getenv("ENABLE_FILE_OPS", "false").lower() == "true",
        project_root=os.getenv("PROJECT_ROOT"),
        sandbox_dir=os.getenv("SANDBOX_DIR"),
        verbose=os.getenv("VERBOSE", "false").lower() == "true",
        save_transcript=os.getenv("SAVE_TRANSCRIPT", "true").lower() == "true",
        output_dir=os.getenv("OUTPUT_DIR", "./ai_duet_outputs"),
        max_budget_tokens=int(os.getenv("MAX_BUDGET_TOKENS", "50000")),
        enable_dry_run=os.getenv("DRY_RUN", "false").lower() == "true",
    )

    return config


def update_config_from_args(config: DuetConfig, args: Dict[str, Any]) -> DuetConfig:
    """Apply CLI args into configuration."""
    field_mapping = {
        "claude_role": "claude_role",
        "openai_role": "openai_role",
        "type": "task_type",
        "max_turns": "max_turns",
        "first": "first_speaker",
        "with_files": "enable_file_ops",
        "project_root": "project_root",
        "verbose": "verbose",
        "dry_run": "enable_dry_run",
        "budget": "max_budget_tokens",
    }

    for arg_name, field_name in field_mapping.items():
        if arg_name in args and args[arg_name] is not None:
            setattr(config, field_name, args[arg_name])

    # Model overrides
    if args.get("openai_model"):
        config.openai.model = args["openai_model"]
    if args.get("claude_model"):
        config.claude.model = args["claude_model"]

    # Temperature override
    if args.get("temperature") is not None:
        config.openai.temperature = args["temperature"]
        config.claude.temperature = args["temperature"]

    return config


def validate_config(config: DuetConfig) -> bool:
    """Validate configuration; print errors and return False if invalid."""
    errors: list[str] = []

    valid_roles = ["executor", "reviewer", "facilitator"]
    if config.claude_role not in valid_roles:
        errors.append(f"Invalid Claude role: {config.claude_role}")
    if config.openai_role not in valid_roles:
        errors.append(f"Invalid OpenAI role: {config.openai_role}")

    valid_task_types = ["debug", "review", "design", "implement"]
    if config.task_type not in valid_task_types:
        errors.append(f"Invalid task type: {config.task_type}")

    if config.first_speaker not in ["claude", "openai"]:
        errors.append(f"Invalid first speaker: {config.first_speaker}")

    if config.enable_file_ops and config.project_root:
        if not Path(config.project_root).exists():
            errors.append(f"Project root does not exist: {config.project_root}")

    if config.max_turns <= 0:
        errors.append("max_turns must be > 0")
    if config.max_budget_tokens <= 0:
        errors.append("max_budget_tokens must be > 0")

    if errors:
        for e in errors:
            print(f"Config error: {e}")
        return False

    return True


def print_config(config: DuetConfig):
    """Pretty-print configuration for debugging."""
    print("=== AI Duet Config ===")
    print(f"Claude role: {config.claude_role} (model: {config.claude.model})")
    print(f"OpenAI role: {config.openai_role} (model: {config.openai.model})")
    print(f"Task type: {config.task_type}")
    print(f"Max turns: {config.max_turns}")
    print(f"First speaker: {config.first_speaker}")
    print(f"File ops: {'on' if config.enable_file_ops else 'off'}")
    if config.project_root:
        print(f"Project root: {config.project_root}")
    print(f"Token budget: {config.max_budget_tokens}")
    print(f"Dry run: {'on' if config.enable_dry_run else 'off'}")
    print("=" * 30)


def setup_output_directory(config: DuetConfig) -> Path:
    """Ensure output directories exist and return root path."""
    output_path = Path(config.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    (output_path / "transcripts").mkdir(exist_ok=True)
    (output_path / "artifacts").mkdir(exist_ok=True)
    (output_path / "logs").mkdir(exist_ok=True)
    return output_path
