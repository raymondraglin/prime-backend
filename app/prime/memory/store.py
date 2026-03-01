# app/prime/memory/store.py
"""
PRIME persistent memory store.

Storage backend:
  If DATABASE_URL is set → Postgres (production).
  Otherwise            → SQLite at prime_memory.db (local dev fallback).

  URL is always normalized to psycopg2 (sync) driver so asyncpg never
  gets loaded here. Async drivers belong only in async-native code.

Fallback chain:
  1. Postgres via DATABASE_URL  (if set and reachable)
  2. SQLite at prime_memory.db  (if Postgres unavailable at startup)

Every turn is saved immediately.
Every 10 unsummarized turns trigger a DeepSeek summarization.
On every LLM call, PRIME loads summaries + recent raw turns for context.

Vector indexing (semantic memory):
  After save_turn / save_summary, the text is embedded + stored in
  pgvector via retrieval.index_turn / retrieval.index_summary.
  Fire-and-forget — never blocks or crashes chat.
  Requires OPENAI_API_KEY + VECTOR_DATABASE_URL.
"""

from __future__ import annotations
import os
from datetime import datetime
from typing import Optional
import httpx
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import Session
from app.prime.memory.models import Base, PrimeConversationTurn, PrimeMemorySummary


# ---------------------------------------------------------------------------
# URL normalisation — always use psycopg2 (sync) for store.py
# ---------------------------------------------------------------------------

def _sync_url(url: str) -> str:
    url = url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    if url.startswith("postgresql://") and "+" not in url.split("://")[0]:
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


# ---------------------------------------------------------------------------
# Engine — Postgres if DATABASE_URL is set, SQLite as fallback
# ---------------------------------------------------------------------------

_raw_url = os.getenv("DATABASE_URL", "")

if _raw_url:
    _db_url = _sync_url(_raw_url)
    try:
        engine = create_engine(_db_url, echo=False)
        Base.metadata.create_all(engine)
    except Exception as _pg_err:
        print(f"[PRIME MEMORY] Postgres unavailable ({_pg_err!r}), falling back to SQLite")
        _DB_PATH = os.path.join(os.path.dirname(__file__), "prime_memory.db")
        engine   = create_engine(f"sqlite:///{_DB_PATH}", echo=False)
        Base.metadata.create_all(engine)
else:
    _DB_PATH = os.path.join(os.path.dirname(__file__), "prime_memory.db")
    engine   = create_engine(f"sqlite:///{_DB_PATH}", echo=False)
    Base.metadata.create_all(engine)


SUMMARY_THRESHOLD    = 10
RECENT_TURNS_TO_LOAD = 6


# ---------------------------------------------------------------------------
# Turn operations
# ---------------------------------------------------------------------------

def save_turn(
    session_id: str,
    role:       str,
    content:    str,
    user_id:    str = "raymond",
) -> None:
    with Session(engine) as db:
        turn = PrimeConversationTurn(
            session_id=session_id,
            user_id=user_id,
            role=role,
            content=content,
            timestamp=datetime.utcnow(),
            summarized=False,
        )
        db.add(turn)
        db.commit()

    # Index in vector store — fire-and-forget
    try:
        from app.prime.memory.retrieval import index_turn
        index_turn(user_id=user_id, session_id=session_id, role=role, content=content)
    except Exception:
        pass


def load_recent_turns(user_id: str = "raymond", limit: int = RECENT_TURNS_TO_LOAD):
    with Session(engine) as db:
        rows = db.execute(
            select(PrimeConversationTurn)
            .where(PrimeConversationTurn.user_id == user_id)
            .where(PrimeConversationTurn.summarized == False)
            .order_by(PrimeConversationTurn.id.desc())
            .limit(limit)
        ).scalars().all()
        return list(reversed(rows))


# ---------------------------------------------------------------------------
# Summary operations
# ---------------------------------------------------------------------------

def load_all_summaries(user_id: str = "raymond"):
    with Session(engine) as db:
        rows = db.execute(
            select(PrimeMemorySummary)
            .where(PrimeMemorySummary.user_id == user_id)
            .order_by(PrimeMemorySummary.id.asc())
        ).scalars().all()
        return rows


def count_unsummarized(user_id: str = "raymond") -> int:
    with Session(engine) as db:
        rows = db.execute(
            select(PrimeConversationTurn)
            .where(PrimeConversationTurn.user_id == user_id)
            .where(PrimeConversationTurn.summarized == False)
        ).scalars().all()
        return len(rows)


def mark_turns_summarized(user_id: str = "raymond") -> None:
    with Session(engine) as db:
        db.execute(
            update(PrimeConversationTurn)
            .where(PrimeConversationTurn.user_id == user_id)
            .where(PrimeConversationTurn.summarized == False)
            .values(summarized=True)
        )
        db.commit()


def save_summary(
    summary_text: str,
    turn_range:   str,
    user_id:      str = "raymond",
) -> None:
    with Session(engine) as db:
        entry = PrimeMemorySummary(
            user_id=user_id,
            summary=summary_text,
            turn_range=turn_range,
            created_at=datetime.utcnow(),
            archived=False,
        )
        db.add(entry)
        db.commit()

    # Index summary in vector store — fire-and-forget
    try:
        from app.prime.memory.retrieval import index_summary
        index_summary(user_id=user_id, summary_text=summary_text)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Auto-summarization
# ---------------------------------------------------------------------------

async def maybe_summarize(user_id: str = "raymond") -> None:
    """
    If unsummarized turns hit SUMMARY_THRESHOLD, compress them into
    a DeepSeek summary and mark raw turns as summarized.
    """
    if count_unsummarized(user_id) < SUMMARY_THRESHOLD:
        return

    turns = load_recent_turns(user_id=user_id, limit=SUMMARY_THRESHOLD)
    if not turns:
        return

    transcript = "\n".join(f"{t.role.upper()}: {t.content}" for t in turns)
    turn_range = f"turns {turns[0].id}-{turns[-1].id}"

    prompt = (
        "You are PRIME's memory system. Compress the following conversation into "
        "a dense, third-person summary that captures: key decisions made, "
        "important facts Raymond shared, emotional tone, open questions, "
        "and anything PRIME should remember permanently. "
        "Be specific. No filler. Write it so PRIME can read it months from now "
        "and know exactly what mattered.\n\n"
        f"CONVERSATION:\n{transcript}\n\nSUMMARY:"
    )

    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        return

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type":  "application/json",
                },
                json={
                    "model":                "deepseek-chat",
                    "messages":             [{"role": "user", "content": prompt}],
                    "max_completion_tokens": 512,
                    "temperature":          0.3,
                },
            )
            data         = response.json()
            summary_text = data["choices"][0]["message"]["content"].strip()

        save_summary(summary_text, turn_range, user_id)
        mark_turns_summarized(user_id)
        print(f"[PRIME MEMORY] Summarized {turn_range} for {user_id}")

    except Exception as exc:
        print(f"[PRIME MEMORY] Summarization failed: {exc!r}")
