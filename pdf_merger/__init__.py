"""
PDF Merger Package
A modular package for merging PDFs based on serial numbers from CSV/Excel files.
"""

__version__ = '1.0.0'

# Import main functions for easy access
from .processor import process_file, ProcessingResult, process_row
from .pdf_operations import find_pdf_file, merge_pdfs
from .data_parser import parse_serial_numbers
from .file_reader import read_data_file, get_file_columns
from .validators import validate_file, validate_folder, validate_paths

__all__ = [
    'process_file',
    'process_row',
    'ProcessingResult',
    'find_pdf_file',
    'merge_pdfs',
    'parse_serial_numbers',
    'read_data_file',
    'get_file_columns',
    'validate_file',
    'validate_folder',
    'validate_paths',
]
