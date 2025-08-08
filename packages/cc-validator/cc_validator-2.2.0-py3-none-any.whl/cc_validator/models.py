#!/usr/bin/env python3
"""
Pydantic models for the CC-Validator.
"""

from typing import Optional, List
from pydantic import BaseModel


class TDDValidationResponse(BaseModel):
    """TDD-specific validation response model"""

    approved: bool
    violation_type: Optional[str] = None
    test_count: Optional[int] = None
    affected_files: List[str] = []
    tdd_phase: str = "unknown"
    reason: str = ""
    suggestions: List[str] = []
    detailed_analysis: Optional[str] = None


class FileCategorizationResponse(BaseModel):
    """Response model for file categorization"""

    category: str
    reason: str
    requires_tdd: bool
