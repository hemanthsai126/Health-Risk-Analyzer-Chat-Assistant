"""Utility for extracting text from uploaded PDF files."""
import pdfplumber
from typing import List, Union
from io import BytesIO

def extract_text(files: List[Union[BytesIO, str]]) -> str:
    """Extract concatenated text from uploaded PDFs.

    Args:
        files: List of PDF files as file-like objects or file paths.

    Returns:
        Concatenated text from all PDFs, or empty string if none.
    """
    if not files:
        return ""

    all_text = []
    for file in files:
        try:
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages:
                    text = page.extract_text() or ""
                    all_text.append(text)
        except Exception as e:
            all_text.append(f"\n[Error reading PDF: {e}]")

    return "\n\n".join(all_text)
