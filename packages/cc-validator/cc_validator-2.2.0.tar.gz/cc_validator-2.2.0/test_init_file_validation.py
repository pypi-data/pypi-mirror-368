#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
import asyncio

from cc_validator.hybrid_validator import HybridValidator

# Test __init__.py with only version
content = "__version__ = '1.0.0'"
file_path = "__init__.py"

print("=== Testing __init__.py with only version ===")
print(f"File: {file_path}")
print(f"Content: {content}")

# Create the operation as it would come from Claude Code
tool_name = "Edit"
tool_input = {
    "file_path": file_path,
    "old_string": "",
    "new_string": content
}
context = ""  # Empty context for testing

async def test_validation():
    validator = HybridValidator()
    result = await validator.validate_tool_use(tool_name, tool_input, context)
    
    print(f"\nValidation Result:")
    print(f"Approved: {result['approved']}")
    if not result['approved']:
        print(f"Reason: {result['reason']}")
        if 'suggestions' in result:
            print(f"Suggestions: {result['suggestions']}")
    
    return result

result = asyncio.run(test_validation())

# Test other common __init__.py patterns
print("\n\n=== Testing other __init__.py patterns ===")

test_cases = [
    ("Empty __init__.py", ""),
    ("__init__.py with imports", "from .module import function\nfrom .another import Class"),
    ("__init__.py with __all__", "__all__ = ['function', 'Class']"),
    ("__init__.py with version and all", "__version__ = '1.0.0'\n__all__ = ['function']"),
]

async def test_all_cases():
    validator = HybridValidator()
    for name, content in test_cases:
        print(f"\n{name}:")
        print(f"Content: {repr(content)}")
        
        tool_name = "Write"
        tool_input = {
            "file_path": "__init__.py",
            "content": content
        }
        context = ""
        
        result = await validator.validate_tool_use(tool_name, tool_input, context)
        print(f"Approved: {result['approved']}")
        if not result['approved']:
            print(f"Reason: {result['reason']}")

asyncio.run(test_all_cases())