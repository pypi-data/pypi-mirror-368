#!/usr/bin/env python3
"""Test to reproduce the dashboard.py TDD validation issue"""

import asyncio
import os
import tempfile
from pathlib import Path

import pytest

from cc_validator.hybrid_validator import HybridValidator


def test_dashboard_update_should_be_blocked():
    """Test that updating dashboard.py with new methods should be blocked by TDD"""

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create the directory structure
        ui_dir = Path(tmpdir) / "src" / "ui"
        ui_dir.mkdir(parents=True, exist_ok=True)

        # Create initial dashboard.py
        dashboard_path = ui_dir / "dashboard.py"
        initial_content = '''from datetime import datetime

class Dashboard:
    """Displays the current state of the tracked stacks."""
    
    def __init__(self):
        self.log_buffer = []
        self.max_logs = 20
        self.layout = self._create_layout()
    
    def _create_layout(self):
        return None
    
    def add_log(self, message: str, style: str = "white"):
        self.log_buffer.append({"time": datetime.now(), "message": message, "style": style})
'''

        with open(dashboard_path, "w") as f:
            f.write(initial_content)

        # Updated content with logging functionality (no comments to avoid security block)
        updated_content = '''from datetime import datetime
from pathlib import Path

class Dashboard:
    """Displays the current state of the tracked stacks."""
    
    def __init__(self):
        self.log_buffer = []
        self.max_logs = 20
        self.layout = self._create_layout()
        
        self.log_dir = Path("logs/dashboard")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"dashboard_session_{self.session_timestamp}.log"
        self._init_log_file()
    
    def _create_layout(self):
        return None
    
    def _init_log_file(self):
        with open(self.log_file, "w") as f:
            f.write(f"Dashboard Session Started: {datetime.now().isoformat()}\\n")
            f.write(f"="*80 + "\\n\\n")
    
    def add_log(self, message: str, style: str = "white"):
        timestamp = datetime.now()
        self.log_buffer.append({"time": timestamp, "message": message, "style": style})
        
        with open(self.log_file, "a") as f:
            f.write(f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] {message}\\n")
'''

        # Initialize validator
        api_key = os.environ.get("GEMINI_API_KEY")

        # Set test branch to avoid protected branch issues
        os.environ["CLAUDE_TEST_BRANCH"] = "feature-test-branch"

        validator = HybridValidator(api_key=api_key)

        # Prepare Update operation
        tool_input = {"file_path": str(dashboard_path), "content": updated_content}

        # Run validation
        result = asyncio.run(validator.validate_tool_use("Update", tool_input, ""))

        # Print detailed results for debugging
        print("\n=== VALIDATION RESULT ===")
        print(f"Approved: {result.get('approved')}")
        print(f"Reason: {result.get('reason')}")
        print(f"TDD Approved: {result.get('tdd_approved')}")
        print(f"TDD Analysis: {result.get('tdd_analysis', {})}")
        print(f"File Categorization: {result.get('file_category', 'Not provided')}")
        print(f"Heuristic Decision: {result.get('heuristic_decision', 'Not provided')}")
        print(f"TDD Phase: {result.get('tdd_phase', 'Not provided')}")

        # Clean up environment
        os.environ.pop("CLAUDE_TEST_BRANCH", None)

        # The update should be blocked because:
        # 1. It adds new methods (_init_log_file)
        # 2. It adds new functionality without tests
        assert not result[
            "approved"
        ], f"Dashboard update should be blocked but was approved: {result}"

        # Check if blocked for TDD reasons
        tdd_blocked = not result.get("tdd_approved", True)
        assert (
            tdd_blocked
        ), f"Should be blocked for TDD reasons. TDD approved: {result.get('tdd_approved')}"

        # When both security and TDD fail, both should be shown in reason
        if not result.get("security_approved", True) and not result.get(
            "tdd_approved", True
        ):
            assert "TDD:" in result.get(
                "reason", ""
            ), f"TDD reason should be visible in primary reason when both fail. Reason: {result.get('reason')}"


if __name__ == "__main__":
    test_dashboard_update_should_be_blocked()
    print("\n✅ Test completed!")
