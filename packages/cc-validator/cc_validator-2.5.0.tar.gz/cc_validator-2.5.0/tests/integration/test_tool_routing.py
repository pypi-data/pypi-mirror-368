#!/usr/bin/env python3
"""
Tool routing and miscellaneous integration tests.
"""

import json
import os
from typing import Any

import pytest


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
