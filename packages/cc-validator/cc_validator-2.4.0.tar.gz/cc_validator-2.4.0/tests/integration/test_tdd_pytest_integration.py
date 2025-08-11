#!/usr/bin/env python3

import json
import os
import subprocess
import time
from pathlib import Path

import pytest


def test_tdd_workflow_with_collection_error() -> None:
    """Test complete TDD workflow with pytest collection error"""
    import tempfile

    # Create a temporary directory for better isolation
    with tempfile.TemporaryDirectory(prefix="test_tdd_") as temp_dir:
        test_dir = Path(temp_dir)

        # Create test file
        test_file = test_dir / "test_calculator.py"
        test_file.write_text(
            """
from calculator import add

def test_add():
    assert add(2, 3) == 5
"""
        )

        # Step 1: Run pytest - should fail with collection error (RED phase)
        # Use subprocess to run pytest in the test directory
        result = subprocess.run(
            ["uv", "run", "pytest", str(test_file), "-v", "--tb=short"],
            capture_output=True,
            text=True,
            cwd=str(test_dir),
            env={**os.environ, "PYTHONPATH": str(test_dir)},
        )

        print(f"Step 1 - Pytest exit code: {result.returncode}")
        print(f"Step 1 - Pytest stdout:\n{result.stdout}")
        if result.stderr:
            print(f"Step 1 - Pytest stderr:\n{result.stderr}")

        # Should see collection error
        assert result.returncode != 0, "Pytest should fail with collection error"
        assert "Test results captured for TDD validation:" in result.stdout
        assert "Errors: 1" in result.stdout

        # Check test.json was created
        # Look in multiple possible locations
        test_json_locations = [
            test_dir / ".claude/cc-validator/data/test.json",
            Path.cwd() / ".claude/cc-validator/data/test.json",
        ]

        test_json = None
        for location in test_json_locations:
            if location.exists():
                test_json = location
                print(f"Found test.json at: {test_json}")
                break

        assert (
            test_json is not None
        ), f"test.json not found in any of: {test_json_locations}"

        # Verify test.json content
        with open(test_json) as f:
            data = json.load(f)
            test_results = data["test_results"]
            print(f"Test results: {json.dumps(test_results, indent=2)}")

            assert test_results["errors"] == 1
            assert test_results["status"] == "failed"
            assert test_results["total_tests"] == 1

        # Wait to ensure file is fully written
        time.sleep(0.2)

        # Step 2: Write implementation - should be allowed (GREEN phase)
        calculator_file = test_dir / "calculator.py"
        impl_json = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(calculator_file.absolute()),
                "content": "def add(a, b):\n    return a + b",
            },
        }

        # Run validator from the test directory
        env = os.environ.copy()
        # Use real API key from environment if available
        # Test runs regardless of GEMINI_API_KEY presence
        # Set the data directory to match where pytest wrote the test.json
        env["CC_VALIDATOR_DATA_DIR"] = str(test_dir / ".claude/cc-validator/data")

        result = subprocess.run(
            ["uv", "run", "python", "-m", "cc_validator"],
            input=json.dumps(impl_json),
            capture_output=True,
            text=True,
            cwd=str(test_dir),
            env=env,
        )

        print(f"Step 2 - Validator exit code: {result.returncode}")
        if result.stderr:
            print(f"Step 2 - Validator stderr:\n{result.stderr}")
        if result.stdout:
            print(f"Step 2 - Validator stdout:\n{result.stdout}")

        # Should allow implementation
        assert result.returncode == 0, (
            f"TDD validator should allow GREEN phase after collection error. "
            f"Exit code: {result.returncode}, stderr: {result.stderr}"
        )

        # Since the validator only approves/rejects operations (doesn't execute them),
        # we need to simulate what Claude Code would do after approval: create the file
        calculator_file.write_text("def add(a, b):\n    return a + b")
        print(f"calculator.py created successfully at: {calculator_file}")
        print(f"calculator.py content:\n{calculator_file.read_text()}")

        # Step 3: Run tests again - should pass (verify GREEN)
        result = subprocess.run(
            ["uv", "run", "pytest", str(test_file), "-v", "--tb=short"],
            capture_output=True,
            text=True,
            cwd=str(test_dir),
            env={**os.environ, "PYTHONPATH": str(test_dir)},
        )

        print(f"Step 3 - Pytest exit code: {result.returncode}")
        print(f"Step 3 - Pytest stdout:\n{result.stdout}")
        if result.stderr:
            print(f"Step 3 - Pytest stderr:\n{result.stderr}")

        assert result.returncode == 0, (
            f"Tests should pass after implementation. "
            f"Exit code: {result.returncode}, stdout: {result.stdout}"
        )
        assert "1 passed" in result.stdout

        print("✓ TDD workflow with collection error works correctly!")


if __name__ == "__main__":
    test_tdd_workflow_with_collection_error()
