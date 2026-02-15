"""CSV and column configuration constants for PDF Merger.
DEFAULT_SERIAL_NUMBERS_COLUMN must match pdf_merger.models.defaults.DEFAULT_SERIAL_NUMBERS_COLUMN (core cannot import models here to avoid circular import).
CSV/encoding constants are re-exported from utils.csv_constants (single source). Serial number format constants live in utils.serial_number_parser."""

from ..utils.csv_constants import CSV_SAMPLE_SIZE, DEFAULT_CSV_DELIMITER, UTF_8_ENCODING


class CsvSerialConstants:
    """Column names and CSV parsing (encoding/delimiter/sample size from utils.csv_constants)."""

    DEFAULT_SERIAL_NUMBERS_COLUMN = "serial_numbers"
    DEFAULT_CSV_DELIMITER = DEFAULT_CSV_DELIMITER
    CSV_SAMPLE_SIZE = CSV_SAMPLE_SIZE
    UTF_8_ENCODING = UTF_8_ENCODING
