#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
import asyncio

from cc_validator.file_categorization import FileContextAnalyzer
from cc_validator.tdd_validator import TDDValidator

# Test __init__.py with only version
content = "__version__ = '1.0.0'"
file_path = "__init__.py"

print("=== Testing __init__.py with only version ===")
print(f"File: {file_path}")
print(f"Content: {content}")

# Test FileContextAnalyzer
print("\n1. FileContextAnalyzer (used by security validator):")
categorization = FileContextAnalyzer.categorize_file(file_path, content)
print(f"   Category: {categorization['category']}")
print(f"   Requires strict security: {categorization['requires_strict_security']}")
print(f"   Reason: {categorization['reason']}")

# Test TDDValidator internal logic
print("\n2. TDDValidator internal categorization:")

async def test_all():
    validator = TDDValidator()
    
    # Test the internal categorization method
    tdd_category = await validator.categorize_file(file_path, content)
    print(f"   Category: {tdd_category['category']}")
    print(f"   Requires TDD: {tdd_category['requires_tdd']}")
    print(f"   Reason: {tdd_category['reason']}")
    
    # Test the minimal __init__.py check
    is_minimal = validator._is_minimal_init_file(file_path, content)
    print(f"\n3. TDDValidator._is_minimal_init_file: {is_minimal}")
    
    # Test with async validate_edit_operation to see full flow
    print("\n4. Full TDD validation flow (Edit operation):")
    result = await validator.validate_edit_operation(
        file_path=file_path,
        old_string="",
        new_string=content
    )
    print(f"   Approved: {result.approved}")
    if not result.approved:
        print(f"   Reason: {result.reason}")
        if result.suggestions:
            print(f"   Suggestions: {result.suggestions[0]}")

asyncio.run(test_all())