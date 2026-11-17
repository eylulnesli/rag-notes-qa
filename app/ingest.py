"""PDF -> cleaned text -> overlapping chunks with source/page metadata."""
import re
from pathlib import Path
from pypdf import PdfReader
from .config import DOCS_DIR, CHUNK_CHARS, CHUNK_OVERLAP


def clean(text: str) -> str:
    lines = [l.strip() for l in text.splitlines() if "McGraw-Hill" not in l]  # slide footer noise
    return re.sub(r"[ \t]+", " ", "\n".join(l for l in lines if l)).strip()


def split(text: str, size: int = CHUNK_CHARS, overlap: int = CHUNK_OVERLAP):
    if len(text) <= size:
        return [text]
    parts, i = [], 0
    while i < len(text):
        parts.append(text[i:i + size])
        i += size - overlap
    return parts


def load_chunks(docs_dir: Path = DOCS_DIR):
    chunks = []
    for pdf in sorted(Path(docs_dir).glob("*.pdf")):
        for page_no, page in enumerate(PdfReader(str(pdf)).pages, 1):
            text = clean(page.extract_text() or "")
            if len(text) < 40:  # title slides, empty pages
                continue
            for part in split(text):
                chunks.append({"id": len(chunks), "source": pdf.name, "page": page_no, "text": part})
    return chunks
