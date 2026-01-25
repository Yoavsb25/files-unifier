"""
License-related UI logic.
"""

import customtkinter as ctk

from ..licensing import LicenseManager, LicenseStatus

GREEN_COLOR = "green"
RED_COLOR = "red"
ORANGE_COLOR = "orange"
YELLOW_COLOR = "yellow"
VALID_LICENSE = "✓ License valid"
EXPIRED_LICENSE = "⚠ License expired - Merge functionality disabled"
LABEL_FONT = ctk.CTkFont(size=18, weight="bold")

def match_color_to_display_text(
    color: str,
    company_name: str,
    expires: str,
    warning_msg: str,
    error_msg: str
) -> str:
    """
    Return the appropriate license display text based on the given color and context.

    Args:
        color: Color representing license state (e.g., green, red).
        company_name: The name of the licensed company.
        expires: The license expiration date.
        warning_msg: A warning message if applicable.
        error_msg: An error message for failed license checks.

    Returns:
        A formatted string for UI display.
    """
    if color == GREEN_COLOR:
        return f"✓ Licensed to: {company_name} (Expires: {expires})"

    elif color == ORANGE_COLOR:
        return EXPIRED_LICENSE

    elif color == YELLOW_COLOR:
        return f"✓ Licensed to: {company_name} - {warning_msg}"

    elif color == RED_COLOR:
        return f"✓ Licensed to: {company_name} - {warning_msg}" if warning_msg else f"✗ {error_msg}"

def match_color_to_warning_level(warning_level: str) -> str:
    """
    Match color to warning level.
    """
    dict_warning_level_to_color = {
        'critical': RED_COLOR,
        'warning': ORANGE_COLOR,
        'info': YELLOW_COLOR
    }
    return dict_warning_level_to_color.get(warning_level, YELLOW_COLOR)


def update_license_display(license_manager: LicenseManager, license_label) -> bool:
    """
    Update license status display and return whether license is valid.
    
    Args:
        license_manager: The license manager instance
        license_label: The label widget to update
        
    Returns:
        True if license is valid, False otherwise
    """
    status = license_manager.get_license_status()
    license_valid = (status == LicenseStatus.VALID)

    if license_valid:
        info = license_manager.get_license_info()
        if not info:
            # No license info available - show simple valid message
            license_label.configure(
                text=VALID_LICENSE,
                text_color=GREEN_COLOR,
                font=LABEL_FONT
            )
        else:
            warning_msg = license_manager.get_expiry_warning_message()
            warning_level = info.get("expiry_warning_level", "info")
            company_name = info.get("company", "Unknown")
            expires = info.get("expires", "Unknown")
            error_msg = ""

            text_color = GREEN_COLOR if not warning_msg else match_color_to_warning_level(warning_level)
            display_text = match_color_to_display_text(
                text_color, company_name, expires, warning_msg, error_msg
            )

            license_label.configure(
                text=display_text,
                text_color=text_color,
                font=LABEL_FONT
            )
    elif status == LicenseStatus.EXPIRED:
        license_label.configure(
            text=EXPIRED_LICENSE,
            text_color=ORANGE_COLOR,
            font=LABEL_FONT
        )
    else:
        error_msg = license_manager.get_license_error_message(status)
        license_label.configure(
            text=f"✗ {error_msg}",
            text_color=RED_COLOR,
            font=LABEL_FONT
        )

    return license_valid
