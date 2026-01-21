"""
CLI interfaces for PDF Merger
"""

from .command_line import main as cli_main
from .interactive import main as interactive_main

__all__ = ['cli_main', 'interactive_main']
