#!/usr/bin/env python3
"""
Comprehensive TDD enforcement tests for all file operations.
"""

import json
import os
import tempfile
from typing import Any

import pytest


def assert_blocked(
    run_validation: Any,
    tool_name: str,
    tool_input: dict,
    expected_reason_fragment: str = "",
) -> None:
    """Assert that the tool operation is blocked."""
    returncode, stdout, stderr = run_validation(tool_name, tool_input)
    assert (
        returncode == 2
    ), f"Expected operation to be blocked, but it was allowed. stdout: {stdout}"
    try:
        response = json.loads(stdout)
        reason = response.get("hookSpecificOutput", {}).get(
            "permissionDecisionReason", ""
        )
        if expected_reason_fragment:
            # Support both "multiple" and "new tests" language patterns
            if expected_reason_fragment.lower() == "multiple":
                assert (
                    "multiple" in reason.lower()
                    or "new tests" in reason.lower()
                    or "2 new tests" in reason.lower()
                )
            else:
                assert expected_reason_fragment.lower() in reason.lower()
    except json.JSONDecodeError:
        pytest.fail(f"Failed to decode JSON from stdout: {stdout}")


def assert_allowed(run_validation: Any, tool_name: str, tool_input: dict) -> None:
    """Assert that the tool operation is allowed."""
    returncode, stdout, stderr = run_validation(tool_name, tool_input)
    assert (
        returncode == 0
    ), f"Expected operation to be allowed, but it was blocked. stdout: {stdout}"


def test_write_implementation_without_test(run_validation: Any) -> None:
    """Write tool should block implementation without test."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY not set")

    assert_blocked(
        run_validation,
        "Write",
        {"file_path": "calculator.py", "content": "def add(a, b):\n    return a + b\n"},
        "TDD",
    )


def test_write_test_file(run_validation: Any) -> None:
    """Write tool should allow test files."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY not set")

    assert_allowed(
        run_validation,
        "Write",
        {
            "file_path": "test_simple_validation.py",
            "content": "import pytest\n\ndef test_example():\n    assert False\n",
        },
    )


def test_update_implementation_without_test(run_validation: Any) -> None:
    """Update tool should block implementation without test."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY not set")

    assert_blocked(
        run_validation,
        "Update",
        {
            "file_path": "calculator.py",
            "content": "def multiply(a, b):\n    return a * b\n",
        },
        "TDD",
    )


def test_write_test_file_should_allow(run_validation: Any) -> None:
    """Write tool should allow test files."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY not set")

    assert_allowed(
        run_validation,
        "Write",
        {
            "file_path": "test_write_allowed.py",
            "content": "import pytest\n\ndef test_example():\n    assert False\n",
        },
    )


def test_update_add_one_test_to_existing(run_validation: Any) -> None:
    """Update adding one new failing test to existing file should be allowed."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY not set")

    with tempfile.NamedTemporaryFile(mode="w", suffix="_test.py", delete=False) as f:
        f.write("def test_existing():\n    assert True\n")
        test_file = f.name
    try:
        assert_allowed(
            run_validation,
            "Update",
            {
                "file_path": test_file,
                "content": "def test_existing():\n    assert True\n\ndef test_new():\n    assert False\n",
            },
        )
    finally:
        os.unlink(test_file)


def test_update_add_multiple_tests_to_existing(run_validation: Any) -> None:
    """Update adding multiple new tests to existing file should be blocked."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY not set")

    with tempfile.NamedTemporaryFile(mode="w", suffix="_test.py", delete=False) as f:
        f.write("def test_existing():\n    assert True\n")
        test_file = f.name
    try:
        assert_blocked(
            run_validation,
            "Update",
            {
                "file_path": test_file,
                "content": "def test_existing():\n    assert True\n\ndef test_new_one():\n    assert True\n\ndef test_new_two():\n    assert True\n",
            },
            "multiple",
        )
    finally:
        os.unlink(test_file)


def test_edit_adds_multiple_tests(run_validation: Any) -> None:
    """Edit tool should block adding multiple tests."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY not set")

    assert_blocked(
        run_validation,
        "Edit",
        {
            "file_path": "test_edit_multiple_calculator.py",
            "old_string": "def test_add():\n    assert True",
            "new_string": "def test_add():\n    assert True\n\ndef test_subtract():\n    assert True\n\ndef test_multiply():\n    assert True",
        },
        "multiple",
    )


def test_edit_single_test(run_validation: Any) -> None:
    """Edit tool should allow adding single test."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY not set")

    assert_allowed(
        run_validation,
        "Edit",
        {
            "file_path": "test_edit_single_calculator.py",
            "old_string": "# Empty test file",
            "new_string": "def test_add():\n    assert False",
        },
    )


def test_multiedit_multiple_tests(run_validation: Any) -> None:
    """MultiEdit should block if total new tests > 1."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY not set")

    edits = [
        {
            "old_string": "# tests here",
            "new_string": "def test_add():\n    assert True",
        },
        {
            "old_string": "# more tests",
            "new_string": "def test_subtract():\n    assert True",
        },
    ]
    assert_blocked(
        run_validation,
        "MultiEdit",
        {"file_path": "test_multiedit_multiple_calculator.py", "edits": edits},
        "multiple",
    )


def test_multiedit_single_test(run_validation: Any) -> None:
    """MultiEdit should allow single test across edits."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY not set")

    edits = [
        {"old_string": "# setup", "new_string": "import calculator"},
        {"old_string": "# test", "new_string": "def test_add():\n    assert False"},
    ]
    assert_allowed(
        run_validation,
        "MultiEdit",
        {"file_path": "test_multiedit_single_calculator.py", "edits": edits},
    )


def test_write_with_comments(run_validation: Any) -> None:
    """Write should block code with comments."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY not set")

    assert_blocked(
        run_validation,
        "Write",
        {
            "file_path": "example.py",
            "content": "# This is a comment\ndef hello():\n    return 'world'  # inline comment\n",
        },
        "comment",
    )


def test_write_no_comments(run_validation: Any) -> None:
    """Write should allow code without comments."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY not set")

    assert_allowed(
        run_validation,
        "Write",
        {
            "file_path": "test_write_no_comments_example.py",
            "content": "def test_hello():\n    assert False\n",
        },
    )


@pytest.mark.parametrize(
    "filename, content",
    [
        ("__init__.py", ""),
        ("__init__.py", "from .module import function"),
        ("setup.py", "from setuptools import setup\n\nsetup(name='test')"),
        ("config.toml", "[tool.test]\nkey = 'value'"),
    ],
)
def test_structural_files(run_validation: Any, filename: str, content: str) -> None:
    """Structural files should be allowed without TDD."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY not set")

    assert_allowed(run_validation, "Write", {"file_path": filename, "content": content})


@pytest.mark.comprehensive
@pytest.mark.tdd
def test_write_implementation_without_test_tempfile(run_validation: Any) -> None:
    """Test that writing implementation without tests is blocked (using temp file)."""
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
def test_write_test_file_allowed_direct(run_validation: Any) -> None:
    """Test that writing test files is allowed (direct validation)."""
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
