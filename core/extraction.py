from pathlib import Path


def extract_text_from_pdf(file_bytes: bytes) -> list[dict]:
    import fitz

    doc = fitz.open(stream=file_bytes, filetype="pdf")
    pages: list[dict] = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = (page.get_text("text") or "").strip()
        if text:
            pages.append({"page": page_num + 1, "text": text})
    doc.close()
    return pages


def extract_text_from_docx(file_bytes: bytes) -> list[dict]:
    import io

    from docx import Document

    doc = Document(io.BytesIO(file_bytes))
    text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    return [{"page": 1, "text": text}] if text else []


def extract_text_from_txt(file_bytes: bytes) -> list[dict]:
    text = file_bytes.decode("utf-8", errors="ignore").strip()
    return [{"page": 1, "text": text}] if text else []


def extract_document_pages(filename: str, file_bytes: bytes) -> list[dict]:
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_bytes)
    if ext == ".docx":
        return extract_text_from_docx(file_bytes)
    if ext in {".txt", ".md"}:
        return extract_text_from_txt(file_bytes)
    raise ValueError(f"Unsupported file type: {ext}")
