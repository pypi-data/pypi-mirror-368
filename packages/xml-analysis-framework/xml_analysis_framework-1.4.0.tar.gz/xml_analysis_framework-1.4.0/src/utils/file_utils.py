#!/usr/bin/env python3
"""
File utility functions for XML analysis framework

Provides helper functions for file validation, size checking, and safe file handling.
"""

import os
from pathlib import Path
from typing import Optional, Tuple


def validate_file_size(
    file_path: str, max_size_mb: Optional[float] = None
) -> Tuple[bool, float, Optional[str]]:
    """
    Validate file size against a maximum limit

    Args:
        file_path: Path to the file to check
        max_size_mb: Maximum allowed size in megabytes. If None, no limit is enforced.

    Returns:
        Tuple of (is_valid, file_size_mb, error_message)
        - is_valid: True if file is within limits or no limit set
        - file_size_mb: Actual file size in megabytes
        - error_message: Error description if file is too large, None otherwise
    """
    try:
        file_size_bytes = Path(file_path).stat().st_size
        file_size_mb = file_size_bytes / (1024 * 1024)

        if max_size_mb is not None and file_size_mb > max_size_mb:
            error_msg = (
                f"File too large: {file_size_mb:.2f}MB exceeds limit of {max_size_mb}MB"
            )
            return False, file_size_mb, error_msg

        return True, file_size_mb, None

    except OSError as e:
        error_msg = f"Failed to check file size: {e}"
        return False, 0.0, error_msg


def validate_file_path(file_path: str) -> Tuple[bool, Optional[str]]:
    """
    Validate that a file path exists and is accessible

    Args:
        file_path: Path to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        path = Path(file_path)

        if not path.exists():
            return False, f"File does not exist: {file_path}"

        if not path.is_file():
            return False, f"Path is not a file: {file_path}"

        if not os.access(file_path, os.R_OK):
            return False, f"File is not readable: {file_path}"

        return True, None

    except Exception as e:
        return False, f"File validation error: {e}"


def get_file_info(file_path: str) -> dict:
    """
    Get comprehensive information about a file

    Args:
        file_path: Path to the file

    Returns:
        Dictionary with file information
    """
    try:
        path = Path(file_path)
        stat = path.stat()

        return {
            "path": str(path.absolute()),
            "name": path.name,
            "size_bytes": stat.st_size,
            "size_mb": stat.st_size / (1024 * 1024),
            "size_human": _format_file_size(stat.st_size),
            "extension": path.suffix.lower(),
            "exists": True,
            "is_readable": os.access(file_path, os.R_OK),
            "modified_time": stat.st_mtime,
        }
    except Exception as e:
        return {"path": file_path, "error": str(e), "exists": False}


def _format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f}TB"


# Convenience functions for common file size limits
def create_analyzer_with_limits(max_size_mb: float = 100.0):
    """
    Create XMLDocumentAnalyzer with recommended file size limits

    Args:
        max_size_mb: Maximum file size in MB (default: 100MB)

    Returns:
        XMLDocumentAnalyzer instance with size limits
    """
    from src.core.analyzer import XMLDocumentAnalyzer

    return XMLDocumentAnalyzer(max_file_size_mb=max_size_mb)


def create_chunking_orchestrator_with_limits(max_size_mb: float = 100.0):
    """
    Create ChunkingOrchestrator with recommended file size limits

    Args:
        max_size_mb: Maximum file size in MB (default: 100MB)

    Returns:
        ChunkingOrchestrator instance with size limits
    """
    from src.core.chunking import ChunkingOrchestrator

    return ChunkingOrchestrator(max_file_size_mb=max_size_mb)


def safe_analyze_document(file_path: str, max_size_mb: float = 100.0):
    """
    Safely analyze a document with comprehensive validation

    Args:
        file_path: Path to the XML file
        max_size_mb: Maximum allowed file size in MB

    Returns:
        Analysis result or error dictionary
    """
    # Validate file path
    path_valid, path_error = validate_file_path(file_path)
    if not path_valid:
        return {"error": path_error, "file_path": file_path, "validation_failed": True}

    # Validate file size
    size_valid, file_size_mb, size_error = validate_file_size(file_path, max_size_mb)
    if not size_valid:
        return {
            "error": size_error,
            "file_path": file_path,
            "file_size_mb": file_size_mb,
            "size_limit_exceeded": True,
        }

    # Perform analysis
    analyzer = create_analyzer_with_limits(max_size_mb)
    return analyzer.analyze_document(file_path)


# Default size limits for different use cases
class FileSizeLimits:
    """Recommended file size limits for different scenarios"""

    # Conservative limits for production use
    PRODUCTION_SMALL = 10.0  # 10MB
    PRODUCTION_MEDIUM = 50.0  # 50MB
    PRODUCTION_LARGE = 100.0  # 100MB

    # Development/testing limits
    DEVELOPMENT = 500.0  # 500MB
    TESTING = 1000.0  # 1GB

    # Specialized limits
    REAL_TIME = 5.0  # 5MB for real-time processing
    BATCH_PROCESSING = 200.0  # 200MB for batch processing
    MEMORY_CONSTRAINED = 25.0  # 25MB for memory-constrained environments
