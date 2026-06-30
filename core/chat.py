from __future__ import annotations

import re
import time

from groq import Groq

import config
from core.retrieval import RetrievedChunk, retrieve_chunks

_INLINE_CITATION_RE = re.compile(r"\s*\[Source:[^\]]+\]", re.IGNORECASE)


def _format_context(chunks: list[RetrievedChunk]) -> str:
    blocks = []
    for i, ch in enumerate(chunks, start=1):
        page = f", page {ch.page_no}" if ch.page_no else ""
        blocks.append(
            f"[Excerpt {i}: {ch.document_name}, chunk {ch.chunk_index}{page}]\n{ch.chunk_text}"
        )
    return "\n\n---\n\n".join(blocks)


def _call_groq(system_prompt: str, user_prompt: str) -> str:
    client = Groq(api_key=config.GROQ_API_KEY)
    max_retries = 4
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=config.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0,
                max_tokens=1200,
            )
            return response.choices[0].message.content or ""
        except Exception as exc:
            last_error = exc
            wait_match = re.search(r"try again in (\d+(?:\.\d+)?)s", str(exc))
            if attempt < max_retries:
                time.sleep(float(wait_match.group(1)) + 1 if wait_match else 2)
    raise RuntimeError(f"Groq failed after retries: {last_error}")


def _clean_answer(text: str) -> str:
    """Remove inline citation clutter; UI shows sources separately."""
    cleaned = _INLINE_CITATION_RE.sub("", text)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def _build_citations(chunks: list[RetrievedChunk]) -> list[dict]:
    seen: set[tuple[str, int]] = set()
    citations: list[dict] = []
    for ch in chunks:
        key = (ch.document_name, ch.chunk_index)
        if key in seen:
            continue
        seen.add(key)
        citations.append(
            {
                "document_name": ch.document_name,
                "chunk_index": ch.chunk_index,
                "page_no": ch.page_no,
                "preview": ch.chunk_text[:220] + ("..." if len(ch.chunk_text) > 220 else ""),
            }
        )
        if len(citations) >= config.MAX_CITATIONS:
            break
    return citations


def answer_question(query: str, document_ids: list[str] | None = None) -> dict:
    chunks = retrieve_chunks(query, document_ids=document_ids)
    if not chunks:
        return {
            "answer": "Not applicable — the selected document(s) do not contain sufficient information to answer this question.",
            "chunks": [],
            "citations": [],
        }

    scope_hint = (
        "The user scoped the search to specific document(s) only. Answer using only those excerpts."
        if document_ids
        else "The user is searching across ALL documents. Group your answer by contract when multiple contracts are relevant."
    )

    context = _format_context(chunks)
    user_prompt = f"""Question:
{query}

Scope: {scope_hint}

Contract excerpts:
{context}

Write a clear, well-structured answer. Do not include [Source: ...] tags in the answer."""
    raw_answer = _call_groq(config.CHAT_SYSTEM_PROMPT, user_prompt)
    answer = _clean_answer(raw_answer)
    citations = _build_citations(chunks)

    return {"answer": answer, "chunks": chunks, "citations": citations}
