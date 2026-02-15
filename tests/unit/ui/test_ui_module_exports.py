"""
Unit tests for UI module exports.
"""

import importlib
import sys
from unittest.mock import MagicMock, patch


def test_ui_exports():
    """Test that UI module exports expected functions."""
    with patch.dict(
        sys.modules,
        {
            "tkinter": MagicMock(),
            "tkinter.filedialog": MagicMock(),
            "customtkinter": MagicMock(),
        },
    ):
        ui_module = importlib.import_module("pdf_merger.ui")
        ui_module = importlib.reload(ui_module)
        assert callable(ui_module.run_gui)
