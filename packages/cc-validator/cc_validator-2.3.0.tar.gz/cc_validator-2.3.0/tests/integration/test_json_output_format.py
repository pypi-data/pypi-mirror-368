#!/usr/bin/env python3
"""
Tests for correct JSON output format that Claude Code expects.
"""

import json
import os
import sys
import subprocess
import tempfile
import pytest
from typing import Dict, Any


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
