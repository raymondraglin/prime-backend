from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class GoalStatus(str, Enum):
    active    = "active"
    paused    = "paused"
    completed = "completed"
    abandoned = "abandoned"


class GoalPriority(str, Enum):
    high   = "high"
    medium = "medium"
    low    = "low"


class PrimeGoal(Base):
    __tablename__ = "prime_goals"

    id:           Mapped[str]  = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    title:        Mapped[str]  = mapped_column(String(255), nullable=False)
    description:  Mapped[str | None] = mapped_column(Text, nullable=True)
    status:       Mapped[str]  = mapped_column(String(50),  nullable=False, default=GoalStatus.active)
    priority:     Mapped[str]  = mapped_column(String(50),  nullable=False, default=GoalPriority.medium)
    domain:       Mapped[str | None] = mapped_column(String(100), nullable=True)
    user_id:      Mapped[str]  = mapped_column(String(100), nullable=False, default="raymond")
    session_id:   Mapped[str | None] = mapped_column(String(255), nullable=True)
    target_date:  Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    outcome:      Mapped[str | None] = mapped_column(Text, nullable=True)
    progress:     Mapped[list]  = mapped_column(JSONB, nullable=False, default=list)
    linked_tasks: Mapped[list]  = mapped_column(JSONB, nullable=False, default=list)
    tags:         Mapped[list]  = mapped_column(JSONB, nullable=False, default=list)
    created_at:   Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at:   Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id":           self.id,
            "title":        self.title,
            "description":  self.description,
            "status":       self.status,
            "priority":     self.priority,
            "domain":       self.domain,
            "user_id":      self.user_id,
            "session_id":   self.session_id,
            "target_date":  self.target_date.isoformat() if self.target_date else None,
            "outcome":      self.outcome,
            "progress":     self.progress or [],
            "linked_tasks": self.linked_tasks or [],
            "tags":         self.tags or [],
            "created_at":   self.created_at.isoformat() if self.created_at else None,
            "updated_at":   self.updated_at.isoformat() if self.updated_at else None,
        }
