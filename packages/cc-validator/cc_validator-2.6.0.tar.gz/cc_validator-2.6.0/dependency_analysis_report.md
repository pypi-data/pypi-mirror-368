# CC-Validator File Dependency Analysis Report

## Overview
Analysis of all Python files in cc_validator/ directory to identify dependencies, usage patterns, and potential dead code.

## Entry Points

### Primary Entry Points
- **main.py** - CLI script entry point (pyproject.toml: `cc-validator = "cc_validator.main:main"`)
- **__main__.py** - Python module entry point (`python -m cc_validator`)
- **pytest_plugin.py** - Pytest plugin integration (pyproject.toml entry point)
- **__init__.py** - Public package API exports

## Core Architecture Files

### Heavily Used Core Files (10+ imports)
- **config.py** (11 imports) - Configuration constants and settings
- **file_storage.py** (15 imports) - Context persistence and storage
- **validation_models.py** (13 imports) - Core validation data models and utilities
- **file_categorization.py** (9 imports) - File type detection and analysis

### Primary Validation Components (5+ imports)
- **security_processors.py** (8 imports) - Security validation processors
- **streaming_processors.py** (6 imports) - Base streaming processor classes
- **pure_validation.py** (6 imports) - Main validation pipeline (public API)
- **security_validator.py** (5 imports) - Security-only validator (public API)

## Supporting Components

### Processor Infrastructure
- **processor_factories.py** (3 imports) - Factory functions for processor parts
- **unified_processor.py** (2 imports) - Unified processing logic
- **pipeline_orchestrator.py** (3 imports) - Pipeline orchestration
- **tdd_processors.py** (2 imports) - TDD-specific processors
- **canonical_part_processors.py** (1 import) - Canonical processor implementations

### Specialized Components
- **models.py** (2 imports) - TDD and file categorization response models
- **tdd_prompts.py** (1 import) - TDD prompt templates
- **validation_dataclasses.py** (2 imports) - Validation data classes
- **reporters.py** (2 imports) - Test result reporting utilities

## Potentially Unused Files (DEAD CODE CANDIDATES)

### Files with Zero Imports
1. **canonical_processors.py** - No imports found
   - Contains processor implementations but not used anywhere
   - Potentially replaced by newer processor architecture

2. **processors.py** - No imports found
   - Legacy processor implementations
   - Only imports config.py but is not imported by anything

3. **validation_pipeline.py** - No imports found
   - Contains validation pipeline logic
   - Only used internally, imports streaming_processors

4. **hybrid_validator.py** - No imports found
   - Contains hybrid validation logic
   - May be superseded by pure_validation.py

5. **test_entry.py** - No imports found
   - Development/testing utility
   - Not part of production code path

6. **pure_pipeline_example.py** - No imports found
   - Example/demonstration code
   - Imports pure_processors but not used in production

## Test Coverage Analysis

### Well-Tested Modules
- **file_categorization.py** - 5 test files
- **streaming_processors.py** - 2 dedicated test files
- **security_validator.py** - 3 test files
- **pure_validation.py** - 3 test files
- **canonical_part_processors.py** - 1 dedicated test file

### Modules with Limited/No Direct Tests
- **config.py** - No direct tests (tested implicitly)
- **file_storage.py** - Tested in integration tests
- **models.py** - Tested implicitly through other components
- **validation_models.py** - Tested implicitly
- **processor_factories.py** - No direct tests

## Import Chain Analysis

### From Entry Point (main.py)
```
main.py
├── pure_validation.PureValidationPipeline
├── config (DEFAULT_HOOK_TIMEOUT, ProcessorConfig)
└── reporters.store_manual_test_results
```

### From Public API (__init__.py)
```
__init__.py
├── pure_validation.PureValidationPipeline
├── security_validator.SecurityValidator  
├── file_storage.FileStorage
├── file_categorization.FileContextAnalyzer
├── pytest_plugin.PytestReporter
└── reporters (multiple classes)
```

### Core Dependency Chain
```
streaming_processors.py (base classes)
├── security_processors.py
├── tdd_processors.py
└── canonical_part_processors.py
    └── validation_pipeline.py (unused?)
```

## Recommendations

### Files Safe to Remove (After Verification)
1. **canonical_processors.py** - Not imported anywhere
2. **processors.py** - Legacy code, not used
3. **validation_pipeline.py** - Superseded by streaming architecture
4. **hybrid_validator.py** - Functionality moved to pure_validation.py
5. **pure_pipeline_example.py** - Example code, not production

### Files to Investigate Further
1. **test_entry.py** - Confirm it's only for development
2. **tdd_prompts.py** - Only imported once, check if still needed

### Architecture Notes
- The codebase has evolved from a hybrid validation approach to a pure processor-based architecture
- Many files ending in "processors.py" are actively used
- The streaming_processors.py provides the base architecture for the current system
- Legacy files (processors.py, hybrid_validator.py) appear to be replaced by newer implementations

## File Count Summary
- **Total Python files**: 28
- **Entry points**: 4
- **Actively used**: 18
- **Potentially dead code**: 6
- **Test coverage**: ~64% of files have direct or indirect test coverage

## Action Items
1. Verify dead code candidates can be safely removed
2. Add unit tests for processor_factories.py and config.py
3. Consider consolidating similar processor files
4. Update documentation to reflect current architecture