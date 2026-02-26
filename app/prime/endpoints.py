from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel

from app.prime.reasoning.prime_personality import (
    PRIME_BRAIN_CONFIG,
    PrimeBrainConfig,
)


router = APIRouter()


class PrimeChatRequest(BaseModel):
    message: str


class PrimeChatResponse(BaseModel):
    prime_id: str
    timestamp: datetime
    reply: str
    personality_snapshot: PrimeBrainConfig


@router.get("/whoami", response_model=dict)
async def whoami():
    """
    Lightweight identity endpoint for PRIME.
    Shows core role and a short summary for control-center.
    """
    identity = PRIME_BRAIN_CONFIG.identity
    return {
        "id": "PRIME",
        "role": "Prime Reasoning Intelligence Management Engine",
        "status": "online",
        "version": "0.1.0",
        "essence": identity.essence,
        "purpose": identity.purpose,
        "primary_counterpart": identity.primary_counterpart,
    }


@router.get("/personality", response_model=PrimeBrainConfig)
async def get_prime_personality() -> PrimeBrainConfig:
    """
    Full personality / brain configuration for PRIME.
    """
    return PRIME_BRAIN_CONFIG


@router.post("/chat", response_model=PrimeChatResponse)
async def prime_chat(payload: PrimeChatRequest):
    """
    Simple chat placeholder that already carries PRIME's brain config,
    so the control center can see and use his personality.
    """
    now = datetime.utcnow()

    # For now, still echo-style, but with personality attached.
    reply_text = f"I hear you: {payload.message}"

    return PrimeChatResponse(
        prime_id="PRIME",
        timestamp=now,
        reply=reply_text,
        personality_snapshot=PRIME_BRAIN_CONFIG,
    )
