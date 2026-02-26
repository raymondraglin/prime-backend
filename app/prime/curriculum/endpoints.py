from fastapi import APIRouter
from pydantic import BaseModel

from app.prime.curriculum.models import SubjectCurriculum
from app.prime.curriculum.math_foundations import build_math_foundations_curriculum
from app.prime.curriculum.money_foundations_history import (
    build_money_foundations_history_curriculum,
)


router = APIRouter()


class CurriculumSnapshot(BaseModel):
    subjects: list[SubjectCurriculum]


class CurriculumSnapshotResponse(BaseModel):
    description: str
    curriculum: CurriculumSnapshot


@router.get("/snapshot", response_model=CurriculumSnapshotResponse)
async def curriculum_snapshot():
    """
    High-level view of PRIME's curriculum across all subjects.
    Currently includes math foundations and money foundations history.
    """
    math_curriculum: SubjectCurriculum = build_math_foundations_curriculum()
    money_history_curriculum: SubjectCurriculum = (
        build_money_foundations_history_curriculum()
    )

    snapshot = CurriculumSnapshot(
        subjects=[
            math_curriculum,
            money_history_curriculum,
        ]
    )

    return CurriculumSnapshotResponse(
        description=(
            "PRIME's current curriculum snapshot. Math foundations holds early number sense "
            "lessons; Money Foundations: History of Money holds an overview of how money developed."
        ),
        curriculum=snapshot,
    )
