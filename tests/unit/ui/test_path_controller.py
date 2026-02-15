"""
Unit tests for PathController.
"""

from pathlib import Path
from unittest.mock import MagicMock

from pdf_merger.ui.path_controller import PathController


def test_apply_path_calls_all_deps_in_order():
    """PathController.apply_path calls set_config, selector, save_config, log_info, update_ui_state in order."""
    path = Path("/some/input.csv")
    path_attr = "input_file_path"
    config_override = {"input_file": "/some/input.csv"}
    log_message = "Selected input file: input.csv"

    get_config = MagicMock()
    merged_config = MagicMock()
    get_config.return_value.merge.return_value = merged_config

    set_config = MagicMock()
    save_config_fn = MagicMock()
    log_info_fn = MagicMock()
    update_ui_state_fn = MagicMock()

    selector = MagicMock()

    controller = PathController(
        get_config=get_config,
        set_config=set_config,
        save_config_fn=save_config_fn,
        log_info_fn=log_info_fn,
        update_ui_state_fn=update_ui_state_fn,
    )
    controller.apply_path(path, path_attr, selector, config_override, log_message)

    get_config.assert_called_once()
    set_config.assert_called_once_with(path_attr, path, merged_config)
    selector.set_path.assert_called_once_with(str(path))
    selector.clear_error.assert_called_once()
    save_config_fn.assert_called_once_with(merged_config)
    log_info_fn.assert_called_once_with(log_message)
    update_ui_state_fn.assert_called_once()
