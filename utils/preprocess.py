import re
from typing import List

def clean_text(text: str) -> str:
    """
    Basic cleaning: remove extra whitespace, special characters, newlines.
    """
    text = re.sub(r'\s+', ' ', text)  # remove excessive whitespace/newlines
    text = re.sub(r'\u00a0', ' ', text)  # non-breaking spaces
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # remove non-ASCII chars
    return text.strip()

def chunk_text(text: str, max_chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """
    Split text into overlapping chunks.
    """
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = words[i:i+max_chunk_size]
        chunks.append(" ".join(chunk))
        i += max_chunk_size - overlap
    return chunks
