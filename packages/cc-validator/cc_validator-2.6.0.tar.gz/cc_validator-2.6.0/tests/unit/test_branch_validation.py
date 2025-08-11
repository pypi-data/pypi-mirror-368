#!/usr/bin/env python3

from typing import Any
from unittest.mock import patch, MagicMock
import subprocess
import os
import sys

import pytest

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
    assert BranchValidationPureFunctions.is_allowed_file_on_main("docs/guide.md") is True
    assert BranchValidationPureFunctions.is_allowed_file_on_main("src/main.py") is False
    assert BranchValidationPureFunctions.is_allowed_file_on_main("tests/test_example.py") is False


@patch.object(BranchValidationPureFunctions, "is_protected_branch")
def test_feature_branch_permissions(
    mock_is_protected: Any) -> None:
    mock_is_protected.return_value = False

    result = BranchValidationPureFunctions.validate_branch_workflow("src/main.py")

    assert result is None


def test_issue_number_extraction() -> None:
    assert BranchValidationPureFunctions.extract_issue_number("123-fix-bug") == "123"
    assert BranchValidationPureFunctions.extract_issue_number("42-add-feature-xyz") == "42"
    assert BranchValidationPureFunctions.extract_issue_number("feature/my-feature") is None
    assert BranchValidationPureFunctions.extract_issue_number("main") is None


@patch.object(BranchValidationPureFunctions, "is_protected_branch")
@patch.object(BranchValidationPureFunctions, "get_current_branch")
def test_main_branch_code_blocking(
    mock_get_branch: Any, mock_is_protected: Any) -> None:
    mock_get_branch.return_value = "main"
    mock_is_protected.return_value = True

    result = BranchValidationPureFunctions.validate_branch_workflow("src/main.py")

    assert result is not None
    assert result["approved"] is False
    assert "protected branch" in result["reason"]
    assert isinstance(result["suggestions"], list)


@patch.object(BranchValidationPureFunctions, "is_protected_branch")
def test_main_branch_docs_allowed(
    mock_is_protected: Any) -> None:
    mock_is_protected.return_value = True

    result = BranchValidationPureFunctions.validate_branch_workflow("README.md")

    assert result is None
