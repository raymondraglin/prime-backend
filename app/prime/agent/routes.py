"""
PRIME Agent Routes
File: app/prime/agent/routes.py

Exposes the orchestrator over HTTP:
  POST /prime/agent/chat    -- full tool loop, returns AgentResponse JSON
  POST /prime/agent/stream  -- streaming SSE variant (no tool loop)

The heavy logic lives in orchestrator.py.
This file contains zero agent logic -- just HTTP plumbing.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.prime.agent.orchestrator import AgentRequest, AgentResponse, run_agent, run_agent_stream

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/prime/agent", tags=["PRIME Agent"])


@router.post("/chat", response_model=AgentResponse)
async def agent_chat(req: AgentRequest) -> AgentResponse:
    """
    Full agent loop with intent classification, tool calling, and memory.
    Use this for engineer-mode requests, tool-required tasks, and any
    request where PRIME needs to read files or search the codebase.
    """
    try:
        return await run_agent(req)
    except Exception as exc:
        logger.exception("Agent chat failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/stream")
async def agent_stream(req: AgentRequest) -> StreamingResponse:
    """
    Streaming SSE variant. Returns text/event-stream.
    Use for conversational turns where low latency matters more than tools.

    Client reads:
      data: {"chunk": "..."}
      data: [DONE]
    """
    try:
        return await run_agent_stream(req)
    except Exception as exc:
        logger.exception("Agent stream failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
