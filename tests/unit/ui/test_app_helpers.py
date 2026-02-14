"""
Unit tests for app_helpers module.
"""

import pytest
from pathlib import Path

from pdf_merger.ui.app_helpers import get_run_block_reasons, can_run_merge


class TestGetRunBlockReasons:
    """Test cases for get_run_block_reasons."""

    def test_empty_when_all_ready(self):
        """No block reasons when license valid, all paths set, no validation errors, not processing."""
        reasons = get_run_block_reasons(
            license_valid=True,
            input_file_path=Path("/a.csv"),
            pdf_dir_path=Path("/pdfs"),
            output_dir_path=Path("/out"),
            has_validation_errors=False,
            is_processing=False,
        )
        assert reasons == []

    def test_license_invalid(self):
        """Block when license invalid."""
        reasons = get_run_block_reasons(
            license_valid=False,
            input_file_path=Path("/a.csv"),
            pdf_dir_path=Path("/pdfs"),
            output_dir_path=Path("/out"),
            has_validation_errors=False,
            is_processing=False,
        )
        assert "License invalid" in reasons

    def test_missing_paths(self):
        """Block when any path is missing."""
        reasons = get_run_block_reasons(
            license_valid=True,
            input_file_path=None,
            pdf_dir_path=Path("/pdfs"),
            output_dir_path=Path("/out"),
            has_validation_errors=False,
            is_processing=False,
        )
        assert "Select input file" in reasons

    def test_validation_errors(self):
        """Block when has validation errors."""
        reasons = get_run_block_reasons(
            license_valid=True,
            input_file_path=Path("/a.csv"),
            pdf_dir_path=Path("/pdfs"),
            output_dir_path=Path("/out"),
            has_validation_errors=True,
            is_processing=False,
        )
        assert "Fix validation errors" in reasons

    def test_processing(self):
        """Block when merge in progress."""
        reasons = get_run_block_reasons(
            license_valid=True,
            input_file_path=Path("/a.csv"),
            pdf_dir_path=Path("/pdfs"),
            output_dir_path=Path("/out"),
            has_validation_errors=False,
            is_processing=True,
        )
        assert "Merge in progress" in reasons


class TestCanRunMerge:
    """Test cases for can_run_merge."""

    def test_true_when_all_ready(self):
        """True when no block reasons."""
        assert can_run_merge(
            license_valid=True,
            input_file_path=Path("/a.csv"),
            pdf_dir_path=Path("/pdfs"),
            output_dir_path=Path("/out"),
            has_validation_errors=False,
            is_processing=False,
        ) is True

    def test_false_when_license_invalid(self):
        """False when license invalid."""
        assert can_run_merge(
            license_valid=False,
            input_file_path=Path("/a.csv"),
            pdf_dir_path=Path("/pdfs"),
            output_dir_path=Path("/out"),
            has_validation_errors=False,
            is_processing=False,
        ) is False
