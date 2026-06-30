from __future__ import annotations

from dataclasses import dataclass

import cohere

import config
from core.embeddings import embed_query
from core.supabase_client import get_supabase


@dataclass
class RetrievedChunk:
    id: str
    document_id: str
    document_name: str
    chunk_index: int
    page_no: int | None
    chunk_text: str
    score: float
    source: str


def _rrf_fuse(
    ranked_lists: list[list[str]],
    *,
    k: int | None = None,
) -> dict[str, float]:
    k = k or config.HYBRID_RRF_K
    scores: dict[str, float] = {}
    for results in ranked_lists:
        for rank, chunk_id in enumerate(results, start=1):
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (k + rank)
    return scores


def _vector_search(query_embedding: list[float], document_ids: list[str] | None, top_k: int) -> list[dict]:
    sb = get_supabase()
    payload = {
        "query_embedding": query_embedding,
        "match_count": top_k,
        "filter_document_ids": document_ids,
    }
    return sb.rpc("match_chunks_vector", payload).execute().data or []


def _fts_search(query: str, document_ids: list[str] | None, top_k: int) -> list[dict]:
    sb = get_supabase()
    payload = {
        "search_query": query,
        "match_count": top_k,
        "filter_document_ids": document_ids,
    }
    return sb.rpc("match_chunks_fts", payload).execute().data or []


def _cohere_rerank(query: str, chunks: list[RetrievedChunk], top_k: int) -> list[RetrievedChunk]:
    if not chunks:
        return []
    if not config.COHERE_API_KEY:
        return chunks[:top_k]

    client = cohere.ClientV2(api_key=config.COHERE_API_KEY)
    docs = [c.chunk_text for c in chunks]
    response = client.rerank(
        model="rerank-english-v3.0",
        query=query,
        documents=docs,
        top_n=min(top_k, len(docs)),
    )
    reranked: list[RetrievedChunk] = []
    for item in response.results:
        base = chunks[item.index]
        reranked.append(
            RetrievedChunk(
                id=base.id,
                document_id=base.document_id,
                document_name=base.document_name,
                chunk_index=base.chunk_index,
                page_no=base.page_no,
                chunk_text=base.chunk_text,
                score=float(item.relevance_score),
                source=base.source,
            )
        )
    return reranked


def retrieve_chunks(query: str, document_ids: list[str] | None = None) -> list[RetrievedChunk]:
    """Hybrid retrieval: vector + BM25/FTS, RRF fusion, then Cohere rerank."""
    filter_ids = document_ids if document_ids else None
    top_k = config.RETRIEVAL_TOP_K

    query_embedding = embed_query(query)
    vector_rows = _vector_search(query_embedding, filter_ids, top_k)
    fts_rows = _fts_search(query, filter_ids, top_k)

    vector_ids = [row["id"] for row in vector_rows]
    fts_ids = [row["id"] for row in fts_rows]
    fused_scores = _rrf_fuse([vector_ids, fts_ids])

    by_id: dict[str, dict] = {}
    for row in vector_rows + fts_rows:
        by_id[row["id"]] = row

    fused_rows = sorted(by_id.values(), key=lambda r: fused_scores.get(r["id"], 0.0), reverse=True)
    candidates: list[RetrievedChunk] = []
    for row in fused_rows[:top_k]:
        candidates.append(
            RetrievedChunk(
                id=row["id"],
                document_id=row["document_id"],
                document_name=row["document_name"],
                chunk_index=row["chunk_index"],
                page_no=row.get("page_no"),
                chunk_text=row["chunk_text"],
                score=fused_scores.get(row["id"], 0.0),
                source="hybrid",
            )
        )

    return _cohere_rerank(query, candidates, config.RERANK_TOP_K)
