from typing import Any
from pydantic import BaseModel

from app.prime.curriculum.models import (
    DomainId,
    CurriculumLevel,
    SubjectId,
    LessonKind,
)

# ============================================================
# Shared history lesson models (reusable across subjects)
# ============================================================


class HistoryLesson(BaseModel):
    """
    Generic history lesson container for PRIME.
    Used by subject-specific history endpoints (philosophy, math, etc.).
    """
    id: str
    subject_id: str  # e.g., "philosophy_core", "math_foundations"
    title: str
    period_overview: str
    periods: list[dict[str, Any]]
    cross_tradition_notes: list[str]
    how_it_shapes_today: list[str]

    domain: DomainId | None = None
    level: CurriculumLevel | None = None
