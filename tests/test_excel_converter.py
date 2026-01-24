"""
Unit tests for excel_converter module.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from pdf_merger.excel_converter import convert_excel_to_pdf, _get_xlsx2pdf
from pdf_merger.enums import EXCEL_FILE_EXTENSIONS


class TestConvertExcelToPdf:
    """Test cases for convert_excel_to_pdf function."""
    
    @patch('pdf_merger.excel_converter._get_xlsx2pdf')
    def test_convert_excel_xlsx_success(self, mock_get_xlsx2pdf, tmp_path):
        """Test successful conversion of .xlsx file to PDF."""
        excel_file = tmp_path / "test.xlsx"
        excel_file.write_bytes(b"fake excel content")
        output_pdf = tmp_path / "test.pdf"
        
        mock_xlsx2pdf = MagicMock()
        mock_get_xlsx2pdf.return_value = mock_xlsx2pdf
        
        result = convert_excel_to_pdf(excel_file, output_pdf)
        
        assert result is True
        mock_xlsx2pdf.convert.assert_called_once_with(str(excel_file), str(output_pdf))
    
    @patch('pdf_merger.excel_converter._get_xlsx2pdf')
    def test_convert_excel_xls_success(self, mock_get_xlsx2pdf, tmp_path):
        """Test successful conversion of .xls file to PDF."""
        excel_file = tmp_path / "test.xls"
        excel_file.write_bytes(b"fake excel content")
        output_pdf = tmp_path / "test.pdf"
        
        mock_xlsx2pdf = MagicMock()
        mock_get_xlsx2pdf.return_value = mock_xlsx2pdf
        
        result = convert_excel_to_pdf(excel_file, output_pdf)
        
        assert result is True
        mock_xlsx2pdf.convert.assert_called_once_with(str(excel_file), str(output_pdf))
    
    @patch('pdf_merger.excel_converter._get_xlsx2pdf')
    @patch('pdf_merger.excel_converter.logger')
    def test_convert_excel_file_not_found(self, mock_logger, mock_get_xlsx2pdf, tmp_path):
        """Test conversion when Excel file doesn't exist."""
        excel_file = tmp_path / "nonexistent.xlsx"
        output_pdf = tmp_path / "test.pdf"
        
        result = convert_excel_to_pdf(excel_file, output_pdf)
        
        assert result is False
        mock_get_xlsx2pdf.assert_not_called()
        mock_logger.error.assert_called_once()
    
    @patch('pdf_merger.excel_converter._get_xlsx2pdf')
    @patch('pdf_merger.excel_converter.logger')
    def test_convert_excel_invalid_file_type(self, mock_logger, mock_get_xlsx2pdf, tmp_path):
        """Test conversion when file is not an Excel file."""
        text_file = tmp_path / "test.txt"
        text_file.write_text("not excel")
        output_pdf = tmp_path / "test.pdf"
        
        result = convert_excel_to_pdf(text_file, output_pdf)
        
        assert result is False
        mock_get_xlsx2pdf.assert_not_called()
        mock_logger.error.assert_called_once()
    
    @patch('pdf_merger.excel_converter._get_xlsx2pdf')
    @patch('pdf_merger.excel_converter.logger')
    def test_convert_excel_import_error(self, mock_logger, mock_get_xlsx2pdf, tmp_path):
        """Test conversion when xlsx2pdf is not installed."""
        excel_file = tmp_path / "test.xlsx"
        excel_file.write_bytes(b"fake excel content")
        output_pdf = tmp_path / "test.pdf"
        
        mock_get_xlsx2pdf.side_effect = ImportError("xlsx2pdf not found")
        
        result = convert_excel_to_pdf(excel_file, output_pdf)
        
        assert result is False
        mock_logger.error.assert_called()
    
    @patch('pdf_merger.excel_converter._get_xlsx2pdf')
    @patch('pdf_merger.excel_converter.logger')
    def test_convert_excel_conversion_error(self, mock_logger, mock_get_xlsx2pdf, tmp_path):
        """Test conversion when xlsx2pdf conversion fails."""
        excel_file = tmp_path / "test.xlsx"
        excel_file.write_bytes(b"fake excel content")
        output_pdf = tmp_path / "test.pdf"
        
        mock_xlsx2pdf = MagicMock()
        mock_xlsx2pdf.convert.side_effect = Exception("Conversion failed")
        mock_get_xlsx2pdf.return_value = mock_xlsx2pdf
        
        result = convert_excel_to_pdf(excel_file, output_pdf)
        
        assert result is False
        mock_logger.error.assert_called()
    
    @patch('pdf_merger.excel_converter._get_xlsx2pdf')
    @patch('pdf_merger.excel_converter.logger')
    @patch('pathlib.Path.exists')
    def test_convert_excel_output_not_created(self, mock_exists, mock_logger, mock_get_xlsx2pdf, tmp_path):
        """Test conversion when output PDF is not created."""
        excel_file = tmp_path / "test.xlsx"
        excel_file.write_bytes(b"fake excel content")
        output_pdf = tmp_path / "test.pdf"
        
        mock_xlsx2pdf = MagicMock()
        mock_get_xlsx2pdf.return_value = mock_xlsx2pdf
        
        # Mock exists() to return False for output file
        def exists_side_effect(path):
            if path == output_pdf:
                return False
            return True
        
        mock_exists.side_effect = exists_side_effect
        
        result = convert_excel_to_pdf(excel_file, output_pdf)
        
        assert result is False
        mock_logger.error.assert_called()


class TestGetXlsx2Pdf:
    """Test cases for _get_xlsx2pdf function."""
    
    def test_get_xlsx2pdf_imports_library(self):
        """Test that _get_xlsx2pdf imports xlsx2pdf when available."""
        import pdf_merger.excel_converter as excel_conv
        
        # Reset the global variable
        original_xlsx2pdf = excel_conv._xlsx2pdf
        
        try:
            excel_conv._xlsx2pdf = None
            
            # Mock the xlsx2pdf import
            with patch('xlsx2pdf', MagicMock()) as mock_xlsx2pdf:
                result = _get_xlsx2pdf()
                
                # Should have been set
                assert excel_conv._xlsx2pdf is not None
        finally:
            excel_conv._xlsx2pdf = original_xlsx2pdf
    
    def test_get_xlsx2pdf_uses_cached_import(self):
        """Test that _get_xlsx2pdf uses cached import on subsequent calls."""
        import pdf_merger.excel_converter as excel_conv
        
        # Set up cached value
        original_xlsx2pdf = excel_conv._xlsx2pdf
        
        try:
            mock_xlsx2pdf = MagicMock()
            excel_conv._xlsx2pdf = mock_xlsx2pdf
            
            # Call should return cached value without importing
            with patch('xlsx2pdf') as mock_import:
                result = _get_xlsx2pdf()
                
                # Should not call import since value is cached
                mock_import.assert_not_called()
                assert result is mock_xlsx2pdf
        finally:
            # Restore original value
            excel_conv._xlsx2pdf = original_xlsx2pdf
    
    def test_get_xlsx2pdf_raises_import_error(self):
        """Test that _get_xlsx2pdf raises ImportError when xlsx2pdf is not available."""
        import pdf_merger.excel_converter as excel_conv
        
        # Reset the global variable
        original_xlsx2pdf = excel_conv._xlsx2pdf
        
        try:
            excel_conv._xlsx2pdf = None
            
            # Mock the import to raise ImportError
            with patch('builtins.__import__', side_effect=ImportError("No module named 'xlsx2pdf'")):
                with pytest.raises(ImportError) as exc_info:
                    _get_xlsx2pdf()
                
                assert "xlsx2pdf" in str(exc_info.value)
        finally:
            excel_conv._xlsx2pdf = original_xlsx2pdf
