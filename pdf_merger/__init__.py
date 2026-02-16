"""
PDF Merger Package
A modular package for merging PDFs based on serial numbers from CSV/Excel files.

Public API (prefer these for external use; internal modules may change):
- run_merge_job: Run merge operations (return MergeResult)
- load_config, AppConfig: Load and represent configuration
- MergeResult: Result type from merge runs
- PDFMergerError: Base exception for error handling
"""

# Public API: high-level entry points and types only (internal refactors won't break callers)
from .config.config_manager import AppConfig, load_config
from .core.merge_orchestrator import run_merge_job
from .models import MergeResult
from .utils.exceptions import PDFMergerError
from .version import APP_NAME, APP_VERSION, __version__

__all__ = [
    "__version__",
    "APP_VERSION",
    "APP_NAME",
    "run_merge_job",
    "load_config",
    "AppConfig",
    "MergeResult",
    "PDFMergerError",
]
