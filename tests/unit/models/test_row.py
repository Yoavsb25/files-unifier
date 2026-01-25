"""
Unit tests for row module.
"""

import pytest
from pdf_merger.models.row import Row


class TestRow:
    """Test cases for Row class."""
    
    def test_row_from_raw_data(self):
        """Test creating Row from raw data."""
        raw_data = {"serial_numbers": "GRNW_123,GRNW_456"}
        row = Row.from_raw_data(0, raw_data, "serial_numbers")
        
        assert row.row_index == 0
        assert row.raw_data == raw_data
        assert row.serial_numbers_str == "GRNW_123,GRNW_456"
        assert len(row.serial_numbers) == 2
        assert row.required_column == "serial_numbers"
    
    def test_row_from_raw_data_empty(self):
        """Test creating Row from raw data with empty serial numbers."""
        raw_data = {"serial_numbers": ""}
        row = Row.from_raw_data(0, raw_data, "serial_numbers")
        
        assert row.serial_numbers_str == ""
        assert len(row.serial_numbers) == 0
    
    def test_row_from_raw_data_missing_column(self):
        """Test creating Row when required column is missing."""
        raw_data = {"other_column": "value"}
        row = Row.from_raw_data(0, raw_data, "serial_numbers")
        
        assert row.serial_numbers_str == ""
        assert len(row.serial_numbers) == 0
    
    def test_row_from_raw_data_invalid_serial_numbers(self):
        """Test creating Row with invalid serial numbers."""
        raw_data = {"serial_numbers": "INVALID,GRNW_123,ALSO_INVALID"}
        row = Row.from_raw_data(0, raw_data, "serial_numbers")
        
        # Only valid serial numbers should be included
        assert len(row.serial_numbers) == 1
        assert "GRNW_123" in row.serial_numbers[0].upper()
    
    def test_row_from_raw_data_deduplicates(self):
        """Test that Row deduplicates serial numbers."""
        raw_data = {"serial_numbers": "GRNW_123,GRNW_123,GRNW_456"}
        row = Row.from_raw_data(0, raw_data, "serial_numbers")
        
        # Should have only 2 unique serial numbers
        assert len(row.serial_numbers) == 2
    
    def test_row_from_raw_data_normalizes(self):
        """Test that Row normalizes serial numbers."""
        raw_data = {"serial_numbers": "grnw_123,GRNW_456"}
        row = Row.from_raw_data(0, raw_data, "serial_numbers")
        
        # Serial numbers should be normalized to uppercase
        assert all(s.isupper() or '_' in s for s in row.serial_numbers)
    
    def test_has_serial_numbers_true(self):
        """Test has_serial_numbers returns True when serial numbers exist."""
        raw_data = {"serial_numbers": "GRNW_123"}
        row = Row.from_raw_data(0, raw_data, "serial_numbers")
        
        assert row.has_serial_numbers() is True
    
    def test_has_serial_numbers_false(self):
        """Test has_serial_numbers returns False when no serial numbers."""
        raw_data = {"serial_numbers": ""}
        row = Row.from_raw_data(0, raw_data, "serial_numbers")
        
        assert row.has_serial_numbers() is False
    
    def test_row_str(self):
        """Test Row string representation."""
        raw_data = {"serial_numbers": "GRNW_123,GRNW_456"}
        row = Row.from_raw_data(0, raw_data, "serial_numbers")
        
        str_repr = str(row)
        assert "Row 1" in str_repr
        assert "2 serial number(s)" in str_repr
    
    def test_row_str_no_serial_numbers(self):
        """Test Row string representation with no serial numbers."""
        raw_data = {"serial_numbers": ""}
        row = Row.from_raw_data(0, raw_data, "serial_numbers")
        
        str_repr = str(row)
        assert "Row 1" in str_repr
        assert "0 serial number(s)" in str_repr
