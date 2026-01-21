"""
File reader module.
Handles reading CSV and Excel files with a unified interface.
"""

import csv
import pandas as pd
from pathlib import Path
from typing import Iterator, Dict, Any, List
from .exceptions import InvalidFileFormatError, MissingColumnError
from .enums import (
    EXCEL_FILE_EXTENSIONS,
    CSV_FILE_EXTENSIONS,
    FILE_TYPE_EXCEL,
    FILE_TYPE_CSV,
    DEFAULT_CSV_DELIMITER,
    CSV_SAMPLE_SIZE,
)

def detect_file_type(file_path: Path) -> str:
    """
    Detect if a file is CSV or Excel based on its extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        'excel' for .xlsx/.xls files, 'csv' for other files
    """
    if file_path.suffix.lower() in EXCEL_FILE_EXTENSIONS:
        return FILE_TYPE_EXCEL
    return FILE_TYPE_CSV


def _detect_csv_delimiter(file_path: Path) -> str:
    """
    Detect CSV delimiter from file sample.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        Detected delimiter character
        
    Raises:
        ValueError: If file is empty or delimiter cannot be detected
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            sample = csvfile.read(CSV_SAMPLE_SIZE)
            if not sample.strip():
                # Default to comma if file is empty
                return DEFAULT_CSV_DELIMITER
            csvfile.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            return delimiter
    except Exception as e:
        # Default to comma if detection fails
        return DEFAULT_CSV_DELIMITER


def read_csv(file_path: Path) -> Iterator[Dict[str, Any]]:
    """
    Read a CSV file and yield rows as dictionaries.
    
    Args:
        file_path: Path to the CSV file
        
    Yields:
        Dictionary representing each row
        
    Raises:
        InvalidFileFormatError: If file cannot be read
    """
    try:
        delimiter = _detect_csv_delimiter(file_path)
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=delimiter)
            
            for row in reader:
                yield row
    except Exception as e:
        raise InvalidFileFormatError(f"Failed to read CSV file {file_path}: {e}") from e


def read_excel(file_path: Path) -> Iterator[Dict[str, Any]]:
    """
    Read an Excel file and yield rows as dictionaries.
    
    Args:
        file_path: Path to the Excel file
        
    Yields:
        Dictionary representing each row
        
    Raises:
        ImportError: If pandas/openpyxl are not installed
        InvalidFileFormatError: If file cannot be read
    """    
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        raise InvalidFileFormatError(f"Failed to read Excel file {file_path}: {e}") from e
    
    df = pd.read_excel(file_path)
    
    for _, row in df.iterrows():
        # Convert row to dictionary, handling NaN values
        row_dict = {}
        for key, value in row.items():
            if pd.notna(value):
                row_dict[key] = str(value)
            else:
                row_dict[key] = ''
        yield row_dict


def read_data_file(file_path: Path) -> Iterator[Dict[str, Any]]:
    """
    Read a data file (CSV or Excel) with a unified interface.
    
    Args:
        file_path: Path to the CSV or Excel file
        
    Yields:
        Dictionary representing each row
        
    Raises:
        ValueError: If file type is not supported
        ImportError: If required libraries are not installed for Excel files
    """
    file_type = detect_file_type(file_path)
    
    if file_type == FILE_TYPE_EXCEL:
        yield from read_excel(file_path)
    else:
        yield from read_csv(file_path)


def get_file_columns(file_path: Path) -> List[str]:
    """
    Get the column names from a data file.
    
    Args:
        file_path: Path to the CSV or Excel file
        
    Returns:
        List of column names
        
    Raises:
        ImportError: If required libraries are not installed for Excel files
        InvalidFileFormatError: If file cannot be read
    """
    file_type = detect_file_type(file_path)
    
    try:
        if file_type == FILE_TYPE_EXCEL:
            if pd is None:
                raise ImportError("pandas and openpyxl are required to read Excel files. Install with: pip install pandas openpyxl")
            df = pd.read_excel(file_path)
            return list(df.columns)
        else:
            delimiter = _detect_csv_delimiter(file_path)
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                return list(reader.fieldnames) if reader.fieldnames else []
    except ImportError:
        raise
    except Exception as e:
        raise InvalidFileFormatError(f"Failed to read file {file_path}: {e}") from e
