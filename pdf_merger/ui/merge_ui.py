"""
Merge lifecycle UI: start, complete, error.
Receives a minimal state (widgets + callbacks); no dependency on app class.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional

from .theme import PROCESSING_BUTTON_TEXT, RUN_MERGE_BUTTON_TEXT, SECTION_SPACING

# MergeResult type for type hints; avoid circular import
MergeResult = Any


@dataclass
class MergeUIState:
    """Minimal state for merge start/complete/error UI. Passed by app; merge_ui does not import app."""

    run_button: Any
    progress_bar: Any
    results_frame: Any
    log_area: Any
    apply_result_fn: Callable[[MergeResult], None]
    update_ui_state_fn: Callable[[], None]
    log_info_fn: Callable[[str], None]
    log_error_fn: Callable[[str], None]
    log_plain_fn: Callable[[str], None]


def _reset_merge_ui_state(state: MergeUIState) -> None:
    """Reset run button and progress bar after merge completes or errors."""
    state.run_button.configure(state="normal", text=RUN_MERGE_BUTTON_TEXT)
    state.progress_bar.stop()
    state.progress_bar.pack_forget()


def on_merge_start(
    state: MergeUIState,
    input_file_path: Optional[Path],
    pdf_dir_path: Optional[Path],
    output_dir_path: Optional[Path],
) -> None:
    """Disable run button, show progress bar, hide results, clear log, log start messages."""
    state.run_button.configure(state="disabled", text=PROCESSING_BUTTON_TEXT)
    state.progress_bar.pack(fill="x", pady=(0, SECTION_SPACING), before=state.log_area)
    state.progress_bar.start()
    state.results_frame.hide()
    state.log_area.clear()
    state.log_info_fn("Starting merge operation...")
    state.log_info_fn(f"Input file: {input_file_path}")
    state.log_info_fn(f"Source directory: {pdf_dir_path}")
    state.log_info_fn(f"Output directory: {output_dir_path}")
    state.log_plain_fn("")


def on_merge_complete(state: MergeUIState, result: MergeResult) -> None:
    """Reset button and progress bar, apply result to UI, then update run button state."""
    _reset_merge_ui_state(state)
    state.apply_result_fn(result)
    state.update_ui_state_fn()


def on_merge_error(state: MergeUIState, message: str) -> None:
    """Reset button and progress bar, log error, then update run button state."""
    _reset_merge_ui_state(state)
    state.log_plain_fn("")
    state.log_error_fn(message)
    state.update_ui_state_fn()
