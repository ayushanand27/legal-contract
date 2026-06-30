"""Clear all documents/chunks and re-seed CUAD with current embedding model."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.ingestion import delete_document, list_documents


def main() -> None:
    docs = list_documents()
    print(f"Deleting {len(docs)} existing documents...")
    for d in docs:
        delete_document(d.id)
        print(f"  deleted: {d.name[:60]}")

    print("Re-seeding CUAD...")
    subprocess.check_call([sys.executable, str(ROOT / "scripts" / "seed_cuad.py")])


if __name__ == "__main__":
    main()
