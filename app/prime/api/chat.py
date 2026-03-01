"""
PRIME Chat Endpoint
File: app/prime/api/chat.py

The endpoint the chat UI talks to.
Now powered by the full genius engine:
  - PRIME's co-founder identity
  - Multi-turn memory via session_id
  - Tool calling (read_file, search_codebase, query_database)
  - Codebase awareness
  - Inline citation system (citations returned alongside reply)

Dropped: reasoning_core (old system, no identity, no tools, no file access)
Kept: Same URL prefix /prime/chat/ so the frontend needs zero changes.
Kept: /rate and /history endpoints for compatibility.
Fixed: response field is 'reply' (matches what PrimeChatInput.tsx reads)
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from openai import OpenAI
from pydantic import BaseModel, Field

from app.prime.identity import PRIME_IDENTITY
from app.prime.memory.session_store import session_store
from app.prime.tools.prime_tools import TOOL_DEFINITIONS, execute_tool
from app.prime.rag.repo_indexer import build_repo_context_for_prime
from app.prime.context.session_startup import get_session_prime_context

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/prime/chat", tags=["PRIME Chat"])

CONV_DIR = Path(os.environ.get(
    "PRIME_CONV_DIR",
    Path(__file__).resolve().parent.parent.parent / "primelogs",
))
CONV_DIR.mkdir(parents=True, exist_ok=True)
CONV_FILE = CONV_DIR / "conversations.jsonl"

MAX_TOOL_ROUNDS = 8


# ---------------------------------------------------------------------------
# SCHEMAS
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    domain: str = "general"
    subdomain: Optional[str] = None
    allowed_tools: list[str] = []


class ChatResponse(BaseModel):
    turn_id:      str
    session_id:   Optional[str]
    reply:        str
    citations:    list[dict] = Field(default_factory=list)
    assembled_at: str


class RatingRequest(BaseModel):
    turn_id: str
    rating: str
    note: Optional[str] = None


# ---------------------------------------------------------------------------
# STORAGE
# ---------------------------------------------------------------------------

def _append_turn(turn: dict) -> None:
    with open(CONV_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(turn, default=str) + "\n")


def _load_turns(session_id: Optional[str] = None, limit: int = 50, offset: int = 0) -> list[dict]:
    if not CONV_FILE.exists():
        return []
    turns = []
    with open(CONV_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except Exception:
                continue
            if session_id and entry.get("session_id") != session_id:
                continue
            turns.append(entry)
    return turns[offset: offset + limit]


# ---------------------------------------------------------------------------
# CORE CHAT CALL
# ---------------------------------------------------------------------------

def _run_chat(message: str, session_id: Optional[str], goal_context: str = "") -> tuple[str, list[dict]]:
    """
    Full genius engine with citation extraction.
    Returns (reply_text, citations).
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    model  = os.getenv("PRIME_MODEL", "gpt-4o")

    repo_context = build_repo_context_for_prime(slim=True)
    if "NOT BUILT" in repo_context:
        system_prompt = (
            PRIME_IDENTITY
            + "\nNote: Repo index not yet built. "
            + "Run POST /prime/repo/index for full codebase awareness.\n"
        )
    else:
        system_prompt = (
            PRIME_IDENTITY
            + "\n==============================================================================\n"
            + "OUR CODEBASE\n"
            + "==============================================================================\n"
            + repo_context
            + "\nUse read_file(path) to read any file. "
            + "Use search_codebase to find patterns. "
            + "Read before answering -- never guess about our code.\n"
        )
    if goal_context:
        system_prompt = goal_context + "\n\n" + system_prompt

    # Inject citation rules
    from app.prime.llm.prompt_builder import CITATION_RULES
    system_prompt += CITATION_RULES

    history  = session_store.get_history(session_id) if session_id else []
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": message})

    citations: list[dict] = []

    for round_num in range(MAX_TOOL_ROUNDS):
        is_last = (round_num == MAX_TOOL_ROUNDS - 1)
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=TOOL_DEFINITIONS,
            tool_choice="none" if is_last else "auto",
            temperature=0.3,
            max_completion_tokens=4096 if is_last else 512,
        )
        msg = response.choices[0].message

        if not msg.tool_calls:
            raw = msg.content or ""
            from app.prime.citations.extractor import extract_citations
            clean, cite_objs = extract_citations(raw)
            citations = [c.to_dict() for c in cite_objs]
            return clean, citations

        messages.append(msg)
        for tc in msg.tool_calls:
            result = execute_tool(tc.function.name, json.loads(tc.function.arguments))
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

    # Safety net
    messages.append({"role": "user", "content": "Write your complete answer now."})
    response = client.chat.completions.create(
        model=model, messages=messages, temperature=0.3, max_completion_tokens=4096
    )
    raw = response.choices[0].message.content or ""
    from app.prime.citations.extractor import extract_citations
    clean, cite_objs = extract_citations(raw)
    return clean, [c.to_dict() for c in cite_objs]


# ---------------------------------------------------------------------------
# ENDPOINTS
# ---------------------------------------------------------------------------
async def _post_reply_goal_hook(
    reply: str,
    session_id: Optional[str],
    active_goals: list[dict],
) -> None:
    if not active_goals or not reply:
        return

    reply_lower = reply.lower()

    COMPLETION_SIGNALS = [
        "push 1 complete", "push 2 complete", "push 3 complete",
        "push 4 complete", "push 5 complete", "push 6 complete",
        "is done", "is complete", "has been completed",
        "successfully wired", "successfully committed",
        "closed", "shipped", "\u2705",
    ]

    PROGRESS_SIGNALS = [
        "created", "updated", "fixed", "added", "wired",
        "committed", "pushed", "tested", "verified", "loaded",
        "patched", "saved", "deployed",
    ]

    for goal in active_goals:
        gid   = goal.get("id", "")
        title = goal.get("title", "").lower()

        if not gid or not title:
            continue

        title_words = [w for w in title.split() if len(w) > 3]
        mentioned   = any(w in reply_lower for w in title_words)
        if not mentioned:
            continue

        is_complete  = any(sig in reply_lower for sig in COMPLETION_SIGNALS)
        has_progress = any(sig in reply_lower for sig in PROGRESS_SIGNALS)

        try:
            if is_complete:
                from app.prime.goals.store import complete_goal
                await complete_goal(gid, outcome=reply[:300])
            elif has_progress:
                from app.prime.goals.store import add_progress_note
                note = f"Session {session_id or 'unknown'}: {reply[:200]}"
                await add_progress_note(gid, note=note)
        except Exception as exc:
            logger.warning("Goal hook failed for %s: %s", gid, exc)


@router.post("/", response_model=ChatResponse)
async def prime_chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(400, "Message cannot be empty.")

    turn_id = str(uuid.uuid4())
    now     = datetime.now(timezone.utc).isoformat()

    _append_turn({
        "turn_id":    turn_id,
        "speaker":    "raymond",
        "message":    req.message,
        "session_id": req.session_id,
        "created_at": now,
    })

    try:
        session_ctx  = await get_session_prime_context(user_id="raymond")
        reply, citations = _run_chat(req.message, req.session_id, session_ctx["goal_context"])

        active_goals = session_ctx.get("goals_raw") or []
        await _post_reply_goal_hook(reply, req.session_id, active_goals)

    except Exception as e:
        raise HTTPException(500, str(e))

    if req.session_id:
        session_store.add_message(req.session_id, "user",      req.message)
        session_store.add_message(req.session_id, "assistant", reply)

    _append_turn({
        "turn_id":    turn_id,
        "speaker":    "prime",
        "message":    reply,
        "citations":  citations,
        "session_id": req.session_id,
        "created_at": now,
    })

    return ChatResponse(
        turn_id=turn_id,
        session_id=req.session_id,
        reply=reply,
        citations=citations,
        assembled_at=now,
    )


@router.post("/rate")
async def rate_response(req: RatingRequest):
    _append_turn({
        "turn_id":      req.turn_id,
        "speaker":      "system",
        "message":      f"Rating: {req.rating}" + (f" - {req.note}" if req.note else ""),
        "rating":       req.rating,
        "rating_note":  req.note,
        "created_at":   datetime.now(timezone.utc).isoformat(),
    })
    return {"status": "rated", "turn_id": req.turn_id, "rating": req.rating}


@router.get("/history")
async def get_history(limit: int = 50, offset: int = 0, session_id: Optional[str] = None):
    turns = _load_turns(session_id=session_id, limit=limit, offset=offset)
    return {"total": len(turns), "offset": offset, "limit": limit, "turns": turns}
