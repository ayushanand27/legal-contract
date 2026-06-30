"""Quick connectivity check for Supabase + embeddings."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.embeddings import embed_query
from core.supabase_client import get_supabase


def main() -> None:
    sb = get_supabase()
    docs = sb.table("documents").select("id", count="exact").execute()
    chunks = sb.table("chunks").select("id", count="exact").execute()
    vec = embed_query("termination clause")
    print("Supabase OK")
    print(f"Documents: {docs.count}")
    print(f"Chunks: {chunks.count}")
    print(f"Embedding dim: {len(vec)}")


if __name__ == "__main__":
    main()
