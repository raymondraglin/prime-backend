# app/prime/academic/routes.py
"""
PRIME Academic Search Endpoints

POST /prime/academic/search
  Full corpus search with mode selection: keyword, vector, hybrid, or auto.

POST /prime/academic/index
  Force-rebuild the in-memory corpus index and optionally embed all chunks.

POST /prime/academic/embed
  Generate embeddings for all corpus chunks and store in corpus_embeddings table.

GET  /prime/academic/stats
  Return corpus index stats: chunk count, domains, corpus root, embedding count.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/prime/academic", tags=["PRIME Academic"])


class AcademicSearchRequest(BaseModel):
    query:  str
    k:      int            = 5
    domain: Optional[str] = None
    mode:   str           = "auto"  # keyword | vector | hybrid | auto


class AcademicSearchResponse(BaseModel):
    query:         str
    hits:          list[dict] = Field(default_factory=list)
    total_hits:    int
    corpus_chunks: int
    domain_filter: Optional[str]
    mode_used:     str


@router.post("/search", response_model=AcademicSearchResponse)
async def academic_search_endpoint(req: AcademicSearchRequest):
    if not req.query.strip():
        raise HTTPException(400, "Query cannot be empty.")
    try:
        from app.prime.academic.search  import academic_search, _detect_mode
        from app.prime.academic.indexer import corpus_stats

        mode_used = req.mode if req.mode != "auto" else _detect_mode()

        hits  = academic_search(
            query  = req.query,
            k      = req.k,
            domain = req.domain,
            mode   = req.mode,
        )
        stats = corpus_stats()

        return AcademicSearchResponse(
            query         = req.query,
            hits          = hits,
            total_hits    = len(hits),
            corpus_chunks = stats["total_chunks"],
            domain_filter = req.domain,
            mode_used     = mode_used,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(500, f"Academic search error: {exc}") from exc


@router.post("/index")
async def rebuild_corpus_index(embed: bool = False):
    """
    Force a full re-scan of external_corpus/ and rebuild the in-memory index.
    If embed=true, also generates embeddings for all chunks.
    """
    try:
        from app.prime.academic.indexer import get_corpus_chunks, corpus_stats
        chunks = get_corpus_chunks(rebuild=True)
        stats  = corpus_stats()

        result = {"status": "ok", "message": "Corpus index rebuilt.", **stats}

        if embed:
            from app.prime.academic.embeddings import embed_chunks
            embedded_count = embed_chunks(chunks)
            result["embeddings_created"] = embedded_count

        return result

    except Exception as exc:
        raise HTTPException(500, str(exc)) from exc


@router.post("/embed")
async def embed_corpus():
    """
    Generate embeddings for all corpus chunks and store in corpus_embeddings table.
    Idempotent: only embeds chunks not already in DB.
    """
    try:
        from app.prime.academic.indexer import get_corpus_chunks
        from app.prime.academic.embeddings import embed_chunks

        chunks         = get_corpus_chunks()
        embedded_count = embed_chunks(chunks)

        return {
            "status": "ok",
            "total_chunks": len(chunks),
            "embedded_count": embedded_count,
            "message": f"Embedded {embedded_count} new chunks.",
        }

    except Exception as exc:
        raise HTTPException(500, str(exc)) from exc


@router.get("/stats")
async def get_corpus_stats():
    """Return corpus index statistics including embedding count."""
    try:
        from app.prime.academic.indexer import corpus_stats
        from app.prime.academic.embeddings import _get_engine, CorpusEmbedding
        from sqlalchemy.orm import sessionmaker

        stats = corpus_stats()

        # Add embedding count
        try:
            engine  = _get_engine()
            Session = sessionmaker(bind=engine)
            session = Session()
            stats["embeddings_count"] = session.query(CorpusEmbedding).count()
            session.close()
        except Exception:
            stats["embeddings_count"] = 0

        return stats

    except Exception as exc:
        raise HTTPException(500, str(exc)) from exc
