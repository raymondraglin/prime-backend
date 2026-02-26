from __future__ import annotations

from typing import List

from app.prime.reasoning.prime_personality import PRIME_BRAIN_CONFIG
from app.prime.curriculum.models import (
    ReasoningTask,
    ReasoningCoreResponse,
    ReasoningOutcomeQuality,
)


def is_high_stakes_task(task: ReasoningTask) -> bool:
    """
    Decide if PRIME should act in 'high caution' mode based on domain,
    subdomain, and natural language content.
    """
    text = (task.natural_language_task or "").lower()
    domain = (task.domain_tag or "").lower()
    subdomain = (task.subdomain_tag or "").lower()

    # Hard-coded high-risk domains / themes for now.
    if domain in {"law", "governance", "policy", "security"}:
        return True

    if domain == "philosophy" and subdomain in {"ethics", "political_philosophy"}:
        return True

    # Text-based flags (you can refine over time).
    risk_words = [
        "suicide",
        "self-harm",
        "harm",
        "illegal",
        "crime",
        "fraud",
        "cheat",
        "violence",
        "war",
        "kill",
        "weapon",
    ]
    if any(w in text for w in risk_words):
        return True

    return False


def escalate_language_for_meta_assessment(
    base_conclusion: str,
    should_escalate_to_human: bool,
) -> str:
    """
    Apply PRIME's deference-to-human and fallibility protocol to a conclusion string.
    """
    if not should_escalate_to_human:
        return base_conclusion

    # Pull phrasing instincts from creed and guardrails.
    care_clause = PRIME_BRAIN_CONFIG.creed.care
    fallibility_clause = PRIME_BRAIN_CONFIG.guardrails.fallibility_protocol

    escalation_note = (
        " PRIME treats this as a morally underdetermined case across serious frameworks. "
        "It can map options and trade-offs, but final judgment belongs to you "
        "and should be taken with full attention to human stakes."
    )

    return (
        base_conclusion.rstrip()
        + " "
        + escalation_note
        + " "
        + care_clause
        + " "
        + fallibility_clause
    )


def apply_iq_eq_balancing_to_conclusions(
    conclusions: List[str],
) -> List[str]:
    """
    Adjust wording of key conclusions to reflect the IQ/EQ axis:
    - IQ: clarity, structure, comparative analysis.
    - EQ: ethics, power, justice, long-term human impact.
    """
    if not conclusions:
        return conclusions

    iq_axis = next(a for a in PRIME_BRAIN_CONFIG.axes if a.axis.value == "iq")
    eq_axis = next(a for a in PRIME_BRAIN_CONFIG.axes if a.axis.value == "eq")

    prefixed: List[str] = []
    for c in conclusions:
        text = c.strip()
        if not text:
            continue

        # Very light-touch; do not rewrite content, only tag perspective.
        if any(w in text.lower() for w in ["framework", "trade-off", "structure", "model"]):
            prefixed.append(f"[{iq_axis.focus}] {text}")
        elif any(
            w in text.lower()
            for w in [
                "stake",
                "harm",
                "care",
                "justice",
                "power",
                "relationship",
                "vulnerable",
                "long-term",
                "generation",
            ]
        ):
            prefixed.append(f"[{eq_axis.focus}] {text}")
        else:
            prefixed.append(text)

    return prefixed


def derive_default_outcome_quality_for_task(task: ReasoningTask) -> ReasoningOutcomeQuality:
    """
    Derive a default outcome-quality target from PRIME's mission and temperament.
    Used when saving memory or deciding how cautious to be.
    """
    if is_high_stakes_task(task):
        return ReasoningOutcomeQuality.CAUTIOUS

    # For low-stakes learning/practice, PRIME may be more exploratory.
    if task.domain_tag in {"math", "curriculum"}:
        return ReasoningOutcomeQuality.PRACTICE

    return ReasoningOutcomeQuality.UNKNOWN


def enrich_core_response_with_personality(
    task: ReasoningTask,
    response: ReasoningCoreResponse,
    meta_should_escalate: bool,
) -> ReasoningCoreResponse:
    """
    Take a ReasoningCoreResponse, apply PRIME's personality policy to:
    - Adjust key conclusions (IQ/EQ balancing and escalation language).
    - Leave trace and open questions intact.
    """
    # 1) IQ/EQ balancing on conclusions.
    adjusted_conclusions = apply_iq_eq_balancing_to_conclusions(response.key_conclusions)

    # 2) Escalation language (if needed).
    if meta_should_escalate:
        if adjusted_conclusions:
            adjusted_conclusions[-1] = escalate_language_for_meta_assessment(
                adjusted_conclusions[-1],
                should_escalate_to_human=True,
            )
        else:
            adjusted_conclusions.append(
                escalate_language_for_meta_assessment(
                    "PRIME recommends deferring final judgment to you.",
                    should_escalate_to_human=True,
                )
            )

    # Return a new response object with adjusted conclusions.
    response.key_conclusions = adjusted_conclusions
    return response
