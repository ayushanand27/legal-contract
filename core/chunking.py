import re
from dataclasses import dataclass

import config

SECTION_PATTERN = re.compile(
    r"(?m)^(?:\d+(?:\.\d+)*\.?\s+|[A-Z][A-Z0-9 \-/&]{3,}\s*$|ARTICLE\s+[IVXLC\d]+|SECTION\s+\d+)"
)


@dataclass
class TextChunk:
    chunk_index: int
    chunk_text: str
    page_no: int | None = None
    metadata: dict | None = None


def _word_chunks(text: str, chunk_size: int, overlap: int) -> list[str]:
    words = text.split()
    if not words:
        return []
    chunks: list[str] = []
    step = max(chunk_size - overlap, 1)
    for i in range(0, len(words), step):
        piece = " ".join(words[i : i + chunk_size]).strip()
        if piece:
            chunks.append(piece)
    return chunks


def chunk_contract_text(
    text: str,
    *,
    chunk_size: int | None = None,
    overlap: int | None = None,
    page_no: int | None = None,
) -> list[TextChunk]:
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []

    sections = SECTION_PATTERN.split(text)
    section_texts = [s.strip() for s in sections if s and s.strip()]
    if len(section_texts) <= 1:
        section_texts = [text]

    raw_chunks: list[str] = []
    for section in section_texts:
        if len(section.split()) <= chunk_size:
            raw_chunks.append(section)
        else:
            raw_chunks.extend(_word_chunks(section, chunk_size, overlap))

    result: list[TextChunk] = []
    for idx, chunk_text in enumerate(raw_chunks):
        result.append(
            TextChunk(
                chunk_index=idx,
                chunk_text=chunk_text,
                page_no=page_no,
                metadata={"strategy": "section_aware"},
            )
        )
    return result
