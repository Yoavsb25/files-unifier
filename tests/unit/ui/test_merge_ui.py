"""
Unit tests for merge_ui module.
"""

from pathlib import Path
from unittest.mock import MagicMock

from pdf_merger.ui.merge_ui import MergeUIState, on_merge_complete, on_merge_error, on_merge_start


def test_on_merge_start_calls_widgets_and_log():
    """on_merge_start disables button, packs progress bar, hides results, clears log, logs messages."""
    state = MergeUIState(
        run_button=MagicMock(),
        progress_bar=MagicMock(),
        results_frame=MagicMock(),
        log_area=MagicMock(),
        apply_result_fn=MagicMock(),
        update_ui_state_fn=MagicMock(),
        log_info_fn=MagicMock(),
        log_error_fn=MagicMock(),
        log_plain_fn=MagicMock(),
    )
    on_merge_start(
        state,
        input_file_path=Path("/in.csv"),
        pdf_dir_path=Path("/pdf"),
        output_dir_path=Path("/out"),
    )
    state.run_button.configure.assert_called_once()
    assert state.run_button.configure.call_args[1]["state"] == "disabled"
    state.progress_bar.pack.assert_called_once()
    state.progress_bar.start.assert_called_once()
    state.results_frame.hide.assert_called_once()
    state.log_area.clear.assert_called_once()
    assert state.log_info_fn.call_count >= 4
    state.log_plain_fn.assert_called_once_with("")


def test_on_merge_complete_resets_then_applies_result_then_updates():
    """on_merge_complete resets UI state, calls apply_result_fn, then update_ui_state_fn."""
    state = MergeUIState(
        run_button=MagicMock(),
        progress_bar=MagicMock(),
        results_frame=MagicMock(),
        log_area=MagicMock(),
        apply_result_fn=MagicMock(),
        update_ui_state_fn=MagicMock(),
        log_info_fn=MagicMock(),
        log_error_fn=MagicMock(),
        log_plain_fn=MagicMock(),
    )
    result = MagicMock()
    on_merge_complete(state, result)
    state.run_button.configure.assert_called_once_with(state="normal", text="Run Merge")
    state.progress_bar.stop.assert_called_once()
    state.progress_bar.pack_forget.assert_called_once()
    state.apply_result_fn.assert_called_once_with(result)
    state.update_ui_state_fn.assert_called_once()


def test_on_merge_error_resets_then_logs_then_updates():
    """on_merge_error resets UI state, logs error, then update_ui_state_fn."""
    state = MergeUIState(
        run_button=MagicMock(),
        progress_bar=MagicMock(),
        results_frame=MagicMock(),
        log_area=MagicMock(),
        apply_result_fn=MagicMock(),
        update_ui_state_fn=MagicMock(),
        log_info_fn=MagicMock(),
        log_error_fn=MagicMock(),
        log_plain_fn=MagicMock(),
    )
    on_merge_error(state, "Something failed")
    state.run_button.configure.assert_called_once()
    state.progress_bar.pack_forget.assert_called_once()
    state.log_plain_fn.assert_called_once_with("")
    state.log_error_fn.assert_called_once_with("Something failed")
    state.update_ui_state_fn.assert_called_once()
