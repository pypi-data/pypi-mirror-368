#!/usr/bin/env python3

from typing import Any
from unittest.mock import patch, MagicMock, call
import subprocess
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cc_validator.validation_logic import BranchValidationPureFunctions


# No fixture needed - using pure functions


@patch.dict(os.environ, {"CLAUDE_TEST_BRANCH": ""}, clear=False)
@patch("subprocess.run")
def test_basic_branch_detection(mock_run: Any) -> None:
    mock_run.return_value = MagicMock(stdout="feature/test-branch\n", returncode=0)

    branch = BranchValidationPureFunctions.get_current_branch()

    assert branch == "feature/test-branch"
    mock_run.assert_called_once_with(
        ["git", "branch", "--show-current"],
        capture_output=True,
        text=True,
        timeout=5,
        cwd=os.getcwd(),
    )


@patch.object(BranchValidationPureFunctions, "get_current_branch")
def test_protected_branch_validation(mock_get_branch: Any) -> None:
    mock_get_branch.return_value = "main"
    assert BranchValidationPureFunctions.is_protected_branch() is True

    mock_get_branch.return_value = "feature/my-feature"
    assert BranchValidationPureFunctions.is_protected_branch() is False


def test_main_branch_file_restrictions() -> None:
    assert BranchValidationPureFunctions.is_allowed_file_on_main("README.md") is True
    assert (
        BranchValidationPureFunctions.is_allowed_file_on_main("docs/guide.md") is True
    )
    assert BranchValidationPureFunctions.is_allowed_file_on_main("src/main.py") is False
    assert (
        BranchValidationPureFunctions.is_allowed_file_on_main("tests/test_example.py")
        is False
    )


@patch.object(BranchValidationPureFunctions, "is_protected_branch")
def test_feature_branch_permissions(mock_is_protected: Any) -> None:
    mock_is_protected.return_value = False

    result = BranchValidationPureFunctions.validate_branch_workflow("src/main.py")

    assert result is None


def test_issue_number_extraction() -> None:
    assert BranchValidationPureFunctions.extract_issue_number("123-fix-bug") == "123"
    assert (
        BranchValidationPureFunctions.extract_issue_number("42-add-feature-xyz") == "42"
    )
    assert (
        BranchValidationPureFunctions.extract_issue_number("feature/my-feature") is None
    )
    assert BranchValidationPureFunctions.extract_issue_number("main") is None


@patch.object(BranchValidationPureFunctions, "is_protected_branch")
@patch.object(BranchValidationPureFunctions, "get_current_branch")
def test_main_branch_code_blocking(
    mock_get_branch: Any, mock_is_protected: Any
) -> None:
    mock_get_branch.return_value = "main"
    mock_is_protected.return_value = True

    result = BranchValidationPureFunctions.validate_branch_workflow("src/main.py")

    assert result is not None
    assert result["approved"] is False
    assert "protected branch" in result["reason"]
    assert isinstance(result["suggestions"], list)


@patch.object(BranchValidationPureFunctions, "is_protected_branch")
def test_main_branch_docs_allowed(mock_is_protected: Any) -> None:
    mock_is_protected.return_value = True

    result = BranchValidationPureFunctions.validate_branch_workflow("README.md")

    assert result is None


@patch("subprocess.run")
def test_validate_issue_exists_when_issue_found(mock_run: Any) -> None:
    mock_run.return_value = MagicMock(returncode=0)

    result = BranchValidationPureFunctions.validate_issue_exists("123")

    assert result is True
    mock_run.assert_called_once_with(
        ["gh", "issue", "view", "123"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=os.getcwd(),
    )


@patch("subprocess.run")
def test_validate_issue_exists_when_issue_not_found(mock_run: Any) -> None:
    mock_run.return_value = MagicMock(returncode=1)

    result = BranchValidationPureFunctions.validate_issue_exists("999")

    assert result is False
    mock_run.assert_called_once_with(
        ["gh", "issue", "view", "999"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=os.getcwd(),
    )


@patch("subprocess.run")
def test_validate_issue_exists_when_gh_command_not_found(mock_run: Any) -> None:
    mock_run.side_effect = FileNotFoundError("gh command not found")

    result = BranchValidationPureFunctions.validate_issue_exists("123")

    assert result is True
    mock_run.assert_called_once_with(
        ["gh", "issue", "view", "123"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=os.getcwd(),
    )


@patch("subprocess.run")
def test_validate_issue_exists_when_command_times_out(mock_run: Any) -> None:
    mock_run.side_effect = subprocess.TimeoutExpired(["gh", "issue", "view", "123"], 10)

    result = BranchValidationPureFunctions.validate_issue_exists("123")

    assert result is False
    mock_run.assert_called_once_with(
        ["gh", "issue", "view", "123"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=os.getcwd(),
    )


@patch("subprocess.run")
@patch("os.getcwd")
def test_validate_issue_exists_with_different_working_directory(
    mock_getcwd: Any, mock_run: Any
) -> None:
    mock_getcwd.return_value = "/custom/working/directory"
    mock_run.return_value = MagicMock(returncode=0)

    result = BranchValidationPureFunctions.validate_issue_exists("456")

    assert result is True
    mock_run.assert_called_once_with(
        ["gh", "issue", "view", "456"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd="/custom/working/directory",
    )


@patch("subprocess.run")
def test_validate_issue_exists_with_general_exception(mock_run: Any) -> None:
    mock_run.side_effect = RuntimeError("Unexpected error")

    result = BranchValidationPureFunctions.validate_issue_exists("123")

    assert result is False
    mock_run.assert_called_once_with(
        ["gh", "issue", "view", "123"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=os.getcwd(),
    )


@patch("subprocess.run")
def test_validate_issue_exists_with_different_issue_numbers(mock_run: Any) -> None:
    mock_run.return_value = MagicMock(returncode=0)

    test_cases = ["1", "42", "999", "12345"]

    for issue_number in test_cases:
        result = BranchValidationPureFunctions.validate_issue_exists(issue_number)
        assert result is True

    expected_calls = [
        call(
            ["gh", "issue", "view", issue_number],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=os.getcwd(),
        )
        for issue_number in test_cases
    ]

    assert mock_run.call_count == len(test_cases)
    mock_run.assert_has_calls(expected_calls)


@patch("subprocess.run")
def test_validate_issue_exists_ensures_cwd_parameter_always_passed(
    mock_run: Any,
) -> None:
    mock_run.return_value = MagicMock(returncode=0)

    BranchValidationPureFunctions.validate_issue_exists("123")

    call_kwargs = mock_run.call_args[1]
    assert "cwd" in call_kwargs
    assert call_kwargs["cwd"] == os.getcwd()
