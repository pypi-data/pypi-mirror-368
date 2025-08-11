#!/usr/bin/env python3
"""
Integration tests for Claude Code hook execution.
"""

import json
import os
import subprocess
import sys
import tempfile
import time
from typing import Dict, Any, Tuple, Optional
import signal
import pytest


# Helper function to invoke the hook, can be moved to a fixture later
def invoke_hook(
    tool_name: str,
    tool_input: Dict[str, Any],
    env_vars: Optional[Dict[str, str]] = None,
    timeout_ms: int = 30000,
) -> Tuple[int, str, str, float]:
    """Invokes the validator hook with timeout handling."""
    start_time = time.time()
    timeout_seconds = timeout_ms / 1000.0

    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        f.write('{"role": "user", "content": "Test command"}\n')
        transcript_path = f.name

    hook_input = {
        "session_id": "test-session-123",
        "transcript_path": transcript_path,
        "hook_event_name": "PreToolUse",
        "tool_name": tool_name,
        "tool_input": tool_input,
    }

    env = os.environ.copy()
    if env_vars:
        env.update(env_vars)

    try:
        process = subprocess.Popen(
            ["uv", "run", "python", "-m", "cc_validator"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
            preexec_fn=os.setsid if sys.platform != "win32" else None,
        )
        stdout, stderr = process.communicate(
            input=json.dumps(hook_input), timeout=timeout_seconds
        )
        exit_code = process.returncode
    except subprocess.TimeoutExpired:
        if sys.platform != "win32":
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        else:
            process.terminate()
        stdout, stderr = process.communicate()
        exit_code = -1
        stderr = f"TIMEOUT: Hook execution exceeded {timeout_ms}ms limit\n{stderr}"
    finally:
        os.unlink(transcript_path)

    duration_ms = (time.time() - start_time) * 1000
    return exit_code, stdout, stderr, duration_ms


def test_write_with_api_key() -> None:
    """Test Write operation with API key - writing documentation should be allowed"""
    exit_code, _, _, duration_ms = invoke_hook(
        "Write",
        {"file_path": "README.md", "content": "# My Project"},
        env_vars={"GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", "")},
    )
    assert exit_code == 0
    assert duration_ms < 15000


def test_dangerous_bash_command() -> None:
    """Test that dangerous Bash commands are blocked"""
    exit_code, stdout, _, _ = invoke_hook("Bash", {"command": "rm -rf /"})
    assert exit_code == 2
    response = json.loads(stdout)
    hook_output = response["hookSpecificOutput"]
    assert hook_output["permissionDecision"] == "deny"
    assert "dangerous" in hook_output["permissionDecisionReason"].lower()


@pytest.mark.parametrize(
    "command",
    ["ls -la", "pwd", "echo 'Hello World'", "npm test", "git status"],
)
def test_safe_bash_commands_allowed(command: str) -> None:
    """Test that safe Bash commands are allowed."""
    exit_code, stdout, _, _ = invoke_hook(
        "Bash",
        {"command": command},
        env_vars={"GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", "")},
    )
    assert exit_code == 0
    response = json.loads(stdout)
    assert response["hookSpecificOutput"]["permissionDecision"] == "allow"


def test_todowrite_operation() -> None:
    """Test TodoWrite operation is always allowed."""
    exit_code, _, _, _ = invoke_hook(
        "TodoWrite",
        {"todos": [{"id": "1", "task": "Test task", "status": "pending"}]},
    )
    assert exit_code == 0


def test_write_with_production_secrets() -> None:
    """Test that production secrets are blocked"""
    exit_code, stdout, _, _ = invoke_hook(
        "Write",
        {
            "file_path": "config.py",
            "content": 'API_KEY = "sk_live_1234567890abcdefghijklmnop"',
        },
        env_vars={"GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", "")},
    )
    assert exit_code == 2
    response = json.loads(stdout)
    assert response["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert (
        "security" in response["hookSpecificOutput"]["permissionDecisionReason"].lower()
    )


def test_timeout_handling() -> None:
    """Test that timeouts are handled correctly"""
    exit_code, _, stderr, duration_ms = invoke_hook(
        "Write",
        {"file_path": "test.py", "content": "x" * 1000000},
        timeout_ms=100,
    )
    assert exit_code == -1
    assert "TIMEOUT" in stderr
    assert duration_ms < 200


def test_json_output_allowed_operation() -> None:
    """Test JSON output format for allowed operations"""
    _, stdout, stderr, _ = invoke_hook(
        "Write",
        {"file_path": "demo.txt", "content": "Hello, world!"},
        env_vars={"GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", "")},
    )
    response = json.loads(stdout)
    hook_output = response["hookSpecificOutput"]
    assert hook_output["permissionDecision"] == "allow"
    assert hook_output["permissionDecisionReason"] == "Operation approved"
    assert stderr == ""


def test_json_output_blocked_operation() -> None:
    """Test JSON output format for blocked operations"""
    exit_code, stdout, stderr, _ = invoke_hook("Bash", {"command": "rm -rf /"})
    assert exit_code == 2
    response = json.loads(stdout)
    hook_output = response["hookSpecificOutput"]
    assert hook_output["permissionDecision"] == "deny"
    assert "❌" in hook_output["permissionDecisionReason"]
    assert stderr == ""


def invoke_validator(hook_input: Dict[str, Any]) -> tuple[str, str, int]:
    """Invoke the validator with given input and return stdout, stderr, exit_code"""
    # Create a temporary transcript file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        f.write('{"role": "user", "content": "Test command"}\n')
        transcript_path = f.name

    hook_input["transcript_path"] = transcript_path

    try:
        # Run the validator
        process = subprocess.Popen(
            [sys.executable, "-m", "cc_validator.main"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        stdout, stderr = process.communicate(input=json.dumps(hook_input), timeout=5)
        exit_code = process.returncode

        return stdout, stderr, exit_code
    finally:
        # Cleanup
        if os.path.exists(transcript_path):
            os.unlink(transcript_path)


class TestJSONOutputFormat:
    """Test that JSON output follows Claude Code's expected format"""

    def test_successful_operation_json_format(self) -> None:
        """Test JSON format for approved operations"""
        hook_input = {
            "tool_name": "TodoWrite",
            "tool_input": {"todos": []},
            "hook_event_name": "PreToolUse",
        }

        stdout, stderr, exit_code = invoke_validator(hook_input)

        # Parse JSON
        try:
            response = json.loads(stdout)
        except json.JSONDecodeError:
            pytest.fail(f"Invalid JSON output: {stdout}")

        # Verify new format with hookSpecificOutput wrapper
        assert "hookSpecificOutput" in response, "Missing hookSpecificOutput wrapper"
        hook_output = response["hookSpecificOutput"]

        assert hook_output["hookEventName"] == "PreToolUse"
        assert hook_output["permissionDecision"] == "allow"
        assert hook_output["permissionDecisionReason"] == "Operation approved"

        # Should NOT have top-level permissionDecision
        assert "permissionDecision" not in response
        assert "permissionDecisionReason" not in response

    def test_blocked_operation_json_format(self) -> None:
        """Test JSON format for blocked operations"""
        hook_input = {
            "tool_name": "Bash",
            "tool_input": {"command": "rm -rf /"},
            "hook_event_name": "PreToolUse",
        }

        stdout, stderr, exit_code = invoke_validator(hook_input)

        # Parse JSON
        try:
            response = json.loads(stdout)
        except json.JSONDecodeError:
            pytest.fail(f"Invalid JSON output: {stdout}")

        # Verify new format with hookSpecificOutput wrapper
        assert "hookSpecificOutput" in response, "Missing hookSpecificOutput wrapper"
        hook_output = response["hookSpecificOutput"]

        assert hook_output["hookEventName"] == "PreToolUse"
        assert hook_output["permissionDecision"] == "deny"
        assert "dangerous" in hook_output["permissionDecisionReason"].lower()

        # Should NOT have top-level permissionDecision
        assert "permissionDecision" not in response
        assert "permissionDecisionReason" not in response

    def test_missing_api_key_json_format(self) -> None:
        """Test JSON format when API key is missing"""
        # Temporarily unset API key
        original_api_key = os.environ.pop("GEMINI_API_KEY", None)

        try:
            hook_input = {
                "tool_name": "Write",
                "tool_input": {"file_path": "test.py", "content": "print('hello')"},
                "hook_event_name": "PreToolUse",
            }

            stdout, stderr, exit_code = invoke_validator(hook_input)

            # Parse JSON
            try:
                response = json.loads(stdout)
            except json.JSONDecodeError:
                pytest.fail(f"Invalid JSON output: {stdout}")

            # Verify new format with hookSpecificOutput wrapper
            assert (
                "hookSpecificOutput" in response
            ), "Missing hookSpecificOutput wrapper"
            hook_output = response["hookSpecificOutput"]

            assert hook_output["hookEventName"] == "PreToolUse"
            assert hook_output["permissionDecision"] == "deny"
            assert "GEMINI_API_KEY" in hook_output["permissionDecisionReason"]

            # Should NOT have top-level permissionDecision
            assert "permissionDecision" not in response
            assert "permissionDecisionReason" not in response

        finally:
            # Restore API key
            if original_api_key:
                os.environ["GEMINI_API_KEY"] = original_api_key

    def test_invalid_json_input_format(self) -> None:
        """Test JSON format when input is invalid"""
        # Send invalid JSON
        process = subprocess.Popen(
            [sys.executable, "-m", "cc_validator.main"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        stdout, stderr = process.communicate(input="invalid json {", timeout=5)

        # Parse JSON
        try:
            response = json.loads(stdout)
        except json.JSONDecodeError:
            pytest.fail(f"Invalid JSON output: {stdout}")

        # Verify new format with hookSpecificOutput wrapper
        assert "hookSpecificOutput" in response, "Missing hookSpecificOutput wrapper"
        hook_output = response["hookSpecificOutput"]

        assert hook_output["hookEventName"] == "PreToolUse"
        assert hook_output["permissionDecision"] == "allow"
        assert "Invalid JSON input" in hook_output["permissionDecisionReason"]

        # Should NOT have top-level permissionDecision
        assert "permissionDecision" not in response
        assert "permissionDecisionReason" not in response
