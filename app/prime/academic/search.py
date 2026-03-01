# app/prime/academic/search.py
"""
PRIME Academic Search

Two-tier retrieval:
  Tier 1 -- Keyword scoring (always runs, zero external dependencies)
             BM25-style: term frequency with document-length normalization.
             Fast enough for tens of thousands of chunks.

  Tier 2 -- Semantic re-ranking (optional, requires OPENAI_API_KEY)
             Computes cosine similarity between query and top-K candidate
             embeddings via text-embedding-3-small.
             Enabled by passing semantic=True to academic_search().

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
            # TF component + length normalization
            score += (1 + math.log1p(tf)) / (1 + math.log1p(doc_len / 300))
    return score


def academic_search(
    query: str,
    k: int = 5,
    domain: str | None = None,
    semantic: bool = False,
) -> list[dict]:
    """
    Search the academic corpus and return the top-k most relevant chunks.

    Args:
        query    : natural language search query.
        k        : number of results to return (default 5, max 20).
        domain   : optional corpus subdomain filter (e.g. 'cs_ict', 'math').
        semantic : if True, re-rank keyword candidates with OpenAI embeddings.

    Returns:
        list of chunk dicts ordered by descending relevance, each with a
        'score' field added.
    """
    from app.prime.academic.indexer import get_corpus_chunks

    k      = min(k, 20)
    chunks = get_corpus_chunks(domain=domain)

    if not chunks:
        return []

    query_terms = _tokenize(query)
    if not query_terms:
        return [{**c, "score": 0.0} for c in chunks[:k]]

    # Tier 1: keyword scoring
    scored: list[tuple[float, dict]] = []
    for chunk in chunks:
        score = _bm25_score(chunk["text"], query_terms)
        if score > 0:
            scored.append((score, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    pool_size     = min(k * 4, 40)
    top_scored    = scored[:pool_size]
    top_chunks    = [{**c, "score": round(s, 4)} for s, c in top_scored]

    # Tier 2: optional semantic re-ranking
    if semantic and top_chunks:
        try:
            top_chunks = _semantic_rerank(query, top_chunks, k)
        except Exception:
            top_chunks = top_chunks[:k]
    else:
        top_chunks = top_chunks[:k]

    return top_chunks


def _semantic_rerank(
    query: str,
    chunks: list[dict],
    k: int,
) -> list[dict]:
    """
    Re-rank chunks using OpenAI text-embedding-3-small cosine similarity.
    Falls back silently -- caller catches exceptions.
    """
    import os
    import numpy as np
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    texts = [query] + [c["text"][:512] for c in chunks]
    resp  = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts,
    )
    embeddings = [e.embedding for e in resp.data]

    q_vec  = np.array(embeddings[0], dtype=float)
    q_norm = np.linalg.norm(q_vec) + 1e-9

    re_scored: list[tuple[float, dict]] = []
    for i, chunk in enumerate(chunks):
        c_vec    = np.array(embeddings[i + 1], dtype=float)
        cosine   = float(np.dot(q_vec, c_vec) / (q_norm * (np.linalg.norm(c_vec) + 1e-9)))
        re_scored.append((cosine, {**chunk, "score": round(cosine, 4)}))

    re_scored.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in re_scored[:k]]
