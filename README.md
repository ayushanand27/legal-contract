# Legal Contract Intelligence

Enterprise-style **RAG chatbot** for legal contract Q&A — grounded answers with hybrid retrieval, reranking, and per-document scope control.

Built as a POC pitch demo. Reference architecture inspired by [SMRA](https://github.com/ayushanand27/SMRA) (multi-agent RAG patterns).

![Stack](https://img.shields.io/badge/RAG-Hybrid%20Search-blue) ![Vector DB](https://img.shields.io/badge/Vector%20DB-Supabase%20pgvector-green) ![LLM](https://img.shields.io/badge/LLM-Groq%20Llama-orange)

---

## Features

- **Document-scoped chat** — multi-select documents; empty selection searches all
- **Hybrid retrieval** — dense vectors (pgvector) + PostgreSQL full-text search + RRF fusion
- **Cohere reranking** — top relevant chunks before generation
- **Citation-backed answers** — sources shown as clean chips (not cluttered inline text)
- **No-fabrication guardrail** — returns "Not applicable" when context is insufficient
- **CUAD seed script** — load 20 real annotated contracts for demo
- **Upload support** — PDF, DOCX, TXT ingestion

---

## Architecture

```
Upload / CUAD JSON
       ↓
  Text extraction → Chunking → Local embeddings (384-dim)
       ↓
  Supabase PostgreSQL
    ├── documents (metadata)
    └── chunks (text + embedding + FTS)
       ↓
  User query → Hybrid search → Cohere rerank → Groq LLM → Cited answer
```

**What is stored:** processed text chunks + embeddings in Supabase. Raw PDF bytes are not persisted (re-upload if needed).

---

## Prerequisites

| Service | Purpose | Sign up |
|---------|---------|---------|
| [Supabase](https://supabase.com) | Vector DB + metadata | Free tier |
| [Groq](https://console.groq.com) | LLM inference | Free tier |
| [Cohere](https://dashboard.cohere.com) | Reranking | Free trial |
| [Render](https://render.com) | Hosting (optional) | Free tier |

---

## Local Setup

### 1. Clone & install

```bash
git clone https://github.com/ayushanand27/legal-contract.git
cd legal-contract
python -m venv .venv

# Windows
.\.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Environment variables

```bash
cp .env.example .env
```

Fill in `.env`:

```env
SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
SUPABASE_SERVICE_KEY=your_service_role_jwt

GROQ_API_KEY=gsk_...
GROQ_MODEL=llama-3.3-70b-versatile

COHERE_API_KEY=...

EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384

CHUNK_SIZE=800
CHUNK_OVERLAP=100
RETRIEVAL_TOP_K=50
RERANK_TOP_K=5
MAX_CITATIONS=4

CUAD_JSON_PATH=data/CUAD_v1.json
CUAD_SEED_LIMIT=20
```

> **Important:** `SUPABASE_URL` must be the REST URL (`https://xxx.supabase.co`), NOT the Postgres connection string.

### 3. Supabase database schema

In Supabase **SQL Editor**, run the migration in `supabase/migrations/001_init.sql`.

This creates:
- `documents` and `chunks` tables
- `pgvector` extension
- `match_chunks_vector` and `match_chunks_fts` RPC functions

### 4. Download CUAD dataset (demo data)

Download [CUAD_v1.json](https://huggingface.co/datasets/theatticusproject/cuad) and place at:

```
data/CUAD_v1.json
```

### 5. Seed demo contracts

```bash
python scripts/seed_cuad.py
```

Expected: 20 contracts ingested into Supabase.

Verify:

```bash
python scripts/check_setup.py
```

### 6. Run the app

```bash
streamlit run app.py
```

Open `http://localhost:8501`

---

## Deploy on Render

### 1. Push to GitHub

Ensure `.env` is **not** committed (it's in `.gitignore`).

### 2. Create Web Service on Render

| Setting | Value |
|---------|-------|
| **Environment** | Python 3.11 |
| **Build Command** | `pip install --upgrade pip && pip install torch==2.6.0 --index-url https://download.pytorch.org/whl/cpu && pip install -r requirements.txt` |
| **Start Command** | `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true` |
| **Plan** | Free (slow cold start) or **Starter $7** (faster, no sleep) |

> **Why builds feel slow:** first deploy downloads CPU PyTorch + embedding model (~2–4 min). Use the build command above (CPU torch only, not CUDA). Data is already in Supabase — no re-seed on Render.

Or use **Blueprint**: connect repo and Render reads `render.yaml` automatically.

### 3. Add environment variables

Add all variables from `.env.example` in Render dashboard → **Environment**.

### 4. Seed data

Render free tier has no persistent shell for one-time seed. Options:

- **Option A:** Run `python scripts/seed_cuad.py` locally once (points to same Supabase project)
- **Option B:** Upload contracts via the app UI after deploy

### 5. Post-deploy

Visit your Render URL. First query may be slow (cold start + model load).

---

## Usage Tips (Pitch Demo)

1. **Single contract demo** — select one document in sidebar, ask "What is the termination clause?"
2. **Multi-contract demo** — clear selection (all 20 docs), ask "What are the payment terms?" — answer groups by contract
3. **Scope badge** — shows whether search is scoped or global
4. **Sources section** — max 4 citation chips per answer (deduplicated)

---

## Project Structure

```
app.py                  # Streamlit UI
config.py               # Settings + system prompt
core/
  chunking.py           # Section-aware text splitting
  chat.py               # RAG answer generation
  embeddings.py         # Local sentence-transformers
  extraction.py         # PDF/DOCX/TXT parsing
  ingestion.py          # Supabase ingest pipeline
  retrieval.py          # Hybrid search + rerank
  supabase_client.py
scripts/
  seed_cuad.py          # Load CUAD demo data
  check_setup.py        # Connectivity check
supabase/migrations/    # Database schema SQL
ui/styles.py            # Premium dark theme CSS
data/                   # CUAD JSON (not in git — download separately)
```

---

## API Keys Summary

| Key | Used for | Required |
|-----|----------|----------|
| `SUPABASE_URL` + `SUPABASE_SERVICE_KEY` | Storage + retrieval | Yes |
| `GROQ_API_KEY` | Answer generation | Yes |
| `COHERE_API_KEY` | Reranking | Yes (falls back to vector-only if missing) |
| OpenAI | — | **Not needed** (local embeddings) |

---

## References

- [CUAD Dataset](https://github.com/TheAtticusProject/cuad) — NeurIPS 2021, 510 annotated contracts
- [SMRA](https://github.com/ayushanand27/SMRA) — prior RAG architecture reference
- Hybrid retrieval + reranking industry patterns (BM25 + dense + RRF + cross-encoder rerank)

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `Supabase OK` fails | Check `SUPABASE_URL` is `https://` format, not postgres URL |
| Empty document list | Run `python scripts/seed_cuad.py` |
| Slow first query | Embedding model downloads on first run (~80MB) |
| Terminal spam on start | Already fixed via `fileWatcherType = "none"` in `.streamlit/config.toml` |
| Cross-doc answers when 1 doc selected | Verify scope badge shows "1 selected document" |

---

## License

MIT — POC / educational use. Not legal advice.
