#!/usr/bin/env python3
"""
Core TDD validation tests.
"""

import json
import os
import tempfile
from typing import Any

import pytest


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