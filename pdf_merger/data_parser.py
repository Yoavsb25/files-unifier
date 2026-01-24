"""
Data parsing module.
Handles parsing serial numbers from strings.
"""

from typing import List, Set, Optional
from .enums import SERIAL_NUMBER_SEPARATOR, SERIAL_NUMBER_PREFIX, SERIAL_NUMBER_PREFIX_LOWER


def split_serial_numbers(serial_numbers_str: str) -> List[str]:
    """
    Split serial numbers from a string into a list of strings according to a known separator.
    
    Args:
        serial_numbers_str: String containing serial numbers separated by a known separator
        
    Returns:
        List of serial numbers (stripped of whitespace)
    """
    if not serial_numbers_str or not serial_numbers_str.strip():
        return []
    
    serial_numbers = [s.strip() for s in serial_numbers_str.split(SERIAL_NUMBER_SEPARATOR)]

    return [s for s in serial_numbers if s]


def normalize_serial_number(serial_number: str, to_uppercase: bool = True) -> str:
    """
    Normalize a serial number to a standard format.
    Only normalizes the prefix (GRNW_/grnw_), leaving the numeric suffix unchanged.
    
    Args:
        serial_number: Serial number to normalize
        to_uppercase: If True, convert prefix to uppercase; if False, convert to lowercase
        
    Returns:
        Normalized serial number string
    """
    if not serial_number:
        return serial_number
    
    normalized = serial_number.strip()
    
    if to_uppercase:
        if normalized.startswith(SERIAL_NUMBER_PREFIX_LOWER):
            normalized = SERIAL_NUMBER_PREFIX + normalized[len(SERIAL_NUMBER_PREFIX_LOWER):]
    else:
        if normalized.startswith(SERIAL_NUMBER_PREFIX):
            normalized = SERIAL_NUMBER_PREFIX_LOWER + normalized[len(SERIAL_NUMBER_PREFIX):]
    
    return normalized


def extract_numeric_suffix(serial_number: str) -> Optional[str]:
    """
    Extract the numeric suffix from a serial number.
    
    Args:
        serial_number: Serial number (e.g., "GRNW_000103851")
        
    Returns:
        Numeric suffix as string, or None if not found
    """
    if not serial_number:
        return None
    
    parts = serial_number.split('_', 1)
    if len(parts) == 2 and parts[1].isdigit():
        return parts[1]
    return None


def join_serial_numbers(serial_numbers: List[str], separator: str = None) -> str:
    """
    Join a list of serial numbers into a single string.
    
    Args:
        serial_numbers: List of serial number strings
        separator: Separator to use (defaults to SERIAL_NUMBER_SEPARATOR)
        
    Returns:
        Joined string of serial numbers
    """
    if not serial_numbers:
        return ""
    
    if separator is None:
        separator = SERIAL_NUMBER_SEPARATOR
    
    # Filter out empty strings and strip whitespace
    cleaned = [s.strip() for s in serial_numbers if s and s.strip()]
    return separator.join(cleaned)


def deduplicate_serial_numbers(serial_numbers: List[str], preserve_order: bool = True) -> List[str]:
    """
    Remove duplicate serial numbers from a list.
    
    Args:
        serial_numbers: List of serial number strings
        preserve_order: If True, preserve the order of first occurrence
        
    Returns:
        List of unique serial numbers
    """
    if not serial_numbers:
        return []
    
    if preserve_order:
        seen: Set[str] = set()
        result = []
        for serial in serial_numbers:
            if serial and serial not in seen:
                seen.add(serial)
                result.append(serial)
        return result
    else:
        return list(set(serial_numbers))


def filter_valid_serial_numbers(serial_numbers_str: str, validator=None) -> List[str]:
    """
    Parse and filter serial numbers, keeping only valid ones.
    
    Args:
        serial_numbers_str: String containing serial numbers separated by separator
        validator: Optional validation function. If None, uses default validator
        
    Returns:
        List of valid serial numbers
    """
    from .validators import validate_serial_number
    
    if validator is None:
        validator = validate_serial_number
    
    all_serial_numbers = split_serial_numbers(serial_numbers_str)
    return [serial for serial in all_serial_numbers if validator(serial)]
