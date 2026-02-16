"""
Logging utilities for PDF Merger.
Provides centralized logging setup and management.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str = "pdf_merger",
    level: int = logging.INFO,
    enable_file_logging: bool = False,
) -> logging.Logger:
    """
    Setup and return a logger instance.
    Logs to both console (if available) and a log file.

    Args:
        name: Logger name (default: "pdf_merger")
        level: Logging level (default: logging.INFO)
        enable_file_logging: Whether to also log to ~/.pdf_merger/logs/pdf_merger.log

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Create console handler (only if stdout is available)
    try:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
        logger.addHandler(console_handler)
    except Exception:
        pass  # Console not available (e.g., in PyInstaller build with console=False)

    # Optional file handler for log file
    if enable_file_logging:
        try:
            log_dir = Path.home() / ".pdf_merger" / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / "pdf_merger.log"

            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception:
            pass  # Could not create log file (e.g., permissions issue)

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Optional module name. If None, uses "pdf_merger"

    Returns:
        Logger instance
    """
    if name is None:
        name = "pdf_merger"
    else:
        # Ensure logger is a child of main logger
        name = f"pdf_merger.{name}"

    return logging.getLogger(name)
