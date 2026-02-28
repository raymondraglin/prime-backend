"""
PRIME Memory Retrieval
File: app/prime/memory/retrieval.py

Builds a ContextBundle for each LLM call by combining three layers:
  1. Recent raw turns    (store.py  — recency, guaranteed freshness)
  2. Memory summaries    (store.py  — compressed long-term history)
  3. Semantic matches    (vector_store.py — similarity to current query)

Budget management:
  Each layer has a character budget. Total is ~6000 chars so the
  bundle never bloats the context window.

Deduplication:
  Semantic hits that overlap with recent turns are dropped.
  Preference: newest over oldest on conflict.

Secret redaction:
  API keys, passwords, and secrets are stripped before any text
  is included in the bundle sent to the LLM.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger("prime.retrieval")

# ---------------------------------------------------------------------------
# Budget (chars per layer)
# ---------------------------------------------------------------------------

_BUDGET_RECENT   = 2_000
_BUDGET_SUMMARIES = 2_000
_BUDGET_SEMANTIC  = 2_000


# ---------------------------------------------------------------------------
# ContextBundle
# ---------------------------------------------------------------------------

@dataclass
class ContextBundle:
    recent_turns:      list[dict] = field(default_factory=list)   # [{role, content}]
    semantic_memories: list[str]  = field(default_factory=list)   # top semantic hits
    summaries:         list[str]  = field(default_factory=list)   # compressed history
    citations:         list[str]  = field(default_factory=list)   # provenance notes
    notes:             list[str]  = field(default_factory=list)   # debug / error notes

    def total_chars(self) -> int:
        parts = (
            [t.get("content", "") for t in self.recent_turns]
            + self.semantic_memories
            + self.summaries
        )
        return sum(len(p) for p in parts)


# ---------------------------------------------------------------------------
# Secret redaction
# ---------------------------------------------------------------------------

_REDACT_RE = re.compile(
    r"(?i)("
    r"sk-[A-Za-z0-9\-_]{20,}"
    r"|api[_\-]?key\s*[:=]\s*\S+"
    r"|password\s*[:=]\s*\S+"
    r"|secret\s*[:=]\s*\S+"
    r")"
)


def _redact(text: str) -> str:
    return _REDACT_RE.sub("[REDACTED]", text)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_context_bundle(
    user_id:    str,
    session_id: str,
    query:      str,
    *,
    top_k_semantic: int  = 5,
    embed_query:    bool = True,
) -> ContextBundle:
    """
    Build a ContextBundle for the next LLM call.

    Set embed_query=False to skip vector search (e.g., embeddings not configured).
    """
    bundle = ContextBundle()

    # 1. Recent turns
    try:
        from app.prime.memory.store import load_recent_turns
        turns = load_recent_turns(user_id=user_id)
        used  = 0
        for t in turns:
            c = _redact(t.content)
            if used + len(c) > _BUDGET_RECENT:
                break
            bundle.recent_turns.append({"role": t.role, "content": c})
            used += len(c)
    except Exception as exc:
        bundle.notes.append(f"recent_turns: {exc}")

    # 2. Summaries (newest → oldest, then reversed to chronological)
    try:
        from app.prime.memory.store import load_all_summaries
        all_summaries = load_all_summaries(user_id=user_id)
        used = 0
        packed: list[str] = []
        for s in reversed(all_summaries):
            t = _redact(s.summary)
            if used + len(t) > _BUDGET_SUMMARIES:
                break
            packed.append(t)
            used += len(t)
        bundle.summaries = list(reversed(packed))
    except Exception as exc:
        bundle.notes.append(f"summaries: {exc}")

    # 3. Semantic search (skipped if embed_query=False or no OPENAI_API_KEY)
    if embed_query and query:
        try:
            from app.prime.memory.embeddings import embed_text
            from app.prime.memory.vector_store import similarity_search

            q_vec = embed_text(query, memory_type="turn")
            if q_vec:
                hits         = similarity_search(q_vec, top_k=top_k_semantic, filters={"user_id": user_id})
                recent_texts = {t["content"] for t in bundle.recent_turns}
                used         = 0

                for hit in hits:
                    if hit.text in recent_texts:
                        continue
                    if hit.score < 0.75:   # skip low-confidence matches
                        continue
                    t = _redact(hit.text)
                    if used + len(t) > _BUDGET_SEMANTIC:
                        break
                    bundle.semantic_memories.append(t)
                    bundle.citations.append(
                        f"semantic:{hit.memory_type}:{hit.memory_id[:8]} score={hit.score:.2f}"
                    )
                    used += len(t)
        except Exception as exc:
            bundle.notes.append(f"semantic: {exc}")

    return bundle


def index_turn(
    user_id:    str,
    session_id: str,
    role:       str,
    content:    str,
) -> None:
    """
    Embed and store a conversation turn in the vector store.
    Called by store.save_turn — fire-and-forget, never raises.
    """
    try:
        from app.prime.memory.embeddings import embed_text
        from app.prime.memory.vector_store import VectorMemory, upsert

        vec = embed_text(content, memory_type="turn")
        if not vec:
            return
        upsert([VectorMemory(
            text=content,
            vector=vec,
            user_id=user_id,
            memory_type="turn",
            session_id=session_id,
            tags={"role": role},
        )])
    except Exception as exc:
        logger.warning("index_turn failed: %s", exc)


def index_summary(user_id: str, summary_text: str) -> None:
    """
    Embed and store a memory summary in the vector store.
    Called by store.save_summary — fire-and-forget, never raises.
    """
    try:
        from app.prime.memory.embeddings import embed_text
        from app.prime.memory.vector_store import VectorMemory, upsert

        vec = embed_text(summary_text, memory_type="summary")
        if not vec:
            return
        upsert([VectorMemory(
            text=summary_text,
            vector=vec,
            user_id=user_id,
            memory_type="summary",
            tags={"source": "auto_summary"},
        )])
    except Exception as exc:
        logger.warning("index_summary failed: %s", exc)
