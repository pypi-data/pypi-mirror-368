#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

from cc_validator.file_categorization import FileContextAnalyzer

# Test __init__.py with only version
content = "__version__ = '1.0.0'"
file_path = "__init__.py"

# Test direct methods
is_test = FileContextAnalyzer.is_test_file(file_path, content)
is_structural = FileContextAnalyzer.is_structural_file(file_path, content)
has_impl = FileContextAnalyzer._has_implementation_logic(content)

print(f"File: {file_path}")
print(f"Content: {content}")
print(f"is_test_file: {is_test}")
print(f"is_structural_file: {is_structural}")
print(f"_has_implementation_logic: {has_impl}")

# Test full categorization
categorization = FileContextAnalyzer.categorize_file(file_path, content)
print(f"\nFull categorization: {categorization}")
