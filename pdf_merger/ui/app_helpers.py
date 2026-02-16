"""
UI helper functions for PDF Merger app.
Pure functions for run-merge eligibility and other state checks so app logic is testable.
"""

from pathlib import Path
from typing import List, Optional


def get_run_block_reasons(
    license_valid: bool,
    input_file_path: Optional[Path],
    pdf_dir_path: Optional[Path],
    output_dir_path: Optional[Path],
    has_validation_errors: bool,
    is_processing: bool,
) -> List[str]:
    """
    Return list of reasons Run Merge is disabled (empty if allowed).
    Use for tooltips and debugging.
    """
    reasons: List[str] = []
    if not license_valid:
        reasons.append("License invalid")
    if input_file_path is None:
        reasons.append("Select input file")
    if pdf_dir_path is None:
        reasons.append("Select source directory")
    if output_dir_path is None:
        reasons.append("Select output directory")
    if has_validation_errors:
        reasons.append("Fix validation errors")
    if is_processing:
        reasons.append("Merge in progress")
    return reasons


def can_run_merge(
    license_valid: bool,
    input_file_path: Optional[Path],
    pdf_dir_path: Optional[Path],
    output_dir_path: Optional[Path],
    has_validation_errors: bool,
    is_processing: bool,
) -> bool:
    """True if Run Merge is allowed: valid license, all paths set, no validation errors, not already processing."""
    return (
        len(
            get_run_block_reasons(
                license_valid,
                input_file_path,
                pdf_dir_path,
                output_dir_path,
                has_validation_errors,
                is_processing,
            )
        )
        == 0
    )
