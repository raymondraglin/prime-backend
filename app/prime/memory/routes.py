# app/prime/memory/routes.py
"""
PRIME Memory Endpoints

POST /prime/memory/save
  Save a conversation turn (user + assistant messages).

POST /prime/memory/search
  Semantic search across all stored conversation turns.

GET  /prime/memory/session/{session_id}
  Retrieve full conversation history for a session.

GET  /prime/memory/recent
  Get the most recent N turns for a user (cross-session context).

GET  /prime/memory/stats
  Return memory system stats: total turns, embeddings count, users.
"""
from __future__ import annotations

from typing import Optional
import uuid

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter(prefix="/prime/memory", tags=["PRIME Memory"])


class SaveTurnRequest(BaseModel):
    user_message:      str
    assistant_message: str
    session_id:        Optional[str] = None
    user_id:           str           = "raymond"
    model:             Optional[str] = None
    tokens_used:       Optional[int] = None
    tool_calls:        list[dict]    = Field(default_factory=list)
    citations:         list[dict]    = Field(default_factory=list)
    metadata:          dict          = Field(default_factory=dict)


class SaveTurnResponse(BaseModel):
    turn_id:    int
    session_id: str
    message:    str


class SearchMemoryRequest(BaseModel):
    query:   str
    k:       int            = 5
    user_id: Optional[str] = None


class SearchMemoryResponse(BaseModel):
    query:   str
    results: list[dict]
    count:   int


@router.post("/save", response_model=SaveTurnResponse)
async def save_turn(req: SaveTurnRequest):
    """Save a conversation turn and generate its embedding."""
    try:
        from app.prime.memory.store import save_conversation_turn

        turn_id = save_conversation_turn(
            user_message      = req.user_message,
            assistant_message = req.assistant_message,
            session_id        = req.session_id,
            user_id           = req.user_id,
            model             = req.model,
            tokens_used       = req.tokens_used,
            tool_calls        = req.tool_calls,
            citations         = req.citations,
            metadata          = req.metadata,
        )

        session_id_str = req.session_id if req.session_id else str(uuid.uuid4())

        return SaveTurnResponse(
            turn_id    = turn_id,
            session_id = session_id_str,
            message    = "Conversation turn saved.",
        )

    except Exception as exc:
        raise HTTPException(500, f"Memory save error: {exc}") from exc


@router.post("/search", response_model=SearchMemoryResponse)
async def search_memory(req: SearchMemoryRequest):
    """Semantic search across all stored conversation turns."""
    if not req.query.strip():
        raise HTTPException(400, "Query cannot be empty.")
    try:
        from app.prime.memory.store import search_memories

        results = search_memories(
            query   = req.query,
            k       = req.k,
            user_id = req.user_id,
        )

        return SearchMemoryResponse(
            query   = req.query,
            results = results,
            count   = len(results),
        )

    except Exception as exc:
        raise HTTPException(500, f"Memory search error: {exc}") from exc


@router.get("/session/{session_id}")
async def get_session_history(session_id: str, limit: int = Query(50, ge=1, le=200)):
    """Retrieve full conversation history for a session."""
    try:
        from app.prime.memory.store import get_conversation_history

        history = get_conversation_history(session_id=session_id, limit=limit)

        return {
            "session_id": session_id,
            "turns":      history,
            "count":      len(history),
        }

    except Exception as exc:
        raise HTTPException(500, f"History retrieval error: {exc}") from exc


@router.get("/recent")
async def get_recent_turns(user_id: str = "raymond", limit: int = Query(10, ge=1, le=50)):
    """Get the most recent N turns for a user (cross-session context)."""
    try:
        from app.prime.memory.store import get_recent_context

        recent = get_recent_context(user_id=user_id, limit=limit)

        return {
            "user_id": user_id,
            "turns":   recent,
            "count":   len(recent),
        }

    except Exception as exc:
        raise HTTPException(500, f"Recent context error: {exc}") from exc


@router.get("/stats")
async def get_memory_stats():
    """Return memory system statistics."""
    try:
        from app.prime.memory.models import ConversationTurn, MemoryEmbedding
        from app.prime.memory.store import _get_engine
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy import func, distinct

        engine  = _get_engine()
        Session = sessionmaker(bind=engine)
        session = Session()

        total_turns  = session.query(func.count(ConversationTurn.id)).scalar() or 0
        total_embeds = session.query(func.count(MemoryEmbedding.turn_id)).scalar() or 0
        unique_users = session.query(func.count(distinct(ConversationTurn.user_id))).scalar() or 0
        unique_sessions = session.query(func.count(distinct(ConversationTurn.session_id))).scalar() or 0

        session.close()

        return {
            "total_turns":      total_turns,
            "total_embeddings": total_embeds,
            "unique_users":     unique_users,
            "unique_sessions":  unique_sessions,
        }

    except Exception as exc:
        raise HTTPException(500, str(exc)) from exc
