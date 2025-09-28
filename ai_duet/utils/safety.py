"""
Security and safety utilities
Unified tool sandbox implementation as recommended by Codex
"""
import os
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, Any, List


class ToolSandbox:
    """
    Unified tool sandbox - implements Codex recommended security constraints
    All tool execution goes through this single secure interface
    """

    def __init__(self, sandbox_dir: str = "/tmp/ai_duet_sandbox", project_root: str = None):
        self.sandbox_dir = Path(sandbox_dir).resolve()
        self.project_root = Path(project_root).resolve() if project_root else None

        # Create sandbox directory
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)

        # Security constraints
        self.allowed_commands = [
            "ls", "cat", "grep", "find", "head", "tail", "wc", "echo",
            "git status", "git diff", "git log", "npm test", "python -m pytest",
            "python -c", "node -e"
        ]

        self.blocked_patterns = [
            "rm -rf", "sudo", "curl", "wget", "ssh", "scp", "chmod +x",
            "exec", "eval", "import os", "subprocess", "__import__",
            "&", "|", ";", "$(", "`", "&&", "||"
        ]

        self.dangerous_paths = [
            "/etc/", "/root/", "/home/", "/usr/", "/var/", "/sys/", "/proc/",
            "~/.ssh/", "~/.aws/", "~/.config/", ".env", "id_rsa", "passwd"
        ]

    def validate_path(self, path: str) -> bool:
        """
        Validate file path security with proper realpath checking
        Following Codex recommendation for robust path validation
        """
        try:
            # Check original path first for dangerous patterns
            original_path = str(path)
            for dangerous in self.dangerous_paths:
                if dangerous in original_path:
                    return False

            # Convert to Path object
            path_obj = Path(path)

            # If it's a relative path and safe, allow it
            if not path_obj.is_absolute():
                # Additional safety for relative paths
                if ".." in original_path:
                    return False
                return True

            # For absolute paths, resolve and check boundaries
            path_obj = path_obj.resolve()
            path_str = str(path_obj)

            # Check resolved path for dangerous patterns
            for dangerous in self.dangerous_paths:
                if dangerous in path_str:
                    return False

            # Check if path is within allowed boundaries
            if self.project_root:
                # Allow project root and sandbox
                allowed_roots = [self.project_root, self.sandbox_dir]
                for root in allowed_roots:
                    try:
                        path_obj.relative_to(root)
                        return True
                    except ValueError:
                        continue
                return False
            else:
                # For absolute paths, only allow sandbox
                try:
                    path_obj.relative_to(self.sandbox_dir)
                    return True
                except ValueError:
                    return False

        except Exception:
            return False

    def validate_command(self, command: str) -> bool:
        """
        Validate command security with strict whitelist approach
        Following Codex recommendation for command validation
        """
        # Check for dangerous patterns first
        for pattern in self.blocked_patterns:
            if pattern in command:
                return False

        # Parse command into components
        parts = command.strip().split()
        if not parts:
            return False

        base_command = parts[0]

        # Strict whitelist check
        for allowed in self.allowed_commands:
            if base_command == allowed or command.startswith(allowed + " "):
                return True

        return False

    async def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Unified tool execution interface
        All tools go through this secure gateway
        """
        try:
            if tool_name == "fs_read":
                return await self._safe_fs_read(args)
            elif tool_name == "fs_write":
                return await self._safe_fs_write(args)
            elif tool_name == "fs_list":
                return await self._safe_fs_list(args)
            elif tool_name == "run_command":
                return await self._safe_run_command(args)
            elif tool_name == "run_tests":
                return await self._safe_run_tests(args)
            else:
                return {
                    "error": f"Unknown tool: {tool_name}",
                    "summary": f"Tool '{tool_name}' not supported"
                }

        except Exception as e:
            return {
                "error": f"Tool execution failed: {str(e)}",
                "summary": f"Failed to execute {tool_name}"
            }

    async def _safe_fs_read(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Safe file reading with security constraints"""
        path = args.get("path", "")

        if not self.validate_path(path):
            return {
                "error": "Unsafe file path rejected",
                "summary": f"Path validation failed: {path}"
            }

        try:
            path_obj = Path(path).resolve()

            # Check file size before reading
            if path_obj.stat().st_size > 1_000_000:  # 1MB limit
                return {
                    "error": "File too large (>1MB)",
                    "summary": f"File size exceeds limit: {path}"
                }

            with open(path_obj, 'r', encoding='utf-8') as f:
                content = f.read()

            # Truncate if too long
            if len(content) > 10_000:
                content = content[:10_000] + "\n[... content truncated ...]"

            return {
                "content": content,
                "size": len(content),
                "summary": f"Successfully read {path} ({len(content)} chars)"
            }

        except Exception as e:
            return {
                "error": str(e),
                "summary": f"Failed to read: {path}"
            }

    async def _safe_fs_write(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Safe file writing to sandbox only"""
        path = args.get("path", "")
        content = args.get("content", "")

        # Force write to sandbox directory only
        filename = Path(path).name  # Extract just the filename
        safe_path = self.sandbox_dir / filename

        try:
            # Limit content size
            if len(content) > 100_000:  # 100KB limit
                return {
                    "error": "Content too large (>100KB)",
                    "summary": f"Content size exceeds limit for {filename}"
                }

            with open(safe_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return {
                "path": str(safe_path),
                "summary": f"Successfully wrote to {safe_path}"
            }

        except Exception as e:
            return {
                "error": str(e),
                "summary": f"Failed to write: {filename}"
            }

    async def _safe_fs_list(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Safe directory listing"""
        path = args.get("path", ".")

        if not self.validate_path(path):
            return {
                "error": "Unsafe directory path rejected",
                "summary": f"Path validation failed: {path}"
            }

        try:
            path_obj = Path(path).resolve()
            items = [item.name for item in path_obj.iterdir()]

            # Limit results
            if len(items) > 100:
                items = items[:100]
                truncated = True
            else:
                truncated = False

            return {
                "files": items,
                "count": len(items),
                "truncated": truncated,
                "summary": f"Listed {len(items)} items in {path}"
            }

        except Exception as e:
            return {
                "error": str(e),
                "summary": f"Failed to list: {path}"
            }

    async def _safe_run_command(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Safe command execution with strict controls"""
        command = args.get("command", "")

        if not self.validate_command(command):
            return {
                "error": "Unsafe command rejected",
                "summary": f"Command validation failed: {command}"
            }

        try:
            # Execute with strict security constraints
            result = await asyncio.wait_for(
                asyncio.create_subprocess_shell(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=self.sandbox_dir,
                    env=self._get_safe_env()
                ),
                timeout=30.0  # 30 second timeout
            )

            stdout, stderr = await result.communicate()

            # Decode and truncate output
            stdout_text = stdout.decode('utf-8', errors='replace')[:2000]
            stderr_text = stderr.decode('utf-8', errors='replace')[:500]

            return {
                "stdout": stdout_text,
                "stderr": stderr_text,
                "returncode": result.returncode,
                "summary": f"Executed: {command} (exit code: {result.returncode})"
            }

        except asyncio.TimeoutError:
            return {
                "error": "Command execution timeout",
                "summary": f"Command timed out: {command}"
            }
        except Exception as e:
            return {
                "error": str(e),
                "summary": f"Command execution failed: {command}"
            }

    async def _safe_run_tests(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Safe test execution"""
        test_command = args.get("command", "npm test")

        # Override with safe test commands only
        safe_test_commands = {
            "npm": "npm test",
            "pytest": "python -m pytest",
            "python": "python -m pytest",
            "node": "npm test"
        }

        # Default to npm test if not specified
        if test_command not in safe_test_commands.values():
            test_command = "npm test"

        return await self._safe_run_command({"command": test_command})

    def _get_safe_env(self) -> Dict[str, str]:
        """Get safe environment variables for command execution"""
        # Minimal safe environment
        safe_env = {
            "PATH": "/usr/local/bin:/usr/bin:/bin",
            "HOME": str(self.sandbox_dir),
            "TMPDIR": str(self.sandbox_dir),
            "USER": "sandbox",
            "SHELL": "/bin/bash"
        }

        # Allow some Node.js and Python paths if they exist
        if "NODE_PATH" in os.environ:
            safe_env["NODE_PATH"] = os.environ["NODE_PATH"]
        if "PYTHONPATH" in os.environ:
            safe_env["PYTHONPATH"] = os.environ["PYTHONPATH"]

        return safe_env

    def get_stats(self) -> Dict[str, Any]:
        """Get sandbox statistics"""
        try:
            sandbox_size = sum(f.stat().st_size for f in self.sandbox_dir.rglob('*') if f.is_file())
            file_count = len(list(self.sandbox_dir.rglob('*')))
        except:
            sandbox_size = 0
            file_count = 0

        return {
            "sandbox_dir": str(self.sandbox_dir),
            "project_root": str(self.project_root) if self.project_root else None,
            "sandbox_size_bytes": sandbox_size,
            "file_count": file_count,
            "allowed_commands": len(self.allowed_commands),
            "blocked_patterns": len(self.blocked_patterns)
        }


# Global sandbox instance
_sandbox_instance = None


def get_sandbox(sandbox_dir: str = None, project_root: str = None) -> ToolSandbox:
    """Get or create global sandbox instance"""
    global _sandbox_instance

    if _sandbox_instance is None:
        _sandbox_instance = ToolSandbox(
            sandbox_dir or "/tmp/ai_duet_sandbox",
            project_root
        )

    return _sandbox_instance


def reset_sandbox():
    """Reset global sandbox instance"""
    global _sandbox_instance
    _sandbox_instance = None