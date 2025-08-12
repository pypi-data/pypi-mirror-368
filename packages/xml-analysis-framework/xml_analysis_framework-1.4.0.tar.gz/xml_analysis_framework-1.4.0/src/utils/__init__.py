"""
Utilities for XML Analysis Framework

This module provides utility functions for file handling, validation, and safety features.
"""

from .file_utils import (
    validate_file_size,
    validate_file_path,
    get_file_info,
    create_analyzer_with_limits,
    create_chunking_orchestrator_with_limits,
    safe_analyze_document,
    FileSizeLimits,
)

__all__ = [
    "validate_file_size",
    "validate_file_path",
    "get_file_info",
    "create_analyzer_with_limits",
    "create_chunking_orchestrator_with_limits",
    "safe_analyze_document",
    "FileSizeLimits",
]
