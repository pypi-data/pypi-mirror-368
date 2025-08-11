# Contributing to Claude Code ADK-Inspired Validation Hooks

Thank you for your interest in contributing to this project! This guide will help you get started with development and ensure your contributions align with the project's goals.

## Quick Start

### Development Setup

1. **Fork and clone the repository:**
```bash
git clone https://github.com/your-username/jk-hooks-gemini-challenge.git
cd jk-hooks-gemini-challenge
```

2. **Set up development environment:**
```bash
uv sync
export GEMINI_API_KEY="your_test_api_key"
```

3. **Run tests to verify setup:**
```bash
uv run python test_validation.py
```

## Development Guidelines

### Code Quality Standards

All contributions must pass these quality checks:

```bash
# Code formatting
uvx black cc_validator/ tests/

# Linting
uvx ruff check cc_validator/ tests/

# Type checking
uvx mypy cc_validator/ tests/

# Test suite
uv run python test_validation.py
```

### Commit Message Format

Use conventional commits for clear history:

```
feat: add new security pattern detection
fix: resolve false positive in secret detection
docs: update installation instructions
test: add validation test for new pattern
refactor: improve prompt structure for LLM analysis
```

### Security-First Development

This project prioritizes security. When contributing:

1. **Never commit real credentials** - Use placeholders in examples
2. **Test thoroughly** - Include test cases for new validation patterns
3. **Document security implications** - Explain the security rationale for changes
4. **Follow defense-in-depth** - Consider multiple validation layers

## Architecture Overview

### Core Components

- **`cc_validator/validator.py`**: Main validation engine
- **Validation Tiers**: Rule-based → LLM analysis → File analysis
- **Security Models**: Pydantic schemas for structured responses
- **Test Suite**: Comprehensive validation scenarios

### Adding New Features

#### 1. Security Pattern Detection

For new threat patterns, add to appropriate validation tier:

```python
# Tier 1: Fast rule-based (cc_validator/validator.py)
def validate_bash_command(self, tool_input: dict) -> dict:
    # Add pattern to critical_patterns or warning_patterns

# Tier 2: LLM analysis (build_validation_prompt method)
# Update prompt with new security considerations

# Tier 3: File analysis (analyze_uploaded_file method)
# Enhance file security analysis prompts
```

#### 2. Tool Enforcement

To enforce modern development practices:

```python
# Add to tool_enforcement list in validate_bash_command
tool_enforcement = [
    (
        r"^your_legacy_tool\b",
        "Use 'modern_alternative' instead for better performance."
    ),
]
```

#### 3. Test Coverage

Every new feature requires test coverage:

```python
# Add test case to test_validation.py
new_test = {
    "session_id": "test123",
    "tool_name": "Bash",
    "tool_input": {"command": "your_test_command"}
}

tests.append(("Description", new_test, expected_exit_code))
```

## Contribution Types

### Bug Reports

When reporting bugs, include:

- **Command that failed**: Exact tool input that caused the issue
- **Expected behavior**: What should have happened
- **Actual behavior**: What actually happened
- **Environment**: OS, Python version, uv version
- **Test case**: Minimal reproduction example

### Feature Requests

For new features, provide:

- **Security rationale**: Why this improves security
- **Use cases**: Real-world scenarios where this helps
- **Implementation approach**: High-level design considerations
- **Breaking changes**: Any compatibility impacts

### Pull Requests

Before submitting:

1. **Create feature branch**: `git checkout -b feature/your-feature-name`
2. **Add tests**: Include comprehensive test coverage
3. **Update documentation**: Reflect changes in README.md
4. **Run quality checks**: Ensure all checks pass
5. **Test integration**: Verify Claude Code hook integration works

#### PR Template

```markdown
## Description
Brief description of changes and motivation.

## Security Impact
How this affects security validation or tool behavior.

## Testing
- [ ] All existing tests pass
- [ ] Added new test cases for changes
- [ ] Manually tested with Claude Code hooks
- [ ] No performance regressions

## Documentation
- [ ] Updated README.md if needed
- [ ] Added inline code documentation
- [ ] Updated CLAUDE.md for development guidance
```

## Security Pattern Guidelines

### Effective Pattern Design

1. **Minimize false positives**: Use precise patterns that don't block legitimate use
2. **Layer validation**: Combine rule-based and LLM analysis
3. **Provide alternatives**: Always suggest better approaches when blocking
4. **Context awareness**: Consider the user's intent and development workflow

### Pattern Examples

```python
# Good: Specific, actionable
r"^rm\s+-rf\s+/\s*$"  # Targets dangerous root deletion

# Bad: Too broad
r"rm"  # Blocks legitimate file removal

# Good: Educational blocking
return {
    "approved": False,
    "reason": "Use 'rg' instead of 'grep' for better performance",
    "suggestions": ["rg pattern file.txt"]
}
```

## Community Guidelines

### Code of Conduct

- **Be respectful**: Treat all contributors with respect
- **Be constructive**: Provide helpful feedback and suggestions
- **Be patient**: Remember that contributors have varying experience levels
- **Focus on security**: Keep security implications at the forefront

### Getting Help

- **GitHub Issues**: For bugs, feature requests, and questions
- **Discussions**: For general development discussions
- **Security Issues**: Email maintainers for security vulnerabilities

## Advanced Development

### LLM Prompt Engineering

When modifying validation prompts:

1. **Test thoroughly**: Use various inputs to verify behavior
2. **Maintain structure**: Keep consistent response formats
3. **Add context**: Include relevant security intelligence
4. **Document changes**: Explain prompt modifications

### Performance Considerations

- **Fast path first**: Rule-based validation should be quick
- **LLM efficiency**: Use structured output to reduce parsing overhead
- **File analysis**: Only trigger for large files (>500 chars)
- **Timeout management**: Keep hook timeouts reasonable (8000ms)

## Release Process

1. **Version bumping**: Update version in `pyproject.toml`
2. **Changelog**: Document changes in release notes
3. **Testing**: Comprehensive validation across scenarios
4. **Publishing**: Create GitHub release and publish to PyPI

## Questions?

Feel free to open an issue for any questions about contributing. We appreciate your help in making Claude Code development more secure!
