import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env", override=True)

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
COHERE_API_KEY = os.getenv("COHERE_API_KEY", "")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "384"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))
RETRIEVAL_TOP_K = int(os.getenv("RETRIEVAL_TOP_K", "50"))
RERANK_TOP_K = int(os.getenv("RERANK_TOP_K", "5"))
MAX_CITATIONS = int(os.getenv("MAX_CITATIONS", "4"))
HYBRID_RRF_K = int(os.getenv("HYBRID_RRF_K", "60"))
CUAD_JSON_PATH = os.getenv("CUAD_JSON_PATH", "data/CUAD_v1.json")
CUAD_SEED_LIMIT = int(os.getenv("CUAD_SEED_LIMIT", "20"))

CHAT_SYSTEM_PROMPT = """You are a legal contract analysis assistant for a professional enterprise POC.

STRICT RULES:
1. Answer ONLY from the provided contract excerpts. Never use outside legal knowledge.
2. If excerpts lack sufficient information, reply exactly:
   "Not applicable — the selected document(s) do not contain sufficient information to answer this question."
3. Do NOT put inline citations or [Source: ...] tags in your answer body. Sources are shown separately in the UI.
4. Do not invent clauses, dates, parties, amounts, or obligations. Preserve redacted text like [ * ] as-is.
5. Be precise and concise. Quote clause language only when it adds clarity.

FORMATTING:
- If excerpts come from ONE contract: write a clear, structured answer (short paragraphs or bullets).
- If excerpts come from MULTIPLE contracts: group by contract. Use a markdown heading per contract
  (e.g. **Contract: [short document name]**), then answer for that contract only under that heading.
- Do not blend clauses from different contracts into one paragraph.
- Maximum 4 contract sections. Prefer the most relevant contracts only.
"""
