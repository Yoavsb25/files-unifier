"""
Unit tests for license UI logic.
"""

import importlib
import sys
from types import ModuleType
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(scope="module")
def license_ui_deps():
    class MockCTkFont:
        def __init__(self, *args, **kwargs):
            pass

    mock_ctk = ModuleType("customtkinter")
    mock_ctk.CTkFont = MockCTkFont

    with patch.dict(sys.modules, {"customtkinter": mock_ctk}):
        licensing_module = importlib.import_module("pdf_merger.licensing")
        theme_module = importlib.import_module("pdf_merger.ui.theme")
        license_ui_module = importlib.import_module("pdf_merger.ui.license_ui")
        yield {
            "LicenseStatus": licensing_module.LicenseStatus,
            "update_license_display": license_ui_module.update_license_display,
            "ERROR_RED": theme_module.ERROR_RED,
            "SUCCESS_GREEN": theme_module.SUCCESS_GREEN,
            "WARNING_YELLOW": theme_module.WARNING_YELLOW,
        }


class TestUpdateLicenseDisplay:
    """Test cases for update_license_display function."""

    @pytest.fixture(autouse=True)
    def _setup(self, license_ui_deps):
        self.LicenseStatus = license_ui_deps["LicenseStatus"]
        self.update_license_display = license_ui_deps["update_license_display"]
        self.ERROR_RED = license_ui_deps["ERROR_RED"]
        self.SUCCESS_GREEN = license_ui_deps["SUCCESS_GREEN"]
        self.WARNING_YELLOW = license_ui_deps["WARNING_YELLOW"]

    def test_update_license_display_valid_no_info(self):
        """Test updating license display with valid license but no info."""
        mock_manager = MagicMock()
        mock_manager.get_license_status.return_value = self.LicenseStatus.VALID
        mock_manager.get_license_info.return_value = None
        mock_label = MagicMock()

        result = self.update_license_display(mock_manager, mock_label)

        assert result is True
        mock_label.configure.assert_called_once()
        call_args = mock_label.configure.call_args[1]
        assert call_args["text"] == "✓ Licensed · Expires Unknown"
        assert call_args["text_color"] == self.SUCCESS_GREEN

    def test_update_license_display_valid_with_info(self):
        """Test updating license display with valid license and info."""
        mock_manager = MagicMock()
        mock_manager.get_license_status.return_value = self.LicenseStatus.VALID
        mock_manager.get_license_info.return_value = {
            "company": "Test Company",
            "expires": "2027-12-31",
        }
        mock_manager.get_expiry_warning_message.return_value = None
        mock_label = MagicMock()

        result = self.update_license_display(mock_manager, mock_label)

        assert result is True
        mock_label.configure.assert_called_once()
        call_args = mock_label.configure.call_args[1]
        assert "2027-12-31" in call_args["text"]
        assert call_args["text_color"] == self.SUCCESS_GREEN

    def test_update_license_display_valid_with_critical_warning(self):
        """Test updating license display with critical expiry warning."""
        mock_manager = MagicMock()
        mock_manager.get_license_status.return_value = self.LicenseStatus.VALID
        mock_manager.get_license_info.return_value = {
            "company": "Test Company",
            "expires": "2027-12-31",
            "expiry_warning_level": "critical",
        }
        mock_manager.get_expiry_warning_message.return_value = "License expires in 5 days!"
        mock_label = MagicMock()

        result = self.update_license_display(mock_manager, mock_label)

        assert result is True
        mock_label.configure.assert_called_once()
        call_args = mock_label.configure.call_args[1]
        assert call_args["text_color"] == self.ERROR_RED
        assert "Expired" in call_args["text"]

    def test_update_license_display_valid_with_warning_level(self):
        """Test updating license display with warning level expiry."""
        mock_manager = MagicMock()
        mock_manager.get_license_status.return_value = self.LicenseStatus.VALID
        mock_manager.get_license_info.return_value = {
            "company": "Test Company",
            "expires": "2027-12-31",
            "expiry_warning_level": "warning",
        }
        mock_manager.get_expiry_warning_message.return_value = "License expires in 10 days."
        mock_label = MagicMock()

        result = self.update_license_display(mock_manager, mock_label)

        assert result is True
        call_args = mock_label.configure.call_args[1]
        assert call_args["text_color"] == self.ERROR_RED

    def test_update_license_display_valid_with_info_level(self):
        """Test updating license display with info level expiry."""
        mock_manager = MagicMock()
        mock_manager.get_license_status.return_value = self.LicenseStatus.VALID
        mock_manager.get_license_info.return_value = {
            "company": "Test Company",
            "expires": "2027-12-31",
            "expiry_warning_level": "info",
        }
        mock_manager.get_expiry_warning_message.return_value = "License expires in 20 days."
        mock_label = MagicMock()

        result = self.update_license_display(mock_manager, mock_label)

        assert result is True
        call_args = mock_label.configure.call_args[1]
        assert call_args["text_color"] == self.WARNING_YELLOW

    def test_update_license_display_expired(self):
        """Test updating license display with expired license."""
        mock_manager = MagicMock()
        mock_manager.get_license_status.return_value = self.LicenseStatus.EXPIRED
        mock_label = MagicMock()

        result = self.update_license_display(mock_manager, mock_label)

        assert result is False
        mock_label.configure.assert_called_once()
        call_args = mock_label.configure.call_args[1]
        assert "expired" in call_args["text"].lower()
        assert call_args["text_color"] == self.ERROR_RED

    def test_update_license_display_invalid(self):
        """Test updating license display with invalid license."""
        mock_manager = MagicMock()
        mock_manager.get_license_status.return_value = self.LicenseStatus.INVALID_SIGNATURE
        mock_manager.get_license_error_message.return_value = "License signature is invalid."
        mock_label = MagicMock()

        result = self.update_license_display(mock_manager, mock_label)

        assert result is False
        mock_label.configure.assert_called_once()
        call_args = mock_label.configure.call_args[1]
        assert "License signature is invalid" in call_args["text"]
        assert call_args["text_color"] == self.ERROR_RED

    def test_update_license_display_not_found(self):
        """Test updating license display when license not found."""
        mock_manager = MagicMock()
        mock_manager.get_license_status.return_value = self.LicenseStatus.NOT_FOUND
        mock_manager.get_license_error_message.return_value = "License file not found."
        mock_label = MagicMock()

        result = self.update_license_display(mock_manager, mock_label)

        assert result is False
        call_args = mock_label.configure.call_args[1]
        assert "License file not found" in call_args["text"]
        assert call_args["text_color"] == self.ERROR_RED
