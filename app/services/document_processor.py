import os
from typing import Optional

import PyPDF2
import docx

def extract_text_from_file(file_path: str, original_filename: str) -> str:
    """
    Extract text from a PDF or DOCX file.
    Args:
        file_path (str): The path to the file on disk.
        original_filename (str): The original filename (for logging or future use).
    Returns:
        str: The extracted text.
    Raises:
        ValueError: If the file type is unsupported or extraction fails.
    """
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    try:
        if ext == ".pdf":
            return _extract_text_from_pdf(file_path)
        elif ext == ".docx":
            return _extract_text_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type for '{original_filename}': {ext}")
    except Exception as e:
        raise ValueError(f"Failed to extract text from '{original_filename}': {e}")

def _extract_text_from_pdf(file_path: str) -> str:
    text = []
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
    except Exception as e:
        raise ValueError(f"Error reading PDF file: {e}")
    return "\n".join(text)

def _extract_text_from_docx(file_path: str) -> str:
    text = []
    try:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            if para.text:
                text.append(para.text)
    except Exception as e:
        raise ValueError(f"Error reading DOCX file: {e}")
    return "\n".join(text) 