#!/usr/bin/env python3

import asyncio
from typing import Any
from unittest.mock import patch, MagicMock
import subprocess
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cc_validator.security_validator import SecurityValidator


@pytest.fixture
def validator() -> SecurityValidator:
    """Provides a SecurityValidator instance for each test."""
    return SecurityValidator()


@patch.dict(os.environ, {"CLAUDE_TEST_BRANCH": ""}, clear=False)
@patch("subprocess.run")
def test_get_current_branch_success(
    mock_run: Any, validator: SecurityValidator
) -> None:
    """Test successful branch detection"""
    mock_run.return_value = MagicMock(stdout="feature/test-branch\n", returncode=0)

    branch = validator._get_current_branch()

    assert branch == "feature/test-branch"
    mock_run.assert_called_once_with(
        ["git", "branch", "--show-current"],
        capture_output=True,
        text=True,
        timeout=5,
        cwd=os.getcwd(),
    )


@patch.dict(os.environ, {"CLAUDE_TEST_BRANCH": ""}, clear=False)
@patch("subprocess.run")
def test_get_current_branch_not_git_repo(
    mock_run: Any, validator: SecurityValidator
) -> None:
    """Test branch detection when not in a git repo"""
    mock_run.side_effect = subprocess.CalledProcessError(128, "git")

    branch = validator._get_current_branch()

    assert branch is None


@patch.dict(os.environ, {"CLAUDE_TEST_BRANCH": ""}, clear=False)
@patch("subprocess.run")
def test_get_current_branch_detached_head(
    mock_run: Any, validator: SecurityValidator
) -> None:
    """Test branch detection in detached HEAD state"""
    mock_run.return_value = MagicMock(stdout="HEAD\n", returncode=0)

    branch = validator._get_current_branch()

    assert branch is None


@patch.object(SecurityValidator, "_get_current_branch")
def test_is_protected_branch_main(
    mock_get_branch: Any, validator: SecurityValidator
) -> None:
    """Test protected branch detection for main branch"""
    mock_get_branch.return_value = "main"

    is_protected = validator._is_protected_branch()

    assert is_protected is True


@patch.object(SecurityValidator, "_get_current_branch")
def test_is_protected_branch_feature(
    mock_get_branch: Any, validator: SecurityValidator
) -> None:
    """Test protected branch detection for feature branch"""
    mock_get_branch.return_value = "feature/my-feature"

    is_protected = validator._is_protected_branch()

    assert is_protected is False


def test_is_allowed_file_on_main_readme(validator: SecurityValidator) -> None:
    """Test allowed files on main - README.md"""
    assert validator._is_allowed_file_on_main("README.md") is True
    assert validator._is_allowed_file_on_main("project/README.md") is True


def test_is_allowed_file_on_main_docs(validator: SecurityValidator) -> None:
    """Test allowed files on main - docs directory"""
    assert validator._is_allowed_file_on_main("docs/guide.md") is True
    assert validator._is_allowed_file_on_main("docs/api/reference.md") is True


def test_is_allowed_file_on_main_code(validator: SecurityValidator) -> None:
    """Test disallowed files on main - code files"""
    assert validator._is_allowed_file_on_main("src/main.py") is False
    assert validator._is_allowed_file_on_main("tests/test_example.py") is False


def test_extract_issue_number_valid(validator: SecurityValidator) -> None:
    """Test extracting issue number from valid branch name"""
    issue_num = validator._extract_issue_number("123-fix-bug")
    assert issue_num == "123"

    issue_num = validator._extract_issue_number("42-add-feature-xyz")
    assert issue_num == "42"


def test_extract_issue_number_invalid(validator: SecurityValidator) -> None:
    """Test extracting issue number from invalid branch name"""
    issue_num = validator._extract_issue_number("feature/my-feature")
    assert issue_num is None

    issue_num = validator._extract_issue_number("main")
    assert issue_num is None


@patch("subprocess.run")
def test_validate_issue_exists_success(
    mock_run: Any, validator: SecurityValidator
) -> None:
    """Test validating issue exists successfully"""
    mock_run.return_value = MagicMock(returncode=0)

    exists = validator._validate_issue_exists("42")

    assert exists is True
    mock_run.assert_called_once_with(
        ["gh", "issue", "view", "42"],
        capture_output=True,
        stderr=subprocess.DEVNULL,
        timeout=5,
    )


@patch("subprocess.run")
def test_validate_issue_exists_not_found(
    mock_run: Any, validator: SecurityValidator
) -> None:
    """Test validating issue that doesn't exist"""
    mock_run.return_value = MagicMock(returncode=1)

    exists = validator._validate_issue_exists("999")

    assert exists is False


@patch("subprocess.run")
def test_validate_issue_exists_gh_not_installed(
    mock_run: Any, validator: SecurityValidator
) -> None:
    """Test validating issue when gh CLI not installed"""
    mock_run.side_effect = FileNotFoundError()

    exists = validator._validate_issue_exists("42")

    assert exists is True  # Assumes issue exists when can't check


@patch.object(SecurityValidator, "_extract_issue_number")
@patch.object(SecurityValidator, "_validate_issue_exists")
def test_get_issue_workflow_suggestions_with_invalid_issue(
    mock_validate: Any, mock_extract: Any, validator: SecurityValidator
) -> None:
    """Test suggestions when issue doesn't exist"""
    mock_extract.return_value = "999"
    mock_validate.return_value = False

    suggestions = validator._get_issue_workflow_suggestions("999-feature")

    assert "Issue #999 not found" in suggestions[0]
    assert "gh issue list" in suggestions[1]


@patch.object(SecurityValidator, "_is_protected_branch")
@patch.object(SecurityValidator, "_get_current_branch")
def test_check_branch_validation_on_main_with_code(
    mock_get_branch: Any, mock_is_protected: Any, validator: SecurityValidator
) -> None:
    """Test branch validation blocks code changes on main"""
    mock_get_branch.return_value = "main"
    mock_is_protected.return_value = True

    result = validator._check_branch_validation("src/main.py")

    assert result is not None
    assert result["approved"] is False
    assert "protected branch" in result["reason"]
    assert isinstance(result["suggestions"], list)


@patch.object(SecurityValidator, "_is_protected_branch")
def test_check_branch_validation_on_main_with_docs(
    mock_is_protected: Any, validator: SecurityValidator
) -> None:
    """Test branch validation allows docs on main"""
    mock_is_protected.return_value = True

    result = validator._check_branch_validation("README.md")

    assert result is None


@patch.object(SecurityValidator, "_is_protected_branch")
def test_check_branch_validation_on_feature_branch(
    mock_is_protected: Any, validator: SecurityValidator
) -> None:
    """Test branch validation allows everything on feature branches"""
    mock_is_protected.return_value = False

    result = validator._check_branch_validation("src/main.py")

    assert result is None


@patch.object(SecurityValidator, "_check_branch_validation")
@pytest.mark.asyncio
async def test_validate_file_operation_with_branch_block(
    mock_check_branch: Any, validator: SecurityValidator
) -> None:
    """Test file operation validation blocked by branch check"""
    mock_check_branch.return_value = {
        "approved": False,
        "reason": "Protected branch",
        "suggestions": ["Use feature branch"],
    }

    result = await validator.validate_file_operation(
        {
            "file_path": "src/main.py",
            "content": "print('hello')",
        }
    )

    assert result["approved"] is False
    assert result["reason"] == "Protected branch"


@patch("cc_validator.security_validator.ENFORCE_ISSUE_WORKFLOW", False)
def test_branch_validation_disabled(validator: SecurityValidator) -> None:
    """Test branch validation when disabled in config"""
    result = validator._check_branch_validation("src/main.py")
    assert result is None
