# app/prime/academic/routes.py
"""
PRIME Academic Search Endpoints

POST /prime/academic/search
  Full corpus search with optional semantic re-ranking.
  Used by the research conductor, agent orchestrator, and the frontend.

POST /prime/academic/index
  Force-rebuild the in-memory corpus index (e.g. after adding new files).

GET  /prime/academic/stats
  Return corpus index stats: chunk count, domains, corpus root.

Corpus is loaded from external_corpus/ on first request.
Drop your textbooks, papers, and notes there and call /prime/academic/index.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/prime/academic", tags=["PRIME Academic"])


class AcademicSearchRequest(BaseModel):
    query:    str
    k:        int            = 5
    domain:   Optional[str] = None
    semantic: bool          = False


class AcademicSearchResponse(BaseModel):
    query:         str
    hits:          list[dict] = Field(default_factory=list)
    total_hits:    int
    corpus_chunks: int
    domain_filter: Optional[str]


@router.post("/search", response_model=AcademicSearchResponse)
async def academic_search_endpoint(req: AcademicSearchRequest):
    if not req.query.strip():
        raise HTTPException(400, "Query cannot be empty.")
    try:
        from app.prime.academic.search  import academic_search
        from app.prime.academic.indexer import corpus_stats

        hits  = academic_search(
            query=req.query,
            k=req.k,
            domain=req.domain,
            semantic=req.semantic,
        )
        stats = corpus_stats()

        return AcademicSearchResponse(
            query         = req.query,
            hits          = hits,
            total_hits    = len(hits),
            corpus_chunks = stats["total_chunks"],
            domain_filter = req.domain,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(500, f"Academic search error: {exc}") from exc


@router.post("/index")
async def rebuild_corpus_index():
    """
    Force a full re-scan of external_corpus/ and rebuild the in-memory index.
    Call this after adding new textbooks or papers.
    """
    try:
        from app.prime.academic.indexer import get_corpus_chunks, corpus_stats
        get_corpus_chunks(rebuild=True)
        stats = corpus_stats()
        return {"status": "ok", "message": "Corpus index rebuilt.", **stats}
    except Exception as exc:
        raise HTTPException(500, str(exc)) from exc


@router.get("/stats")
async def get_corpus_stats():
    """Return corpus index statistics without triggering a rebuild."""
    try:
        from app.prime.academic.indexer import corpus_stats
        return corpus_stats()
    except Exception as exc:
        raise HTTPException(500, str(exc)) from exc
