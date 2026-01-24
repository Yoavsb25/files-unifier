"""
Unit tests for data_parser module.
"""

import pytest
from pdf_merger.data_parser import split_serial_numbers
from pdf_merger.enums import SERIAL_NUMBER_SEPARATOR


class TestSplitSerialNumbers:
    """Test cases for split_serial_numbers function."""
    
    def test_parse_single_serial_number(self):
        """Test parsing a single serial number."""
        result = split_serial_numbers("GRNW_000103851")
        assert result == ["GRNW_000103851"]
    
    def test_parse_multiple_serial_numbers(self):
        """Test parsing multiple comma-separated serial numbers."""
        result = split_serial_numbers("GRNW_000103851,GRNW_000103852,GRNW_000103853")
        assert result == ["GRNW_000103851", "GRNW_000103852", "GRNW_000103853"]
    
    def test_parse_with_whitespace(self):
        """Test parsing serial numbers with whitespace."""
        result = split_serial_numbers("GRNW_000103851 , GRNW_000103852 , GRNW_000103853")
        assert result == ["GRNW_000103851", "GRNW_000103852", "GRNW_000103853"]
    
    def test_parse_empty_string(self):
        """Test parsing an empty string."""
        result = split_serial_numbers("")
        assert result == []
    
    def test_parse_whitespace_only(self):
        """Test parsing a string with only whitespace."""
        result = split_serial_numbers("   ")
        assert result == []
    
    def test_parse_with_empty_elements(self):
        """Test parsing with empty elements between commas."""
        result = split_serial_numbers("GRNW_000103851,,GRNW_000103852, ,GRNW_000103853")
        assert result == ["GRNW_000103851", "GRNW_000103852", "GRNW_000103853"]
    
    def test_parse_none_input(self):
        """Test parsing None input (should return empty list)."""
        result = split_serial_numbers(None)
        assert result == []
    
    def test_parse_lowercase_serial_numbers(self):
        """Test parsing lowercase serial numbers."""
        result = split_serial_numbers("grnw_000103851,grnw_000103852")
        assert result == ["grnw_000103851", "grnw_000103852"]
    
    def test_parse_mixed_case_serial_numbers(self):
        """Test parsing mixed case serial numbers."""
        result = split_serial_numbers("GRNW_000103851,grnw_000103852")
        assert result == ["GRNW_000103851", "grnw_000103852"]
