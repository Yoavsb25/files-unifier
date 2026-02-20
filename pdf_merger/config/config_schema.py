"""
Configuration schema and validation.
Provides schema definitions and validation for application configuration.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any

from ..core.constants import Constants
from ..utils.logging_utils import get_logger

INPUT_FILE = 'input_file'
PDF_DIR = 'pdf_dir'
SOURCE_DIR = 'source_dir'
OUTPUT_DIR = 'output_dir'
REQUIRED_COLUMN = 'required_column'

logger = get_logger("config_schema")


@dataclass
class ConfigSchema:
    """Configuration schema with validation rules."""
    
    @staticmethod
    def validate_input_file(value: Optional[str]) -> Optional[str]:
        """
        Validate input file path.
        
        Args:
            value: Input file path string
            
        Returns:
            Validated path string or None
            
        Raises:
            ValueError: If path is invalid
        """
        if value is None or value == "":
            return None
        
        path = Path(value)
        if not path.exists():
            raise ValueError(f"Input file does not exist: {value}")
        
        if not path.is_file():
            raise ValueError(f"Input file is not a file: {value}")
        
        return str(path.resolve())
    
    @staticmethod
    def validate_source_dir(value: Optional[str]) -> Optional[str]:
        """
        Validate source directory path.
        
        Args:
            value: Source directory path string
            
        Returns:
            Validated path string or None
            
        Raises:
            ValueError: If path is invalid
        """
        if value is None or value == "":
            return None
        
        path = Path(value)
        if not path.exists():
            raise ValueError(f"Source directory does not exist: {value}")
        
        if not path.is_dir():
            raise ValueError(f"Source directory is not a directory: {value}")
        
        return str(path.resolve())
    
    @staticmethod
    def validate_output_dir(value: Optional[str]) -> Optional[str]:
        """
        Validate output directory path (will be created if it doesn't exist).
        
        Args:
            value: Output directory path string
            
        Returns:
            Validated path string or None
            
        Raises:
            ValueError: If path is invalid
        """
        if value is None or value == "":
            return None
        
        path = Path(value)
        # Output directory can be created, so we just validate the parent exists
        if path.exists() and not path.is_dir():
            raise ValueError(f"Output path exists but is not a directory: {value}")
        
        # Try to create parent if needed
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise ValueError(f"Cannot create output directory: {e}")
        
        return str(path.resolve())
    
    @staticmethod
    def validate_column(value: Optional[str]) -> str:
        """
        Validate column name.
        
        Args:
            value: Column name string
            
        Returns:
            Validated column name
            
        Raises:
            ValueError: If column name is invalid
        """
        if value is None or value == "":
            return Constants.DEFAULT_SERIAL_NUMBERS_COLUMN
        
        # Column names should be non-empty strings
        if not isinstance(value, str) or len(value.strip()) == 0:
            raise ValueError(f"Column name must be a non-empty string: {value}")
        
        return value.strip()
    
    @staticmethod
    def validate_config(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate entire configuration dictionary.
        
        Args:
            data: Configuration dictionary
            
        Returns:
            Validated configuration dictionary
            
        Raises:
            ValueError: If any configuration value is invalid
        """
        validated = {}
        
        # Validate input_file
        if INPUT_FILE in data:
            try:
                validated[INPUT_FILE] = ConfigSchema.validate_input_file(data[INPUT_FILE])
            except ValueError as e:
                logger.warning(f"Invalid {INPUT_FILE} in config: {e}")
                validated[INPUT_FILE] = None
        
        # Validate pdf_dir (source_dir)
        if PDF_DIR in data:
            try:
                validated[PDF_DIR] = ConfigSchema.validate_source_dir(data[PDF_DIR])
            except ValueError as e:
                logger.warning(f"Invalid {PDF_DIR} in config: {e}")
                validated[PDF_DIR] = None
        
        # Also handle source_dir alias
        if SOURCE_DIR in data and PDF_DIR not in validated:
            try:
                validated[PDF_DIR] = ConfigSchema.validate_source_dir(data[SOURCE_DIR])
            except ValueError as e:
                logger.warning(f"Invalid {SOURCE_DIR} in config: {e}")
                validated[PDF_DIR] = None
        
        # Validate output_dir
        if OUTPUT_DIR in data:
            try:
                validated[OUTPUT_DIR] = ConfigSchema.validate_output_dir(data[OUTPUT_DIR])
            except ValueError as e:
                logger.warning(f"Invalid {OUTPUT_DIR} in config: {e}")
                validated[OUTPUT_DIR] = None
        
        # Validate required_column
        if REQUIRED_COLUMN in data:
            try:
                validated[REQUIRED_COLUMN] = ConfigSchema.validate_column(data[REQUIRED_COLUMN])
            except ValueError as e:
                logger.warning(f"Invalid {REQUIRED_COLUMN} in config: {e}")
                validated[REQUIRED_COLUMN] = Constants.DEFAULT_SERIAL_NUMBERS_COLUMN
        else:
            validated[REQUIRED_COLUMN] = Constants.DEFAULT_SERIAL_NUMBERS_COLUMN
        
        return validated
