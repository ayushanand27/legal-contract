from __future__ import annotations

from dataclasses import dataclass

from core.chunking import TextChunk, chunk_contract_text
from core.embeddings import embed_texts
from core.extraction import extract_document_pages
from core.supabase_client import get_supabase


@dataclass
class DocumentRecord:
    id: str
    name: str
    source: str | None
    file_type: str | None


def list_documents() -> list[DocumentRecord]:
    sb = get_supabase()
    rows = sb.table("documents").select("id,name,source,file_type").order("created_at", desc=True).execute().data or []
    return [DocumentRecord(**row) for row in rows]


def delete_document(document_id: str) -> None:
    sb = get_supabase()
    sb.table("documents").delete().eq("id", document_id).execute()


def ingest_plain_text(
    *,
    name: str,
    text: str,
    source: str = "upload",
    file_type: str = "text",
    extra_metadata: dict | None = None,
) -> str:
    pages = [{"page": 1, "text": text}]
    return _ingest_pages(name=name, pages=pages, source=source, file_type=file_type, extra_metadata=extra_metadata)


def ingest_uploaded_file(filename: str, file_bytes: bytes, source: str = "upload") -> str:
    pages = extract_document_pages(filename, file_bytes)
    if not pages:
        raise ValueError(f"No extractable text found in {filename}")
    ext = filename.rsplit(".", 1)[-1].lower()
    return _ingest_pages(name=filename, pages=pages, source=source, file_type=ext)


def _ingest_pages(
    *,
    name: str,
    pages: list[dict],
    source: str,
    file_type: str,
    extra_metadata: dict | None = None,
) -> str:
    sb = get_supabase()
    doc_row = (
        sb.table("documents")
        .insert(
            {
                "name": name,
                "source": source,
                "file_type": file_type,
                "metadata": extra_metadata or {},
            }
        )
        .execute()
        .data[0]
    )
    document_id = doc_row["id"]

    all_chunks: list[TextChunk] = []
    global_index = 0
    for page in pages:
        page_chunks = chunk_contract_text(page["text"], page_no=page.get("page"))
        for ch in page_chunks:
            ch.chunk_index = global_index
            global_index += 1
            all_chunks.append(ch)

    if not all_chunks:
        raise ValueError(f"No chunks produced for {name}")

    texts = [c.chunk_text for c in all_chunks]
    vectors = embed_texts(texts)

    batch_size = 50
    for start in range(0, len(all_chunks), batch_size):
        batch_chunks = all_chunks[start : start + batch_size]
        batch_vectors = vectors[start : start + batch_size]
        rows = []
        for ch, vector in zip(batch_chunks, batch_vectors):
            rows.append(
                {
                    "document_id": document_id,
                    "chunk_index": ch.chunk_index,
                    "page_no": ch.page_no,
                    "chunk_text": ch.chunk_text,
                    "metadata": {
                        "document_id": document_id,
                        "document_name": name,
                        "chunk_id": ch.chunk_index,
                        "page_no": ch.page_no,
                        **(ch.metadata or {}),
                    },
                    "embedding": vector,
                }
            )
        sb.table("chunks").insert(rows).execute()

    return document_id
