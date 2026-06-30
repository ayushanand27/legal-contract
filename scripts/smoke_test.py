"""Headless smoke test — run before deploy to verify RAG end-to-end."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.chat import answer_question
from core.ingestion import list_documents


def main() -> None:
    docs = list_documents()
    print(f"Documents: {len(docs)}")
    if not docs:
        print("FAIL: no documents — run seed_cuad.py")
        sys.exit(1)

    # Test 1: all-docs scope
    print("\n--- Test 1: All documents ---")
    r1 = answer_question("What are the payment terms?")
    print(f"Answer length: {len(r1['answer'])} chars")
    print(f"Citations: {len(r1['citations'])}")
    print(f"Preview: {r1['answer'][:200]}...")

    # Test 2: single-doc scope
    target = docs[0]
    print(f"\n--- Test 2: Single doc ({target.name[:50]}...) ---")
    r2 = answer_question("What is this agreement about?", document_ids=[target.id])
    cited_names = {c["document_name"] for c in r2["citations"]}
    leaked = [n for n in cited_names if n != target.name]
    print(f"Citations: {len(r2['citations'])}")
    if leaked:
        print(f"FAIL: citations from other docs: {leaked}")
        sys.exit(1)
    print("PASS: single-doc filter OK")
    print(f"Preview: {r2['answer'][:200]}...")

    print("\nAll smoke tests passed.")


if __name__ == "__main__":
    main()
