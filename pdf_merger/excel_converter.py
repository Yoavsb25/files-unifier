"""
Excel converter module.
Handles converting Excel files to PDF format.
"""

import tempfile
from pathlib import Path
from typing import Optional

from .logger import get_logger
from .enums import EXCEL_FILE_EXTENSIONS

logger = get_logger("excel_converter")

# Lazy import of xlsx2pdf library
_xlsx2pdf = None


def _get_xlsx2pdf():
    """
    Lazy import of xlsx2pdf library.
    Raises ImportError if xlsx2pdf is not available.
    """
    global _xlsx2pdf
    
    if _xlsx2pdf is None:
        try:
            import xlsx2pdf
            _xlsx2pdf = xlsx2pdf
        except ImportError:
            raise ImportError(
                "xlsx2pdf library is required for Excel file conversion. "
                "Install with: pip install xlsx2pdf"
            )
    
    return _xlsx2pdf


def convert_excel_to_pdf(excel_path: Path, output_path: Path) -> bool:
    """
    Convert an Excel file to PDF format.
    
    Args:
        excel_path: Path to the Excel file (.xlsx or .xls)
        output_path: Path where the PDF will be saved
        
    Returns:
        True if successful, False otherwise
        
    Raises:
        ImportError: If xlsx2pdf is not installed
    """
    if not excel_path.exists():
        logger.error(f"Excel file not found: {excel_path}")
        return False
    
    if excel_path.suffix.lower() not in EXCEL_FILE_EXTENSIONS:
        logger.error(f"File is not an Excel file: {excel_path}")
        return False
    
    try:
        xlsx2pdf = _get_xlsx2pdf()
        
        # Convert Excel to PDF
        xlsx2pdf.convert(str(excel_path), str(output_path))
        
        # Verify the output file was created
        if not output_path.exists():
            logger.error(f"PDF conversion failed: output file not created at {output_path}")
            return False
        
        logger.info(f"Successfully converted {excel_path.name} to PDF")
        return True
        
    except ImportError as e:
        logger.error(str(e))
        return False
    except Exception as e:
        logger.error(f"Error converting Excel file {excel_path.name} to PDF: {e}")
        return False
