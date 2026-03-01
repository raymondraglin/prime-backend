# app/prime/tasks/embed_tasks.py
"""
PRIME Embedding Tasks

Async Celery tasks for batch embedding generation.

Tasks:
  embed_corpus_async -- embed all chunks in external_corpus/
  embed_file_async   -- embed a single file by path
"""
from __future__ import annotations

from app.prime.tasks.celery_app import celery_app


@celery_app.task(bind=True, name="prime.embed.corpus")
def embed_corpus_async(self, domain: str | None = None):
    """
    Generate embeddings for all corpus chunks.

    Args:
        domain : optional domain filter

    Returns:
        dict with total_chunks, embedded_count
    """
    from app.prime.academic.indexer import get_corpus_chunks
    from app.prime.academic.embeddings import embed_chunks

    self.update_state(state="STARTED", meta={"stage": "loading_chunks", "progress": 0})

    try:
        chunks = get_corpus_chunks(domain=domain)
        total = len(chunks)
        self.update_state(state="STARTED", meta={"stage": "embedding", "progress": 10, "total_chunks": total})

        embedded_count = embed_chunks(chunks)
        self.update_state(state="STARTED", meta={"stage": "complete", "progress": 100})

        return {
            "total_chunks": total,
            "embedded_count": embedded_count,
            "message": f"Embedded {embedded_count} new chunks out of {total} total.",
        }

    except Exception as exc:
        self.update_state(state="FAILURE", meta={"error": str(exc)})
        raise


@celery_app.task(bind=True, name="prime.embed.file")
def embed_file_async(self, file_path: str):
    """
    Embed a single file from external_corpus/.

    Args:
        file_path : path relative to PROJECT_ROOT

    Returns:
        dict with chunk_count, embedded_count
    """
    from pathlib import Path
    from app.prime.academic.indexer import _chunk_text, PROJECT_ROOT
    from app.prime.academic.embeddings import embed_chunks

    self.update_state(state="STARTED", meta={"stage": "reading_file", "progress": 0})

    try:
        path = PROJECT_ROOT / file_path
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        text = path.read_text(encoding="utf-8", errors="replace")
        self.update_state(state="STARTED", meta={"stage": "chunking", "progress": 20})

        chunks = _chunk_text(text, path)
        self.update_state(state="STARTED", meta={"stage": "embedding", "progress": 40, "chunk_count": len(chunks)})

        embedded_count = embed_chunks(chunks)
        self.update_state(state="STARTED", meta={"stage": "complete", "progress": 100})

        return {
            "file_path": file_path,
            "chunk_count": len(chunks),
            "embedded_count": embedded_count,
        }

    except Exception as exc:
        self.update_state(state="FAILURE", meta={"error": str(exc)})
        raise
