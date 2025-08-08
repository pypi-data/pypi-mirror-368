import asyncio
import json
import os
from cc_validator.file_categorization import FileContextAnalyzer
from cc_validator.streaming_processors import FileCategorizationProcessor, ProcessorPart

async def test_categorization_comparison():
    test_files = [
        ("calculator.py", "def add(a, b):\n    return a + b\n"),
        ("hello.py", "def main():\n    return 'Hello, World!'\n"),
        ("test_calculator.py", "def test_add():\n    assert add(1, 2) == 3\n"),
        ("README.md", "# Project\nThis is a readme file"),
        ("config.toml", "[tool.test]\nkey = 'value'")
    ]
    
    api_key = os.environ.get("GEMINI_API_KEY")
    gemini_processor = FileCategorizationProcessor(api_key)
    
    print("=== Categorization Comparison ===")
    print(f"API Key present: {api_key is not None}")
    print()
    
    for filename, content in test_files:
        print(f"--- {filename} ---")
        print(f"Content: {repr(content[:50])}...")
        
        # Rule-based categorization
        rule_result = FileContextAnalyzer.categorize_file(filename, content)
        print(f"Rule-based: {rule_result['category']} - {rule_result['reason']}")
        
        # LLM-based categorization
        if api_key:
            # Create the prompt that would be sent to Gemini
            prompt = f"""Analyze this file to determine its category for TDD validation purposes.

File: {filename}
Content:
{content}

Categorize as one of:
- implementation: Code that implements business logic or features
- test: Test files that verify functionality  
- config: Configuration files, build files, etc.
- docs: Documentation files
- structural: Setup files, imports, minimal logic

Return JSON with: category, requires_tdd (boolean), reason"""
            
            request_data = {"prompt": prompt}
            request_part = ProcessorPart(json.dumps(request_data))
            
            llm_result = {}
            async for part in gemini_processor.call(request_part):
                llm_result.update(json.loads(part.text) if hasattr(part, 'text') else {})
            
            print(f"LLM-based: {llm_result.get('category', 'unknown')} - {llm_result.get('reason', 'no reason')}")
        else:
            print("LLM-based: API key not available")
        
        print()

if __name__ == "__main__":
    asyncio.run(test_categorization_comparison())