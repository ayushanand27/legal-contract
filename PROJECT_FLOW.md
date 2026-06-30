# Legal Contract Intelligence — Complete Project Flow

> Ek file mein poora picture: kya banaya, kyun banaya, kaise chalaya, kaise test kiya, kaise deploy kiya.

---

## 1. Project kya hai?

**Legal Contract RAG Chatbot** — company pitch ke liye POC.

User legal contracts upload karta hai (ya demo data use karta hai), phir natural language mein questions puchta hai:
- "What are the payment terms?"
- "What is the termination clause?"
- "Who are the parties?"

System **sirf uploaded contracts se** answer deta hai — citations ke saath. Agar context nahi milta to "Not applicable" bolta hai (hallucination avoid).

---

## 2. Kyun ye approach? (Industry-aligned decisions)

| Decision | Kyun |
|----------|------|
| **RAG** (not fine-tuning) | Legal docs change hote rehte hain; RAG flexible hai, industry standard hai (Harvey, LawGeex pattern) |
| **Supabase pgvector** | Cloud persistent storage; Streamlit Cloud local DB uda deta hai restart pe |
| **Local embeddings** (`all-MiniLM-L6-v2`) | Free, no OpenAI quota risk; 384-dim vectors |
| **Groq LLM** | Fast + free tier; InterviewBot/SMRA mein already use kiya |
| **Cohere rerank** | Retrieval accuracy boost — top 50 se best 5 chunks |
| **Hybrid search** | Vector + keyword (BM25/FTS) — legal terms exact match ke liye zaroori |
| **Per-document filter** | Infosys vs Wipro — sirf selected doc ke chunks search hon |
| **SMRA reference** | Prior multi-agent RAG project — credibility for pitch |
| **CUAD dataset** | 510 real annotated contracts — legit demo data |

---

## 3. Architecture (data flow)

```
┌─────────────────────────────────────────────────────────────────┐
│                        INGESTION (one-time / upload)             │
├─────────────────────────────────────────────────────────────────┤
│  CUAD JSON / PDF / DOCX / TXT                                    │
│       ↓                                                          │
│  Text extraction (PyMuPDF / python-docx)                         │
│       ↓                                                          │
│  Chunking (~800 words, section-aware)                            │
│       ↓                                                          │
│  Embedding (sentence-transformers, local, 384-dim)               │
│       ↓                                                          │
│  Supabase PostgreSQL                                             │
│    • documents table  (id, name, source, metadata)               │
│    • chunks table     (text, embedding, document_id, FTS index)  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        CHAT (every question)                     │
├─────────────────────────────────────────────────────────────────┤
│  User question                                                   │
│       ↓                                                          │
│  Embed query (same local model)                                  │
│       ↓                                                          │
│  Hybrid retrieval (vector + full-text) + document_id filter      │
│       ↓                                                          │
│  RRF fusion → top 50 candidates                                  │
│       ↓                                                          │
│  Cohere rerank → top 5 chunks                                    │
│       ↓                                                          │
│  Groq LLM (llama-3.3-70b) + strict system prompt                 │
│       ↓                                                          │
│  Answer + source chips (max 4 citations)                         │
└─────────────────────────────────────────────────────────────────┘
```

**Important:** Raw PDF files Supabase mein store NAHI hote. Sirf **text chunks + embeddings** store hote hain. Original file local/upload se dubara chahiye ho to re-upload karna padega.

---

## 4. Kya kya banaya (file-by-file)

| File / Folder | Kya karta hai |
|---------------|---------------|
| `app.py` | Streamlit UI — chat, sidebar, upload, scope select |
| `config.py` | Env vars + LLM system prompt |
| `core/ingestion.py` | Upload → chunk → embed → Supabase save |
| `core/retrieval.py` | Hybrid search + rerank + document filter |
| `core/chat.py` | RAG answer generation (Groq) |
| `core/embeddings.py` | Local sentence-transformers model |
| `core/chunking.py` | Section-aware text splitting |
| `core/extraction.py` | PDF/DOCX/TXT text extract |
| `scripts/seed_cuad.py` | 20 CUAD contracts load karta hai |
| `scripts/check_setup.py` | Supabase connect + embedding test |
| `scripts/test_filter.py` | Single-doc filter leak check |
| `scripts/smoke_test.py` | Full end-to-end RAG test (headless) |
| `supabase/migrations/001_init.sql` | DB schema + RPC functions |
| `ui/styles.py` | Dark premium CSS theme |
| `ui/render_helpers.py` | Answer cards, citation expander |
| `render.yaml` | Render deploy blueprint |
| `.env` | API keys (git mein NAHI jata) |

---

## 5. Tumne kya kya setup kiya (timeline)

| Step | Kya kiya | Kyun |
|------|----------|------|
| 1 | SMRA clone kiya | Reference architecture |
| 2 | Supabase project banaya + pgvector enable | Vector storage |
| 3 | Groq + Cohere API keys liye | LLM + reranking |
| 4 | CUAD_v1.json download → `data/` | Demo contracts |
| 5 | `.env` file banayi | Secrets local |
| 6 | `pip install -r requirements.txt` | Dependencies |
| 7 | `python scripts/seed_cuad.py` | 20 docs → Supabase |
| 8 | `streamlit run app.py` | Local test |
| 9 | GitHub push | Code backup |
| 10 | Render deploy + build command update | Public URL for pitch |

---

## 6. Environment variables (`.env`)

```env
SUPABASE_URL=https://cpwxjnsxxxbjeosmdslo.supabase.co    # REST URL (NOT postgres string)
SUPABASE_SERVICE_KEY=eyJ...                             # service_role JWT
GROQ_API_KEY=gsk_...
COHERE_API_KEY=...
GROQ_MODEL=llama-3.3-70b-versatile
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
RERANK_TOP_K=5
MAX_CITATIONS=4
CUAD_JSON_PATH=data/CUAD_v1.json
CUAD_SEED_LIMIT=20
```

Render dashboard mein bhi **same keys** add karni hain (`.env` upload nahi hoti).

---

## 7. Kaise test karna hai (step-by-step)

> **Rule:** Hamesha pehle venv activate karo. Bina activate `ModuleNotFoundError: cohere` aayega.

```powershell
cd C:\Users\ayush\Downloads\legal-contract
.\.venv\Scripts\activate
```

### Test 1 — Infrastructure check

```powershell
python scripts\check_setup.py
```

**Pass criteria:**
```
Supabase OK
Documents: 20
Chunks: 201
Embedding dim: 384
```

| Fail | Fix |
|------|-----|
| Supabase error | `.env` mein `SUPABASE_URL` = `https://...` check karo |
| Documents: 0 | `python scripts\seed_cuad.py` chalao |
| Embedding error | `pip install -r requirements.txt` |

---

### Test 2 — Document filter (no cross-doc leak)

```powershell
python scripts\test_filter.py
```

**Pass criteria:**
```
PASS: all chunks belong to selected document
```

Ye confirm karta hai: jab 1 doc select karo, doosre contract ke chunks retrieve nahi honge.

---

### Test 3 — Full RAG smoke test (Groq + Cohere)

```powershell
python scripts\smoke_test.py
```

**Pass criteria:**
```
--- Test 1: All documents ---
Citations: 4
Preview: ## Payment Terms...

--- Test 2: Single doc ---
PASS: single-doc filter OK

All smoke tests passed.
```

Ye ~40 sec leta hai (embedding + API calls).

| Fail | Fix |
|------|-----|
| Groq error | `GROQ_API_KEY` check / rate limit wait |
| Cohere error | `COHERE_API_KEY` check |
| Empty answer | Normal for some docs — query change karo |

---

### Test 4 — UI manual test

```powershell
streamlit run app.py
```

Browser: `http://localhost:8501`

#### Test 4a — Default scope (all 20 docs)

1. Sidebar mein **kuch mat select** karo
2. Badge dikhe: `Scope: All 20 documents`
3. Pucho: **"What are the payment terms?"**
4. Expect:
   - Multiple contracts grouped (headings per contract)
   - Max 4 source chips
   - "View excerpts" expander kaam kare

#### Test 4b — Single document scope

1. Sidebar se **1 contract** select karo (e.g. LIMEENERGYCO...)
2. Badge: `Scope: 1 selected document`
3. Pucho: **"What is the termination clause?"**
4. Expect:
   - Sirf us contract ka answer
   - Citations sirf usi doc ke naam se

#### Test 4c — Multi-select scope

1. **2-3 documents** select karo
2. Same question
3. Expect: sirf selected docs se citations

#### Test 4d — Upload test (optional)

1. Sidebar → PDF upload → Ingest
2. Naya doc list mein dikhe
3. Sirf us doc select karke question pucho

---

### Test 5 — Deployed URL (Render)

Deploy ke baad:

1. URL kholo
2. Pehla load 30–60 sec (model warmup) — normal
3. Same Test 4a + 4b deployed URL pe repeat karo
4. Scope badge + welcome box dikhna chahiye

---

## 8. Pitch demo script (5 min)

```
1. [Show UI] "Legal Contract Intelligence — RAG over commercial contracts"

2. [No selection] Ask: "What are the payment terms?"
   → Show grouped multi-contract answer + citations
   → "System searches all 20 contracts, groups by source"

3. [Select 1 doc] Ask: "What is the termination clause?"
   → Show single-contract focused answer
   → "Document-scoped retrieval — no cross-contamination"

4. [Mention stack] "Hybrid search + Cohere rerank + Groq LLM + Supabase pgvector"

5. [Mention guardrails] "Returns 'Not applicable' if context insufficient — no hallucination"

6. [Reference] "Built on patterns from SMRA + CUAD dataset (NeurIPS 2021)"
```

---

## 9. Deploy on Render

### Build command (updated — CPU torch, faster)

```
pip install --upgrade pip && pip install torch==2.6.0 --index-url https://download.pytorch.org/whl/cpu && pip install -r requirements.txt
```

### Start command

```
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
```

### Env vars

Render → Environment → sab `.env` keys add karo.

### Data

Supabase mein data already hai (20 docs). **Render pe seed dubara chalane ki zaroorat nahi** — same Supabase project use ho raha hai.

### Redeploy

GitHub push ke baad Render → Manual Deploy → latest commit.

---

## 10. Common issues & fixes

| Problem | Solution |
|---------|----------|
| `No module named 'cohere'` | `.venv\Scripts\activate` pehle |
| Build 10+ min | Normal first time; CPU torch command use karo |
| Cold start slow | Starter plan ya pehla chat wait karo |
| Multi-doc answer when 1 selected | Scope badge check — "1 selected" hona chahiye |
| 8 citation chips | Latest code max 4 — redeploy karo |
| Terminal torchvision spam | `fileWatcherType = "none"` already set |
| CUAD missing | Download from HuggingFace → `data/CUAD_v1.json` |

---

## 11. Git commits history (kya kya push hua)

| Commit | Kya tha |
|--------|---------|
| Initial | Full RAG pipeline + Supabase + Streamlit UI |
| UI polish | Answer cards, citations cleanup, scope badge |
| Deploy optimize | CPU torch, pinned requirements, render.yaml |
| Smoke test | `smoke_test.py`, welcome box, pre-deploy checklist |

**Repo:** https://github.com/ayushanand27/legal-contract

---

## 12. Quick command cheat sheet

```powershell
# Activate (ALWAYS FIRST)
cd C:\Users\ayush\Downloads\legal-contract
.\.venv\Scripts\activate

# Pre-deploy tests (run in order)
python scripts\check_setup.py
python scripts\test_filter.py
python scripts\smoke_test.py

# Run app
streamlit run app.py

# Re-seed data (only if Supabase empty)
python scripts\seed_cuad.py

# Git push after changes
git add -A
git commit -m "your message"
git push origin main
```

---

## 13. Ab kya karna hai (tumhara status)

Based on your terminal output — **sab tests PASS**:

- [x] check_setup.py — 20 docs, 201 chunks
- [x] test_filter.py — PASS
- [x] smoke_test.py — All passed
- [x] Build command Render pe update
- [ ] **Redeploy** latest commit (`1df339d`) on Render
- [ ] Deployed URL pe Test 4a + 4b repeat karo
- [ ] Pitch demo practice

**Tum deploy ke liye ready ho.**
