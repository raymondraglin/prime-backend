# app/prime/memory/store.py
"""
PRIME Memory Store

Persistent conversation storage with optional semantic retrieval.

Core operations:
  save_conversation_turn    -- persist user/assistant pair (always works)
  search_memories           -- semantic search (requires pgvector)
  get_conversation_history  -- chronological retrieval by session_id (always works)
  get_recent_context        -- last N turns for a user (always works)

Graceful degradation:
  - Conversations always saved to conversation_turns table
  - Embeddings skipped if pgvector unavailable
  - search_memories returns [] if pgvector unavailable
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any
import uuid

import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.prime.memory.models import Base, ConversationTurn, EMBEDDING_DIM

EMBEDDING_MODEL = "text-embedding-3-small"

_pgvector_available = None


def _check_pgvector() -> bool:
    """Check if pgvector extension is available. Cached after first check."""
    global _pgvector_available
    if _pgvector_available is not None:
        return _pgvector_available
    
    try:
        from pgvector.sqlalchemy import Vector
        engine = _get_engine()
        with engine.connect() as conn:
            conn.execute(sa.text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
        _pgvector_available = True
        print("[memory/store] pgvector extension available")
        return True
    except Exception as e:
        _pgvector_available = False
        print(f"[memory/store] pgvector unavailable (embeddings disabled): {e}")
        return False


def _get_engine():
    db_url = os.getenv("DATABASE_URL", "")
    if not db_url:
        raise ValueError("DATABASE_URL not set")
    sync_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
    return create_engine(sync_url)


def ensure_tables():
    """Create memory tables. Embedding table only created if pgvector available."""
    engine = _get_engine()
    
    # Always create conversation_turns
    try:
        with engine.connect() as conn:
            if _check_pgvector():
                conn.execute(sa.text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
    except Exception as e:
        print(f"[memory/store] Warning: {e}")
    
    # Create base tables
    Base.metadata.create_all(engine)
    
    # Create memory_embeddings only if pgvector available
    if _check_pgvector():
        try:
            from app.prime.memory.models import MemoryEmbedding
            MemoryEmbedding.__table__.create(engine, checkfirst=True)
        except Exception as e:
            print(f"[memory/store] Could not create memory_embeddings: {e}")


def save_conversation_turn(
    user_message: str,
    assistant_message: str,
    session_id: str | uuid.UUID | None = None,
    user_id: str = "raymond",
    model: str | None = None,
    tokens_used: int | None = None,
    tool_calls: list[dict] | None = None,
    citations: list[dict] | None = None,
    metadata: dict | None = None,
) -> int:
    """
    Save a conversation turn (always works).
    Generates embedding only if pgvector available.
    """
    ensure_tables()
    engine  = _get_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        if session_id is None:
            session_id = uuid.uuid4()
        elif isinstance(session_id, str):
            session_id = uuid.UUID(session_id)

        turn = ConversationTurn(
            session_id    = session_id,
            user_id       = user_id,
            user_message  = user_message,
            assistant_msg = assistant_message,
            model         = model,
            tokens_used   = tokens_used,
            tool_calls    = tool_calls or [],
            citations     = citations or [],
            metadata_     = metadata or {},
        )
        session.add(turn)
        session.flush()
        turn_id = turn.id

        # Generate embedding only if pgvector available
        if _check_pgvector():
            try:
                from app.prime.memory.models import MemoryEmbedding
                from openai import OpenAI
                
                summary = f"{user_message[:500]} | {assistant_message[:200]}"
                client  = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                resp    = client.embeddings.create(model=EMBEDDING_MODEL, input=[summary])
                emb     = resp.data[0].embedding

                mem_emb = MemoryEmbedding(
                    turn_id   = turn_id,
                    user_id   = user_id,
                    summary   = summary,
                    embedding = emb,
                )
                session.add(mem_emb)
            except Exception as e:
                print(f"[memory/store] Embedding generation failed (non-critical): {e}")
        
        session.commit()
        return turn_id

    finally:
        session.close()


def search_memories(
    query: str,
    k: int = 5,
    user_id: str | None = None,
) -> list[dict]:
    """
    Semantic search across all stored conversation turns.
    Returns [] if pgvector unavailable.
    """
    if not _check_pgvector():
        print("[memory/store] search_memories unavailable (pgvector not installed)")
        return []
    
    try:
        from app.prime.memory.models import MemoryEmbedding
        from openai import OpenAI
        
        ensure_tables()
        engine  = _get_engine()
        Session = sessionmaker(bind=engine)
        session = Session()

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        resp   = client.embeddings.create(model=EMBEDDING_MODEL, input=[query])
        q_emb  = resp.data[0].embedding

        query_obj = (
            session.query(
                ConversationTurn.id,
                ConversationTurn.user_message,
                ConversationTurn.assistant_msg,
                ConversationTurn.created_at,
                MemoryEmbedding.embedding.cosine_distance(q_emb).label("distance"),
            )
            .join(MemoryEmbedding, ConversationTurn.id == MemoryEmbedding.turn_id)
        )

        if user_id:
            query_obj = query_obj.filter(ConversationTurn.user_id == user_id)

        results = query_obj.order_by(sa.text("distance")).limit(k).all()
        session.close()

        return [
            {
                "turn_id":       r.id,
                "user_message":  r.user_message,
                "assistant_msg": r.assistant_msg,
                "created_at":    r.created_at.isoformat(),
                "score":         round(1 - r.distance, 4),
            }
            for r in results
        ]

    except Exception as e:
        print(f"[memory/store] search_memories error: {e}")
        return []


def get_conversation_history(
    session_id: str | uuid.UUID,
    limit: int = 50,
) -> list[dict]:
    """Retrieve chronological conversation history for a session (always works)."""
    ensure_tables()
    engine  = _get_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        if isinstance(session_id, str):
            session_id = uuid.UUID(session_id)

        turns = (
            session.query(ConversationTurn)
            .filter(ConversationTurn.session_id == session_id)
            .order_by(ConversationTurn.created_at.asc())
            .limit(limit)
            .all()
        )

        return [
            {
                "turn_id":       t.id,
                "user_message":  t.user_message,
                "assistant_msg": t.assistant_msg,
                "model":         t.model,
                "tokens_used":   t.tokens_used,
                "tool_calls":    t.tool_calls,
                "citations":     t.citations,
                "metadata":      t.metadata_,
                "created_at":    t.created_at.isoformat(),
            }
            for t in turns
        ]

    finally:
        session.close()


def get_recent_context(
    user_id: str = "raymond",
    limit: int = 10,
) -> list[dict]:
    """Get the most recent N conversation turns for a user (always works)."""
    ensure_tables()
    engine  = _get_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        turns = (
            session.query(ConversationTurn)
            .filter(ConversationTurn.user_id == user_id)
            .order_by(ConversationTurn.created_at.desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "turn_id":       t.id,
                "session_id":    str(t.session_id),
                "user_message":  t.user_message,
                "assistant_msg": t.assistant_msg,
                "created_at":    t.created_at.isoformat(),
            }
            for t in turns
        ]

    finally:
        session.close()
