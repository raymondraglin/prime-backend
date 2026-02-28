from __future__ import annotations

from typing import Any, Optional
from app.prime.tools.live_api_caller import call_prime_api


# ─── CORE REASONING ──────────────────────────────────────────────────────────

def prime_reasoning_core(*, task: str, max_steps: int = 8) -> dict[str, Any]:
    return call_prime_api(
        method="POST",
        path="/prime/reasoning/core",
        json_body={"task": task, "max_steps": max_steps},
    )


def prime_memory_save(
    *,
    entry_id: str,
    task: str,
    response: dict[str, Any],
    domain: str,
    outcome_quality: str = "unknown",
    user_id: Optional[str] = "raymond",
) -> dict[str, Any]:
    return call_prime_api(
        method="POST",
        path="/prime/reasoning/memory/save",
        json_body={
            "entry_id": entry_id,
            "task": task,
            "response": response,
            "tags": {"domain": domain},
            "user_id": user_id,
            "outcome_quality": outcome_quality,
        },
    )


# ─── PRIME CHAT ───────────────────────────────────────────────────────────────

def prime_chat(*, message: str, session_id: Optional[str] = None) -> dict[str, Any]:
    body: dict[str, Any] = {"message": message}
    if session_id:
        body["session_id"] = session_id
    return call_prime_api(method="POST", path="/prime/chat", json_body=body)


def prime_chat_history(
    *, limit: int = 20, offset: int = 0, session_id: Optional[str] = None
) -> dict[str, Any]:
    params: dict[str, Any] = {"limit": limit, "offset": offset}
    if session_id:
        params["session_id"] = session_id
    return call_prime_api(method="GET", path="/prime/chat/history", params=params)


# ─── GENIUS ENDPOINTS ─────────────────────────────────────────────────────────

def prime_ask(
    *, question: str, mode: str = "general", session_id: Optional[str] = None
) -> dict[str, Any]:
    return call_prime_api(
        method="POST",
        path="/prime/ask",
        json_body={"question": question, "mode": mode, "session_id": session_id},
    )


def prime_explain(*, topic: str, session_id: Optional[str] = None) -> dict[str, Any]:
    return call_prime_api(
        method="POST",
        path="/prime/explain",
        json_body={"topic": topic, "session_id": session_id},
    )


def prime_debug(
    *, code: str, error: Optional[str] = None, session_id: Optional[str] = None
) -> dict[str, Any]:
    return call_prime_api(
        method="POST",
        path="/prime/debug",
        json_body={"code": code, "error": error, "session_id": session_id},
    )


def prime_generate(
    *, description: str, language: str = "python", session_id: Optional[str] = None
) -> dict[str, Any]:
    return call_prime_api(
        method="POST",
        path="/prime/generate",
        json_body={
            "description": description,
            "language": language,
            "session_id": session_id,
        },
    )


def prime_review(*, code: str, focus: Optional[str] = None) -> dict[str, Any]:
    return call_prime_api(
        method="POST",
        path="/prime/review",
        json_body={"code": code, "focus": focus},
    )


def prime_architect(
    *,
    description: str,
    constraints: Optional[list[str]] = None,
    scale: str = "startup",
    session_id: Optional[str] = None,
) -> dict[str, Any]:
    return call_prime_api(
        method="POST",
        path="/prime/architect",
        json_body={
            "description": description,
            "constraints": constraints or [],
            "scale": scale,
            "session_id": session_id,
        },
    )


def prime_threat_model(*, system: str, session_id: Optional[str] = None) -> dict[str, Any]:
    return call_prime_api(
        method="POST",
        path="/prime/security",
        json_body={"system": system, "session_id": session_id},
    )


# ─── REPO ─────────────────────────────────────────────────────────────────────

def prime_repo_index() -> dict[str, Any]:
    return call_prime_api(method="POST", path="/prime/repo/index")


def prime_repo_map() -> dict[str, Any]:
    return call_prime_api(method="GET", path="/prime/repo/map")


def prime_repo_search(*, query: str, top_k: int = 5) -> dict[str, Any]:
    return call_prime_api(
        method="POST",
        path="/prime/repo/search",
        json_body={"query": query, "top_k": top_k},
    )


def prime_repo_ask(*, question: str) -> dict[str, Any]:
    return call_prime_api(
        method="POST",
        path="/prime/repo/ask",
        json_body={"question": question},
    )


# ─── IDENTITY / STATUS ────────────────────────────────────────────────────────

def prime_identity() -> dict[str, Any]:
    return call_prime_api(method="GET", path="/prime/identity")


def prime_status() -> dict[str, Any]:
    return call_prime_api(method="GET", path="/prime/status")


# ─── NOTEBOOK ─────────────────────────────────────────────────────────────────

def prime_notebook_get() -> dict[str, Any]:
    return call_prime_api(method="GET", path="/prime/ingest/notebook")


# ─── CURRICULUM ───────────────────────────────────────────────────────────────

def prime_curriculum_snapshot() -> dict[str, Any]:
    return call_prime_api(method="GET", path="/prime/curriculum/snapshot")


# ─────────────────────────────────────────────────────────────────────────────
# TOOL DEFINITIONS — OpenAI function-calling schema
# ─────────────────────────────────────────────────────────────────────────────

LIVE_TOOL_DEFINITIONS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "prime_reasoning_core",
            "description": "Run a multi-step reasoning trace against PRIME's reasoning core. Use this for any complex analysis, planning, or decision-making task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {"type": "string", "description": "Natural language task or question to reason about."},
                    "max_steps": {"type": "integer", "description": "Max reasoning steps (default 8).", "default": 8},
                },
                "required": ["task"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "prime_memory_save",
            "description": "Save a completed reasoning episode into PRIME's persistent reasoning memory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "entry_id": {"type": "string", "description": "Unique ID for this memory entry."},
                    "task": {"type": "string", "description": "The original task or question."},
                    "response": {"type": "object", "description": "The reasoning response payload.", "additionalProperties": True},
                    "domain": {"type": "string", "description": "Domain tag (e.g. math, philosophy, code, business)."},
                    "outcome_quality": {"type": "string", "enum": ["unknown", "good", "mixed", "bad", "cautious"], "default": "unknown"},
                    "user_id": {"type": "string", "default": "raymond"},
                },
                "required": ["entry_id", "task", "response", "domain"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "prime_chat",
            "description": "Send a message to PRIME's main chat endpoint and get a full reasoning-backed response.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "The message to send to PRIME."},
                    "session_id": {"type": "string", "description": "Optional session ID to continue a conversation."},
                },
                "required": ["message"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "prime_ask",
            "description": "Ask PRIME a genius-level question. Best for knowledge, analysis, and open-ended queries.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "The question to ask."},
                    "mode": {"type": "string", "description": "Mode (general, code, math, philosophy).", "default": "general"},
                    "session_id": {"type": "string"},
                },
                "required": ["question"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "prime_explain",
            "description": "Ask PRIME to explain a concept, algorithm, or idea at a teaching level.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "The concept or topic to explain."},
                    "session_id": {"type": "string"},
                },
                "required": ["topic"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "prime_debug",
            "description": "Send code to PRIME for debugging. Optionally include the error message.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "The code to debug."},
                    "error": {"type": "string", "description": "The error message or traceback, if any."},
                    "session_id": {"type": "string"},
                },
                "required": ["code"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "prime_generate",
            "description": "Ask PRIME to generate code from a description.",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {"type": "string", "description": "What to build."},
                    "language": {"type": "string", "description": "Target language (python, typescript, sql, etc).", "default": "python"},
                    "session_id": {"type": "string"},
                },
                "required": ["description"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "prime_review",
            "description": "Submit code to PRIME for a production-quality review.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Code to review."},
                    "focus": {"type": "string", "description": "Optional focus area (security, performance, readability)."},
                },
                "required": ["code"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "prime_architect",
            "description": "Ask PRIME to design a system architecture from a description.",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {"type": "string", "description": "What system to architect."},
                    "constraints": {"type": "array", "items": {"type": "string"}, "description": "Optional constraints."},
                    "scale": {"type": "string", "description": "Scale level: startup, growth, enterprise.", "default": "startup"},
                    "session_id": {"type": "string"},
                },
                "required": ["description"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "prime_threat_model",
            "description": "Ask PRIME to produce a security threat model for a described system.",
            "parameters": {
                "type": "object",
                "properties": {
                    "system": {"type": "string", "description": "Description of the system to threat-model."},
                    "session_id": {"type": "string"},
                },
                "required": ["system"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "prime_repo_index",
            "description": "Trigger PRIME to index the current codebase for search.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "prime_repo_map",
            "description": "Get PRIME's structural map of the current indexed codebase.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "prime_repo_search",
            "description": "Semantic search through the indexed codebase. Use this to find relevant files, functions, or logic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "What to search for in the codebase."},
                    "top_k": {"type": "integer", "description": "Number of results to return.", "default": 5},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "prime_repo_ask",
            "description": "Ask a natural language question about the codebase. PRIME retrieves relevant context and answers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "Question about the codebase."},
                },
                "required": ["question"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "prime_identity",
            "description": "Retrieve PRIME's full identity document.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "prime_status",
            "description": "Get PRIME's current status and capability summary.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "prime_notebook_get",
            "description": "Retrieve all entries in PRIME's notebook (ingested documents, images, and notes).",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "prime_curriculum_snapshot",
            "description": "Get a high-level snapshot of PRIME's full curriculum across all subjects.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]

# ─── IMPLEMENTATIONS MAP ──────────────────────────────────────────────────────

LIVE_TOOL_IMPLEMENTATIONS: dict[str, Any] = {
    "prime_reasoning_core": lambda **kw: prime_reasoning_core(**kw),
    "prime_memory_save": lambda **kw: prime_memory_save(**kw),
    "prime_chat": lambda **kw: prime_chat(**kw),
    "prime_ask": lambda **kw: prime_ask(**kw),
    "prime_explain": lambda **kw: prime_explain(**kw),
    "prime_debug": lambda **kw: prime_debug(**kw),
    "prime_generate": lambda **kw: prime_generate(**kw),
    "prime_review": lambda **kw: prime_review(**kw),
    "prime_architect": lambda **kw: prime_architect(**kw),
    "prime_threat_model": lambda **kw: prime_threat_model(**kw),
    "prime_repo_index": lambda **kw: prime_repo_index(),
    "prime_repo_map": lambda **kw: prime_repo_map(),
    "prime_repo_search": lambda **kw: prime_repo_search(**kw),
    "prime_repo_ask": lambda **kw: prime_repo_ask(**kw),
    "prime_identity": lambda **kw: prime_identity(),
    "prime_status": lambda **kw: prime_status(),
    "prime_notebook_get": lambda **kw: prime_notebook_get(),
    "prime_curriculum_snapshot": lambda **kw: prime_curriculum_snapshot(),
}
