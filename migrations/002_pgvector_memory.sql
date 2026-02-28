-- migrations/002_pgvector_memory.sql
-- Run this once against your Postgres database before using semantic memory.
-- Safe to run multiple times (all statements are idempotent).
--
-- Prerequisites:
--   1. Postgres 14+ with pgvector extension available
--   2. DATABASE_URL pointing to the right database
--
-- Run it:
--   psql $DATABASE_URL -f migrations/002_pgvector_memory.sql

-- Step 1: Install pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Step 2: Create the memory vectors table
CREATE TABLE IF NOT EXISTS prime_memory_vectors (
    id          SERIAL PRIMARY KEY,
    memory_id   TEXT        UNIQUE NOT NULL,     -- SHA256 hash of content+user+type
    user_id     TEXT        NOT NULL,
    session_id  TEXT,
    memory_type TEXT        NOT NULL DEFAULT 'turn',  -- 'turn' | 'summary' | 'doc'
    text        TEXT        NOT NULL,
    embedding   vector(1536),                     -- text-embedding-3-small dims
    tags        JSONB       DEFAULT '{}',
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Step 3: Index for fast cosine similarity search (IVFFlat)
-- lists=100 is good for up to ~1M rows; increase to 200 for larger datasets
CREATE INDEX IF NOT EXISTS prime_memory_vectors_embedding_idx
ON prime_memory_vectors
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Step 4: Index for user-scoped queries (fast filtering)
CREATE INDEX IF NOT EXISTS prime_memory_vectors_user_idx
ON prime_memory_vectors (user_id, memory_type, created_at DESC);

-- Verify
SELECT 'prime_memory_vectors ready' AS status,
       COUNT(*) AS existing_rows
FROM   prime_memory_vectors;
