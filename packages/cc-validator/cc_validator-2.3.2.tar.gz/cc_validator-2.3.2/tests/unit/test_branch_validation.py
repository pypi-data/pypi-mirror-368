#!/usr/bin/env python3

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
    return SecurityValidator()


@patch.dict(os.environ, {"CLAUDE_TEST_BRANCH": ""}, clear=False)
@patch("subprocess.run")
def test_basic_branch_detection(mock_run: Any, validator: SecurityValidator) -> None:
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


@patch.object(SecurityValidator, "_get_current_branch")
def test_protected_branch_validation(
    mock_get_branch: Any, validator: SecurityValidator
) -> None:
    mock_get_branch.return_value = "main"
    assert validator._is_protected_branch() is True

    mock_get_branch.return_value = "feature/my-feature"
    assert validator._is_protected_branch() is False


def test_main_branch_file_restrictions(validator: SecurityValidator) -> None:
    assert validator._is_allowed_file_on_main("README.md") is True
    assert validator._is_allowed_file_on_main("docs/guide.md") is True
    assert validator._is_allowed_file_on_main("src/main.py") is False
    assert validator._is_allowed_file_on_main("tests/test_example.py") is False


@patch.object(SecurityValidator, "_is_protected_branch")
def test_feature_branch_permissions(
    mock_is_protected: Any, validator: SecurityValidator
) -> None:
    mock_is_protected.return_value = False

    result = validator._check_branch_validation("src/main.py")

    assert result is None


def test_issue_number_extraction(validator: SecurityValidator) -> None:
    assert validator._extract_issue_number("123-fix-bug") == "123"
    assert validator._extract_issue_number("42-add-feature-xyz") == "42"
    assert validator._extract_issue_number("feature/my-feature") is None
    assert validator._extract_issue_number("main") is None


@patch.object(SecurityValidator, "_is_protected_branch")
@patch.object(SecurityValidator, "_get_current_branch")
def test_main_branch_code_blocking(
    mock_get_branch: Any, mock_is_protected: Any, validator: SecurityValidator
) -> None:
    mock_get_branch.return_value = "main"
    mock_is_protected.return_value = True

    result = validator._check_branch_validation("src/main.py")

    assert result is not None
    assert result["approved"] is False
    assert "protected branch" in result["reason"]
    assert isinstance(result["suggestions"], list)


@patch.object(SecurityValidator, "_is_protected_branch")
def test_main_branch_docs_allowed(
    mock_is_protected: Any, validator: SecurityValidator
) -> None:
    mock_is_protected.return_value = True

    result = validator._check_branch_validation("README.md")

    assert result is None
