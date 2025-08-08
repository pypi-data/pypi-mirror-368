import asyncio
import json
import os
from cc_validator.tdd_pipeline import TDDValidationPipeline
from cc_validator.file_storage import FileStorage

async def test_tdd_pipeline_behavior():
    # Test simple implementation files
    test_cases = [
        {
            "tool_name": "Write",
            "file_path": "calculator.py",
            "content": "def add(a, b):\n    return a + b\n"
        },
        {
            "tool_name": "Edit", 
            "file_path": "hello.py",
            "content": "def main():\n    return 'Hello, World!'\n"
        },
        {
            "tool_name": "Write",
            "file_path": "test_calculator.py",
            "content": "def test_add():\n    assert add(1, 2) == 3\n"
        }
    ]
    
    api_key = os.environ.get("GEMINI_API_KEY")
    pipeline = TDDValidationPipeline(api_key)
    
    # Clear any existing context
    file_storage = FileStorage()
    file_storage.clear_test_results()
    
    print("=== Testing TDD Pipeline Behavior ===")
    print(f"API Key present: {api_key is not None}")
    print(f"Current TDD context: {file_storage.get_tdd_context()}")
    print()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"--- Test Case {i}: {test_case['tool_name']} {test_case['file_path']} ---")
        print(f"Content:\n{test_case['content']}")
        
        tool_input = {
            "file_path": test_case["file_path"],
            "content": test_case["content"]
        }
        
        result = await pipeline.validate(
            tool_name=test_case["tool_name"],
            tool_input=tool_input,
            context="Test context"
        )
        
        print(f"Result: {json.dumps(result, indent=2)}")
        print()

if __name__ == "__main__":
    asyncio.run(test_tdd_pipeline_behavior())