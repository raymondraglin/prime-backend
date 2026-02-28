from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ─── REQUESTS ─────────────────────────────────────────────────────────────────

class GoalCreateRequest(BaseModel):
    title:        str              = Field(..., min_length=1, max_length=255)
    description:  Optional[str]   = None
    priority:     str              = Field("medium", pattern="^(high|medium|low)$")
    domain:       Optional[str]   = None
    session_id:   Optional[str]   = None
    target_date:  Optional[datetime] = None
    linked_tasks: list[str]        = Field(default_factory=list)
    tags:         list[str]        = Field(default_factory=list)


class GoalUpdateRequest(BaseModel):
    title:        Optional[str]      = Field(None, min_length=1, max_length=255)
    description:  Optional[str]      = None
    priority:     Optional[str]      = Field(None, pattern="^(high|medium|low)$")
    status:       Optional[str]      = Field(None, pattern="^(active|paused|completed|abandoned)$")
    domain:       Optional[str]      = None
    target_date:  Optional[datetime] = None
    outcome:      Optional[str]      = None
    linked_tasks: Optional[list[str]] = None
    tags:         Optional[list[str]] = None


class GoalProgressRequest(BaseModel):
    note: str = Field(..., min_length=1)


class GoalCompleteRequest(BaseModel):
    outcome: str = Field(..., min_length=1)


class GoalAbandonRequest(BaseModel):
    reason: Optional[str] = None


# ─── RESPONSES ────────────────────────────────────────────────────────────────

class GoalResponse(BaseModel):
    ok:   bool
    goal: Optional[dict[str, Any]] = None


class GoalListResponse(BaseModel):
    ok:    bool
    goals: list[dict[str, Any]] = Field(default_factory=list)
    count: int = 0


class GoalDeleteResponse(BaseModel):
    ok:      bool
    deleted: Optional[str] = None
    error:   Optional[str] = None
