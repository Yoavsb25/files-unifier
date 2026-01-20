#!/usr/bin/env python3
"""
Main entry point for PDF Merger.
Supports both interactive and command-line modes.
"""

import sys
from cli.interactive import main as interactive_main
from cli.command_line import main as cli_main


if __name__ == '__main__':
    if len(sys.argv) > 1:
        cli_main()
    else:
        interactive_main()
