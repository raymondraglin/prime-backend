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
    LogicConceptId,
    LogicConceptLesson,
    MethodsConceptId,
    MethodsConceptLesson,
    MetaphysicsConceptId,
    MetaphysicsConceptLesson,
    EthicsFramework,
)


router = APIRouter()


class PhilosophyGSHelloResponse(BaseModel):
    description: str


@router.get("/hello", response_model=PhilosophyGSHelloResponse)
async def philosophy_gs_hello() -> PhilosophyGSHelloResponse:
    """
    Grad-school philosophy endpoints. Placeholder for now.
    """
    return PhilosophyGSHelloResponse(
        description="PRIME humanities/philosophy grad-school spine is wired (placeholder)."
    )
