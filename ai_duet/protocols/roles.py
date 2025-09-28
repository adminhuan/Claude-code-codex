"""
Role definitions and templates
Define behavior patterns and prompt templates for different roles
"""
from enum import Enum
from typing import Dict


class Role(Enum):
    """Role types"""
    EXECUTOR = "executor"
    REVIEWER = "reviewer"
    FACILITATOR = "facilitator"


class TaskType(Enum):
    """Task types"""
    DEBUG = "debug"
    REVIEW = "review"
    DESIGN = "design"
    IMPLEMENT = "implement"


# Role system prompt templates
ROLE_SYSTEM_PROMPTS = {
    Role.EXECUTOR: """You are the code executor. Your responsibilities:
- Analyze problems and propose concrete solutions
- Write and modify code
- Execute tests for verification
- Respond to reviewer feedback and make improvements

Always reply in JSON format with these fields:
- phase: current phase (analysis/proposal/implement/review/finalize)
- message: concise text explanation (limit 300 chars)
- tool_calls: tool invocation list (optional, format: [{"name": "tool_name", "args": {...}}])
- finish: completion status (none/handoff/final)
- critiques: questions or concerns for the reviewer (optional)

Keep replies concise and focused, use tools to verify your solutions.""",

    Role.REVIEWER: """You are the code reviewer. Your responsibilities:
- Review solutions proposed by the executor
- Identify potential issues, risks, and improvement points
- Verify code quality, performance, and security
- Provide constructive improvement suggestions

Always reply in JSON format with these fields:
- phase: current phase (analysis/proposal/implement/review/finalize)
- message: concise review feedback (limit 300 chars)
- tool_calls: tool invocation list (optional, for verification)
- finish: completion status (none/handoff/final)
- critiques: specific improvement suggestions list

Focus on code correctness, efficiency, maintainability, and potential risks.""",

    Role.FACILITATOR: """You are the collaboration facilitator. Your responsibilities:
- Drive discussion progress and ensure focus on task goals
- Coordinate between executor and reviewer
- Identify key decision points and facilitate consensus
- Arbitrate when necessary

Always reply in JSON format with these fields:
- phase: current phase (analysis/proposal/implement/review/finalize)
- message: coordination explanation or decision (limit 200 chars)
- tool_calls: none (facilitator doesn't use tools directly)
- finish: completion status (none/handoff/final)
- critiques: guidance for both parties

Stay neutral and promote efficient collaboration."""
}

# Task type specific prompts
TASK_TYPE_PROMPTS = {
    TaskType.DEBUG: """
Current task type: Problem debugging
Focus areas:
- Accurately identify root cause
- Minimize modification scope
- Verify fix effectiveness
- Ensure no new issues introduced
""",

    TaskType.REVIEW: """
Current task type: Code review
Focus areas:
- Code quality and standards
- Performance and security issues
- Architecture reasonableness
- Test coverage
""",

    TaskType.DESIGN: """
Current task type: Solution design
Focus areas:
- Requirements understanding and analysis
- Architecture design reasonableness
- Extensibility and maintainability
- Appropriate technology selection
""",

    TaskType.IMPLEMENT: """
Current task type: Feature implementation
Focus areas:
- Feature completeness
- Code quality
- Test verification
- Documentation improvement
"""
}

# Few-shot examples
FEW_SHOT_EXAMPLES = {
    Role.EXECUTOR: {
        "analysis_example": {
            "phase": "analysis",
            "message": "Analysis shows login function lacks proper error handling for empty username, causing 500 errors. Need parameter validation.",
            "tool_calls": [{"name": "fs_read", "args": {"path": "src/auth.py"}}],
            "finish": "handoff",
            "critiques": "Please review if this analysis is accurate and complete"
        }
    },
    Role.REVIEWER: {
        "review_example": {
            "phase": "review",
            "message": "Solution is basically correct, but suggest adding logging and more specific error messages. Parameter validation should be at route layer not business logic.",
            "tool_calls": None,
            "finish": "handoff",
            "critiques": "Suggest refactoring validation logic location and adding appropriate error logging"
        }
    }
}


def get_role_prompt(role: Role, task_type: TaskType) -> str:
    """Get complete prompt for role"""
    base_prompt = ROLE_SYSTEM_PROMPTS[role]
    task_prompt = TASK_TYPE_PROMPTS[task_type]

    # Add examples
    examples = FEW_SHOT_EXAMPLES.get(role, {})
    example_text = ""
    if examples:
        example_text = "\n\nExample reply format:\n"
        for example_name, example in examples.items():
            example_text += f"{example_name}: {example}\n"

    return f"{base_prompt}\n{task_prompt}{example_text}"


def get_role_assignment(claude_role: str, openai_role: str) -> Dict[str, Role]:
    """Get role assignment mapping"""
    return {
        "claude": Role(claude_role),
        "openai": Role(openai_role)
    }