# What’s happening?
# fitz.open() loads the PDF from raw bytes.
# We loop through all pages and extract text.
# Returns list of page-wise strings — easy to chunk later.

import fitz
from typing import List

def extract_text_from_pdf(file_bytes: bytes) -> List[str]:
    """
    Extract text from PDF bytes. Return list of text per page.
    """
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    pages = [page.get_text() for page in doc]
    doc.close()
    return pages

