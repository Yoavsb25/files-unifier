"""
Modal and auxiliary dialogs for the PDF Merger UI.
Centralizes dialog layout and sizing so app.py stays thin and theme constants are used consistently.
"""

from typing import Callable, Optional

import customtkinter as ctk

from ..models import MergeResult
from .theme import (
    DETAILED_REPORT_DIALOG_GEOMETRY,
    DETAILED_REPORT_DIALOG_MIN_SIZE,
    DETAILED_REPORT_DIALOG_TITLE,
    DETAILED_REPORT_CLOSE_BUTTON_TEXT,
)


def show_detailed_report_dialog(
    parent: ctk.CTk,
    result: MergeResult,
    format_fn: Optional[Callable[[MergeResult], str]] = None,
) -> None:
    """
    Open a toplevel dialog showing the detailed processing report for a merge result.

    Args:
        parent: Parent window (e.g. main app).
        result: MergeResult to format and display.
        format_fn: Function that takes MergeResult and returns report text. Defaults to format_result_detailed from core.
    """
    if format_fn is None:
        from ..core import format_result_detailed
        format_fn = format_result_detailed
    report_text = format_fn(result)
    dialog = ctk.CTkToplevel(parent)
    dialog.title(DETAILED_REPORT_DIALOG_TITLE)
    dialog.geometry(DETAILED_REPORT_DIALOG_GEOMETRY)
    dialog.minsize(*DETAILED_REPORT_DIALOG_MIN_SIZE)
    text = ctk.CTkTextbox(dialog, font=ctk.CTkFont(family="Courier New", size=12), wrap="word")
    text.pack(fill="both", expand=True, padx=10, pady=10)
    text.insert("1.0", report_text)
    text.configure(state="disabled")
    close_btn = ctk.CTkButton(dialog, text=DETAILED_REPORT_CLOSE_BUTTON_TEXT, command=dialog.destroy)
    close_btn.pack(pady=(0, 10))
