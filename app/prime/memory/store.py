# app/prime/memory/store.py
"""
PRIME persistent memory store.
Saves every turn to SQLite immediately.
Summarizes every 20 turns via DeepSeek.
PRIME loads summaries + recent raw turns on every session start.
"""

from __future__ import annotations
import os
from datetime import datetime
from typing import Optional
import httpx
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import Session
from app.prime.memory.models import Base, PrimeConversationTurn, PrimeMemorySummary

# SQLite for now — easy to swap to Postgres later
DB_PATH = os.path.join(os.path.dirname(__file__), "prime_memory.db")
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
Base.metadata.create_all(engine)

SUMMARY_THRESHOLD = 10   # summarize more frequently
RECENT_TURNS_TO_LOAD = 6  # carry fewer raw turns — summaries cover the rest


def save_turn(session_id: str, role: str, content: str, user_id: str = "raymond"):
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


def load_recent_turns(user_id: str = "raymond", limit: int = RECENT_TURNS_TO_LOAD):
    """Load the most recent unsummarized turns for context."""
    with Session(engine) as db:
        rows = db.execute(
            select(PrimeConversationTurn)
            .where(PrimeConversationTurn.user_id == user_id)
            .where(PrimeConversationTurn.summarized == False)
            .order_by(PrimeConversationTurn.id.desc())
            .limit(limit)
        ).scalars().all()
        return list(reversed(rows))


def load_all_summaries(user_id: str = "raymond"):
    """Load all memory summaries — PRIME's long-term memory."""
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


def mark_turns_summarized(user_id: str = "raymond"):
    with Session(engine) as db:
        db.execute(
            update(PrimeConversationTurn)
            .where(PrimeConversationTurn.user_id == user_id)
            .where(PrimeConversationTurn.summarized == False)
            .values(summarized=True)
        )
        db.commit()


def save_summary(summary_text: str, turn_range: str, user_id: str = "raymond"):
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


async def maybe_summarize(user_id: str = "raymond"):
    """
    If unsummarized turns hit the threshold, compress them into
    a summary via DeepSeek and mark the raw turns as summarized.
    """
    if count_unsummarized(user_id) < SUMMARY_THRESHOLD:
        return

    turns = load_recent_turns(user_id=user_id, limit=SUMMARY_THRESHOLD)
    if not turns:
        return

    transcript = "\n".join(
        f"{t.role.upper()}: {t.content}" for t in turns
    )
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
                    "Content-Type": "application/json",
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 512,
                    "temperature": 0.3,
                },
            )
            data = response.json()
            summary_text = data["choices"][0]["message"]["content"].strip()

        save_summary(summary_text, turn_range, user_id)
        mark_turns_summarized(user_id)
        print(f"[PRIME MEMORY] Summarized {turn_range} for {user_id}")

    except Exception as e:
        print(f"[PRIME MEMORY] Summarization failed: {e!r}")
