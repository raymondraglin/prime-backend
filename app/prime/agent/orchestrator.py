"""
PRIME Agent Orchestrator
File: app/prime/agent/orchestrator.py

The single entrypoint for all chat orchestration.
endpoints.py hands off here; orchestrator returns AgentResponse.

Loop:
  1. detect_intent()           → IntentDecision
  2. load memory + corpus      → context bundle
  3. build_chat_messages()     → formatted message list
  4. chat_with_tools() OR      → LLMResponse
     chat_or_fallback()
  5. persist turn + summarize
  6. return AgentResponse

Design rules:
  - orchestrator never duplicates prompt layering logic (lives in prompt_builder)
  - orchestrator never duplicates tool execution logic (lives in prime_tools)
  - endpoints.py contains zero agent logic after this wiring
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from app.prime.agent.intent import detect_intent, IntentDecision, ToolPolicy
from app.prime.llm import prime_llm
from app.prime.llm.prompt_builder import build_chat_messages
from app.prime.tools.prime_tools import TOOL_DEFINITIONS
from app.prime.memory.store import (
    save_turn,
    load_recent_turns,
    load_all_summaries,
    maybe_summarize,
)
from app.prime.reasoning.memory_store import search_corpus
from app.prime.reasoning.memory import query_recent_practice_for_user


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class AgentRequest(BaseModel):
    session_id: str
    user_id:    str
    message:    str
    route_hint: Optional[str] = None
    stream:     bool = False


class ToolCallRecord(BaseModel):
    tool_name:   str
    args:        dict          = Field(default_factory=dict)
    result:      Any           = None
    duration_ms: float         = 0.0
    error:       Optional[str] = None


class AgentResponse(BaseModel):
    request_id:    str
    session_id:    str
    user_id:       str
    message:       str
    reply:         str
    intent:        str
    engineer_mode: bool
    tool_calls:    list[ToolCallRecord] = Field(default_factory=list)
    tool_rounds:   int                  = 0
    timestamp:     datetime             = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Main agent loop
# ---------------------------------------------------------------------------

async def run_agent(req: AgentRequest) -> AgentResponse:
    """
    Full orchestration loop. Called by endpoints.py for every /chat request.
    """
    request_id = uuid4().hex

    # 1. Classify intent
    decision: IntentDecision = detect_intent(
        req.message,
        route_hint=req.route_hint,
    )

    # 2. Load persistent memory
    summaries    = load_all_summaries(user_id=req.user_id)
    recent_turns = load_recent_turns(user_id=req.user_id)
    persistent_history = [
        {"role": t.role, "content": t.content}
        for t in recent_turns
    ]

    # 3. Load corpus + episodes (skip for pure chat to reduce latency)
    corpus_hits:     list = []
    memory_episodes: list = []
    if decision.intent.value != "general_chat":
        corpus_hits     = search_corpus(req.message, top_k=5)
        memory_episodes = query_recent_practice_for_user(
            user_id=req.user_id,
            domain="philosophy",
            subdomain="ethics",
            limit=5,
        )

    # 4. Build context
    from app.prime.context import build_prime_context
    context = await build_prime_context(
        message=req.message,
        session_id=req.session_id,
    )

    # 5. Build LLM messages
    messages = build_chat_messages(
        user_message=req.message,
        context=context,
        corpus_hits=corpus_hits,
        memory_episodes=memory_episodes,
        conversation_history=persistent_history,
        summaries=[s.summary for s in summaries],
        engineer_mode=decision.engineer_mode,
    )

    # 6. LLM call — tool loop if policy allows/requires, plain chat otherwise
    tool_calls_record: list[ToolCallRecord] = []
    tool_rounds = 0
    reply_text  = ""

    use_tools = (
        decision.tool_policy in (ToolPolicy.ALLOWED, ToolPolicy.REQUIRED)
        and len(decision.allowed_tools) > 0
    )

    if use_tools:
        allowed_defs = [
            t for t in TOOL_DEFINITIONS
            if t["function"]["name"] in decision.allowed_tools
        ]
        try:
            llm_response = await prime_llm.chat_with_tools(
                messages=messages,
                tools=allowed_defs,
                force_first_tool=decision.force_first_tool,
                max_rounds=decision.max_tool_rounds,
            )
            reply_text  = llm_response.text
            tool_rounds = getattr(llm_response, "rounds", 1)

            for tc in (getattr(llm_response, "tool_calls", None) or []):
                tool_calls_record.append(ToolCallRecord(
                    tool_name=tc.get("name", ""),
                    args=tc.get("args", {}),
                    result=tc.get("result"),
                    duration_ms=tc.get("duration_ms", 0.0),
                    error=tc.get("error"),
                ))
        except Exception as exc:
            fallback = await prime_llm.chat_or_fallback(
                messages=messages,
                fallback_text=f"[tool loop error: {exc}]",
            )
            reply_text = fallback.text
    else:
        plain = await prime_llm.chat_or_fallback(
            messages=messages,
            fallback_text=req.message,
        )
        reply_text = plain.text

    # 7. Persist turn with real user_id (not hardcoded default)
    save_turn(session_id=req.session_id, role="user",      content=req.message,   user_id=req.user_id)
    save_turn(session_id=req.session_id, role="assistant", content=reply_text,    user_id=req.user_id)
    await maybe_summarize(user_id=req.user_id)

    return AgentResponse(
        request_id=request_id,
        session_id=req.session_id,
        user_id=req.user_id,
        message=req.message,
        reply=reply_text,
        intent=decision.intent.value,
        engineer_mode=decision.engineer_mode,
        tool_calls=tool_calls_record,
        tool_rounds=tool_rounds,
    )
