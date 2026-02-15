"""
Unit tests for crash_reporting module.
"""

import sys
from pathlib import Path
from unittest.mock import patch

from pdf_merger.observability.crash_reporting import CrashReporter, get_crash_reporter


class TestCrashReporter:
    """Test cases for CrashReporter class."""

    def test_crash_reporter_init_disabled(self, tmp_path):
        """Test initializing CrashReporter with disabled state."""
        reporter = CrashReporter(enabled=False, report_dir=tmp_path)

        assert reporter.enabled is False
        assert reporter.report_dir == tmp_path

    def test_crash_reporter_init_enabled(self, tmp_path):
        """Test initializing CrashReporter with enabled state."""
        reporter = CrashReporter(enabled=True, report_dir=tmp_path)

        assert reporter.enabled is True
        assert reporter.report_dir == tmp_path
        assert reporter.report_dir.exists()

    def test_crash_reporter_init_default_dir(self):
        """Test initializing CrashReporter with default directory."""
        with patch("pathlib.Path.home", return_value=Path("/tmp")):
            reporter = CrashReporter(enabled=True)

            assert reporter.report_dir == Path("/tmp/.pdf_merger/crashes")
            assert reporter.report_dir.exists()

    def test_report_exception_disabled(self, tmp_path):
        """Test reporting exception when disabled."""
        reporter = CrashReporter(enabled=False, report_dir=tmp_path)

        result = reporter.report_exception(ValueError("Test error"))

        assert result is None
        # No crash reports should be created
        assert len(list(tmp_path.glob("crash_*.txt"))) == 0

    def test_report_exception_enabled(self, tmp_path):
        """Test reporting exception when enabled."""
        reporter = CrashReporter(enabled=True, report_dir=tmp_path)

        exception = ValueError("Test error message")
        result = reporter.report_exception(exception)

        assert result is not None
        assert result.exists()
        assert result.name.startswith("crash_")
        assert result.suffix == ".txt"

        # Verify report content
        content = result.read_text()
        assert "Crash Report" in content
        assert "ValueError" in content
        assert "Test error message" in content
        assert "Stack Trace" in content

    def test_report_exception_with_context(self, tmp_path):
        """Test reporting exception with context information."""
        reporter = CrashReporter(enabled=True, report_dir=tmp_path)

        exception = ValueError("Test error")
        context = {"user_action": "merge_pdfs", "file_count": 5, "error_location": "processor.py"}

        result = reporter.report_exception(exception, context=context)

        assert result is not None
        content = result.read_text()
        assert "Context:" in content
        assert "user_action: merge_pdfs" in content
        assert "file_count: 5" in content
        assert "error_location: processor.py" in content

    def test_report_exception_system_info(self, tmp_path):
        """Test that crash report includes system information."""
        reporter = CrashReporter(enabled=True, report_dir=tmp_path)

        exception = ValueError("Test error")
        result = reporter.report_exception(exception)

        content = result.read_text()
        assert "System Information:" in content
        assert "Platform:" in content
        assert "Python Version:" in content

    def test_report_exception_save_failure(self, tmp_path):
        """Test handling save failure when reporting exception."""
        reporter = CrashReporter(enabled=True, report_dir=tmp_path)

        # Make the directory read-only to cause save failure
        tmp_path.chmod(0o444)  # Read-only

        try:
            exception = ValueError("Test error")
            result = reporter.report_exception(exception)

            # Should return None on failure
            assert result is None
        finally:
            # Restore permissions
            tmp_path.chmod(0o755)

    def test_install_exception_hook_disabled(self):
        """Test installing exception hook when disabled."""
        original_hook = sys.excepthook
        reporter = CrashReporter(enabled=False)

        reporter.install_exception_hook()

        # Hook should not be installed
        assert sys.excepthook == original_hook

    def test_install_exception_hook_enabled(self):
        """Test installing exception hook when enabled."""
        original_hook = sys.excepthook
        reporter = CrashReporter(enabled=True)

        try:
            reporter.install_exception_hook()

            # Hook should be installed
            assert sys.excepthook != original_hook
            assert sys.excepthook is not None
        finally:
            # Restore original hook
            sys.excepthook = original_hook

    def test_install_exception_hook_calls_original(self, tmp_path):
        """Test that exception hook calls original hook."""
        import sys

        original_called = []
        original_hook = sys.__excepthook__

        def mock_original(exc_type, exc_value, exc_traceback):
            original_called.append((exc_type, exc_value))
            original_hook(exc_type, exc_value, exc_traceback)

        # Patch sys.__excepthook__ to track calls
        with patch.object(sys, "__excepthook__", side_effect=mock_original):
            reporter = CrashReporter(enabled=True, report_dir=tmp_path)
            reporter.install_exception_hook()

            # Trigger an exception
            try:
                raise ValueError("Test")
            except ValueError as e:
                sys.excepthook(type(e), e, e.__traceback__)

            # Original hook should have been called
            assert len(original_called) > 0

    def test_install_exception_hook_reports_exception(self, tmp_path):
        """Test that exception hook reports exceptions."""
        reporter = CrashReporter(enabled=True, report_dir=tmp_path)
        reporter.install_exception_hook()

        try:
            # Trigger an exception
            try:
                raise ValueError("Test exception")
            except ValueError as e:
                sys.excepthook(type(e), e, e.__traceback__)

            # Should have created a crash report
            crash_reports = list(tmp_path.glob("crash_*.txt"))
            assert len(crash_reports) > 0
        finally:
            # Restore original hook
            sys.excepthook = sys.__excepthook__


class TestGetCrashReporter:
    """Test cases for get_crash_reporter function."""

    def test_get_crash_reporter_creates_instance(self):
        """Test getting crash reporter creates new instance."""
        # Reset global state
        import pdf_merger.observability.crash_reporting as cr_module

        cr_module._crash_reporter = None

        reporter1 = get_crash_reporter(enabled=False)

        assert reporter1 is not None
        assert isinstance(reporter1, CrashReporter)

    def test_get_crash_reporter_returns_same_instance(self):
        """Test getting crash reporter returns same instance."""
        # Reset global state
        import pdf_merger.observability.crash_reporting as cr_module

        cr_module._crash_reporter = None

        reporter1 = get_crash_reporter(enabled=False)
        reporter2 = get_crash_reporter(enabled=True)

        # Should return same instance (singleton)
        assert reporter1 is reporter2

    def test_get_crash_reporter_enabled(self):
        """Test getting crash reporter with enabled flag."""
        # Reset global state
        import pdf_merger.observability.crash_reporting as cr_module

        cr_module._crash_reporter = None

        reporter = get_crash_reporter(enabled=True)

        assert reporter.enabled is True
