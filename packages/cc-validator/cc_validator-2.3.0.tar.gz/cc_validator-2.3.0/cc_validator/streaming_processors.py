#!/usr/bin/env python3
"""
Streaming processors implementation following genai-processors pattern.
Refactors all validation operations to use proper async streaming.
"""

import json
from typing import AsyncIterable, Optional, Dict, Any, Type
from pydantic import BaseModel

try:
    from genai_processors import processor, ProcessorPart, streams, content_api
    from genai_processors.core import genai_model
    from google import genai
    from google.genai import types
except ImportError:
    processor = None
    ProcessorPart = None
    streams = None
    content_api = None
    genai_model = None
    genai = None
    types = None

from .config import (
    GEMINI_MODEL,
    FILE_CATEGORIZATION_MODEL,
    SECURITY_THINKING_BUDGET,
    TDD_THINKING_BUDGET,
)
from .models import TDDValidationResponse, FileCategorizationResponse


def extract_json_from_part(part: Any) -> Dict[str, Any]:
    """Extract JSON data from a ProcessorPart"""
    try:
        # If part has text attribute, parse it as JSON
        if hasattr(part, "text") and part.text:
            return json.loads(part.text)  # type: ignore[no-any-return]
        # Fallback to json attribute if available
        elif hasattr(part, "json") and part.json:
            return part.json  # type: ignore[no-any-return]
        else:
            return {}
    except (json.JSONDecodeError, AttributeError):
        return {}


class ValidationProcessor(processor.PartProcessor):  # type: ignore[misc]
    """Base validation processor implementing streaming pattern"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = GEMINI_MODEL,
        thinking_budget: Optional[int] = None,
        response_schema: Optional[Type[BaseModel]] = None,
    ):
        super().__init__()
        self.api_key = api_key
        self.model_name = model_name
        self.thinking_budget = thinking_budget
        self.response_schema = response_schema
        self._genai_processor = None

    def _create_genai_processor(self) -> Optional[Any]:
        """Create GenAI processor with configuration"""
        if not self.api_key or not genai_model:
            return None

        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=self.response_schema,
        )

        if self.thinking_budget:
            config.thinking_config = types.ThinkingConfig(
                thinking_budget=self.thinking_budget
            )

        return genai_model.GenaiModel(
            api_key=self.api_key,
            model_name=self.model_name,
            generate_content_config=config,
        )

    def match(self, part: ProcessorPart) -> bool:
        """Check if this processor can handle the given part"""
        # Override in subclasses for specific matching logic
        return hasattr(part, "text") and part.text

    async def call(self, part: ProcessorPart) -> AsyncIterable[ProcessorPart]:
        """Process the input part and yield results"""
        # Default implementation - override in subclasses
        yield part

    def __add__(self, other: "ValidationProcessor") -> "ChainedProcessor":
        """Enable chaining processors with the + operator"""
        if isinstance(other, ChainedProcessor):
            return ChainedProcessor([self] + other.processors)
        elif isinstance(other, ValidationProcessor):
            return ChainedProcessor([self, other])
        else:
            raise TypeError(f"Cannot chain with {type(other)}")


class SecurityValidationProcessor(ValidationProcessor):
    """Security validation processor with streaming"""

    def __init__(self, api_key: Optional[str] = None):
        from .security_validator import ValidationResponse

        super().__init__(
            api_key=api_key,
            thinking_budget=SECURITY_THINKING_BUDGET,
            response_schema=ValidationResponse,
        )
        self.processor_type = "security"

    async def call(self, part: ProcessorPart) -> AsyncIterable[ProcessorPart]:
        """Process security validation request"""
        if not self._genai_processor:
            self._genai_processor = self._create_genai_processor()

        if not self._genai_processor:
            # ProcessorPart takes content as first positional argument
            error_data = {"error": "No API key configured", "approved": False}
            yield ProcessorPart(json.dumps(error_data))
            return

        # Extract validation request from part
        validation_request = extract_json_from_part(part)
        prompt = validation_request.get("prompt", "")

        # Create input stream for GenAI processor
        input_stream = [content_api.ProcessorPart(prompt)]

        # Process through GenAI using synchronous execution
        response_text = ""
        processed_parts = processor.apply_sync(self._genai_processor, input_stream)
        for content_part in processed_parts:
            if hasattr(content_part, "text") and content_part.text:
                response_text += content_part.text

        # Parse and yield result
        try:
            result = json.loads(response_text)
            yield ProcessorPart(json.dumps(result))
        except json.JSONDecodeError:
            error_data = {
                "error": "Failed to parse response",
                "raw": response_text,
                "approved": False,
            }
            yield ProcessorPart(json.dumps(error_data))


class TDDValidationProcessor(ValidationProcessor):
    """TDD validation processor with streaming"""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(
            api_key=api_key,
            thinking_budget=TDD_THINKING_BUDGET,
            response_schema=TDDValidationResponse,
        )
        self.processor_type = "tdd"

    async def call(self, part: ProcessorPart) -> AsyncIterable[ProcessorPart]:
        """Process TDD validation request"""
        if not self._genai_processor:
            self._genai_processor = self._create_genai_processor()

        if not self._genai_processor:
            error_data = {
                "error": "No API key configured",
                "approved": False,
                "tdd_phase": "unknown",
            }
            yield ProcessorPart(json.dumps(error_data))
            return

        # Extract validation request
        validation_request = extract_json_from_part(part)
        prompt = validation_request.get("prompt", "")

        if not prompt:
            error_data = {
                "error": "No prompt provided for TDD validation",
                "approved": False,
                "tdd_phase": "unknown",
            }
            yield ProcessorPart(json.dumps(error_data))
            return

        # Create input stream
        input_stream = [content_api.ProcessorPart(prompt)]

        # Process through GenAI using synchronous execution
        response_text = ""
        processed_parts = processor.apply_sync(self._genai_processor, input_stream)
        for content_part in processed_parts:
            if hasattr(content_part, "text") and content_part.text:
                response_text += content_part.text

        # Parse and yield result
        try:
            result = json.loads(response_text)
            yield ProcessorPart(json.dumps(result))
        except json.JSONDecodeError:
            error_data = {
                "error": "Failed to parse response",
                "raw": response_text,
                "approved": False,
                "tdd_phase": "unknown",
            }
            yield ProcessorPart(json.dumps(error_data))


class FileCategorizationPromptBuilder(ValidationProcessor):
    """Builds file categorization prompt from tool input data"""

    def match(self, part: ProcessorPart) -> bool:
        data = extract_json_from_part(part)

        # Skip file categorization if there are collection errors (heuristic will handle it)
        tdd_context = data.get("tdd_context", {})
        test_results = tdd_context.get("test_results", {})
        if test_results and len(test_results.get("collection_errors", [])) > 0:
            return False

        return (
            data.get("is_tdd_relevant", False)
            and "tdd_context" in data
            and "tool_input" in data
            and "prompt" not in data
        )

    async def call(self, part: ProcessorPart) -> AsyncIterable[ProcessorPart]:
        data = extract_json_from_part(part)
        tool_input = data.get("tool_input", {})
        file_path = tool_input.get("file_path", "")

        # Get content based on tool type
        tool_name = data.get("tool_name", "")
        if tool_name == "Write":
            content = tool_input.get("content", "")
        elif tool_name in ["Edit", "MultiEdit"]:
            # For Edit/MultiEdit, read file content if needed
            import os

            content = ""
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                except Exception:
                    pass
        else:
            content = tool_input.get("content", "")

        # Build categorization prompt
        prompt = f"""Analyze this code file to determine its category.

FILE PATH: {file_path}
FILE CONTENT:
```
{content[:32768] if content else ""}
```

CATEGORIES:
- "test": Test files containing test functions/classes
- "implementation": Code with executable logic (functions, classes, business logic)
- "structural": Files with ONLY imports, constants, metadata (__version__, __author__), and NO executable code
- "config": Configuration files (JSON, YAML, TOML, etc.)
- "docs": Documentation files
- "data": Data files (CSV, SQL, etc.)
- "template": UI templates (HTML, Jinja2, etc.)

SPECIAL CASES:
- setup.py files are ALWAYS "config" (Python packaging configuration)
- pyproject.toml files are ALWAYS "config" (Python project configuration)
- Dockerfile, Makefile, docker-compose.yml are ALWAYS "config"
- __init__.py files with only imports/metadata are "structural", NOT "implementation"

IMPORTANT: Simple Python files with functions like "def add(a, b): return a + b" are "implementation", NOT documentation.

Respond with ONLY this JSON:
{{
  "category": "<category>",
  "reason": "<brief explanation>",
  "requires_tdd": <true for test/implementation, false for others>
}}"""

        data["prompt"] = prompt
        yield ProcessorPart(json.dumps(data))


class TDDPromptBuilder(ValidationProcessor):
    """Builds TDD validation prompt from tool input data for deep analysis"""

    def match(self, part: ProcessorPart) -> bool:
        data = extract_json_from_part(part)
        return data.get("heuristic_decision") == "proceed" and "tdd_prompt" not in data

    async def call(self, part: ProcessorPart) -> AsyncIterable[ProcessorPart]:
        from .tdd_prompts import (
            TDDCorePrompt,
            EditAnalysisPrompt,
            WriteAnalysisPrompt,
            MultiEditAnalysisPrompt,
            TDDContextFormatter,
        )

        data = extract_json_from_part(part)
        tool_name = data.get("tool_name", "")
        tool_input = data.get("tool_input", {})
        tdd_context = data.get("tdd_context", {})

        # Build the appropriate prompt based on tool type
        if tool_name == "Edit":
            old_content = tool_input.get("old_string", "")
            new_content = tool_input.get("new_string", "")
            file_path = tool_input.get("file_path", "")

            operation_prompt = EditAnalysisPrompt.get_analysis_prompt(
                old_content, new_content, file_path
            )
        elif tool_name == "Write":
            file_path = tool_input.get("file_path", "")
            content = tool_input.get("content", "")

            operation_prompt = WriteAnalysisPrompt.get_analysis_prompt(
                file_path, content
            )
        elif tool_name == "MultiEdit":
            edits = tool_input.get("edits", [])

            operation_prompt = MultiEditAnalysisPrompt.get_analysis_prompt(edits)
        elif tool_name == "Update":
            # For Update operations, compare old vs new content like Edit
            file_path = tool_input.get("file_path", "")
            new_content = tool_input.get("content", "")

            # Read existing content if file exists
            import os

            old_content = ""
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        old_content = f.read()
                except Exception:
                    pass

            # If file doesn't exist, treat as Write operation
            if not old_content:
                operation_prompt = WriteAnalysisPrompt.get_analysis_prompt(
                    file_path, new_content
                ).replace("WRITE ANALYSIS", "UPDATE ANALYSIS (NEW FILE)")
            else:
                # Use Edit-style analysis for comparing old vs new
                operation_prompt = f"""
# UPDATE ANALYSIS

FILE: {file_path}

OLD CONTENT:
```
{old_content}
```

NEW CONTENT:
```
{new_content}
```

VALIDATE:
1. Count NET new tests (new tests - removed tests, only +1 allowed)
2. Check for comments (NONE allowed)  
3. Verify minimal implementation
4. Ensure SOLID compliance
5. Zen of Python adherence

DECISION: Block if TDD/quality rules violated.
"""
        else:
            # Fallback for unknown operations
            operation_prompt = f"# UNKNOWN OPERATION ANALYSIS\n\nOperation: {tool_name}\nValidate for TDD compliance."

        # Build complete TDD validation prompt
        tdd_principles = TDDCorePrompt.get_tdd_principles()
        context_section = TDDContextFormatter.format_tdd_context(tdd_context)

        complete_prompt = f"""{tdd_principles}

{context_section}

{operation_prompt}

# VALIDATION DECISION

Analyze the operation and provide a structured JSON response:

{{
  "approved": <boolean>,
  "violation_type": "<type if blocked>",
  "test_count": <number of new tests added>,
  "affected_files": ["<list of affected files>"],
  "tdd_phase": "<red|green|refactor>",
  "reason": "<detailed reason>",
  "suggestions": ["<list of suggestions>"],
  "detailed_analysis": "<comprehensive analysis>"
}}

CRITICAL: Block if multiple new tests are added (test_count > 1). The TDD rule is ONE test per operation."""

        data["prompt"] = complete_prompt
        yield ProcessorPart(json.dumps(data))


class FileCategorizationProcessor(ValidationProcessor):
    """File categorization processor with streaming"""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(
            api_key=api_key,
            model_name=FILE_CATEGORIZATION_MODEL,
            thinking_budget=None,  # No thinking for categorization
            response_schema=FileCategorizationResponse,
        )

    def match(self, part: ProcessorPart) -> bool:
        """Only process TDD-relevant operations that have a categorization prompt"""
        data = extract_json_from_part(part)

        # Skip file categorization if there are collection errors (heuristic will handle it)
        tdd_context = data.get("tdd_context", {})
        test_results = tdd_context.get("test_results", {})
        if test_results and len(test_results.get("collection_errors", [])) > 0:
            return False

        return data.get("is_tdd_relevant", False) and "prompt" in data

    async def call(self, part: ProcessorPart) -> AsyncIterable[ProcessorPart]:
        """Process file categorization request"""
        if not self._genai_processor:
            self._genai_processor = self._create_genai_processor()

        if not self._genai_processor:
            # No fallback - operation requires API key
            error_data = {
                "error": "GEMINI_API_KEY required for file categorization",
                "approved": False,
            }
            yield ProcessorPart(json.dumps(error_data))
            return

        # Extract request
        request = extract_json_from_part(part)
        prompt = request.get("prompt", "")

        # Create input stream
        input_stream = [content_api.ProcessorPart(prompt)]

        # Process through GenAI using synchronous execution
        response_text = ""
        processed_parts = processor.apply_sync(self._genai_processor, input_stream)
        for content_part in processed_parts:
            if hasattr(content_part, "text") and content_part.text:
                response_text += content_part.text

        # Parse and add to existing data
        try:
            categorization_result = json.loads(response_text)
            # Merge categorization result with existing data
            merged_data = dict(request)
            merged_data["file_category"] = categorization_result
            yield ProcessorPart(json.dumps(merged_data))
        except json.JSONDecodeError:
            # If parsing fails, merge fallback categorization with existing data
            fallback_categorization = {
                "category": "unknown",
                "requires_tdd": True,
                "reason": "Failed to parse categorization",
            }
            merged_data = dict(request)
            merged_data["file_category"] = fallback_categorization
            yield ProcessorPart(json.dumps(merged_data))


class ParallelValidationPipeline:
    """Pipeline for running security and TDD validation in parallel using genai-processors"""

    def __init__(self, api_key: Optional[str] = None):
        self.security_processor = SecurityValidationProcessor(api_key)
        self.tdd_processor = TDDValidationProcessor(api_key)

        # Create parallel processor using genai-processors built-in parallel execution
        if processor:
            self.parallel_processor = processor.parallel_concat(
                [self.security_processor, self.tdd_processor]
            )
        else:
            self.parallel_processor = None

    def process_parallel(
        self,
        security_request: Dict[str, Any],
        tdd_request: Dict[str, Any],
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Run security and TDD validation in parallel using processor.parallel_concat()"""

        if not self.parallel_processor:
            # Fallback for environments without genai_processors
            return self._fallback_parallel_processing(security_request, tdd_request)

        # Create unified input parts with both requests
        input_parts = [
            ProcessorPart(
                json.dumps({**security_request, "_processor_type": "security"})
            ),
            ProcessorPart(json.dumps({**tdd_request, "_processor_type": "tdd"})),
        ]

        # Process through parallel processor synchronously
        security_result = None
        tdd_result = None

        processed_parts = processor.apply_sync(self.parallel_processor, input_parts)
        for result_part in processed_parts:
            result_data = extract_json_from_part(result_part)
            if not result_data:
                continue

            # Route results based on processor type or content
            if self._is_security_result(result_data):
                if not security_result:
                    security_result = result_data
            elif self._is_tdd_result(result_data):
                if not tdd_result:
                    tdd_result = result_data

        # Ensure we have both results with fallbacks
        if not security_result:
            security_result = {
                "approved": False,
                "reason": "Security validation did not complete",
            }

        if not tdd_result:
            tdd_result = {
                "approved": False,
                "reason": "TDD validation did not complete",
                "tdd_phase": "unknown",
            }

        return security_result, tdd_result

    def _is_security_result(self, result_data: Dict[str, Any]) -> bool:
        """Determine if result is from security validation"""
        return (
            "_processor_type" in result_data
            and result_data["_processor_type"] == "security"
        ) or (
            "security" in str(result_data.get("reason", "")).lower()
            or "threat" in str(result_data.get("reason", "")).lower()
            or "vulnerability" in str(result_data.get("reason", "")).lower()
        )

    def _is_tdd_result(self, result_data: Dict[str, Any]) -> bool:
        """Determine if result is from TDD validation"""
        return (
            "_processor_type" in result_data and result_data["_processor_type"] == "tdd"
        ) or (
            "tdd_phase" in result_data
            or "test" in str(result_data.get("reason", "")).lower()
        )

    def _fallback_parallel_processing(
        self, security_request: Dict[str, Any], tdd_request: Dict[str, Any]
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Fallback processing when genai_processors is not available"""

        # Run processors sequentially since this is fallback code
        security_part = ProcessorPart(json.dumps(security_request))
        tdd_part = ProcessorPart(json.dumps(tdd_request))

        # Process security validation synchronously
        try:
            security_results = processor.apply_sync(
                self.security_processor, [security_part]
            )
            security_result: Any = self._collect_results_sync(security_results)
        except Exception as e:
            security_result = {
                "approved": False,
                "reason": f"Security validation blocked: {str(e)}",
            }

        # Process TDD validation synchronously
        try:
            tdd_results = processor.apply_sync(self.tdd_processor, [tdd_part])
            tdd_result: Any = self._collect_results_sync(tdd_results)
        except Exception as e:
            tdd_result = {
                "approved": False,
                "reason": f"TDD validation blocked: {str(e)}",
                "tdd_phase": "unknown",
            }

        # Handle exceptions
        if isinstance(security_result, Exception):
            security_result = {
                "approved": False,
                "reason": f"Security validation error: {str(security_result)}",
            }

        if isinstance(tdd_result, Exception):
            tdd_result = {
                "approved": False,
                "reason": f"TDD validation error: {str(tdd_result)}",
                "tdd_phase": "unknown",
            }

        return security_result, tdd_result

    def _collect_results_from_stream(
        self, parts: list[ProcessorPart]
    ) -> Dict[str, Any]:
        """Collect results from a list of ProcessorParts"""
        result = {}
        for part in parts:
            json_data = extract_json_from_part(part)
            if json_data:
                result.update(json_data)
        return result

    def _collect_results_sync(self, parts: list[ProcessorPart]) -> Dict[str, Any]:
        """Collect results from a list of ProcessorParts synchronously"""
        result = {}
        for part in parts:
            json_data = extract_json_from_part(part)
            if json_data:
                result.update(json_data)
        return result


class ChainedProcessor(ValidationProcessor):
    """Processor that chains multiple processors together"""

    def __init__(self, processors: list[ValidationProcessor]):
        super().__init__()
        self.processors = processors

    def match(self, part: ProcessorPart) -> bool:
        """A chained processor matches if any of its processors match"""
        return any(p.match(part) for p in self.processors)

    async def call(self, part: ProcessorPart) -> AsyncIterable[ProcessorPart]:
        """Process the input through all processors in sequence"""
        # Start with the input part
        current_parts = [part]

        # Process through each processor in the chain
        for processor_instance in self.processors:
            next_parts = []
            for current_part in current_parts:
                if processor_instance.match(current_part):
                    # Process the part using async execution
                    async for processed_part in processor_instance.call(current_part):
                        next_parts.append(processed_part)
                else:
                    # If processor doesn't match, pass through unchanged
                    next_parts.append(current_part)
            current_parts = next_parts

        # Yield all final results
        for final_part in current_parts:
            yield final_part

    def process_sync(self, input_parts: list[ProcessorPart]) -> list[ProcessorPart]:
        """Process input parts through all processors in sequence synchronously"""
        # Process all parts through the chain synchronously
        results = []
        for part in input_parts:
            processed_parts = processor.apply_sync(self, [part])
            results.extend(processed_parts)
        return results

    def __add__(self, other: ValidationProcessor) -> "ChainedProcessor":
        """Enable further chaining of already chained processors"""
        if isinstance(other, ChainedProcessor):
            return ChainedProcessor(self.processors + other.processors)
        elif isinstance(other, ValidationProcessor):
            return ChainedProcessor(self.processors + [other])
        else:
            raise TypeError(f"Cannot chain with {type(other)}")


class ProcessorChain:
    """Custom chaining implementation for processors"""

    def __init__(self, processors: list[ValidationProcessor]):
        self.processors = processors

    async def __call__(
        self, input_stream: AsyncIterable[ProcessorPart]
    ) -> AsyncIterable[ProcessorPart]:
        """Process input stream through all processors in parallel"""
        # Convert stream to parts
        input_parts = []
        async for part in input_stream:
            input_parts.append(part)

        # Process each input part through all processors independently
        for part in input_parts:
            for processor_instance in self.processors:
                if processor_instance.match(part):
                    # Process using async call - each processor gets the original input
                    async for processed_part in processor_instance.call(part):
                        yield processed_part

    def process_sync(self, input_parts: list[ProcessorPart]) -> list[ProcessorPart]:
        """Process input through all processors in sequence synchronously"""
        # Process through each processor in the chain
        current_parts = input_parts
        results = []
        for processor_instance in self.processors:
            next_parts = []
            for part in current_parts:
                if processor_instance.match(part):
                    # Use processor.apply_sync for synchronous processing
                    processed_parts = processor.apply_sync(processor_instance, [part])
                    next_parts.extend(processed_parts)
                    results.extend(processed_parts)
                else:
                    next_parts.append(part)
            current_parts = next_parts
        return results


class ValidationPipelineBuilder:
    """Builder for creating validation pipelines"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def create_security_pipeline(self) -> ValidationProcessor:
        """Create security validation pipeline"""
        return SecurityValidationProcessor(self.api_key)

    def create_tdd_pipeline(self) -> ValidationProcessor:
        """Create TDD validation pipeline"""
        return TDDValidationProcessor(self.api_key)

    def create_file_categorization_pipeline(self) -> ValidationProcessor:
        """Create file categorization pipeline"""
        return FileCategorizationProcessor(self.api_key)

    def create_parallel_pipeline(self) -> ParallelValidationPipeline:
        """Create parallel validation pipeline"""
        return ParallelValidationPipeline(self.api_key)

    def create_chained_pipeline(
        self, processors: list[ValidationProcessor]
    ) -> ProcessorChain:
        """Create a chained pipeline from multiple processors"""
        return ProcessorChain(processors)
