import textwrap, pathlib

code = textwrap.dedent("""\
    from __future__ import annotations

    import json
    import os
    import uuid
    from datetime import datetime, timezone
    from pathlib import Path
    from typing import Optional

    from fastapi import APIRouter, HTTPException
    from pydantic import BaseModel

    from app.prime.reasoning.endpoints import reasoning_core
    from app.prime.curriculum.models import (
        ReasoningTask,
        ReasoningTaskKind,
        ReasoningCoreRequest,
        ReasoningCoreResponse,
    )

    router = APIRouter(prefix="/prime/chat", tags=["PRIME Chat"])

    CONV_DIR = Path(os.environ.get(
        "PRIME_CONV_DIR",
        Path(__file__).resolve().parent.parent.parent / "primelogs",
    ))
    CONV_DIR.mkdir(parents=True, exist_ok=True)
    CONV_FILE = CONV_DIR / "conversations.jsonl"


    # ── Schemas ──────────────────────────────────────────────────

    class ChatRequest(BaseModel):
        message: str
        session_id: Optional[str] = None
        domain: str = "general"
        subdomain: Optional[str] = None
        allowed_tools: list[str] = []


    class ChatResponse(BaseModel):
        turn_id: str
        session_id: Optional[str]
        key_conclusions: list[str]
        open_questions: list[str]
        step_count: int
        overall_confidence: float
        assembled_at: str


    class RatingRequest(BaseModel):
        turn_id: str
        rating: str
        note: Optional[str] = None


    # ── JSONL storage ────────────────────────────────────────────

    def _append_turn(turn: dict) -> None:
        with open(CONV_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(turn, default=str) + "\\n")


    def _load_turns(session_id: Optional[str] = None, limit: int = 50, offset: int = 0) -> list[dict]:
        if not CONV_FILE.exists():
            return []
        turns = []
        with open(CONV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                entry = json.loads(line)
                if session_id and entry.get("session_id") != session_id:
                    continue
                turns.append(entry)
        return turns[offset : offset + limit]


    # ── Endpoints ────────────────────────────────────────────────

    @router.post("/", response_model=ChatResponse)
    async def prime_chat(req: ChatRequest):
        if not req.message.strip():
            raise HTTPException(400, "Message cannot be empty.")

        turn_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        _append_turn({
            "turn_id": turn_id,
            "speaker": "raymond",
            "message": req.message,
            "session_id": req.session_id,
            "created_at": now,
        })

        task = ReasoningTask(
            task_id="chat-" + turn_id,
            natural_language_task=req.message,
            desired_output_kind=ReasoningTaskKind.ANALYSIS,
            domain_tag=req.domain,
            subdomain_tag=req.subdomain,
            allowed_tools=req.allowed_tools,
            given_facts=[],
            assumptions=[],
            constraints=[],
        )

        core_req = ReasoningCoreRequest(task=task, max_steps=12)
        result: ReasoningCoreResponse = await reasoning_core(core_req)

        _append_turn({
            "turn_id": turn_id,
            "speaker": "prime",
            "message": " | ".join(result.key_conclusions[:3]) if result.key_conclusions else req.message,
            "session_id": req.session_id,
            "key_conclusions": result.key_conclusions,
            "open_questions": result.open_questions,
            "step_count": len(result.trace.steps),
            "confidence": result.trace.overall_confidence,
            "created_at": now,
        })

        return ChatResponse(
            turn_id=turn_id,
            session_id=req.session_id,
            key_conclusions=result.key_conclusions,
            open_questions=result.open_questions,
            step_count=len(result.trace.steps),
            overall_confidence=result.trace.overall_confidence,
            assembled_at=now,
        )


    @router.post("/rate")
    async def rate_response(req: RatingRequest):
        _append_turn({
            "turn_id": req.turn_id,
            "speaker": "system",
            "message": f"Rating: {req.rating}" + (f" - {req.note}" if req.note else ""),
            "rating": req.rating,
            "rating_note": req.note,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        return {"status": "rated", "turn_id": req.turn_id, "rating": req.rating}


    @router.get("/history")
    async def get_history(limit: int = 50, offset: int = 0, session_id: Optional[str] = None):
        turns = _load_turns(session_id=session_id, limit=limit, offset=offset)
        return {
            "total": len(turns),
            "offset": offset,
            "limit": limit,
            "turns": turns,
        }
""")

target = pathlib.Path("app/prime/api/chat.py")
target.write_text(code, encoding="utf-8", newline="\n")
raw = target.read_bytes()
print(f"Null bytes: {raw.count(b'\\x00')}")
print(f"BOM: {raw[:3] == b'\\xef\\xbb\\xbf'}")
print(f"Size: {len(raw)} bytes")
print("SUCCESS")
