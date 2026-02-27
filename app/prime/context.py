from typing import Any, Dict, Optional

from app.prime.reasoning.prime_personality import PRIME_BRAIN_CONFIG


async def build_prime_context(
    message: str,
    session_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Minimal, DB-free PRIME context builder used by /prime/chat.

    This does NOT touch Postgres at all, so it cannot fail on db.execute().
    It just packages:
      - PRIME's brain config (identity, creed, temperament, loop, etc.)
      - the raw message
      - the session_id for continuity

    Later we will reintroduce the full builder (memories, projects, foundations,
    notebook, conversations, corpus) once a DB session is wired in cleanly.
    """
    return {
        "session_id": session_id,
        "message": message,
        "identity": PRIME_BRAIN_CONFIG,
    }
