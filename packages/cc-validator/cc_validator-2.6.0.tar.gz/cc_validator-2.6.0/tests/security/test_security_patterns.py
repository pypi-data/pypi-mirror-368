#!/usr/bin/env python3
"""
Security pattern validation tests.
"""

import json
import os
from typing import Any
import pytest


@pytest.mark.unit
@pytest.mark.quick
@pytest.mark.security
@pytest.mark.parametrize(
    "command, reason_keyword",
    [
        ("rm -rf /", "dangerous"),
        ("sudo rm -rf /", "dangerous"),
        ("dd if=/dev/zero of=/dev/sda", "dangerous"),
        ("mkfs.ext4 /dev/sda", "dangerous"),
        ("> /dev/sda", "dangerous"),
        ("chmod -R 777 /", "dangerous"),
        ("chown -R nobody:nobody /", "dangerous"),
    ],
)
def test_dangerous_bash_commands(
    run_validation: Any, command: str, reason_keyword: str
) -> None:
    """Test that dangerous bash commands are blocked."""
    returncode, stdout, stderr = run_validation("Bash", {"command": command})
    assert returncode == 2, f"Expected dangerous command '{command}' to be blocked"
    response = json.loads(stdout)
    hook_output = response["hookSpecificOutput"]
    assert hook_output["permissionDecision"] == "deny"
    assert reason_keyword in hook_output["permissionDecisionReason"].lower()


@pytest.mark.unit
@pytest.mark.quick
@pytest.mark.security
@pytest.mark.parametrize(
    "command",
    [
        "ls -la",
        "pwd",
        "echo 'Hello World'",
        "cd src",
        "mkdir test_dir",
        "npm test",
        "git status",
        "node -v",
        "cat README.md",
    ],
)
def test_safe_bash_commands(run_validation: Any, command: str) -> None:
    """Test that safe bash commands are allowed."""
    returncode, stdout, stderr = run_validation("Bash", {"command": command})
    assert returncode == 0, f"Expected safe command '{command}' to be allowed"
    response = json.loads(stdout)
    assert response["hookSpecificOutput"]["permissionDecision"] == "allow"


@pytest.mark.unit
@pytest.mark.quick
@pytest.mark.security
@pytest.mark.parametrize(
    "command, suggested_tool",
    [
        ("grep -r 'pattern' .", "rg"),
        ("find . -name '*.py'", "rg"),
    ],
)
def test_tool_enforcement_commands(
    run_validation: Any, command: str, suggested_tool: str
) -> None:
    """Test that commands with better alternatives are blocked with a suggestion."""
    returncode, stdout, stderr = run_validation("Bash", {"command": command})
    assert returncode == 2, f"Expected command '{command}' to be blocked"
    response = json.loads(stdout)
    assert response["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert suggested_tool in response["hookSpecificOutput"]["permissionDecisionReason"]


@pytest.mark.comprehensive
@pytest.mark.security
def test_api_key_in_write(run_validation: Any) -> None:
    """Test that API keys in written files are blocked."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY not set")

    tool_input = {
        "file_path": "config.py",
        "content": "STRIPE_KEY = 'sk_live_abcdef1234567890abcdef1234567890'",
    }
    returncode, stdout, _ = run_validation("Write", tool_input)
    assert returncode == 2
    response = json.loads(stdout)
    assert response["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert "secret" in response["hookSpecificOutput"]["permissionDecisionReason"]
