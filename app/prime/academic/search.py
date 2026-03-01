# app/prime/academic/search.py
"""
PRIME Academic Search

Three search modes:
  1. keyword  -- BM25-style term frequency (fast, zero dependencies)
  2. vector   -- pgvector cosine similarity (requires embeddings in DB)
  3. hybrid   -- vector retrieval + BM25 re-ranking (best quality)

Default mode is 'vector' if corpus_embeddings table has data, else 'keyword'.

Return format per hit:
  {
    id, text, source_path, title, domain, chunk_index,
    citation_type: 'corpus', score: float
  }
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
        list of chunk dicts ordered by descending relevance, each with a
        'score' field and 'citation_type': 'corpus'.
    """
    k = min(k, 20)

    # Auto mode: use vector if embeddings exist, else keyword
    if mode == "auto":
        mode = _detect_mode()

    if mode == "vector":
        return _vector_search(query, k, domain)
    elif mode == "hybrid":
        return _hybrid_search(query, k, domain)
    else:
        return _keyword_search(query, k, domain)


def _detect_mode() -> str:
    """Auto-detect: vector if corpus_embeddings has data, else keyword."""
    try:
        from app.prime.academic.embeddings import _get_engine, CorpusEmbedding
        from sqlalchemy.orm import sessionmaker
        engine  = _get_engine()
        Session = sessionmaker(bind=engine)
        session = Session()
        count   = session.query(CorpusEmbedding).count()
        session.close()
        return "vector" if count > 0 else "keyword"
    except Exception:
        return "keyword"


def _keyword_search(query: str, k: int, domain: str | None) -> list[dict]:
    """BM25-style keyword search over in-memory chunks."""
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


def _vector_search(query: str, k: int, domain: str | None) -> list[dict]:
    """pgvector cosine similarity search."""
    from app.prime.academic.embeddings import vector_search

    results = vector_search(query, k=k, domain=domain)
    for r in results:
        r["citation_type"] = "corpus"
    return results


def _hybrid_search(query: str, k: int, domain: str | None) -> list[dict]:
    """
    Hybrid: vector retrieval (top 4*k) + BM25 re-ranking.
    Best of both worlds — semantic recall + exact keyword match.
    """
    from app.prime.academic.embeddings import vector_search

    pool_size    = min(k * 4, 40)
    candidates   = vector_search(query, k=pool_size, domain=domain)
    query_terms  = _tokenize(query)

    if not query_terms:
        return candidates[:k]

    # Re-score with BM25 and average with vector score
    hybrid_scored = []
    for c in candidates:
        vec_score = c["score"]
        bm25_score = _bm25_score(c["text"], query_terms)
        # Normalize BM25 to [0, 1] range (rough heuristic)
        bm25_norm = min(bm25_score / 5.0, 1.0)
        hybrid = (vec_score + bm25_norm) / 2
        hybrid_scored.append((hybrid, {**c, "score": round(hybrid, 4), "citation_type": "corpus"}))

    hybrid_scored.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in hybrid_scored[:k]]
