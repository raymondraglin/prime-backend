from fastapi import APIRouter
from pydantic import BaseModel

from app.prime.curriculum.models import SubjectCurriculum
from app.prime.curriculum.money_foundations_history import (
    build_money_foundations_history_curriculum,
)


router = APIRouter()


class MoneyHistoryCurriculumResponse(BaseModel):
    description: str
    curriculum: SubjectCurriculum


@router.get("/money/history/curriculum", response_model=MoneyHistoryCurriculumResponse)
async def money_history_curriculum():
    """
    Get the curriculum for the Money Foundations: History of Money subject.
    """
    curriculum = build_money_foundations_history_curriculum()
    return MoneyHistoryCurriculumResponse(
        description="Money Foundations: History of Money curriculum.",
        curriculum=curriculum,
    )
