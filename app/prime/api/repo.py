"""
PRIME Repo Endpoints
File: app/prime/api/repo.py

Endpoints:
  POST   /prime/repo/index   -- Build or rebuild the full repo index
  GET    /prime/repo/status  -- Check index status
  GET    /prime/repo/map     -- Get the full file tree (no content)
  POST   /prime/repo/search  -- Keyword search over indexed files
  POST   /prime/repo/ask     -- Ask PRIME about the codebase (full context)
"""

from __future__ import annotations

import json
import logging
import os
import time
from typing import Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks
from openai import OpenAI, RateLimitError
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

MAX_TOOL_ROUNDS = 10
MAX_RETRIES = 3
RETRY_BASE_DELAY = 3  # seconds


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
# CORE: rate-limit-aware tool loop with guaranteed final answer
# ---------------------------------------------------------------------------

def _chat_with_retry(client: OpenAI, **kwargs) -> any:
    """
    Wrapper around client.chat.completions.create with exponential backoff
    on 429 RateLimitError. Retries up to MAX_RETRIES times.
    """
    for attempt in range(MAX_RETRIES + 1):
        try:
            return client.chat.completions.create(**kwargs)
        except RateLimitError as e:
            if attempt == MAX_RETRIES:
                raise
            wait = RETRY_BASE_DELAY * (2 ** attempt)  # 3s, 6s, 12s
            logger.warning("Rate limit hit. Waiting %ds before retry %d/%d...", wait, attempt + 1, MAX_RETRIES)
            time.sleep(wait)


def _run_with_tools(messages: list, model: str) -> str:
    """
    Tool-calling loop with:
    - Rate limit retry (exponential backoff)
    - Reduced tokens on intermediate rounds (tool calls don't need 4096)
    - Forced final answer if loop exhausts
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    for round_num in range(MAX_TOOL_ROUNDS):
        is_last_round = (round_num == MAX_TOOL_ROUNDS - 1)

        response = _chat_with_retry(
            client,
            model=model,
            messages=messages,
            tools=TOOL_DEFINITIONS,
            tool_choice="auto" if not is_last_round else "none",
            temperature=0.3,
            # Intermediate rounds: 512 tokens (just enough for tool call JSON)
            # Final round: 4096 tokens for the full answer
            max_tokens=4096 if is_last_round else 512,
        )
        msg = response.choices[0].message

        # PRIME finished -- return the answer
        if not msg.tool_calls:
            return msg.content or ""

        # Execute tool calls and feed results back
        messages.append(msg)
        for tc in msg.tool_calls:
            result = execute_tool(tc.function.name, json.loads(tc.function.arguments))
            logger.debug("Tool %s: %d chars returned", tc.function.name, len(result))
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })

    # Shouldn't reach here (last round forces tool_choice=none) but safety net:
    logger.warning("Tool loop exhausted. Forcing final answer.")
    messages.append({"role": "user", "content": "Write your complete answer now."})
    response = _chat_with_retry(
        client, model=model, messages=messages, temperature=0.3, max_tokens=4096
    )
    return response.choices[0].message.content or "PRIME could not produce an answer."


# ---------------------------------------------------------------------------
# ENDPOINTS
# ---------------------------------------------------------------------------

@router.post("/index", summary="Build the full repo index")
async def index_repo(background_tasks: BackgroundTasks):
    try:
        result = build_index(verbose=False)
        return {
            "status": "indexed",
            "file_count": result["file_count"],
            "skipped_count": result["skipped_count"],
            "error_count": result["error_count"],
            "built_at": result["built_at"],
            "message": f"PRIME now knows {result['file_count']} files.",
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
    model = os.getenv("PRIME_MODEL", "gpt-4o")

    # Slim=True: paths + language only (~500-1500 tokens vs 5000+ for full map)
    repo_map = build_repo_context_for_prime(slim=True)
    if "NOT BUILT" in repo_map:
        raise HTTPException(400, "Index not built. Run POST /prime/repo/index first.")

    system_prompt = (
        "YOU ARE PRIME -- Elite Principal Software Engineer.\n"
        "You have complete awareness of Raymond's codebase.\n\n"
        f"{repo_map}\n"
        "Rules:\n"
        "- Use read_file(path) to read any file in full before answering questions about it.\n"
        "- Use search_codebase to find patterns across files.\n"
        "- Do NOT guess. Read first, then answer.\n"
        "- Connect findings to Raymond's mission: Synergy Unlimited + PRIME platform.\n"
    )

    history = session_store.get_history(req.session_id) if req.session_id else []
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": req.question})

    try:
        answer = _run_with_tools(messages, model)
    except RateLimitError as e:
        raise HTTPException(429, f"OpenAI rate limit exceeded after retries. Wait a moment and try again. Detail: {e}")
    except Exception as e:
        logger.error("/prime/repo/ask error: %s", e)
        raise HTTPException(500, str(e))

    if req.session_id:
        session_store.add_message(req.session_id, "user", req.question)
        session_store.add_message(req.session_id, "assistant", answer)

    return {"answer": answer, "session_id": req.session_id, "model": model}
