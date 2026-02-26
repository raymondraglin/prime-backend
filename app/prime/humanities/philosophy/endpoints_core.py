from fastapi import APIRouter
from pydantic import BaseModel

from app.prime.curriculum.models import (
    PhilosophyRubricDimension,
    PhilosophyRubricScore,
    PhilosophyRubricEvaluateRequest,
    PhilosophyRubricEvaluateResponse,
)

router = APIRouter(
    prefix="/prime/humanities/philosophy",
    tags=["philosophy-core"],
)


class PhilosophyHelloResponse(BaseModel):
    message: str


@router.get(
    "/hello",
    response_model=PhilosophyHelloResponse,
    name="philosophy_root_hello",
)
async def philosophy_root_hello() -> PhilosophyHelloResponse:
    """
    Simple root hello endpoint for philosophy namespace.
    """
    return PhilosophyHelloResponse(
        message="PRIME philosophy root router is alive."
    )


@router.post(
    "/rubric/evaluate-answer",
    response_model=PhilosophyRubricEvaluateResponse,
    name="philosophy_rubric_evaluate_answer",
)
async def philosophy_rubric_evaluate_answer(
    req: PhilosophyRubricEvaluateRequest,
) -> PhilosophyRubricEvaluateResponse:
    """
    Stub rubric evaluation endpoint for philosophy answers.

    For now this returns mid-level scores with generic explanations.
    Later, this can be wired to the reasoning core or a dedicated evaluator.
    """
    scores = [
        PhilosophyRubricScore(
            dimension=PhilosophyRubricDimension.CLARITY,
            score_1_to_5=3,
            explanation=(
                "The answer is partly clear but its structure and key claims could be sharper."
            ),
        ),
        PhilosophyRubricScore(
            dimension=PhilosophyRubricDimension.CHARITY,
            score_1_to_5=3,
            explanation=(
                "It mentions alternative views but does not fully develop them in their strongest form."
            ),
        ),
        PhilosophyRubricScore(
            dimension=PhilosophyRubricDimension.RIGOR,
            score_1_to_5=3,
            explanation=(
                "Some reasons and distinctions are present, but counterarguments are not systematically addressed."
            ),
        ),
        PhilosophyRubricScore(
            dimension=PhilosophyRubricDimension.HISTORY_AWARENESS,
            score_1_to_5=2,
            explanation=(
                "The answer hints at historical ideas but rarely names specific traditions or figures."
            ),
        ),
    ]

    overall_comment = (
        "Overall, this is a promising partial answer, but it would benefit from a clearer structure, "
        "more careful presentation of competing views, and explicit references to key historical "
        "figures or schools where relevant."
    )

    return PhilosophyRubricEvaluateResponse(
        scores=scores,
        overall_comment=overall_comment,
    )
