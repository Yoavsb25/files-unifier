"""
Validation module.
Handles validation of files, folders, and paths.
"""

from pathlib import Path
from typing import Tuple
from .file_reader import get_file_columns, detect_file_type


def validate_folder(folder_path: Path, folder_type: str = "Folder") -> bool:
    """
    Validate that a folder exists and is a directory.
    
    Args:
        folder_path: Path to validate
        folder_type: Type description for error messages (e.g., "Source", "Output")
        
    Returns:
        True if valid, False otherwise
    """
    if not folder_path.exists():
        print(f"Error: {folder_type} folder not found: {folder_path}")
        return False
    
    if not folder_path.is_dir():
        print(f"Error: {folder_path} is not a directory")
        return False
    
    return True


def validate_file(file_path: Path, required_column: str = 'serial_numbers') -> bool:
    """
    Validate that a data file exists and has the required column.
    
    Args:
        file_path: Path to the file to validate
        required_column: Name of the required column (default: 'serial_numbers')
        
    Returns:
        True if valid, False otherwise
    """
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        return False
    
    try:
        columns = get_file_columns(file_path)
        
        if required_column not in columns:
            print(f"Error: '{required_column}' column not found in file.")
            print(f"Available columns: {', '.join(columns)}")
            return False
    except Exception as e:
        print(f"Error reading file: {e}")
        return False
    
    return True


def validate_paths(file_path: Path, source_folder: Path, output_folder: Path, 
                   required_column: str = 'serial_numbers') -> Tuple[bool, str]:
    """
    Validate all paths needed for processing.
    
    Args:
        file_path: Path to the data file (CSV/Excel)
        source_folder: Path to folder containing PDF files
        output_folder: Path to output folder
        required_column: Name of the required column
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not validate_file(file_path, required_column):
        return False, "File validation failed"
    
    if not validate_folder(source_folder, "Source"):
        return False, "Source folder validation failed"
    
    # Output folder doesn't need to exist, we'll create it
    # But check if parent exists if output_folder is not root
    if output_folder.parent != output_folder:
        if not output_folder.parent.exists():
            print(f"Error: Parent directory of output folder does not exist: {output_folder.parent}")
            return False, "Output folder parent validation failed"
    
    return True, ""
