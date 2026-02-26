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
    PhilosophyLane1Mode,
    PhilosophyLane1PlannerRequest,
    PhilosophyLane1PlannerResponse,
    PhilosophyBranch,
    PhilosophyBranchPracticeRequest,
    PhilosophyBranchPracticeResponse,
    PhilosophyLane2Mode,
    PhilosophyLane2PlannerRequest,
    PhilosophyLane2PlannerResponse,
    PhilosophyLane3Mode,
    PhilosophyLane3PlannerRequest,
    PhilosophyLane3PlannerResponse,
    PhilosophyLane4Mode,
    PhilosophyLane4PlannerRequest,
    PhilosophyLane4PlannerResponse,
    PhilosophyLane5Mode,
    PhilosophyLane5PlannerRequest,
    PhilosophyLane5PlannerResponse,
    LogicConceptId,
    LogicConceptLesson,
    MethodsConceptId,
    MethodsConceptLesson,
    MetaphysicsConceptId,
    MetaphysicsConceptLesson,
    EthicsFramework,
)


router = APIRouter()


class PhilosophyUNHelloResponse(BaseModel):
    description: str


@router.get("/hello", response_model=PhilosophyUNHelloResponse)
async def philosophy_un_hello() -> PhilosophyUNHelloResponse:
    """
    Undergraduate philosophy endpoints. Placeholder for now.
    """
    return PhilosophyUNHelloResponse(
        description="PRIME humanities/philosophy undergraduate spine is wired (placeholder)."
    )
