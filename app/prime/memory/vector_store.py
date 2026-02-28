"""
PRIME Vector Store
File: app/prime/memory/vector_store.py

Stores and searches memory embeddings using Postgres + pgvector.

Schema (auto-created on first call to ensure_schema()):
  prime_memory_vectors (
    id          SERIAL PRIMARY KEY,
    memory_id   TEXT UNIQUE NOT NULL,     -- deterministic content hash
    user_id     TEXT NOT NULL,
    session_id  TEXT,
    memory_type TEXT NOT NULL,            -- 'turn' | 'summary' | 'doc'
    text        TEXT NOT NULL,
    embedding   vector(1536),
    tags        JSONB DEFAULT '{}',
    created_at  TIMESTAMPTZ DEFAULT NOW()
  )

DB selection (in priority order):
  1. VECTOR_DATABASE_URL  -- dedicated vector DB (Supabase recommended)
  2. DATABASE_URL         -- fall back to main app DB if above not set

Requirements:
  Extension: pgvector (pre-installed on Supabase)
  Package:   pip install pgvector

All failures are logged and swallowed so a missing DB never crashes chat.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from dataclasses import dataclass, field
from typing import Any, Optional

import sqlalchemy as sa
from sqlalchemy import text

logger = logging.getLogger("prime.vector_store")

_TABLE     = "prime_memory_vectors"
_DIM       = 1536
_MAX_TOP_K = 50


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class VectorMemory:
    text:        str
    vector:      list[float]
    user_id:     str
    memory_type: str                       # 'turn' | 'summary' | 'doc'
    session_id:  Optional[str] = None
    tags:        dict           = field(default_factory=dict)
    memory_id:   Optional[str] = None      # auto-generated if None


@dataclass
class VectorMatch:
    memory_id:   str
    text:        str
    user_id:     str
    session_id:  Optional[str]
    memory_type: str
    tags:        dict
    score:       float   # cosine similarity 0..1


# ---------------------------------------------------------------------------
# Engine — VECTOR_DATABASE_URL first, DATABASE_URL as fallback
# ---------------------------------------------------------------------------

def _engine():
    url = os.getenv("VECTOR_DATABASE_URL") or os.getenv("DATABASE_URL", "")
    if not url:
        raise RuntimeError(
            "Neither VECTOR_DATABASE_URL nor DATABASE_URL is set — vector store unavailable"
        )
    return sa.create_engine(url, echo=False)


def _memory_id(text: str, user_id: str, memory_type: str) -> str:
    key = f"{user_id}:{memory_type}:{text[:200]}"
    return hashlib.sha256(key.encode()).hexdigest()[:32]


# ---------------------------------------------------------------------------
# Schema bootstrap
# ---------------------------------------------------------------------------

def ensure_schema() -> None:
    """
    Create pgvector extension + table + index if they don\'t exist.
    Safe to call on every startup — all operations are idempotent.
    """
    try:
        engine = _engine()
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {_TABLE} (
                    id          SERIAL PRIMARY KEY,
                    memory_id   TEXT UNIQUE NOT NULL,
                    user_id     TEXT NOT NULL,
                    session_id  TEXT,
                    memory_type TEXT NOT NULL DEFAULT \'turn\',
                    text        TEXT NOT NULL,
                    embedding   vector({_DIM}),
                    tags        JSONB DEFAULT \'{{}}\',
                    created_at  TIMESTAMPTZ DEFAULT NOW()
                )
            """))
            conn.execute(text(f"""
                CREATE INDEX IF NOT EXISTS {_TABLE}_embedding_idx
                ON {_TABLE} USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100)
            """))
            conn.commit()
        logger.info("Vector store schema ready (%s)", _TABLE)
        print(f"[PRIME] Vector store schema ready ({_TABLE})")
    except Exception as exc:
        logger.warning("ensure_schema failed (pgvector may not be installed): %s", exc)
        print(f"ensure_schema failed: {exc}")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def upsert(memories: list[VectorMemory]) -> None:
    """
    Insert or update memory vectors. On conflict (same memory_id),
    updates text, embedding, and tags.
    """
    if not memories:
        return
    try:
        engine = _engine()
        with engine.connect() as conn:
            for m in memories:
                mid     = m.memory_id or _memory_id(m.text, m.user_id, m.memory_type)
                vec_str = "[" + ",".join(str(v) for v in m.vector) + "]"
                conn.execute(text(f"""
                    INSERT INTO {_TABLE}
                        (memory_id, user_id, session_id, memory_type, text, embedding, tags)
                    VALUES
                        (:mid, :uid, :sid, :mtype, :txt, :vec::vector, :tags::jsonb)
                    ON CONFLICT (memory_id) DO UPDATE SET
                        text      = EXCLUDED.text,
                        embedding = EXCLUDED.embedding,
                        tags      = EXCLUDED.tags
                """), {
                    "mid":   mid,
                    "uid":   m.user_id,
                    "sid":   m.session_id,
                    "mtype": m.memory_type,
                    "txt":   m.text,
                    "vec":   vec_str,
                    "tags":  json.dumps(m.tags),
                })
            conn.commit()
    except Exception as exc:
        logger.warning("upsert failed: %s", exc)


def similarity_search(
    query_vector: list[float],
    *,
    top_k:   int  = 5,
    filters: dict = None,
) -> list[VectorMatch]:
    """
    Return the top_k most similar memories by cosine similarity.

    Optional filters dict keys:
      user_id      — restrict to one user
      session_id   — restrict to one session
      memory_type  — 'turn' | 'summary' | 'doc'
    """
    top_k   = min(top_k, _MAX_TOP_K)
    filters = filters or {}
    try:
        engine  = _engine()
        vec_str = "[" + ",".join(str(v) for v in query_vector) + "]"

        clauses: list[str] = []
        params: dict[str, Any] = {"vec": vec_str, "k": top_k}

        if "user_id"     in filters: clauses.append("user_id = :user_id");          params["user_id"]     = filters["user_id"]
        if "session_id"  in filters: clauses.append("session_id = :session_id");    params["session_id"]  = filters["session_id"]
        if "memory_type" in filters: clauses.append("memory_type = :memory_type");  params["memory_type"] = filters["memory_type"]

        where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
        sql = f"""
            SELECT memory_id, text, user_id, session_id, memory_type, tags,
                   1 - (embedding <=> :vec::vector) AS score
            FROM   {_TABLE}
            {where}
            ORDER  BY embedding <=> :vec::vector
            LIMIT  :k
        """
        with engine.connect() as conn:
            rows = conn.execute(text(sql), params).fetchall()

        return [
            VectorMatch(
                memory_id=r.memory_id,
                text=r.text,
                user_id=r.user_id,
                session_id=r.session_id,
                memory_type=r.memory_type,
                tags=r.tags if isinstance(r.tags, dict) else json.loads(r.tags or "{}"),
                score=float(r.score),
            )
            for r in rows
        ]
    except Exception as exc:
        logger.warning("similarity_search failed: %s", exc)
        return []
