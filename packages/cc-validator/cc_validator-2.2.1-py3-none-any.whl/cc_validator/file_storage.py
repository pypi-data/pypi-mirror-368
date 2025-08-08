#!/usr/bin/env python3

import json
import os
import time
from typing import Optional, Dict, Any
from pathlib import Path


class FileStorage:
    """
    File storage system for TDD validation context persistence.
    Manages test results, todos, and modification history similar to TDD Guard.
    """

    def __init__(self, data_dir: Optional[str] = None):
        if data_dir is None:
            data_dir = os.environ.get(
                "CC_VALIDATOR_DATA_DIR", ".claude/cc-validator/data"
            )
        self.data_dir = Path(data_dir)
        self.test_results_file = self.data_dir / "test.json"
        self.todos_file = self.data_dir / "todos.json"
        self.modifications_file = self.data_dir / "modifications.json"
        self.config_file = self.data_dir / "config.json"

        # Create data directory if it doesn't exist - with error handling
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
        except (OSError, IOError):
            # Try to use a temporary directory as fallback
            import tempfile

            temp_dir = Path(tempfile.gettempdir()) / "cc-validator"
            try:
                temp_dir.mkdir(parents=True, exist_ok=True)
                self.data_dir = temp_dir
                self.test_results_file = self.data_dir / "test.json"
                self.todos_file = self.data_dir / "todos.json"
                self.modifications_file = self.data_dir / "modifications.json"
                self.config_file = self.data_dir / "config.json"
            except (OSError, IOError):
                self.data_dir = Path("/tmp/cc-validator")
                self.data_dir.mkdir(parents=True, exist_ok=True)
                self.test_results_file = self.data_dir / "test.json"
                self.todos_file = self.data_dir / "todos.json"
                self.modifications_file = self.data_dir / "modifications.json"
                self.config_file = self.data_dir / "config.json"

    def _read_json_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Safely read JSON file with error handling"""
        try:
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data  # type: ignore[no-any-return]
        except json.JSONDecodeError:
            pass
        except IOError:
            pass
        except Exception:
            pass

        return None

    def _write_json_file(self, file_path: Path, data: Dict[str, Any]) -> bool:
        """Safely write JSON file with error handling"""
        try:
            # Atomic write using temporary file
            temp_file = file_path.with_suffix(".tmp")
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            temp_file.replace(file_path)
            return True
        except IOError:
            return False

    def store_test_results(self, test_data: Dict[str, Any]) -> bool:
        """
        Store test results with timestamp and 20-minute expiry.

        Args:
            test_data: Test execution results including pass/fail status,
                      error messages, and test file information
        """
        current_time = time.time()

        stored_data = {
            "timestamp": current_time,
            "expiry": current_time + (20 * 60),  # 20 minutes from now
            "test_results": test_data,
        }

        return self._write_json_file(self.test_results_file, stored_data)

    def get_recent_test_results(self) -> Optional[Dict[str, Any]]:
        """
        Get test results if they're still valid (within 20-minute window).

        Returns:
            Test results if valid, None if expired or missing
        """
        data = self._read_json_file(self.test_results_file)
        if not data:
            return None

        current_time = time.time()
        expiry_time = data.get("expiry", 0)

        if current_time > expiry_time:
            # Test results have expired, clean up
            self._cleanup_expired_test_results()
            return None

        test_results = data.get("test_results")
        return test_results

    def _cleanup_expired_test_results(self) -> None:
        """Remove expired test results file"""
        try:
            if not self.test_results_file.exists():
                return

            data = self._read_json_file(self.test_results_file)
            if not data:
                return

            current_time = time.time()
            expiry_time = data.get("expiry", 0)

            if current_time > expiry_time:
                self.test_results_file.unlink()
        except IOError:
            pass

    def store_todo_state(self, todos: Dict[str, Any]) -> bool:
        """Store current todo state for TDD workflow tracking"""
        return self._write_json_file(
            self.todos_file, {"timestamp": time.time(), "todos": todos}
        )

    def get_todo_state(self) -> Optional[Dict[str, Any]]:
        """Get current todo state"""
        data = self._read_json_file(self.todos_file)
        return data.get("todos") if data else None

    def store_file_modification(
        self,
        file_path: str,
        operation: str,
        content_before: str = "",
        content_after: str = "",
    ) -> bool:
        """
        Store file modification history for context aggregation.

        Args:
            file_path: Path to modified file
            operation: Type of operation (Edit, Write, MultiEdit)
            content_before: File content before modification
            content_after: File content after modification
        """
        modifications = self._read_json_file(self.modifications_file) or {
            "modifications": []
        }

        modification_entry = {
            "timestamp": time.time(),
            "file_path": file_path,
            "operation": operation,
            "content_before": content_before,
            "content_after": content_after,
        }

        modifications["modifications"].append(modification_entry)

        # Keep only last 50 modifications to prevent unbounded growth
        if len(modifications["modifications"]) > 50:
            modifications["modifications"] = modifications["modifications"][-50:]

        return self._write_json_file(self.modifications_file, modifications)

    def get_recent_modifications(self, limit: int = 10) -> list[Dict[str, Any]]:
        """Get recent file modifications for context"""
        data = self._read_json_file(self.modifications_file)
        if not data or "modifications" not in data:
            return []

        modifications = data["modifications"]
        return modifications[-limit:] if modifications else []

    def get_tdd_context(self) -> Dict[str, Any]:
        """
        Get comprehensive TDD context including test results, todos, and modifications.
        This is used by the TDD validator for context-aware validation.
        """
        return {
            "test_results": self.get_recent_test_results(),
            "todos": self.get_todo_state(),
            "recent_modifications": self.get_recent_modifications(),
            "has_valid_test_data": self.get_recent_test_results() is not None,
            "branch_context": self.get_branch_context(),
        }

    def store_branch_context(
        self, branch: str, issue_num: Optional[str] = None
    ) -> bool:
        """
        Store current branch and issue context for workflow tracking.

        Args:
            branch: Current git branch name
            issue_num: Associated GitHub issue number (if any)
        """
        branch_file = self.data_dir / "branch_context.json"
        data = {
            "timestamp": time.time(),
            "branch": branch,
            "issue_number": issue_num,
        }
        return self._write_json_file(branch_file, data)

    def get_branch_context(self) -> Optional[Dict[str, Any]]:
        """
        Get stored branch context if available.

        Returns:
            Branch context dict with branch name and issue number, or None
        """
        branch_file = self.data_dir / "branch_context.json"
        data = self._read_json_file(branch_file)
        if data:
            return {
                "branch": data.get("branch"),
                "issue_number": data.get("issue_number"),
                "timestamp": data.get("timestamp"),
            }
        return None

    def cleanup_expired_data(self) -> None:
        """Clean up expired data files"""
        self._cleanup_expired_test_results()

        # Clean up old modifications (older than 1 hour)
        modifications = self._read_json_file(self.modifications_file)
        if modifications and "modifications" in modifications:
            current_time = time.time()
            hour_ago = current_time - (60 * 60)

            filtered_mods = [
                mod
                for mod in modifications["modifications"]
                if mod.get("timestamp", 0) > hour_ago
            ]

            if len(filtered_mods) != len(modifications["modifications"]):
                modifications["modifications"] = filtered_mods
                self._write_json_file(self.modifications_file, modifications)

    def clear_test_results(self) -> None:
        """Clear all test results immediately (for test isolation)"""
        try:
            if self.test_results_file.exists():
                self.test_results_file.unlink()
        except IOError:
            pass
