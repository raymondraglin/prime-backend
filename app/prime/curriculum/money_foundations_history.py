from app.prime.curriculum.models import (
    SubjectId,
    DifficultyLevel,
    LessonKind,
    Lesson,
    SubjectCurriculum,
    DomainId,
    CurriculumLevel,
)
from app.prime.curriculum.money_history import get_history_of_money


def build_money_foundations_history_curriculum() -> SubjectCurriculum:
    """
    Curriculum for the Money Foundations: History of Money subject.
    """
    events = get_history_of_money()

    lesson_money_hist_overview = Lesson(
        id="money_hist_overview",
        subject=SubjectId.MONEY_FOUNDATIONS_HISTORY,
        title="Overview: History of Money",
        kind=LessonKind.HISTORY,
        difficulty=DifficultyLevel.EARLY,
        description=(
            "A timeline of how money evolved from barter and commodity money to coins, paper money, "
            "banks, and modern digital systems."
        ),
        content={
            "events": [ev.model_dump() for ev in events],
        },
    )

    recommended_order = [
        lesson_money_hist_overview.id,
    ]

    return SubjectCurriculum(
        subject=SubjectId.MONEY_FOUNDATIONS_HISTORY,
        name="Money Foundations: History of Money",
        description=(
            "A focused history track showing how money developed from early barter and commodities "
            "to coins, paper, banks, and digital money, linked back to PRIME's math foundations."
        ),
        lessons=[
            lesson_money_hist_overview,
        ],
        recommended_order=recommended_order,
        domain=DomainId.BUSINESS_ECONOMICS_AND_MANAGEMENT,
        default_level=CurriculumLevel.SCHOOL_SECONDARY,
    )

