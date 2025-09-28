"""
AI Duet module entry point
Allows running via python -m ai_duet
"""
import asyncio
from .duet import async_main


def main():
    """Synchronous entry point for console scripts"""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()