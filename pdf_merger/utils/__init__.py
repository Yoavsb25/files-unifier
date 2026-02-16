"""
Utilities package.
Cross-platform utilities and helpers.
"""

from .exceptions import PDFMergerError, PDFMergerFileNotFoundError
from .path_utils import (
    compare_paths,
    enable_long_paths_windows,
    is_long_path,
    normalize_path,
    resolve_path,
)

__all__ = [
    "normalize_path",
    "compare_paths",
    "resolve_path",
    "is_long_path",
    "enable_long_paths_windows",
    "PDFMergerError",
    "PDFMergerFileNotFoundError",
]
