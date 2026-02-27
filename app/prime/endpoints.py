from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.auth import get_current_user  # ← ADD THIS
from app.prime.context import build_prime_context

from app.prime.reasoning.prime_personality import (
    PRIME_BRAIN_CONFIG,
    PrimeBrainConfig,
)
from app.prime.reasoning.personality_policy import (
    is_high_stakes_task,
    enrich_core_response_with_personality,
)
from app.prime.reasoning.memory_store import (
    search_corpus,
    append_memory_entry,
)
from app.prime.reasoning.memory import (
    save_practice_to_memory,
    query_recent_practice_for_user,
)
from app.prime.curriculum.models import (
    ReasoningTask,
    ReasoningTaskKind,
    ReasoningStep,
    ReasoningStepKind,
    ReasoningTrace,
    ReasoningCoreRequest,
    ReasoningCoreResponse,
    ReasoningTraceTag,
    ReasoningOutcomeQuality,
    ReasoningMemoryEntry,
)

from app.prime.llm import prime_llm
from app.prime.llm.prompt_builder import build_chat_messages
from app.prime.memory.store import (
    save_turn,
    load_recent_turns,
    load_all_summaries,
    maybe_summarize,
)

router = APIRouter()

from collections import defaultdict
_session_history: dict[str, list[dict[str, str]]] = defaultdict(list)


class PrimeChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class PrimeChatResponse(BaseModel):
    prime_id: str
    session_id: str
    timestamp: datetime
    reply: str
    personality_snapshot: PrimeBrainConfig
    reasoning_trace: Optional[ReasoningTrace] = None


# ── Identity endpoints — NO auth required ──────────────────────────────────

@router.get("/whoami", response_model=dict)
async def whoami(current_user: dict = Depends(get_current_user)):
    identity = PRIME_BRAIN_CONFIG.identity
    return {
        "id": "PRIME",
        "role": "Prime Reasoning Intelligence Management Engine",
        "status": "online",
        "version": "0.2.0",
        "essence": identity.essence,
        "purpose": identity.purpose,
        "primary_counterpart": identity.primary_counterpart,
    }


@router.get("/personality", response_model=PrimeBrainConfig)
async def get_prime_personality(
    current_user: dict = Depends(get_current_user),
) -> PrimeBrainConfig:
    return PRIME_BRAIN_CONFIG

# ── /chat — AUTH REQUIRED ──────────────────────────────────────────────────

@router.post("/chat", response_model=PrimeChatResponse)
async def prime_chat(
    payload: PrimeChatRequest,
    current_user: dict = Depends(get_current_user),  # ← LOCKS THE ROUTE
):
    user_id = current_user["user_id"]  # ← USE REAL USER, not hardcoded "raymond"

    # ── 1. Session ────────────────────────────────────────────────────────
    session_id = payload.session_id or uuid4().hex
    history = _session_history[session_id]

    # ── 2. Context ────────────────────────────────────────────────────────
    context = await build_prime_context(
        message=payload.message,
        session_id=session_id,
    )

    # ── 3. Conversational intent check ────────────────────────────────────
    SKIP_CORPUS_PHRASES = [
        "do you know who i am", "who are you", "who am i",
        "i am raymond", "this is raymond", "are you there",
        "hello", "hey prime", "hi prime", "hey", "hi",
        "yes it's me", "yes its me", "it's me raymond",
    ]
    _msg_lower = payload.message.lower().strip()
    _is_conversational = (
        any(phrase in _msg_lower for phrase in SKIP_CORPUS_PHRASES)
        or len(payload.message.split()) <= 5
    )

    # ── 4. Corpus + memory ────────────────────────────────────────────────
    corpus_hits = []
    corpus_notes: list[str] = []
    recent = []
    memory_notes: list[str] = []

    if not _is_conversational:
        corpus_hits = search_corpus(payload.message, top_k=5)
        if corpus_hits:
            for i, hit in enumerate(corpus_hits, 1):
                meta = hit.get("metadata", {}) or {}
                src = meta.get("source_path", "unknown")
                preview = (hit.get("text") or "").strip().replace("\n", " ")[:280]
                corpus_notes.append(f"[{i}] {src} :: {preview}")

        recent = query_recent_practice_for_user(
            user_id=user_id,  # ← dynamic
            domain="philosophy",
            subdomain="ethics",
            limit=5,
        )
        if recent:
            for entry in recent[:3]:
                memory_notes.append(
                    f"Past episode {entry.id}: "
                    f"domain={entry.tags.domain}, "
                    f"subdomain={entry.tags.subdomain}, "
                    f"quality={entry.outcome_quality}"
                )

    # ── 5. Build reasoning trace ──────────────────────────────────────────
    steps: list[ReasoningStep] = []
    notes: list[str] = []
    contradictions: list[str] = []
    next_idx = 0

    steps.append(ReasoningStep(
        index=next_idx,
        kind=ReasoningStepKind.INTERPRET,
        description="Interpret the user message, restate the goal.",
        inputs=[],
        outputs=[
            f"User said: {payload.message}",
            f"Session: {session_id}",
            f"Prior turns in session: {len(history)}",
        ],
        confidence=0.85,
    ))
    next_idx += 1

    if corpus_notes:
        steps.append(ReasoningStep(
            index=next_idx,
            kind=ReasoningStepKind.TOOL_CALL,
            description="Consult PRIME corpus for relevant background.",
            inputs=[payload.message],
            outputs=corpus_notes,
            confidence=0.82,
        ))
        next_idx += 1
        notes.append("Corpus consulted; relevant material found.")

    if memory_notes:
        steps.append(ReasoningStep(
            index=next_idx,
            kind=ReasoningStepKind.DECOMPOSE,
            description="Recall similar reasoning episodes from memory.",
            inputs=[payload.message],
            outputs=memory_notes,
            confidence=0.75,
        ))
        next_idx += 1
        notes.append("Similar past reasoning episodes recalled.")

    ctx_summary = []
    if context.get("identity"):
        ctx_summary.append(f"Identity loaded: {PRIME_BRAIN_CONFIG.identity.name}")
    if context.get("session_id"):
        ctx_summary.append(f"Session continuity: {session_id}")

    steps.append(ReasoningStep(
        index=next_idx,
        kind=ReasoningStepKind.DEDUCE,
        description="Summarise live context: identity, session, corpus, memory.",
        inputs=[],
        outputs=ctx_summary,
        confidence=0.9,
    ))
    next_idx += 1

    steps.append(ReasoningStep(
        index=next_idx,
        kind=ReasoningStepKind.CRITIQUE,
        description="Check for gaps: missing perspectives, stakeholders, or values.",
        inputs=[s.description for s in steps],
        outputs=[
            "Verify no important angle is ignored.",
            "Flag if high-stakes escalation is needed.",
        ],
        confidence=0.7,
    ))
    next_idx += 1

    key_conclusions: list[str] = []
    open_questions: list[str] = []

    if corpus_notes:
        key_conclusions.append(f"Corpus provided {len(corpus_notes)} relevant passages.")
    if memory_notes:
        key_conclusions.append(f"Found {len(memory_notes)} related past reasoning episodes.")

    steps.append(ReasoningStep(
        index=next_idx,
        kind=ReasoningStepKind.SUMMARIZE,
        description="Summarise conclusions and open questions.",
        inputs=[s.description for s in steps],
        outputs=[
            f"Conclusions: {key_conclusions}",
            f"Open questions: {open_questions}",
        ],
        confidence=0.8,
    ))

    trace = ReasoningTrace(
        steps=steps,
        overall_confidence=0.8,
        detected_contradictions=contradictions,
        notes=notes,
    )

    task = ReasoningTask(
        task_id=f"chat-{session_id}-{uuid4().hex[:8]}",
        natural_language_task=payload.message,
        desired_output_kind=ReasoningTaskKind.EXPLANATION,
        allowed_tools=[],
    )

    core_response = ReasoningCoreResponse(
        task_id=task.task_id,
        trace=trace,
        key_conclusions=key_conclusions,
        open_questions=open_questions,
    )

    meta_escalate = is_high_stakes_task(task)
    core_response = enrich_core_response_with_personality(
        task=task,
        response=core_response,
        meta_should_escalate=meta_escalate,
    )

    # ── 6. Load persistent memory ─────────────────────────────────────────
    summaries = load_all_summaries(user_id=user_id)       # ← dynamic
    recent_turns = load_recent_turns(user_id=user_id)     # ← dynamic

    persistent_history = [
        {"role": t.role, "content": t.content}
        for t in recent_turns
    ]

    # ── 7. Build messages ─────────────────────────────────────────────────
    llm_messages = build_chat_messages(
        user_message=payload.message,
        context=context,
        corpus_hits=corpus_hits,
        memory_episodes=recent,
        trace_steps=steps,
        conversation_history=persistent_history,
        summaries=[s.summary for s in summaries],
    )

    fallback_text = "\n".join(core_response.key_conclusions)

    llm_response = await prime_llm.chat_or_fallback(
        messages=llm_messages,
        fallback_text=fallback_text,
    )
    reply_text = llm_response.text

    # ── 8. Save this turn permanently ─────────────────────────────────────
    save_turn(session_id=session_id, role="user", content=payload.message)
    save_turn(session_id=session_id, role="assistant", content=reply_text)

    # ── 9. Summarize if threshold hit ─────────────────────────────────────
    await maybe_summarize(user_id=user_id)  # ← dynamic

    return PrimeChatResponse(
        prime_id="PRIME",
        session_id=session_id,
        timestamp=datetime.utcnow(),
        reply=reply_text,
        personality_snapshot=PRIME_BRAIN_CONFIG,
        reasoning_trace=trace,
    )
