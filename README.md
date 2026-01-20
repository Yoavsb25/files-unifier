# PDF Merger from CSV/Excel Serial Numbers

A Python tool for merging PDF files based on filenames specified in CSV or Excel files. Each row in your data file produces one merged PDF document.

## Features

- ✅ **Multiple Input Formats**: Supports both CSV and Excel (.xlsx, .xls) files
- ✅ **Flexible File Matching**: Finds PDFs by filename with case-insensitive matching
- ✅ **Two Usage Modes**: Interactive prompts or command-line arguments
- ✅ **Modular Architecture**: Clean, maintainable code structure
- ✅ **Comprehensive Logging**: Detailed progress and error reporting
- ✅ **Error Handling**: Custom exceptions for better error messages
- ✅ **Library Support**: Can be imported and used as a Python package

## Requirements

- Python 3.6 or higher
- pypdf (for PDF operations)
- pandas and openpyxl (for Excel file support)

## Installation

1. Clone or download this repository

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

This will install:
- `pypdf` - PDF merging library
- `pandas` - Data manipulation (for Excel files)
- `openpyxl` - Excel file reading

## Usage

### Interactive Mode (Recommended for Beginners)

Simply run `main.py` without arguments:

```bash
python main.py
```

The script will prompt you for:
- CSV or Excel file path
- Folder containing PDF files
- Output folder path

Example session:
```
============================================================
PDF Merger - Interactive Mode
============================================================

Enter path to CSV or Excel file (.csv, .xlsx, .xls): data.xlsx
Enter path to folder containing PDF files: ./pdfs
Enter path to output folder (will be created if it doesn't exist): ./output

============================================================
Processing file...
============================================================
...
```

### Command-Line Mode

Run `main.py` with command-line arguments:

```bash
python main.py --csv <data_file> --folder <pdf_folder> --output <output_folder>
```

**Arguments:**
- `--csv`: Path to the CSV or Excel file (.csv, .xlsx, .xls) containing `serial_numbers` column
- `--folder`: Path to the folder containing PDF files to merge
- `--output`: Path to the output folder where merged PDFs will be saved

**Example:**
```bash
python main.py --csv data.csv --folder ./pdfs --output ./merged_output
```

**Alternative (backward compatibility):**
```bash
python -m cli.command_line --csv data.xlsx --folder ./pdfs --output ./output
```

## Data File Format

### Supported Formats
- **CSV files** (.csv) - Comma-separated or other delimiters (auto-detected)
- **Excel files** (.xlsx, .xls) - Standard Excel format

### Required Column
Your data file must contain a column named **`serial_numbers`** (case-sensitive).

### Data Format
Each row should contain comma-separated filenames (strings) that correspond to PDF files in your source folder.

**Example CSV:**
```csv
serial_numbers
ABC123,DEF456,GHI789
ABC123,XYZ999
document1,document2,document3
```

**Example Excel:**
| serial_numbers |
|----------------|
| ABC123,DEF456,GHI789 |
| ABC123,XYZ999 |
| document1,document2,document3 |

### Output
The above examples will create:
- `merged_row_1.pdf` - merges ABC123.pdf, DEF456.pdf, GHI789.pdf
- `merged_row_2.pdf` - merges ABC123.pdf, XYZ999.pdf
- `merged_row_3.pdf` - merges document1.pdf, document2.pdf, document3.pdf

## PDF File Naming

The script searches for PDF files matching the filenames specified in your data file. Each string in the `serial_numbers` column represents a unique filename.

**Matching Strategy:**
1. Exact match with `.pdf` extension (e.g., `ABC123.pdf`)
2. Exact match without extension (e.g., `ABC123`)
3. Case-insensitive match if exact match fails

**Examples:**
- Filename `ABC123` → looks for `ABC123.pdf` or `ABC123`
- Filename `document1.pdf` → looks for `document1.pdf`
- Filename `MyFile` → looks for `MyFile.pdf` or `MyFile` (case-insensitive)

## Output Files

Merged PDFs are saved in the output folder with sequential names:
- `merged_row_1.pdf` (first row)
- `merged_row_2.pdf` (second row)
- `merged_row_3.pdf` (third row)
- etc.

The script displays:
- Progress information for each row
- Found/missing files
- Success/failure status
- Final summary with statistics

## Using as a Python Library

You can import and use the PDF Merger as a library in your own Python code:

```python
from pdf_merger import process_file, ProcessingResult
from pathlib import Path

# Process a file
result: ProcessingResult = process_file(
    file_path=Path("data.csv"),
    source_folder=Path("./pdfs"),
    output_folder=Path("./output")
)

print(f"Processed {result.total_rows} rows")
print(f"Successfully merged {result.successful_merges} PDFs")
```

### Available Functions

**Main Processing:**
- `process_file()` - Process entire data file and merge PDFs
- `ProcessingResult` - Data class with processing statistics

**PDF Operations:**
- `find_pdf_file()` - Find a PDF file by filename
- `merge_pdfs()` - Merge multiple PDFs into one

**Data Parsing:**
- `parse_serial_numbers()` - Parse comma-separated filenames

**File Reading:**
- `read_data_file()` - Read CSV or Excel file (unified interface)
- `get_file_columns()` - Get column names from data file

**Validation:**
- `validate_file()` - Validate data file exists and has required column
- `validate_folder()` - Validate folder exists
- `validate_paths()` - Validate all paths needed for processing

**Exceptions:**
- `PDFMergerError` - Base exception
- `FileNotFoundError` - File/folder not found
- `InvalidFileFormatError` - Unsupported file format
- `MissingColumnError` - Required column missing
- `PDFProcessingError` - PDF operation failed
- `ValidationError` - Validation failure

## Project Structure

```
files_unifeder/
├── pdf_merger/          # Core business logic package
│   ├── __init__.py      # Public API exports
│   ├── processor.py     # Main processing orchestration
│   ├── pdf_operations.py # PDF finding and merging
│   ├── file_reader.py   # CSV/Excel reading
│   ├── data_parser.py   # Serial number parsing
│   ├── validators.py    # Path and file validation
│   ├── logger.py        # Logging configuration
│   └── exceptions.py    # Custom exceptions
├── cli/                 # User interface package
│   ├── __init__.py
│   ├── command_line.py  # CLI interface
│   └── interactive.py   # Interactive prompts
├── main.py              # Entry point (auto-detects mode)
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Error Handling

The tool provides detailed error messages:

- **Missing files**: Warns about missing PDFs but continues with available files
- **Invalid formats**: Clear error messages for unsupported file types
- **Missing columns**: Lists available columns if `serial_numbers` is missing
- **PDF errors**: Specific error messages for PDF reading/merging failures

All errors are logged and displayed to help you troubleshoot issues.

## Examples

### Example 1: Basic CSV Processing

```bash
python main.py --csv invoices.csv --folder ./documents --output ./merged_invoices
```

### Example 2: Excel File Processing

```bash
python main.py --csv data.xlsx --folder ./pdfs --output ./output
```

### Example 3: Interactive Mode

```bash
python main.py
# Follow the prompts
```

### Example 4: Using as Library

```python
from pdf_merger import process_file, validate_paths
from pathlib import Path

# Validate first
is_valid, _ = validate_paths(
    Path("data.csv"),
    Path("./pdfs"),
    Path("./output")
)

if is_valid:
    result = process_file(
        Path("data.csv"),
        Path("./pdfs"),
        Path("./output")
    )
    print(f"Success: {result.successful_merges}/{result.total_rows}")
```

## Troubleshooting

### "pandas and openpyxl are required"
**Solution:** Install missing dependencies:
```bash
pip install pandas openpyxl
```

### "serial_numbers column not found"
**Solution:** Ensure your CSV/Excel file has a column header exactly named `serial_numbers` (case-sensitive).

### "PDF file not found"
**Solution:** 
- Check that PDF files exist in the source folder
- Verify filenames match exactly (case-insensitive)
- Ensure PDF files have `.pdf` extension

### "Error reading file"
**Solution:**
- Verify file is not corrupted
- Check file permissions
- Ensure file is a valid CSV or Excel format

## License

This project is open source and available for use.

## Contributing

Contributions are welcome! Please ensure:
- Code follows the existing style
- All tests pass
- Documentation is updated

## Version

Current version: 1.0.0
