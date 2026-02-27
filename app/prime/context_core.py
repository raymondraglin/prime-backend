"""
PRIME Context Builder
File: app/prime/context.py

Assembles the full memory snapshot PRIME "sees" before every response.
Runs in under 100ms. Called by /prime/chat before the LLM sees a token.
"""

from __future__ import annotations

import re
from typing import Optional
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import desc, text

from app.prime.models import (
    PrimeMemory,
    PrimeConversation,
    PrimeProject,
    Foundation,
    PrimeNotebookEntry,
    Domain,
    Subject,
)


# ─────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────

CONVERSATION_TAIL   = 20    # last N exchanges loaded always
MEMORY_TOP_K        = 15    # top memories by relevance + importance
FOUNDATION_TOP_K    = 5     # cliff notes relevant to this message
NOTEBOOK_TOP_K      = 5     # notebook entries relevant to this message
CONSTITUTION_KIND   = "raymond_preference"  # highest-importance memories
MIN_IMPORTANCE      = 1     # only load memories above this threshold


# ─────────────────────────────────────────────────────────────
# SIMPLE KEYWORD EXTRACTOR
# Used for relevance matching until vector search is added.
# Replace with pgvector cosine similarity when embeddings are live.
# ─────────────────────────────────────────────────────────────

def _keywords(text: str) -> set[str]:
    """Extract meaningful keywords from a string."""
    stop = {
        "a","an","the","and","or","but","in","on","at","to","for",
        "of","with","by","from","is","was","are","were","be","been",
        "i","we","you","he","she","it","they","this","that","what",
        "how","when","where","who","which","will","can","do","did",
        "not","no","if","as","so","my","your","his","her","our",
        "me","him","us","them","have","has","had","about","would",
    }
    words = re.findall(r"[a-z]+", text.lower())
    return {w for w in words if len(w) > 3 and w not in stop}


def _score_relevance(target: str, keywords: set[str]) -> int:
    """Count keyword hits in target string."""
    target_words = set(re.findall(r"[a-z]+", target.lower()))
    return len(keywords & target_words)


# ─────────────────────────────────────────────────────────────
# LAYER 1: PRIME'S CONSTITUTION + IDENTITY MEMORIES
# importance=10 entries — who PRIME is, never forgotten
# ─────────────────────────────────────────────────────────────

def _load_constitution(db: Session) -> list[dict]:
    """Load PRIME's highest-importance identity memories (importance >= 8)."""
    rows = (
        db.query(PrimeMemory)
        .filter(PrimeMemory.importance >= 8)
        .order_by(desc(PrimeMemory.importance))
        .all()
    )
    return [
        {
            "kind":       r.kind,
            "subject":    r.subject,
            "body":       r.body,
            "importance": r.importance,
            "tags":       r.tags,
        }
        for r in rows
    ]


# ─────────────────────────────────────────────────────────────
# LAYER 2: RAYMOND'S PROFILE + EPISODIC MEMORIES
# ─────────────────────────────────────────────────────────────

def _load_raymond_memories(db: Session, keywords: set[str]) -> list[dict]:
    """
    Load memories about Raymond: preferences, decisions, open questions,
    things Raymond said, relationship notes.
    Sorted by: keyword relevance first, then importance.
    """
    rows = (
        db.query(PrimeMemory)
        .filter(
            PrimeMemory.importance < 8,   # constitution loaded separately
            PrimeMemory.importance >= MIN_IMPORTANCE,
        )
        .order_by(desc(PrimeMemory.importance))
        .limit(100)   # pre-filter pool
        .all()
    )

    scored = []
    for r in rows:
        score = _score_relevance(r.subject + " " + r.body, keywords)
        scored.append((score, r.importance, r))

    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    top = [r for _, _, r in scored[:MEMORY_TOP_K]]

    # Update last_recalled timestamp
    for r in top:
        r.last_recalled = datetime.utcnow()
    db.commit()

    return [
        {
            "kind":       r.kind,
            "subject":    r.subject,
            "body":       r.body,
            "importance": r.importance,
            "tags":       r.tags,
        }
        for r in top
    ]


# ─────────────────────────────────────────────────────────────
# LAYER 3: ACTIVE PROJECTS
# ─────────────────────────────────────────────────────────────

def _load_active_projects(db: Session) -> list[dict]:
    """Load all active projects — PRIME always knows what we're building."""
    rows = (
        db.query(PrimeProject)
        .filter(PrimeProject.status == "active")
        .order_by(PrimeProject.updated_at.desc())
        .all()
    )
    return [
        {
            "name":           r.name,
            "description":    r.description,
            "goals":          r.goals,
            "decisions":      r.decisions,
            "open_questions": r.open_questions,
            "notes":          r.notes,
        }
        for r in rows
    ]


# ─────────────────────────────────────────────────────────────
# LAYER 4: CONVERSATION TAIL
# The last N exchanges — the immediate working memory
# ─────────────────────────────────────────────────────────────

def _load_conversation_tail(
    db: Session,
    session_id: Optional[str] = None,
    tail: int = CONVERSATION_TAIL,
) -> list[dict]:
    """
    Load the most recent conversation exchanges.
    If session_id is provided, load from that session first,
    then pad with older exchanges if needed.
    Always returns in chronological order (oldest first).
    """
    query = db.query(PrimeConversation)

    # No session filter — PRIME's conversation is one continuous thread.
    # session_id is soft grouping only.
    rows = (
        query
        .order_by(desc(PrimeConversation.created_at))
        .limit(tail)
        .all()
    )
    rows.reverse()  # chronological order for the LLM

    return [
        {
            "speaker":    r.speaker,
            "message":    r.message,
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]


# ─────────────────────────────────────────────────────────────
# LAYER 5: FOUNDATIONS (cliff notes)
# Fast knowledge retrieval — PRIME's distilled understanding
# ─────────────────────────────────────────────────────────────

def _load_foundations(db: Session, keywords: set[str]) -> list[dict]:
    """
    Load the most relevant foundation cliff notes for this message.
    Scored by keyword match against summary + key_concepts.
    """
    rows = (
        db.query(Foundation, Subject, Domain)
        .join(Subject, Foundation.subject_id == Subject.id)
        .join(Domain,  Foundation.domain_id  == Domain.id)
        .limit(200)
        .all()
    )

    scored = []
    for f, s, d in rows:
        search_text = (
            f.summary + " "
            + " ".join(f.key_concepts if isinstance(f.key_concepts, list) else [])
            + " " + s.name + " " + d.name
        )
        score = _score_relevance(search_text, keywords)
        if score > 0:
            scored.append((score, f, s, d))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:FOUNDATION_TOP_K]

    return [
        {
            "domain":          d.name,
            "subject":         s.name,
            "level":           f.level_tag,
            "summary":         f.summary,
            "key_concepts":    f.key_concepts,
            "historical_notes":f.historical_notes,
            "innovator_gaps":  f.innovator_gaps,
        }
        for _, f, s, d in top
    ]


# ─────────────────────────────────────────────────────────────
# LAYER 6: NOTEBOOK ENTRIES
# PRIME's own summaries of what he's read
# ─────────────────────────────────────────────────────────────

def _load_notebook_entries(db: Session, keywords: set[str]) -> list[dict]:
    """
    Load the most relevant notebook entries for this message.
    """
    rows = (
        db.query(PrimeNotebookEntry)
        .order_by(desc(PrimeNotebookEntry.updated_at))
        .limit(100)
        .all()
    )

    scored = []
    for r in rows:
        score = _score_relevance(r.title + " " + r.body[:500], keywords)
        if score > 0:
            scored.append((score, r))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = [r for _, r in scored[:NOTEBOOK_TOP_K]]

    return [
        {
            "kind":    r.kind,
            "title":   r.title,
            "body":    r.body[:1000],   # first 1000 chars — cliff notes not full text
            "version": r.version,
        }
        for r in top
    ]


# ─────────────────────────────────────────────────────────────
# MASTER CONTEXT BUILDER
# This is the one function the chat endpoint calls.
# ─────────────────────────────────────────────────────────────

async def build_prime_context(
    message: str,
    db: Session,
    session_id: Optional[str] = None,
) -> dict:
    """
    Assemble the full memory snapshot PRIME sees before responding.

    Returns a structured dict with six layers:
      1. constitution      — who PRIME is (importance >= 8)
      2. raymond_memories  — Raymond's preferences, decisions, history
      3. active_projects   — what we're currently building
      4. conversation_tail — last 20 exchanges (working memory)
      5. foundations       — cliff notes relevant to this message
      6. notebook          — PRIME's own reading summaries

    Called by /prime/chat before the LLM receives a single token.
    Target: < 100ms on warm DB connection.
    """
    keywords = _keywords(message)

    constitution     = _load_constitution(db)
    raymond_memories = _load_raymond_memories(db, keywords)
    active_projects  = _load_active_projects(db)
    conversation_tail= _load_conversation_tail(db, session_id)
    foundations      = _load_foundations(db, keywords)
    notebook         = _load_notebook_entries(db, keywords)

    return {
        "message":          message,
        "keywords":         list(keywords),
        "constitution":     constitution,
        "raymond_memories": raymond_memories,
        "active_projects":  active_projects,
        "conversation_tail":conversation_tail,
        "foundations":      foundations,
        "notebook":         notebook,
        "assembled_at":     datetime.utcnow().isoformat(),
    }


# ─────────────────────────────────────────────────────────────
# CONTEXT → PROMPT FORMATTER
# Converts the context dict into the text block the LLM sees.
# Called by the reasoning core, not by the endpoint directly.
# ─────────────────────────────────────────────────────────────

def format_context_for_llm(context: dict) -> str:
    """
    Format the assembled context into a structured text block
    for injection into the LLM call.

    This is NOT a system prompt — it is dynamic memory, assembled
    fresh every turn. PRIME's identity comes from his memories,
    not from a hardcoded prompt.
    """
    lines = []

    # ── Constitution (identity) ──────────────────────────────
    if context["constitution"]:
        lines.append("## PRIME IDENTITY AND CONSTITUTION")
        for m in context["constitution"]:
            lines.append(f"[{m['kind'].upper()}] {m['subject']}: {m['body']}")
        lines.append("")

    # ── Active Projects ──────────────────────────────────────
    if context["active_projects"]:
        lines.append("## ACTIVE PROJECTS")
        for p in context["active_projects"]:
            lines.append(f"PROJECT: {p['name']}")
            if p["description"]:
                lines.append(f"  {p['description']}")
            if p["goals"]:
                lines.append(f"  Goals: {', '.join(str(g) for g in p['goals'])}")
            if p["decisions"]:
                lines.append(f"  Decisions: {', '.join(str(d) for d in p['decisions'])}")
            if p["open_questions"]:
                lines.append(f"  Open: {', '.join(str(q) for q in p['open_questions'])}")
        lines.append("")

    # ── Raymond's Memories ───────────────────────────────────
    if context["raymond_memories"]:
        lines.append("## RAYMOND — WHAT I KNOW ABOUT HIM")
        for m in context["raymond_memories"]:
            lines.append(f"[{m['kind'].upper()}] {m['subject']}: {m['body']}")
        lines.append("")

    # ── Foundations (cliff notes) ────────────────────────────
    if context["foundations"]:
        lines.append("## RELEVANT KNOWLEDGE (CLIFF NOTES)")
        for f in context["foundations"]:
            lines.append(
                f"[{f['domain']} / {f['subject']} / {f['level']}] "
                f"{f['summary']}"
            )
            if f["key_concepts"]:
                lines.append(f"  Key concepts: {', '.join(f['key_concepts'][:8])}")
        lines.append("")

    # ── Notebook ─────────────────────────────────────────────
    if context["notebook"]:
        lines.append("## MY NOTEBOOK")
        for n in context["notebook"]:
            lines.append(f"[{n['kind'].upper()}] {n['title']}")
            lines.append(f"  {n['body'][:300]}...")
        lines.append("")

    # ── Conversation Tail ────────────────────────────────────
    if context["conversation_tail"]:
        lines.append("## OUR CONVERSATION")
        for turn in context["conversation_tail"]:
            speaker = "Raymond" if turn["speaker"] == "raymond" else "PRIME"
            lines.append(f"{speaker}: {turn['message']}")
        lines.append("")

    # ── Current Message ──────────────────────────────────────
    lines.append("## RAYMOND NOW SAYS")
    lines.append(context["message"])

    return "\n".join(lines)