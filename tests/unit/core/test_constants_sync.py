"""
Unit tests for constants sync between models.defaults and core.constants.
Ensures DEFAULT_SERIAL_NUMBERS_COLUMN stays in sync (canonical source is models.defaults).
"""

from pdf_merger.core.constants import Constants
from pdf_merger.models.defaults import DEFAULT_SERIAL_NUMBERS_COLUMN


def test_default_serial_numbers_column_in_sync():
    """Core.Constants must match models.defaults (canonical source)."""
    assert Constants.DEFAULT_SERIAL_NUMBERS_COLUMN == DEFAULT_SERIAL_NUMBERS_COLUMN
