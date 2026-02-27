"""
PRIME Session Store
File: app/prime/memory/session_store.py

Multi-turn conversation memory.
PRIME remembers every message in a session -- across API calls.
Persisted to JSONL so memory survives server restarts.
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional

# In-memory cache: session_id -> list of messages
_SESSIONS: Dict[str, List[Dict]] = {}

SESSION_DIR = Path(os.environ.get(
    "PRIME_SESSION_DIR",
    Path(__file__).resolve().parent.parent.parent.parent / "primelogs" / "sessions",
))
SESSION_DIR.mkdir(parents=True, exist_ok=True)


class SessionStore:
    """Manages PRIME's conversation memory across API calls."""

    def add_message(self, session_id: str, role: str, content: str) -> None:
        """Append a message to a session. Persists immediately to disk."""
        if session_id not in _SESSIONS:
            _SESSIONS[session_id] = []

        msg = {
            "role": role,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        _SESSIONS[session_id].append(msg)

        with open(self._session_file(session_id), "a", encoding="utf-8") as f:
            f.write(json.dumps(msg) + "\n")

    def get_history(self, session_id: str, limit: int = 20) -> List[Dict[str, str]]:
        """
        Returns last N messages as OpenAI-compatible {role, content} dicts.
        Loads from disk if not in memory.
        """
        if session_id not in _SESSIONS:
            self._load_from_disk(session_id)

        msgs = _SESSIONS.get(session_id, [])
        # Return only role+content for LLM -- strip timestamps
        return [{"role": m["role"], "content": m["content"]} for m in msgs[-limit:]]

    def get_full_history(self, session_id: str) -> List[Dict]:
        """Returns full history including timestamps (for the API response)."""
        if session_id not in _SESSIONS:
            self._load_from_disk(session_id)
        return _SESSIONS.get(session_id, []).copy()

    def clear_session(self, session_id: str) -> None:
        """Delete session from memory and disk."""
        _SESSIONS.pop(session_id, None)
        f = self._session_file(session_id)
        if f.exists():
            f.unlink()

    def list_sessions(self) -> List[str]:
        """Return all known session IDs."""
        return [f.stem for f in SESSION_DIR.glob("*.jsonl")]

    def new_session_id(self) -> str:
        return str(uuid.uuid4())

    def _session_file(self, session_id: str) -> Path:
        return SESSION_DIR / f"{session_id}.jsonl"

    def _load_from_disk(self, session_id: str) -> None:
        f = self._session_file(session_id)
        if not f.exists():
            return
        msgs = []
        with open(f, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    try:
                        msgs.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        _SESSIONS[session_id] = msgs


# Singleton
session_store = SessionStore()
