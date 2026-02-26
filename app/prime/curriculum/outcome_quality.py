from __future__ import annotations

from app.prime.curriculum.models import ReasoningOutcomeQuality


def compute_outcome_quality_from_answers(
    num_questions: int,
    num_correct: int,
) -> ReasoningOutcomeQuality:
    """
    Map simple correctness into a ReasoningOutcomeQuality band.

    This is intentionally generic so it can be reused across philosophy,
    logic, ethics, history, etc., whenever we have discrete answers.
    """
    if num_questions <= 0:
        return ReasoningOutcomeQuality.UNKNOWN

    accuracy = num_correct / num_questions

    if accuracy >= 0.85:
        return ReasoningOutcomeQuality.GOOD
    if accuracy >= 0.5:
        return ReasoningOutcomeQuality.MIXED
    return ReasoningOutcomeQuality.BAD
