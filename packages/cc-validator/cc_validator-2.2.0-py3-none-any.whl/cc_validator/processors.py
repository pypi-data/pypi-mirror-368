#!/usr/bin/env python3
"""
GenAI Processors implementation for Claude Code ADK Validator.
Converts generate_content calls to processor-based streaming pattern.
"""

import asyncio
import json
from typing import Optional, Dict, Any, Type

try:
    from genai_processors import content_api, streams
    from genai_processors.core import genai_model
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    genai_processors = None
    genai_model = None


from .config import (
    GEMINI_MODEL,
    FILE_CATEGORIZATION_MODEL,
    SECRET_VALIDATION_MODEL,
    SECURITY_THINKING_BUDGET,
    TDD_THINKING_BUDGET,
    FILE_ANALYSIS_THINKING_BUDGET,
    SECRET_VALIDATION_THINKING_BUDGET,
)


class BaseValidationProcessor:
    """Base class for validation processors using GenAI Processors pattern"""

    def __init__(self, api_key: Optional[str] = None, model_name: str = GEMINI_MODEL):
        self.api_key = api_key
        self.model_name = model_name
        self._processor = None

    def _get_processor(
        self,
        thinking_budget: Optional[int] = None,
        response_schema: Optional[Type[Any]] = None,
    ) -> Optional[Any]:
        """Get or create a GenAI processor with specified configuration"""
        if not self.api_key or not genai_model:
            return None

        if not self._processor:
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=response_schema,
            )

            if thinking_budget:
                config.thinking_config = types.ThinkingConfig(
                    thinking_budget=thinking_budget
                )

            self._processor = genai_model.GenaiModel(
                api_key=self.api_key,
                model_name=self.model_name,
                generate_content_config=config,
            )

        return self._processor

    async def process_prompt(
        self,
        prompt: str,
        thinking_budget: Optional[int] = None,
        response_schema: Optional[Type[Any]] = None,
        uploaded_file: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Process a prompt through the GenAI processor and return structured response"""
        processor = self._get_processor(thinking_budget, response_schema)

        if not processor:
            return {"error": "No API key configured"}

        # Create input stream
        input_parts = []
        input_parts.append(content_api.ProcessorPart(prompt))

        if uploaded_file:
            input_parts.append(uploaded_file)

        input_stream = streams.stream_content(input_parts)

        # Process through the model
        response_text = ""
        async for part in processor(input_stream):
            if hasattr(part, "text") and part.text:
                response_text += part.text

        # Parse JSON response
        try:
            return json.loads(response_text)  # type: ignore[no-any-return]
        except json.JSONDecodeError:
            return {"error": "Failed to parse response", "raw": response_text}


class SecurityValidationProcessor(BaseValidationProcessor):
    """Security validation using GenAI Processors"""

    async def validate_security(
        self,
        prompt: str,
        response_schema: Type[Any],
        thinking_budget: int = SECURITY_THINKING_BUDGET,
    ) -> Dict[str, Any]:
        """Run security validation through processor"""
        return await self.process_prompt(prompt, thinking_budget, response_schema)

    async def validate_secrets(
        self,
        prompt: str,
        response_schema: Type[Any],
        thinking_budget: int = SECRET_VALIDATION_THINKING_BUDGET,
    ) -> Dict[str, Any]:
        """Run secret validation through processor"""
        # Use secret validation model
        original_model = self.model_name
        self.model_name = SECRET_VALIDATION_MODEL
        self._processor = None  # Reset processor to use new model

        result = await self.process_prompt(prompt, thinking_budget, response_schema)

        # Restore original model
        self.model_name = original_model
        self._processor = None

        return result

    async def analyze_file(
        self,
        prompt: str,
        uploaded_file: Any,
        response_schema: Type[Any],
        thinking_budget: int = FILE_ANALYSIS_THINKING_BUDGET,
    ) -> Dict[str, Any]:
        """Run file analysis through processor"""
        return await self.process_prompt(
            prompt, thinking_budget, response_schema, uploaded_file
        )


class TDDValidationProcessor(BaseValidationProcessor):
    """TDD validation using GenAI Processors"""

    async def validate_tdd(
        self,
        prompt: str,
        response_schema: Type[Any],
        thinking_budget: int = TDD_THINKING_BUDGET,
    ) -> Dict[str, Any]:
        """Run TDD validation through processor"""
        return await self.process_prompt(prompt, thinking_budget, response_schema)

    async def categorize_file(
        self,
        prompt: str,
        response_schema: Type[Any],
    ) -> Dict[str, Any]:
        """Run file categorization through processor"""
        # Use file categorization model
        original_model = self.model_name
        self.model_name = FILE_CATEGORIZATION_MODEL
        self._processor = None  # Reset processor to use new model

        result = await self.process_prompt(prompt, None, response_schema)

        # Restore original model
        self.model_name = original_model
        self._processor = None

        return result


class ParallelValidationProcessor:
    """Run multiple validations in parallel using processors"""

    def __init__(self, api_key: Optional[str] = None):
        self.security_processor = SecurityValidationProcessor(api_key)
        self.tdd_processor = TDDValidationProcessor(api_key)

    async def validate_parallel(
        self,
        security_prompt: str,
        security_schema: type,
        tdd_prompt: str,
        tdd_schema: type,
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Run security and TDD validation in parallel"""
        security_task = self.security_processor.validate_security(
            security_prompt, security_schema
        )
        tdd_task = self.tdd_processor.validate_tdd(tdd_prompt, tdd_schema)

        # Run both validations in parallel
        results = await asyncio.gather(security_task, tdd_task, return_exceptions=True)
        security_result: Any = results[0]
        tdd_result: Any = results[1]

        # Handle exceptions
        if isinstance(security_result, Exception):
            security_result = {
                "approved": False,
                "reason": f"Security validation blocked: {str(security_result)}",
            }

        if isinstance(tdd_result, Exception):
            tdd_result = {
                "approved": False,
                "reason": f"TDD validation blocked: {str(tdd_result)}",
                "tdd_phase": "unknown",
            }

        return security_result, tdd_result
