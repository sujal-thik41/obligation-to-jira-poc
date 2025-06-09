import fitz
from typing import List, Dict, Any
import io
import docx
from app.utils.logger import ColorLogger as log

def extract_text_from_pdf(file_bytes: bytes) -> List[str]:
    """
    Extract text from PDF bytes. Return list of text per page.
    
    Args:
        file_bytes: Raw bytes of the PDF file
        
    Returns:
        List of text content per page
    """
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        pages = [page.get_text() for page in doc]
        doc.close()
        return pages
    except Exception as e:
        log.error(f"Error extracting text from PDF: {str(e)}")
        return []

def extract_text_from_docx(file_bytes: bytes) -> List[str]:
    """
    Extract text from DOCX bytes. Return list of text per paragraph.
    
    Args:
        file_bytes: Raw bytes of the DOCX file
        
    Returns:
        List of text content per paragraph
    """
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
        
        # Group paragraphs into "pages" (roughly 3000 characters per page)
        pages = []
        current_page = ""
        char_count = 0
        
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue
                
            if char_count + len(text) > 3000:
                pages.append(current_page)
                current_page = text + "\n"
                char_count = len(text)
            else:
                current_page += text + "\n"
                char_count += len(text)
                
        # Add the last page if it's not empty
        if current_page:
            pages.append(current_page)
            
        return pages
    except Exception as e:
        log.error(f"Error extracting text from DOCX: {str(e)}")
        return []

def extract_text_from_document(file_bytes: bytes, content_type: str) -> List[str]:
    """
    Extract text from document bytes based on content type.
    
    Args:
        file_bytes: Raw bytes of the document file
        content_type: MIME type of the document
        
    Returns:
        List of text content
    """
    if content_type == "application/pdf":
        return extract_text_from_pdf(file_bytes)
    elif content_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/docx"]:
        return extract_text_from_docx(file_bytes)
    else:
        log.error(f"Unsupported document type: {content_type}")
        return []
