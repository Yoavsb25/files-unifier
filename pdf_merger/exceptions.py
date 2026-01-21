"""
Custom exceptions for PDF Merger.
Provides specific exception types for different error conditions.
"""


class PDFMergerError(Exception):
    """Base exception for all PDF Merger errors."""
    pass


class FileNotFoundError(PDFMergerError):
    """Raised when a required file or folder is not found."""
    pass


class InvalidFileFormatError(PDFMergerError):
    """Raised when file format is unsupported or invalid."""
    pass


class MissingColumnError(PDFMergerError):
    """Raised when required column is missing from data file."""
    
    def __init__(self, column_name: str, available_columns: list):
        """
        Initialize MissingColumnError.
        
        Args:
            column_name: Name of the missing column
            available_columns: List of available columns
        """
        self.column_name = column_name
        self.available_columns = available_columns
        message = f"Required column '{column_name}' not found. Available columns: {', '.join(available_columns)}"
        super().__init__(message)


class PDFProcessingError(PDFMergerError):
    """Raised when PDF operations fail (reading, merging)."""
    pass


class ValidationError(PDFMergerError):
    """Raised for general validation failures."""
    pass
