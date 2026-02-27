"""
PRIME Repo Endpoints
File: app/prime/api/repo.py

Endpoints:
  POST   /prime/repo/index   -- Build or rebuild the full repo index
  GET    /prime/repo/status  -- Check index status
  GET    /prime/repo/map     -- Get the full file tree
  POST   /prime/repo/search  -- Keyword search over indexed files
  POST   /prime/repo/ask     -- Ask PRIME about the codebase
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

from app.prime.identity import get_repo_identity
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
RETRY_BASE_DELAY = 3


class SearchRequest(BaseModel):
    query: str = Field(...)
    top_k: int = Field(default=8)


class RepoAskRequest(BaseModel):
    question: str = Field(...)
    session_id: Optional[str] = Field(default=None)


def _chat_with_retry(client: OpenAI, **kwargs):
    for attempt in range(MAX_RETRIES + 1):
        try:
            return client.chat.completions.create(**kwargs)
        except RateLimitError as e:
            if attempt == MAX_RETRIES:
                raise
            wait = RETRY_BASE_DELAY * (2 ** attempt)
            logger.warning("Rate limit. Waiting %ds (attempt %d/%d)...", wait, attempt + 1, MAX_RETRIES)
            time.sleep(wait)


def _run_with_tools(messages: list, model: str) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    for round_num in range(MAX_TOOL_ROUNDS):
        is_last = (round_num == MAX_TOOL_ROUNDS - 1)
        response = _chat_with_retry(
            client,
            model=model,
            messages=messages,
            tools=TOOL_DEFINITIONS,
            tool_choice="none" if is_last else "auto",
            temperature=0.3,
            max_tokens=4096 if is_last else 512,
        )
        msg = response.choices[0].message

        if not msg.tool_calls:
            return msg.content or ""

        messages.append(msg)
        for tc in msg.tool_calls:
            result = execute_tool(tc.function.name, json.loads(tc.function.arguments))
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

    # Safety net
    messages.append({"role": "user", "content": "Write your complete answer now."})
    response = _chat_with_retry(
        client, model=model, messages=messages, temperature=0.3, max_tokens=4096
    )
    return response.choices[0].message.content or ""


@router.post("/index")
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
        raise HTTPException(500, str(e))


@router.get("/status")
async def repo_status():
    return index_status()


@router.get("/map")
async def repo_map():
    files = get_file_map()
    if not files:
        raise HTTPException(404, "Index not built. Run POST /prime/repo/index first.")
    return {"file_count": len(files), "files": files}


@router.post("/search")
async def search_repo(req: SearchRequest):
    results = search_index(req.query, req.top_k)
    return {"query": req.query, "results": results}


@router.post("/ask")
async def ask_about_repo(req: RepoAskRequest):
    model = os.getenv("PRIME_MODEL", "gpt-4o")

    repo_map = build_repo_context_for_prime(slim=True)
    if "NOT BUILT" in repo_map:
        raise HTTPException(400, "Index not built. Run POST /prime/repo/index first.")

    # Full co-founder identity + codebase awareness
    system_prompt = get_repo_identity(repo_map)

    history = session_store.get_history(req.session_id) if req.session_id else []
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": req.question})

    try:
        answer = _run_with_tools(messages, model)
    except RateLimitError as e:
        raise HTTPException(429, f"Rate limit exceeded. Wait a moment and retry. Detail: {e}")
    except Exception as e:
        raise HTTPException(500, str(e))

    if req.session_id:
        session_store.add_message(req.session_id, "user", req.question)
        session_store.add_message(req.session_id, "assistant", answer)

    return {"answer": answer, "session_id": req.session_id, "model": model}
