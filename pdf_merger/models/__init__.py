"""
Domain models package.
Contains data models for Files Unifier.
"""

from .row import Row
from .merge_job import MergeJob
from .merge_result import MergeResult, RowResult
from ..core.enums import RowStatus

__all__ = ['Row', 'MergeJob', 'MergeResult', 'RowResult', 'RowStatus']
