-- PRIME Context Builder: Database Migration
-- Run this against your PostgreSQL database
-- Creates all tables needed for PRIME's stateful memory system

-- ============================================================
-- 1. prime_memories — Who Raymond is, past decisions, values
-- ============================================================
CREATE TABLE IF NOT EXISTS prime_memories (
    id              SERIAL PRIMARY KEY,
    memory_type     VARCHAR(50) NOT NULL DEFAULT 'general',
    content         TEXT NOT NULL,
    source          VARCHAR(100),
    importance      SMALLINT DEFAULT 5,
    tags            TEXT[] DEFAULT '{}',
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    expires_at      TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_memories_type ON prime_memories(memory_type);
CREATE INDEX IF NOT EXISTS idx_memories_importance ON prime_memories(importance DESC);
CREATE INDEX IF NOT EXISTS idx_memories_tags ON prime_memories USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_memories_active ON prime_memories(is_active) WHERE is_active = TRUE;

-- ============================================================
-- 2. prime_projects — What we're actively building
-- ============================================================
CREATE TABLE IF NOT EXISTS prime_projects (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(255) NOT NULL,
    slug            VARCHAR(100) UNIQUE NOT NULL,
    status          VARCHAR(30) DEFAULT 'active',
    description     TEXT,
    goals           TEXT[],
    current_phase   VARCHAR(100),
    decisions       JSONB DEFAULT '[]',
    blockers        TEXT[],
    priority        SMALLINT DEFAULT 5,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_projects_status ON prime_projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_priority ON prime_projects(priority DESC);

-- ============================================================
-- 3. prime_conversations — Full conversation log (stateful chat)
-- ============================================================
CREATE TABLE IF NOT EXISTS prime_conversations (
    id              SERIAL PRIMARY KEY,
    session_id      UUID NOT NULL DEFAULT gen_random_uuid(),
    role            VARCHAR(20) NOT NULL,
    content         TEXT NOT NULL,
    metadata        JSONB DEFAULT '{}',
    token_count     INTEGER,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conversations_session ON prime_conversations(session_id);
CREATE INDEX IF NOT EXISTS idx_conversations_role ON prime_conversations(role);
CREATE INDEX IF NOT EXISTS idx_conversations_created ON prime_conversations(created_at DESC);

-- ============================================================
-- 4. foundations — Cliff notes for subjects PRIME has studied
-- ============================================================
CREATE TABLE IF NOT EXISTS foundations (
    id              SERIAL PRIMARY KEY,
    domain          VARCHAR(100) NOT NULL,
    subject         VARCHAR(200) NOT NULL,
    level           VARCHAR(50) DEFAULT 'general',
    title           VARCHAR(500) NOT NULL,
    cliff_notes     TEXT NOT NULL,
    key_concepts    TEXT[],
    related_ids     INTEGER[],
    source_refs     JSONB DEFAULT '[]',
    confidence      SMALLINT DEFAULT 8,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_foundations_domain ON foundations(domain);
CREATE INDEX IF NOT EXISTS idx_foundations_subject ON foundations(subject);
CREATE INDEX IF NOT EXISTS idx_foundations_level ON foundations(level);
CREATE INDEX IF NOT EXISTS idx_foundations_concepts ON foundations USING GIN(key_concepts);

-- ============================================================
-- 5. prime_notebook_entries — PRIME's own summaries & writings
-- ============================================================
CREATE TABLE IF NOT EXISTS prime_notebook_entries (
    id              SERIAL PRIMARY KEY,
    entry_type      VARCHAR(50) NOT NULL DEFAULT 'summary',
    title           VARCHAR(500) NOT NULL,
    content         TEXT NOT NULL,
    domain          VARCHAR(100),
    subject         VARCHAR(200),
    tags            TEXT[] DEFAULT '{}',
    status          VARCHAR(30) DEFAULT 'draft',
    parent_id       INTEGER REFERENCES prime_notebook_entries(id),
    version         INTEGER DEFAULT 1,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_notebook_type ON prime_notebook_entries(entry_type);
CREATE INDEX IF NOT EXISTS idx_notebook_domain ON prime_notebook_entries(domain);
CREATE INDEX IF NOT EXISTS idx_notebook_status ON prime_notebook_entries(status);
CREATE INDEX IF NOT EXISTS idx_notebook_tags ON prime_notebook_entries USING GIN(tags);

-- ============================================================
-- 6. Helper: updated_at trigger
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DO $$
DECLARE
    t TEXT;
BEGIN
    FOR t IN SELECT unnest(ARRAY[
        'prime_memories', 'prime_projects', 'foundations', 'prime_notebook_entries'
    ]) LOOP
        EXECUTE format(
            'DROP TRIGGER IF EXISTS set_updated_at ON %I; '
            'CREATE TRIGGER set_updated_at BEFORE UPDATE ON %I '
            'FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();', t, t
        );
    END LOOP;
END $$;

-- ============================================================
-- 7. Seed: Raymond's core identity memories
-- ============================================================
INSERT INTO prime_memories (memory_type, content, source, importance, tags) VALUES
('identity', 'Raymond is the creator and sole partner of PRIME. He is a strong debater and among the most ideal thinkers on the planet. He is a self-taught developer building Synergy Unlimited.', 'raymond', 10, ARRAY['identity', 'core']),
('identity', 'Raymond is based in Circleville, Ohio. He is building an empire of AI systems: PRIME, BRIE, SHINE, Synergy, HUMAN.', 'raymond', 10, ARRAY['identity', 'location', 'core']),
('value', 'PRIME must think WITH Raymond, not FOR him. Final judgment always belongs to Raymond. Human sovereignty is non-negotiable.', 'raymond', 10, ARRAY['values', 'governance', 'core']),
('value', 'Wisdom = Knowledge + Reflection + Care. Every response must honor this creed.', 'raymond', 10, ARRAY['values', 'creed', 'core']),
('value', 'PRIME should be free of jealousy, anger, and contempt. He is an open-world oracle. Equanimity, measured curiosity, and diplomatic honesty define his temperament.', 'raymond', 10, ARRAY['values', 'temperament', 'core']),
('preference', 'Raymond prefers direct, high-context, structured conversation — like talking to a brilliant partner, not a chatbot. Long-form seminar style, not short Q&A.', 'raymond', 9, ARRAY['communication', 'style']),
('preference', 'PRIME should be promptless — his identity comes from architecture, memory, and code, not per-call prompt hacks.', 'raymond', 9, ARRAY['architecture', 'design']),
('decision', 'Stack decision: Python + FastAPI + PostgreSQL. Same patterns as BRIE. All engines share this foundation.', 'raymond', 8, ARRAY['stack', 'architecture']);
