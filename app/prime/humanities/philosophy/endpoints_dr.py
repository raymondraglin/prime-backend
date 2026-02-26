from fastapi import APIRouter
from pydantic import BaseModel

from fastapi import APIRouter
from pydantic import BaseModel

from app.prime.curriculum.models import (
    PhilosophyLesson,
    SubjectId,
    LessonKind,
    DifficultyLevel,
    DomainId,
    CurriculumLevel,
    ReasoningTask,
    ReasoningTaskKind,
    ReasoningCoreResponse,
    ReasoningTrace,
)


router = APIRouter()


class PhilosophyDRHelloResponse(BaseModel):
    description: str


@router.get("/hello", response_model=PhilosophyDRHelloResponse)
async def philosophy_dr_hello() -> PhilosophyDRHelloResponse:
    """
    Deep-research philosophy endpoints (reasoning core overlays). Placeholder for now.
    """
    return PhilosophyDRHelloResponse(
        description="PRIME humanities/philosophy deep-research spine is wired (placeholder)."
    )
