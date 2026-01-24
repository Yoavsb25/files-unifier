"""
Unit tests for data_parser module.
"""

import pytest
from pdf_merger.data_parser import (
    split_serial_numbers,
    normalize_serial_number,
    extract_numeric_suffix,
    join_serial_numbers,
    deduplicate_serial_numbers,
    filter_valid_serial_numbers
)
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


class TestNormalizeSerialNumber:
    """Test cases for normalize_serial_number function."""
    
    def test_normalize_lowercase_to_uppercase(self):
        """Test normalizing lowercase prefix to uppercase."""
        result = normalize_serial_number("grnw_000103851", to_uppercase=True)
        assert result == "GRNW_000103851"
    
    def test_normalize_uppercase_stays_uppercase(self):
        """Test that uppercase prefix remains uppercase."""
        result = normalize_serial_number("GRNW_000103851", to_uppercase=True)
        assert result == "GRNW_000103851"
    
    def test_normalize_uppercase_to_lowercase(self):
        """Test normalizing uppercase prefix to lowercase."""
        result = normalize_serial_number("GRNW_000103851", to_uppercase=False)
        assert result == "grnw_000103851"
    
    def test_normalize_lowercase_stays_lowercase(self):
        """Test that lowercase prefix remains lowercase."""
        result = normalize_serial_number("grnw_000103851", to_uppercase=False)
        assert result == "grnw_000103851"
    
    def test_normalize_preserves_suffix(self):
        """Test that numeric suffix is preserved unchanged."""
        result = normalize_serial_number("grnw_000103851", to_uppercase=True)
        assert result == "GRNW_000103851"
        assert result.endswith("000103851")
    
    def test_normalize_with_whitespace(self):
        """Test normalizing serial number with whitespace."""
        result = normalize_serial_number("  grnw_000103851  ", to_uppercase=True)
        assert result == "GRNW_000103851"
    
    def test_normalize_empty_string(self):
        """Test normalizing empty string."""
        result = normalize_serial_number("", to_uppercase=True)
        assert result == ""
    
    def test_normalize_none(self):
        """Test normalizing None input."""
        result = normalize_serial_number(None, to_uppercase=True)
        assert result is None


class TestExtractNumericSuffix:
    """Test cases for extract_numeric_suffix function."""
    
    def test_extract_suffix_uppercase(self):
        """Test extracting numeric suffix from uppercase serial number."""
        result = extract_numeric_suffix("GRNW_000103851")
        assert result == "000103851"
    
    def test_extract_suffix_lowercase(self):
        """Test extracting numeric suffix from lowercase serial number."""
        result = extract_numeric_suffix("grnw_000103851")
        assert result == "000103851"
    
    def test_extract_suffix_no_underscore(self):
        """Test extracting suffix from serial number without underscore."""
        result = extract_numeric_suffix("GRNW000103851")
        assert result is None
    
    def test_extract_suffix_empty_string(self):
        """Test extracting suffix from empty string."""
        result = extract_numeric_suffix("")
        assert result is None
    
    def test_extract_suffix_none(self):
        """Test extracting suffix from None input."""
        result = extract_numeric_suffix(None)
        assert result is None
    
    def test_extract_suffix_multiple_underscores(self):
        """Test extracting suffix when multiple underscores exist."""
        result = extract_numeric_suffix("GRNW_000_103_851")
        assert result == "000_103_851"


class TestJoinSerialNumbers:
    """Test cases for join_serial_numbers function."""
    
    def test_join_single_serial_number(self):
        """Test joining a single serial number."""
        result = join_serial_numbers(["GRNW_000103851"])
        assert result == "GRNW_000103851"
    
    def test_join_multiple_serial_numbers(self):
        """Test joining multiple serial numbers."""
        result = join_serial_numbers(["GRNW_000103851", "GRNW_000103852", "GRNW_000103853"])
        assert result == "GRNW_000103851,GRNW_000103852,GRNW_000103853"
    
    def test_join_with_custom_separator(self):
        """Test joining with custom separator."""
        result = join_serial_numbers(["GRNW_000103851", "GRNW_000103852"], separator=";")
        assert result == "GRNW_000103851;GRNW_000103852"
    
    def test_join_with_whitespace(self):
        """Test joining serial numbers with whitespace."""
        result = join_serial_numbers(["  GRNW_000103851  ", "  GRNW_000103852  "])
        assert result == "GRNW_000103851,GRNW_000103852"
    
    def test_join_empty_list(self):
        """Test joining empty list."""
        result = join_serial_numbers([])
        assert result == ""
    
    def test_join_filters_empty_strings(self):
        """Test that empty strings are filtered out."""
        result = join_serial_numbers(["GRNW_000103851", "", "GRNW_000103852", "  "])
        assert result == "GRNW_000103851,GRNW_000103852"


class TestDeduplicateSerialNumbers:
    """Test cases for deduplicate_serial_numbers function."""
    
    def test_deduplicate_preserve_order(self):
        """Test deduplication preserving order."""
        result = deduplicate_serial_numbers(
            ["GRNW_000103851", "GRNW_000103852", "GRNW_000103851", "GRNW_000103853"],
            preserve_order=True
        )
        assert result == ["GRNW_000103851", "GRNW_000103852", "GRNW_000103853"]
    
    def test_deduplicate_no_preserve_order(self):
        """Test deduplication without preserving order."""
        result = deduplicate_serial_numbers(
            ["GRNW_000103851", "GRNW_000103852", "GRNW_000103851"],
            preserve_order=False
        )
        assert len(result) == 2
        assert "GRNW_000103851" in result
        assert "GRNW_000103852" in result
    
    def test_deduplicate_no_duplicates(self):
        """Test deduplication with no duplicates."""
        result = deduplicate_serial_numbers(
            ["GRNW_000103851", "GRNW_000103852", "GRNW_000103853"],
            preserve_order=True
        )
        assert result == ["GRNW_000103851", "GRNW_000103852", "GRNW_000103853"]
    
    def test_deduplicate_empty_list(self):
        """Test deduplication of empty list."""
        result = deduplicate_serial_numbers([], preserve_order=True)
        assert result == []
    
    def test_deduplicate_filters_none(self):
        """Test that None values are filtered out."""
        result = deduplicate_serial_numbers(
            ["GRNW_000103851", None, "GRNW_000103852", None],
            preserve_order=True
        )
        assert result == ["GRNW_000103851", "GRNW_000103852"]


class TestFilterValidSerialNumbers:
    """Test cases for filter_valid_serial_numbers function."""
    
    def test_filter_valid_only(self):
        """Test filtering with only valid serial numbers."""
        result = filter_valid_serial_numbers("GRNW_000103851,grnw_000103852,GRNW_000103853")
        assert result == ["GRNW_000103851", "grnw_000103852", "GRNW_000103853"]
    
    def test_filter_invalid_only(self):
        """Test filtering with only invalid serial numbers."""
        result = filter_valid_serial_numbers("INVALID_123,WRONG_456")
        assert result == []
    
    def test_filter_mixed_valid_invalid(self):
        """Test filtering with mix of valid and invalid serial numbers."""
        result = filter_valid_serial_numbers("GRNW_000103851,INVALID_123,grnw_000103852")
        assert result == ["GRNW_000103851", "grnw_000103852"]
        assert "INVALID_123" not in result
    
    def test_filter_empty_string(self):
        """Test filtering empty string."""
        result = filter_valid_serial_numbers("")
        assert result == []
    
    def test_filter_with_custom_validator(self):
        """Test filtering with custom validator function."""
        def custom_validator(serial: str) -> bool:
            return serial.startswith("GRNW_")
        
        result = filter_valid_serial_numbers(
            "GRNW_000103851,grnw_000103852,GRNW_000103853",
            validator=custom_validator
        )
        assert result == ["GRNW_000103851", "GRNW_000103853"]
        assert "grnw_000103852" not in result
