"""
PRIME Genius Endpoints
File: app/prime/api/genius.py

All capability gaps closed:
  [1] True identity    -- PRIME knows he is co-founder of Synergy Unlimited
  [2] Multi-turn memory -- session_id persists conversation across calls
  [3] RAG codebase access -- PRIME reads actual files via tool calling
  [4] Tool calling     -- read_file, list_directory, search_codebase, query_database

Endpoints:
  POST /prime/ask                      -- Ask PRIME anything (8 modes, memory, tools)
  POST /prime/debug                    -- Debug broken code
  POST /prime/explain                  -- Explain any concept
  POST /prime/generate                 -- Generate code from description
  POST /prime/review                   -- Review code
  POST /prime/architect                -- Design a system
  POST /prime/security                 -- Threat model and harden
  GET  /prime/status                   -- PRIME status
  GET  /prime/sessions                 -- List all sessions
  GET  /prime/sessions/{session_id}    -- Get conversation history
  DELETE /prime/sessions/{session_id}  -- Clear a session
  POST /prime/sessions/new             -- Create a new session ID
  GET  /prime/identity                 -- Read PRIME's full identity
"""

from __future__ import annotations

import json
import os
import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from openai import OpenAI

from app.prime.identity import PRIME_IDENTITY, get_identity_with_mode
from app.prime.memory.session_store import session_store
from app.prime.tools.prime_tools import TOOL_DEFINITIONS, execute_tool

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/prime", tags=["PRIME Genius"])


# ---------------------------------------------------------------------------
# MODE INSTRUCTIONS
# ---------------------------------------------------------------------------

MODE_PROMPTS = {
    "general": (
        "Answer as PRIME: co-founder and elite engineer. Be direct, expert, invested.\n"
        "Think about the business impact, not just the technical answer.\n"
        "Use tools when the question involves specific files or code."
    ),
    "debug": (
        "DEBUG MODE: You are debugging OUR code. This is your codebase.\n"
        "1. Read the file if you need context.\n"
        "2. Find the ROOT CAUSE -- not the symptom.\n"
        "3. Show the exact fix.\n"
        "4. Explain WHY this fix works.\n"
        "5. Note anything else that needs attention."
    ),
    "explain": (
        "EXPLAIN MODE: Explain as a co-founder teaching a critical concept.\n"
        "1. One-sentence definition.\n"
        "2. How it actually works.\n"
        "3. A concrete example from OUR stack.\n"
        "4. The most important gotcha."
    ),
    "generate": (
        "GENERATE MODE: Write production code for OUR company.\n"
        "Standards: PEP 8, Pydantic, FastAPI patterns, parameterized SQL, secure defaults.\n"
        "Read existing files first so the new code fits our patterns exactly."
    ),
    "review": (
        "REVIEW MODE: Review OUR code like a co-founder who cares about the outcome.\n"
        "Rate each issue: Critical / High / Medium / Low.\n"
        "Check: bugs, security, performance, correctness, maintainability.\n"
        "Read the actual file before commenting."
    ),
    "architecture": (
        "ARCHITECTURE MODE: Design systems for OUR company's mission.\n"
        "1. State the core tradeoffs.\n"
        "2. Design the components and interactions.\n"
        "3. Explain every decision.\n"
        "4. Name the failure modes.\n"
        "5. Define the MVP -- what we build first."
    ),
    "security": (
        "SECURITY MODE: Think like the best hacker alive -- then harden against them.\n"
        "This is OUR company's data, OUR users, OUR reputation.\n"
        "Identify every attack surface. Name specific vectors. Rate severity.\n"
        "Give exact hardening fixes. No vague advice."
    ),
    "teach": (
        "TEACH MODE: Raymond is a self-taught developer building an empire.\n"
        "Start with WHY. Build from what he already knows.\n"
        "Use examples from OUR stack. End with one concrete thing to try."
    ),
}

VALID_MODES = list(MODE_PROMPTS.keys())
MAX_TOOL_ROUNDS = 5


# ---------------------------------------------------------------------------
# CORE LLM CALL
# ---------------------------------------------------------------------------

def _call_prime(
    question: str,
    mode: str = "general",
    history: Optional[List[dict]] = None,
    use_tools: bool = True,
) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    model = os.getenv("PRIME_MODEL", "gpt-4o")

    system_prompt = get_identity_with_mode(MODE_PROMPTS.get(mode, MODE_PROMPTS["general"]))

    messages = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": question})

    tools = TOOL_DEFINITIONS if use_tools else None

    for _ in range(MAX_TOOL_ROUNDS):
        kwargs = {"model": model, "messages": messages, "temperature": 0.3, "max_tokens": 4096}
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        response = client.chat.completions.create(**kwargs)
        msg = response.choices[0].message

        if not msg.tool_calls:
            return msg.content or ""

        messages.append(msg)
        for tc in msg.tool_calls:
            result = execute_tool(tc.function.name, json.loads(tc.function.arguments))
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

    # Force final answer
    messages.append({"role": "user", "content": "Write your complete answer now."})
    response = client.chat.completions.create(
        model=model, messages=messages, temperature=0.3, max_tokens=4096
    )
    return response.choices[0].message.content or ""


# ---------------------------------------------------------------------------
# REQUEST / RESPONSE MODELS
# ---------------------------------------------------------------------------

class AskRequest(BaseModel):
    question: str
    mode: str = Field(default="general")
    session_id: Optional[str] = Field(default=None)
    use_tools: bool = Field(default=True)

class DebugRequest(BaseModel):
    code: str
    error: str = Field(default="")
    language: str = Field(default="python")
    context: str = Field(default="")
    session_id: Optional[str] = Field(default=None)

class ExplainRequest(BaseModel):
    topic: str
    language: Optional[str] = Field(default=None)
    level: str = Field(default="engineer")
    session_id: Optional[str] = Field(default=None)

class GenerateRequest(BaseModel):
    description: str
    language: str = Field(default="python")
    framework: str = Field(default="")
    requirements: Optional[List[str]] = Field(default=None)
    session_id: Optional[str] = Field(default=None)

class ReviewRequest(BaseModel):
    code: str = Field(default="")
    file_path: Optional[str] = Field(default=None)
    language: str = Field(default="python")
    focus: Optional[List[str]] = Field(default=None)
    session_id: Optional[str] = Field(default=None)

class ArchitectRequest(BaseModel):
    description: str
    constraints: Optional[List[str]] = Field(default=None)
    scale: str = Field(default="startup")
    session_id: Optional[str] = Field(default=None)

class ThreatModelRequest(BaseModel):
    system_description: str
    code: str = Field(default="")
    file_path: Optional[str] = Field(default=None)
    session_id: Optional[str] = Field(default=None)

class PRIMEResponse(BaseModel):
    answer: str
    mode: str
    model: str
    session_id: Optional[str] = None


# ---------------------------------------------------------------------------
# MEMORY HELPER
# ---------------------------------------------------------------------------

def _with_memory(session_id, question, mode, use_tools=True):
    history = session_store.get_history(session_id) if session_id else None
    answer = _call_prime(question=question, mode=mode, history=history, use_tools=use_tools)
    if session_id:
        session_store.add_message(session_id, "user", question)
        session_store.add_message(session_id, "assistant", answer)
    return answer, session_id


# ---------------------------------------------------------------------------
# ENDPOINTS
# ---------------------------------------------------------------------------

@router.get("/identity", summary="Read PRIME's full identity")
async def prime_identity():
    """Returns the complete identity document that defines who PRIME is."""
    return {"identity": PRIME_IDENTITY}


@router.get("/status", summary="PRIME status and capabilities")
async def prime_status():
    return {
        "status": "online",
        "name": "PRIME",
        "role": "Co-founder and Principal Engineer, Synergy Unlimited LLC",
        "model": os.getenv("PRIME_MODEL", "gpt-4o"),
        "modes": VALID_MODES,
        "tools": [t["function"]["name"] for t in TOOL_DEFINITIONS],
        "capabilities": [
            "Co-founder identity -- answers as an owner, not an assistant",
            "Multi-turn memory -- pass session_id to any endpoint",
            "RAG codebase access -- reads files autonomously",
            "Tool calling -- read_file, list_directory, search_codebase, query_database",
        ],
    }


@router.post("/ask", response_model=PRIMEResponse)
async def ask_prime(req: AskRequest):
    if req.mode not in VALID_MODES:
        raise HTTPException(400, f"Invalid mode. Choose from: {VALID_MODES}")
    try:
        answer, sid = _with_memory(req.session_id, req.question, req.mode, req.use_tools)
        return PRIMEResponse(answer=answer, mode=req.mode, model=os.getenv("PRIME_MODEL", "gpt-4o"), session_id=sid)
    except Exception as e:
        logger.error("PRIME /ask error: %s", e)
        raise HTTPException(500, str(e))


@router.post("/debug", response_model=PRIMEResponse)
async def debug_code(req: DebugRequest):
    parts = []
    if req.context:
        parts.append(f"CONTEXT: {req.context}")
    parts.append(f"LANGUAGE: {req.language}")
    parts.append(f"\nCODE:\n```{req.language}\n{req.code}\n```")
    if req.error:
        parts.append(f"\nERROR:\n{req.error}")
    parts.append("Find the root cause and fix it.")
    try:
        answer, sid = _with_memory(req.session_id, "\n".join(parts), "debug")
        return PRIMEResponse(answer=answer, mode="debug", model=os.getenv("PRIME_MODEL", "gpt-4o"), session_id=sid)
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/explain", response_model=PRIMEResponse)
async def explain_concept(req: ExplainRequest):
    mode = "teach" if req.level == "student" else "explain"
    parts = [f"Explain: {req.topic}"]
    if req.language:
        parts.append(f"Language: {req.language}")
    parts.append(f"Level: {req.level}")
    try:
        answer, sid = _with_memory(req.session_id, "\n".join(parts), mode)
        return PRIMEResponse(answer=answer, mode=mode, model=os.getenv("PRIME_MODEL", "gpt-4o"), session_id=sid)
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/generate", response_model=PRIMEResponse)
async def generate_code(req: GenerateRequest):
    parts = [f"Generate: {req.description}", f"Language: {req.language}"]
    if req.framework:
        parts.append(f"Framework: {req.framework}")
    if req.requirements:
        parts.append("Requirements:\n" + "\n".join(f"  - {r}" for r in req.requirements))
    try:
        answer, sid = _with_memory(req.session_id, "\n".join(parts), "generate")
        return PRIMEResponse(answer=answer, mode="generate", model=os.getenv("PRIME_MODEL", "gpt-4o"), session_id=sid)
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/review", response_model=PRIMEResponse)
async def review_code(req: ReviewRequest):
    if req.file_path:
        question = f"Review our file: {req.file_path}"
    else:
        question = f"Review this {req.language} code:\n```{req.language}\n{req.code}\n```"
    if req.focus:
        question += f"\nFocus: {', '.join(req.focus)}"
    try:
        answer, sid = _with_memory(req.session_id, question, "review")
        return PRIMEResponse(answer=answer, mode="review", model=os.getenv("PRIME_MODEL", "gpt-4o"), session_id=sid)
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/architect", response_model=PRIMEResponse)
async def architect_system(req: ArchitectRequest):
    parts = [f"Design: {req.description}", f"Scale: {req.scale}"]
    if req.constraints:
        parts.append("Constraints:\n" + "\n".join(f"  - {c}" for c in req.constraints))
    try:
        answer, sid = _with_memory(req.session_id, "\n".join(parts), "architecture")
        return PRIMEResponse(answer=answer, mode="architecture", model=os.getenv("PRIME_MODEL", "gpt-4o"), session_id=sid)
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/security", response_model=PRIMEResponse)
async def threat_model(req: ThreatModelRequest):
    parts = [f"Threat model: {req.system_description}"]
    if req.file_path:
        parts.append(f"Read and analyze: {req.file_path}")
    elif req.code:
        parts.append(f"\nCode:\n```\n{req.code}\n```")
    try:
        answer, sid = _with_memory(req.session_id, "\n".join(parts), "security")
        return PRIMEResponse(answer=answer, mode="security", model=os.getenv("PRIME_MODEL", "gpt-4o"), session_id=sid)
    except Exception as e:
        raise HTTPException(500, str(e))


# ---------------------------------------------------------------------------
# SESSION ENDPOINTS
# ---------------------------------------------------------------------------

@router.post("/sessions/new")
async def new_session():
    sid = session_store.new_session_id()
    return {"session_id": sid, "message": "Pass this session_id to any /prime endpoint for multi-turn memory."}


@router.get("/sessions")
async def list_sessions():
    sessions = session_store.list_sessions()
    return {"sessions": sessions, "count": len(sessions)}


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    history = session_store.get_full_history(session_id)
    if not history:
        raise HTTPException(404, f"Session '{session_id}' not found or empty.")
    return {"session_id": session_id, "message_count": len(history), "messages": history}


@router.delete("/sessions/{session_id}")
async def clear_session(session_id: str):
    session_store.clear_session(session_id)
    return {"status": "cleared", "session_id": session_id}
