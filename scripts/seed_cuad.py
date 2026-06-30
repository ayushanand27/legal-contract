"""Seed Supabase with N contracts from CUAD_v1.json."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import config
from core.ingestion import ingest_plain_text, list_documents


def _contract_text(contract: dict) -> str:
    paragraphs = contract.get("paragraphs") or []
    parts: list[str] = []
    for para in paragraphs:
        ctx = para.get("context") if isinstance(para, dict) else None
        if ctx and isinstance(ctx, str):
            parts.append(ctx.strip())
    return "\n\n".join(parts).strip()


def main() -> None:
    cuad_path = ROOT / config.CUAD_JSON_PATH
    if not cuad_path.exists():
        raise FileNotFoundError(f"CUAD file not found: {cuad_path}")

    existing = {d.name for d in list_documents()}
    payload = json.loads(cuad_path.read_text(encoding="utf-8"))
    contracts = payload.get("data") or []

    limit = config.CUAD_SEED_LIMIT
    seeded = 0
    for contract in contracts:
        if seeded >= limit:
            break
        title = (contract.get("title") or f"contract_{seeded}").strip()
        if title in existing:
            continue
        text = _contract_text(contract)
        if len(text) < 200:
            continue
        ingest_plain_text(
            name=title,
            text=text,
            source="cuad",
            file_type="cuad",
            extra_metadata={"dataset": "CUAD_v1"},
        )
        print(f"Seeded: {title}")
        seeded += 1

    print(f"Done. Seeded {seeded} contracts (limit={limit}).")


if __name__ == "__main__":
    main()
