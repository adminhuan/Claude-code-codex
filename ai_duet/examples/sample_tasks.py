"""
Sample tasks for AI Duet (clean ASCII)
"""

# Debug tasks
DEBUG_TASKS = [
    "Fix a bug causing 500 error on empty username in login handler",
    "Investigate intermittent timeout in data fetch function",
    "Resolve memory leak in long-running worker",
    "Fix API returning 500 on invalid JWT signature"
]

# Review tasks
REVIEW_TASKS = [
    "Review auth module for security issues",
    "Review pagination implementation for performance",
    "Review configuration loading for error handling",
    "Review REST API for consistency and status codes"
]

# Design tasks
DESIGN_TASKS = [
    "Design a caching layer with Redis",
    "Design a rate limiting strategy for login",
    "Design multi-tenant SaaS auth architecture",
    "Design a background job scheduling system"
]

# Implement tasks
IMPLEMENT_TASKS = [
    "Implement Redis-based deduplication of events",
    "Implement a robust retryable HTTP client",
    "Implement WebSocket broadcast service",
    "Implement a CRUD REST API for tasks"
]

# Complex tasks
COMPLEX_TASKS = [
    "Build a web scraper with politeness and storage",
    "Implement end-to-end user onboarding flow",
    "Build a feature flag system with SDK",
    "Design and implement a CI pipeline for tests"
]


def get_sample_task(task_type: str = "implement", difficulty: str = "medium") -> str:
    """Return a sample task based on type and difficulty."""
    task_pools = {
        "debug": DEBUG_TASKS,
        "review": REVIEW_TASKS,
        "design": DESIGN_TASKS,
        "implement": IMPLEMENT_TASKS,
        "complex": COMPLEX_TASKS,
    }

    tasks = task_pools.get(task_type, IMPLEMENT_TASKS)

    if difficulty == "simple":
        return tasks[0]
    elif difficulty == "hard":
        return tasks[-1]
    else:
        return tasks[len(tasks) // 2]


def list_sample_tasks():
    """Print sample tasks by category."""
    print("Sample tasks for AI Duet\n")

    categories = [
        ("Debug", DEBUG_TASKS),
        ("Review", REVIEW_TASKS),
        ("Design", DESIGN_TASKS),
        ("Implement", IMPLEMENT_TASKS),
        ("Complex", COMPLEX_TASKS),
    ]

    for category, tasks in categories:
        print(f"## {category}")
        for i, task in enumerate(tasks, 1):
            print(f"  {i}. {task}")
        print()


if __name__ == "__main__":
    list_sample_tasks()
