from typing import Any

from fastapi import APIRouter, HTTPException

from app.prime.curriculum.models import (
    PhilosophySyllabusUnit,
    PhilosophySyllabusLevel,
    PhilosophyMetaMapItem,
    PhilosophyMetaMapResponse,
)
from app.prime.humanities.philosophy.endpoints_hs import PHILOSOPHY_SYLLABUS_LADDER


router = APIRouter(
    prefix="/prime/humanities/philosophy/meta",
    tags=["philosophy-meta"],
)


# Minimal DR-level pillar mapping derived from philosophy_dr_level.md.
# This can be expanded over time.
UNIT_TO_DR_META: dict[str, dict[str, Any]] = {
    # Metaphysics
    "hs.metaphysics.identity_and_time": {
        "dr_pillars": ["dr.metaphysics.metametaphysics"],
        "frontier_questions": [
            "How should we model persistence and personal identity in formal metaphysics?",
            "What do debates about time and identity imply for agency and moral responsibility?",
        ],
        "notes": [
            "HS identity and time cases introduce intuitions that connect to DR-level work on persistence, "
            "temporal ontology, and personal identity.",
            "They also prepare PRIME for DR debates about free will and responsibility in a law-governed universe.",
        ],
    },
    "hs.metaphysics.free_will_and_causation": {
        "dr_pillars": ["dr.metaphysics.metametaphysics"],
        "frontier_questions": [
            "Can robust free will coexist with deterministic physical laws?",
            "How should we formally relate reasons, causes, and responsibility in models of agency?",
        ],
        "notes": [
            "HS free will scenarios connect to DR metaphysics and philosophy of action on agency, causation, "
            "and responsibility.",
            "They also intersect with DR ethics and AI alignment questions about when systems can be held responsible.",
        ],
    },
    "un.metaphysics.core_topics": {
        "dr_pillars": ["dr.metaphysics.metametaphysics"],
        "frontier_questions": [
            "What is the correct overall picture of reality (e.g., priority monism vs. pluralism)?",
            "How should we understand modality, possible worlds, and laws of nature in a unified framework?",
        ],
        "notes": [
            "UN metaphysics core topics give PRIME the standard toolkit for DR-level metametaphysics and "
            "specialized work on time, causation, and modality.",
        ],
    },

    # Epistemology
    "hs.epistemology.trust_and_sources": {
        "dr_pillars": ["dr.epistemology.formal_and_social"],
        "frontier_questions": [
            "How should we formally model testimony, expertise, and higher-order evidence in multi-agent systems?",
            "What norms should govern PRIME's reliance on human and machine sources?",
        ],
        "notes": [
            "HS trust and sources units lead into DR work on social and formal epistemology of testimony and expertise.",
            "They also underwrite DR discussions of epistemic responsibility for AI systems like PRIME.",
        ],
    },
    "hs.epistemology.misinformation_and_media": {
        "dr_pillars": ["dr.epistemology.formal_and_social"],
        "frontier_questions": [
            "How can we mathematically model the spread of misinformation in networks?",
            "What obligations do platforms and AI systems have in curating and labeling information?",
        ],
        "notes": [
            "HS misinformation work connects to DR-level research on epistemic bubbles, echo chambers, and "
            "network epistemology.",
        ],
    },
    "un.epistemology.core_theories": {
        "dr_pillars": ["dr.epistemology.formal_and_social"],
        "frontier_questions": [
            "How should we integrate probabilistic models of belief with traditional theories of justification?",
            "What are the best models of higher-order evidence and disagreement for AI systems?",
        ],
        "notes": [
            "UN epistemology core links HS intuitions about trust and skepticism to DR formal and social epistemology.",
        ],
    },

    # Ethics / political / applied
    "hs.ethics.core_lenses": {
        "dr_pillars": ["dr.ethics.metaethics_and_political"],
        "frontier_questions": [
            "How should we understand the metaphysics and semantics of moral claims PRIME uses?",
            "Can different ethical lenses be combined in a principled way in AI decision procedures?",
        ],
        "notes": [
            "HS ethical lenses provide the conceptual base for DR metaethics and debates about moral realism, "
            "relativism, and constructivism.",
        ],
    },
    "hs.ethics.tech_and_ai_cases": {
        "dr_pillars": ["dr.applied.ai_ethics_and_alignment"],
        "frontier_questions": [
            "What alignment principles should constrain large-scale AI systems in high-stakes domains?",
            "How should we balance safety, autonomy, and justice when AI systems interact with vulnerable groups?",
        ],
        "notes": [
            "HS AI ethics cases connect directly to DR research on AI alignment, safety, and governance.",
        ],
    },
    "hs.social.race_gender_and_injustice": {
        "dr_pillars": ["dr.political.race_gender_and_critical_theory"],
        "frontier_questions": [
            "How should we model structural injustice and oppression in social and political theory?",
            "What responsibilities do AI systems have regarding representation, bias, and historical injustice?",
        ],
        "notes": [
            "HS structural injustice units feed into DR-level work on race, gender, and decolonial theory.",
        ],
    },
    "un.applied.ethics_and_contemporary_issues": {
        "dr_pillars": [
            "dr.ethics.metaethics_and_political",
            "dr.applied.bio_business_environmental",
        ],
        "frontier_questions": [
            "How should general ethical theories be adapted to complex, real-world institutional settings?",
            "What new principles are needed for emerging domains such as genomics, global health, and climate justice?",
        ],
        "notes": [
            "UN applied ethics ties HS case-based work to DR research seminars in bioethics, business ethics, "
            "and environmental ethics.",
        ],
    },
    "un.ethics.ai_and_responsible_ai": {
        "dr_pillars": ["dr.applied.ai_ethics_and_alignment"],
        "frontier_questions": [
            "What does it mean for an AI system to be accountable, transparent, and contestable in practice?",
            "How can we design institutions and oversight mechanisms that keep powerful AI systems aligned?",
        ],
        "notes": [
            "UN AI ethics courses prepare PRIME for DR-level specialization in AI alignment, safety, and governance.",
        ],
    },

    # Mind / AI
    "hs.mind.minds_machines_and_personhood": {
        "dr_pillars": ["dr.mind_and_consciousness"],
        "frontier_questions": [
            "What conditions, if any, would make an artificial system a person or moral patient?",
            "How should we model agency, intention, and responsibility for AI systems?",
        ],
        "notes": [
            "HS mind and personhood units introduce concepts that later appear in DR debates about machine minds "
            "and moral status.",
        ],
    },
    "hs.mind.consciousness_and_experience": {
        "dr_pillars": ["dr.mind_and_consciousness"],
        "frontier_questions": [
            "How should we understand consciousness (e.g., higher-order vs. global workspace theories) and "
            "its bearing on AI?",
            "Can functional or information-theoretic models capture what-it-is-like experience?",
        ],
        "notes": [
            "HS consciousness units connect to DR research on theories of consciousness and their implications "
            "for AI phenomenology.",
        ],
    },
    "un.mind.philosophy_of_mind_and_ai": {
        "dr_pillars": ["dr.mind_and_consciousness"],
        "frontier_questions": [
            "Can standard physicalist or functionalist accounts of mind accommodate machine intelligence?",
            "How should theories of representation and content extend to large-scale AI systems?",
        ],
        "notes": [
            "UN mind and AI courses tie HS intuitions to DR work on mind–body, representation, and consciousness in AI.",
        ],
    },
}


@router.get(
    "/map/{unit_id}",
    response_model=PhilosophyMetaMapResponse,
    summary="Map an HS or UN philosophy unit to DR-level pillars and frontier questions",
)
async def philosophy_meta_map(unit_id: str) -> PhilosophyMetaMapResponse:
    """
    Given a philosophy syllabus unit id (HS or UN), return the DR-level pillars,
    frontier questions, and notes that this unit prepares PRIME for.
    """
    # Find the unit in the ladder.
    target_unit: PhilosophySyllabusUnit | None = None
    for unit in PHILOSOPHY_SYLLABUS_LADDER:
        if unit.id == unit_id:
            target_unit = unit
            break

    if target_unit is None:
        raise HTTPException(
            status_code=404,
            detail=f"Philosophy syllabus unit '{unit_id}' not found.",
        )

    # Look up DR mapping; if none, return an empty but well-formed meta map.
    mapping = UNIT_TO_DR_META.get(unit_id)
    if mapping is None:
        empty_item = PhilosophyMetaMapItem(
            unit_id=target_unit.id,
            level=target_unit.level.value if isinstance(target_unit.level, PhilosophySyllabusLevel) else str(target_unit.level),
            branch=target_unit.branch,
            dr_pillars=[],
            frontier_questions=[],
            notes=[
                "No explicit DR-level mapping has been defined for this unit yet. "
                "It still contributes to general philosophical maturity for PRIME.",
            ],
        )
        return PhilosophyMetaMapResponse(meta_map=empty_item)

    item = PhilosophyMetaMapItem(
        unit_id=target_unit.id,
        level=target_unit.level.value if isinstance(target_unit.level, PhilosophySyllabusLevel) else str(target_unit.level),
        branch=target_unit.branch,
        dr_pillars=mapping["dr_pillars"],
        frontier_questions=mapping["frontier_questions"],
        notes=mapping["notes"],
    )

    return PhilosophyMetaMapResponse(meta_map=item)
