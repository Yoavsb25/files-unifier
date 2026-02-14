"""
Result view abstraction for formatting.
Provides a unified view over MergeResult for formatters.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional

from .constants import Constants

if TYPE_CHECKING:
    from ..models import MergeResult, RowResult


@dataclass
class ResultView:
    """Unified view of processing result for formatting. Built from MergeResult."""
    total_rows: int
    successful_merges: int
    failed_rows: List[int]
    skipped_rows: List[int]
    success_rate: float
    row_results: List[RowResult]
    total_processing_time: Optional[float] = None


def as_result_view(result: "MergeResult") -> ResultView:
    """Build a ResultView from MergeResult."""
    return _view_from_merge_result(result)


def _view_from_merge_result(result: "MergeResult") -> ResultView:
    """Build ResultView from MergeResult (single code path)."""
    return ResultView(
        total_rows=result.total_rows,
        successful_merges=result.successful_merges,
        failed_rows=result.failed_rows,
        skipped_rows=getattr(result, "skipped_rows", []) or [],
        success_rate=result.get_success_rate(),
        row_results=getattr(result, "row_results", []) or [],
        total_processing_time=getattr(result, "total_processing_time", None),
    )
