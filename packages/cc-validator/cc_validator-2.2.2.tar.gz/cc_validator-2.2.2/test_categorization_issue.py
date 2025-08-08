from cc_validator.file_categorization import FileContextAnalyzer

def test_categorization():
    test_files = [
        ("calculator.py", "def add(a, b):\n    return a + b\n"),
        ("hello.py", "def main():\n    return 'Hello, World!'\n"),
        ("simple.py", "def greet(name):\n    print(f'Hello {name}')\n"),
        ("math_utils.py", "def multiply(x, y):\n    return x * y\n\ndef divide(x, y):\n    return x / y\n"),
    ]
    
    for filename, content in test_files:
        print(f"\n=== Testing {filename} ===")
        print(f"Content:\n{content}")
        result = FileContextAnalyzer.categorize_file(filename, content)
        print(f"Category: {result.get('category')}")
        print(f"Reason: {result.get('reason')}")
        print(f"Requires strict security: {result.get('requires_strict_security')}")

if __name__ == "__main__":
    test_categorization()
