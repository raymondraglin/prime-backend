# app/prime/context/__init__.py

"""
PRIME Context package.

Exposes build_prime_context and get_db for convenience.
When no live DB session is available (db=None), returns a minimal
in-memory context so /prime/chat never crashes on a missing DB.
"""

from typing import Any, Optional

from app.prime.reasoning.prime_personality import PRIME_BRAIN_CONFIG
from .builder import build_prime_context as _real_build_prime_context
from .database import get_db  # noqa: F401


async def build_prime_context(
    message: str,
    db: Optional[Any] = None,
    session_id: Optional[str] = None,
) -> dict:
    """
    Safe wrapper around the real context builder.

    - If db is None  → return a minimal in-memory context (no Postgres needed).
    - If db is provided → delegate to the full builder which loads memories,
      projects, conversations, foundations, and notebook entries from the DB.
    """
    if db is None:
        return {
            "session_id": session_id,
            "message": message,
            "identity": PRIME_BRAIN_CONFIG,
            "memories": [],
            "projects": [],
            "recent_conversation": [],
            "foundations": [],
            "notebook": [],
            "db_attached": False,
            "meta": {
                "keyword_hits": [],
                "memory_count": 0,
                "project_count": 0,
                "conversation_turns": 0,
                "foundation_count": 0,
                "notebook_count": 0,
            },
        }

    return await _real_build_prime_context(
        message=message,
        db=db,
        session_id=session_id,
    )
