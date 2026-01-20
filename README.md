# PDF Merger from CSV Serial Numbers

This script merges PDF files based on serial numbers specified in a CSV file. Each row in the CSV produces one merged PDF document.

## Requirements

- Python 3.6 or higher
- pypdf library

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the script with the following command:

```bash
python merge_pdfs.py --csv <csv_file> --folder <pdf_folder> --output <output_folder>
```

### Arguments

- `--csv`: Path to the CSV file containing the `serial_numbers` column
- `--folder`: Path to the folder containing the PDF files to merge
- `--output`: Path to the output folder where merged PDFs will be saved

### Example

```bash
python merge_pdfs.py --csv data.csv --folder ./pdfs --output ./merged_output
```

## CSV Format

The CSV file must contain a column named `serial_numbers`. Each row should contain comma-separated serial numbers that correspond to PDF filenames.

### Example CSV

```csv
serial_numbers
1,2,3,6
1,2,6
4,5,7
```

This will create:
- `merged_row_1.pdf` - merges 1.pdf, 2.pdf, 3.pdf, 6.pdf
- `merged_row_2.pdf` - merges 1.pdf, 2.pdf, 6.pdf
- `merged_row_3.pdf` - merges 4.pdf, 5.pdf, 7.pdf

## PDF File Naming

The script looks for PDF files named exactly as the serial number with a `.pdf` extension. For example:
- Serial number `1` → looks for `1.pdf`
- Serial number `123` → looks for `123.pdf`

## Output

Merged PDFs are saved in the output folder with names like:
- `merged_row_1.pdf`
- `merged_row_2.pdf`
- `merged_row_3.pdf`
- etc.

The script will display progress information and a summary when complete.
