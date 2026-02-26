from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from app.prime.curriculum.models import (
    ReasoningTask,
    ReasoningCoreResponse,
    ReasoningTraceTag,
    ReasoningOutcomeQuality,
    ReasoningMemoryEntry,
)

from app.prime.reasoning.memory_store import load_memory_entries, append_memory_entry


def save_practice_to_memory(
    *,
    entry_id: str,
    user_id: Optional[str],
    domain: str,
    subdomain: Optional[str],
    theme: Optional[str],
    practice_task: ReasoningTask,
    practice_response: ReasoningCoreResponse,
    outcome_quality: ReasoningOutcomeQuality = ReasoningOutcomeQuality.UNKNOWN,
) -> None:
    """
    Persist a practice episode (e.g., metaphysics practice) into the JSONL
    reasoning memory file as a ReasoningMemoryEntry.
    """
    try:
        tags = ReasoningTraceTag(
            domain=domain,
            subdomain=subdomain,
            theme=theme,
            user_label=None,
        )

        entry = ReasoningMemoryEntry(
            id=entry_id,
            task=practice_task,
            response=practice_response,
            tags=tags,
            created_at=datetime.utcnow(),
            user_id=user_id or "raymond",
            outcome_quality=outcome_quality,
        )

        append_memory_entry(entry)
    except Exception:
        # Fail silently for now.
        return


def query_recent_practice_for_user(
    user_id: Optional[str],
    domain: str,
    subdomain: str,
    theme_contains: Optional[str] = None,
    limit: int = 20,
) -> List[ReasoningMemoryEntry]:
    """
    Read recent ReasoningMemoryEntry rows from JSONL and filter by:
      - tags.domain == domain
      - tags.subdomain == subdomain
      - (optional) user_id match if provided (None means “any user”)
      - (optional) substring match on theme_contains in tags.theme

    Returns a list of entries ordered from most recent to oldest.
    """
    raw_entries = load_memory_entries(limit=limit * 5)
    matched: List[ReasoningMemoryEntry] = []

    # raw_entries is oldest->newest; traverse newest-first.
    for entry in reversed(raw_entries):
        if entry.tags is None:
            continue
        if entry.tags.domain != domain:
            continue
        if entry.tags.subdomain != subdomain:
            continue

        if user_id is not None and entry.user_id != user_id:
            continue

        if theme_contains is not None:
            theme_text = entry.tags.theme or ""
            if theme_contains not in theme_text:
                continue

        matched.append(entry)
        if len(matched) >= limit:
            break

    return matched
