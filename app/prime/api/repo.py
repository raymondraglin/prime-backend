"""
PRIME Repo Endpoints
File: app/prime/api/repo.py

Endpoints for indexing and searching the entire codebase.

Endpoints:
  POST   /prime/repo/index          -- Build or rebuild the full repo index
  GET    /prime/repo/status         -- Check index status
  GET    /prime/repo/map            -- Get the full file tree (no content)
  POST   /prime/repo/search         -- Keyword search over indexed files
  POST   /prime/repo/ask            -- Ask PRIME about the codebase (with full context)
"""

from __future__ import annotations

import json
import logging
import os
from typing import Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks
from openai import OpenAI
from pydantic import BaseModel, Field

from app.prime.memory.session_store import session_store
from app.prime.rag.repo_indexer import (
    build_index,
    build_repo_context_for_prime,
    get_file_map,
    index_status,
    search_index,
)
from app.prime.tools.prime_tools import TOOL_DEFINITIONS, execute_tool

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/prime/repo", tags=["PRIME Repo"])

MAX_TOOL_ROUNDS = 10  # Max tool call rounds before forcing final answer


# ---------------------------------------------------------------------------
# MODELS
# ---------------------------------------------------------------------------

class SearchRequest(BaseModel):
    query: str = Field(..., description="What to search for in the codebase")
    top_k: int = Field(default=8, description="Number of results to return")


class RepoAskRequest(BaseModel):
    question: str = Field(..., description="Question about the codebase")
    session_id: Optional[str] = Field(default=None)


# ---------------------------------------------------------------------------
# CORE: tool loop with guaranteed final answer
# ---------------------------------------------------------------------------

def _run_with_tools(messages: list, model: str) -> str:
    """
    Run the OpenAI tool-calling loop.
    After MAX_TOOL_ROUNDS, forces a final answer by disabling tools.
    Guarantees a non-empty string is always returned.
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    for round_num in range(MAX_TOOL_ROUNDS):
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=TOOL_DEFINITIONS,
            tool_choice="auto",
            temperature=0.3,
            max_tokens=4096,
        )
        msg = response.choices[0].message

        # PRIME finished -- return the answer
        if not msg.tool_calls:
            return msg.content or ""

        # Execute tool calls and feed results back
        messages.append(msg)
        for tc in msg.tool_calls:
            result = execute_tool(tc.function.name, json.loads(tc.function.arguments))
            logger.debug("Tool: %s → %s chars", tc.function.name, len(result))
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })

    # Tool loop exhausted -- force a final answer without tools
    logger.warning("Tool loop hit max rounds (%d). Forcing final answer.", MAX_TOOL_ROUNDS)
    messages.append({
        "role": "user",
        "content": "You have gathered enough information from the tools. Now write your complete answer.",
    })
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.3,
        max_tokens=4096,
        # No tools -- PRIME must answer now
    )
    return response.choices[0].message.content or "PRIME could not produce an answer."


# ---------------------------------------------------------------------------
# ENDPOINTS
# ---------------------------------------------------------------------------

@router.post("/index", summary="Build the full repo index")
async def index_repo(background_tasks: BackgroundTasks):
    """
    Walks the entire codebase and builds a searchable index.
    After this runs, PRIME knows every file that exists.
    """
    try:
        logger.info("Building repo index...")
        result = build_index(verbose=False)
        return {
            "status": "indexed",
            "file_count": result["file_count"],
            "skipped_count": result["skipped_count"],
            "error_count": result["error_count"],
            "built_at": result["built_at"],
            "message": f"PRIME now knows {result['file_count']} files. Use /prime/repo/ask to query the codebase.",
        }
    except Exception as e:
        logger.error("Index build failed: %s", e)
        raise HTTPException(500, str(e))


@router.get("/status", summary="Check index status")
async def repo_status():
    return index_status()


@router.get("/map", summary="Get the full file tree")
async def repo_map():
    files = get_file_map()
    if not files:
        raise HTTPException(404, "Index not built. Run POST /prime/repo/index first.")
    return {"file_count": len(files), "files": files}


@router.post("/search", summary="Search the indexed codebase")
async def search_repo(req: SearchRequest):
    results = search_index(req.query, req.top_k)
    return {"query": req.query, "results": results}


@router.post("/ask", summary="Ask PRIME about the codebase with full context")
async def ask_about_repo(req: RepoAskRequest):
    """
    Ask PRIME a question about the codebase.
    PRIME gets the full repo map injected into context + tool access to read any file.
    Always returns an answer -- tool loop exhaustion no longer causes a 500.
    """
    model = os.getenv("PRIME_MODEL", "gpt-4o")

    repo_map = build_repo_context_for_prime()
    if "NOT BUILT" in repo_map:
        raise HTTPException(
            400,
            "Index not built. Run POST /prime/repo/index first, then retry."
        )

    system_prompt = f"""YOU ARE PRIME -- Elite Principal Software Engineer.
You have complete awareness of Raymond's codebase.

{repo_map}

Instructions:
- You know every file listed above. Use read_file(path) to read any of them in full.
- Use search_codebase to find patterns across multiple files.
- ALWAYS read the relevant files before answering. Do not guess.
- After reading the files, write a complete, precise answer.
- Connect findings to Raymond's mission: Synergy Unlimited + PRIME platform.
"""

    history = session_store.get_history(req.session_id) if req.session_id else []
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": req.question})

    try:
        answer = _run_with_tools(messages, model)
    except Exception as e:
        logger.error("/prime/repo/ask error: %s", e)
        raise HTTPException(500, str(e))

    if req.session_id:
        session_store.add_message(req.session_id, "user", req.question)
        session_store.add_message(req.session_id, "assistant", answer)

    return {
        "answer": answer,
        "session_id": req.session_id,
        "model": model,
    }
