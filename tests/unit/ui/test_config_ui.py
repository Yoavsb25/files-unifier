"""
Unit tests for config_ui module.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock

from pdf_merger.ui.config_ui import apply_config_to_ui


class TestApplyConfigToUi:
    """Test cases for apply_config_to_ui."""

    def test_sets_column_and_applies_valid_paths(self):
        """Column entry gets required_column; valid paths are applied and on_update_state called."""
        config = MagicMock()
        config.required_column = "serial_numbers"
        config.input_file = "/path/to/input.csv"
        config.pdf_dir = "/path/to/source"
        config.output_dir = None  # skip this one

        column_entry = MagicMock()
        selector = MagicMock()
        set_path_attr = MagicMock()
        log_info = MagicMock()
        log_warning = MagicMock()
        on_update_state = MagicMock()

        def validator(p: Path) -> None:
            pass

        apply_config_to_ui(
            config,
            column_entry=column_entry,
            path_applyments=[
                (config.input_file, "input_file_path", selector, validator, "input file"),
                (config.pdf_dir, "pdf_dir_path", selector, validator, "source directory"),
                (config.output_dir, "output_dir_path", selector, validator, "output directory"),
            ],
            set_path_attr=set_path_attr,
            log_info=log_info,
            log_warning=log_warning,
            on_update_state=on_update_state,
        )

        column_entry.insert.assert_called_once_with(0, "serial_numbers")
        assert set_path_attr.call_count == 2
        set_path_attr.assert_any_call("input_file_path", Path("/path/to/input.csv"))
        set_path_attr.assert_any_call("pdf_dir_path", Path("/path/to/source"))
        assert selector.set_path.call_count == 2
        on_update_state.assert_called_once()

    def test_skips_none_path_str(self):
        """Path applyments with path_str None are skipped."""
        config = MagicMock()
        config.required_column = "col"
        column_entry = MagicMock()
        set_path_attr = MagicMock()
        apply_config_to_ui(
            config,
            column_entry=column_entry,
            path_applyments=[
                (None, "input_file_path", MagicMock(), lambda p: None, "input file"),
            ],
            set_path_attr=set_path_attr,
            log_info=MagicMock(),
            log_warning=MagicMock(),
            on_update_state=MagicMock(),
        )
        set_path_attr.assert_not_called()

    def test_on_validation_error_logs_warning_and_continues(self):
        """When validator raises, log warning and continue; on_update_state still called."""
        config = MagicMock()
        config.required_column = "col"
        config.input_file = "/bad/path.csv"
        column_entry = MagicMock()
        selector = MagicMock()
        log_warning = MagicMock()
        on_update_state = MagicMock()

        def failing_validator(p: Path) -> None:
            raise ValueError("not found")

        apply_config_to_ui(
            config,
            column_entry=column_entry,
            path_applyments=[
                (config.input_file, "input_file_path", selector, failing_validator, "input file"),
            ],
            set_path_attr=MagicMock(),
            log_info=MagicMock(),
            log_warning=log_warning,
            on_update_state=on_update_state,
        )
        log_warning.assert_called_once()
        assert "Could not load" in log_warning.call_args[0][0]
        on_update_state.assert_called_once()
