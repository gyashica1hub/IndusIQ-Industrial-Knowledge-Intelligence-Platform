"""
Document Ingestion Module
--------------------------
Handles PDF parsing, text/table extraction, and chunking for the RAG pipeline.
Designed to be extensible: add DOCX/scanned-image parsing later using the same
`ingest_file` interface.
"""

import pdfplumber
import re
import uuid
from pathlib import Path
from typing import List, Dict


def extract_text_from_pdf(file_path: str) -> List[Dict]:
    """
    Extracts text page-by-page from a PDF, keeping page numbers so we can
    cite the exact source page later (important for the "source citations"
    requirement in the problem statement).
    """
    pages = []
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            tables = page.extract_tables()
            table_text = ""
            for t in tables:
                for row in t:
                    row_clean = [c if c else "" for c in row]
                    table_text += " | ".join(row_clean) + "\n"
            full_text = text + "\n" + table_text
            if full_text.strip():
                pages.append({"page_number": i, "text": full_text.strip()})
    return pages


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> List[str]:
    """
    Splits text into overlapping chunks on sentence boundaries where possible.
    Overlap preserves context across chunk edges, which matters a lot for
    technical/maintenance documents where a spec spans multiple sentences.
    """
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current = ""
    for sentence in sentences:
        if len(current) + len(sentence) <= chunk_size:
            current += (" " if current else "") + sentence
        else:
            if current:
                chunks.append(current.strip())
            # start new chunk, carry over overlap from end of previous chunk
            overlap_text = current[-overlap:] if len(current) > overlap else current
            current = overlap_text + " " + sentence
    if current.strip():
        chunks.append(current.strip())
    return chunks


def ingest_file(file_path: str, doc_type: str = "general") -> List[Dict]:
    """
    Main entry point. Returns a list of chunk records ready for embedding:
    {id, doc_name, doc_type, page_number, chunk_text}
    """
    doc_name = Path(file_path).name
    pages = extract_text_from_pdf(file_path)

    records = []
    for page in pages:
        chunks = chunk_text(page["text"])
        for chunk in chunks:
            records.append({
                "id": str(uuid.uuid4()),
                "doc_name": doc_name,
                "doc_type": doc_type,
                "page_number": page["page_number"],
                "chunk_text": chunk,
            })
    return records
