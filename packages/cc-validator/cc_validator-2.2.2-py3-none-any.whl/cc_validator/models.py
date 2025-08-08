#!/usr/bin/env python3
"""
Pydantic models for the CC-Validator.
"""

from dataclasses import dataclass
from typing import Optional, List
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class TDDValidationResponse:
    """TDD-specific validation response model"""

    approved: bool
    tdd_phase: str = "unknown"
    reason: str = ""
    violation_type: Optional[str] = None
    test_count: Optional[int] = None
    affected_files: Optional[List[str]] = None
    suggestions: Optional[List[str]] = None
    detailed_analysis: Optional[str] = None

    def __post_init__(self) -> None:
        if self.affected_files is None:
            self.affected_files = []
        if self.suggestions is None:
            self.suggestions = []


@dataclass_json
@dataclass
class FileCategorizationResponse:
    """Response model for file categorization"""

    category: str
    reason: str
    requires_tdd: bool
