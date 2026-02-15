"""
Domain models package.
Contains data models for the PDF merger application.
"""

from .enums import MatchBehavior, MatchConfidence, RowStatus
from .merge_job import MergeJob
from .merge_result import MergeResult, RowResult
from .row import Row

__all__ = [
    "Row",
    "MergeJob",
    "MergeResult",
    "RowResult",
    "RowStatus",
    "MatchConfidence",
    "MatchBehavior",
]
