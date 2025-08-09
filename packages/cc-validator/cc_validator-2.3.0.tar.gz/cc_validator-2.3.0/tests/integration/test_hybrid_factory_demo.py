#!/usr/-bin/env python3
"""
Demo tests for the consolidated run_validation fixture.
"""

import json
import os
from typing import Any

import pytest


def test_run_validation_fixture_usage(run_validation: Any) -> None:
    """Demo: Using the consolidated run_validation fixture."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY not set")

    tool_name = "Write"
    tool_input = {"file_path": "demo.txt", "content": "Hello, world!"}

    returncode, stdout, stderr = run_validation(tool_name, tool_input)

    # With API key present, simple writes should be allowed
    assert returncode == 0, f"Expected success with API key, stderr: {stderr}"

    # Verify the output is a valid JSON response
    try:
        response = json.loads(stdout)
        assert "hookSpecificOutput" in response
        assert response["hookSpecificOutput"]["permissionDecision"] == "allow"
    except json.JSONDecodeError:
        pytest.fail(f"Output was not valid JSON: {stdout}")
