"""Streamlit app for Legal Contract RAG chatbot."""

from __future__ import annotations

import streamlit as st

from core.chat import answer_question
from core.ingestion import delete_document, ingest_uploaded_file, list_documents
from ui.styles import CUSTOM_CSS

st.set_page_config(
    page_title="Legal Contract Intelligence",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_doc_ids" not in st.session_state:
    st.session_state.selected_doc_ids = []


def _refresh_documents():
    st.session_state.documents = list_documents()


if "documents" not in st.session_state:
    _refresh_documents()


def _short_name(name: str, max_len: int = 42) -> str:
    return name if len(name) <= max_len else name[: max_len - 3] + "..."


def _render_citations(citations: list[dict]) -> None:
    if not citations:
        return
    st.markdown('<div class="sources-label">Sources</div>', unsafe_allow_html=True)
    chips = []
    for c in citations:
        page = f" · p.{c['page_no']}" if c.get("page_no") else ""
        short = _short_name(c["document_name"], 50)
        chips.append(
            f'<span class="citation-chip" title="{c["document_name"]}">'
            f'📄 {short} · chunk {c["chunk_index"]}{page}</span>'
        )
    st.markdown(" ".join(chips), unsafe_allow_html=True)


def _scope_badge(selected_count: int, total: int) -> str:
    if selected_count == 0:
        return (
            f'<div class="scope-badge warn">🔍 Scope: All {total} documents '
            f'(answers may combine multiple contracts)</div>'
        )
    label = "document" if selected_count == 1 else "documents"
    return (
        f'<div class="scope-badge">🔍 Scope: {selected_count} selected {label}</div>'
    )


st.markdown('<div class="hero-title">Legal Contract Intelligence</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-subtitle">Grounded contract Q&amp;A with hybrid retrieval, '
    "reranking, and per-document scope control.</div>",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("### Corpus")
    uploaded_files = st.file_uploader(
        "Upload PDF / DOCX / TXT",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
    )
    if uploaded_files and st.button("Ingest uploaded files", use_container_width=True):
        with st.spinner("Extracting, chunking, embedding..."):
            for f in uploaded_files:
                try:
                    ingest_uploaded_file(f.name, f.getvalue())
                    st.success(f"Ingested {f.name}")
                except Exception as exc:
                    st.error(f"{f.name}: {exc}")
        _refresh_documents()

    docs = st.session_state.documents
    if docs:
        options = {d.name: d.id for d in docs}
        selected_names = st.multiselect(
            "Scope chat to documents",
            options=list(options.keys()),
            default=[],
            help="Leave empty to search all documents. Select one or more to restrict retrieval.",
        )
        st.session_state.selected_doc_ids = [options[n] for n in selected_names]

        st.markdown(
            _scope_badge(len(selected_names), len(docs)),
            unsafe_allow_html=True,
        )

        with st.expander(f"Manage documents ({len(docs)})", expanded=False):
            for d in docs:
                ftype = (d.file_type or "doc").upper()[:4]
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(
                        f'<div class="doc-card"><span class="doc-type">{ftype}</span>'
                        f"{_short_name(d.name, 55)}</div>",
                        unsafe_allow_html=True,
                    )
                with col2:
                    if st.button("Del", key=f"del_{d.id}"):
                        delete_document(d.id)
                        _refresh_documents()
                        st.rerun()
    else:
        st.info("No documents yet. Run `python scripts/seed_cuad.py` or upload files.")

    if st.button("Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

docs = st.session_state.get("documents", [])
selected_count = len(st.session_state.selected_doc_ids)
if docs:
    st.markdown(_scope_badge(selected_count, len(docs)), unsafe_allow_html=True)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        _render_citations(msg.get("citations") or [])

prompt = st.chat_input("Ask about termination, payment terms, liability...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Retrieving and analyzing..."):
            try:
                doc_ids = st.session_state.selected_doc_ids or None
                result = answer_question(prompt, document_ids=doc_ids)
                answer = result["answer"]
                citations = result["citations"]
            except Exception as exc:
                answer = f"Error: {exc}"
                citations = []

        st.markdown(answer)
        _render_citations(citations)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "citations": citations}
    )
