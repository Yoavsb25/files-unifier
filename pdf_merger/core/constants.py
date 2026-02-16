"""
Constants for PDF Merger.
Composes domain-specific constant classes; import Constants from here.
"""

from .csv_serial_constants import CsvSerialConstants
from .excel_constants import ExcelConstants
from .file_constants import FileConstants
from .license_constants import LicenseConstants
from .pdf_operations_constants import PdfOperationsConstants
from .pipeline_constants import PipelineConstants
from .ui_constants import UiConstants


class Constants(
    FileConstants,
    CsvSerialConstants,
    LicenseConstants,
    PdfOperationsConstants,
    ExcelConstants,
    UiConstants,
    PipelineConstants,
):
    """Configuration constants for PDF Merger (composed from domain modules)."""

    pass
