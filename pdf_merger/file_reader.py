"""
File reader module.
Handles reading CSV and Excel files with a unified interface.
"""

import csv
import sys
from pathlib import Path
from typing import Iterator, Dict, Any

try:
    import pandas as pd
except ImportError:
    pd = None


def detect_file_type(file_path: Path) -> str:
    """
    Detect if a file is CSV or Excel based on its extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        'excel' for .xlsx/.xls files, 'csv' for other files
    """
    if file_path.suffix.lower() in ['.xlsx', '.xls']:
        return 'excel'
    return 'csv'


def read_csv(file_path: Path) -> Iterator[Dict[str, Any]]:
    """
    Read a CSV file and yield rows as dictionaries.
    
    Args:
        file_path: Path to the CSV file
        
    Yields:
        Dictionary representing each row
    """
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        # Try to detect delimiter
        sample = csvfile.read(1024)
        csvfile.seek(0)
        sniffer = csv.Sniffer()
        delimiter = sniffer.sniff(sample).delimiter
        
        reader = csv.DictReader(csvfile, delimiter=delimiter)
        
        for row in reader:
            yield row


def read_excel(file_path: Path) -> Iterator[Dict[str, Any]]:
    """
    Read an Excel file and yield rows as dictionaries.
    
    Args:
        file_path: Path to the Excel file
        
    Yields:
        Dictionary representing each row
        
    Raises:
        ImportError: If pandas/openpyxl are not installed
    """
    if pd is None:
        raise ImportError("pandas and openpyxl are required to read Excel files. Install with: pip install pandas openpyxl")
    
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
    
    if file_type == 'excel':
        yield from read_excel(file_path)
    else:
        yield from read_csv(file_path)


def get_file_columns(file_path: Path) -> list:
    """
    Get the column names from a data file.
    
    Args:
        file_path: Path to the CSV or Excel file
        
    Returns:
        List of column names
        
    Raises:
        ImportError: If required libraries are not installed for Excel files
    """
    file_type = detect_file_type(file_path)
    
    if file_type == 'excel':
        if pd is None:
            raise ImportError("pandas and openpyxl are required to read Excel files. Install with: pip install pandas openpyxl")
        df = pd.read_excel(file_path)
        return list(df.columns)
    else:
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            sample = csvfile.read(1024)
            csvfile.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            reader = csv.DictReader(csvfile, delimiter=delimiter)
            return list(reader.fieldnames) if reader.fieldnames else []
