#!/usr/bin/env python3
"""
Pure processor validation entry point - replaces monolithic HybridValidator.
Provides direct access to pure processor pipelines without complex orchestration layers.
"""

from typing import Optional, Dict, Any

try:
    from genai_processors import processor, content_api
except ImportError:
    processor = None
    content_api = None

from .canonical_pipeline import CanonicalPipelineValidator
from .file_storage import FileStorage
from .config import ProcessorConfig


class PureValidationPipeline:
    """
    Direct pure processor validation pipeline.
    Now uses the canonical pipeline implementation for consistency.
    """

    def __init__(
        self,
        config: Optional[ProcessorConfig] = None,
        data_dir: str = ".claude/cc-validator/data",
    ):
        self.config = config
        self.data_dir = data_dir
        self.file_storage = FileStorage(data_dir)
        self.file_storage.cleanup_expired_data()
        self.canonical_validator = CanonicalPipelineValidator(
            self.file_storage, self.config
        )

    def create_validation_processor(self) -> CanonicalPipelineValidator:
        """Return the canonical pipeline validation function."""
        return self.canonical_validator

    async def validate_tool_use(
        self, tool_name: str, tool_input: Dict[str, Any], context: str
    ) -> Dict[str, Any]:
        """
        Pure processor validation entry point using canonical pipeline.

        Args:
            tool_name: The Claude tool being executed (Bash, Write, Edit, etc.)
            tool_input: The tool's input parameters
            context: Conversation context from transcript

        Returns:
            Validation response with security and TDD analysis
        """

        # Use canonical pipeline for all validation
        return await self.canonical_validator.validate_tool_use_async(
            tool_name, tool_input, context
        )

    def before_tool_callback(self, hook_data: Dict[str, Any]) -> int:
        """
        Main hook callback for Claude Code integration.
        Delegates to canonical pipeline validator.
        """
        return self.canonical_validator.before_tool_callback(hook_data)
