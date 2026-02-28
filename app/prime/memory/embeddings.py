"""
PRIME Memory Embeddings
File: app/prime/memory/embeddings.py

Converts text into embedding vectors for semantic memory.

Model:    text-embedding-3-small (1536 dims, ~$0.02/M tokens)
Provider: OpenAI (OPENAI_API_KEY required)

Key behaviors:
  - Batches up to 100 texts per API call
  - Normalizes input (whitespace, length cap)
  - Tags each text with a memory_type prefix for retrieval quality
  - Never crashes the main request — returns [] on failure with a log

If OPENAI_API_KEY is not set, all calls return [] gracefully.
The rest of the memory stack handles missing vectors without error.
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger("prime.embeddings")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

_EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
_EMBEDDING_DIM   = 1536
_MAX_BATCH_SIZE  = 100
_MAX_INPUT_CHARS = 8_000   # ~2000 tokens, safe cap for this model

_PREFIX_MAP = {
    "turn":    "MEMORY_TURN: ",
    "summary": "MEMORY_SUMMARY: ",
    "doc":     "MEMORY_DOC: ",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_client():
    import openai
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set")
    return openai.OpenAI(api_key=api_key)


def _canonicalize(text: str, memory_type: str = "turn") -> str:
    """Normalize + prefix input for consistent embedding quality."""
    prefix  = _PREFIX_MAP.get(memory_type, "")
    cleaned = " ".join(text.split())[:_MAX_INPUT_CHARS]
    return f"{prefix}{cleaned}"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def embed_text(text: str, memory_type: str = "turn") -> list[float]:
    """
    Embed a single string.
    Returns a 1536-dim float list, or [] on any failure.
    """
    results = embed_texts([text], memory_type=memory_type)
    return results[0] if results else []


def embed_texts(
    texts: list[str],
    memory_type: str = "turn",
) -> list[list[float]]:
    """
    Embed a list of strings in batches.
    Returns list of 1536-dim vectors (same length as input), or [] on failure.
    """
    if not texts:
        return []
    try:
        client    = _get_client()
        canonical = [_canonicalize(t, memory_type) for t in texts]
        all_vectors: list[list[float]] = []

        for i in range(0, len(canonical), _MAX_BATCH_SIZE):
            batch = canonical[i : i + _MAX_BATCH_SIZE]
            resp  = client.embeddings.create(model=_EMBEDDING_MODEL, input=batch)
            all_vectors.extend(item.embedding for item in resp.data)

        return all_vectors
    except Exception as exc:
        logger.warning("embed_texts failed: %s", exc)
        return []


def embedding_dim()   -> int: return _EMBEDDING_DIM
def embedding_model() -> str: return _EMBEDDING_MODEL
