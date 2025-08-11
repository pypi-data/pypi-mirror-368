# CC-Validator Architecture Flow

## Overview
The CC-Validator uses a hybrid approach combining rule-based patterns and LLM-powered analysis to validate Claude Code operations.

## End-to-End Flow

```mermaid
flowchart TD
    A[Claude Code Hook] -->|JSON stdin| B[main.py]
    B --> C{GEMINI_API_KEY?}
    C -->|No| D[Block - Exit 2]
    C -->|Yes| E[HybridValidator]
    
    E --> F{Tool Type?}
    F -->|TodoWrite| G[Skip Validation<br/>Store Context]
    F -->|Write/Edit/MultiEdit/Update| H[Parallel Validation]
    F -->|Bash| I[Security Only]
    F -->|Other| J[Unknown Tool Block]
    
    H --> K[Security Validator]
    H --> L[TDD Validator]
    
    K --> K1[Tier 1: Pattern Matching<br/>- Dangerous commands<br/>- Secret patterns<br/>- Tool enforcement]
    K1 --> K2[Tier 2: Context-Aware<br/>- File type specific rules<br/>- Test vs production]
    K2 --> K3[Tier 3: File Analysis<br/>- LLM for files >500 chars<br/>- Security review]
    K3 --> K4[Tier 4: Deep Analysis<br/>- LLM comprehensive<br/>- 24K token thinking]
    
    L --> L1[File Categorization<br/>- Fast path rules<br/>- LLM fallback]
    L1 --> L2[TDD Enforcement<br/>- Red-Green-Refactor<br/>- Single test rule<br/>- Language suggestions]
    
    K4 --> M[Security Result]
    L2 --> N[TDD Result]
    
    M --> O{Both Approved?}
    N --> O
    O -->|Yes| P[Allow - Exit 0]
    O -->|No| Q[Block - Exit 2]
    
    G --> R[Allow - Exit 0]
    I --> K
```

## Processor Types

### 1. Rule-Based Processors (No LLM)
- **Security Tier 1**: Pattern matching for dangerous commands
  - Example: `rm -rf /`, `chmod 777 /`, API key patterns
  - Location: `security_validator.py` lines 337-367
  
- **Security Tier 2**: Context-aware rules
  - Different validation for test/config/template files
  - Location: `security_validator.py` lines 209-245

- **File Categorization Fast Path**: 
  - Obvious patterns: `test_*.py`, `*.md`, `package.json`
  - Location: `file_categorization.py` lines 31-87

### 2. LLM-Based Processors (Uses Gemini)
- **Security Tier 3**: File content analysis
  - Triggered for files >500 characters
  - Uses file upload to Gemini
  - Location: `security_validator.py` lines 246-274

- **Security Tier 4**: Comprehensive analysis
  - Deep thinking with 24K token budget
  - Structured output via Pydantic
  - Location: `security_validator.py` lines 275-336

- **File Categorization LLM**: 
  - For ambiguous files not matching fast path
  - Categories: test, implementation, structural, config, docs, data, template
  - Location: `file_categorization.py` lines 88-130

- **TDD Validation**:
  - Enforces Red-Green-Refactor cycle
  - Language-aware suggestions
  - Location: `tdd_validator.py` lines 366-433

## Test Failure Analysis

### 1. Security Test Failure ("> /dev/sda")
- **Root Cause**: Missing pattern in rule-based Tier 1
- **Not LLM Related**: Pure pattern matching gap
- **Fix**: Add pattern for device file redirects

### 2. TDD Test Failures (Branch Protection)
- **Root Cause**: Tests running on 'main' branch
- **Not Processor Issue**: Branch validation working correctly
- **Fix**: Tests should use feature branch environment

### 3. Language Suggestion Hallucination
- **Root Cause**: Gemini LLM generating cross-language suggestions
- **LLM Issue**: Despite prompts saying "no Java references"
- **Known Issue**: Documented as Gemini limitation

## Key Architectural Insights

1. **Hybrid Design**: Mix of fast rule-based and intelligent LLM processing
2. **Fail-Safe**: Defaults to blocking when uncertain
3. **Parallel Execution**: Security and TDD run concurrently via asyncio
4. **Context Persistence**: 20-minute cache for test results and todos
5. **Streaming JSON**: Handles Gemini's streamed responses properly

## Performance Characteristics
- Rule-based tiers: <100ms
- LLM tiers: 2-10 seconds depending on complexity
- Parallel execution reduces overall latency
- 8-second timeout for Claude Code hooks
