"""
Unit tests for path_utils module.
"""

import pytest
import platform
import unicodedata
from pathlib import Path
from unittest.mock import patch, MagicMock
from pdf_merger.utils.path_utils import (
    normalize_path,
    compare_paths,
    resolve_path,
    is_long_path,
    enable_long_paths_windows,
    get_case_insensitive_path,
    validate_path,
    WINDOWS_LONG_PATH_PREFIX,
    WINDOWS_MAX_PATH
)


class TestNormalizePath:
    """Test cases for normalize_path function."""
    
    def test_normalize_path_absolute(self, tmp_path):
        """Test normalizing an absolute path."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        
        result = normalize_path(test_file)
        
        assert result.is_absolute()
        assert result.exists()
    
    def test_normalize_path_relative(self, tmp_path):
        """Test normalizing a relative path."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        
        # Change to tmp_path directory
        import os
        old_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = normalize_path(Path("test.txt"))
            assert result.is_absolute()
            assert result.exists()
        finally:
            os.chdir(old_cwd)
    
    def test_normalize_path_resolve_fails(self, tmp_path):
        """Test normalizing when resolve() fails."""
        # Create a path that might fail to resolve
        test_path = tmp_path / "nonexistent" / ".." / "test.txt"
        
        with patch.object(Path, 'resolve', side_effect=OSError("Cannot resolve")):
            result = normalize_path(test_path)
            # Should fall back to absolute()
            assert result.is_absolute()
    
    def test_normalize_path_unicode_normalization(self, tmp_path):
        """Test Unicode normalization (NFD/NFC)."""
        # Create a path with Unicode characters
        unicode_name = "test_é_ñ_ü.txt"
        test_file = tmp_path / unicode_name
        test_file.write_text("test")
        
        result = normalize_path(test_file)
        
        # Should normalize to NFC
        assert unicodedata.normalize('NFC', str(result)) == str(result)
        assert result.exists()


class TestComparePaths:
    """Test cases for compare_paths function."""
    
    def test_compare_paths_same(self, tmp_path):
        """Test comparing identical paths."""
        path1 = tmp_path / "test.txt"
        path2 = tmp_path / "test.txt"
        
        assert compare_paths(path1, path2) is True
    
    def test_compare_paths_different(self, tmp_path):
        """Test comparing different paths."""
        path1 = tmp_path / "test1.txt"
        path2 = tmp_path / "test2.txt"
        
        assert compare_paths(path1, path2) is False
    
    def test_compare_paths_case_sensitive(self, tmp_path):
        """Test case-sensitive comparison."""
        path1 = tmp_path / "Test.txt"
        path2 = tmp_path / "test.txt"
        
        result = compare_paths(path1, path2, case_sensitive=True)
        
        # On case-sensitive filesystems, these should be different
        # On case-insensitive filesystems, they might be the same
        # But with case_sensitive=True, they should be compared case-sensitively
        if platform.system() != 'Windows':
            assert result is False
        else:
            # On Windows, even with case_sensitive=True, the normalization might make them equal
            # This is expected behavior
            pass
    
    def test_compare_paths_case_insensitive(self, tmp_path):
        """Test case-insensitive comparison."""
        path1 = tmp_path / "Test.txt"
        path2 = tmp_path / "test.txt"
        
        result = compare_paths(path1, path2, case_sensitive=False)
        
        # Should be equal regardless of case
        assert result is True
    
    def test_compare_paths_platform_default(self, tmp_path):
        """Test using platform default case sensitivity."""
        path1 = tmp_path / "Test.txt"
        path2 = tmp_path / "test.txt"
        
        result = compare_paths(path1, path2, case_sensitive=None)
        
        # Should use platform default (case-insensitive on Windows)
        if platform.system() == 'Windows':
            assert result is True
        else:
            assert result is False


class TestResolvePath:
    """Test cases for resolve_path function."""
    
    def test_resolve_path(self, tmp_path):
        """Test resolving a path."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        
        result = resolve_path(test_file)
        
        assert result.is_absolute()
        assert result.exists()


class TestIsLongPath:
    """Test cases for is_long_path function."""
    
    def test_is_long_path_short(self, tmp_path):
        """Test with a short path."""
        short_path = tmp_path / "test.txt"
        
        result = is_long_path(short_path)
        
        assert result is False
    
    def test_is_long_path_long(self, tmp_path):
        """Test with a long path."""
        # Create a path that exceeds Windows MAX_PATH
        long_name = "a" * 300
        long_path = tmp_path / long_name
        
        result = is_long_path(long_path)
        
        # Should be True if the full resolved path exceeds 260 characters
        path_str = str(long_path.resolve())
        if len(path_str) > WINDOWS_MAX_PATH:
            assert result is True
        else:
            assert result is False


class TestEnableLongPathsWindows:
    """Test cases for enable_long_paths_windows function."""
    
    @patch('pdf_merger.utils.path_utils.platform.system')
    def test_enable_long_paths_non_windows(self, mock_system):
        """Test on non-Windows platform."""
        mock_system.return_value = 'Linux'
        
        result = enable_long_paths_windows()
        
        assert result is True
    
    @patch('pdf_merger.utils.path_utils.platform.system')
    def test_enable_long_paths_windows_success(self, mock_system):
        """Test on Windows with successful path creation."""
        mock_system.return_value = 'Windows'
        
        result = enable_long_paths_windows()
        
        # Should return True (the function always returns True on success)
        assert result is True
    
    @patch('pdf_merger.utils.path_utils.platform.system')
    @patch('pdf_merger.utils.path_utils.Path')
    @patch('pdf_merger.utils.path_utils.logger')
    def test_enable_long_paths_windows_exception(self, mock_logger, mock_path, mock_system):
        """Test on Windows when path creation raises exception."""
        mock_system.return_value = 'Windows'
        mock_path.side_effect = Exception("Failed")
        
        result = enable_long_paths_windows()
        
        assert result is False
        mock_logger.warning.assert_called_once()


class TestGetCaseInsensitivePath:
    """Test cases for get_case_insensitive_path function."""
    
    def test_get_case_insensitive_path_found(self, tmp_path):
        """Test finding a file with case-insensitive matching."""
        test_file = tmp_path / "TestFile.txt"
        test_file.write_text("test")
        
        result = get_case_insensitive_path(tmp_path, "testfile.txt")
        
        assert result is not None
        assert result.name == "TestFile.txt"
    
    def test_get_case_insensitive_path_not_found(self, tmp_path):
        """Test when file is not found."""
        result = get_case_insensitive_path(tmp_path, "nonexistent.txt")
        
        assert result is None
    
    def test_get_case_insensitive_path_folder_not_exists(self, tmp_path):
        """Test when folder doesn't exist."""
        nonexistent_folder = tmp_path / "nonexistent"
        
        result = get_case_insensitive_path(nonexistent_folder, "test.txt")
        
        assert result is None
    
    def test_get_case_insensitive_path_folder_not_dir(self, tmp_path):
        """Test when folder is not a directory."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        
        result = get_case_insensitive_path(test_file, "test.txt")
        
        assert result is None
    
    @patch('pdf_merger.utils.path_utils.logger')
    def test_get_case_insensitive_path_permission_error(self, mock_logger, tmp_path):
        """Test when permission error occurs."""
        with patch.object(Path, 'iterdir', side_effect=PermissionError("Access denied")):
            result = get_case_insensitive_path(tmp_path, "test.txt")
            
            assert result is None
            mock_logger.warning.assert_called_once()
    
    @patch('pdf_merger.utils.path_utils.logger')
    def test_get_case_insensitive_path_os_error(self, mock_logger, tmp_path):
        """Test when OSError occurs."""
        with patch.object(Path, 'iterdir', side_effect=OSError("Error")):
            result = get_case_insensitive_path(tmp_path, "test.txt")
            
            assert result is None
            mock_logger.warning.assert_called_once()


class TestValidatePath:
    """Test cases for validate_path function."""
    
    def test_validate_path_exists(self, tmp_path):
        """Test validating an existing path."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        
        result = validate_path(test_file, must_exist=True)
        
        assert result is True
    
    def test_validate_path_not_exists(self, tmp_path):
        """Test validating a non-existent path."""
        nonexistent = tmp_path / "nonexistent.txt"
        
        result = validate_path(nonexistent, must_exist=True)
        
        assert result is False
    
    def test_validate_path_not_exists_optional(self, tmp_path):
        """Test validating a non-existent path when existence is optional."""
        nonexistent = tmp_path / "nonexistent.txt"
        
        result = validate_path(nonexistent, must_exist=False)
        
        assert result is True
    
    def test_validate_path_must_be_file(self, tmp_path):
        """Test validating that path must be a file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        
        result = validate_path(test_file, must_be_file=True)
        
        assert result is True
    
    def test_validate_path_must_be_file_but_is_dir(self, tmp_path):
        """Test validating when path must be file but is directory."""
        result = validate_path(tmp_path, must_be_file=True)
        
        assert result is False
    
    def test_validate_path_must_be_dir(self, tmp_path):
        """Test validating that path must be a directory."""
        result = validate_path(tmp_path, must_be_dir=True)
        
        assert result is True
    
    def test_validate_path_must_be_dir_but_is_file(self, tmp_path):
        """Test validating when path must be dir but is file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        
        result = validate_path(test_file, must_be_dir=True)
        
        assert result is False
    
    @patch('pdf_merger.utils.path_utils.platform.system')
    @patch('pdf_merger.utils.path_utils.is_long_path')
    @patch('pdf_merger.utils.path_utils.enable_long_paths_windows')
    @patch('pdf_merger.utils.path_utils.logger')
    def test_validate_path_long_path_windows_disabled(self, mock_logger, mock_enable, mock_is_long, mock_system, tmp_path):
        """Test validating a long path on Windows when long paths are disabled."""
        mock_system.return_value = 'Windows'
        mock_is_long.return_value = True
        mock_enable.return_value = False
        
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        
        result = validate_path(test_file)
        
        assert result is False
        mock_logger.warning.assert_called_once()
    
    @patch('pdf_merger.utils.path_utils.platform.system')
    @patch('pdf_merger.utils.path_utils.is_long_path')
    @patch('pdf_merger.utils.path_utils.enable_long_paths_windows')
    def test_validate_path_long_path_windows_enabled(self, mock_enable, mock_is_long, mock_system, tmp_path):
        """Test validating a long path on Windows when long paths are enabled."""
        mock_system.return_value = 'Windows'
        mock_is_long.return_value = True
        mock_enable.return_value = True
        
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        
        result = validate_path(test_file)
        
        assert result is True
    
    @patch('pdf_merger.utils.path_utils.logger')
    def test_validate_path_exception(self, mock_logger, tmp_path):
        """Test when an exception occurs during validation."""
        with patch.object(Path, 'resolve', side_effect=Exception("Error")):
            result = validate_path(tmp_path / "test.txt")
            
            assert result is False
            mock_logger.warning.assert_called_once()
