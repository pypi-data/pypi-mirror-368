#!/usr/bin/env python3
"""
Global test fixtures for the Claude Code ADK Validator test suite.

Provides centralized fixtures for:
- Validation command execution
- Environment setup (CI mode, API keys)
- Common test utilities
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, overload

import pytest


# Set test environment to use a non-protected branch by default
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up global test environment to avoid branch protection issues"""
    os.environ["CLAUDE_TEST_BRANCH"] = "feature-test-branch"
    yield
    # Cleanup after all tests
    os.environ.pop("CLAUDE_TEST_BRANCH", None)


@pytest.fixture(autouse=True)
def clean_tdd_context():
    """Clean TDD context data before each test to prevent interference."""
    import shutil
    import time
    from pathlib import Path

    tdd_data_dir = Path.home() / ".claude" / "cc-validator" / "data"

    # Clean up any existing data files
    max_retries = 3
    for attempt in range(max_retries):
        try:
            if tdd_data_dir.exists():
                # Remove all files but keep the directory structure
                for file_path in tdd_data_dir.glob("*"):
                    if file_path.is_file():
                        file_path.unlink()
            else:
                # Create the directory if it doesn't exist
                tdd_data_dir.mkdir(parents=True, exist_ok=True)
            break
        except (OSError, PermissionError):
            if attempt < max_retries - 1:
                time.sleep(0.1 * (attempt + 1))
            else:
                # Final fallback - remove what we can
                try:
                    if tdd_data_dir.exists():
                        for file_path in tdd_data_dir.glob("*"):
                            file_path.unlink(missing_ok=True)
                    else:
                        tdd_data_dir.mkdir(parents=True, exist_ok=True)
                except:
                    pass

    # Brief delay for parallel execution synchronization
    time.sleep(0.1)

    yield

    # Clean up after the test
    try:
        if tdd_data_dir.exists():
            for file_path in tdd_data_dir.glob("*"):
                if file_path.is_file():
                    file_path.unlink(missing_ok=True)
    except:
        pass


@pytest.fixture
def run_validation() -> Callable[..., Tuple[int, str, str]]:
    """
    Simple fixture to run the validator in a subprocess, simulating the hook environment.
    """

    def _run(
        tool_name: str,
        tool_input: Dict[str, Any],
        env_vars: Optional[Dict[str, str]] = None,
        timeout: int = 30,
    ) -> Tuple[int, str, str]:
        """
        Executes the validator with the given tool data.
        """
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write('{"role": "user", "content": "Test command"}\n')
            transcript_path = f.name

        hook_input = {
            "tool_name": tool_name,
            "tool_input": tool_input,
            "transcript_path": transcript_path,
            "hook_event_name": "PreToolUse",
        }

        final_env = os.environ.copy()
        if env_vars:
            final_env.update(env_vars)

        try:
            process = subprocess.run(
                ["uv", "run", "python", "-m", "cc_validator"],
                input=json.dumps(hook_input),
                capture_output=True,
                text=True,
                timeout=timeout,
                env=final_env,
                cwd=Path(__file__).parent.parent,
            )
            return process.returncode, process.stdout, process.stderr
        finally:
            os.unlink(transcript_path)

    return _run


@pytest.fixture
def run_validation_factory() -> Callable[..., Tuple[int, str, str]]:
    """
    Hybrid factory fixture for running validation commands.

    Supports two modes:
    1. Convenience mode: run_validation_factory(tool_data)
    2. Raw mode: run_validation_factory(args=[...], env={...})

    Returns a function that can execute validation with different parameters.
    Handles subprocess execution, environment setup, and result parsing.
    """

    @overload
    def _run_validation(tool_data: Dict[str, Any]) -> Tuple[int, str, str]:
        """Convenience mode: builds the subprocess call from a data dictionary."""
        ...

    @overload
    def _run_validation(
        *, args: List[str], env: Optional[Dict[str, str]] = None
    ) -> Tuple[int, str, str]:
        """Raw mode: provides direct control over subprocess arguments."""
        ...

    def _run_validation(
        tool_data: Optional[Dict[str, Any]] = None,
        *,
        args: Optional[List[str]] = None,
        env: Optional[Dict[str, str]] = None,
    ) -> Tuple[int, str, str]:
        """Run validation with hybrid mode support."""
        # Validate that arguments for different modes are not mixed
        if tool_data is not None and args is not None:
            raise ValueError(
                "Cannot specify both 'tool_data' (convenience mode) and 'args' (raw mode)."
            )
        if tool_data is None and args is None:
            raise ValueError(
                "Must specify either 'tool_data' (convenience mode) or 'args' (raw mode)."
            )

        final_args: List[str]
        final_env: Dict[str, str] = os.environ.copy()

        # Prepare arguments based on the selected mode
        if tool_data is not None:
            # --- Convenience Mode ---
            if env is not None:
                raise ValueError("'env' argument is only for raw mode.")

            # Convert to expected format
            formatted_data = {
                "tool_name": tool_data.get("tool", ""),
                "tool_input": tool_data.get("input", {}),
                "transcript_path": tool_data.get("transcript_path", ""),
            }
            final_args = [
                "uv",
                "run",
                "python",
                "-m",
                "cc_validator.test_entry",
                json.dumps(formatted_data),
            ]

        elif args is not None:
            # --- Raw Mode ---
            final_args = args
            if env is not None:
                final_env.update(env)  # Allow overriding/extending the base environment

        else:
            # This case should be unreachable due to the initial validation
            raise RuntimeError("Invalid combination of arguments.")

        # Execute the subprocess with the prepared arguments
        process = subprocess.run(
            final_args,
            capture_output=True,
            text=True,
            timeout=30,
            env=final_env,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        )
        return process.returncode, process.stdout, process.stderr

    return _run_validation


# Environment fixtures - composable and single-purpose


@pytest.fixture
def set_api_key_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set a dummy API key for testing."""
    monkeypatch.setenv("GEMINI_API_KEY", "DUMMY_API_KEY_FOR_TESTING")


# CI mode fixture removed - CI mode no longer exists


@pytest.fixture
def set_debug_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set debug environment flag."""
    monkeypatch.setenv("DEBUG", "true")


# Composed environment fixtures for common scenarios

# ci_mode_env fixture removed - CI mode no longer exists


@pytest.fixture
def api_key_env(set_api_key_env: None) -> None:
    """Sets a dummy API key for tests that require one."""
    pass  # Composition through fixture dependencies


@pytest.fixture
def debug_mode_env(set_debug_env: None, set_api_key_env: None) -> None:
    """Debug mode with API key available."""
    pass  # Composition through fixture dependencies


# @pytest.fixture
# def tdd_validator_with_api() -> TDDValidator:
#     """Provides a TDD validator instance with API key from environment."""
#     api_key = os.environ.get("GEMINI_API_KEY")
#     return TDDValidator(api_key)


@pytest.fixture
def temp_project_dir(tmp_path: Path) -> Path:
    """
    Creates a temporary directory with basic project structure.

    Useful for tests that need to create files and directories
    in an isolated environment.
    """
    # Create basic project structure if needed
    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "docs").mkdir()

    return tmp_path


@pytest.fixture
def main_branch_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Sets environment to simulate being on main branch."""
    monkeypatch.setenv("CLAUDE_TEST_BRANCH", "main")


@pytest.fixture
def feature_branch_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Sets environment to simulate being on a feature branch."""
    monkeypatch.setenv("CLAUDE_TEST_BRANCH", "feature-branch")
