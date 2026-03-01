# app/prime/memory/models.py
"""
PRIME Memory Models

Persistent conversation storage with semantic search.

Tables:
  conversation_turns  -- user/assistant message pairs with metadata
  memory_embeddings   -- pgvector semantic search over turns

Design:
  - One turn = user message + assistant response (atomic unit)
  - Embeddings generated from turn summary (user query + first 200 chars of response)
  - Session grouping via session_id for chronological retrieval
  - User-scoped for multi-user deployments
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
import uuid

Base = declarative_base()

EMBEDDING_DIM = 1536  # text-embedding-3-small


class ConversationTurn(Base):
    __tablename__ = "conversation_turns"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    session_id    = Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False, index=True)
    user_id       = Column(String(100), nullable=False, index=True, default="raymond")
    user_message  = Column(Text, nullable=False)
    assistant_msg = Column(Text, nullable=False)
    model         = Column(String(50))
    tokens_used   = Column(Integer)
    tool_calls    = Column(JSONB)  # list of {name, args}
    citations     = Column(JSONB)  # list of {source, text}
    metadata_     = Column("metadata", JSONB)  # avoid reserved word, map to 'metadata' in DB
    created_at    = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class MemoryEmbedding(Base):
    __tablename__ = "memory_embeddings"

    turn_id     = Column(Integer, ForeignKey("conversation_turns.id"), primary_key=True)
    user_id     = Column(String(100), nullable=False, index=True)
    summary     = Column(Text, nullable=False)  # user query + response snippet
    embedding   = Column(Vector(EMBEDDING_DIM), nullable=False)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
