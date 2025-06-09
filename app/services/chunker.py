from typing import List, Dict
import re
from app.utils.logger import ColorLogger as log

def extract_section_info(text: str) -> Dict[str, str]:
    """
    Extract section number and title from text if present.
    """
    section_pattern = r'^(?:Section|SECTION|Art\.|ARTICLE)\s*([\d\.]+)\s*[:\-]?\s*(.+)?$'
    match = re.match(section_pattern, text.strip())
    if match:
        section_info = {
            'section_number': match.group(1),
            'section_title': match.group(2).strip() if match.group(2) else ''
        }
        log.info(f"📑 Found section {section_info['section_number']}: {section_info['section_title']}")
        return section_info
    return None

def chunk_text(pages: List[str], max_tokens: int = 800) -> List[Dict[str, str]]:
    """
    Chunk the list of page texts into smaller chunks under max_tokens while preserving context.
    Approx: 1 token = 4 characters (rough).
    Returns list of dicts with chunk text and metadata.
    """
    log.info(f"🔄 Starting document chunking process - {len(pages)} pages to process")
    chunks = []
    current_chunk = ""
    current_section = {'number': '', 'title': ''}
    current_page = 0
    total_chars = 0

    for page_num, page in enumerate(pages, 1):
        log.processing(f"Processing page {page_num}/{len(pages)}", indent=1)
        paragraphs = [p for p in page.split("\n") if p.strip()]
        total_chars += len(page)
        
        for paragraph in paragraphs:
            # Check if this is a section header
            section_info = extract_section_info(paragraph)
            if section_info:
                current_section = {
                    'number': section_info['section_number'],
                    'title': section_info['section_title']
                }
                
            # Check if adding this paragraph would exceed the token limit
            if len(current_chunk) + len(paragraph) < max_tokens * 4:
                current_chunk += paragraph + "\n"
            else:
                if current_chunk.strip():
                    chunk_data = {
                        'text': current_chunk.strip(),
                        'section_number': current_section['number'],
                        'section_title': current_section['title'],
                        'page_number': current_page,
                        'context': f"Page {current_page}, Section {current_section['number']}: {current_section['title']}"
                    }
                    chunks.append(chunk_data)
                    log.chunk(f"Created chunk {len(chunks)} ({len(current_chunk)} chars)", indent=2)
                current_chunk = paragraph + "\n"
                current_page = page_num

    # Add the last chunk if it exists
    if current_chunk.strip():
        chunk_data = {
            'text': current_chunk.strip(),
            'section_number': current_section['number'],
            'section_title': current_section['title'],
            'page_number': current_page,
            'context': f"Page {current_page}, Section {current_section['number']}: {current_section['title']}"
        }
        chunks.append(chunk_data)
        log.chunk(f"Created final chunk {len(chunks)} ({len(current_chunk)} chars)", indent=2)

    avg_chunk_size = total_chars / len(chunks) if chunks else 0
    log.success(f"✨ Chunking complete! Created {len(chunks)} chunks (avg {avg_chunk_size:.0f} chars per chunk)")
    return chunks