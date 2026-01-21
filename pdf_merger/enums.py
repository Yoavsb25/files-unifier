"""
Constants and enumerations for PDF Merger.
Centralized location for all configuration constants.
"""

# File Extensions
EXCEL_FILE_EXTENSIONS = ['.xlsx', '.xls']
CSV_FILE_EXTENSIONS = ['.csv']
PDF_FILE_EXTENSION = '.pdf'

# File Types
FILE_TYPE_EXCEL = 'excel'
FILE_TYPE_CSV = 'csv'

# Default Column Names
DEFAULT_REQUIRED_COLUMN = 'serial_numbers'

# CSV Configuration
DEFAULT_CSV_DELIMITER = ','
CSV_SAMPLE_SIZE = 1024  # Bytes to read for delimiter detection

# Output File Configuration
OUTPUT_FILENAME_PATTERN = 'merged_row_{}.pdf'

# Serial Number Configuration
SERIAL_NUMBER_PREFIX = 'GRNW_'
SERIAL_NUMBER_PREFIX_LOWER = 'grnw_'
SERIAL_NUMBER_SEPARATOR = ','  # Comma separator for multiple serial numbers
