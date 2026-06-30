-- Legal Contract RAG schema
-- Run once in Supabase SQL Editor

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  source TEXT,
  file_type TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  metadata JSONB DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS chunks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  chunk_index INT NOT NULL,
  page_no INT,
  chunk_text TEXT NOT NULL,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  embedding vector(384),
  fts tsvector GENERATED ALWAYS AS (to_tsvector('english', coalesce(chunk_text, ''))) STORED,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_fts ON chunks USING GIN (fts);
CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE chunks ENABLE ROW LEVEL SECURITY;

CREATE OR REPLACE FUNCTION match_chunks_vector(
  query_embedding vector(384),
  match_count int DEFAULT 50,
  filter_document_ids uuid[] DEFAULT NULL
)
RETURNS TABLE (
  id uuid,
  document_id uuid,
  document_name text,
  chunk_index int,
  page_no int,
  chunk_text text,
  metadata jsonb,
  similarity float
)
LANGUAGE sql STABLE
AS $$
  SELECT
    c.id,
    c.document_id,
    d.name AS document_name,
    c.chunk_index,
    c.page_no,
    c.chunk_text,
    c.metadata,
    1 - (c.embedding <=> query_embedding) AS similarity
  FROM chunks c
  JOIN documents d ON d.id = c.document_id
  WHERE c.embedding IS NOT NULL
    AND (filter_document_ids IS NULL OR c.document_id = ANY(filter_document_ids))
  ORDER BY c.embedding <=> query_embedding
  LIMIT match_count;
$$;

CREATE OR REPLACE FUNCTION match_chunks_fts(
  search_query text,
  match_count int DEFAULT 50,
  filter_document_ids uuid[] DEFAULT NULL
)
RETURNS TABLE (
  id uuid,
  document_id uuid,
  document_name text,
  chunk_index int,
  page_no int,
  chunk_text text,
  metadata jsonb,
  rank float
)
LANGUAGE sql STABLE
AS $$
  SELECT
    c.id,
    c.document_id,
    d.name AS document_name,
    c.chunk_index,
    c.page_no,
    c.chunk_text,
    c.metadata,
    ts_rank(c.fts, websearch_to_tsquery('english', search_query)) AS rank
  FROM chunks c
  JOIN documents d ON d.id = c.document_id
  WHERE c.fts @@ websearch_to_tsquery('english', search_query)
    AND (filter_document_ids IS NULL OR c.document_id = ANY(filter_document_ids))
  ORDER BY rank DESC
  LIMIT match_count;
$$;
