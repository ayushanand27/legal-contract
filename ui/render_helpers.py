"""UI rendering helpers for chat answers and citations."""

from __future__ import annotations

import html
import re

import streamlit as st

_CONTRACT_SPLIT_RE = re.compile(
    r"(?=\n(?:\*\*Contract:|\*\*Document:|###\s+Contract:))",
    re.IGNORECASE,
)


def short_name(name: str, max_len: int = 42) -> str:
    return name if len(name) <= max_len else name[: max_len - 3] + "..."


def scope_badge_html(selected_count: int, total: int) -> str:
    if selected_count == 0:
        return (
            f'<div class="scope-badge warn">🔍 Scope: All {total} documents '
            f"(answers may combine multiple contracts)</div>"
        )
    label = "document" if selected_count == 1 else "documents"
    return (
        f'<div class="scope-badge">🔍 Scope: {selected_count} selected {label}</div>'
    )


def _escape(text: str) -> str:
    return html.escape(text)


def render_answer_cards(answer: str) -> None:
    """Split multi-contract answers into visual cards."""
    parts = _CONTRACT_SPLIT_RE.split(answer.strip())
    if len(parts) <= 1:
        st.markdown(answer)
        return

    for part in parts:
        part = part.strip()
        if not part:
            continue
        title_match = re.match(
            r"^(?:\*\*Contract:|\*\*Document:|###\s+Contract:)\s*(.+?)\*\*\s*\n?",
            part,
            re.IGNORECASE | re.DOTALL,
        )
        if title_match:
            title = title_match.group(1).strip().rstrip("*")
            body = part[title_match.end() :].strip()
            st.markdown(
                f'<div class="answer-card">'
                f'<div class="answer-card-title">📄 {_escape(short_name(title, 60))}</div>'
                f"</div>",
                unsafe_allow_html=True,
            )
            if body:
                st.markdown(body)
        else:
            st.markdown(part)


def render_citations(citations: list[dict]) -> None:
    if not citations:
        return

    chips = []
    for c in citations:
        page = f" · p.{c['page_no']}" if c.get("page_no") else ""
        name = c["document_name"]
        chips.append(
            f'<span class="citation-chip" title="{_escape(name)}">'
            f"📄 {_escape(short_name(name, 48))} · chunk {c['chunk_index']}{page}</span>"
        )
    st.markdown('<div class="sources-label">Sources</div>', unsafe_allow_html=True)
    st.markdown(" ".join(chips), unsafe_allow_html=True)

    with st.expander(f"View excerpts ({len(citations)})", expanded=False):
        for i, c in enumerate(citations, start=1):
            page = f", page {c['page_no']}" if c.get("page_no") else ""
            st.markdown(f"**{i}. {_escape(short_name(c['document_name'], 70))}** · chunk {c['chunk_index']}{page}")
            st.caption(c.get("preview", ""))
