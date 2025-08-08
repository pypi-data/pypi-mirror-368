#!/usr/bin/env python3

import json
import subprocess
import tempfile
from pathlib import Path

# Clean up any existing test.json
test_json_path = Path.cwd() / ".claude/cc-validator/data/test.json"
if test_json_path.exists():
    test_json_path.unlink()
    print(f"Cleaned up existing test.json")

# Create a test that will have collection error
with tempfile.TemporaryDirectory() as temp_dir:
    test_file = Path(temp_dir) / "test_error.py"
    test_file.write_text("""
from nonexistent import something

def test_something():
    assert True
""")
    
    # Run pytest from current directory (where cc-validator is installed)
    result = subprocess.run(
        ["uv", "run", "pytest", str(test_file), "-v"],
        capture_output=True,
        text=True,
    )
    
    print(f"Exit code: {result.returncode}")
    print(f"Stdout:\n{result.stdout}")
    print(f"Stderr:\n{result.stderr}")
    
    # Check if test.json was created
    if test_json_path.exists():
        print(f"\ntest.json found at: {test_json_path}")
        with open(test_json_path) as f:
            data = json.load(f)
            test_results = data["test_results"]
            print(f"\nTest results:")
            print(f"  errors: {test_results['errors']}")
            print(f"  collection_errors: {test_results['collection_errors']}")
            print(f"  errors_list: {test_results['errors_list']}")
    else:
        print("\nNo test.json found!")