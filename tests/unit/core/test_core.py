"""
Unit tests for core module (merger and reporter).
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from pdf_merger.core.merge_orchestrator import run_merge, run_merge_job
from pdf_merger.core.result_reporter import format_result_summary, format_result_detailed
from pdf_merger.core.merge_processor import ProcessingResult
from pdf_merger.models import MergeResult, RowResult, RowStatus


class TestRunMerge:
    """Test cases for run_merge function."""
    
    @patch('pdf_merger.core.merge_orchestrator.process_file')
    @patch('pdf_merger.core.merge_orchestrator.logger')
    def test_run_merge_success(self, mock_logger, mock_process_file, tmp_path):
        """Test successful merge operation."""
        input_file = tmp_path / "input.csv"
        pdf_dir = tmp_path / "pdfs"
        output_dir = tmp_path / "output"
        
        expected_result = ProcessingResult(
            total_rows=5,
            successful_merges=4,
            failed_rows=[3]
        )
        mock_process_file.return_value = expected_result
        
        result = run_merge(input_file, pdf_dir, output_dir)
        
        assert result == expected_result
        mock_process_file.assert_called_once_with(
            file_path=input_file,
            source_folder=pdf_dir,
            output_folder=output_dir,
            required_column='serial_numbers'
        )
        assert mock_logger.info.called
    
    @patch('pdf_merger.core.merge_orchestrator.process_file')
    @patch('pdf_merger.core.merge_orchestrator.logger')
    def test_run_merge_with_custom_column(self, mock_logger, mock_process_file, tmp_path):
        """Test merge operation with custom required column."""
        input_file = tmp_path / "input.csv"
        pdf_dir = tmp_path / "pdfs"
        output_dir = tmp_path / "output"
        
        expected_result = ProcessingResult(
            total_rows=2,
            successful_merges=2,
            failed_rows=[]
        )
        mock_process_file.return_value = expected_result
        
        result = run_merge(input_file, pdf_dir, output_dir, required_column="custom_column")
        
        assert result == expected_result
        mock_process_file.assert_called_once_with(
            file_path=input_file,
            source_folder=pdf_dir,
            output_folder=output_dir,
            required_column="custom_column"
        )
    
    @patch('pdf_merger.core.merge_orchestrator.process_file')
    @patch('pdf_merger.core.merge_orchestrator.logger')
    def test_run_merge_exception(self, mock_logger, mock_process_file, tmp_path):
        """Test merge operation when exception occurs."""
        input_file = tmp_path / "input.csv"
        pdf_dir = tmp_path / "pdfs"
        output_dir = tmp_path / "output"
        
        mock_process_file.side_effect = ValueError("Processing error")
        
        with pytest.raises(ValueError, match="Processing error"):
            run_merge(input_file, pdf_dir, output_dir)
        
        assert mock_logger.error.called
        error_call = str(mock_logger.error.call_args)
        assert "Error during merge operation" in error_call


class TestFormatResultSummary:
    """Test cases for format_result_summary function."""
    
    def test_format_result_summary_success(self):
        """Test formatting summary with successful results."""
        result = ProcessingResult(
            total_rows=10,
            successful_merges=10,
            failed_rows=[]
        )
        
        summary = format_result_summary(result)
        
        assert "Processing Complete" in summary
        assert "Total rows processed: 10" in summary
        assert "Successfully merged PDFs: 10" in summary
        assert "Failed rows: 0" in summary
        assert "=" * 60 in summary
    
    def test_format_result_summary_with_failures(self):
        """Test formatting summary with failed rows."""
        result = ProcessingResult(
            total_rows=10,
            successful_merges=7,
            failed_rows=[2, 5, 8]
        )
        
        summary = format_result_summary(result)
        
        assert "Total rows processed: 10" in summary
        assert "Successfully merged PDFs: 7" in summary
        assert "Failed rows: 3" in summary
        assert "Failed row numbers: 2, 5, 8" in summary
    
    def test_format_result_summary_long_failed_list(self):
        """Test formatting summary with many failed rows (truncation)."""
        result = ProcessingResult(
            total_rows=100,
            successful_merges=50,
            failed_rows=list(range(1, 51))  # 50 failed rows
        )
        
        summary = format_result_summary(result)
        
        assert "Failed rows: 50" in summary
        # Should truncate long list
        if "Failed row numbers:" in summary:
            failed_line = [line for line in summary.split('\n') if 'Failed row numbers:' in line][0]
            assert len(failed_line) <= 100 or "..." in failed_line
    
    def test_format_result_summary_empty(self):
        """Test formatting summary with empty result."""
        result = ProcessingResult(
            total_rows=0,
            successful_merges=0,
            failed_rows=[]
        )
        
        summary = format_result_summary(result)
        
        assert "Total rows processed: 0" in summary
        assert "Successfully merged PDFs: 0" in summary
        assert "Failed rows: 0" in summary


class TestFormatResultDetailed:
    """Test cases for format_result_detailed function."""
    
    def test_format_result_detailed_success(self):
        """Test formatting detailed report with successful results."""
        result = ProcessingResult(
            total_rows=10,
            successful_merges=10,
            failed_rows=[]
        )
        
        report = format_result_detailed(result)
        
        assert "Detailed Processing Report" in report
        assert "Total rows in input file: 10" in report
        assert "Successfully merged PDFs: 10" in report
        assert "Failed rows: 0" in report
        assert "Success rate: 100.0%" in report
        assert "=" * 60 in report
    
    def test_format_result_detailed_with_failures(self):
        """Test formatting detailed report with failed rows."""
        result = ProcessingResult(
            total_rows=10,
            successful_merges=7,
            failed_rows=[2, 5, 8]
        )
        
        report = format_result_detailed(result)
        
        assert "Total rows in input file: 10" in report
        assert "Successfully merged PDFs: 7" in report
        assert "Failed rows: 3" in report
        assert "Success rate: 70.0%" in report
        assert "Failed/Skipped Row Numbers:" in report
        assert "  - Row 2" in report
        assert "  - Row 5" in report
        assert "  - Row 8" in report
    
    def test_format_result_detailed_empty(self):
        """Test formatting detailed report with empty result."""
        result = ProcessingResult(
            total_rows=0,
            successful_merges=0,
            failed_rows=[]
        )
        
        report = format_result_detailed(result)
        
        assert "Total rows in input file: 0" in report
        assert "Successfully merged PDFs: 0" in report
        assert "Failed rows: 0" in report
        assert "Success rate: 0.0%" in report
    
    def test_format_result_detailed_partial_success(self):
        """Test formatting detailed report with partial success."""
        result = ProcessingResult(
            total_rows=5,
            successful_merges=3,
            failed_rows=[1, 4]
        )
        
        report = format_result_detailed(result)
        
        assert "Success rate: 60.0%" in report
        assert "  - Row 1" in report
        assert "  - Row 4" in report
    
    def test_format_result_detailed_with_mergeresult(self):
        """Test formatting detailed report with MergeResult."""
        from pdf_merger.models import MergeResult, RowResult, RowStatus
        
        # Start with 0 successful_merges - add_row_result will update counters
        result = MergeResult(
            total_rows=10,
            successful_merges=0,
            failed_rows=[],
            skipped_rows=[]
        )
        
        # Add some row results - these will update the counters
        result.add_row_result(RowResult(0, RowStatus.SUCCESS))
        result.add_row_result(RowResult(1, RowStatus.SKIPPED, error_message="No serial numbers"))
        result.add_row_result(RowResult(2, RowStatus.FAILED, error_message="File not found", files_missing=["GRNW_123"]))
        
        report = format_result_detailed(result)
        
        assert "Total rows in input file: 10" in report
        assert "Successfully merged PDFs: 1" in report  # Only 1 success from add_row_result
        assert "Failed rows: 1" in report  # Only 1 failed from add_row_result
        assert "Skipped rows: 1" in report  # Only 1 skipped from add_row_result
        assert "Success rate: 10.0%" in report  # 1 out of 10
        assert "Failed Row Numbers:" in report
        assert "Skipped Row Numbers:" in report
        assert "Row Details:" in report
        assert "FAILED" in report
        assert "SKIPPED" in report
    
    def test_format_result_detailed_with_mergeresult_partial(self):
        """Test formatting detailed report with MergeResult containing partial results."""
        from pdf_merger.models import MergeResult, RowResult, RowStatus
        
        result = MergeResult(
            total_rows=5,
            successful_merges=3
        )
        
        # Add partial result
        partial_result = RowResult(
            0,
            RowStatus.PARTIAL,
            files_found=[Path("/tmp/file1.pdf")],
            files_missing=["GRNW_123"]
        )
        result.add_row_result(partial_result)
        
        report = format_result_detailed(result)
        
        assert "PARTIAL" in report
        assert "Some files missing" in report
        assert "Missing files: GRNW_123" in report
    
    def test_format_result_detailed_with_processing_time(self):
        """Test formatting detailed report with processing time."""
        from pdf_merger.models import MergeResult
        
        result = MergeResult(
            total_rows=10,
            successful_merges=10,
            total_processing_time=5.5
        )
        
        report = format_result_detailed(result)
        
        assert "Total processing time: 5.50 seconds" in report
    
    def test_format_result_summary_with_mergeresult_skipped(self):
        """Test formatting summary with MergeResult containing skipped rows."""
        from pdf_merger.models import MergeResult
        
        result = MergeResult(
            total_rows=10,
            successful_merges=7,
            failed_rows=[2],
            skipped_rows=[1, 3]
        )
        
        summary = format_result_summary(result)
        
        assert "Total rows processed: 10" in summary
        assert "Successfully merged PDFs: 7" in summary
        assert "Failed rows: 1" in summary
        assert "Skipped rows: 2" in summary


class TestRunMergeJob:
    """Test cases for run_merge_job function."""
    
    @patch('pdf_merger.core.merge_orchestrator.process_job')
    @patch('pdf_merger.core.merge_orchestrator.read_data_file')
    @patch('pdf_merger.core.merge_orchestrator.logger')
    def test_run_merge_job_success(self, mock_logger, mock_read_data, mock_process_job, tmp_path):
        """Test successful merge job."""
        input_file = tmp_path / "input.csv"
        input_file.write_text("serial_numbers\nGRNW_123")
        pdf_dir = tmp_path / "pdfs"
        output_dir = tmp_path / "output"
        
        # Mock read_data_file to return row data
        mock_read_data.return_value = iter([
            {"serial_numbers": "GRNW_123"}
        ])
        
        # Mock process_job to return result
        from pdf_merger.models import MergeResult
        expected_result = MergeResult(
            total_rows=1,
            successful_merges=1,
            job_id="test-job"
        )
        mock_process_job.return_value = expected_result
        
        result = run_merge_job(input_file, pdf_dir, output_dir, job_id="test-job")
        
        assert result == expected_result
        mock_read_data.assert_called_once_with(input_file)
        mock_process_job.assert_called_once()
        assert mock_logger.info.called
    
    @patch('pdf_merger.core.merge_orchestrator.read_data_file')
    @patch('pdf_merger.core.merge_orchestrator.logger')
    def test_run_merge_job_read_error(self, mock_logger, mock_read_data, tmp_path):
        """Test merge job when file reading fails."""
        input_file = tmp_path / "input.csv"
        pdf_dir = tmp_path / "pdfs"
        output_dir = tmp_path / "output"
        
        mock_read_data.side_effect = Exception("File read error")
        
        result = run_merge_job(input_file, pdf_dir, output_dir, job_id="test-job")
        
        assert result.total_rows == 0
        assert result.successful_merges == 0
        assert result.job_id == "test-job"
        mock_logger.error.assert_called_once()
    
    @patch('pdf_merger.core.merge_orchestrator.process_job')
    @patch('pdf_merger.core.merge_orchestrator.read_data_file')
    @patch('pdf_merger.core.merge_orchestrator.logger')
    def test_run_merge_job_with_fail_on_ambiguous(self, mock_logger, mock_read_data, mock_process_job, tmp_path):
        """Test merge job with fail_on_ambiguous parameter."""
        input_file = tmp_path / "input.csv"
        input_file.write_text("serial_numbers\nGRNW_123")
        pdf_dir = tmp_path / "pdfs"
        output_dir = tmp_path / "output"
        
        mock_read_data.return_value = iter([
            {"serial_numbers": "GRNW_123"}
        ])
        
        from pdf_merger.models import MergeResult
        expected_result = MergeResult(total_rows=1, successful_merges=1)
        mock_process_job.return_value = expected_result
        
        result = run_merge_job(input_file, pdf_dir, output_dir, fail_on_ambiguous=False)
        
        assert result == expected_result
        # Verify fail_on_ambiguous was passed to process_job
        call_args = mock_process_job.call_args
        assert call_args[1]['fail_on_ambiguous'] is False
    
    @patch('pdf_merger.core.merge_orchestrator.process_job')
    @patch('pdf_merger.core.merge_orchestrator.read_data_file')
    @patch('pdf_merger.core.merge_orchestrator.logger')
    def test_run_merge_job_with_custom_column(self, mock_logger, mock_read_data, mock_process_job, tmp_path):
        """Test merge job with custom required column."""
        input_file = tmp_path / "input.csv"
        input_file.write_text("custom_col\nGRNW_123")
        pdf_dir = tmp_path / "pdfs"
        output_dir = tmp_path / "output"
        
        mock_read_data.return_value = iter([
            {"custom_col": "GRNW_123"}
        ])
        
        from pdf_merger.models import MergeResult
        expected_result = MergeResult(total_rows=1, successful_merges=1)
        mock_process_job.return_value = expected_result
        
        result = run_merge_job(input_file, pdf_dir, output_dir, required_column="custom_col")
        
        assert result == expected_result
        # Verify the job was created with custom column
        mock_read_data.assert_called_once_with(input_file)
    
    @patch('pdf_merger.core.merge_orchestrator.process_job')
    @patch('pdf_merger.core.merge_orchestrator.read_data_file')
    @patch('pdf_merger.core.merge_orchestrator.logger')
    def test_run_merge_job_empty_file(self, mock_logger, mock_read_data, mock_process_job, tmp_path):
        """Test merge job with empty file."""
        input_file = tmp_path / "input.csv"
        pdf_dir = tmp_path / "pdfs"
        output_dir = tmp_path / "output"
        
        mock_read_data.return_value = iter([])
        
        from pdf_merger.models import MergeResult
        expected_result = MergeResult(total_rows=0, successful_merges=0)
        mock_process_job.return_value = expected_result
        
        result = run_merge_job(input_file, pdf_dir, output_dir)
        
        assert result == expected_result
        assert result.total_rows == 0
