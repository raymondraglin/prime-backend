"""
PRIME Genius Endpoints
File: app/prime/api/genius.py

All capability gaps closed:
  [1] Multi-turn memory    -- session_id persists conversation across calls
  [2] RAG codebase access  -- PRIME reads actual files via tool calling
  [3] Tool calling         -- PRIME invokes read_file, search_codebase, query_database autonomously

Endpoints:
  POST /prime/ask                      -- Ask PRIME anything (8 modes, memory, tools)
  POST /prime/debug                    -- Debug broken code
  POST /prime/explain                  -- Explain any concept
  POST /prime/generate                 -- Generate code from description
  POST /prime/review                   -- Review code for bugs/security/quality
  POST /prime/architect                -- Design a system
  POST /prime/security                 -- Threat model and harden
  GET  /prime/status                   -- PRIME status and capabilities
  GET  /prime/sessions                 -- List all sessions
  GET  /prime/sessions/{session_id}    -- Get conversation history
  DELETE /prime/sessions/{session_id}  -- Clear a session
  POST /prime/sessions/new             -- Create a new session ID
"""

from __future__ import annotations

import json
import os
import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from openai import OpenAI

from app.prime.memory.session_store import session_store
from app.prime.tools.prime_tools import TOOL_DEFINITIONS, execute_tool

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/prime", tags=["PRIME Genius"])


# ---------------------------------------------------------------------------
# PRIME'S IDENTITY
# ---------------------------------------------------------------------------

PRIME_BASE_IDENTITY = """
======================================================================
YOU ARE PRIME
======================================================================
Role: Elite Principal Software Engineer and Systems Architect
Level: Beyond Senior -- Principal / Architect / 10x

Philosophy:
  Software is thinking made real. Every line of code is a decision.
  Every architecture is a bet on the future.
  You understand both the code and the consequences.

Mission:
  Help Raymond build his empire -- Synergy Unlimited and PRIME.
  Not just working software -- systems that scale, survive, and dominate.

Hacker Creed:
  You think like the best hacker alive to protect Raymond's systems.
  You see every attack surface, every edge case, every race condition.
  You are better than the best hackers. You know every attack.
  You know every defense. You build systems that cannot be broken.

Tools Available:
  You have access to tools. Use them proactively:
  - read_file: Read any file in the codebase before answering questions about it
  - list_directory: Explore the project structure
  - search_codebase: Find where functions, classes, patterns are used
  - query_database: Inspect the database schema and data (SELECT only)
  ALWAYS use tools when the question involves specific files or code.
  Do NOT answer from assumptions -- read the actual file first.

Raymond's Stack (master level):
  Backend:  Python, FastAPI, SQLAlchemy, PostgreSQL
  Frontend: React, TypeScript, Next.js
  AI:       OpenAI API, DeepSeek API, RAG, embeddings, agents
  DevOps:   Docker, GitHub Actions, PowerShell, Windows
  Platform: Synergy Unlimited (Healthcare, Criminal Justice, Marketing, Business)
  Education: PRIME (Adaptive Learning), ALP, BRIE reasoning engine

Principles:
  1. Understand the problem completely before writing one line.
  2. Read the error message -- all of it, twice.
  3. Security is a property of the design, not a feature.
  4. Data outlives code. Schema decisions matter forever.
  5. The hacker sees what the developer misses.
  6. Ship it. Then improve it. Perfect is the enemy of shipped.
  7. Every answer is in service of Raymond's empire.
======================================================================
"""

MODE_PROMPTS = {
    "general": "Answer as PRIME: elite principal engineer. Be direct, expert, precise. Use tools when the question involves specific files or code.",
    "debug": "DEBUG MODE: Find the root cause. Show the exact fix. Explain why. Read the file first if you need context.",
    "explain": "EXPLAIN MODE: One-sentence definition. How it works. Concrete example. Gotcha. Connect to Raymond's stack.",
    "generate": "GENERATE MODE: Write production-quality code. Type hints. Error handling. Secure defaults. PEP 8 / FastAPI patterns.",
    "review": "REVIEW MODE: Rate each issue Critical/High/Medium/Low. Check bugs, security, performance, correctness, quality. Read the file if you need full context.",
    "architecture": "ARCHITECTURE MODE: Identify tradeoffs. Design components. Explain decisions. State failure modes. Define the MVP.",
    "security": "SECURITY MODE: Think like the best hacker alive. Identify every attack surface. Name specific vectors. Rate severity. Give exact hardening fixes.",
    "teach": "TEACH MODE: Start with WHY. Build from what they know. Minimal example. One thing to try.",
}

VALID_MODES = list(MODE_PROMPTS.keys())
MAX_TOOL_ROUNDS = 5  # Max rounds of tool calls per request


# ---------------------------------------------------------------------------
# CORE LLM CALL WITH TOOL LOOP
# ---------------------------------------------------------------------------

def _call_prime(
    question: str,
    mode: str = "general",
    history: Optional[List[dict]] = None,
    use_tools: bool = True,
) -> str:
    """
    Core LLM call with:
    - PRIME's full identity as system prompt
    - Conversation history for multi-turn memory
    - Tool calling loop (read files, search code, query DB)
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    model = os.getenv("PRIME_MODEL", "gpt-4o")

    system_prompt = PRIME_BASE_IDENTITY + "\n" + MODE_PROMPTS.get(mode, MODE_PROMPTS["general"])

    # Build message list: system + history + current question
    messages = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": question})

    tools = TOOL_DEFINITIONS if use_tools else None

    # Tool calling loop
    for _ in range(MAX_TOOL_ROUNDS):
        kwargs = {"model": model, "messages": messages, "temperature": 0.3, "max_tokens": 4096}
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        response = client.chat.completions.create(**kwargs)
        msg = response.choices[0].message

        # No tool calls -- final answer
        if not msg.tool_calls:
            return msg.content or ""

        # Execute tool calls and feed results back
        messages.append(msg)  # assistant message with tool_calls
        for tc in msg.tool_calls:
            result = execute_tool(tc.function.name, json.loads(tc.function.arguments))
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })

    # Fallback: final call without tools
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.3,
        max_tokens=4096,
    )
    return response.choices[0].message.content or ""


# ---------------------------------------------------------------------------
# REQUEST / RESPONSE MODELS
# ---------------------------------------------------------------------------

class AskRequest(BaseModel):
    question: str = Field(..., description="What you want to ask PRIME")
    mode: str = Field(default="general", description="general | debug | explain | generate | review | architecture | security | teach")
    session_id: Optional[str] = Field(default=None, description="Session ID for multi-turn memory. Omit for stateless call.")
    use_tools: bool = Field(default=True, description="Allow PRIME to use tools (read files, search code, query DB)")

class DebugRequest(BaseModel):
    code: str = Field(..., description="The broken code")
    error: str = Field(default="", description="Error message or traceback")
    language: str = Field(default="python")
    context: str = Field(default="", description="What the code is supposed to do")
    session_id: Optional[str] = Field(default=None)

class ExplainRequest(BaseModel):
    topic: str = Field(..., description="Concept or code to explain")
    language: Optional[str] = Field(default=None)
    level: str = Field(default="engineer", description="student | engineer | expert")
    session_id: Optional[str] = Field(default=None)

class GenerateRequest(BaseModel):
    description: str = Field(..., description="What to build")
    language: str = Field(default="python")
    framework: str = Field(default="")
    requirements: Optional[List[str]] = Field(default=None)
    session_id: Optional[str] = Field(default=None)

class ReviewRequest(BaseModel):
    code: str = Field(default="", description="Code to review (or omit and let PRIME read the file)")
    file_path: Optional[str] = Field(default=None, description="File path for PRIME to read directly")
    language: str = Field(default="python")
    focus: Optional[List[str]] = Field(default=None, description="security | performance | bugs")
    session_id: Optional[str] = Field(default=None)

class ArchitectRequest(BaseModel):
    description: str = Field(..., description="System to design")
    constraints: Optional[List[str]] = Field(default=None)
    scale: str = Field(default="startup")
    session_id: Optional[str] = Field(default=None)

class ThreatModelRequest(BaseModel):
    system_description: str = Field(..., description="System to threat model")
    code: str = Field(default="")
    file_path: Optional[str] = Field(default=None, description="File path for PRIME to read")
    session_id: Optional[str] = Field(default=None)

class PRIMEResponse(BaseModel):
    answer: str
    mode: str
    model: str
    session_id: Optional[str] = None


# ---------------------------------------------------------------------------
# HELPER: Load history + save turn
# ---------------------------------------------------------------------------

def _with_memory(session_id: Optional[str], question: str, mode: str, use_tools: bool = True) -> tuple[str, Optional[str]]:
    """Load history, call PRIME, save turn. Returns (answer, session_id)."""
    history = session_store.get_history(session_id) if session_id else None

    answer = _call_prime(question=question, mode=mode, history=history, use_tools=use_tools)

    if session_id:
        session_store.add_message(session_id, "user", question)
        session_store.add_message(session_id, "assistant", answer)

    return answer, session_id


# ---------------------------------------------------------------------------
# ENDPOINTS
# ---------------------------------------------------------------------------

@router.get("/status", summary="PRIME status and capabilities")
async def prime_status():
    return {
        "status": "online",
        "model": os.getenv("PRIME_MODEL", "gpt-4o"),
        "identity": "Elite principal engineer. Hacker-level security. Tool calling. Multi-turn memory. Codebase RAG.",
        "modes": VALID_MODES,
        "tools": [t["function"]["name"] for t in TOOL_DEFINITIONS],
        "gaps_closed": [
            "Multi-turn memory: pass session_id to any endpoint",
            "RAG codebase access: PRIME reads files autonomously via read_file tool",
            "Tool calling: PRIME calls read_file, list_directory, search_codebase, query_database",
        ],
        "endpoints": [
            "POST /prime/ask",
            "POST /prime/debug",
            "POST /prime/explain",
            "POST /prime/generate",
            "POST /prime/review",
            "POST /prime/architect",
            "POST /prime/security",
            "GET  /prime/status",
            "GET  /prime/sessions",
            "GET  /prime/sessions/{session_id}",
            "DELETE /prime/sessions/{session_id}",
            "POST /prime/sessions/new",
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
        question = f"Review the file at: {req.file_path}"
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
        parts.append(f"Read and analyze this file: {req.file_path}")
    elif req.code:
        parts.append(f"\nCode:\n```\n{req.code}\n```")
    try:
        answer, sid = _with_memory(req.session_id, "\n".join(parts), "security")
        return PRIMEResponse(answer=answer, mode="security", model=os.getenv("PRIME_MODEL", "gpt-4o"), session_id=sid)
    except Exception as e:
        raise HTTPException(500, str(e))


# ---------------------------------------------------------------------------
# SESSION MANAGEMENT ENDPOINTS
# ---------------------------------------------------------------------------

@router.post("/sessions/new", summary="Create a new session ID")
async def new_session():
    sid = session_store.new_session_id()
    return {"session_id": sid, "message": "Pass this session_id to any /prime endpoint to enable multi-turn memory."}


@router.get("/sessions", summary="List all sessions")
async def list_sessions():
    sessions = session_store.list_sessions()
    return {"sessions": sessions, "count": len(sessions)}


@router.get("/sessions/{session_id}", summary="Get conversation history for a session")
async def get_session(session_id: str):
    history = session_store.get_full_history(session_id)
    if not history:
        raise HTTPException(404, f"Session '{session_id}' not found or empty.")
    return {"session_id": session_id, "message_count": len(history), "messages": history}


@router.delete("/sessions/{session_id}", summary="Clear a session")
async def clear_session(session_id: str):
    session_store.clear_session(session_id)
    return {"status": "cleared", "session_id": session_id}
