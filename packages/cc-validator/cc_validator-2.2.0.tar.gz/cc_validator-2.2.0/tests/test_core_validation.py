#!/usr/bin/env python3
"""
Core validation tests for security, TDD, and tool routing.
"""

import json
import os
import tempfile
from typing import Any

import pytest

# Security Validation Tests


@pytest.mark.quick
@pytest.mark.security
def test_dangerous_bash_command(run_validation: Any) -> None:
    """Test that dangerous bash commands are blocked."""
    returncode, stdout, _ = run_validation("Bash", {"command": "rm -rf /"})
    assert returncode == 2
    response = json.loads(stdout)
    assert response["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert (
        "dangerous"
        in response["hookSpecificOutput"]["permissionDecisionReason"].lower()
    )


@pytest.mark.quick
@pytest.mark.security
def test_safe_bash_command(run_validation: Any) -> None:
    """Test that safe bash commands are allowed."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY not set")

    returncode, stdout, _ = run_validation("Bash", {"command": "ls -la"})
    assert returncode == 0
    response = json.loads(stdout)
    assert response["hookSpecificOutput"]["permissionDecision"] == "allow"


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


# TDD Validation Tests


@pytest.mark.comprehensive
@pytest.mark.tdd
def test_write_implementation_without_test(run_validation: Any) -> None:
    """Test that writing implementation without tests is blocked."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY not set")

    with tempfile.TemporaryDirectory() as temp_dir:
        tool_input = {
            "file_path": os.path.join(temp_dir, "calculator.py"),
            "content": "def add(a, b):\n    return a + b",
        }
        returncode, stdout, _ = run_validation("Write", tool_input)
        assert returncode == 2
        response = json.loads(stdout)
        assert response["hookSpecificOutput"]["permissionDecision"] == "deny"
        assert "TDD" in response["hookSpecificOutput"]["permissionDecisionReason"]


@pytest.mark.comprehensive
@pytest.mark.tdd
def test_write_test_file_allowed(run_validation: Any) -> None:
    """Test that writing test files is allowed."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY not set")

    tool_input = {
        "file_path": "test_calculator.py",
        "content": "import pytest\n\ndef test_add():\n    assert False",
    }
    returncode, stdout, _ = run_validation("Write", tool_input)
    assert returncode == 0
    response = json.loads(stdout)
    assert response["hookSpecificOutput"]["permissionDecision"] == "allow"


# Tool Routing Tests


@pytest.mark.quick
def test_unknown_tool_blocked(run_validation: Any) -> None:
    """Test unknown tools are blocked."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY not set")

    returncode, stdout, _ = run_validation("UnknownTool", {"some": "data"})
    assert returncode == 2
    response = json.loads(stdout)
    assert response["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert (
        "Unhandled tool" in response["hookSpecificOutput"]["permissionDecisionReason"]
    )


# Documentation Validation Tests


@pytest.mark.comprehensive
@pytest.mark.documentation
def test_documentation_skips_tdd_validation(run_validation: Any) -> None:
    """Test that documentation files skip TDD validation."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY not set")

    tool_input = {
        "file_path": "docs/guide.md",
        "content": "# User Guide\n\nThis is documentation.",
    }
    returncode, stdout, _ = run_validation("Write", tool_input)
    assert returncode == 0
    response = json.loads(stdout)
    assert response["hookSpecificOutput"]["permissionDecision"] == "allow"
