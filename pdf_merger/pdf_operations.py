"""
PDF operations module.
Handles finding and merging PDF files.
"""

import sys
from pathlib import Path
from typing import List, Optional

try:
    from pypdf import PdfWriter, PdfReader
except ImportError:
    try:
        from PyPDF2 import PdfWriter, PdfReader
    except ImportError:
        print("Error: pypdf or PyPDF2 library is required. Install with: pip install pypdf")
        sys.exit(1)


def find_pdf_file(folder: Path, filename: str) -> Optional[Path]:
    """
    Find a PDF file matching the filename in the given folder.
    
    Args:
        folder: Path to the folder containing PDF files
        filename: Filename (with or without .pdf extension) to search for
        
    Returns:
        Path to the PDF file if found, None otherwise
    """
    # If filename already has .pdf extension, try that first
    if filename.lower().endswith('.pdf'):
        pdf_path = folder / filename
        if pdf_path.exists():
            return pdf_path
    
    # Try with .pdf extension appended
    pdf_path = folder / f"{filename}.pdf"
    if pdf_path.exists():
        return pdf_path
    
    # Try case-insensitive search (exact filename match)
    filename_lower = filename.lower()
    for pdf_file in folder.glob("*.pdf"):
        if pdf_file.name.lower() == filename_lower or pdf_file.name.lower() == f"{filename_lower}.pdf":
            return pdf_file
        # Also try matching just the stem (filename without extension)
        if pdf_file.stem.lower() == filename_lower:
            return pdf_file
    
    return None


def merge_pdfs(pdf_paths: List[Path], output_path: Path) -> bool:
    """
    Merge multiple PDF files into a single PDF.
    
    Args:
        pdf_paths: List of paths to PDF files to merge
        output_path: Path where the merged PDF will be saved
        
    Returns:
        True if successful, False otherwise
    """
    if not pdf_paths:
        print(f"Warning: No PDF files to merge for {output_path.name}")
        return False
    
    try:
        writer = PdfWriter()
        
        for pdf_path in pdf_paths:
            try:
                reader = PdfReader(str(pdf_path))
                # Add all pages from this PDF
                for page in reader.pages:
                    writer.add_page(page)
            except Exception as e:
                print(f"Error reading PDF {pdf_path.name}: {e}")
                return False
        
        # Write the merged PDF
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        return True
    except Exception as e:
        print(f"Error merging PDFs to {output_path.name}: {e}")
        return False
