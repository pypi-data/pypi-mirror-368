import asyncio
import json
from cc_validator.streaming_processors import FileCategorizationProcessor, ProcessorPart

async def test_missing_prompt():
    print("=== Testing FileCategorizationProcessor with missing prompt ===")
    
    processor = FileCategorizationProcessor("dummy-key")
    
    # Simulate what the pipeline is currently passing (no prompt key)
    pipeline_data = {
        "tool_name": "Write",
        "tool_input": {
            "file_path": "calculator.py",
            "content": "def add(a, b):\n    return a + b\n"
        },
        "context": "Test context"
    }
    
    print(f"Data passed to processor: {json.dumps(pipeline_data, indent=2)}")
    
    part = ProcessorPart(json.dumps(pipeline_data))
    
    # Extract what the processor will get as prompt
    from cc_validator.streaming_processors import extract_json_from_part
    request = extract_json_from_part(part)
    prompt = request.get("prompt", "")
    
    print(f"Prompt extracted by processor: '{prompt}'")
    print(f"Prompt is empty: {prompt == ''}")
    
    print("\nThis explains why the LLM is giving strange categorizations!")
    print("The LLM is receiving an empty prompt and trying to categorize based on no information.")

if __name__ == "__main__":
    asyncio.run(test_missing_prompt())