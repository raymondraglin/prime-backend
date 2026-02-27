# app/prime/context/models.py

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    SmallInteger,
    DateTime,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func
import uuid


class Base(DeclarativeBase):
    """Base class for PRIME context models."""
    pass


class PrimeMemory(Base):
    __tablename__ = "prime_memories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    memory_type: Mapped[str] = mapped_column(String(50), default="general", index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[Optional[str]] = mapped_column(String(100))
    importance: Mapped[int] = mapped_column(SmallInteger, default=5)
    tags: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text), default=[])
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class PrimeProject(Base):
    __tablename__ = "prime_projects"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="active")
    description: Mapped[Optional[str]] = mapped_column(Text)
    goals: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text))
    current_phase: Mapped[Optional[str]] = mapped_column(String(100))
    decisions: Mapped[Optional[dict]] = mapped_column(JSONB, default=[])
    blockers: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text))
    priority: Mapped[int] = mapped_column(SmallInteger, default=5)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class PrimeConversation(Base):
    __tablename__ = "prime_conversations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), default=uuid.uuid4, index=True
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSONB, default={})
    token_count: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Foundation(Base):
    __tablename__ = "foundations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    domain: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    subject: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    level: Mapped[str] = mapped_column(String(50), default="general")
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    cliff_notes: Mapped[str] = mapped_column(Text, nullable=False)
    key_concepts: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text))
    related_ids: Mapped[Optional[list[int]]] = mapped_column(ARRAY(Integer))
    source_refs: Mapped[Optional[dict]] = mapped_column(JSONB, default=[])
    confidence: Mapped[int] = mapped_column(SmallInteger, default=8)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class PrimeNotebookEntry(Base):
    __tablename__ = "prime_notebook_entries"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    entry_type: Mapped[str] = mapped_column(String(50), default="summary")
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    domain: Mapped[Optional[str]] = mapped_column(String(100))
    subject: Mapped[Optional[str]] = mapped_column(String(200))
    tags: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text), default=[])
    status: Mapped[str] = mapped_column(String(30), default="draft")
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("prime_notebook_entries.id")
    )
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
