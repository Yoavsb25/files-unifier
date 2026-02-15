"""
Unit tests for core module exports.
"""

from pdf_merger.core import format_result_detailed, format_result_summary, run_merge_job


def test_core_exports():
    """Test that core module exports expected functions."""
    assert callable(run_merge_job)
    assert callable(format_result_summary)
    assert callable(format_result_detailed)
