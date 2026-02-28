"""
PRIME Endpoints
File: app/prime/endpoints.py

All chat orchestration is delegated to app.prime.agent.orchestrator.
This file owns only:
  - FastAPI routing and request/response models
  - Auth dependency injection
  - Mapping AgentResponse → PrimeChatResponse for backward compat

Version: 0.4.0 — streaming + observability wired
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.auth import get_current_user
from app.prime.agent.orchestrator import run_agent, run_agent_stream, AgentRequest
from app.prime.reasoning.prime_personality import PRIME_BRAIN_CONFIG, PrimeBrainConfig
from app.prime.curriculum.models import (
    ReasoningTrace,
    ReasoningStep,
    ReasoningStepKind,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class PrimeChatRequest(BaseModel):
    message:    str
    session_id: Optional[str] = None


class PrimeChatResponse(BaseModel):
    prime_id:             str
    session_id:           str
    timestamp:            datetime
    reply:                str
    personality_snapshot: PrimeBrainConfig
    reasoning_trace:      Optional[ReasoningTrace] = None


# ---------------------------------------------------------------------------
# Identity endpoints (no auth required)
# ---------------------------------------------------------------------------

@router.get("/whoami", response_model=dict)
async def whoami(current_user: dict = Depends(get_current_user)):
    identity = PRIME_BRAIN_CONFIG.identity
    return {
        "id":                   "PRIME",
        "role":                 "Prime Reasoning Intelligence Management Engine",
        "status":               "online",
        "version":              "0.4.0",
        "essence":              identity.essence,
        "purpose":              identity.purpose,
        "primary_counterpart": identity.primary_counterpart,
    }


@router.get("/personality", response_model=PrimeBrainConfig)
async def get_prime_personality(
    current_user: dict = Depends(get_current_user),
) -> PrimeBrainConfig:
    return PRIME_BRAIN_CONFIG


# ---------------------------------------------------------------------------
# /chat — AUTH REQUIRED — Orchestrator-wired
# ---------------------------------------------------------------------------

@router.post("/chat", response_model=PrimeChatResponse)
async def prime_chat(
    payload:      PrimeChatRequest,
    current_user: dict = Depends(get_current_user),
):
    user_id    = current_user["user_id"]
    session_id = payload.session_id or uuid4().hex

    agent_req = AgentRequest(
        session_id=session_id,
        user_id=user_id,
        message=payload.message,
    )

    agent_resp = await run_agent(agent_req)

    tool_names = [tc.tool_name for tc in agent_resp.tool_calls]
    trace = ReasoningTrace(
        steps=[
            ReasoningStep(
                index=0,
                kind=ReasoningStepKind.INTERPRET,
                description=f"Intent classified: {agent_resp.intent}",
                inputs=[],
                outputs=[
                    f"intent:        {agent_resp.intent}",
                    f"engineer_mode: {agent_resp.engineer_mode}",
                    f"tool_rounds:   {agent_resp.tool_rounds}",
                    f"tools_called:  {tool_names}",
                    f"request_id:    {agent_resp.request_id}",
                ],
                confidence=0.95,
            ),
        ],
        overall_confidence=0.95,
        detected_contradictions=[],
        notes=["Orchestrated via agent loop v0.4"],
    )

    return PrimeChatResponse(
        prime_id="PRIME",
        session_id=agent_resp.session_id,
        timestamp=datetime.utcnow(),
        reply=agent_resp.reply,
        personality_snapshot=PRIME_BRAIN_CONFIG,
        reasoning_trace=trace,
    )


# ---------------------------------------------------------------------------
# /chat/stream — AUTH REQUIRED — SSE streaming
# ---------------------------------------------------------------------------

@router.post("/chat/stream")
async def prime_chat_stream(
    payload:      PrimeChatRequest,
    current_user: dict = Depends(get_current_user),
):
    user_id    = current_user["user_id"]
    session_id = payload.session_id or uuid4().hex

    agent_req = AgentRequest(
        session_id=session_id,
        user_id=user_id,
        message=payload.message,
        stream=True,
    )
    return await run_agent_stream(agent_req)
