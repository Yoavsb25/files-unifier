"""
Data parsing module.
Handles parsing serial numbers and filenames from strings.
"""

from typing import List
from .enums import SERIAL_NUMBER_SEPARATOR


def parse_serial_numbers(serial_numbers_str: str) -> List[str]:
    """
    Parse comma-separated filenames (serial numbers) from a string.
    
    Args:
        serial_numbers_str: String containing comma-separated filenames
        
    Returns:
        List of filenames (stripped of whitespace)
    """
    if not serial_numbers_str or not serial_numbers_str.strip():
        return []
    
    filenames = [s.strip() for s in serial_numbers_str.split(SERIAL_NUMBER_SEPARATOR)]

    return [s for s in filenames if s]
