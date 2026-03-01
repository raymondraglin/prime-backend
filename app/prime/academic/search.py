# app/prime/academic/search.py
"""
PRIME Academic Search

Three search modes:
  1. keyword  -- BM25-style term frequency (fast, zero dependencies, always works)
  2. vector   -- pgvector cosine similarity (requires embeddings in DB)
  3. hybrid   -- vector retrieval + BM25 re-ranking (best quality)

Graceful degradation:
  - Auto mode detects if pgvector available and has data
  - Falls back to keyword if vector/hybrid unavailable
  - Never crashes, always returns results if corpus exists
"""
from __future__ import annotations

import math
import re


def _tokenize(text: str) -> list[str]:
    """Lowercase alphanum tokens, min length 2."""
    return re.findall(r"\b[a-z0-9]{2,}\b", text.lower())


def _bm25_score(chunk_text: str, query_terms: list[str]) -> float:
    """
    BM25-style keyword score.
    Rewards term frequency while penalizing very long passages.
    """
    text_lower = chunk_text.lower()
    doc_len    = max(len(chunk_text), 1)
    score      = 0.0
    for term in query_terms:
        tf = text_lower.count(term)
        if tf > 0:
            score += (1 + math.log1p(tf)) / (1 + math.log1p(doc_len / 300))
    return score


def academic_search(
    query: str,
    k: int = 5,
    domain: str | None = None,
    mode: str = "auto",
) -> list[dict]:
    """
    Search the academic corpus and return the top-k most relevant chunks.

    Args:
        query  : natural language search query.
        k      : number of results to return (default 5, max 20).
        domain : optional corpus subdomain filter (e.g. 'cs_ict', 'math').
        mode   : 'keyword', 'vector', 'hybrid', or 'auto' (default).

    Returns:
        list of chunk dicts ordered by descending relevance.
    """
    k = min(k, 20)

    # Auto mode: use vector if embeddings exist, else keyword
    if mode == "auto":
        mode = _detect_mode()

    if mode == "vector":
        results = _vector_search(query, k, domain)
        # Fall back to keyword if vector returns empty
        if not results:
            print("[academic/search] vector mode returned empty, falling back to keyword")
            return _keyword_search(query, k, domain)
        return results
    elif mode == "hybrid":
        results = _hybrid_search(query, k, domain)
        if not results:
            print("[academic/search] hybrid mode returned empty, falling back to keyword")
            return _keyword_search(query, k, domain)
        return results
    else:
        return _keyword_search(query, k, domain)


def _detect_mode() -> str:
    """Auto-detect: vector if corpus_embeddings has data, else keyword."""
    try:
        from app.prime.academic.embeddings import _check_pgvector
        if not _check_pgvector():
            return "keyword"
        
        from app.prime.academic.embeddings import _get_engine, CorpusEmbedding
        from sqlalchemy.orm import sessionmaker
        engine  = _get_engine()
        Session = sessionmaker(bind=engine)
        session = Session()
        count   = session.query(CorpusEmbedding).count()
        session.close()
        return "vector" if count > 0 else "keyword"
    except Exception as e:
        print(f"[academic/search] _detect_mode error, using keyword: {e}")
        return "keyword"


def _keyword_search(query: str, k: int, domain: str | None) -> list[dict]:
    """BM25-style keyword search over in-memory chunks (always works)."""
    try:
        from app.prime.academic.indexer import get_corpus_chunks

        chunks      = get_corpus_chunks(domain=domain)
        query_terms = _tokenize(query)

        if not chunks or not query_terms:
            return []

        scored = [(_bm25_score(c["text"], query_terms), c) for c in chunks]
        scored.sort(key=lambda x: x[0], reverse=True)

        return [
            {**c, "score": round(s, 4), "citation_type": "corpus"}
            for s, c in scored[:k]
            if s > 0
        ]
    except Exception as e:
        print(f"[academic/search] _keyword_search error: {e}")
        return []


def _vector_search(query: str, k: int, domain: str | None) -> list[dict]:
    """pgvector cosine similarity search. Returns [] if unavailable."""
    try:
        from app.prime.academic.embeddings import vector_search

        results = vector_search(query, k=k, domain=domain)
        for r in results:
            r["citation_type"] = "corpus"
        return results
    except Exception as e:
        print(f"[academic/search] _vector_search error: {e}")
        return []


def _hybrid_search(query: str, k: int, domain: str | None) -> list[dict]:
    """Hybrid: vector retrieval + BM25 re-ranking. Falls back to keyword if vector fails."""
    try:
        from app.prime.academic.embeddings import vector_search

        pool_size    = min(k * 4, 40)
        candidates   = vector_search(query, k=pool_size, domain=domain)
        
        if not candidates:
            return []
        
        query_terms  = _tokenize(query)

        if not query_terms:
            return candidates[:k]

        # Re-score with BM25 and average with vector score
        hybrid_scored = []
        for c in candidates:
            vec_score = c["score"]
            bm25_score = _bm25_score(c["text"], query_terms)
            bm25_norm = min(bm25_score / 5.0, 1.0)
            hybrid = (vec_score + bm25_norm) / 2
            hybrid_scored.append((hybrid, {**c, "score": round(hybrid, 4), "citation_type": "corpus"}))

        hybrid_scored.sort(key=lambda x: x[0], reverse=True)
        return [c for _, c in hybrid_scored[:k]]
    except Exception as e:
        print(f"[academic/search] _hybrid_search error: {e}")
        return []
