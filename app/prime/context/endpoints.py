# app/prime/context/endpoints.py

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_db
from .builder import build_prime_context
from .models import PrimeConversation

router = APIRouter(prefix="/prime", tags=["PRIME Chat"])


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=50_000)
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    context_meta: Optional[dict] = None


async def reasoning_core(message: str, context: dict) -> str:
    """Temporary stub; replace with your real reasoning core."""
    meta = context.get("meta", {})
    return (
        "[PRIME Context Builder Active]\n\n"
        f"Loaded {meta.get('memory_count', 0)} memories, "
        f"{meta.get('project_count', 0)} projects, "
        f"{meta.get('conversation_turns', 0)} conversation turns, "
        f"{meta.get('foundation_count', 0)} foundation notes, "
        f"{meta.get('notebook_count', 0)} notebook entries.\n\n"
        f"Your message: \"{message}\"\n\n"
        "[Replace this stub with your reasoning_core integration]"
    )


@router.post("/chat", response_model=ChatResponse)
async def prime_chat(
    req: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    session_id = req.session_id or str(uuid.uuid4())

    try:
        context = await build_prime_context(
            message=req.message,
            db=db,
            session_id=session_id,
        )

        response_text = await reasoning_core(req.message, context)

        user_msg = PrimeConversation(
            session_id=uuid.UUID(session_id),
            role="raymond",
            content=req.message,
            metadata_={"keywords": context["meta"]["keyword_hits"]},
        )
        prime_msg = PrimeConversation(
            session_id=uuid.UUID(session_id),
            role="prime",
            content=response_text,
            metadata_={
                "context_meta": context["meta"],
                "foundations_used": [f["title"] for f in context["foundations"]],
            },
        )

        db.add_all([user_msg, prime_msg])
        await db.commit()

        return ChatResponse(
            response=response_text,
            session_id=session_id,
            context_meta=context["meta"],
        )

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/context-debug")
async def debug_context(
    message: str = "test",
    db: AsyncSession = Depends(get_db),
):
    """Debug endpoint to see the raw context PRIME would load."""
    context = await build_prime_context(message=message, db=db)
    return context
