# app/prime/academic/embeddings.py
"""
PRIME Academic Embeddings

Generates and persists OpenAI embeddings for corpus chunks in PostgreSQL
using pgvector for cosine similarity search.

Graceful degradation:
  - If pgvector extension unavailable, functions return empty results
  - No startup crashes, no exceptions propagated to API layer
  - Academic search falls back to keyword-only mode automatically
"""
from __future__ import annotations

import os
from typing import Any

import sqlalchemy as sa
from sqlalchemy import create_engine, Column, String, Integer, Text
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM   = 1536

_pgvector_available = None


def _check_pgvector() -> bool:
    """Check if pgvector extension is available. Cached after first check."""
    global _pgvector_available
    if _pgvector_available is not None:
        return _pgvector_available
    
    try:
        from pgvector.sqlalchemy import Vector
        engine = _get_engine()
        with engine.connect() as conn:
            conn.execute(sa.text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
        _pgvector_available = True
        print("[academic/embeddings] pgvector extension available")
        return True
    except Exception as e:
        _pgvector_available = False
        print(f"[academic/embeddings] pgvector unavailable: {e}")
        return False


class CorpusEmbedding(Base):
    __tablename__ = "corpus_embeddings"

    id            = Column(String, primary_key=True)
    text          = Column(Text, nullable=False)
    source_path   = Column(String, nullable=False)
    title         = Column(String)
    domain        = Column(String)
    chunk_index   = Column(Integer)
    # embedding column added dynamically if pgvector available


def _add_embedding_column():
    """Add embedding column to model if pgvector is available."""
    if _check_pgvector():
        try:
            from pgvector.sqlalchemy import Vector
            if not hasattr(CorpusEmbedding, 'embedding'):
                CorpusEmbedding.embedding = Column(Vector(EMBEDDING_DIM), nullable=False)
        except Exception:
            pass


def _get_engine():
    db_url = os.getenv("DATABASE_URL", "")
    if not db_url:
        raise ValueError("DATABASE_URL not set")
    sync_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
    return create_engine(sync_url)


def ensure_table():
    """Create corpus_embeddings table if pgvector available."""
    if not _check_pgvector():
        return
    try:
        _add_embedding_column()
        engine = _get_engine()
        Base.metadata.create_all(engine)
    except Exception as e:
        print(f"[academic/embeddings] ensure_table error: {e}")


def embed_chunks(chunks: list[dict], batch_size: int = 2048) -> int:
    """
    Generate embeddings for chunks not already in DB.
    Returns 0 if pgvector unavailable.
    """
    if not _check_pgvector():
        print("[academic/embeddings] Skipping embedding - pgvector unavailable")
        return 0
    
    try:
        ensure_table()
        engine  = _get_engine()
        Session = sessionmaker(bind=engine)
        session = Session()

        existing_ids = {row[0] for row in session.query(CorpusEmbedding.id).all()}
        to_embed     = [c for c in chunks if c["id"] not in existing_ids]

        if not to_embed:
            return 0

        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        embedded_count = 0

        for i in range(0, len(to_embed), batch_size):
            batch = to_embed[i:i + batch_size]
            texts = [c["text"][:8000] for c in batch]

            resp       = client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
            embeddings = [e.embedding for e in resp.data]

            for chunk, emb in zip(batch, embeddings):
                session.add(CorpusEmbedding(
                    id          = chunk["id"],
                    text        = chunk["text"],
                    source_path = chunk["source_path"],
                    title       = chunk.get("title", ""),
                    domain      = chunk.get("domain", ""),
                    chunk_index = chunk.get("chunk_index", 0),
                    embedding   = emb,
                ))
            session.commit()
            embedded_count += len(batch)

        session.close()
        return embedded_count

    except Exception as e:
        print(f"[academic/embeddings] embed_chunks error: {e}")
        return 0


def vector_search(
    query: str,
    k: int = 5,
    domain: str | None = None,
) -> list[dict]:
    """
    Semantic search using pgvector cosine similarity.
    Returns [] if pgvector unavailable.
    """
    if not _check_pgvector():
        return []
    
    try:
        ensure_table()
        engine  = _get_engine()
        Session = sessionmaker(bind=engine)
        session = Session()

        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        resp   = client.embeddings.create(model=EMBEDDING_MODEL, input=[query])
        q_emb  = resp.data[0].embedding

        query_obj = session.query(
            CorpusEmbedding.id,
            CorpusEmbedding.text,
            CorpusEmbedding.source_path,
            CorpusEmbedding.title,
            CorpusEmbedding.domain,
            CorpusEmbedding.chunk_index,
            CorpusEmbedding.embedding.cosine_distance(q_emb).label("distance"),
        )

        if domain:
            query_obj = query_obj.filter(CorpusEmbedding.domain == domain)

        results = query_obj.order_by(sa.text("distance")).limit(k).all()

        session.close()
        return [
            {
                "id":          r.id,
                "text":        r.text,
                "source_path": r.source_path,
                "title":       r.title,
                "domain":      r.domain,
                "chunk_index": r.chunk_index,
                "score":       round(1 - r.distance, 4),
            }
            for r in results
        ]

    except Exception as e:
        print(f"[academic/embeddings] vector_search error: {e}")
        return []
