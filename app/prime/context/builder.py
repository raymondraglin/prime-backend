# app/prime/context/builder.py

import asyncio
import re
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, desc, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from .models import (
    PrimeMemory,
    PrimeProject,
    PrimeConversation,
    Foundation,
    PrimeNotebookEntry,
)

MAX_MEMORIES = 20
MAX_PROJECTS = 10
MAX_CONVERSATIONS = 20
MAX_FOUNDATIONS = 5
MAX_NOTEBOOK = 5


def _extract_keywords(message: str) -> list[str]:
    stop_words = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "to", "of", "in", "for",
        "on", "with", "at", "by", "from", "it", "its", "this", "that", "these",
        "those", "my", "your", "his", "her", "our", "their", "i", "you", "he",
        "she", "we", "they", "me", "him", "us", "them",
    }
    words = re.findall(r"[a-zA-Z]{3,}", message.lower())
    return [w for w in words if w not in stop_words]


async def _fetch_memories(db: AsyncSession, keywords: list[str]) -> list[dict]:
    core_q = (
        select(PrimeMemory)
        .where(
            and_(
                PrimeMemory.is_active.is_(True),
                PrimeMemory.importance >= 9,
            )
        )
        .order_by(desc(PrimeMemory.importance))
        .limit(MAX_MEMORIES)
    )
    result = await db.execute(core_q)
    core = list(result.scalars().all())

    relevant = []
    if keywords and len(core) < MAX_MEMORIES:
        conds = [PrimeMemory.content.ilike(f"%{kw}%") for kw in keywords[:8]]
        rel_q = (
            select(PrimeMemory)
            .where(
                and_(
                    PrimeMemory.is_active.is_(True),
                    PrimeMemory.importance < 9,
                    or_(*conds),
                )
            )
            .order_by(desc(PrimeMemory.importance))
            .limit(MAX_MEMORIES - len(core))
        )
        result = await db.execute(rel_q)
        relevant = list(result.scalars().all())

    all_mem = core + relevant
    return [
        {
            "id": m.id,
            "type": m.memory_type,
            "content": m.content,
            "importance": m.importance,
            "tags": m.tags or [],
        }
        for m in all_mem
    ]


async def _fetch_projects(db: AsyncSession) -> list[dict]:
    q = (
        select(PrimeProject)
        .where(PrimeProject.status == "active")
        .order_by(desc(PrimeProject.priority))
        .limit(MAX_PROJECTS)
    )
    result = await db.execute(q)
    projects = list(result.scalars().all())
    return [
        {
            "id": p.id,
            "name": p.name,
            "slug": p.slug,
            "phase": p.current_phase,
            "goals": p.goals or [],
            "blockers": p.blockers or [],
            "priority": p.priority,
        }
        for p in projects
    ]


async def _fetch_conversations(
    db: AsyncSession,
    session_id: Optional[str],
) -> list[dict]:
    q = select(PrimeConversation).order_by(
        desc(PrimeConversation.created_at)
    ).limit(MAX_CONVERSATIONS)

    if session_id:
        from uuid import UUID

        q = q.where(PrimeConversation.session_id == UUID(session_id))

    result = await db.execute(q)
    convos = list(result.scalars().all())
    convos.reverse()

    return [
        {
            "role": c.role,
            "content": c.content,
            "timestamp": c.created_at.isoformat() if c.created_at else None,
            "metadata": c.metadata_ or {},
        }
        for c in convos
    ]


async def _fetch_foundations(db: AsyncSession, keywords: list[str]) -> list[dict]:
    if not keywords:
        return []

    conds = []
    for kw in keywords[:6]:
        conds.extend(
            [
                Foundation.domain.ilike(f"%{kw}%"),
                Foundation.subject.ilike(f"%{kw}%"),
                Foundation.title.ilike(f"%{kw}%"),
                Foundation.cliff_notes.ilike(f"%{kw}%"),
            ]
        )

    q = (
        select(Foundation)
        .where(or_(*conds))
        .order_by(desc(Foundation.confidence))
        .limit(MAX_FOUNDATIONS)
    )
    result = await db.execute(q)
    founds = list(result.scalars().all())
    return [
        {
            "id": f.id,
            "domain": f.domain,
            "subject": f.subject,
            "level": f.level,
            "title": f.title,
            "cliff_notes": f.cliff_notes,
            "key_concepts": f.key_concepts or [],
        }
        for f in founds
    ]


async def _fetch_notebook(db: AsyncSession, keywords: list[str]) -> list[dict]:
    if not keywords:
        q = (
            select(PrimeNotebookEntry)
            .where(PrimeNotebookEntry.status == "canonical")
            .order_by(desc(PrimeNotebookEntry.updated_at))
            .limit(3)
        )
        result = await db.execute(q)
        entries = list(result.scalars().all())
    else:
        conds = []
        for kw in keywords[:6]:
            conds.extend(
                [
                    PrimeNotebookEntry.title.ilike(f"%{kw}%"),
                    PrimeNotebookEntry.content.ilike(f"%{kw}%"),
                ]
            )
        q = (
            select(PrimeNotebookEntry)
            .where(or_(*conds))
            .order_by(
                desc(PrimeNotebookEntry.status),  # canonical > reviewed > draft (lex)
                desc(PrimeNotebookEntry.updated_at),
            )
            .limit(MAX_NOTEBOOK)
        )
        result = await db.execute(q)
        entries = list(result.scalars().all())

    return [
        {
            "id": e.id,
            "type": e.entry_type,
            "title": e.title,
            "content": e.content[:2000],
            "domain": e.domain,
            "status": e.status,
        }
        for e in entries
    ]


async def build_prime_context(
    message: str,
    db: AsyncSession,
    session_id: Optional[str] = None,
) -> dict:
    """Build the context snapshot PRIME sees before answering."""
    keywords = _extract_keywords(message)

    memories, projects, conversations, foundations, notebook = await asyncio.gather(
        _fetch_memories(db, keywords),
        _fetch_projects(db),
        _fetch_conversations(db, session_id),
        _fetch_foundations(db, keywords),
        _fetch_notebook(db, keywords),
    )

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message": message,
        "memories": memories,
        "projects": projects,
        "recent_conversation": conversations,
        "foundations": foundations,
        "notebook": notebook,
        "meta": {
            "keyword_hits": keywords,
            "memory_count": len(memories),
            "project_count": len(projects),
            "conversation_turns": len(conversations),
            "foundation_count": len(foundations),
            "notebook_count": len(notebook),
        },
    }
