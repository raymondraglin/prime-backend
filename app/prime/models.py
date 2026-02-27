"""
PRIME Data Spine — SQLAlchemy Models
File: app/prime/models.py
"""

from datetime import datetime
from typing import Optional, List, Any, Dict
from sqlalchemy import (
    Integer, Text, Boolean, LargeBinary,
    ForeignKey, UniqueConstraint, Index,
    func
)
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column,
    relationship
)


class Base(DeclarativeBase):
    pass


# ─────────────────────────────────────────────────────────────
# 1. TAXONOMY SPINE
# ─────────────────────────────────────────────────────────────

class Domain(Base):
    __tablename__ = "domains"

    id:          Mapped[int]           = mapped_column(Integer, primary_key=True)
    code:        Mapped[str]           = mapped_column(Text, unique=True, nullable=False)
    name:        Mapped[str]           = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sort_order:  Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at:  Mapped[datetime]      = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    subjects:         Mapped[List["Subject"]]             = relationship(back_populates="domain",   cascade="all, delete-orphan")
    foundations:      Mapped[List["Foundation"]]          = relationship(back_populates="domain",   cascade="all, delete-orphan")
    corpus_documents: Mapped[List["CorpusDocument"]]      = relationship(back_populates="domain",   cascade="all, delete-orphan")
    notebook_entries: Mapped[List["PrimeNotebookEntry"]]  = relationship(back_populates="domain")
    failure_cases:    Mapped[List["FailureCase"]]         = relationship(back_populates="domain")
    prime_artifacts:  Mapped[List["PrimeArtifact"]]       = relationship(back_populates="domain")
    prime_memories:   Mapped[List["PrimeMemory"]]         = relationship(back_populates="domain")

    def __repr__(self):
        return f"<Domain {self.code}>"


class Subject(Base):
    __tablename__ = "subjects"
    __table_args__ = (
        UniqueConstraint("domain_id", "code", name="uq_subjects_domain_code"),
        Index("ix_subjects_domain_id", "domain_id"),
    )

    id:            Mapped[int]           = mapped_column(Integer, primary_key=True)
    domain_id:     Mapped[int]           = mapped_column(ForeignKey("domains.id",  ondelete="CASCADE"), nullable=False)
    code:          Mapped[str]           = mapped_column(Text, nullable=False)
    name:          Mapped[str]           = mapped_column(Text, nullable=False)
    level_tag:     Mapped[str]           = mapped_column(Text, nullable=False)
    description:   Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    language_code: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sort_order:    Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at:    Mapped[datetime]      = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    domain:           Mapped["Domain"]                   = relationship(back_populates="subjects")
    subfields:        Mapped[List["Subfield"]]           = relationship(back_populates="subject", cascade="all, delete-orphan")
    foundations:      Mapped[List["Foundation"]]         = relationship(back_populates="subject")
    corpus_documents: Mapped[List["CorpusDocument"]]     = relationship(back_populates="subject")
    notebook_entries: Mapped[List["PrimeNotebookEntry"]] = relationship(back_populates="subject")
    failure_cases:    Mapped[List["FailureCase"]]        = relationship(back_populates="subject")
    prime_artifacts:  Mapped[List["PrimeArtifact"]]      = relationship(back_populates="subject")

    def __repr__(self):
        return f"<Subject {self.code} [{self.level_tag}]>"


class Subfield(Base):
    __tablename__ = "subfields"
    __table_args__ = (
        UniqueConstraint("subject_id", "code", name="uq_subfields_subject_code"),
        Index("ix_subfields_subject_id", "subject_id"),
    )

    id:          Mapped[int]           = mapped_column(Integer, primary_key=True)
    subject_id:  Mapped[int]           = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    code:        Mapped[str]           = mapped_column(Text, nullable=False)
    name:        Mapped[str]           = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sort_order:  Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at:  Mapped[datetime]      = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    subject:          Mapped["Subject"]                  = relationship(back_populates="subfields")
    foundations:      Mapped[List["Foundation"]]         = relationship(back_populates="subfield")
    corpus_documents: Mapped[List["CorpusDocument"]]     = relationship(back_populates="subfield")
    notebook_entries: Mapped[List["PrimeNotebookEntry"]] = relationship(back_populates="subfield")

    def __repr__(self):
        return f"<Subfield {self.code}>"


# ─────────────────────────────────────────────────────────────
# 2. FOUNDATIONS — cliff notes, fastest retrieval layer
# ─────────────────────────────────────────────────────────────

class Foundation(Base):
    __tablename__ = "foundations"
    __table_args__ = (
        UniqueConstraint(
            "domain_id", "subject_id", "subfield_id", "level_tag",
            name="uq_foundations_slot"
        ),
        Index("ix_foundations_domain_subject", "domain_id", "subject_id"),
        Index("ix_foundations_level_tag", "level_tag"),
    )

    id:                  Mapped[int]           = mapped_column(Integer, primary_key=True)
    domain_id:           Mapped[int]           = mapped_column(ForeignKey("domains.id",   ondelete="CASCADE"), nullable=False)
    subject_id:          Mapped[int]           = mapped_column(ForeignKey("subjects.id",  ondelete="CASCADE"), nullable=False)
    subfield_id:         Mapped[Optional[int]] = mapped_column(ForeignKey("subfields.id", ondelete="SET NULL"), nullable=True)
    level_tag:           Mapped[str]           = mapped_column(Text, nullable=False)
    summary:             Mapped[str]           = mapped_column(Text, nullable=False)
    key_concepts:        Mapped[List[Any]]     = mapped_column(JSONB, server_default="[]", nullable=False)
    synonyms:            Mapped[List[Any]]     = mapped_column(JSONB, server_default="[]", nullable=False)
    common_notation:     Mapped[List[Any]]     = mapped_column(JSONB, server_default="[]", nullable=False)
    examples:            Mapped[List[Any]]     = mapped_column(JSONB, server_default="[]", nullable=False)
    counterexamples:     Mapped[List[Any]]     = mapped_column(JSONB, server_default="[]", nullable=False)
    historical_notes:    Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    canonical_refs:      Mapped[List[Any]]     = mapped_column(JSONB, server_default="[]", nullable=False)
    related_concept_ids: Mapped[List[Any]]     = mapped_column(JSONB, server_default="[]", nullable=False)
    innovator_gaps:      Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes:               Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_updated_at:     Mapped[datetime]      = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    domain:   Mapped["Domain"]            = relationship(back_populates="foundations")
    subject:  Mapped["Subject"]           = relationship(back_populates="foundations")
    subfield: Mapped[Optional["Subfield"]]= relationship(back_populates="foundations")

    def __repr__(self):
        return f"<Foundation domain={self.domain_id} subject={self.subject_id} level={self.level_tag}>"


# ─────────────────────────────────────────────────────────────
# 3. CATHEDRAL LIBRARY
# ─────────────────────────────────────────────────────────────

class CorpusDocument(Base):
    __tablename__ = "corpus_documents"
    __table_args__ = (
        Index("ix_corpus_docs_domain_subject", "domain_id", "subject_id"),
        Index("ix_corpus_docs_kind",           "kind"),
        Index("ix_corpus_docs_hash",           "content_hash"),
    )

    id:              Mapped[int]            = mapped_column(Integer, primary_key=True)
    domain_id:       Mapped[int]            = mapped_column(ForeignKey("domains.id",   ondelete="CASCADE"), nullable=False)
    subject_id:      Mapped[Optional[int]]  = mapped_column(ForeignKey("subjects.id",  ondelete="SET NULL"), nullable=True)
    subfield_id:     Mapped[Optional[int]]  = mapped_column(ForeignKey("subfields.id", ondelete="SET NULL"), nullable=True)
    level_tag:       Mapped[Optional[str]]  = mapped_column(Text, nullable=True)
    kind:            Mapped[str]            = mapped_column(Text, nullable=False)
    title:           Mapped[str]            = mapped_column(Text, nullable=False)
    source:          Mapped[Optional[str]]  = mapped_column(Text, nullable=True)
    author:          Mapped[Optional[str]]  = mapped_column(Text, nullable=True)
    year:            Mapped[Optional[int]]  = mapped_column(Integer, nullable=True)
    source_language: Mapped[Optional[str]]  = mapped_column(Text, nullable=True)
    path:            Mapped[str]            = mapped_column(Text, nullable=False)
    content_hash:    Mapped[Optional[str]]  = mapped_column(Text, nullable=True)
    extra_metadata:  Mapped[Dict[str, Any]] = mapped_column(JSONB, server_default="{}", nullable=False)
    ingested_at:     Mapped[datetime]       = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    is_active:       Mapped[bool]           = mapped_column(Boolean, server_default="true", nullable=False)

    domain:     Mapped["Domain"]              = relationship(back_populates="corpus_documents")
    subject:    Mapped[Optional["Subject"]]   = relationship(back_populates="corpus_documents")
    subfield:   Mapped[Optional["Subfield"]]  = relationship(back_populates="corpus_documents")
    chunks:     Mapped[List["CorpusChunk"]]   = relationship(back_populates="document", cascade="all, delete-orphan")
    study_jobs: Mapped[List["StudyJob"]]      = relationship(back_populates="document", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CorpusDocument {self.title[:40]} [{self.kind}]>"


class CorpusChunk(Base):
    __tablename__ = "corpus_chunks"
    __table_args__ = (
        UniqueConstraint("document_id", "chunk_index", name="uq_chunks_doc_idx"),
        Index("ix_corpus_chunks_doc_id", "document_id"),
    )

    id:             Mapped[int]            = mapped_column(Integer, primary_key=True)
    document_id:    Mapped[int]            = mapped_column(ForeignKey("corpus_documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index:    Mapped[int]            = mapped_column(Integer, nullable=False)
    text:           Mapped[str]            = mapped_column(Text, nullable=False)
    token_count:    Mapped[Optional[int]]  = mapped_column(Integer, nullable=True)
    embedding:      Mapped[Optional[bytes]]= mapped_column(LargeBinary, nullable=True)
    chunk_metadata: Mapped[Dict[str, Any]] = mapped_column(JSONB, server_default="{}", nullable=False)
    # NOTE: renamed from 'metadata' — reserved word in SQLAlchemy Declarative API

    document: Mapped["CorpusDocument"] = relationship(back_populates="chunks")

    def __repr__(self):
        return f"<CorpusChunk doc={self.document_id} idx={self.chunk_index}>"


# ─────────────────────────────────────────────────────────────
# 4. PRIME NOTEBOOK
# ─────────────────────────────────────────────────────────────

class PrimeNotebookEntry(Base):
    __tablename__ = "prime_notebook_entries"
    __table_args__ = (
        Index("ix_notebook_domain_subject", "domain_id", "subject_id"),
        Index("ix_notebook_kind",           "kind"),
    )

    id:                  Mapped[int]           = mapped_column(Integer, primary_key=True)
    prime_id:            Mapped[int]           = mapped_column(Integer, nullable=False, server_default="1")
    domain_id:           Mapped[Optional[int]] = mapped_column(ForeignKey("domains.id",   ondelete="SET NULL"), nullable=True)
    subject_id:          Mapped[Optional[int]] = mapped_column(ForeignKey("subjects.id",  ondelete="SET NULL"), nullable=True)
    subfield_id:         Mapped[Optional[int]] = mapped_column(ForeignKey("subfields.id", ondelete="SET NULL"), nullable=True)
    kind:                Mapped[str]           = mapped_column(Text, nullable=False)
    title:               Mapped[str]           = mapped_column(Text, nullable=False)
    body:                Mapped[str]           = mapped_column(Text, nullable=False)
    source_document_ids: Mapped[List[Any]]     = mapped_column(JSONB, server_default="[]", nullable=False)
    created_at:          Mapped[datetime]      = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at:          Mapped[datetime]      = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    version:             Mapped[int]           = mapped_column(Integer, server_default="1", nullable=False)

    domain:   Mapped[Optional["Domain"]]   = relationship(back_populates="notebook_entries")
    subject:  Mapped[Optional["Subject"]]  = relationship(back_populates="notebook_entries")
    subfield: Mapped[Optional["Subfield"]] = relationship(back_populates="notebook_entries")

    def __repr__(self):
        return f"<PrimeNotebookEntry {self.title[:40]} [{self.kind}]>"


# ─────────────────────────────────────────────────────────────
# 5. STUDY JOBS
# ─────────────────────────────────────────────────────────────

class StudyJob(Base):
    __tablename__ = "study_jobs"
    __table_args__ = (
        Index("ix_study_jobs_status_priority", "status", "priority"),
    )

    id:          Mapped[int]           = mapped_column(Integer, primary_key=True)
    document_id: Mapped[int]           = mapped_column(ForeignKey("corpus_documents.id", ondelete="CASCADE"), nullable=False)
    status:      Mapped[str]           = mapped_column(Text, server_default="pending", nullable=False)
    priority:    Mapped[int]           = mapped_column(Integer, server_default="5", nullable=False)
    last_error:  Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at:  Mapped[datetime]      = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at:  Mapped[datetime]      = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    document: Mapped["CorpusDocument"] = relationship(back_populates="study_jobs")

    def __repr__(self):
        return f"<StudyJob doc={self.document_id} [{self.status}]>"


# ─────────────────────────────────────────────────────────────
# 6. FAILURE CASES
# ─────────────────────────────────────────────────────────────

class FailureCase(Base):
    __tablename__ = "failure_cases"
    __table_args__ = (
        Index("ix_failure_cases_domain", "domain_id"),
    )

    id:                  Mapped[int]           = mapped_column(Integer, primary_key=True)
    domain_id:           Mapped[Optional[int]] = mapped_column(ForeignKey("domains.id",  ondelete="SET NULL"), nullable=True)
    subject_id:          Mapped[Optional[int]] = mapped_column(ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True)
    title:               Mapped[str]           = mapped_column(Text, nullable=False)
    summary:             Mapped[str]           = mapped_column(Text, nullable=False)
    what_failed:         Mapped[str]           = mapped_column(Text, nullable=False)
    root_causes:         Mapped[List[Any]]     = mapped_column(JSONB, server_default="[]", nullable=False)
    failed_controls:     Mapped[List[Any]]     = mapped_column(JSONB, server_default="[]", nullable=False)
    lessons:             Mapped[List[Any]]     = mapped_column(JSONB, server_default="[]", nullable=False)
    what_should_exist:   Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_document_ids: Mapped[List[Any]]     = mapped_column(JSONB, server_default="[]", nullable=False)
    year:                Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    location:            Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at:          Mapped[datetime]      = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    domain:  Mapped[Optional["Domain"]]  = relationship(back_populates="failure_cases")
    subject: Mapped[Optional["Subject"]] = relationship(back_populates="failure_cases")

    def __repr__(self):
        return f"<FailureCase {self.title[:40]}>"


# ─────────────────────────────────────────────────────────────
# 7. PRIME ARTIFACTS
# ─────────────────────────────────────────────────────────────

class PrimeArtifact(Base):
    __tablename__ = "prime_artifacts"
    __table_args__ = (
        Index("ix_prime_artifacts_kind_status", "kind", "status"),
    )

    id:                  Mapped[int]           = mapped_column(Integer, primary_key=True)
    prime_id:            Mapped[int]           = mapped_column(Integer, nullable=False, server_default="1")
    domain_id:           Mapped[Optional[int]] = mapped_column(ForeignKey("domains.id",  ondelete="SET NULL"), nullable=True)
    subject_id:          Mapped[Optional[int]] = mapped_column(ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True)
    kind:                Mapped[str]           = mapped_column(Text, nullable=False)
    title:               Mapped[str]           = mapped_column(Text, nullable=False)
    abstract:            Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    body:                Mapped[str]           = mapped_column(Text, nullable=False)
    outline:             Mapped[List[Any]]     = mapped_column(JSONB, server_default="[]", nullable=False)
    source_document_ids: Mapped[List[Any]]     = mapped_column(JSONB, server_default="[]", nullable=False)
    failure_case_ids:    Mapped[List[Any]]     = mapped_column(JSONB, server_default="[]", nullable=False)
    status:              Mapped[str]           = mapped_column(Text, server_default="draft", nullable=False)
    version:             Mapped[int]           = mapped_column(Integer, server_default="1", nullable=False)
    created_at:          Mapped[datetime]      = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at:          Mapped[datetime]      = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    domain:  Mapped[Optional["Domain"]]  = relationship(back_populates="prime_artifacts")
    subject: Mapped[Optional["Subject"]] = relationship(back_populates="prime_artifacts")

    def __repr__(self):
        return f"<PrimeArtifact {self.title[:40]} [{self.kind}]>"


# ─────────────────────────────────────────────────────────────
# 8. PRIME MEMORIES
# ─────────────────────────────────────────────────────────────

class PrimeMemory(Base):
    __tablename__ = "prime_memories"
    __table_args__ = (
        Index("ix_prime_memories_kind",       "kind"),
        Index("ix_prime_memories_importance", "importance"),
    )

    id:          Mapped[int]           = mapped_column(Integer, primary_key=True)
    kind:        Mapped[str]           = mapped_column(Text, nullable=False)
    subject:     Mapped[str]           = mapped_column(Text, nullable=False)
    body:        Mapped[str]           = mapped_column(Text, nullable=False)
    importance:  Mapped[int]           = mapped_column(Integer, server_default="5", nullable=False)
    domain_id:   Mapped[Optional[int]] = mapped_column(ForeignKey("domains.id", ondelete="SET NULL"), nullable=True)
    source_conversation_ids: Mapped[List[Any]] = mapped_column(JSONB, server_default="[]", nullable=False)
    tags:        Mapped[List[Any]]     = mapped_column(JSONB, server_default="[]", nullable=False)
    created_at:  Mapped[datetime]      = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    last_recalled: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )

    domain: Mapped[Optional["Domain"]] = relationship(back_populates="prime_memories")

    def __repr__(self):
        return f"<PrimeMemory [{self.kind}] importance={self.importance}: {self.subject[:40]}>"


# ─────────────────────────────────────────────────────────────
# 9. PRIME CONVERSATIONS — permanent, never-resetting log
# ─────────────────────────────────────────────────────────────

class PrimeConversation(Base):
    __tablename__ = "prime_conversations"
    __table_args__ = (
        Index("ix_prime_conversations_created_at", "created_at"),
        Index("ix_prime_conversations_session",    "session_id"),
    )

    id:              Mapped[int]            = mapped_column(Integer, primary_key=True)
    session_id:      Mapped[Optional[str]]  = mapped_column(Text, nullable=True)
    speaker:         Mapped[str]            = mapped_column(Text, nullable=False)
    message:         Mapped[str]            = mapped_column(Text, nullable=False)
    conv_metadata:   Mapped[Dict[str, Any]] = mapped_column(JSONB, server_default="{}", nullable=False)
    # NOTE: renamed from 'metadata' — reserved word in SQLAlchemy Declarative API
    created_at:      Mapped[datetime]       = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self):
        return f"<PrimeConversation [{self.speaker}] {str(self.created_at)[:16]}>"


# ─────────────────────────────────────────────────────────────
# 10. PRIME PROJECTS
# ─────────────────────────────────────────────────────────────

class PrimeProject(Base):
    __tablename__ = "prime_projects"
    __table_args__ = (
        Index("ix_prime_projects_status", "status"),
    )

    id:             Mapped[int]            = mapped_column(Integer, primary_key=True)
    name:           Mapped[str]            = mapped_column(Text, nullable=False)
    description:    Mapped[Optional[str]]  = mapped_column(Text, nullable=True)
    status:         Mapped[str]            = mapped_column(Text, server_default="active", nullable=False)
    domain_ids:     Mapped[List[Any]]      = mapped_column(JSONB, server_default="[]", nullable=False)
    goals:          Mapped[List[Any]]      = mapped_column(JSONB, server_default="[]", nullable=False)
    decisions:      Mapped[List[Any]]      = mapped_column(JSONB, server_default="[]", nullable=False)
    open_questions: Mapped[List[Any]]      = mapped_column(JSONB, server_default="[]", nullable=False)
    artifact_ids:   Mapped[List[Any]]      = mapped_column(JSONB, server_default="[]", nullable=False)
    notes:          Mapped[Optional[str]]  = mapped_column(Text, nullable=True)
    created_at:     Mapped[datetime]       = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at:     Mapped[datetime]       = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self):
        return f"<PrimeProject {self.name} [{self.status}]>"


__all__ = [
    "Base",
    "Domain", "Subject", "Subfield",
    "Foundation",
    "CorpusDocument", "CorpusChunk",
    "PrimeNotebookEntry",
    "StudyJob",
    "FailureCase",
    "PrimeArtifact",
    "PrimeMemory",
    "PrimeConversation",
    "PrimeProject",
]