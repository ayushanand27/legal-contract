"""Verify document_id filter returns only scoped chunks."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.ingestion import list_documents
from core.retrieval import retrieve_chunks


def main() -> None:
    docs = list_documents()
    if not docs:
        print("No documents in Supabase. Run seed_cuad.py first.")
        return

    target = docs[0]
    query = "termination clause"
    chunks = retrieve_chunks(query, document_ids=[target.id])

    foreign = [c for c in chunks if c.document_id != target.id]
    print(f"Scoped to: {target.name}")
    print(f"Retrieved: {len(chunks)} chunks")
    if foreign:
        print(f"FAIL: {len(foreign)} chunks from other documents leaked")
        for c in foreign[:3]:
            print(f"  - {c.document_name}")
    else:
        print("PASS: all chunks belong to selected document")


if __name__ == "__main__":
    main()
