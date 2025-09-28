#!/usr/bin/env python3
"""
Test script to verify all Codex-recommended fixes
Tests the critical path without requiring API keys
"""
import asyncio
import sys
from pathlib import Path


def test_imports():
    """Test that all modules can be imported without errors"""
    print("🧪 Testing imports...")

    try:
        # Test core protocol imports
        from ai_duet.protocols.conversation import (
            Phase, FinishStatus, AgentReply, validate_agent_reply,
            StateMachine, ConversationManager
        )
        print("✅ Core protocols import successful")

        # Test roles import
        from ai_duet.protocols.roles import Role, TaskType, get_role_prompt
        print("✅ Roles module import successful")

        # Test agents import
        from ai_duet.agents.base_agent import BaseAgent, RetryableAgent
        from ai_duet.agents.openai_agent import OpenAIAgent, OpenAIProviderWithFallback
        from ai_duet.agents.claude_agent import ClaudeAgent, ClaudeAgentWithSandbox
        print("✅ Agent modules import successful")

        # Test utils import
        from ai_duet.utils.safety import ToolSandbox, get_sandbox
        from ai_duet.utils.config import DuetConfig, load_config_from_env
        print("✅ Utils modules import successful")

        # Test main orchestrator
        from ai_duet.duet import DuetOrchestrator, async_main
        print("✅ Main orchestrator import successful")

        # Test entry point
        from ai_duet.__main__ import main
        print("✅ Entry point import successful")

        return True

    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def test_json_protocol():
    """Test JSON protocol validation"""
    print("\n🧪 Testing JSON protocol...")

    try:
        from ai_duet.protocols.conversation import validate_agent_reply, create_error_reply, Phase

        # Test valid reply
        valid_reply = {
            "phase": "analysis",
            "message": "Test message",
            "tool_calls": [],
            "finish": "handoff",
            "critiques": "Test critique"
        }

        validated = validate_agent_reply(valid_reply)
        assert validated["phase"] == Phase.ANALYSIS
        assert validated["message"] == "Test message"
        print("✅ Valid reply validation passed")

        # Test invalid reply should raise error
        invalid_reply = {
            "phase": "invalid_phase",
            "message": "test",
            "finish": "handoff"
        }

        try:
            validate_agent_reply(invalid_reply)
            print("❌ Invalid reply should have been rejected")
            return False
        except ValueError:
            print("✅ Invalid reply correctly rejected")

        # Test error reply creation
        error_reply = create_error_reply("Test error")
        assert "系统错误" in error_reply["message"]
        print("✅ Error reply creation works")

        return True

    except Exception as e:
        print(f"❌ JSON protocol test failed: {e}")
        return False


def test_state_machine():
    """Test state machine logic"""
    print("\n🧪 Testing state machine...")

    try:
        from ai_duet.protocols.conversation import StateMachine, Phase, FinishStatus

        sm = StateMachine()

        # Test initial state
        assert sm.current_phase == Phase.ANALYSIS
        assert sm.current_speaker == "executor"
        print("✅ Initial state correct")

        # Test state transition
        reply = {
            "phase": Phase.ANALYSIS,
            "message": "Analysis complete",
            "tool_calls": [],
            "finish": FinishStatus.HANDOFF,
            "critiques": ""
        }

        next_phase, next_speaker = sm.next_state(reply, "executor")
        assert next_phase == Phase.PROPOSAL
        assert next_speaker == "executor"
        print("✅ State transition analysis -> proposal works")

        return True

    except Exception as e:
        print(f"❌ State machine test failed: {e}")
        return False


def test_sandbox():
    """Test tool sandbox"""
    print("\n🧪 Testing tool sandbox...")

    try:
        from ai_duet.utils.safety import ToolSandbox

        sandbox = ToolSandbox()

        # Test path validation
        assert sandbox.validate_path("test.txt") == True
        assert sandbox.validate_path("../etc/passwd") == False
        assert sandbox.validate_path("/etc/passwd") == False
        print("✅ Path validation works")

        # Test command validation
        assert sandbox.validate_command("ls -la") == True
        assert sandbox.validate_command("rm -rf /") == False
        assert sandbox.validate_command("sudo rm file") == False
        print("✅ Command validation works")

        return True

    except Exception as e:
        print(f"❌ Sandbox test failed: {e}")
        return False


def test_entry_point():
    """Test that entry point can be called"""
    print("\n🧪 Testing entry point...")

    try:
        from ai_duet.__main__ import main

        # Test that main function exists and is callable
        assert callable(main)
        print("✅ Entry point is callable")

        # We can't actually run it without args, but structure is correct
        return True

    except Exception as e:
        print(f"❌ Entry point test failed: {e}")
        return False


async def test_dry_run():
    """Test dry run mode"""
    print("\n🧪 Testing dry run mode...")

    try:
        # Set environment variables for testing
        import os
        os.environ["OPENAI_API_KEY"] = "test-key"
        os.environ["ANTHROPIC_API_KEY"] = "test-key"

        from ai_duet.utils.config import load_config_from_env, update_config_from_args
        from ai_duet.duet import DuetOrchestrator

        # Load config
        config = load_config_from_env()
        config = update_config_from_args(config, {
            "enable_dry_run": True,
            "max_turns": 3
        })

        # Create orchestrator
        orchestrator = DuetOrchestrator(config)

        # Run dry mode test
        result = await orchestrator.run_duet("Test task for dry run")

        assert result["success"] == True
        assert result["turns"] >= 1
        print("✅ Dry run mode works")

        return True

    except Exception as e:
        print(f"❌ Dry run test failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("🚀 Running comprehensive fix verification tests...\n")

    tests = [
        ("Module Imports", test_imports),
        ("JSON Protocol", test_json_protocol),
        ("State Machine", test_state_machine),
        ("Tool Sandbox", test_sandbox),
        ("Entry Point", test_entry_point),
        ("Dry Run Mode", test_dry_run)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()

            if result:
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")

    print(f"\n{'='*50}")
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All fixes verified successfully!")
        print("\n✅ Codex recommendations implemented:")
        print("  - Fixed encoding issues and corruption")
        print("  - Unified class names and interfaces")
        print("  - Aligned state machine with orchestrator")
        print("  - Fixed enum/string consistency")
        print("  - Unified tool sandbox implementation")
        print("  - Fixed entry point script")
        print("\n🚀 System is now ready for real collaboration!")
    else:
        print(f"⚠️  {total - passed} tests failed - needs attention")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)