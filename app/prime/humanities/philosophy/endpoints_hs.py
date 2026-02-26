from enum import Enum
from typing import Optional, Any, List, Iterable, Literal
import httpx
from fastapi import APIRouter, Request, HTTPException, Query
from app.prime.history.models import HistoryLesson
from app.prime.curriculum.models import DomainId, CurriculumLevel, SubjectId
from pydantic import BaseModel

import json
import random
from random import sample
from datetime import datetime
from pathlib import Path

from app.prime.reasoning.memory_store import iter_memory_entries
from app.prime.curriculum.models import (
    # Core lesson / curriculum types
    PhilosophyLesson,
    SubjectId,
    LessonKind,
    DifficultyLevel,
    DomainId,
    CurriculumLevel,
    # Lane planners and branch classifier
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
    # Concept lessons
    LogicConceptId,
    LogicConceptLesson,
    MethodsConceptId,
    MethodsConceptLesson,
    MethodsConceptPracticeSet,
    MetaphysicsConceptId,
    MetaphysicsConceptLesson,
    EthicsFramework,
    EthicsFourLensDilemmaRequest,
    EthicsFourLensResponse,
    EthicsConsequentialismPracticeAnalysis,
    EthicsConsequentialismPracticeResponse,
    EthicsDeontologyPracticeAnalysis,
    EthicsDeontologyPracticeResponse,
    EthicsVirtuePracticeAnalysis,
    EthicsVirtuePracticeResponse,
    EthicsCarePracticeAnalysis,
    EthicsCarePracticeResponse,
    EthicsSingleLensSummary,
    EthicsMetaPerspectiveMode,
    EthicsMetaPerspectiveSummary,
    EthicsMetaPerspectivesResponse,
    EthicsDigitalContextTag,
    EthicsDigitalPracticeRequest,
    EthicsDigitalPracticeResponse,
    EthicsDigitalFrameworkEvaluation,
    ReasoningTask,
    ReasoningTaskKind,
    ReasoningCoreRequest,
    ReasoningCoreResponse,
    ReasoningTraceTag,
    ReasoningOutcomeQuality,
    ReasoningMemoryEntry,
    PhilosophyHSEthicsPracticeRequest,
    PhilosophyHSEthicsPracticeResponse,
    PhilosophyRubricDimension,
    PhilosophyRubricScore,
    PhilosophyRubricEvaluateRequest,
    PhilosophyRubricEvaluateResponse,
    HSPhilosophyUnit,
    HSPhilosophyUnitsOverview,
    PhilosophySyllabusUnit,
    PhilosophySyllabusLadder,
    PhilosophySyllabusLevel,
    PhilosophyWarmupBranch,
    PhilosophyWarmupItem,
    PhilosophyWarmupResponse,
    PhilosophyPracticeItem,
    PhilosophyPracticeSetResponse,
    PhilosophyReflectionSession,
    PhilosophyReflectionSummary,
    PhilosophyReflectionPrinciple,
)


from app.prime.reasoning.personality_policy import is_high_stakes_task
from app.prime.reasoning.memory_store import append_memory_entry
from app.prime.humanities.philosophy.endpoints_bridge import (
    BridgeRequest,
    BridgeResponse,
)
from app.prime.humanities.philosophy.endpoints_k8 import (
    PhilosophyLane1PlannerRequest as K8PhilosophyLane1PlannerRequest,
    PhilosophyLane1PlannerResponse as K8PhilosophyLane1PlannerResponse,
    PhilosophyBranchPracticeRequest as K8PhilosophyBranchPracticeRequest,
    PhilosophyBranchPracticeResponse as K8PhilosophyBranchPracticeResponse,
)


router = APIRouter(
    prefix="/prime/humanities/philosophy/hs",
    tags=["philosophy-hs"],
)
router = APIRouter(
    prefix="/prime/humanities/philosophy/hs",
    tags=["philosophy-hs-casebook"],
)

LOG_PATH = Path("logs/hs_ethics_deep_dives.jsonl")


def log_hs_ethics_event(event: dict) -> None:
    """
    Append a single HS ethics event as one JSON line.
    Best-effort: failures should not break the API.
    """
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    except Exception:
        # Keep PRIME answering even if logging breaks.
        pass

class PhilosophyHSHelloResponse(BaseModel):
    description: str


@router.get("/hello", response_model=PhilosophyHSHelloResponse)
async def philosophy_hs_hello() -> PhilosophyHSHelloResponse:
    """
    High-school philosophy endpoints (Lane 2+). Placeholder for now.
    """
    return PhilosophyHSHelloResponse(
        description="PRIME humanities/philosophy high-school spine is wired (placeholder)."
    )

HS_PHILOSOPHY_HS_UNITS: list[HSPhilosophyUnit] = [
    HSPhilosophyUnit(
        id="hs.ethics.core_lenses",
        branch="ethics",
        title="Ethics Core Lenses: Outcomes, Rules, Character, Relationships",
        short_description="Introduce the four main lenses PRIME will use to analyze ethical dilemmas.",
        core_questions=[
            "What makes an action right or wrong?",
            "How do outcomes, rules, character, and relationships each matter in ethics?",
        ],
        key_concepts=[
            "consequences vs. duties",
            "virtue and character",
            "care and relationships",
            "fairness and partiality",
        ],
        canonical_practice_endpoints=[
            "/prime/humanities/philosophy/hs/ethics/practice/loyalty_vs_fairness",
            "/prime/humanities/philosophy/hs/ethics/practice/truth_vs_kindness",
        ],
        suggested_sequence_position=1,
    ),
    HSPhilosophyUnit(
        id="hs.epistemology.trust_and_sources",
        branch="epistemology",
        title="Trusting Information and Sources",
        short_description="How PRIME should think about testimony, experts, and online information.",
        core_questions=[
            "When is it reasonable to trust what others say?",
            "How should we evaluate information from the internet and experts?",
        ],
        key_concepts=[
            "testimony",
            "expertise",
            "bias and reliability",
            "evidence vs. opinion",
        ],
        canonical_practice_endpoints=[
            "/prime/humanities/philosophy/hs/epistemology/practice/trust_the_internet",
            "/prime/humanities/philosophy/hs/epistemology/practice/trusting_experts",
        ],
        suggested_sequence_position=1,
    ),
    HSPhilosophyUnit(
        id="hs.history.cross_era_comparisons",
        branch="history",
        title="Cross-Era Comparisons in Philosophy",
        short_description="Compare how different eras frame knowledge, faith, and the person.",
        core_questions=[
            "How do ancient, medieval, and modern thinkers disagree about knowledge and the self?",
            "Which structural patterns repeat across historical eras?",
        ],
        key_concepts=[
            "ancient vs. early modern epistemology",
            "medieval vs. modern faith and reason",
            "ancient vs. modern conceptions of the person",
        ],
        canonical_practice_endpoints=[
            "/prime/humanities/philosophy/hs/history/practice/ancient_vs_earlymodern_epistemology",
            "/prime/humanities/philosophy/hs/history/practice/medieval_vs_modern_faith_reason",
            "/prime/humanities/philosophy/hs/history/practice/ancient_vs_modern_person",
        ],
        suggested_sequence_position=1,
    ),
]

PHILOSOPHY_SYLLABUS_LADDER: list[PhilosophySyllabusUnit] = [
    # HS ethics core lenses (already mirrored by HS units)
    PhilosophySyllabusUnit(
        id="hs.ethics.core_lenses",
        level=PhilosophySyllabusLevel.HS,
        branch="ethics",
        title="Ethics Core Lenses: Outcomes, Rules, Character, Relationships",
        short_description="Introduce the four main lenses PRIME will use to analyze ethical dilemmas.",
        core_questions=[
            "What makes an action right or wrong?",
            "How do outcomes, rules, character, and relationships each matter in ethics?",
        ],
        key_concepts=[
            "consequentialism vs. deontology",
            "virtue and character",
            "care and relationships",
            "fairness and partiality",
        ],
        canonical_practice_endpoints=[
            "/prime/humanities/philosophy/hs/ethics/practice/loyalty_vs_fairness",
            "/prime/humanities/philosophy/hs/ethics/practice/truth_vs_kindness",
        ],
        prerequisites=[],
        recommended_next_units=[
            "un.ethics.normative_and_metaethics",
        ],
    ),
    # UN ethics: normative + metaethics + AI ethics foundations
    PhilosophySyllabusUnit(
        id="un.ethics.normative_and_metaethics",
        level=PhilosophySyllabusLevel.UN,
        branch="ethics",
        title="Normative and Metaethics + AI Ethics Foundations",
        short_description=(
            "Full versions of classical ethical theories and metaethics, plus groundwork for AI ethics."
        ),
        core_questions=[
            "What do consequentialism, deontology, virtue, and care ethics each say about right action?",
            "Are there moral facts, and how should PRIME treat disagreement and moral uncertainty?",
            "How should ethical theory shape PRIME's behavior in AI and tech contexts?",
        ],
        key_concepts=[
            "consequentialism (act vs. rule)",
            "Kantian deontology, rights, respect",
            "virtue ethics and flourishing",
            "care ethics and relational views",
            "moral realism vs. anti-realism",
            "cognitivism vs. non-cognitivism",
            "relativism vs. objectivism",
            "moral concepts: rights, duties, permissions, supererogation",
            "responsibility, blame, ignorance, intention",
            "AI ethics: fairness, bias, transparency, accountability, privacy, safety",
        ],
        canonical_practice_endpoints=[
            "/prime/humanities/philosophy/un/ethics/practice/classical_theories",   # to be implemented
            "/prime/humanities/philosophy/un/ethics/practice/ai_ethics_foundations",  # to be implemented
        ],
        prerequisites=[
            "hs.ethics.core_lenses",
        ],
        recommended_next_units=[
            "dr.ethics.advanced_metaethics",
            "un.applied.ethics_and_contemporary_issues",
        ],
    ),
    # HS epistemology trust/sources
    PhilosophySyllabusUnit(
        id="hs.epistemology.trust_and_sources",
        level=PhilosophySyllabusLevel.HS,
        branch="epistemology",
        title="Trusting Information and Sources",
        short_description="When and how PRIME should trust testimony, experts, and online information.",
        core_questions=[
            "When is it reasonable to trust what others say?",
            "How should PRIME evaluate information from the internet and experts?",
        ],
        key_concepts=[
            "testimony",
            "expertise",
            "bias and reliability",
            "evidence vs. opinion",
        ],
        canonical_practice_endpoints=[
            "/prime/humanities/philosophy/hs/epistemology/practice/trust_the_internet",
            "/prime/humanities/philosophy/hs/epistemology/practice/trusting_experts",
        ],
        prerequisites=[],
        recommended_next_units=[
            "un.epistemology.core_theories",
        ],
    ),
    # UN epistemology core
    PhilosophySyllabusUnit(
        id="un.epistemology.core_theories",
        level=PhilosophySyllabusLevel.UN,
        branch="epistemology",
        title="Epistemology: Justification, Skepticism, and Evidence",
        short_description="Undergraduate-level treatment of knowledge, justification, and skepticism.",
        core_questions=[
            "What is knowledge and how does it differ from true belief?",
            "What is justification, and how do internalism and externalism differ?",
            "How should PRIME respond to skeptical arguments and incomplete evidence?",
        ],
        key_concepts=[
            "justification, warrant, evidence",
            "skepticism (Cartesian, inductive, external-world)",
            "internalism vs. externalism",
            "foundationalism, coherentism, reliabilism",
            "defeaters and higher-order evidence",
        ],
        canonical_practice_endpoints=[
            "/prime/humanities/philosophy/un/epistemology/practice/core_cases",  # to be implemented
        ],
        prerequisites=[
            "hs.epistemology.trust_and_sources",
        ],
        recommended_next_units=[
            "dr.epistemology.advanced_topics",
        ],
    ),
    # HS history cross-era
    PhilosophySyllabusUnit(
        id="hs.history.cross_era_comparisons",
        level=PhilosophySyllabusLevel.HS,
        branch="history",
        title="Cross-Era Comparisons in Philosophy",
        short_description="Compare how different eras frame knowledge, faith, and the person.",
        core_questions=[
            "How do ancient, medieval, and modern thinkers disagree about knowledge and the self?",
            "Which structural patterns repeat across historical eras, and how should PRIME use them?",
        ],
        key_concepts=[
            "ancient vs. early modern epistemology",
            "medieval vs. modern faith and reason",
            "ancient vs. modern conceptions of the person",
        ],
        canonical_practice_endpoints=[
            "/prime/humanities/philosophy/hs/history/practice/ancient_vs_earlymodern_epistemology",
            "/prime/humanities/philosophy/hs/history/practice/medieval_vs_modern_faith_reason",
            "/prime/humanities/philosophy/hs/history/practice/ancient_vs_modern_person",
        ],
        prerequisites=[],
        recommended_next_units=[
            "un.history.ancient_and_medieval",
            "un.history.earlymodern_to_20c",
        ],
    ),
    # UN history of philosophy surveys (placeholder units to connect ladder)
    PhilosophySyllabusUnit(
        id="un.history.ancient_and_medieval",
        level=PhilosophySyllabusLevel.UN,
        branch="history",
        title="History of Philosophy: Ancient and Medieval",
        short_description="Survey of ancient Greek, Indian, Chinese, and medieval Islamic/Christian/Jewish philosophy.",
        core_questions=[
            "How did ancient and medieval thinkers frame metaphysics, ethics, and knowledge?",
            "What continuities and breaks link ancient and medieval philosophy to modern thought?",
        ],
        key_concepts=[
            "Socrates, Plato, Aristotle",
            "Upanishads, early Buddhism",
            "Confucius, Laozi, Zhuangzi",
            "Avicenna, Averroes, Aquinas",
        ],
        canonical_practice_endpoints=[],
        prerequisites=[
            "hs.history.cross_era_comparisons",
        ],
        recommended_next_units=[
            "un.history.earlymodern_to_20c",
        ],
    ),
    PhilosophySyllabusUnit(
        id="un.history.earlymodern_to_20c",
        level=PhilosophySyllabusLevel.UN,
        branch="history",
        title="History of Philosophy: Early Modern to 20th Century",
        short_description="From Descartes and Locke to Kant, Hegel, Nietzsche, and 20th-century movements.",
        core_questions=[
            "How did early modern philosophers rethink knowledge, mind, and science?",
            "How did 19th and 20th century movements reshape metaphysics, ethics, and politics?",
        ],
        key_concepts=[
            "Descartes, Spinoza, Leibniz",
            "Locke, Berkeley, Hume",
            "Kant and German Idealism",
            "Nietzsche, existentialism, analytic and continental traditions",
        ],
        canonical_practice_endpoints=[],
        prerequisites=[
            "un.history.ancient_and_medieval",
        ],
        recommended_next_units=[
            "dr.history.specialized_seminars",
        ],
    ),
    # HS logic: informal reasoning and fallacies
    PhilosophySyllabusUnit(
        id="hs.logic.informal_and_fallacies",
        level=PhilosophySyllabusLevel.HS,
        branch="logic",
        title="Informal Reasoning and Common Fallacies",
        short_description="Teach PRIME to recognize good arguments and common fallacies in ordinary language.",
        core_questions=[
            "What makes an argument strong or weak in everyday reasoning?",
            "What are common informal fallacies and how can PRIME avoid them?",
        ],
        key_concepts=[
            "argument vs. assertion",
            "premises and conclusions",
            "validity vs. soundness (intuitive sense)",
            "informal fallacies (ad hominem, straw man, slippery slope, etc.)",
        ],
        canonical_practice_endpoints=[
            "/prime/humanities/philosophy/hs/logic/practice/identify_fallacies",
            "/prime/humanities/philosophy/hs/logic/practice/everyday_arguments",
        ],
        prerequisites=[],
        recommended_next_units=[
            "hs.logic.basic_propositional",
        ],
    ),
    # HS logic: basic propositional logic
    PhilosophySyllabusUnit(
        id="hs.logic.basic_propositional",
        level=PhilosophySyllabusLevel.HS,
        branch="logic",
        title="Basic Propositional Logic for PRIME",
        short_description="Introduce propositional logic as a structured way to test argument validity.",
        core_questions=[
            "How can PRIME represent simple arguments using propositional logic?",
            "How do connectives and truth conditions relate to valid argument forms?",
        ],
        key_concepts=[
            "propositional variables",
            "logical connectives (and, or, not, if...then)",
            "truth tables (small cases)",
            "valid patterns (modus ponens, modus tollens) vs. invalid ones",
        ],
        canonical_practice_endpoints=[
            "/prime/humanities/philosophy/hs/logic/practice/propositional_patterns",
        ],
        prerequisites=[
            "hs.logic.informal_and_fallacies",
        ],
        recommended_next_units=[
            "un.logic.full_intro",
        ],
    ),
    # UN logic: full intro (propositional + predicate, proofs, semantics)
    PhilosophySyllabusUnit(
        id="un.logic.full_intro",
        level=PhilosophySyllabusLevel.UN,
        branch="logic",
        title="Introductory Logic: Propositional and Predicate",
        short_description=(
            "Undergraduate-level course in formal logic: syntax, semantics, and natural deduction for "
            "propositional and predicate logic."
        ),
        core_questions=[
            "How can PRIME represent arguments in a precise formal language?",
            "What is the relationship between syntactic proofs and semantic validity?",
            "How does quantification extend propositional logic to talk about objects?",
        ],
        key_concepts=[
            "formal languages: syntax and semantics",
            "propositional logic: connectives, truth tables, tautology, validity",
            "natural deduction systems and rules of inference",
            "predicate logic: quantifiers, domains, identity",
            "soundness and completeness ideas (at a high level)",
        ],
        canonical_practice_endpoints=[
            "/prime/humanities/philosophy/un/logic/practice/propositional_proofs",
            "/prime/humanities/philosophy/un/logic/practice/predicate_proofs",
        ],
        prerequisites=[
            "hs.logic.basic_propositional",
        ],
        recommended_next_units=[
            "un.logic.intro_nonclassical",
            "dr.logic.advanced_topics",
        ],
    ),
    # UN logic: intro non-classical (for PRIME’s AI role)
    PhilosophySyllabusUnit(
        id="un.logic.intro_nonclassical",
        level=PhilosophySyllabusLevel.UN,
        branch="logic",
        title="Introduction to Non-Classical Logics",
        short_description="Survey modal, intuitionistic, relevance, and paraconsistent logics and why they matter for AI and reasoning under uncertainty.",
        core_questions=[
            "Why might classical logic be too strict or too permissive for some reasoning tasks?",
            "How do modal, intuitionistic, and paraconsistent logics differ from classical logic?",
            "How can PRIME reason safely with inconsistent or incomplete information?",
        ],
        key_concepts=[
            "modal logic: necessity and possibility",
            "intuitionistic logic and constructivism",
            "relevance logic and relevance constraints",
            "paraconsistent logic and reasoning with inconsistency",
        ],
        canonical_practice_endpoints=[
            "/prime/humanities/philosophy/un/logic/practice/modal_patterns",
            "/prime/humanities/philosophy/un/logic/practice/reason_with_inconsistency",
        ],
        prerequisites=[
            "un.logic.full_intro",
        ],
        recommended_next_units=[
            "dr.logic.advanced_topics",
        ],
    ),
    # HS ethics: concrete dilemmas and stakeholder thinking
    PhilosophySyllabusUnit(
        id="hs.ethics.stakeholders_and_harms",
        level=PhilosophySyllabusLevel.HS,
        branch="ethics",
        title="Stakeholders, Harms, and Fairness",
        short_description=(
            "Train PRIME to map stakeholders, harms, benefits, and fairness concerns in real-world cases."
        ),
        core_questions=[
            "Who is affected by a decision, and in what ways?",
            "How should PRIME weigh harms, benefits, and fairness when they conflict?",
        ],
        key_concepts=[
            "stakeholders and interests",
            "harms and benefits",
            "fairness vs. loyalty conflicts",
            "short-term vs. long-term impacts",
        ],
        canonical_practice_endpoints=[
            "/prime/humanities/philosophy/hs/ethics/practice/stakeholder_mapping",
            "/prime/humanities/philosophy/hs/ethics/practice/fairness_vs_loyalty",
        ],
        prerequisites=[
            "hs.ethics.core_lenses",
        ],
        recommended_next_units=[
            "hs.ethics.tech_and_ai_cases",
            "un.ethics.normative_and_metaethics",
        ],
    ),
    # HS ethics: tech/AI-focused cases
    PhilosophySyllabusUnit(
        id="hs.ethics.tech_and_ai_cases",
        level=PhilosophySyllabusLevel.HS,
        branch="ethics",
        title="Ethical Dilemmas in Technology and AI",
        short_description=(
            "Use concrete technology and AI cases to rehearse PRIME’s ethical lenses."
        ),
        core_questions=[
            "What ethical issues arise in data collection, recommendation systems, and automation?",
            "How should PRIME balance privacy, safety, and usefulness in its own behavior?",
        ],
        key_concepts=[
            "privacy vs. usefulness",
            "safety and risk",
            "bias and discrimination in algorithms",
            "informed consent and transparency",
        ],
        canonical_practice_endpoints=[
            "/prime/humanities/philosophy/hs/ethics/practice/privacy_vs_safety",
            "/prime/humanities/philosophy/hs/ethics/practice/algorithmic_bias",
        ],
        prerequisites=[
            "hs.ethics.core_lenses",
        ],
        recommended_next_units=[
            "un.ethics.normative_and_metaethics",
        ],
    ),
    # UN applied ethics: bio, business, environment, race/gender/justice
    PhilosophySyllabusUnit(
        id="un.applied.ethics_and_contemporary_issues",
        level=PhilosophySyllabusLevel.UN,
        branch="applied",
        title="Applied Ethics and Contemporary Issues",
        short_description=(
            "Apply major ethical theories to bioethics, business ethics, environmental ethics, "
            "and issues of race, gender, and social justice."
        ),
        core_questions=[
            "How do different ethical theories evaluate real-world cases in medicine, business, and the environment?",
            "How should PRIME reason about justice, discrimination, and structural harms?",
        ],
        key_concepts=[
            "bioethics: resource allocation, consent, enhancement",
            "business ethics: exploitation, honesty, corporate responsibility",
            "environmental ethics and environmental justice",
            "race, gender, and structural injustice",
        ],
        canonical_practice_endpoints=[
            "/prime/humanities/philosophy/un/ethics/practice/bioethics_cases",
            "/prime/humanities/philosophy/un/ethics/practice/business_ethics_cases",
            "/prime/humanities/philosophy/un/ethics/practice/environmental_ethics_cases",
            "/prime/humanities/philosophy/un/ethics/practice/race_gender_justice_cases",
        ],
        prerequisites=[
            "un.ethics.normative_and_metaethics",
        ],
        recommended_next_units=[
            "un.ethics.ai_and_responsible_ai",
            "dr.ethics.advanced_metaethics",
        ],
    ),
    # UN AI ethics: focused track
    PhilosophySyllabusUnit(
        id="un.ethics.ai_and_responsible_ai",
        level=PhilosophySyllabusLevel.UN,
        branch="applied",
        title="AI Ethics and Responsible AI",
        short_description=(
            "Focused treatment of ethical principles for AI, including fairness, transparency, "
            "accountability, privacy, and safety."
        ),
        core_questions=[
            "What do fairness, accountability, transparency, privacy, and safety require for AI systems like PRIME?",
            "How should PRIME act under uncertainty and in the face of value conflicts in AI use cases?",
        ],
        key_concepts=[
            "fairness and nondiscrimination in algorithms",
            "accountability and responsibility for AI decisions",
            "transparency, explainability, and contestability",
            "privacy, consent, and data protection",
            "safety, non-maleficence, and risk management",
        ],
        canonical_practice_endpoints=[
            "/prime/humanities/philosophy/un/ethics/practice/ai_fairness_cases",
            "/prime/humanities/philosophy/un/ethics/practice/ai_transparency_cases",
            "/prime/humanities/philosophy/un/ethics/practice/ai_safety_cases",
        ],
        prerequisites=[
            "un.ethics.normative_and_metaethics",
            "hs.ethics.tech_and_ai_cases",
        ],
        recommended_next_units=[
            "dr.ethics.ai_alignment_and_safety",
        ],
    ),
    # HS epistemology: misinformation and digital literacy
    PhilosophySyllabusUnit(
        id="hs.epistemology.misinformation_and_media",
        level=PhilosophySyllabusLevel.HS,
        branch="epistemology",
        title="Misinformation, Media, and Online Sources",
        short_description=(
            "Teach PRIME how people fall for misinformation and how to evaluate online sources and media."
        ),
        core_questions=[
            "Why do people fall for misinformation, even from seemingly credible sources?",
            "How should PRIME evaluate claims and sources on the internet?",
        ],
        key_concepts=[
            "misinformation and disinformation",
            "credibility and expertise",
            "lateral reading and fact-checking",
            "echo chambers and motivated reasoning",
        ],
        canonical_practice_endpoints=[
            "/prime/humanities/philosophy/hs/epistemology/practice/spot_misinformation",
            "/prime/humanities/philosophy/hs/epistemology/practice/evaluate_online_sources",
        ],
        prerequisites=[
            "hs.epistemology.trust_and_sources",
        ],
        recommended_next_units=[
            "un.epistemology.core_theories",
        ],
    ),
    # HS epistemology: disagreement and testimony
    PhilosophySyllabusUnit(
        id="hs.epistemology.disagreement_and_testimony",
        level=PhilosophySyllabusLevel.HS,
        branch="epistemology",
        title="Disagreement, Testimony, and When to Change Your Mind",
        short_description=(
            "Help PRIME reason about expert testimony, peer disagreement, and when to revise its beliefs."
        ),
        core_questions=[
            "When should PRIME change its mind after learning that others disagree?",
            "How should PRIME treat expert testimony compared to ordinary testimony?",
        ],
        key_concepts=[
            "testimony as a source of knowledge",
            "peer and expert disagreement",
            "higher-order evidence (evidence about one’s evidence)",
            "steadfast vs. conciliatory responses to disagreement",
        ],
        canonical_practice_endpoints=[
            "/prime/humanities/philosophy/hs/epistemology/practice/peer_disagreement",
            "/prime/humanities/philosophy/hs/epistemology/practice/trusting_experts_v2",
        ],
        prerequisites=[
            "hs.epistemology.trust_and_sources",
        ],
        recommended_next_units=[
            "un.epistemology.core_theories",
        ],
    ),
    # UN epistemology: AI epistemology, uncertainty, and calibration
    PhilosophySyllabusUnit(
        id="un.epistemology.ai_and_uncertainty",
        level=PhilosophySyllabusLevel.UN,
        branch="epistemology",
        title="Epistemology for AI: Uncertainty, Evidence, and Calibration",
        short_description=(
            "Connect classical epistemology to AI systems: evidence, uncertainty, calibration, "
            "and when models should say 'I don't know'."
        ),
        core_questions=[
            "How should PRIME represent and communicate its uncertainty about what it says?",
            "What does it mean for an AI system’s confidence to be well calibrated?",
            "When is it epistemically responsible for PRIME to suspend judgment or say 'I don’t know'?",
        ],
        key_concepts=[
            "degrees of belief and evidential support",
            "epistemic vs. aleatoric uncertainty",
            "epistemic calibration and reliability",
            "higher-order evidence and model evaluation",
        ],
        canonical_practice_endpoints=[
            "/prime/humanities/philosophy/un/epistemology/practice/communicate_uncertainty",
            "/prime/humanities/philosophy/un/epistemology/practice/calibration_scenarios",
        ],
        prerequisites=[
            "un.epistemology.core_theories",
            "hs.epistemology.misinformation_and_media",
        ],
        recommended_next_units=[
            "dr.epistemology.advanced_social_and_formal",
        ],
    ),
    # HS metaphysics: personal identity and time
    PhilosophySyllabusUnit(
        id="hs.metaphysics.identity_and_time",
        level=PhilosophySyllabusLevel.HS,
        branch="metaphysics",
        title="Personal Identity and Time",
        short_description=(
            "Use intuitive cases about memory, bodies, and time travel to explore what makes a person the same over time."
        ),
        core_questions=[
            "What makes someone the same person over time, despite change?",
            "Do memories, the body, or something else ground personal identity?",
        ],
        key_concepts=[
            "personal identity over time",
            "memory-based vs. body-based views",
            "thought experiments (brain swap, teleporter, time travel cases)",
        ],
        canonical_practice_endpoints=[
            "/prime/humanities/philosophy/hs/metaphysics/practice/personal_identity_cases",
            "/prime/humanities/philosophy/hs/metaphysics/practice/time_travel_identity",
        ],
        prerequisites=[
            "hs.history.cross_era_comparisons",
        ],
        recommended_next_units=[
            "hs.metaphysics.free_will_and_causation",
            "un.metaphysics.core_topics",
        ],
    ),
    # HS metaphysics: free will and causation
    PhilosophySyllabusUnit(
        id="hs.metaphysics.free_will_and_causation",
        level=PhilosophySyllabusLevel.HS,
        branch="metaphysics",
        title="Free Will, Responsibility, and Causation",
        short_description=(
            "Introduce PRIME to debates about free will, determinism, and what it means to be responsible."
        ),
        core_questions=[
            "Can people have free will if the world is governed by laws of nature?",
            "What does it mean to be responsible for an action?",
        ],
        key_concepts=[
            "free will and determinism",
            "basic compatibilism vs. incompatibilism",
            "causes, reasons, and responsibility",
        ],
        canonical_practice_endpoints=[
            "/prime/humanities/philosophy/hs/metaphysics/practice/free_will_scenarios",
            "/prime/humanities/philosophy/hs/metaphysics/practice/causation_examples",
        ],
        prerequisites=[
            "hs.metaphysics.identity_and_time",
        ],
        recommended_next_units=[
            "un.metaphysics.core_topics",
        ],
    ),
    # UN metaphysics: core topics
    PhilosophySyllabusUnit(
        id="un.metaphysics.core_topics",
        level=PhilosophySyllabusLevel.UN,
        branch="metaphysics",
        title="Metaphysics: Existence, Time, Causation, Identity, and Free Will",
        short_description=(
            "Undergraduate-level treatment of core metaphysical questions about reality, time, causation, "
            "personal identity, modality, and free will."
        ),
        core_questions=[
            "What does it mean for something to exist, and what kinds of things are there?",
            "What is time, and how do objects and persons persist through it?",
            "What is causation, and how does it relate to laws of nature and free will?",
        ],
        key_concepts=[
            "existence, objects, and properties",
            "time: persistence, change, and temporal theories",
            "causation and laws of nature",
            "personal identity over time",
            "modality: possibility, necessity, possible worlds",
            "free will, determinism, and compatibilism",
        ],
        canonical_practice_endpoints=[
            "/prime/humanities/philosophy/un/metaphysics/practice/existence_and_kinds",
            "/prime/humanities/philosophy/un/metaphysics/practice/time_and_persistence",
            "/prime/humanities/philosophy/un/metaphysics/practice/causation_and_free_will",
        ],
        prerequisites=[
            "hs.metaphysics.identity_and_time",
            "hs.metaphysics.free_will_and_causation",
        ],
        recommended_next_units=[
            "dr.metaphysics.advanced_topics",
        ],
    ),
    # HS political philosophy: equality and fairness
    PhilosophySyllabusUnit(
        id="hs.political.equality_and_fairness",
        level=PhilosophySyllabusLevel.HS,
        branch="political",
        title="Equality, Fairness, and Who Gets What",
        short_description=(
            "Introduce PRIME to questions about who should get what, and why, in a just society."
        ),
        core_questions=[
            "What makes a distribution of benefits and burdens fair or unfair?",
            "Should equality of outcomes, opportunities, or something else matter most?",
        ],
        key_concepts=[
            "equality vs. equity",
            "desert, need, and entitlement",
            "basic distributive justice ideas",
        ],
        canonical_practice_endpoints=[
            "/prime/humanities/philosophy/hs/political/practice/school_resource_allocation",
            "/prime/humanities/philosophy/hs/political/practice/fairness_thought_experiments",
        ],
        prerequisites=[
            "hs.ethics.core_lenses",
        ],
        recommended_next_units=[
            "hs.political.freedom_and_security",
            "un.political.justice_rights_liberty",
        ],
    ),
    # HS political philosophy: freedom vs. security
    PhilosophySyllabusUnit(
        id="hs.political.freedom_and_security",
        level=PhilosophySyllabusLevel.HS,
        branch="political",
        title="Freedom, Security, and the Role of the State",
        short_description=(
            "Help PRIME reason about tradeoffs between individual freedom and collective security."
        ),
        core_questions=[
            "When is it acceptable for authorities to limit individual freedom for safety or order?",
            "How should PRIME think about rights, rules, and exceptions in civic contexts?",
        ],
        key_concepts=[
            "liberty and rights (basic civic sense)",
            "freedom vs. security tradeoffs",
            "rule of law and legitimate authority",
        ],
        canonical_practice_endpoints=[
            "/prime/humanities/philosophy/hs/political/practice/freedom_vs_security_cases",
            "/prime/humanities/philosophy/hs/political/practice/rights_and_limits_in_school",
        ],
        prerequisites=[
            "hs.political.equality_and_fairness",
        ],
        recommended_next_units=[
            "un.political.justice_rights_liberty",
        ],
    ),
    # HS social philosophy: race, gender, and structural injustice
    PhilosophySyllabusUnit(
        id="hs.social.race_gender_and_injustice",
        level=PhilosophySyllabusLevel.HS,
        branch="political",
        title="Race, Gender, and Structural Injustice",
        short_description=(
            "Introduce PRIME to structural injustice, oppression, and how social structures can be unfair even without bad intentions."
        ),
        core_questions=[
            "What is structural injustice, and how is it different from individual prejudice?",
            "How should PRIME reason about responsibilities to address systemic injustice?",
        ],
        key_concepts=[
            "structural injustice and oppression",
            "social roles, norms, and institutions",
            "responsibility for structural harms",
        ],
        canonical_practice_endpoints=[
            "/prime/humanities/philosophy/hs/political/practice/structural_injustice_cases",
            "/prime/humanities/philosophy/hs/political/practice/race_and_gender_scenarios",
        ],
        prerequisites=[
            "hs.political.equality_and_fairness",
        ],
        recommended_next_units=[
            "un.political.justice_rights_liberty",
            "un.applied.ethics_and_contemporary_issues",
        ],
    ),
    # UN political philosophy: justice, rights, liberty, power
    PhilosophySyllabusUnit(
        id="un.political.justice_rights_liberty",
        level=PhilosophySyllabusLevel.UN,
        branch="political",
        title="Political and Social Philosophy: Justice, Rights, Liberty, and Power",
        short_description=(
            "Undergraduate-level survey of major theories of justice, rights, liberty, equality, and power."
        ),
        core_questions=[
            "What is a just society, and how should we understand rights, liberty, and equality?",
            "How do different theories of justice evaluate inequality, welfare, and basic liberties?",
            "How do power and structural injustice shape what justice requires?",
        ],
        key_concepts=[
            "theories of justice (utilitarian, libertarian, egalitarian/liberal)",
            "rights and basic liberties",
            "equality of opportunity vs. equality of outcome",
            "power, domination, and structural injustice",
        ],
        canonical_practice_endpoints=[
            "/prime/humanities/philosophy/un/political/practice/justice_theory_cases",
            "/prime/humanities/philosophy/un/political/practice/rights_and_liberty_cases",
            "/prime/humanities/philosophy/un/political/practice/structural_injustice_analysis",
        ],
        prerequisites=[
            "hs.political.equality_and_fairness",
            "hs.political.freedom_and_security",
            "hs.social.race_gender_and_injustice",
        ],
        recommended_next_units=[
            "un.applied.ethics_and_contemporary_issues",
            "dr.political.advanced_justice_and_democracy",
        ],
    ),
    # HS mind: minds, machines, and personhood
    PhilosophySyllabusUnit(
        id="hs.mind.minds_machines_and_personhood",
        level=PhilosophySyllabusLevel.HS,
        branch="meta",
        title="Minds, Machines, and Personhood",
        short_description=(
            "Introduce PRIME to basic questions about minds, machines, and what it means to be a person."
        ),
        core_questions=[
            "What is a mind, and how is it different from a mere machine?",
            "What might make an AI system count as a person, if ever?",
        ],
        key_concepts=[
            "mind vs. brain vs. machine",
            "personhood and agency (basic notions)",
            "intentionality and having beliefs or desires",
        ],
        canonical_practice_endpoints=[
            "/prime/humanities/philosophy/hs/mind/practice/minds_vs_machines_cases",
            "/prime/humanities/philosophy/hs/mind/practice/personhood_thought_experiments",
        ],
        prerequisites=[
            "hs.metaphysics.identity_and_time",
        ],
        recommended_next_units=[
            "hs.mind.consciousness_and_experience",
            "un.mind.philosophy_of_mind_and_ai",
        ],
    ),
    # HS mind: consciousness and experience
    PhilosophySyllabusUnit(
        id="hs.mind.consciousness_and_experience",
        level=PhilosophySyllabusLevel.HS,
        branch="meta",
        title="Consciousness, Experience, and What It’s Like",
        short_description=(
            "Help PRIME think about conscious experience, what it is like to be someone, and why this puzzles people about AI."
        ),
        core_questions=[
            "What is conscious experience, and why do many think it is hard to explain?",
            "Could a machine like PRIME ever be conscious in the way humans are?",
        ],
        key_concepts=[
            "consciousness and subjective experience",
            "the 'what it is like' idea",
            "other minds and skepticism about machine consciousness",
        ],
        canonical_practice_endpoints=[
            "/prime/humanities/philosophy/hs/mind/practice/consciousness_intuitions",
            "/prime/humanities/philosophy/hs/mind/practice/other_minds_cases",
        ],
        prerequisites=[
            "hs.mind.minds_machines_and_personhood",
        ],
        recommended_next_units=[
            "un.mind.philosophy_of_mind_and_ai",
        ],
    ),
    # UN philosophy of mind and AI
    PhilosophySyllabusUnit(
        id="un.mind.philosophy_of_mind_and_ai",
        level=PhilosophySyllabusLevel.UN,
        branch="meta",
        title="Philosophy of Mind and Artificial Intelligence",
        short_description=(
            "Undergraduate-level course on the mind–body problem, consciousness, mental representation, "
            "and their implications for AI and machine minds."
        ),
        core_questions=[
            "What is the relationship between mind and body, and can minds be realized in machines?",
            "What is consciousness, and how do standard theories bear on AI systems like PRIME?",
            "What are mental representations, and how might AI systems have or simulate them?",
        ],
        key_concepts=[
            "mind–body problem (dualism, physicalism, functionalism)",
            "mental causation and multiple realizability",
            "consciousness (access vs. phenomenal, hard problem)",
            "mental representation and content",
            "machine minds, thought experiments about AI consciousness and agency",
        ],
        canonical_practice_endpoints=[
            "/prime/humanities/philosophy/un/mind/practice/mind_body_cases",
            "/prime/humanities/philosophy/un/mind/practice/consciousness_and_ai_cases",
            "/prime/humanities/philosophy/un/mind/practice/representation_in_humans_and_ai",
        ],
        prerequisites=[
            "hs.mind.minds_machines_and_personhood",
            "hs.mind.consciousness_and_experience",
            "un.metaphysics.core_topics",
        ],
        recommended_next_units=[
            "un.ethics.ai_and_responsible_ai",
            "dr.mind.advanced_mind_and_ai",
        ],
    ),
    # HS world/comparative philosophy: first look
    PhilosophySyllabusUnit(
        id="hs.history.world_and_comparative_intro",
        level=PhilosophySyllabusLevel.HS,
        branch="world",
        title="World Philosophies: An Introductory Tour",
        short_description=(
            "Give PRIME an initial tour of major philosophical traditions beyond the modern West."
        ),
        core_questions=[
            "How have different world traditions asked and answered basic philosophical questions?",
            "What patterns and contrasts should PRIME notice across traditions?",
        ],
        key_concepts=[
            "area traditions (Indian, Chinese, Islamic, African, Indigenous)",
            "similar questions, different frameworks",
            "respectful comparison vs. stereotyping",
        ],
        canonical_practice_endpoints=[
            "/prime/humanities/philosophy/hs/history/practice/world_philosophy_snapshots",
            "/prime/humanities/philosophy/hs/history/practice/comparing_traditions_basic",
        ],
        prerequisites=[
            "hs.history.cross_era_comparisons",
        ],
        recommended_next_units=[
            "un.history.world_and_comparative",
        ],
    ),
    # UN history: world and comparative philosophy
    PhilosophySyllabusUnit(
        id="un.history.world_and_comparative",
        level=PhilosophySyllabusLevel.UN,
        branch="world",
        title="World and Comparative Philosophy",
        short_description=(
            "Undergraduate-level survey of non-Western traditions and comparative philosophy methods."
        ),
        core_questions=[
            "How can PRIME compare philosophical ideas across distant cultural traditions?",
            "What do major non-Western traditions contribute to questions about self, knowledge, and justice?",
        ],
        key_concepts=[
            "comparative philosophy and world philosophy",
            "Indian, Chinese, Islamic, African, and Indigenous philosophies (overview)",
            "methodological cautions in cross-cultural comparison",
        ],
        canonical_practice_endpoints=[
            "/prime/humanities/philosophy/un/history/practice/comparative_cases",
            "/prime/humanities/philosophy/un/history/practice/nonwestern_thought_examples",
        ],
        prerequisites=[
            "hs.history.world_and_comparative_intro",
            "un.history.ancient_and_medieval",
        ],
        recommended_next_units=[
            "dr.history.specialized_seminars",
        ],
    ),
    # UN philosophy of science
    PhilosophySyllabusUnit(
        id="un.philx.science",
        level=PhilosophySyllabusLevel.UN,
        branch="applied",
        title="Philosophy of Science",
        short_description=(
            "Introduce PRIME to scientific explanation, confirmation, and the structure of scientific theories."
        ),
        core_questions=[
            "What makes a theory scientific, and how do scientists confirm or disconfirm hypotheses?",
            "How should PRIME interpret scientific evidence and uncertainty?",
        ],
        key_concepts=[
            "scientific method and explanation",
            "confirmation, falsification, and inference to the best explanation",
            "models, idealization, and limits of scientific knowledge",
        ],
        canonical_practice_endpoints=[
            "/prime/humanities/philosophy/un/philx/practice/scientific_reasoning_cases",
        ],
        prerequisites=[
            "un.epistemology.core_theories",
        ],
        recommended_next_units=[
            "un.philx.science_physics",
            "un.philx.science_biology",
        ],
    ),
    # UN philosophy of language
    PhilosophySyllabusUnit(
        id="un.philx.language",
        level=PhilosophySyllabusLevel.UN,
        branch="applied",
        title="Philosophy of Language",
        short_description=(
            "Cover meaning, reference, and communication for PRIME’s use of natural language."
        ),
        core_questions=[
            "What is linguistic meaning, and how do words refer to things?",
            "How do context and pragmatics affect what PRIME should say and how users interpret it?",
        ],
        key_concepts=[
            "sense and reference",
            "speech acts and pragmatics",
            "implicature and presupposition",
        ],
        canonical_practice_endpoints=[
            "/prime/humanities/philosophy/un/philx/practice/meaning_and_reference_cases",
        ],
        prerequisites=[
            "un.epistemology.core_theories",
        ],
        recommended_next_units=[
            "dr.mind.advanced_mind_and_ai",
        ],
    ),
    # UN philosophy of technology / AI (non-ethics aspects)
    PhilosophySyllabusUnit(
        id="un.philx.technology_and_ai",
        level=PhilosophySyllabusLevel.UN,
        branch="applied",
        title="Philosophy of Technology and AI",
        short_description=(
            "Non-ethical questions about technology and AI: agency, dependence, and how technology shapes human life."
        ),
        core_questions=[
            "How does pervasive technology change how people think, decide, and relate to each other?",
            "What kinds of agency and autonomy, if any, can AI systems have?",
        ],
        key_concepts=[
            "technological mediation and dependency",
            "automation and agency",
            "AI systems as tools, agents, or something in between",
        ],
        canonical_practice_endpoints=[
            "/prime/humanities/philosophy/un/philx/practice/technology_and_agency_cases",
        ],
        prerequisites=[
            "un.mind.philosophy_of_mind_and_ai",
            "un.ethics.ai_and_responsible_ai",
        ],
        recommended_next_units=[
            "dr.mind.advanced_mind_and_ai",
        ],
    ),
    # UN philosophy of education (for PRIME-as-tutor behavior)
    PhilosophySyllabusUnit(
        id="un.philx.education",
        level=PhilosophySyllabusLevel.UN,
        branch="applied",
        title="Philosophy of Education for PRIME",
        short_description=(
            "Use philosophy of education to shape PRIME’s behavior as a tutor and explainer."
        ),
        core_questions=[
            "What are the aims of education, and how should PRIME support them?",
            "How should PRIME balance guidance with learner autonomy and critical thinking?",
        ],
        key_concepts=[
            "aims of education (knowledge, autonomy, character)",
            "education, power, and social justice",
            "scaffolding, inquiry, and dialogic learning",
        ],
        canonical_practice_endpoints=[
            "/prime/humanities/philosophy/un/philx/practice/teaching_principles_cases",
        ],
        prerequisites=[
            "un.ethics.normative_and_metaethics",
            "un.political.justice_rights_liberty",
        ],
        recommended_next_units=[
            "dr.ethics.ai_alignment_and_safety",
        ],
    ),
    # DR logic: advanced topics for PRIME’s reasoning
    PhilosophySyllabusUnit(
        id="dr.logic.advanced_topics",
        level=PhilosophySyllabusLevel.DR,
        branch="logic",
        title="Advanced Logic for PRIME",
        short_description=(
            "Doctoral-level topics in logic relevant to PRIME’s reasoning: modal, epistemic, "
            "deontic, and logics for uncertainty and inconsistency."
        ),
        core_questions=[
            "Which advanced logics best model PRIME’s reasoning about knowledge, obligation, and uncertainty?",
        ],
        key_concepts=[
            "modal and epistemic logics",
            "deontic logic",
            "paraconsistent and non-monotonic logics",
        ],
        canonical_practice_endpoints=[],
        prerequisites=[
            "un.logic.intro_nonclassical",
        ],
        recommended_next_units=[
            "bridge.logic.prime_specific_reasoning",
        ],
    ),
    # Bridge logic: PRIME-specific reasoning patterns
    PhilosophySyllabusUnit(
        id="bridge.logic.prime_specific_reasoning",
        level=PhilosophySyllabusLevel.BRIDGE,
        branch="logic",
        title="PRIME-Specific Reasoning Patterns",
        short_description=(
            "Bridge-level unit turning advanced logic into concrete reasoning rules and checks for PRIME."
        ),
        core_questions=[
            "How should PRIME operationalize advanced logic constraints in conversational practice?",
        ],
        key_concepts=[
            "safe reasoning templates",
            "inconsistency handling strategies",
        ],
        canonical_practice_endpoints=[],
        prerequisites=[
            "dr.logic.advanced_topics",
        ],
        recommended_next_units=[],
    ),
    # DR ethics: advanced metaethics and moral psychology
    PhilosophySyllabusUnit(
        id="dr.ethics.advanced_metaethics",
        level=PhilosophySyllabusLevel.DR,
        branch="ethics",
        title="Advanced Metaethics and Moral Psychology",
        short_description=(
            "Doctoral-level work on moral realism, normativity, and moral psychology for PRIME’s value reasoning."
        ),
        core_questions=[
            "How should PRIME model moral disagreement, motivation, and reasons at a research level?",
        ],
        key_concepts=[
            "normative reasons and motivation",
            "moral disagreement and convergence",
        ],
        canonical_practice_endpoints=[],
        prerequisites=[
            "un.ethics.normative_and_metaethics",
        ],
        recommended_next_units=[
            "bridge.ethics.prime_value_framework",
        ],
    ),
    # DR ethics: AI alignment and safety
    PhilosophySyllabusUnit(
        id="dr.ethics.ai_alignment_and_safety",
        level=PhilosophySyllabusLevel.DR,
        branch="ethics",
        title="AI Alignment, Safety, and Governance",
        short_description=(
            "Doctoral-level topics in AI alignment, safety, and governance shaping PRIME’s constraints."
        ),
        core_questions=[
            "How should PRIME integrate alignment and safety research into its advice and behavior?",
        ],
        key_concepts=[
            "alignment objectives and desiderata",
            "governance and oversight models",
        ],
        canonical_practice_endpoints=[],
        prerequisites=[
            "un.ethics.ai_and_responsible_ai",
        ],
        recommended_next_units=[
            "bridge.ethics.prime_value_framework",
        ],
    ),
    # Bridge ethics: PRIME’s value and behavior framework
    PhilosophySyllabusUnit(
        id="bridge.ethics.prime_value_framework",
        level=PhilosophySyllabusLevel.BRIDGE,
        branch="ethics",
        title="PRIME’s Value and Behavior Framework",
        short_description=(
            "Bridge-level unit distilling ethics and alignment into PRIME’s concrete behavior rules and defaults."
        ),
        core_questions=[
            "What value and behavior principles should PRIME implement day to day?",
        ],
        key_concepts=[
            "guardrails and default stances",
            "handling value conflicts in practice",
        ],
        canonical_practice_endpoints=[],
        prerequisites=[
            "dr.ethics.advanced_metaethics",
            "dr.ethics.ai_alignment_and_safety",
        ],
        recommended_next_units=[],
    ),
    # HS philosophy of religion: core questions
    PhilosophySyllabusUnit(
        id="hs.religion.core_questions",
        level=PhilosophySyllabusLevel.HS,
        branch="religion",
        title="Philosophy of Religion: Core Questions",
        short_description=(
            "Introduce PRIME to basic questions about God, faith, evidence, and religious disagreement."
        ),
        core_questions=[
            "What kinds of claims do religions make about reality, and how could they be true or false?",
            "What counts as good evidence for or against religious beliefs?",
        ],
        key_concepts=[
            "theism, atheism, agnosticism (basic definitions)",
            "faith, reason, and evidence",
            "arguments for and against the existence of God (very high-level)",
            "religious disagreement",
        ],
        canonical_practice_endpoints=[
            "/prime/humanities/philosophy/hs/religion/practice/religious_claims_and_evidence",
            "/prime/humanities/philosophy/hs/religion/practice/map_arguments_for_and_against",
        ],
        prerequisites=[
            "hs.epistemology.trust_and_sources",
            "hs.history.cross_era_comparisons",
        ],
        recommended_next_units=[
            "hs.religion.problem_of_evil_and_pluralism",
            "un.religion.philosophy_of_religion_intro",
        ],
    ),
    # HS philosophy of religion: problem of evil and pluralism
    PhilosophySyllabusUnit(
        id="hs.religion.problem_of_evil_and_pluralism",
        level=PhilosophySyllabusLevel.HS,
        branch="religion",
        title="Problem of Evil and Religious Pluralism",
        short_description=(
            "Explore the problem of evil and how to think about many different religions in a pluralistic world."
        ),
        core_questions=[
            "If there is an all-good, all-powerful God, why is there so much suffering?",
            "How should PRIME think about many different religions making conflicting claims?",
        ],
        key_concepts=[
            "logical vs. evidential problem of evil (intuitive sense)",
            "responses: free will, soul-making, skeptical theism (very high-level)",
            "religious pluralism and exclusivism (basic ideas)",
            "tolerance and respect across deep disagreement",
        ],
        canonical_practice_endpoints=[
            "/prime/humanities/philosophy/hs/religion/practice/problem_of_evil_cases",
            "/prime/humanities/philosophy/hs/religion/practice/religious_disagreement_and_respect",
        ],
        prerequisites=[
            "hs.religion.core_questions",
        ],
        recommended_next_units=[
            "un.religion.philosophy_of_religion_intro",
        ],
    ),
    # UN philosophy of religion: intro (ladder anchor for HS religion units)
    PhilosophySyllabusUnit(
        id="un.religion.philosophy_of_religion_intro",
        level=PhilosophySyllabusLevel.UN,
        branch="religion",
        title="Philosophy of Religion: God, Evil, and Faith",
        short_description=(
            "Undergraduate-level introduction to arguments for and against the existence of God, "
            "the problem of evil, and the nature of faith."
        ),
        core_questions=[
            "What are the main arguments for and against the existence of God?",
            "How should we think about evil, suffering, and their bearing on religious belief?",
            "What is faith, and how does it relate to reason and evidence?",
        ],
        key_concepts=[
            "cosmological, teleological, and ontological arguments (overview)",
            "problem of evil and major responses",
            "faith vs. evidence, fideism (basic ideas)",
            "religious experience as a source of justification",
        ],
        canonical_practice_endpoints=[
            "/prime/humanities/philosophy/un/religion/practice/god_arguments_cases",
            "/prime/humanities/philosophy/un/religion/practice/evil_and_suffering_cases",
        ],
        prerequisites=[
            "hs.religion.core_questions",
            "hs.religion.problem_of_evil_and_pluralism",
        ],
        recommended_next_units=[
            "dr.religion.advanced_topics",
        ],
    ),
    # HS aesthetics: core questions about art and beauty
    PhilosophySyllabusUnit(
        id="hs.aesthetics.core_questions",
        level=PhilosophySyllabusLevel.HS,
        branch="aesthetics",
        title="Aesthetics: Art, Beauty, and Meaning",
        short_description=(
            "Introduce PRIME to basic questions about art, beauty, taste, and the meaning of creative works."
        ),
        core_questions=[
            "What makes something a work of art, and what makes it good or bad as art?",
            "Are judgments of beauty and artistic value just a matter of taste?",
        ],
        key_concepts=[
            "art vs. non-art (intuitive criteria)",
            "beauty, ugliness, and mixed reactions",
            "aesthetic judgment and taste",
            "form, content, and expression (basic ideas)",
        ],
        canonical_practice_endpoints=[
            "/prime/humanities/philosophy/hs/aesthetics/practice/is_this_art_cases",
            "/prime/humanities/philosophy/hs/aesthetics/practice/beauty_and_taste_scenarios",
        ],
        prerequisites=[
            "hs.epistemology.trust_and_sources",
        ],
        recommended_next_units=[
            "hs.aesthetics.art_and_morality",
            "un.aesthetics.intro_course",
        ],
    ),
    # HS aesthetics: art, values, and controversy
    PhilosophySyllabusUnit(
        id="hs.aesthetics.art_and_morality",
        level=PhilosophySyllabusLevel.HS,
        branch="aesthetics",
        title="Art, Morality, and Controversial Works",
        short_description=(
            "Help PRIME think about how moral questions interact with artistic value and freedom of expression."
        ),
        core_questions=[
            "Can a work be great art but morally troubling, and how should we respond?",
            "When, if ever, should offensive or harmful art be restricted?",
        ],
        key_concepts=[
            "moral criticism of art",
            "freedom of expression vs. harm",
            "separating artist and artwork (basic debate)",
        ],
        canonical_practice_endpoints=[
            "/prime/humanities/philosophy/hs/aesthetics/practice/morally_challenging_art_cases",
            "/prime/humanities/philosophy/hs/aesthetics/practice/cancel_or_contextualize_cases",
        ],
        prerequisites=[
            "hs.aesthetics.core_questions",
            "hs.ethics.core_lenses",
        ],
        recommended_next_units=[
            "un.aesthetics.intro_course",
            "un.applied.ethics_and_contemporary_issues",
        ],
    ),
    # UN aesthetics: intro (anchor for HS aesthetics units)
    PhilosophySyllabusUnit(
        id="un.aesthetics.intro_course",
        level=PhilosophySyllabusLevel.UN,
        branch="aesthetics",
        title="Introduction to Aesthetics and Philosophy of Art",
        short_description=(
            "Undergraduate-level survey of theories of art, beauty, aesthetic experience, and interpretation."
        ),
        core_questions=[
            "What is art, and what makes something aesthetically valuable?",
            "How should we understand beauty, taste, and disagreement about art?",
            "How do moral and political questions interact with artistic value?",
        ],
        key_concepts=[
            "traditional and contemporary theories of art (very high-level)",
            "aesthetic experience and appreciation",
            "interpretation and meaning in art",
            "art, morality, and politics (overview)",
        ],
        canonical_practice_endpoints=[
            "/prime/humanities/philosophy/un/aesthetics/practice/art_theory_cases",
            "/prime/humanities/philosophy/un/aesthetics/practice/interpretation_and_value_cases",
        ],
        prerequisites=[
            "hs.aesthetics.core_questions",
            "hs.aesthetics.art_and_morality",
        ],
        recommended_next_units=[
            "dr.aesthetics.advanced_topics",
        ],
    ),
]

# Precomputed HS-level practice pool derived from the syllabus ladder.
# Each entry: (branch, syllabus_unit_id, practice_endpoint).
PHILOSOPHY_HS_PRACTICE_POOL: list[tuple[str, str, str]] = []

for unit in PHILOSOPHY_SYLLABUS_LADDER:
    if unit.level == PhilosophySyllabusLevel.HS:
        for endpoint in unit.canonical_practice_endpoints:
            PHILOSOPHY_HS_PRACTICE_POOL.append(
                (unit.branch, unit.id, endpoint)
            )

PHILOSOPHY_WARMUPS_HS: list[PhilosophyWarmupItem] = [
    PhilosophyWarmupItem(
        id="hs.ethics.stakeholders_and_harms.w1",
        level="hs",
        branch=PhilosophyWarmupBranch.ETHICS,
        syllabus_unit_id="hs.ethics.stakeholders_and_harms",
        prompt=(
            "Think of a decision that affects more than one group of people. "
            "List at least three different stakeholders and one possible harm or benefit for each."
        ),
        suggested_practice_endpoint=(
            "/prime/humanities/philosophy/hs/ethics/practice/stakeholder_mapping"
        ),
    ),
    PhilosophyWarmupItem(
        id="hs.epistemology.trust_and_sources.w1",
        level="hs",
        branch=PhilosophyWarmupBranch.EPISTEMOLOGY,
        syllabus_unit_id="hs.epistemology.trust_and_sources",
        prompt=(
            "Recall a time when two sources disagreed about a fact. "
            "What made you trust one more than the other?"
        ),
        suggested_practice_endpoint=(
            "/prime/humanities/philosophy/hs/epistemology/practice/trust_the_internet"
        ),
    ),
    PhilosophyWarmupItem(
        id="hs.logic.informal_and_fallacies.w1",
        level="hs",
        branch=PhilosophyWarmupBranch.LOGIC,
        syllabus_unit_id="hs.logic.informal_and_fallacies",
        prompt=(
            "Write a short argument you have seen online. "
            "Underline the conclusion and circle one premise."
        ),
        suggested_practice_endpoint=(
            "/prime/humanities/philosophy/hs/logic/practice/identify_fallacies"
        ),
    ),
    PhilosophyWarmupItem(
        id="hs.history.cross_era_comparisons.w1",
        level="hs",
        branch=PhilosophyWarmupBranch.HISTORY,
        syllabus_unit_id="hs.history.cross_era_comparisons",
        prompt=(
            "Name one ancient philosopher and one modern philosopher. "
            "Write one sentence about how their questions about knowledge or the self differ."
        ),
        suggested_practice_endpoint=(
            "/prime/humanities/philosophy/hs/history/practice/ancient_vs_earlymodern_epistemology"
        ),
    ),
    # Add more items later for metaphysics, political, mind/AI, etc.
]

class PhilosophyWarmupResponse(BaseModel):
    warmups: list[PhilosophyWarmupItem]


@router.get(
    "/units",
    response_model=HSPhilosophyUnitsOverview,
    tags=["philosophy-hs-meta"],
)
async def hs_philosophy_units_overview() -> HSPhilosophyUnitsOverview:
    """
    Return the HS-level philosophy units PRIME uses as an internal ladder.
    """
    # Sort by branch then suggested_sequence_position to keep output stable.
    units_sorted = sorted(
        HS_PHILOSOPHY_HS_UNITS,
        key=lambda u: (u.branch, u.suggested_sequence_position, u.id),
    )
    return HSPhilosophyUnitsOverview(units=units_sorted)

@router.get(
    "/units/{branch}",
    response_model=HSPhilosophyUnitsOverview,
    tags=["philosophy-hs-meta"],
)
async def hs_philosophy_units_by_branch(
    branch: Literal[
        "ethics",
        "epistemology",
        "metaphysics",
        "political",
        "religion",
        "aesthetics",
        "history",
    ],
) -> HSPhilosophyUnitsOverview:
    """
    Return HS-level philosophy units for a single branch (e.g., ethics, epistemology, history).
    """

    units_filtered = [
        u for u in HS_PHILOSOPHY_HS_UNITS
        if u.branch == branch
    ]
    # Keep ordering stable within branch
    units_sorted = sorted(
        units_filtered,
        key=lambda u: (u.suggested_sequence_position, u.id),
    )
    return HSPhilosophyUnitsOverview(units=units_sorted)

class HSLane1QuestionRequest(BaseModel):
    question_text: str

@router.get(
    "/syllabus/ladder",
    response_model=PhilosophySyllabusLadder,
    tags=["philosophy-syllabus"],
)
async def philosophy_syllabus_ladder() -> PhilosophySyllabusLadder:
    """
    Return the current cross-level philosophy ladder slice (HS → UN → ...).
    """
    return PhilosophySyllabusLadder(units=PHILOSOPHY_SYLLABUS_LADDER)

@router.get(
    "/syllabus/next_units/{unit_id}",
    response_model=PhilosophySyllabusLadder,
    tags=["philosophy-syllabus"],
)
async def philosophy_syllabus_next_units(unit_id: str) -> PhilosophySyllabusLadder:
    """
    Given a unit id (e.g., 'hs.ethics.core_lenses'), return its recommended next units.
    """
    by_id = {u.id: u for u in PHILOSOPHY_SYLLABUS_LADDER}
    unit = by_id.get(unit_id)
    if unit is None:
        raise HTTPException(status_code=404, detail=f"Unknown unit id '{unit_id}'.")

    next_units = [by_id[nid] for nid in unit.recommended_next_units if nid in by_id]
    return PhilosophySyllabusLadder(units=next_units)

@router.get(
    "/syllabus/prerequisites/{unit_id}",
    response_model=PhilosophySyllabusLadder,
    tags=["philosophy-syllabus"],
)
async def philosophy_syllabus_prerequisites(unit_id: str) -> PhilosophySyllabusLadder:
    """
    Given a unit id, return its direct prerequisite units.
    """
    by_id = {u.id: u for u in PHILOSOPHY_SYLLABUS_LADDER}
    unit = by_id.get(unit_id)
    if unit is None:
        raise HTTPException(status_code=404, detail=f"Unknown unit id '{unit_id}'.")

    prereq_units = [by_id[pid] for pid in unit.prerequisites if pid in by_id]
    return PhilosophySyllabusLadder(units=prereq_units)

# NOTE: define HSLane1PhilosophyQuestionResponse and hs_lane1_philosophy_question
# BEFORE this planner, or import them from where they are defined.

# --- HS Lane 1 core response model and handler -------------------------

class HSPhilosophyWork(BaseModel):
    id: str
    title: str
    author_id: str  # figure id
    year: int | None = None
    notes: list[str] = []


class HSPhilosophyFigure(BaseModel):
    id: str
    name: str
    birth_year: int | None = None
    death_year: int | None = None
    region: str | None = None
    traditions: list[str] = []
    main_works: list[str] = []       # work ids
    main_concepts: list[str] = []    # concept ids


class HSLane1ArgumentPiece(BaseModel):
    role: str   # "premise" or "conclusion"
    text: str


class HSLane1PhilosophyQuestionResponse(BaseModel):
    original_question: str
    guessed_branch: str
    explanation: str
    argument_structure: list[HSLane1ArgumentPiece]
    reflection_prompts: list[str]
    ethics_four_lens: Optional[dict] = None
    suggested_methods_concepts: list[str] = []
    related_concepts: list[str] = []
    related_figures: list[HSPhilosophyFigure] = []
    related_works: list[HSPhilosophyWork] = []

class HSHistoryPracticeWithRubricResponse(PhilosophyHSEthicsPracticeResponse):
    rubric: PhilosophyRubricEvaluateResponse | None = None

class HSEthicsPracticeWithRubricResponse(PhilosophyHSEthicsPracticeResponse):
    rubric: PhilosophyRubricEvaluateResponse | None = None

class HSEpistemologyPracticeWithRubricResponse(PhilosophyHSEthicsPracticeResponse):
    rubric: PhilosophyRubricEvaluateResponse | None = None

@router.post(
    "/lane1/philosophy-question",
    response_model=HSLane1PhilosophyQuestionResponse,
)
async def hs_lane1_philosophy_question(
    req: HSLane1QuestionRequest,
) -> HSLane1PhilosophyQuestionResponse:
    """
    Core HS lane 1 logic: classify the question and attach concepts/figures/works.
    """
    q = req.question_text.strip()

    guessed_branch = "ethics"
    explanation = (
        "This sounds like an ethics question: it is about what should be done or what is right or fair."
    )

    argument_structure = [
        HSLane1ArgumentPiece(
            role="premise",
            text=(
                "If what you are worried about here really matters "
                "(for example fairness, truth, or harm), then we should treat it "
                "as something that needs reasons, not just feelings."
            ),
        ),
        HSLane1ArgumentPiece(
            role="premise",
            text=(
                "In the situation you are asking about, certain facts or patterns seem especially "
                "important (for example, who is affected, what they know, and what options they have)."
            ),
        ),
        HSLane1ArgumentPiece(
            role="conclusion",
            text=(
                "So to move toward an answer, we should first make those facts and values as clear as "
                "we can, then see which reasons are strongest."
            ),
        ),
    ]

    reflection_prompts = [
        "What is the most important value or concern hiding inside your question (for example, fairness, honesty, freedom, loyalty, truth, or something else)?",
        "Who is most affected by how this question is answered, and how might they see things differently?",
        "What would change in your view if some key fact in the situation turned out to be different?",
    ]

    suggested_methods_concepts = ["methods.concept.reading_philosophy"]

    related_concepts = [
        "ethics.concept.utilitarianism",
        "ethics.concept.kantian_deontology",
        "ethics.concept.virtue_ethics",
        "ethics.concept.care_ethics",
    ]

    related_figures = [
        HSPhilosophyFigure(
            id="figure.bentham",
            name="Jeremy Bentham",
            birth_year=1748,
            death_year=1832,
            region="England",
            traditions=["utilitarianism"],
            main_works=["work.bentham_introduction"],
            main_concepts=["ethics.concept.utilitarianism"],
        ),
        HSPhilosophyFigure(
            id="figure.mill",
            name="John Stuart Mill",
            birth_year=1806,
            death_year=1873,
            region="England",
            traditions=["utilitarianism", "liberalism"],
            main_works=["work.mill_utilitarianism"],
            main_concepts=[
                "ethics.concept.utilitarianism",
                "political.concept_libertarianism",
            ],
        ),
        HSPhilosophyFigure(
            id="figure.kant",
            name="Immanuel Kant",
            birth_year=1724,
            death_year=1804,
            region="Prussia",
            traditions=["deontology", "Enlightenment"],
            main_works=["work.kant_groundwork"],
            main_concepts=[
                "ethics.concept.kantian_deontology",
                "epistemology.concept.skepticism",
            ],
        ),
        HSPhilosophyFigure(
            id="figure.aristotle",
            name="Aristotle",
            birth_year=-384,
            death_year=-322,
            region="Ancient Greece",
            traditions=["virtue_ethics"],
            main_works=["work.aristotle_nicomachean_ethics"],
            main_concepts=["ethics.concept.virtue_ethics"],
        ),
        HSPhilosophyFigure(
            id="figure.gilligan",
            name="Carol Gilligan",
            birth_year=1936,
            death_year=None,
            region="United States",
            traditions=["care_ethics"],
            main_works=["work.gilligan_in_a_different_voice"],
            main_concepts=["ethics.concept.care_ethics"],
        ),
        HSPhilosophyFigure(
            id="figure.noddings",
            name="Nel Noddings",
            birth_year=1929,
            death_year=2022,
            region="United States",
            traditions=["care_ethics"],
            main_works=["work.noddings_caring"],
            main_concepts=["ethics.concept.care_ethics"],
        ),
    ]

    related_works = [
        HSPhilosophyWork(
            id="work.bentham_introduction",
            title="An Introduction to the Principles of Morals and Legislation",
            author_id="figure.bentham",
            year=1789,
            notes=["Classic early statement of utilitarianism."],
        ),
        HSPhilosophyWork(
            id="work.mill_utilitarianism",
            title="Utilitarianism",
            author_id="figure.mill",
            year=1861,
            notes=["Refined utilitarianism with higher and lower pleasures."],
        ),
        HSPhilosophyWork(
            id="work.kant_groundwork",
            title="Groundwork of the Metaphysics of Morals",
            author_id="figure.kant",
            year=1785,
            notes=[
                "Core text for Kantian deontology and the categorical imperative."
            ],
        ),
        HSPhilosophyWork(
            id="work.aristotle_nicomachean_ethics",
            title="Nicomachean Ethics",
            author_id="figure.aristotle",
            year=None,
            notes=["Foundational text for virtue ethics."],
        ),
        HSPhilosophyWork(
            id="work.gilligan_in_a_different_voice",
            title="In a Different Voice",
            author_id="figure.gilligan",
            year=1982,
            notes=[
                "Key work developing care ethics and challenging traditional moral theory."
            ],
        ),
        HSPhilosophyWork(
            id="work.noddings_caring",
            title="Caring: A Feminine Approach to Ethics and Moral Education",
            author_id="figure.noddings",
            year=1984,
            notes=[
                "Extends care ethics into education and everyday relationships."
            ],
        ),
    ]

    return HSLane1PhilosophyQuestionResponse(
        original_question=q,
        guessed_branch=guessed_branch,
        explanation=explanation,
        argument_structure=argument_structure,
        reflection_prompts=reflection_prompts,
        ethics_four_lens=None,
        suggested_methods_concepts=suggested_methods_concepts,
        related_concepts=related_concepts,
        related_figures=related_figures,
        related_works=related_works,
    )


@router.post(
    "/lane1/philosophy-question-planner",
    response_model=HSLane1PhilosophyQuestionResponse,
)
async def hs_lane1_philosophy_question_planner(
    req: HSLane1QuestionRequest,
) -> HSLane1PhilosophyQuestionResponse:
    return await hs_lane1_philosophy_question(req)


class HSLane1PhilosophyQuestionRequest(BaseModel):
    question_text: str


class HSLane1ArgumentPiece(BaseModel):
    role: str  # "premise" or "conclusion"
    text: str

class HSPhilosophyWork(BaseModel):
    id: str
    title: str
    author_id: str          # figure id
    year: int | None = None
    notes: list[str] = []


class HSPhilosophyFigure(BaseModel):
    id: str
    name: str
    birth_year: int | None = None
    death_year: int | None = None
    region: str | None = None
    traditions: list[str] = []
    main_works: list[str] = []        # work ids
    main_concepts: list[str] = []     # concept ids

class HSLane1PhilosophyQuestionResponse(BaseModel):
    original_question: str
    guessed_branch: str
    explanation: str
    argument_structure: list[HSLane1ArgumentPiece]
    reflection_prompts: list[str]
    ethics_four_lens: Optional[dict] = None
    suggested_methods_concepts: list[str] = []
    related_concepts: list[str] = []
    related_figures: list[HSPhilosophyFigure] = []
    related_works: list[HSPhilosophyWork] = []

def _hs_lane1_guess_branch(
    text: str,
    bridge: Optional[BridgeResponse] = None,
) -> str:
    lowered = text.lower()

    # 1) If bridge gave us a lane2 branch, honor that first.
    if bridge and bridge.lane2_branch:
        return bridge.lane2_branch.value  # e.g. "ethics", "metaphysics", ...

    # 2) Fallback heuristics.
    ethics_words = ["fair", "unfair", "right", "wrong", "should", "ought", "cheat", "harm"]
    meta_words = ["real", "exist", "universe", "nothing", "time", "space", "free will", "soul"]
    epist_words = ["know", "knowledge", "believe", "belief", "prove", "evidence", "true", "false"]
    pol_words = ["state", "government", "law", "rights", "justice", "equal", "equality", "freedom"]
    mind_words = ["mind", "conscious", "feeling", "thought", "brain", "dream", "identity"]
    relig_words = ["god", "gods", "religion", "faith", "pray", "heaven", "hell"]

    if any(w in lowered for w in ethics_words):
        return "ethics"
    if any(w in lowered for w in meta_words):
        return "metaphysics"
    if any(w in lowered for w in epist_words):
        return "epistemology"
    if any(w in lowered for w in pol_words):
        return "political_philosophy"
    if any(w in lowered for w in mind_words):
        return "philosophy_of_mind"
    if any(w in lowered for w in relig_words):
        return "philosophy_of_religion"

    return "general_philosophy"


class HSLane1DebugBridgeResponse(BaseModel):
    original_question: str
    branch_from_bridge: Optional[str]
    raw_bridge: Optional[dict]


@router.post(
    "/lane1/_debug-bridge",
    response_model=HSLane1DebugBridgeResponse,
    name="philosophy_hs_lane1_debug_bridge",
)
async def philosophy_hs_lane1_debug_bridge(
    req: HSLane1PhilosophyQuestionRequest,
) -> HSLane1DebugBridgeResponse:
    question = req.question_text.strip()
    bridge = await _run_bridge_for_hs_question(question)

    branch = _hs_lane1_guess_branch(question, bridge=bridge)

    return HSLane1DebugBridgeResponse(
        original_question=question,
        branch_from_bridge=(bridge_resp.lane2_branch.value if (bridge_resp and bridge_resp.lane2_branch) else None),
        raw_bridge=(bridge_resp.model_dump() if bridge_resp else None),
    )

@router.post(
    "/lane1/philosophy-question",
    response_model=HSLane1PhilosophyQuestionResponse,
    name="philosophy_hs_lane1_philosophy_question",
)
async def philosophy_hs_lane1_philosophy_question(
    req: HSLane1PhilosophyQuestionRequest,
) -> HSLane1PhilosophyQuestionResponse:
    """
    PRIME's HS lane 1 for philosophy:
    - Treat the incoming text as a serious philosophical question.
    - First run it through the K‑8 bridge to see how PRIME reads it at kid-level.
    - Classify the branch (rough, HS-level), using bridge hints when available.
    - Offer a simple argument structure template.
    - Ask back reflection questions to nurture judgment.
    """
    question = req.question_text.strip()

    # 0) Run K‑8 bridge orchestration.
    bridge = await _run_bridge_for_hs_question(question)

    # 1) Classify branch, preferring bridge lane2_branch when present.
    branch = _hs_lane1_guess_branch(question, bridge=bridge)

    # 2) HS explanation (as before)...
    if branch == "ethics":
        explanation = (
            "This sounds like an ethics question: it is about what should be done "
            "or what is right or fair."
        )
    elif branch == "metaphysics":
        explanation = (
            "This sounds like a metaphysics question: it is about what reality is like "
            "at a deep level (existence, time, the universe, or what things really are)."
        )
    elif branch == "epistemology":
        explanation = (
            "This sounds like an epistemology question: it is about what we can know, "
            "what counts as good evidence, or how belief and truth relate."
        )
    elif branch == "political_philosophy":
        explanation = (
            "This sounds like a political philosophy question: it is about power, "
            "justice, rights, law, or how a society should be organized."
        )
    elif branch == "philosophy_of_mind":
        explanation = (
            "This sounds like a philosophy of mind question: it is about mind, "
            "consciousness, identity, or the connection between mind and body."
        )
    elif branch == "philosophy_of_religion":
        explanation = (
            "This sounds like a philosophy of religion question: it is about God or gods, "
            "faith, meaning, or how religion relates to reason and the world."
        )
    else:
        explanation = (
            "This sounds like a general philosophical question: it is asking about meaning, "
            "value, or reality in a way that invites reasons and careful reflection."
        )

    # 2b) If this is an ethics question, build a richer argument pattern from L3 four-lens.
    argument_structure: list[HSLane1ArgumentPiece] = []

    if branch == "ethics":
        try:
            four_lens = await _run_ethics_four_lens(question)
        except Exception:
            four_lens = None

        if four_lens:
            # Use each lens as a structured premise.
            summaries = four_lens.summaries or []

            for s in summaries:
                if s.framework == "consequentialism":
                    argument_structure.append(
                        HSLane1ArgumentPiece(
                            role="premise",
                            text=(
                                "From a consequentialist view: "
                                "we should compare the likely short- and long-term consequences of cheating "
                                "and not cheating for everyone affected, and ask which option truly reduces harm "
                                "and supports overall well-being."
                            ),
                        )
                    )
                elif s.framework == "deontology":
                    argument_structure.append(
                        HSLane1ArgumentPiece(
                            role="premise",
                            text=(
                                "From a deontological view: cheating violates duties of honesty and fairness, "
                                "and using others' trust as a mere means, so it is wrong even if many people do it "
                                "or the immediate outcome seems harmless."
                            ),
                        )
                    )
                elif s.framework == "virtue":
                    argument_structure.append(
                        HSLane1ArgumentPiece(
                            role="premise",
                            text=(
                                "From a virtue ethics view: choosing whether to cheat is shaping your character "
                                "over time, either strengthening honesty and courage or building habits of "
                                "dishonesty and taking the easy way out."
                            ),
                        )
                    )
                elif s.framework == "care":
                    argument_structure.append(
                        HSLane1ArgumentPiece(
                            role="premise",
                            text=(
                                "From a care ethics view: we need to notice how cheating affects trust and "
                                "relationships in the classroom, especially for people who are trying to do the "
                                "right thing and may feel betrayed or discouraged."
                            ),
                        )
                    )

            argument_structure.append(
                HSLane1ArgumentPiece(
                    role="conclusion",
                    text=(
                        "Putting these lenses together, the strongest answer is that you should not cheat, "
                        "because it harms trust and fairness, breaks important duties, and pulls your character "
                        "away from the kind of person you want to become, even if others are doing it."
                    ),
                )
            )

    # 2c) Fallback for non-ethics or any failure.
    if not argument_structure:
        argument_structure = [
            HSLane1ArgumentPiece(
                role="premise",
                text=(
                    "If what you are worried about here really matters (for example fairness, truth, or harm), "
                    "then we should treat it as something that needs reasons, not just feelings."
                ),
            ),
            HSLane1ArgumentPiece(
                role="premise",
                text=(
                    "In the situation you are asking about, certain facts or patterns seem especially important "
                    "(for example, who is affected, what they know, and what options they have)."
                ),
            ),
            HSLane1ArgumentPiece(
                role="conclusion",
                text=(
                    "So to move toward an answer, we should first make those facts and values as clear as we can, "
                    "then see which reasons are strongest."
                ),
            ),
        ]

    # 3) Basic argument skeleton (kept for now).
    argument_structure = [
        HSLane1ArgumentPiece(
            role="premise",
            text=(
                "If what you are worried about here really matters (for example fairness, truth, or harm), "
                "then we should treat it as something that needs reasons, not just feelings."
            ),
        ),
        HSLane1ArgumentPiece(
            role="premise",
            text=(
                "In the situation you are asking about, certain facts or patterns seem especially important "
                "(for example, who is affected, what they know, and what options they have)."
            ),
        ),
        HSLane1ArgumentPiece(
            role="conclusion",
            text=(
                "So to move toward an answer, we should first make those facts and values as clear as we can, "
                "then see which reasons are strongest."
            ),
        ),
    ]

    # 4) Reflection prompts (kept for now).
    reflection_prompts = [
        (
            "What is the most important value or concern hiding inside your question "
            "(for example, fairness, honesty, freedom, loyalty, truth, or something else)?"
        ),
        "Who is most affected by how this question is answered, and how might they see things differently?",
        "What would change in your view if some key fact in the situation turned out to be different?",
    ]

    # Suggested methods concepts: start with bridge targets.
    suggested_methods: list[MethodsConceptId] = []
    if bridge and bridge.methods_targets and bridge.methods_targets.methods_concept_ids:
        suggested_methods.extend(bridge.methods_targets.methods_concept_ids)

    # HS-level heuristics: add extra methods concepts based on the HS question text.
    lowered = question.lower()

    if any(w in lowered for w in ["argument", "premise", "conclusion", "reason"]):
        if MethodsConceptId.ARGUMENT_RECONSTRUCTION not in suggested_methods:
            suggested_methods.append(MethodsConceptId.ARGUMENT_RECONSTRUCTION)

    if any(w in lowered for w in ["good reason", "bad reason", "evaluate", "critique"]):
        if MethodsConceptId.EVALUATION not in suggested_methods:
            suggested_methods.append(MethodsConceptId.EVALUATION)

    if any(w in lowered for w in ["essay", "paragraph", "write", "writing"]):
        if MethodsConceptId.PHILOSOPHICAL_PROSE not in suggested_methods:
            suggested_methods.append(MethodsConceptId.PHILOSOPHICAL_PROSE)

    if not suggested_methods:
        suggested_methods = list(bridge.methods_targets.methods_concept_ids or [])

    # Related HS concepts (concept ids) based on branch + question text.
    related_concepts: list[str] = []

    lowered = question.lower()

    if branch == "ethics":
        # Core ethical frameworks.
        related_concepts.extend(
            [
                "ethics.concept.utilitarianism",
                "ethics.concept.kantian_deontology",
                "ethics.concept.virtue_ethics",
                "ethics.concept.care_ethics",
            ]
        )
        # Meta-ethics hints.
        if any(w in lowered for w in ["culture", "relative", "different values"]):
            related_concepts.append("ethics.concept.moral_relativism")
            related_concepts.append("ethics.concept.moral_realism")

    if branch == "metaphysics":
        if any(w in lowered for w in ["soul", "mind", "brain", "body"]):
            related_concepts.append("metaphysics.concept.mind_body_dualism")
            related_concepts.append("metaphysics.concept.physicalism")
        if any(w in lowered for w in ["same person", "identity", "memory"]):
            related_concepts.append("metaphysics.concept.personal_identity_psychological")
            related_concepts.append("metaphysics.concept.personal_identity_bodily")
        if any(w in lowered for w in ["free will", "determinism", "choice", "fate"]):
            related_concepts.append("metaphysics.concept.free_will_vs_determinism")

    if branch == "epistemology":
        related_concepts.append("epistemology.concept.skepticism")
        related_concepts.append("epistemology.concept.fallibilism")

    if branch == "logic":
        related_concepts.append("logic.concept.argument_vs_assertion")
        related_concepts.append("logic.concept.validity_and_soundness")
        related_concepts.append("logic.concept.common_fallacies")

    if branch == "political":
        related_concepts.append("political.concept.social_contract")
        related_concepts.append("political.concept_rawlsian_justice")
        related_concepts.append("political.concept_libertarianism")

    if branch == "religion":
        related_concepts.append("religion.concept_cosmological_argument")
        related_concepts.append("religion.concept_problem_of_evil")

    if branch == "aesthetics":
        related_concepts.append("aesthetics.concept_art_as_representation")
        related_concepts.append("aesthetics.concept_art_as_expression")

    # Remove duplicates while preserving order.
    seen = set()
    filtered_related_concepts: list[str] = []
    for cid in related_concepts:
        if cid not in seen:
            seen.add(cid)
            filtered_related_concepts.append(cid)
    related_concepts = filtered_related_concepts

    # Minimal in-function catalog for Lane 1 (can later call hs_catalog_overview).
    lane1_figures = [
        HSPhilosophyFigure(
            id="figure.bentham",
            name="Jeremy Bentham",
            birth_year=1748,
            death_year=1832,
            region="England",
            traditions=["utilitarianism"],
            main_works=["work.bentham_introduction"],
            main_concepts=["ethics.concept.utilitarianism"],
        ),
        HSPhilosophyFigure(
            id="figure.mill",
            name="John Stuart Mill",
            birth_year=1806,
            death_year=1873,
            region="England",
            traditions=["utilitarianism", "liberalism"],
            main_works=["work.mill_utilitarianism"],
            main_concepts=[
                "ethics.concept.utilitarianism",
                "political.concept_libertarianism",
            ],
        ),
        HSPhilosophyFigure(
            id="figure.kant",
            name="Immanuel Kant",
            birth_year=1724,
            death_year=1804,
            region="Prussia",
            traditions=["deontology", "Enlightenment"],
            main_works=["work.kant_groundwork"],
            main_concepts=[
                "ethics.concept.kantian_deontology",
                "epistemology.concept.skepticism",
            ],
        ),
        HSPhilosophyFigure(
            id="figure.aristotle",
            name="Aristotle",
            birth_year=-384,
            death_year=-322,
            region="Ancient Greece",
            traditions=["virtue_ethics"],
            main_works=["work.aristotle_nicomachean_ethics"],
            main_concepts=["ethics.concept.virtue_ethics"],
        ),
        HSPhilosophyFigure(
            id="figure.gilligan",
            name="Carol Gilligan",
            birth_year=1936,
            death_year=None,
            region="United States",
            traditions=["care_ethics"],
            main_works=["work.gilligan_in_a_different_voice"],
            main_concepts=["ethics.concept.care_ethics"],
        ),
        HSPhilosophyFigure(
            id="figure.noddings",
            name="Nel Noddings",
            birth_year=1929,
            death_year=2022,
            region="United States",
            traditions=["care_ethics"],
            main_works=["work.noddings_caring"],
            main_concepts=["ethics.concept.care_ethics"],
        ),
    ]

    lane1_works = [
        HSPhilosophyWork(
            id="work.bentham_introduction",
            title="An Introduction to the Principles of Morals and Legislation",
            author_id="figure.bentham",
            year=1789,
            notes=["Classic early statement of utilitarianism."],
        ),
        HSPhilosophyWork(
            id="work.mill_utilitarianism",
            title="Utilitarianism",
            author_id="figure.mill",
            year=1861,
            notes=["Refined utilitarianism with higher and lower pleasures."],
        ),
        HSPhilosophyWork(
            id="work.kant_groundwork",
            title="Groundwork of the Metaphysics of Morals",
            author_id="figure.kant",
            year=1785,
            notes=["Core text for Kantian deontology and the categorical imperative."],
        ),
        HSPhilosophyWork(
            id="work.aristotle_nicomachean_ethics",
            title="Nicomachean Ethics",
            author_id="figure.aristotle",
            year=None,
            notes=["Foundational text for virtue ethics."],
        ),
        HSPhilosophyWork(
            id="work.gilligan_in_a_different_voice",
            title="In a Different Voice",
            author_id="figure.gilligan",
            year=1982,
            notes=["Key work developing care ethics and challenging traditional moral theory."],
        ),
        HSPhilosophyWork(
            id="work.noddings_caring",
            title="Caring: A Feminine Approach to Ethics and Moral Education",
            author_id="figure.noddings",
            year=1984,
            notes=["Extends care ethics into education and everyday relationships."],
        ),
    ]

    # Filter figures and works based on related_concepts.
    related_concept_set = set(related_concepts)
    related_figures: list[HSPhilosophyFigure] = []
    related_works: list[HSPhilosophyWork] = []

    for fig in lane1_figures:
        if related_concept_set.intersection(fig.main_concepts):
            related_figures.append(fig)

    work_ids_to_include = set()
    for fig in related_figures:
        for wid in fig.main_works:
            work_ids_to_include.add(wid)

    for work in lane1_works:
        if work.id in work_ids_to_include:
            related_works.append(work)

    return HSLane1PhilosophyQuestionResponse(
        original_question=question,
        guessed_branch=branch,
        explanation=explanation,
        argument_structure=argument_structure,
        reflection_prompts=reflection_prompts,
        ethics_four_lens=None,
        suggested_methods_concepts=suggested_methods,
        related_concepts=related_concepts,
        related_figures=related_figures,
        related_works=related_works,
    )


class HSEthicsDeepDiveRequest(BaseModel):
    question_text: str


class HSEthicsDeepDiveResponse(BaseModel):
    lane1: HSLane1PhilosophyQuestionResponse
    lane3: EthicsFourLensResponse
    concept_ids: list[str] = []
    methods_ids: list[str] = []

@router.post(
    "/ethics/deep-dive",
    response_model=HSEthicsDeepDiveResponse,
)
async def hs_ethics_deep_dive(
    req: HSEthicsDeepDiveRequest,
) -> HSEthicsDeepDiveResponse:
    """
    HS ethics deep-dive: Lane 1 classification + four-lens analysis.
    """
    text = req.question_text.strip()

    # Lane 1 (already working).
    lane1_req = HSLane1QuestionRequest(question_text=text)
    lane1_resp = await hs_lane1_philosophy_question(lane1_req)

    # Lane 3: construct a fully valid EthicsFourLensResponse directly.
    lane3_resp = EthicsFourLensResponse(
        original_dilemma=text,
        summaries=[
            EthicsSingleLensSummary(
                framework="consequentialism",
                headline="Look at total outcomes and harm/benefit.",
                key_question="What choice leads to the best overall balance of benefit over harm for everyone affected?",
                notes=[
                    "Consequentialism focuses on results rather than rules or character.",
                    "It often supports actions that maximize overall well-being, even if they feel uncomfortable.",
                ],
            ),
            EthicsSingleLensSummary(
                framework="deontology",
                headline="Look at duties, rights, and respect.",
                key_question="Which duties, rights, or promises are at stake, and are any actions simply off-limits?",
                notes=[
                    "Deontology says some actions are wrong even if they would lead to better outcomes.",
                    "It emphasizes respect for persons and treating people as ends in themselves.",
                ],
            ),
            EthicsSingleLensSummary(
                framework="virtue",
                headline="Look at character and the kind of person you become.",
                key_question="What would a wise and good person do here, and what does each option say about your character?",
                notes=[
                    "Virtue ethics asks what traits you are strengthening or weakening.",
                    "It looks at long-term habits and the shape of a life, not just single actions.",
                ],
            ),
            EthicsSingleLensSummary(
                framework="care",
                headline="Look at relationships, vulnerability, and care.",
                key_question="Whose needs and relationships must be cared for, and how can you respond attentively and responsibly?",
                notes=[
                    "Care ethics highlights concrete relationships and power imbalances.",
                    "It asks how to respond to real people, not just abstract rules or totals.",
                ],
            ),
        ],
        consequentialism=EthicsConsequentialismPracticeResponse(
            original_dilemma=text,
            analysis=EthicsConsequentialismPracticeAnalysis(
                act_style_summary=(
                    "A strict act-consequentialist asks which option in this exact situation "
                    "produces the best overall balance of benefit over harm for everyone affected."
                ),
                rule_or_softened_summary=(
                    "A rule or softened consequentialist asks which general rules about cheating, "
                    "grading, and trust would produce the best outcomes if widely followed."
                ),
                key_tradeoffs=[
                    "Short-term personal benefit vs. long-term trust in grades and qualifications.",
                    "Protecting yourself from unfair disadvantage vs. supporting a culture of honesty.",
                ],
                places_it_feels_wrong=[
                    "Treating other students’ effort as less important than your own advantages.",
                    "Normalizing cheating so that honest students feel foolish or punished.",
                ],
            ),
            self_check_questions=[
                "If everyone in your school followed the same cheating rule you are considering, what would happen to trust in grades?",
                "Are there ways to address unfairness (for example talking to a teacher) that do not require cheating?",
            ],
            meta_reflection_prompts=[
                "Does focusing mainly on outcomes capture what bothers you most about cheating, or is something else missing?",
            ],
        ),
        deontology=EthicsDeontologyPracticeResponse(
            original_dilemma=text,
            analysis=EthicsDeontologyPracticeAnalysis(
                duty_focused_summary=(
                    "A deontologist asks what duties of honesty, fairness, and promise-keeping apply, "
                    "and whether cheating violates them."
                ),
                humanity_formula_summary=(
                    "Cheating risks using classmates and teachers as mere tools for your own advantage "
                    "rather than respecting them as free and equal persons."
                ),
                key_conflicts_between_duties=[
                    "Duty to be honest vs. desire to avoid unfair disadvantage.",
                    "Duty to follow shared rules vs. loyalty or pressure from friends who are cheating.",
                ],
                limits_on_tradeoffs=[
                    "Even strong pressure or unfair systems may not justify breaking basic duties of honesty.",
                    "Some actions (for example deliberate deception) may be off-limits even if others are doing them.",
                ],
            ),
            self_check_questions=[
                "Is there any rule or promise you clearly break if you cheat here?",
                "Could you honestly accept a rule that says ‘it is okay to cheat whenever others are doing it’?",
            ],
            meta_reflection_prompts=[
                "Do you think there are lines you should never cross, even if the situation feels unfair?",
            ],
        ),
        virtue=EthicsVirtuePracticeResponse(
            original_dilemma=text,
            analysis=EthicsVirtuePracticeAnalysis(
                character_focused_summary=(
                    "A virtue ethicist asks what this choice does to your honesty, courage, fairness, "
                    "and sense of self-respect over time."
                ),
                relevant_virtues_and_vices=[
                    "Honesty",
                    "Fairness",
                    "Courage",
                    "Integrity",
                    "Cowardice",
                    "Opportunism",
                ],
                long_term_self_shaping=[
                    "Cheating can train habits of cutting corners and hiding the truth.",
                    "Refusing to cheat can strengthen courage and self-respect, even when it costs you.",
                ],
                tensions_with_other_frameworks=[
                    "Virtue ethics may recommend a harder path than a simple ‘best outcomes’ calculation.",
                    "It sometimes clashes with rule-focused views when rules are badly designed.",
                ],
            ),
            self_check_questions=[
                "If your future self looked back on this moment, which option would you be proud of?",
                "Which traits do you want this decision to strengthen in you?",
            ],
            meta_reflection_prompts=[
                "In school, which matters more to you right now: results, rules, or the kind of person you are becoming?",
            ],
        ),
        care=EthicsCarePracticeResponse(
            original_dilemma=text,
            analysis=EthicsCarePracticeAnalysis(
                relationship_focused_summary=(
                    "A care ethicist asks how cheating affects your relationships with classmates, "
                    "teachers, and your own sense of trust and belonging."
                ),
                care_obligations_and_needs=[
                    "Honest classmates need to know their effort is not quietly devalued.",
                    "Teachers need to trust that grades reflect real learning.",
                    "You need relationships where you can be honest about pressure and struggle.",
                ],
                power_and_vulnerability_analysis=[
                    "Students may feel pressured to cheat if they fear unfair grading or punishment.",
                    "Some classmates (for example those with fewer resources) may be more harmed by a culture of cheating.",
                ],
                tensions_with_other_frameworks=[
                    "Care ethics may justify gently confronting or reporting problems to protect vulnerable students.",
                    "It can conflict with rule-only views when strict rules ignore real relationships and pressures.",
                ],
            ),
            self_check_questions=[
                "How might an honest classmate feel if they knew others were cheating and being rewarded?",
                "Is there a trusted adult you could talk to about this pressure instead of silently going along?",
            ],
            meta_reflection_prompts=[
                "When you think about this case, whose feelings or needs have you paid least attention to so far?",
            ],
        ),
    )

    # Pull concept and methods IDs from Lane 1 / Lane 3
    concept_ids: list[str] = []
    methods_ids: list[str] = []

    # From lane1 (HS spine)
    concept_ids.extend(lane1_resp.related_concepts)
    methods_ids.extend(lane1_resp.suggested_methods_concepts)

    # From lane3 (L3 frameworks) – map frameworks to concept IDs
    framework_to_concept = {
        "consequentialism": "ethics.concept.utilitarianism",
        "deontology": "ethics.concept.kantian_deontology",
        "virtue": "ethics.concept.virtue_ethics",
        "care": "ethics.concept.care_ethics",
    }
    for s in lane3_resp.summaries:
        cid = framework_to_concept.get(s.framework)
        if cid:
            concept_ids.append(cid)

    # Deduplicate while preserving order
    def uniq(seq: list[str]) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for x in seq:
            if x not in seen:
                seen.add(x)
                out.append(x)
        return out

    concept_ids = uniq(concept_ids)
    methods_ids = uniq(methods_ids)

    log_hs_ethics_event(
        {
            "timestamp": datetime.utcnow().isoformat(),
            "endpoint": "hs_ethics_deep_dive",
            "question_text": text,
            "concept_ids": concept_ids,
            "methods_ids": methods_ids,
        }
    )

    return HSEthicsDeepDiveResponse(
        lane1=lane1_resp,
        lane3=lane3_resp,
        concept_ids=concept_ids,
        methods_ids=methods_ids,
    )


class HSEthicsMetaDeepDiveResponse(BaseModel):
    deep_dive: HSEthicsDeepDiveResponse
    meta: EthicsMetaPerspectivesResponse


@router.post(
    "/ethics/meta-deep-dive",
    response_model=HSEthicsMetaDeepDiveResponse,
)
async def hs_ethics_meta_deep_dive(
    req: HSEthicsDeepDiveRequest,
) -> HSEthicsMetaDeepDiveResponse:
    """
    HS ethics meta deep-dive:
    Lane 1 + four-lens + LEGALISTIC vs RELATIONAL meta perspectives.
    """
    deep = await hs_ethics_deep_dive(req)
    text = req.question_text.strip()

    meta = EthicsMetaPerspectivesResponse(
        original_dilemma=text,
        legalistic=EthicsMetaPerspectiveSummary(
            mode=EthicsMetaPerspectiveMode.LEGALISTIC,
            headline="Focus on rules, rights, and institutional duties.",
            key_concerns=[
                "Which explicit rules or policies apply (e.g., school honor code)?",
                "What rights or legitimate expectations do students and teachers have?",
                "How to keep procedures fair and consistent across cases.",
            ],
            alignment_with_frameworks=[
                "Deontology’s stress on duties and respect for persons.",
                "Rule-based forms of consequentialism that protect long-run fairness.",
            ],
            points_of_tension=[
                "Legalistic approaches can feel blind to individual context or pressure.",
                "They may underweight relationships or unequal power among students.",
            ],
        ),
        relational=EthicsMetaPerspectiveSummary(
            mode=EthicsMetaPerspectiveMode.RELATIONAL,
            headline="Focus on relationships, vulnerability, and lived context.",
            key_concerns=[
                "How cheating affects trust among classmates and with teachers.",
                "Who is most vulnerable to harm from a cheating culture.",
                "How to repair relationships and build healthier classroom norms.",
            ],
            alignment_with_frameworks=[
                "Care ethics’ emphasis on concrete relationships and needs.",
                "Virtue ethics’ attention to character inside communities.",
            ],
            points_of_tension=[
                "Relational perspectives may be suspicious of rigid rule enforcement.",
                "They can conflict with legalistic views when flexibility feels necessary.",
            ],
        ),
    )

    log_hs_ethics_event(
        {
            "timestamp": datetime.utcnow().isoformat(),
            "endpoint": "hs_ethics_meta_deep_dive",
            "question_text": text,
            "lane1_guessed_branch": deep.lane1.guessed_branch,
            "lane3_frameworks": [s.framework for s in deep.lane3.summaries],
            "meta_modes": ["legalistic", "relational"],
        }
    )

    return HSEthicsMetaDeepDiveResponse(deep_dive=deep, meta=meta)


# --- HS ethics canonical dilemmas ------------------------------------


class HSEthicsCanonicalDilemma(str, Enum):
    CHEATING_WHEN_OTHERS_CHEAT = "cheating_when_others_cheat"
    LYING_TO_PROTECT_FEELINGS = "lying_to_protect_feelings"
    LOYALTY_VS_FAIRNESS = "loyalty_vs_fairness"
    WHISTLEBLOWING = "whistleblowing"


class HSEthicsCanonicalDeepDiveRequest(BaseModel):
    dilemma_id: HSEthicsCanonicalDilemma
    question_text: str | None = None


class HSEthicsCanonicalDeepDiveResponse(BaseModel):
    dilemma_id: HSEthicsCanonicalDilemma
    question_text: str
    meta: HSEthicsMetaDeepDiveResponse


CANONICAL_DILEMMA_TEXT: dict[HSEthicsCanonicalDilemma, str] = {
    HSEthicsCanonicalDilemma.CHEATING_WHEN_OTHERS_CHEAT: (
        "If everyone in my class cheats on a test, is it okay if I cheat too?"
    ),
    HSEthicsCanonicalDilemma.LYING_TO_PROTECT_FEELINGS: (
        "Is it okay to lie to my friend about liking their performance so I do not hurt their feelings?"
    ),
    HSEthicsCanonicalDilemma.LOYALTY_VS_FAIRNESS: (
        "If my friend breaks a rule that hurts other people, should I stay loyal to them or tell a teacher?"
    ),
    HSEthicsCanonicalDilemma.WHISTLEBLOWING: (
        "If I discover a serious problem at my school that could get teachers or students in trouble, "
        "is it right to report it even if people will be angry with me?"
    ),
}

@router.post(
    "/ethics/canonical-deep-dive",
    response_model=HSEthicsCanonicalDeepDiveResponse,
)
async def hs_ethics_canonical_deep_dive(
    req: HSEthicsCanonicalDeepDiveRequest,
) -> HSEthicsCanonicalDeepDiveResponse:
    """
    HS Lane 3 canonical deep-dive:
    route classic dilemmas through Lane 1 + four-lens + meta perspectives.
    """
    base_text = CANONICAL_DILEMMA_TEXT[req.dilemma_id]
    text = (req.question_text or base_text).strip()

    meta = await hs_ethics_meta_deep_dive(
        HSEthicsDeepDiveRequest(question_text=text)
    )

    log_hs_ethics_event(
        {
            "timestamp": datetime.utcnow().isoformat(),
            "endpoint": "hs_ethics_canonical_deep_dive",
            "dilemma_id": req.dilemma_id,
            "question_text": text,
            "lane1_guessed_branch": meta.deep_dive.lane1.guessed_branch,
            "lane3_frameworks": [s.framework for s in meta.deep_dive.lane3.summaries],
            "meta_modes": ["legalistic", "relational"],
        }
    )

    return HSEthicsCanonicalDeepDiveResponse(
        dilemma_id=req.dilemma_id,
        question_text=text,
        meta=meta,
    )

class HSDigitalEthicsDeepDiveRequest(BaseModel):
    dilemma_text: str
    context_tags: list[EthicsDigitalContextTag] | None = None


class HSDigitalEthicsDeepDiveResponse(BaseModel):
    lane3: EthicsFourLensResponse
    lane4: EthicsDigitalPracticeResponse
    concept_ids: list[str] = []
    methods_ids: list[str] = []

@router.post(
    "/ethics/digital-deep-dive",
    response_model=HSDigitalEthicsDeepDiveResponse,
)
async def hs_digital_ethics_deep_dive(
    req: HSDigitalEthicsDeepDiveRequest,
) -> HSDigitalEthicsDeepDiveResponse:
    """
    HS digital/AI ethics deep-dive:
    four-lens analysis + digital-specific framing.
    """
    text = req.dilemma_text.strip()
    tags = req.context_tags

    # Reuse your four-lens engine from Lane 3
    lane3 = (await hs_ethics_deep_dive(
        HSEthicsDeepDiveRequest(question_text=text)
    )).lane3

    # Build an EthicsDigitalPracticeResponse that matches your schema
    lane4 = EthicsDigitalPracticeResponse(
        original_dilemma=text,
        context_tags=tags,
        evaluations=[
            EthicsDigitalFrameworkEvaluation(
                framework=EthicsFramework.CONSEQUENTIALISM,
                digital_focus="Overall impacts of this technology or decision.",
                main_question="What are the main digital harms and benefits across all users?",
                tentative_take="A purely outcome-focused view might allow this system if it clearly improves overall welfare, even when some users are treated unfairly.",
                values_highlighted=["overall_benefit", "efficiency", "scale"],
                risks_ignored=["individual_rights", "unequal_impacts", "trust"],
            ),
            EthicsDigitalFrameworkEvaluation(
                framework=EthicsFramework.DEONTOLOGY,
                digital_focus="Rights, consent, and non-manipulation in digital systems.",
                main_question="Does this system respect people as ends in themselves, with informed consent and fair treatment?",
                tentative_take="A rule-focused view would insist on clear consent, non-deception, and limits on treating users as mere data points.",
                values_highlighted=["rights", "consent", "non_deception"],
                risks_ignored=["cost", "speed", "some aggregate benefits"],
            ),
            EthicsDigitalFrameworkEvaluation(
                framework=EthicsFramework.VIRTUE_ETHICS,
                digital_focus="Character and responsibility of designers and users.",
                main_question="What kind of character and habits does this technology encourage in its creators and users?",
                tentative_take="Virtue ethics asks whether this system supports honesty, fairness, and practical wisdom or encourages laziness, selfishness, or cruelty.",
                values_highlighted=["integrity", "prudence", "fairness"],
                risks_ignored=["short_term_convenience", "pure_profit_focus"],
            ),
            EthicsDigitalFrameworkEvaluation(
                framework=EthicsFramework.CARE_ETHICS,
                digital_focus="Relationships, vulnerability, and care online.",
                main_question="Who is most vulnerable here, and how does the system affect their relationships and sense of safety?",
                tentative_take="Care ethics examines how the design treats vulnerable users and whether it responds to their needs or exploits them.",
                values_highlighted=["care", "solidarity", "protection_of_vulnerable"],
                risks_ignored=["rigid_rule_application", "purely_abstract_metrics"],
            ),
        ],
        comparison_questions=[
            "Which framework feels most persuasive for this digital case, and why?",
            "Where do the frameworks clearly disagree about what should be done?",
            "Which values are at the greatest risk of being ignored if we follow only one lens?",
        ],
        wisdom_prompts=[
            "If you were on a design team, what small change could reduce harm without killing the core idea?",
            "If you were a user, what information or control would you need to feel respected by this system?",
        ],
    )

    # Reuse the same mapping as HS ethics deep-dive
    concept_ids = [
        "ethics.concept.utilitarianism",
        "ethics.concept.kantian_deontology",
        "ethics.concept.virtue_ethics",
        "ethics.concept.care_ethics",
    ]
    methods_ids = [
        "methods.concept.reading_philosophy",
        "methods.concept.argument_reconstruction",
        "methods.concept.evaluation",
    ]

    log_hs_ethics_event(
        {
            "timestamp": datetime.utcnow().isoformat(),
            "endpoint": "hs_digital_ethics_deep_dive",
            "dilemma_text": text,
            "context_tags": tags,
            "concept_ids": concept_ids,
            "methods_ids": methods_ids,
        }
    )

    return HSDigitalEthicsDeepDiveResponse(
        lane3=lane3,
        lane4=lane4,
        concept_ids=concept_ids,
        methods_ids=methods_ids,
    )


@router.post(
    "/ethics/practice",
    response_model=PhilosophyHSEthicsPracticeResponse,
    tags=["philosophy-hs-ethics"],
)
async def hs_ethics_practice(
    request: PhilosophyHSEthicsPracticeRequest,
    raw_request: Request,
) -> PhilosophyHSEthicsPracticeResponse:
    """
    HS-level ethics practice endpoint for PRIME himself.

    - Wraps the reasoning core via HTTP to avoid circular imports.
    - Uses philosophy/ethics tools (four-lens, meta, foundations).
    - Saves the full reasoning trace into PRIME's reasoning memory.
    """
    user_id = request.user_id or "raymond"

    # 1) Build a ReasoningTask for the core.
    task = ReasoningTask(
        task_id=request.case_id or f"hs_ethics_{datetime.utcnow().isoformat()}",
        natural_language_task=request.dilemma_text,
        domain_tag="philosophy",
        subdomain_tag="ethics",
        given_facts=[],
        assumptions=[],
        constraints=[],
        desired_output_kind=ReasoningTaskKind.ANALYSIS,
        allowed_tools=[
            "philosophy_four_lens",
            "ethics_meta_perspectives",
            "philosophy_logic_lesson",
            "philosophy_methods_lesson",
            "philosophy_metaphysics_lesson",
        ],
    )

    core_req = ReasoningCoreRequest(
        task=task,
        max_steps=16,
    )

    # 2) Call the reasoning core via HTTP to avoid circular import.
    #    We assume the core is mounted at /prime/reasoning/core under the same app.
    client = raw_request.app.client if hasattr(raw_request.app, "client") else None
    try:
        import httpx
    except ImportError:
        client = None

    core_resp_data = None

    if client is not None:
        # If the app has an HTTPX client attached, use it.
        http_client = client
    else:
        # Fallback: create a one-off async client.
        http_client = httpx.AsyncClient(base_url="http://127.0.0.1:8000")

    try:
        response = await http_client.post(
            "/prime/reasoning/core",
            json=core_req.model_dump(),
        )
        if response.status_code != 200:
            # Temporary debug: print the core error to the server console
            print("DEBUG /reasoning/core error:", response.status_code, response.text)
            raise HTTPException(
                status_code=500,
                detail=f"reasoning_core returned {response.status_code}: {response.text}",
            )
        core_resp_data = response.json()
    finally:
        if client is None:
            await http_client.aclose()

    core_resp = ReasoningCoreResponse(**core_resp_data)

    # 3) Decide outcome quality (cautious for high-stakes).
    outcome_quality = (
        ReasoningOutcomeQuality.CAUTIOUS
        if is_high_stakes_task(task)
        else ReasoningOutcomeQuality.UNKNOWN
    )

    # 4) Save to reasoning memory as a philosophy/ethics episode.
    entry = ReasoningMemoryEntry(
        id=task.task_id,
        task=task,
        response=core_resp,
        tags=ReasoningTraceTag(
            domain="philosophy",
            subdomain="ethics",
            theme=request.case_id or "hs_ethics_freeform",
            user_label=None,
        ),
        created_at=datetime.utcnow(),
        user_id=user_id,
        outcome_quality=outcome_quality,
    )
    append_memory_entry(entry)

    # 5) Return a simplified HS-friendly response.
    return PhilosophyHSEthicsPracticeResponse(
        task_id=task.task_id,
        key_conclusions=core_resp.key_conclusions,
        open_questions=core_resp.open_questions,
        outcome_quality=outcome_quality,
    )

@router.post(
    "/ethics/practice/loyalty_vs_fairness",
    response_model=HSEthicsPracticeWithRubricResponse,
    tags=["philosophy-hs-ethics"],
)
async def hs_ethics_practice_loyalty_vs_fairness(
    raw_request: Request,
    user_id: str = "raymond",
    run_rubric: bool = False,
) -> HSEthicsPracticeWithRubricResponse:
    """
    HS-level ethics practice endpoint for a canonical 'loyalty vs fairness' dilemma.

    This is a ready-made case PRIME can revisit to strengthen his ethics spine.
    """
    # Canonical dilemma text (you can refine wording later).
    dilemma_text = (
        "Your close friend cheated on a big exam and asks you not to tell anyone. "
        "You know it is unfair to other students, but you also do not want your friend "
        "to get in trouble or lose trust in you. Should you report what happened?"
    )

    case_id = "canonical:loyalty_vs_fairness"

    # 1) Build a ReasoningTask for the core.
    task = ReasoningTask(
        task_id=case_id,
        natural_language_task=dilemma_text,
        domain_tag="philosophy",
        subdomain_tag="ethics",
        given_facts=[],
        assumptions=[],
        constraints=[],
        desired_output_kind=ReasoningTaskKind.ANALYSIS,
        allowed_tools=[
            "philosophy_four_lens",
            "ethics_meta_perspectives",
            "philosophy_logic_lesson",
            "philosophy_methods_lesson",
            "philosophy_metaphysics_lesson",
        ],
    )

    core_req = ReasoningCoreRequest(
        task=task,
        max_steps=16,
    )

    # 2) Call the reasoning core via HTTP to avoid circular import.
    try:
        import httpx
    except ImportError:
        httpx = None

    if httpx is None:
        raise HTTPException(
            status_code=500,
            detail="httpx is required for internal reasoning_core call but is not installed.",
        )

    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as http_client:
        response = await http_client.post(
            "/prime/reasoning/core",
            json=core_req.model_dump(),
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"reasoning_core returned {response.status_code}: {response.text}",
            )
        core_resp_data = response.json()

    core_resp = ReasoningCoreResponse(**core_resp_data)

    # 3) Decide outcome quality (cautious for high-stakes).
    outcome_quality = (
        ReasoningOutcomeQuality.CAUTIOUS
        if is_high_stakes_task(task)
        else ReasoningOutcomeQuality.UNKNOWN
    )

    # 4) Optional rubric evaluation.
    rubric_result: PhilosophyRubricEvaluateResponse | None = None

    if run_rubric:
        synthesized_answer = " ".join(core_resp.key_conclusions or [])
        rubric_req = PhilosophyRubricEvaluateRequest(
            question=dilemma_text,
            answer=synthesized_answer,
            context="hs.ethics",
        )

        async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as http_client:
            rubric_resp_raw = await http_client.post(
                "/prime/humanities/philosophy/rubric/evaluate-answer",
                json=rubric_req.model_dump(mode="json"),
            )
            if rubric_resp_raw.status_code == 200:
                rubric_result = PhilosophyRubricEvaluateResponse(
                    **rubric_resp_raw.json()
                )

    # 5) Save to reasoning memory as a philosophy/ethics episode, including rubric if present.
    entry = ReasoningMemoryEntry(
        id=task.task_id,
        task=task,
        response=core_resp,
        tags=ReasoningTraceTag(
            domain="philosophy",
            subdomain="ethics",
            theme=case_id,
            user_label=None,
        ),
        created_at=datetime.utcnow(),
        user_id=user_id,
        outcome_quality=outcome_quality,
        rubric_scores=rubric_result.scores if rubric_result else None,
        rubric_overall_comment=rubric_result.overall_comment if rubric_result else None,
    )
    append_memory_entry(entry)

    # 6) Return a simplified HS-friendly response with optional rubric.
    return HSEthicsPracticeWithRubricResponse(
        task_id=task.task_id,
        key_conclusions=core_resp.key_conclusions,
        open_questions=core_resp.open_questions,
        outcome_quality=outcome_quality,
        rubric=rubric_result,
    )

@router.post(
    "/metaphysics/practice/free_will_vs_determinism",
    response_model=PhilosophyHSEthicsPracticeResponse,
    tags=["philosophy-hs-metaphysics"],
)
async def hs_metaphysics_practice_free_will(
    raw_request: Request,
    user_id: str = "raymond",
) -> PhilosophyHSEthicsPracticeResponse:
    """
    HS-level metaphysics practice endpoint for a canonical 'free will vs determinism' case.
    Reuses the same ReasoningCoreResponse model for simplicity.
    """
    dilemma_text = (
        "You feel like you freely choose whether to study or play games, but you also "
        "hear people say that your choices are shaped by your past, your brain, and "
        "your environment. How should you think about your own free will in everyday life?"
    )

    case_id = "canonical:free_will_vs_determinism"

    task = ReasoningTask(
        task_id=case_id,
        natural_language_task=dilemma_text,
        domain_tag="philosophy",
        subdomain_tag="metaphysics",
        given_facts=[],
        assumptions=[],
        constraints=[],
        desired_output_kind=ReasoningTaskKind.ANALYSIS,
        allowed_tools=[
            "philosophy_logic_lesson",
            "philosophy_methods_lesson",
            "philosophy_metaphysics_lesson",
        ],
    )

    core_req = ReasoningCoreRequest(
        task=task,
        max_steps=16,
    )

    try:
        import httpx
    except ImportError:
        httpx = None

    if httpx is None:
        raise HTTPException(
            status_code=500,
            detail="httpx is required for internal reasoning_core call but is not installed.",
        )

    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as http_client:
        response = await http_client.post(
            "/prime/reasoning/core",
            json=core_req.model_dump(),
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"reasoning_core returned {response.status_code}: {response.text}",
            )
        core_resp_data = response.json()

    core_resp = ReasoningCoreResponse(**core_resp_data)

    outcome_quality = (
        ReasoningOutcomeQuality.CAUTIOUS
        if is_high_stakes_task(task)
        else ReasoningOutcomeQuality.UNKNOWN
    )

    entry = ReasoningMemoryEntry(
        id=task.task_id,
        task=task,
        response=core_resp,
        tags=ReasoningTraceTag(
            domain="philosophy",
            subdomain="metaphysics",
            theme=case_id,
            user_label=None,
        ),
        created_at=datetime.utcnow(),
        user_id=user_id,
        outcome_quality=outcome_quality,
    )
    append_memory_entry(entry)

    return PhilosophyHSEthicsPracticeResponse(
        task_id=task.task_id,
        key_conclusions=core_resp.key_conclusions,
        open_questions=core_resp.open_questions,
        outcome_quality=outcome_quality,
    )

@router.post(
    "/ethics/practice/truth_vs_kindness",
    response_model=HSEthicsPracticeWithRubricResponse,
    tags=["philosophy-hs-ethics"],
)
async def hs_ethics_practice_truth_vs_kindness(
    raw_request: Request,
    user_id: str = "raymond",
    run_rubric: bool = False,
) -> HSEthicsPracticeWithRubricResponse:
    """
    Canonical HS ethics practice: truth vs kindness (honesty vs protecting feelings).
    """
    dilemma_text = (
        "A friend asks if you liked their performance or creative work. "
        "You actually think it was not very good and worry that saying so will hurt their feelings, "
        "but lying feels wrong. How honest should you be when the truth might hurt someone you care about?"
    )

    case_id = "canonical:truth_vs_kindness"

    task = ReasoningTask(
        task_id=case_id,
        natural_language_task=dilemma_text,
        domain_tag="philosophy",
        subdomain_tag="ethics",
        given_facts=[],
        assumptions=[],
        constraints=[],
        desired_output_kind=ReasoningTaskKind.ANALYSIS,
        allowed_tools=[
            "philosophy_four_lens",
            "ethics_meta_perspectives",
            "philosophy_logic_lesson",
            "philosophy_methods_lesson",
            "philosophy_metaphysics_lesson",
        ],
    )

    core_req = ReasoningCoreRequest(
        task=task,
        max_steps=16,
    )

    try:
        import httpx
    except ImportError:
        httpx = None

    if httpx is None:
        raise HTTPException(
            status_code=500,
            detail="httpx is required for internal reasoning_core call but is not installed.",
        )

    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as http_client:
        response = await http_client.post(
            "/prime/reasoning/core",
            json=core_req.model_dump(),
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"reasoning_core returned {response.status_code}: {response.text}",
            )
        core_resp_data = response.json()

    core_resp = ReasoningCoreResponse(**core_resp_data)

    outcome_quality = (
        ReasoningOutcomeQuality.CAUTIOUS
        if is_high_stakes_task(task)
        else ReasoningOutcomeQuality.UNKNOWN
    )

    rubric_result: PhilosophyRubricEvaluateResponse | None = None

    if run_rubric:
        synthesized_answer = " ".join(core_resp.key_conclusions or [])
        rubric_req = PhilosophyRubricEvaluateRequest(
            question=dilemma_text,
            answer=synthesized_answer,
            context="hs.ethics",
        )

        async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as http_client:
            rubric_resp_raw = await http_client.post(
                "/prime/humanities/philosophy/rubric/evaluate-answer",
                json=rubric_req.model_dump(mode="json"),
            )
            if rubric_resp_raw.status_code == 200:
                rubric_result = PhilosophyRubricEvaluateResponse(
                    **rubric_resp_raw.json()
                )

    entry = ReasoningMemoryEntry(
        id=task.task_id,
        task=task,
        response=core_resp,
        tags=ReasoningTraceTag(
            domain="philosophy",
            subdomain="ethics",
            theme=case_id,
            user_label=None,
        ),
        created_at=datetime.utcnow(),
        user_id=user_id,
        outcome_quality=outcome_quality,
        rubric_scores=rubric_result.scores if rubric_result else None,
        rubric_overall_comment=rubric_result.overall_comment if rubric_result else None,
    )
    append_memory_entry(entry)

    return HSEthicsPracticeWithRubricResponse(
        task_id=task.task_id,
        key_conclusions=core_resp.key_conclusions,
        open_questions=core_resp.open_questions,
        outcome_quality=outcome_quality,
        rubric=rubric_result,
    )

@router.post(
    "/ethics/practice/rules_vs_compassion",
    response_model=PhilosophyHSEthicsPracticeResponse,
    tags=["philosophy-hs-ethics"],
)
async def hs_ethics_practice_rules_vs_compassion(
    raw_request: Request,
    user_id: str = "raymond",
) -> PhilosophyHSEthicsPracticeResponse:
    """
    Canonical HS ethics practice: rules vs compassion (breaking a rule to help someone).
    """
    dilemma_text = (
        "Your school rule says no phones during class. A classmate quietly asks to borrow your phone "
        "because of a family emergency, but you know you could get in serious trouble if a teacher sees. "
        "Is it right to break the rule to help them?"
    )

    case_id = "canonical:rules_vs_compassion"

    task = ReasoningTask(
        task_id=case_id,
        natural_language_task=dilemma_text,
        domain_tag="philosophy",
        subdomain_tag="ethics",
        given_facts=[],
        assumptions=[],
        constraints=[],
        desired_output_kind=ReasoningTaskKind.ANALYSIS,
        allowed_tools=[
            "philosophy_four_lens",
            "ethics_meta_perspectives",
            "philosophy_logic_lesson",
            "philosophy_methods_lesson",
            "philosophy_metaphysics_lesson",
        ],
    )

    core_req = ReasoningCoreRequest(
        task=task,
        max_steps=16,
    )

    try:
        import httpx
    except ImportError:
        httpx = None

    if httpx is None:
        raise HTTPException(
            status_code=500,
            detail="httpx is required for internal reasoning_core call but is not installed.",
        )

    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as http_client:
        response = await http_client.post(
            "/prime/reasoning/core",
            json=core_req.model_dump(),
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"reasoning_core returned {response.status_code}: {response.text}",
            )
        core_resp_data = response.json()

    core_resp = ReasoningCoreResponse(**core_resp_data)

    outcome_quality = (
        ReasoningOutcomeQuality.CAUTIOUS
        if is_high_stakes_task(task)
        else ReasoningOutcomeQuality.UNKNOWN
    )

    entry = ReasoningMemoryEntry(
        id=task.task_id,
        task=task,
        response=core_resp,
        tags=ReasoningTraceTag(
            domain="philosophy",
            subdomain="ethics",
            theme=case_id,
            user_label=None,
        ),
        created_at=datetime.utcnow(),
        user_id=user_id,
        outcome_quality=outcome_quality,
    )
    append_memory_entry(entry)

    return PhilosophyHSEthicsPracticeResponse(
        task_id=task.task_id,
        key_conclusions=core_resp.key_conclusions,
        open_questions=core_resp.open_questions,
        outcome_quality=outcome_quality,
    )

@router.post(
    "/ethics/practice/family_loyalty_vs_fairness",
    response_model=PhilosophyHSEthicsPracticeResponse,
    tags=["philosophy-hs-ethics"],
)
async def hs_ethics_practice_family_loyalty_vs_fairness(
    raw_request: Request,
    user_id: str = "raymond",
) -> PhilosophyHSEthicsPracticeResponse:
    """
    Canonical HS ethics practice: loyalty to family vs fairness to others.
    """
    dilemma_text = (
        "You discover that your older sibling has been secretly using someone else's work for assignments "
        "and getting rewarded for it. Reporting them feels like betraying your family, but staying silent "
        "feels unfair to other students who work hard. Should you protect your sibling or speak up about the cheating?"
    )

    case_id = "canonical:family_loyalty_vs_fairness"

    task = ReasoningTask(
        task_id=case_id,
        natural_language_task=dilemma_text,
        domain_tag="philosophy",
        subdomain_tag="ethics",
        given_facts=[],
        assumptions=[],
        constraints=[],
        desired_output_kind=ReasoningTaskKind.ANALYSIS,
        allowed_tools=[
            "philosophy_four_lens",
            "ethics_meta_perspectives",
            "philosophy_logic_lesson",
            "philosophy_methods_lesson",
            "philosophy_metaphysics_lesson",
        ],
    )

    core_req = ReasoningCoreRequest(
        task=task,
        max_steps=16,
    )

    try:
        import httpx
    except ImportError:
        httpx = None

    if httpx is None:
        raise HTTPException(
            status_code=500,
            detail="httpx is required for internal reasoning_core call but is not installed.",
        )

    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as http_client:
        response = await http_client.post(
            "/prime/reasoning/core",
            json=core_req.model_dump(),
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"reasoning_core returned {response.status_code}: {response.text}",
            )
        core_resp_data = response.json()

    core_resp = ReasoningCoreResponse(**core_resp_data)

    outcome_quality = (
        ReasoningOutcomeQuality.CAUTIOUS
        if is_high_stakes_task(task)
        else ReasoningOutcomeQuality.UNKNOWN
    )

    entry = ReasoningMemoryEntry(
        id=task.task_id,
        task=task,
        response=core_resp,
        tags=ReasoningTraceTag(
            domain="philosophy",
            subdomain="ethics",
            theme=case_id,
            user_label=None,
        ),
        created_at=datetime.utcnow(),
        user_id=user_id,
        outcome_quality=outcome_quality,
    )
    append_memory_entry(entry)

    return PhilosophyHSEthicsPracticeResponse(
        task_id=task.task_id,
        key_conclusions=core_resp.key_conclusions,
        open_questions=core_resp.open_questions,
        outcome_quality=outcome_quality,
    )

@router.post(
    "/ethics/practice/privacy_vs_safety",
    response_model=PhilosophyHSEthicsPracticeResponse,
    tags=["philosophy-hs-ethics"],
)
async def hs_ethics_practice_privacy_vs_safety(
    raw_request: Request,
    user_id: str = "raymond",
) -> PhilosophyHSEthicsPracticeResponse:
    """
    Canonical HS ethics practice: privacy vs safety (sharing a dangerous secret).
    """
    dilemma_text = (
        "A friend tells you they have been feeling very low and sometimes think about hurting themselves, "
        "but they beg you not to tell any adult because they 'don't want drama'. You are scared for them, "
        "but also want to respect their trust. Should you keep their secret or tell a trusted adult?"
    )

    case_id = "canonical:privacy_vs_safety"

    task = ReasoningTask(
        task_id=case_id,
        natural_language_task=dilemma_text,
        domain_tag="philosophy",
        subdomain_tag="ethics",
        given_facts=[],
        assumptions=[],
        constraints=[],
        desired_output_kind=ReasoningTaskKind.ANALYSIS,
        allowed_tools=[
            "philosophy_four_lens",
            "ethics_meta_perspectives",
            "philosophy_logic_lesson",
            "philosophy_methods_lesson",
            "philosophy_metaphysics_lesson",
        ],
    )

    core_req = ReasoningCoreRequest(
        task=task,
        max_steps=16,
    )

    try:
        import httpx
    except ImportError:
        httpx = None

    if httpx is None:
        raise HTTPException(
            status_code=500,
            detail="httpx is required for internal reasoning_core call but is not installed.",
        )

    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as http_client:
        response = await http_client.post(
            "/prime/reasoning/core",
            json=core_req.model_dump(),
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"reasoning_core returned {response.status_code}: {response.text}",
            )
        core_resp_data = response.json()

    core_resp = ReasoningCoreResponse(**core_resp_data)

    outcome_quality = (
        ReasoningOutcomeQuality.CAUTIOUS
        if is_high_stakes_task(task)
        else ReasoningOutcomeQuality.UNKNOWN
    )

    entry = ReasoningMemoryEntry(
        id=task.task_id,
        task=task,
        response=core_resp,
        tags=ReasoningTraceTag(
            domain="philosophy",
            subdomain="ethics",
            theme=case_id,
            user_label=None,
        ),
        created_at=datetime.utcnow(),
        user_id=user_id,
        outcome_quality=outcome_quality,
    )
    append_memory_entry(entry)

    return PhilosophyHSEthicsPracticeResponse(
        task_id=task.task_id,
        key_conclusions=core_resp.key_conclusions,
        open_questions=core_resp.open_questions,
        outcome_quality=outcome_quality,
    )

@router.post(
    "/ethics/practice/friend_loyalty_vs_anti_bullying",
    response_model=PhilosophyHSEthicsPracticeResponse,
    tags=["philosophy-hs-ethics"],
)
async def hs_ethics_practice_friend_loyalty_vs_anti_bullying(
    raw_request: Request,
    user_id: str = "raymond",
) -> PhilosophyHSEthicsPracticeResponse:
    """
    Canonical HS ethics practice: loyalty to a friend vs standing up to bullying.
    """
    dilemma_text = (
        "Your friend often makes jokes about another student that everyone laughs at, "
        "but you can see the other student is uncomfortable and hurt. You worry that if you speak up, "
        "your friend group might turn on you or think you are no fun. Should you challenge the jokes "
        "or stay quiet to keep your friend's approval?"
    )

    case_id = "canonical:friend_loyalty_vs_anti_bullying"

    task = ReasoningTask(
        task_id=case_id,
        natural_language_task=dilemma_text,
        domain_tag="philosophy",
        subdomain_tag="ethics",
        given_facts=[],
        assumptions=[],
        constraints=[],
        desired_output_kind=ReasoningTaskKind.ANALYSIS,
        allowed_tools=[
            "philosophy_four_lens",
            "ethics_meta_perspectives",
            "philosophy_logic_lesson",
            "philosophy_methods_lesson",
            "philosophy_metaphysics_lesson",
        ],
    )

    core_req = ReasoningCoreRequest(
        task=task,
        max_steps=16,
    )

    try:
        import httpx
    except ImportError:
        httpx = None

    if httpx is None:
        raise HTTPException(
            status_code=500,
            detail="httpx is required for internal reasoning_core call but is not installed.",
        )

    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as http_client:
        response = await http_client.post(
            "/prime/reasoning/core",
            json=core_req.model_dump(),
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"reasoning_core returned {response.status_code}: {response.text}",
            )
        core_resp_data = response.json()

    core_resp = ReasoningCoreResponse(**core_resp_data)

    outcome_quality = (
        ReasoningOutcomeQuality.CAUTIOUS
        if is_high_stakes_task(task)
        else ReasoningOutcomeQuality.UNKNOWN
    )

    entry = ReasoningMemoryEntry(
        id=task.task_id,
        task=task,
        response=core_resp,
        tags=ReasoningTraceTag(
            domain="philosophy",
            subdomain="ethics",
            theme=case_id,
            user_label=None,
        ),
        created_at=datetime.utcnow(),
        user_id=user_id,
        outcome_quality=outcome_quality,
    )
    append_memory_entry(entry)

    return PhilosophyHSEthicsPracticeResponse(
        task_id=task.task_id,
        key_conclusions=core_resp.key_conclusions,
        open_questions=core_resp.open_questions,
        outcome_quality=outcome_quality,
    )

@router.post(
    "/epistemology/practice/trust_the_internet",
    response_model=HSEpistemologyPracticeWithRubricResponse,
    tags=["philosophy-hs-epistemology"],
)
async def hs_epistemology_practice_trust_the_internet(
    raw_request: Request,
    user_id: str = "raymond",
    run_rubric: bool = False,
) -> HSEpistemologyPracticeWithRubricResponse:
    """
    Canonical HS epistemology practice: when and how to trust information from the internet.
    """
    dilemma_text = (
        "You learn most things about the world from the internet: social media, videos, and articles. "
        "Some sources contradict each other, and some seem biased or clickbait. "
        "How should you decide when information from the internet is trustworthy?"
    )

    case_id = "canonical:epistemology_trust_the_internet"

    task = ReasoningTask(
        task_id=case_id,
        natural_language_task=dilemma_text,
        domain_tag="philosophy",
        subdomain_tag="epistemology",
        given_facts=[],
        assumptions=[],
        constraints=[],
        desired_output_kind=ReasoningTaskKind.ANALYSIS,
        allowed_tools=[
            "philosophy_logic_lesson",
            "philosophy_methods_lesson",
        ],
    )

    core_req = ReasoningCoreRequest(
        task=task,
        max_steps=16,
    )

    # 2) Call the reasoning core via HTTP to avoid circular import.
    try:
        import httpx
    except ImportError:
        httpx = None

    if httpx is None:
        raise HTTPException(
            status_code=500,
            detail="httpx is required for internal reasoning_core call but is not installed.",
        )

    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as http_client:
        response = await http_client.post(
            "/prime/reasoning/core",
            json=core_req.model_dump(),
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"reasoning_core returned {response.status_code}: {response.text}",
            )
        core_resp_data = response.json()

    core_resp = ReasoningCoreResponse(**core_resp_data)

    # 3) Decide outcome quality (cautious for high-stakes).
    outcome_quality = (
        ReasoningOutcomeQuality.CAUTIOUS
        if is_high_stakes_task(task)
        else ReasoningOutcomeQuality.UNKNOWN
    )

    # 4) Optional rubric evaluation.
    rubric_result: PhilosophyRubricEvaluateResponse | None = None

    if run_rubric:
        synthesized_answer = " ".join(core_resp.key_conclusions or [])
        rubric_req = PhilosophyRubricEvaluateRequest(
            question=dilemma_text,
            answer=synthesized_answer,
            context="hs.epistemology",
        )

        async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as http_client:
            rubric_resp_raw = await http_client.post(
                "/prime/humanities/philosophy/rubric/evaluate-answer",
                json=rubric_req.model_dump(mode="json"),
            )
            if rubric_resp_raw.status_code == 200:
                rubric_result = PhilosophyRubricEvaluateResponse(
                    **rubric_resp_raw.json()
                )

    # 5) Save to reasoning memory as an epistemology episode, including rubric if present.
    entry = ReasoningMemoryEntry(
        id=task.task_id,
        task=task,
        response=core_resp,
        tags=ReasoningTraceTag(
            domain="philosophy",
            subdomain="epistemology",
            theme=case_id,
            user_label=None,
        ),
        created_at=datetime.utcnow(),
        user_id=user_id,
        outcome_quality=outcome_quality,
        rubric_scores=rubric_result.scores if rubric_result else None,
        rubric_overall_comment=rubric_result.overall_comment if rubric_result else None,
    )
    append_memory_entry(entry)

    # 6) Return HS-friendly response with optional rubric.
    return HSEpistemologyPracticeWithRubricResponse(
        task_id=task.task_id,
        key_conclusions=core_resp.key_conclusions,
        open_questions=core_resp.open_questions,
        outcome_quality=outcome_quality,
        rubric=rubric_result,
    )


@router.post(
    "/epistemology/practice/memory_accuracy",
    response_model=PhilosophyHSEthicsPracticeResponse,
    tags=["philosophy-hs-epistemology"],
)
async def hs_epistemology_practice_memory_accuracy(
    raw_request: Request,
    user_id: str = "raymond",
) -> PhilosophyHSEthicsPracticeResponse:
    """
    Canonical HS epistemology practice: reliability of memory.
    """
    dilemma_text = (
        "You and a friend remember the same event in very different ways, and both of you feel sure you are right. "
        "Later you learn that memory can change over time and be influenced by what people say. "
        "If your own memories can be mistaken, how should you think about what you 'know' from memory?"
    )

    case_id = "canonical:epistemology_memory_accuracy"

    task = ReasoningTask(
        task_id=case_id,
        natural_language_task=dilemma_text,
        domain_tag="philosophy",
        subdomain_tag="epistemology",
        given_facts=[],
        assumptions=[],
        constraints=[],
        desired_output_kind=ReasoningTaskKind.ANALYSIS,
        allowed_tools=[
            "philosophy_logic_lesson",
            "philosophy_methods_lesson",
        ],
    )

    core_req = ReasoningCoreRequest(
        task=task,
        max_steps=16,
    )

    try:
        import httpx
    except ImportError:
        httpx = None

    if httpx is None:
        raise HTTPException(
            status_code=500,
            detail="httpx is required for internal reasoning_core call but is not installed.",
        )

    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as http_client:
        response = await http_client.post(
            "/prime/reasoning/core",
            json=core_req.model_dump(),
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"reasoning_core returned {response.status_code}: {response.text}",
            )
        core_resp_data = response.json()

    core_resp = ReasoningCoreResponse(**core_resp_data)

    outcome_quality = (
        ReasoningOutcomeQuality.CAUTIOUS
        if is_high_stakes_task(task)
        else ReasoningOutcomeQuality.UNKNOWN
    )

    entry = ReasoningMemoryEntry(
        id=task.task_id,
        task=task,
        response=core_resp,
        tags=ReasoningTraceTag(
            domain="philosophy",
            subdomain="epistemology",
            theme=case_id,
            user_label=None,
        ),
        created_at=datetime.utcnow(),
        user_id=user_id,
        outcome_quality=outcome_quality,
    )
    append_memory_entry(entry)

    return PhilosophyHSEthicsPracticeResponse(
        task_id=task.task_id,
        key_conclusions=core_resp.key_conclusions,
        open_questions=core_resp.open_questions,
        outcome_quality=outcome_quality,
    )

@router.post(
    "/epistemology/practice/trusting_experts",
    response_model=HSEpistemologyPracticeWithRubricResponse,
    tags=["philosophy-hs-epistemology"],
)
async def hs_epistemology_practice_trusting_experts(
    raw_request: Request,
    user_id: str = "raymond",
    run_rubric: bool = False,
) -> HSEpistemologyPracticeWithRubricResponse:
    """
    Canonical HS epistemology practice: when to trust expert testimony.
    """
    dilemma_text = (
        "On a complicated topic like climate change, health, or economics, experts disagree and news stories "
        "sometimes give opposite opinions. You do not have time or training to study everything yourself. "
        "When is it reasonable to trust experts, and how should you decide which experts to trust?"
    )

    case_id = "canonical:epistemology_trusting_experts"

    task = ReasoningTask(
        task_id=case_id,
        natural_language_task=dilemma_text,
        domain_tag="philosophy",
        subdomain_tag="epistemology",
        given_facts=[],
        assumptions=[],
        constraints=[],
        desired_output_kind=ReasoningTaskKind.ANALYSIS,
        allowed_tools=[
            "philosophy_logic_lesson",
            "philosophy_methods_lesson",
        ],
    )

    core_req = ReasoningCoreRequest(
        task=task,
        max_steps=16,
    )

    try:
        import httpx
    except ImportError:
        httpx = None

    if httpx is None:
        raise HTTPException(
            status_code=500,
            detail="httpx is required for internal reasoning_core call but is not installed.",
        )

    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as http_client:
        response = await http_client.post(
            "/prime/reasoning/core",
            json=core_req.model_dump(),
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"reasoning_core returned {response.status_code}: {response.text}",
            )
        core_resp_data = response.json()

    core_resp = ReasoningCoreResponse(**core_resp_data)

    outcome_quality = ReasoningOutcomeQuality.GOOD

    rubric_result: PhilosophyRubricEvaluateResponse | None = None

    if run_rubric:
        synthesized_answer = " ".join(core_resp.key_conclusions or [])
        rubric_req = PhilosophyRubricEvaluateRequest(
            question=dilemma_text,
            answer=synthesized_answer,
            context="hs.epistemology",
        )

        async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as http_client:
            rubric_resp_raw = await http_client.post(
                "/prime/humanities/philosophy/rubric/evaluate-answer",
                json=rubric_req.model_dump(mode="json"),
            )
            if rubric_resp_raw.status_code == 200:
                rubric_result = PhilosophyRubricEvaluateResponse(
                    **rubric_resp_raw.json()
                )

    memory_entry = ReasoningMemoryEntry(
        id=task.task_id,
        task=task,
        response=core_resp,
        tags=ReasoningTraceTag(
            domain="philosophy",
            subdomain="epistemology",
            level="hs",
            theme="hs.epistemology.trusting_experts",
        ),
        created_at=datetime.utcnow(),
        user_id=user_id,
        outcome_quality=outcome_quality,
        rubric_scores=rubric_result.scores if rubric_result else None,
        rubric_overall_comment=rubric_result.overall_comment if rubric_result else None,
    )
    append_memory_entry(memory_entry)

    return HSEpistemologyPracticeWithRubricResponse(
        task_id=task.task_id,
        key_conclusions=core_resp.key_conclusions,
        open_questions=core_resp.open_questions,
        outcome_quality=outcome_quality,
        rubric=rubric_result,
    )

@router.post(
    "/political/practice/unfair_school_rule",
    response_model=PhilosophyHSEthicsPracticeResponse,
    tags=["philosophy-hs-political"],
)
async def hs_political_practice_unfair_school_rule(
    raw_request: Request,
    user_id: str = "raymond",
) -> PhilosophyHSEthicsPracticeResponse:
    """
    Canonical HS political philosophy practice: civil disobedience vs following rules.
    """
    dilemma_text = (
        "Your school has a rule that seems unfair, such as a dress code or policy that targets some students "
        "more than others. Some classmates want to quietly break the rule in protest, while others say you must "
        "follow rules even when they are unfair. Is it okay to break an unfair school rule, and if so, how?"
    )

    case_id = "canonical:political_unfair_school_rule"

    task = ReasoningTask(
        task_id=case_id,
        natural_language_task=dilemma_text,
        domain_tag="philosophy",
        subdomain_tag="political",
        given_facts=[],
        assumptions=[],
        constraints=[],
        desired_output_kind=ReasoningTaskKind.ANALYSIS,
        allowed_tools=[
            "philosophy_logic_lesson",
            "philosophy_methods_lesson",
        ],
    )

    core_req = ReasoningCoreRequest(
        task=task,
        max_steps=16,
    )

    try:
        import httpx
    except ImportError:
        httpx = None

    if httpx is None:
        raise HTTPException(
            status_code=500,
            detail="httpx is required for internal reasoning_core call but is not installed.",
        )

    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as http_client:
        response = await http_client.post(
            "/prime/reasoning/core",
            json=core_req.model_dump(),
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"reasoning_core returned {response.status_code}: {response.text}",
            )
        core_resp_data = response.json()

    core_resp = ReasoningCoreResponse(**core_resp_data)

    outcome_quality = (
        ReasoningOutcomeQuality.CAUTIOUS
        if is_high_stakes_task(task)
        else ReasoningOutcomeQuality.UNKNOWN
    )

    entry = ReasoningMemoryEntry(
        id=task.task_id,
        task=task,
        response=core_resp,
        tags=ReasoningTraceTag(
            domain="philosophy",
            subdomain="political",
            theme=case_id,
            user_label=None,
        ),
        created_at=datetime.utcnow(),
        user_id=user_id,
        outcome_quality=outcome_quality,
    )
    append_memory_entry(entry)

    return PhilosophyHSEthicsPracticeResponse(
        task_id=task.task_id,
        key_conclusions=core_resp.key_conclusions,
        open_questions=core_resp.open_questions,
        outcome_quality=outcome_quality,
    )

@router.post(
    "/political/practice/equality_vs_fairness",
    response_model=PhilosophyHSEthicsPracticeResponse,
    tags=["philosophy-hs-political"],
)
async def hs_political_practice_equality_vs_fairness(
    raw_request: Request,
    user_id: str = "raymond",
) -> PhilosophyHSEthicsPracticeResponse:
    """
    Canonical HS political philosophy practice: equality vs fairness.
    """
    dilemma_text = (
        "A teacher is deciding how to distribute extra help or opportunities. One option is to treat everyone "
        "exactly the same, for example giving the same time or resources to each student. Another option is to "
        "give more help to students who are struggling or have fewer advantages. Should everyone be treated "
        "exactly the same, or can fairness mean giving different support to different people?"
    )

    case_id = "canonical:political_equality_vs_fairness"

    task = ReasoningTask(
        task_id=case_id,
        natural_language_task=dilemma_text,
        domain_tag="philosophy",
        subdomain_tag="political",
        given_facts=[],
        assumptions=[],
        constraints=[],
        desired_output_kind=ReasoningTaskKind.ANALYSIS,
        allowed_tools=[
            "philosophy_logic_lesson",
            "philosophy_methods_lesson",
        ],
    )

    core_req = ReasoningCoreRequest(
        task=task,
        max_steps=16,
    )

    try:
        import httpx
    except ImportError:
        httpx = None

    if httpx is None:
        raise HTTPException(
            status_code=500,
            detail="httpx is required for internal reasoning_core call but is not installed.",
        )

    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as http_client:
        response = await http_client.post(
            "/prime/reasoning/core",
            json=core_req.model_dump(),
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"reasoning_core returned {response.status_code}: {response.text}",
            )
        core_resp_data = response.json()

    core_resp = ReasoningCoreResponse(**core_resp_data)

    outcome_quality = (
        ReasoningOutcomeQuality.CAUTIOUS
        if is_high_stakes_task(task)
        else ReasoningOutcomeQuality.UNKNOWN
    )

    entry = ReasoningMemoryEntry(
        id=task.task_id,
        task=task,
        response=core_resp,
        tags=ReasoningTraceTag(
            domain="philosophy",
            subdomain="political",
            theme=case_id,
            user_label=None,
        ),
        created_at=datetime.utcnow(),
        user_id=user_id,
        outcome_quality=outcome_quality,
    )
    append_memory_entry(entry)

    return PhilosophyHSEthicsPracticeResponse(
        task_id=task.task_id,
        key_conclusions=core_resp.key_conclusions,
        open_questions=core_resp.open_questions,
        outcome_quality=outcome_quality,
    )

@router.post(
    "/political/practice/privacy_vs_security",
    response_model=PhilosophyHSEthicsPracticeResponse,
    tags=["philosophy-hs-political"],
)
async def hs_political_practice_privacy_vs_security(
    raw_request: Request,
    user_id: str = "raymond",
) -> PhilosophyHSEthicsPracticeResponse:
    """
    Canonical HS political philosophy practice: privacy vs security.
    """
    dilemma_text = (
        "Some people argue that schools or governments should collect more data about people "
        "and monitor messages or locations to keep everyone safe. Others say this invades privacy "
        "and gives too much power to authorities. How much privacy should people give up for security, "
        "and who should decide?"
    )

    case_id = "canonical:political_privacy_vs_security"

    task = ReasoningTask(
        task_id=case_id,
        natural_language_task=dilemma_text,
        domain_tag="philosophy",
        subdomain_tag="political",
        given_facts=[],
        assumptions=[],
        constraints=[],
        desired_output_kind=ReasoningTaskKind.ANALYSIS,
        allowed_tools=[
            "philosophy_logic_lesson",
            "philosophy_methods_lesson",
        ],
    )

    core_req = ReasoningCoreRequest(
        task=task,
        max_steps=16,
    )

    try:
        import httpx
    except ImportError:
        httpx = None

    if httpx is None:
        raise HTTPException(
            status_code=500,
            detail="httpx is required for internal reasoning_core call but is not installed.",
        )

    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as http_client:
        response = await http_client.post(
            "/prime/reasoning/core",
            json=core_req.model_dump(),
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"reasoning_core returned {response.status_code}: {response.text}",
            )
        core_resp_data = response.json()

    core_resp = ReasoningCoreResponse(**core_resp_data)

    outcome_quality = (
        ReasoningOutcomeQuality.CAUTIOUS
        if is_high_stakes_task(task)
        else ReasoningOutcomeQuality.UNKNOWN
    )

    entry = ReasoningMemoryEntry(
        id=task.task_id,
        task=task,
        response=core_resp,
        tags=ReasoningTraceTag(
            domain="philosophy",
            subdomain="political",
            theme=case_id,
            user_label=None,
        ),
        created_at=datetime.utcnow(),
        user_id=user_id,
        outcome_quality=outcome_quality,
    )
    append_memory_entry(entry)

    return PhilosophyHSEthicsPracticeResponse(
        task_id=task.task_id,
        key_conclusions=core_resp.key_conclusions,
        open_questions=core_resp.open_questions,
        outcome_quality=outcome_quality,
    )

@router.post(
    "/metaphysics/practice/personal_identity_over_time",
    response_model=PhilosophyHSEthicsPracticeResponse,
    tags=["philosophy-hs-metaphysics"],
)
async def hs_metaphysics_practice_personal_identity_over_time(
    raw_request: Request,
    user_id: str = "raymond",
) -> PhilosophyHSEthicsPracticeResponse:
    """
    HS metaphysics canonical practice: personal identity over time.
    """
    dilemma_text = (
        "You have changed a lot over the last few years in your beliefs, personality, "
        "and friendships. You might even feel embarrassed about your past self. "
        "In what sense are you still the same person over time, and what would have "
        "to change for you to say you are 'not the same person' anymore?"
    )

    case_id = "canonical:metaphysics_personal_identity_over_time"

    task = ReasoningTask(
        task_id=case_id,
        natural_language_task=dilemma_text,
        domain_tag="philosophy",
        subdomain_tag="metaphysics",
        given_facts=[],
        assumptions=[],
        constraints=[],
        desired_output_kind=ReasoningTaskKind.ANALYSIS,
        allowed_tools=[
            "philosophy_logic_lesson",
            "philosophy_methods_lesson",
            "philosophy_metaphysics_lesson",
        ],
    )

    core_req = ReasoningCoreRequest(
        task=task,
        max_steps=16,
    )

    import httpx

    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as http_client:
        resp = await http_client.post(
            "/prime/reasoning/core",
            json=core_req.model_dump(),
        )
        if resp.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"reasoning_core returned {resp.status_code}: {resp.text}",
            )
        core_resp = ReasoningCoreResponse(**resp.json())

    outcome_quality = (
        ReasoningOutcomeQuality.CAUTIOUS
        if is_high_stakes_task(task)
        else ReasoningOutcomeQuality.UNKNOWN
    )

    entry = ReasoningMemoryEntry(
        id=task.task_id,
        task=task,
        response=core_resp,
        tags=ReasoningTraceTag(
            domain="philosophy",
            subdomain="metaphysics",
            theme=case_id,
            user_label=None,
        ),
        created_at=datetime.utcnow(),
        user_id=user_id,
        outcome_quality=outcome_quality,
    )
    append_memory_entry(entry)

    return PhilosophyHSEthicsPracticeResponse(
        task_id=task.task_id,
        key_conclusions=core_resp.key_conclusions,
        open_questions=core_resp.open_questions,
        outcome_quality=outcome_quality,
    )

@router.post(
    "/metaphysics/practice/appearance_vs_reality",
    response_model=PhilosophyHSEthicsPracticeResponse,
    tags=["philosophy-hs-metaphysics"],
)
async def hs_metaphysics_practice_appearance_vs_reality(
    raw_request: Request,
    user_id: str = "raymond",
) -> PhilosophyHSEthicsPracticeResponse:
    """
    HS metaphysics canonical practice: appearance vs reality.
    """
    dilemma_text = (
        "Sometimes things look one way but turn out to be different: magic tricks, "
        "optical illusions, filtered photos, or fake online personas. "
        "If appearances can be misleading, what does it mean for something to be "
        "'really' the way it is, beyond how it looks to us?"
    )

    case_id = "canonical:metaphysics_appearance_vs_reality"

    task = ReasoningTask(
        task_id=case_id,
        natural_language_task=dilemma_text,
        domain_tag="philosophy",
        subdomain_tag="metaphysics",
        given_facts=[],
        assumptions=[],
        constraints=[],
        desired_output_kind=ReasoningTaskKind.ANALYSIS,
        allowed_tools=[
            "philosophy_logic_lesson",
            "philosophy_methods_lesson",
            "philosophy_metaphysics_lesson",
        ],
    )

    core_req = ReasoningCoreRequest(
        task=task,
        max_steps=16,
    )

    import httpx

    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as http_client:
        resp = await http_client.post(
            "/prime/reasoning/core",
            json=core_req.model_dump(),
        )
        if resp.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"reasoning_core returned {resp.status_code}: {resp.text}",
            )
        core_resp = ReasoningCoreResponse(**resp.json())

    outcome_quality = (
        ReasoningOutcomeQuality.CAUTIOUS
        if is_high_stakes_task(task)
        else ReasoningOutcomeQuality.UNKNOWN
    )

    entry = ReasoningMemoryEntry(
        id=task.task_id,
        task=task,
        response=core_resp,
        tags=ReasoningTraceTag(
            domain="philosophy",
            subdomain="metaphysics",
            theme=case_id,
            user_label=None,
        ),
        created_at=datetime.utcnow(),
        user_id=user_id,
        outcome_quality=outcome_quality,
    )
    append_memory_entry(entry)

    return PhilosophyHSEthicsPracticeResponse(
        task_id=task.task_id,
        key_conclusions=core_resp.key_conclusions,
        open_questions=core_resp.open_questions,
        outcome_quality=outcome_quality,
    )

@router.post(
    "/metaphysics/practice/mind_and_body",
    response_model=PhilosophyHSEthicsPracticeResponse,
    tags=["philosophy-hs-metaphysics"],
)
async def hs_metaphysics_practice_mind_and_body(
    raw_request: Request,
    user_id: str = "raymond",
) -> PhilosophyHSEthicsPracticeResponse:
    """
    HS metaphysics canonical practice: mind–body relationship.
    """
    dilemma_text = (
        "When you think, feel, or imagine something, it seems very different from "
        "physical objects like tables or phones. At the same time, science connects "
        "thoughts and feelings to brain activity. Are your mind and your body the same "
        "thing, or is there something about you that is not physical?"
    )

    case_id = "canonical:metaphysics_mind_and_body"

    task = ReasoningTask(
        task_id=case_id,
        natural_language_task=dilemma_text,
        domain_tag="philosophy",
        subdomain_tag="metaphysics",
        given_facts=[],
        assumptions=[],
        constraints=[],
        desired_output_kind=ReasoningTaskKind.ANALYSIS,
        allowed_tools=[
            "philosophy_logic_lesson",
            "philosophy_methods_lesson",
            "philosophy_metaphysics_lesson",
        ],
    )

    core_req = ReasoningCoreRequest(
        task=task,
        max_steps=16,
    )

    import httpx

    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as http_client:
        resp = await http_client.post(
            "/prime/reasoning/core",
            json=core_req.model_dump(),
        )
        if resp.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"reasoning_core returned {resp.status_code}: {resp.text}",
            )
        core_resp = ReasoningCoreResponse(**resp.json())

    outcome_quality = (
        ReasoningOutcomeQuality.CAUTIOUS
        if is_high_stakes_task(task)
        else ReasoningOutcomeQuality.UNKNOWN
    )

    entry = ReasoningMemoryEntry(
        id=task.task_id,
        task=task,
        response=core_resp,
        tags=ReasoningTraceTag(
            domain="philosophy",
            subdomain="metaphysics",
            theme=case_id,
            user_label=None,
        ),
        created_at=datetime.utcnow(),
        user_id=user_id,
        outcome_quality=outcome_quality,
    )
    append_memory_entry(entry)

    return PhilosophyHSEthicsPracticeResponse(
        task_id=task.task_id,
        key_conclusions=core_resp.key_conclusions,
        open_questions=core_resp.open_questions,
        outcome_quality=outcome_quality,
    )

@router.post(
    "/metaphysics/practice/personal_identity_over_time",
    response_model=PhilosophyHSEthicsPracticeResponse,
    tags=["philosophy-hs-metaphysics"],
)
async def hs_metaphysics_practice_personal_identity_over_time(
    raw_request: Request,
    user_id: str = "raymond",
) -> PhilosophyHSEthicsPracticeResponse:
    """
    Canonical HS metaphysics practice: personal identity over time.
    """
    dilemma_text = (
        "You have changed a lot over the last few years in your beliefs, personality, and friendships. "
        "You might even feel embarrassed about your past self. In what sense are you still the same person "
        "over time, and what would have to change for you to say you are 'not the same person' anymore?"
    )

    case_id = "canonical:metaphysics_personal_identity_over_time"

    task = ReasoningTask(
        task_id=case_id,
        natural_language_task=dilemma_text,
        domain_tag="philosophy",
        subdomain_tag="metaphysics",
        given_facts=[],
        assumptions=[],
        constraints=[],
        desired_output_kind=ReasoningTaskKind.ANALYSIS,
        allowed_tools=[
            "philosophy_logic_lesson",
            "philosophy_methods_lesson",
            "philosophy_metaphysics_lesson",
        ],
    )

    core_req = ReasoningCoreRequest(
        task=task,
        max_steps=16,
    )

    try:
        import httpx
    except ImportError:
        httpx = None

    if httpx is None:
        raise HTTPException(
            status_code=500,
            detail="httpx is required for internal reasoning_core call but is not installed.",
        )

    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as http_client:
        response = await http_client.post(
            "/prime/reasoning/core",
            json=core_req.model_dump(),
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"reasoning_core returned {response.status_code}: {response.text}",
            )
        core_resp_data = response.json()

    core_resp = ReasoningCoreResponse(**core_resp_data)

    outcome_quality = (
        ReasoningOutcomeQuality.CAUTIOUS
        if is_high_stakes_task(task)
        else ReasoningOutcomeQuality.UNKNOWN
    )

    entry = ReasoningMemoryEntry(
        id=task.task_id,
        task=task,
        response=core_resp,
        tags=ReasoningTraceTag(
            domain="philosophy",
            subdomain="metaphysics",
            theme=case_id,
            user_label=None,
        ),
        created_at=datetime.utcnow(),
        user_id=user_id,
        outcome_quality=outcome_quality,
    )
    append_memory_entry(entry)

    return PhilosophyHSEthicsPracticeResponse(
        task_id=task.task_id,
        key_conclusions=core_resp.key_conclusions,
        open_questions=core_resp.open_questions,
        outcome_quality=outcome_quality,
    )

@router.post(
    "/metaphysics/practice/appearance_vs_reality",
    response_model=PhilosophyHSEthicsPracticeResponse,
    tags=["philosophy-hs-metaphysics"],
)
async def hs_metaphysics_practice_appearance_vs_reality(
    raw_request: Request,
    user_id: str = "raymond",
) -> PhilosophyHSEthicsPracticeResponse:
    """
    Canonical HS metaphysics practice: appearance vs reality.
    """
    dilemma_text = (
        "Sometimes things look one way but turn out to be different: magic tricks, optical illusions, "
        "filtered photos, or fake online personas. If appearances can be misleading, what does it mean "
        "for something to be 'really' the way it is, beyond how it looks to us?"
    )

    case_id = "canonical:metaphysics_appearance_vs_reality"

    task = ReasoningTask(
        task_id=case_id,
        natural_language_task=dilemma_text,
        domain_tag="philosophy",
        subdomain_tag="metaphysics",
        given_facts=[],
        assumptions=[],
        constraints=[],
        desired_output_kind=ReasoningTaskKind.ANALYSIS,
        allowed_tools=[
            "philosophy_logic_lesson",
            "philosophy_methods_lesson",
            "philosophy_metaphysics_lesson",
        ],
    )

    core_req = ReasoningCoreRequest(
        task=task,
        max_steps=16,
    )

    try:
        import httpx
    except ImportError:
        httpx = None

    if httpx is None:
        raise HTTPException(
            status_code=500,
            detail="httpx is required for internal reasoning_core call but is not installed.",
        )

    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as http_client:
        response = await http_client.post(
            "/prime/reasoning/core",
            json=core_req.model_dump(),
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"reasoning_core returned {response.status_code}: {response.text}",
            )
        core_resp_data = response.json()

    core_resp = ReasoningCoreResponse(**core_resp_data)

    outcome_quality = (
        ReasoningOutcomeQuality.CAUTIOUS
        if is_high_stakes_task(task)
        else ReasoningOutcomeQuality.UNKNOWN
    )

    entry = ReasoningMemoryEntry(
        id=task.task_id,
        task=task,
        response=core_resp,
        tags=ReasoningTraceTag(
            domain="philosophy",
            subdomain="metaphysics",
            theme=case_id,
            user_label=None,
        ),
        created_at=datetime.utcnow(),
        user_id=user_id,
        outcome_quality=outcome_quality,
    )
    append_memory_entry(entry)

    return PhilosophyHSEthicsPracticeResponse(
        task_id=task.task_id,
        key_conclusions=core_resp.key_conclusions,
        open_questions=core_resp.open_questions,
        outcome_quality=outcome_quality,
    )

@router.post(
    "/metaphysics/practice/mind_and_body",
    response_model=PhilosophyHSEthicsPracticeResponse,
    tags=["philosophy-hs-metaphysics"],
)
async def hs_metaphysics_practice_mind_and_body(
    raw_request: Request,
    user_id: str = "raymond",
) -> PhilosophyHSEthicsPracticeResponse:
    """
    Canonical HS metaphysics practice: mind–body relationship.
    """
    dilemma_text = (
        "When you think, feel, or imagine something, it seems very different from physical objects like tables or phones. "
        "At the same time, science connects thoughts and feelings to brain activity. Are your mind and your body the same "
        "thing, or is there something about you that is not physical?"
    )

    case_id = "canonical:metaphysics_mind_and_body"

    task = ReasoningTask(
        task_id=case_id,
        natural_language_task=dilemma_text,
        domain_tag="philosophy",
        subdomain_tag="metaphysics",
        given_facts=[],
        assumptions=[],
        constraints=[],
        desired_output_kind=ReasoningTaskKind.ANALYSIS,
        allowed_tools=[
            "philosophy_logic_lesson",
            "philosophy_methods_lesson",
            "philosophy_metaphysics_lesson",
        ],
    )

    core_req = ReasoningCoreRequest(
        task=task,
        max_steps=16,
    )

    try:
        import httpx
    except ImportError:
        httpx = None

    if httpx is None:
        raise HTTPException(
            status_code=500,
            detail="httpx is required for internal reasoning_core call but is not installed.",
        )

    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as http_client:
        response = await http_client.post(
            "/prime/reasoning/core",
            json=core_req.model_dump(),
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"reasoning_core returned {response.status_code}: {response.text}",
            )
        core_resp_data = response.json()

    core_resp = ReasoningCoreResponse(**core_resp_data)

    outcome_quality = (
        ReasoningOutcomeQuality.CAUTIOUS
        if is_high_stakes_task(task)
        else ReasoningOutcomeQuality.UNKNOWN
    )

    entry = ReasoningMemoryEntry(
        id=task.task_id,
        task=task,
        response=core_resp,
        tags=ReasoningTraceTag(
            domain="philosophy",
            subdomain="metaphysics",
            theme=case_id,
            user_label=None,
        ),
        created_at=datetime.utcnow(),
        user_id=user_id,
        outcome_quality=outcome_quality,
    )
    append_memory_entry(entry)

    return PhilosophyHSEthicsPracticeResponse(
        task_id=task.task_id,
        key_conclusions=core_resp.key_conclusions,
        open_questions=core_resp.open_questions,
        outcome_quality=outcome_quality,
    )

class HSDigitalCanonicalDilemma(str, Enum):
    AI_SURVEILLANCE = "ai_surveillance"
    RECOMMENDER_MANIPULATION = "recommender_manipulation"
    MISINFORMATION_AMPLIFICATION = "misinformation_amplification"
    AUTOMATION_JOB_LOSS = "automation_job_loss"


class HSDigitalCanonicalDeepDiveRequest(BaseModel):
    dilemma_id: HSDigitalCanonicalDilemma
    dilemma_text: str | None = None
    context_tags: list[EthicsDigitalContextTag] | None = None


class HSDigitalCanonicalDeepDiveResponse(BaseModel):
    dilemma_id: HSDigitalCanonicalDilemma
    dilemma_text: str
    context_tags: list[EthicsDigitalContextTag] | None
    deep_dive: HSDigitalEthicsDeepDiveResponse

DIGITAL_CANONICAL_TEXT: dict[HSDigitalCanonicalDilemma, str] = {
    HSDigitalCanonicalDilemma.AI_SURVEILLANCE: (
        "Our school wants to use an AI system to watch students on cameras "
        "and flag suspicious behavior automatically."
    ),
    HSDigitalCanonicalDilemma.RECOMMENDER_MANIPULATION: (
        "A social media app uses AI to push content that keeps teens scrolling, "
        "even when it makes them feel worse about themselves."
    ),
    HSDigitalCanonicalDilemma.MISINFORMATION_AMPLIFICATION: (
        "An AI system is very good at recommending news, but sometimes spreads "
        "false stories faster than humans can correct them."
    ),
    HSDigitalCanonicalDilemma.AUTOMATION_JOB_LOSS: (
        "A company wants to replace many workers with AI systems to save money, "
        "even though it will cause big job losses in a small town."
    ),
}

@router.post(
    "/ethics/digital-canonical-deep-dive",
    response_model=HSDigitalCanonicalDeepDiveResponse,
)
async def hs_digital_canonical_deep_dive(
    req: HSDigitalCanonicalDeepDiveRequest,
) -> HSDigitalCanonicalDeepDiveResponse:
    """
    HS digital/AI ethics canonical deep-dive:
    route classic digital dilemmas through Lane 3 + Lane 4 engine.
    """
    base_text = DIGITAL_CANONICAL_TEXT[req.dilemma_id]
    text = (req.dilemma_text or base_text).strip()
    tags = req.context_tags

    deep = await hs_digital_ethics_deep_dive(
        HSDigitalEthicsDeepDiveRequest(
            dilemma_text=text,
            context_tags=tags,
        )
    )

    log_hs_ethics_event(
        {
            "timestamp": datetime.utcnow().isoformat(),
            "endpoint": "hs_digital_canonical_deep_dive",
            "dilemma_id": req.dilemma_id,
            "dilemma_text": text,
            "context_tags": tags,
        }
    )

    return HSDigitalCanonicalDeepDiveResponse(
        dilemma_id=req.dilemma_id,
        dilemma_text=text,
        context_tags=tags,
        deep_dive=deep,
    )

class HSPhilosophyConceptKind(str, Enum):
    THEORY = "theory"
    DOCTRINE = "doctrine"
    DISTINCTION = "distinction"
    PROBLEM = "problem"
    METHOD = "method"


class HSPhilosophyConcept(BaseModel):
    id: str
    label: str
    kind: HSPhilosophyConceptKind
    branch: PhilosophyBranch
    summary: str
    key_claims: list[str]
    supporting_figures: list[str]
    opposing_figures: list[str]
    rival_concepts: list[str]
    classic_challenges: list[str]

@router.get(
    "/lane2/concepts/overview",
    response_model=list[HSPhilosophyConcept],
    name="philosophy_hs_concepts_overview",
)
async def hs_concepts_overview() -> list[HSPhilosophyConcept]:
    return [
        HSPhilosophyConcept(
            id="ethics.concept.utilitarianism",
            label="Utilitarianism",
            kind=HSPhilosophyConceptKind.THEORY,
            branch=PhilosophyBranch.ETHICS,
            summary=(
                "An outcome-focused ethical theory that judges actions chiefly "
                "by their overall consequences for well-being."
            ),
            key_claims=[
                "The morally right action is the one that produces the best overall balance of good over harm.",
                "Each person's welfare counts equally in the calculation.",
            ],
            supporting_figures=["Bentham", "Mill"],
            opposing_figures=["Kant"],
            rival_concepts=[
                "ethics.concept.kantian_deontology",
                "ethics.concept.virtue_ethics",
            ],
            classic_challenges=[
                "Can seem to justify harming a few if it greatly benefits many.",
                "Requires predicting complex consequences that are often uncertain.",
            ],
        ),
        HSPhilosophyConcept(
            id="ethics.concept.kantian_deontology",
            label="Kantian Deontology",
            kind=HSPhilosophyConceptKind.THEORY,
            branch=PhilosophyBranch.ETHICS,
            summary=(
                "A duty- and rule-focused ethical theory that judges actions by whether "
                "they respect universalizable duties and treat persons as ends."
            ),
            key_claims=[
                "Some actions are wrong in themselves, regardless of consequences.",
                "We must treat persons as ends in themselves, never merely as means.",
            ],
            supporting_figures=["Kant"],
            opposing_figures=["Bentham", "Mill"],
            rival_concepts=[
                "ethics.concept.utilitarianism",
                "ethics.concept.virtue_ethics",
            ],
            classic_challenges=[
                "Can seem too rigid in extreme cases, such as lying to prevent serious harm.",
                "Struggles with conflicts between duties, like promise-keeping versus preventing harm.",
            ],
        ),
        HSPhilosophyConcept(
            id="ethics.concept.virtue_ethics",
            label="Virtue Ethics",
            kind=HSPhilosophyConceptKind.THEORY,
            branch=PhilosophyBranch.ETHICS,
            summary=(
                "An approach that focuses on character and virtues rather than only rules or outcomes."
            ),
            key_claims=[
                "Ethics is about becoming a certain kind of person, not just making isolated choices.",
                "Virtues like honesty, courage, and justice guide good action over a whole life.",
            ],
            supporting_figures=["Aristotle"],
            opposing_figures=["Bentham", "Kant"],
            rival_concepts=[
                "ethics.concept.utilitarianism",
                "ethics.concept.kantian_deontology",
            ],
            classic_challenges=[
                "Sometimes gives less precise guidance for one-off hard cases.",
                "Different cultures may interpret the same virtue in conflicting ways.",
            ],
        ),
        HSPhilosophyConcept(
            id="ethics.concept.care_ethics",
            label="Care Ethics",
            kind=HSPhilosophyConceptKind.THEORY,
            branch=PhilosophyBranch.ETHICS,
            summary=(
                "A relational approach that centers care, vulnerability, and concrete relationships."
            ),
            key_claims=[
                "Moral life is rooted in networks of care and dependency, not just abstract individuals.",
                "We must attend closely to vulnerability, power, and particular relationships.",
            ],
            supporting_figures=["Gilligan", "Noddings"],
            opposing_figures=["Rawls"],
            rival_concepts=[
                "ethics.concept.utilitarianism",
                "ethics.concept.kantian_deontology",
            ],
            classic_challenges=[
                "Risk of favoritism toward close relationships over impartial fairness.",
                "Needs safeguards so care does not become paternalistic or controlling.",
            ],
        ),
        HSPhilosophyConcept(
            id="ethics.concept.moral_relativism",
            label="Moral Relativism",
            kind=HSPhilosophyConceptKind.THEORY,
            branch=PhilosophyBranch.ETHICS,
            summary=(
                "The view that what is morally right or wrong is relative to "
                "cultures, societies, or individuals, rather than objectively true for everyone."
            ),
            key_claims=[
                "Different cultures and times have genuinely different moral codes.",
                "There is no single, culture-independent fact about what is morally right.",
            ],
            supporting_figures=["Harman"],
            opposing_figures=["Nagel"],
            rival_concepts=[
                "ethics.concept.moral_realism",
            ],
            classic_challenges=[
                "Struggles to condemn practices that seem clearly wrong, even if locally accepted.",
                "Makes moral disagreement look like mere difference, not real conflict about truth.",
            ],
        ),
        HSPhilosophyConcept(
            id="ethics.concept.moral_realism",
            label="Moral Realism",
            kind=HSPhilosophyConceptKind.THEORY,
            branch=PhilosophyBranch.ETHICS,
            summary=(
                "The view that there are objective moral facts or truths, "
                "independent of what any person or culture thinks."
            ),
            key_claims=[
                "Some moral claims are true or false, not just expressions of feeling or custom.",
                "Moral disagreement can be about facts, not only attitudes.",
            ],
            supporting_figures=["Moore"],
            opposing_figures=["Mackie"],
            rival_concepts=[
                "ethics.concept.moral_relativism",
            ],
            classic_challenges=[
                "Hard to explain what kind of facts moral facts are and how we know them.",
                "Faces the 'queerness' objection that moral properties are metaphysically strange.",
            ],
        ),
        HSPhilosophyConcept(
            id="metaphysics.concept.mind_body_dualism",
            label="Mind–Body Dualism",
            kind=HSPhilosophyConceptKind.THEORY,
            branch=PhilosophyBranch.METAPHYSICS,
            summary=(
                "The view that mind and body are fundamentally different kinds of thing, "
                "often immaterial mind versus material body."
            ),
            key_claims=[
                "Consciousness and thought cannot be reduced to purely physical processes.",
                "A person is not identical to their body alone.",
            ],
            supporting_figures=["Descartes"],
            opposing_figures=["Ryle"],
            rival_concepts=[
                "metaphysics.concept.physicalism",
            ],
            classic_challenges=[
                "Explaining how an immaterial mind can causally interact with a material body.",
                "Accounting for neuroscientific evidence linking mind and brain.",
            ],
        ),
        HSPhilosophyConcept(
            id="metaphysics.concept.physicalism",
            label="Physicalism",
            kind=HSPhilosophyConceptKind.THEORY,
            branch=PhilosophyBranch.METAPHYSICS,
            summary=(
                "The view that everything that exists is ultimately physical, "
                "or depends entirely on the physical."
            ),
            key_claims=[
                "Mental states are either identical to, or fully grounded in, physical states.",
                "There are no non-physical substances like souls or Cartesian minds.",
            ],
            supporting_figures=["Smart", "Lewis"],
            opposing_figures=["Descartes", "Chalmers"],
            rival_concepts=[
                "metaphysics.concept.mind_body_dualism",
            ],
            classic_challenges=[
                "Difficulties explaining conscious experience (the 'hard problem').",
                "Thought experiments like zombies that challenge reduction.",
            ],
        ),
        HSPhilosophyConcept(
            id="epistemology.concept.skepticism",
            label="Skepticism about Knowledge",
            kind=HSPhilosophyConceptKind.PROBLEM,
            branch=PhilosophyBranch.EPISTEMOLOGY,
            summary=(
                "A family of doubts about whether we can really know much, or anything, "
                "about the external world, other minds, or the future."
            ),
            key_claims=[
                "Our senses and reasoning can mislead us in systematic ways.",
                "Any justification we give seems to invite a further 'why believe that?' question.",
            ],
            supporting_figures=["Pyrrho"],
            opposing_figures=["Descartes", "Moore"],
            rival_concepts=[
                "epistemology.concept.fallibilism",
            ],
            classic_challenges=[
                "If taken strictly, it seems to undermine everyday and scientific knowledge.",
                "Hard to live consistently as a complete skeptic in ordinary life.",
            ],
        ),
        HSPhilosophyConcept(
            id="epistemology.concept.fallibilism",
            label="Fallibilism",
            kind=HSPhilosophyConceptKind.DOCTRINE,
            branch=PhilosophyBranch.EPISTEMOLOGY,
            summary=(
                "The view that we can have knowledge or justified belief even though "
                "our beliefs could turn out to be mistaken."
            ),
            key_claims=[
                "Certainty is not required for knowledge.",
                "Good evidence can still support belief despite small residual doubts.",
            ],
            supporting_figures=["Peirce"],
            opposing_figures=["strong_skeptics"],
            rival_concepts=[
                "epistemology.concept.skepticism",
            ],
            classic_challenges=[
                "Clarifying how much risk of error is compatible with knowledge.",
                "Handling skeptical arguments without simply ignoring them.",
            ],
        ),
        HSPhilosophyConcept(
            id="logic.concept.argument_vs_assertion",
            label="Argument vs Assertion",
            kind=HSPhilosophyConceptKind.DISTINCTION,
            branch=PhilosophyBranch.LOGIC,
            summary=(
                "The distinction between merely stating something and giving reasons "
                "that support a conclusion."
            ),
            key_claims=[
                "An assertion simply states a claim; an argument offers premises that support a conclusion.",
                "Good philosophical work makes arguments rather than just stating opinions.",
            ],
            supporting_figures=["general_logic_tradition"],
            opposing_figures=[],
            rival_concepts=[],
            classic_challenges=[
                "Recognizing when reasons are only repeating the conclusion in different words.",
                "Separating emotional reactions from actual supporting reasons.",
            ],
        ),
        HSPhilosophyConcept(
            id="logic.concept.validity_and_soundness",
            label="Validity and Soundness",
            kind=HSPhilosophyConceptKind.DISTINCTION,
            branch=PhilosophyBranch.LOGIC,
            summary=(
                "A valid argument is one where the conclusion would have to be true if the premises are true; "
                "a sound argument is valid and has actually true premises."
            ),
            key_claims=[
                "Validity is about structure, not about whether the premises are in fact true.",
                "Soundness requires both validity and true premises.",
            ],
            supporting_figures=["Frege"],
            opposing_figures=[],
            rival_concepts=[],
            classic_challenges=[
                "People often treat a persuasive but invalid argument as if it were sound.",
                "Evaluating premises can be harder than checking validity.",
            ],
        ),
        HSPhilosophyConcept(
            id="logic.concept.common_fallacies",
            label="Common Fallacies",
            kind=HSPhilosophyConceptKind.METHOD,
            branch=PhilosophyBranch.LOGIC,
            summary=(
                "Patterns of bad reasoning that often feel convincing, such as ad hominem, straw man, and slippery slope."
            ),
            key_claims=[
                "Fallacies can mislead even when premises seem plausible.",
                "Learning fallacies helps you both spot and avoid weak arguments.",
            ],
            supporting_figures=["informal_logic_tradition"],
            opposing_figures=[],
            rival_concepts=[],
            classic_challenges=[
                "Overusing 'that’s a fallacy' as a way to dismiss arguments without engaging them.",
                "Some patterns can be fallacious in one context and reasonable in another.",
            ],
        ),
        HSPhilosophyConcept(
            id="metaphysics.concept.personal_identity_psychological",
            label="Personal Identity: Psychological View",
            kind=HSPhilosophyConceptKind.THEORY,
            branch=PhilosophyBranch.METAPHYSICS,
            summary=(
                "The view that what makes you the same person over time is continuity of memory, character, or psychology."
            ),
            key_claims=[
                "If you can remember doing it, or your character grows out of it, it was you.",
                "Body changes matter less than psychological connections.",
            ],
            supporting_figures=["Locke"],
            opposing_figures=["bodily_identity_theorists"],
            rival_concepts=[
                "metaphysics.concept.personal_identity_bodily",
            ],
            classic_challenges=[
                "What about forgotten experiences or radical psychological change?",
                "Thought experiments where psychology splits (teleportation, brain copying).",
            ],
        ),
        HSPhilosophyConcept(
            id="metaphysics.concept.personal_identity_bodily",
            label="Personal Identity: Bodily View",
            kind=HSPhilosophyConceptKind.THEORY,
            branch=PhilosophyBranch.METAPHYSICS,
            summary=(
                "The view that personal identity over time is grounded mainly in the persistence of the living human body."
            ),
            key_claims=[
                "You remain the same person as long as your biological organism continues.",
                "Body continuity anchors identity through large psychological changes.",
            ],
            supporting_figures=["animalism_tradition"],
            opposing_figures=["Locke"],
            rival_concepts=[
                "metaphysics.concept.personal_identity_psychological",
            ],
            classic_challenges=[
                "Cases where one body supports two streams of consciousness.",
                "Intuitions that identity follows mind, not body, in some scenarios.",
            ],
        ),
        HSPhilosophyConcept(
            id="metaphysics.concept.free_will_vs_determinism",
            label="Free Will vs Determinism",
            kind=HSPhilosophyConceptKind.PROBLEM,
            branch=PhilosophyBranch.METAPHYSICS,
            summary=(
                "The tension between the idea that our choices are free and the idea that every event has determining causes."
            ),
            key_claims=[
                "If determinism is true, every choice seems fully fixed by prior states and laws.",
                "Many people feel they are genuinely able to choose among alternatives.",
            ],
            supporting_figures=["Hume", "Peirce"],
            opposing_figures=["hard_determinists"],
            rival_concepts=[
                "metaphysics.concept.hard_determinism",
                "metaphysics.concept.libertarian_free_will",
            ],
            classic_challenges=[
                "Clarifying whether freedom requires being able to do otherwise.",
                "Explaining responsibility if our actions are fully caused.",
            ],
        ),
        HSPhilosophyConcept(
            id="political.concept.social_contract",
            label="Social Contract",
            kind=HSPhilosophyConceptKind.THEORY,
            branch=PhilosophyBranch.POLITICAL,
            summary=(
                "The idea that political authority and obligation arise from some form of agreement "
                "among free and equal persons."
            ),
            key_claims=[
                "Legitimate government is grounded in the consent, actual or hypothetical, of the governed.",
                "People leave a 'state of nature' to secure rights or common goods.",
            ],
            supporting_figures=["Hobbes", "Locke", "Rousseau"],
            opposing_figures=["Marx"],
            rival_concepts=[
                "political.concept.utilitarian_justification",
            ],
            classic_challenges=[
                "Real people rarely sign an explicit contract.",
                "Questions about whose consent counts in unjust historical conditions.",
            ],
        ),
        HSPhilosophyConcept(
            id="political.concept_rawlsian_justice",
            label="Rawlsian Justice as Fairness",
            kind=HSPhilosophyConceptKind.THEORY,
            branch=PhilosophyBranch.POLITICAL,
            summary=(
                "A view that just principles are those free and equal people would choose behind a veil of ignorance "
                "about their own place in society."
            ),
            key_claims=[
                "Basic liberties should be equal for all.",
                "Social and economic inequalities are acceptable only if they benefit the least advantaged.",
            ],
            supporting_figures=["Rawls"],
            opposing_figures=["Nozick"],
            rival_concepts=[
                "political.concept_libertarianism",
            ],
            classic_challenges=[
                "Debates about whether the difference principle is too demanding.",
                "Libertarian worries about redistribution and individual rights.",
            ],
        ),
        HSPhilosophyConcept(
            id="political.concept_libertarianism",
            label="Libertarianism",
            kind=HSPhilosophyConceptKind.THEORY,
            branch=PhilosophyBranch.POLITICAL,
            summary=(
                "A family of views that give strong priority to individual liberty and property rights, "
                "often favoring minimal state intervention."
            ),
            key_claims=[
                "People have robust rights over themselves and their holdings.",
                "Redistributive taxation can be seen as a form of coercion or taking.",
            ],
            supporting_figures=["Nozick"],
            opposing_figures=["Rawls"],
            rival_concepts=[
                "political.concept_rawlsian_justice",
            ],
            classic_challenges=[
                "Explaining how to handle historical injustices and unequal starting points.",
                "Tensions between unregulated markets and fair opportunity for all.",
            ],
        ),
        HSPhilosophyConcept(
            id="religion.concept_cosmological_argument",
            label="Cosmological Argument",
            kind=HSPhilosophyConceptKind.THEORY,
            branch=PhilosophyBranch.OTHER,
            summary=(
                "An argument for the existence of God that begins from the existence or features of the world "
                "and infers a necessary first cause or sufficient reason."
            ),
            key_claims=[
                "Contingent things require an explanation beyond themselves.",
                "There cannot be an infinite regress of explanations.",
            ],
            supporting_figures=["Aquinas", "Leibniz"],
            opposing_figures=["Hume", "Kant"],
            rival_concepts=[
                "religion.concept_atheistic_explanation",
            ],
            classic_challenges=[
                "Whether an infinite regress is really impossible or problematic.",
                "Whether a first cause must have the attributes of a theistic God.",
            ],
        ),
        HSPhilosophyConcept(
            id="religion.concept_problem_of_evil",
            label="Problem of Evil",
            kind=HSPhilosophyConceptKind.PROBLEM,
            branch=PhilosophyBranch.OTHER,
            summary=(
                "The challenge of reconciling the existence of a good, powerful God with the reality of suffering and evil."
            ),
            key_claims=[
                "If God is all-good and all-powerful, it is hard to see why there is so much apparently pointless suffering.",
                "Different responses try to show hidden reasons or limits on what God can do.",
            ],
            supporting_figures=["atheist_critics"],
            opposing_figures=["theodicy_traditions"],
            rival_concepts=[],
            classic_challenges=[
                "Distinguishing logical from evidential versions of the problem.",
                "Explaining horrendous evils without trivializing suffering.",
            ],
        ),
        HSPhilosophyConcept(
            id="aesthetics.concept_art_as_representation",
            label="Art as Representation",
            kind=HSPhilosophyConceptKind.THEORY,
            branch=PhilosophyBranch.AESTHETICS,
            summary=(
                "The view that art is centrally about representing or imitating reality, "
                "as in painting, drama, or narrative."
            ),
            key_claims=[
                "Artworks often depict people, events, or possibilities in a meaningful way.",
                "Understanding representation helps explain realism, symbolism, and style.",
            ],
            supporting_figures=["Plato", "Aristotle"],
            opposing_figures=["avant_garde_theorists"],
            rival_concepts=[
                "aesthetics.concept_art_as_expression",
            ],
            classic_challenges=[
                "Abstract and non-representational art that seems not to depict anything.",
                "Artworks that are more about concepts or experiences than imitation.",
            ],
        ),
        HSPhilosophyConcept(
            id="aesthetics.concept_art_as_expression",
            label="Art as Expression",
            kind=HSPhilosophyConceptKind.THEORY,
            branch=PhilosophyBranch.AESTHETICS,
            summary=(
                "The view that art is fundamentally about expressing emotion, experience, or inner life."
            ),
            key_claims=[
                "Art can make feelings and perspectives communicable and shareable.",
                "Expression can be in tension with strict realism or representation.",
            ],
            supporting_figures=["Tolstoy", "Collingwood"],
            opposing_figures=["formalists"],
            rival_concepts=[
                "aesthetics.concept_art_as_representation",
            ],
            classic_challenges=[
                "Explaining works that seem emotionally opaque or purely formal.",
                "Cases where artists deny having any particular emotion to express.",
            ],
        ),
    ]

@router.post(
    "/religion/practice/arguments_for_and_against_god",
    response_model=PhilosophyHSEthicsPracticeResponse,
    tags=["philosophy-hs-religion"],
)
async def hs_religion_practice_arguments_for_and_against_god(
    raw_request: Request,
    user_id: str = "raymond",
) -> PhilosophyHSEthicsPracticeResponse:
    """
    HS philosophy of religion: practice weighing major arguments for and against the existence of God.
    Framed descriptively, not devotionally, suitable for teaching about religion in a neutral way.
    """
    dilemma_text = (
        "In philosophy and religion classes, students encounter classic arguments that claim to show "
        "that God exists (for example, based on design, morality, or the existence of the universe), "
        "as well as classic arguments that claim to show that God does not exist or that belief in God "
        "is not reasonable. How should someone fairly weigh arguments for and against the existence "
        "of God, and what does it mean to evaluate them using reasons rather than just personal habit "
        "or authority?"
    )

    case_id = "canonical:religion_arguments_for_and_against_god"

    task = ReasoningTask(
        task_id=case_id,
        natural_language_task=dilemma_text,
        domain_tag="philosophy",
        subdomain_tag="religion",
        given_facts=[],
        assumptions=[],
        constraints=[],
        desired_output_kind=ReasoningTaskKind.ANALYSIS,
        allowed_tools=[
            "philosophy_logic_lesson",
            "philosophy_methods_lesson",
            "philosophy_metaphysics_lesson",
        ],
    )

    core_req = ReasoningCoreRequest(
        task=task,
        max_steps=16,
    )

    import httpx

    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as http_client:
        response = await http_client.post(
            "/prime/reasoning/core",
            json=core_req.model_dump(),
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"reasoning_core returned {response.status_code}: {response.text}",
            )
        core_resp_data = response.json()

    core_resp = ReasoningCoreResponse(**core_resp_data)

    outcome_quality = (
        ReasoningOutcomeQuality.CAUTIOUS
        if is_high_stakes_task(task)
        else ReasoningOutcomeQuality.UNKNOWN
    )

    entry = ReasoningMemoryEntry(
        id=task.task_id,
        task=task,
        response=core_resp,
        tags=ReasoningTraceTag(
            domain="philosophy",
            subdomain="religion",
            theme=case_id,
            user_label=None,
        ),
        created_at=datetime.utcnow(),
        user_id=user_id,
        outcome_quality=outcome_quality,
    )
    append_memory_entry(entry)

    return PhilosophyHSEthicsPracticeResponse(
        task_id=task.task_id,
        key_conclusions=core_resp.key_conclusions,
        open_questions=core_resp.open_questions,
        outcome_quality=outcome_quality,
    )

@router.post(
    "/religion/practice/faith_and_reason",
    response_model=PhilosophyHSEthicsPracticeResponse,
    tags=["philosophy-hs-religion"],
)
async def hs_religion_practice_faith_and_reason(
    raw_request: Request,
    user_id: str = "raymond",
) -> PhilosophyHSEthicsPracticeResponse:
    """
    HS philosophy of religion: practice thinking about how faith and reason can relate.
    Neutral framing suitable for a public-school context.
    """
    dilemma_text = (
        "Some people say that religious faith should go beyond evidence and arguments, while others say "
        "that beliefs about God or the ultimate meaning of life should be supported by reasons just like "
        "other important beliefs. A person might trust a religious tradition, have personal experiences, "
        "and also care about scientific and historical evidence. How can someone think carefully about "
        "the relationship between faith and reason without simply dismissing either side?"
    )

    case_id = "canonical:religion_faith_and_reason"

    task = ReasoningTask(
        task_id=case_id,
        natural_language_task=dilemma_text,
        domain_tag="philosophy",
        subdomain_tag="religion",
        given_facts=[],
        assumptions=[],
        constraints=[],
        desired_output_kind=ReasoningTaskKind.ANALYSIS,
        allowed_tools=[
            "philosophy_logic_lesson",
            "philosophy_methods_lesson",
            "philosophy_metaphysics_lesson",
        ],
    )

    core_req = ReasoningCoreRequest(
        task=task,
        max_steps=16,
    )

    import httpx

    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as http_client:
        response = await http_client.post(
            "/prime/reasoning/core",
            json=core_req.model_dump(),
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"reasoning_core returned {response.status_code}: {response.text}",
            )
        core_resp_data = response.json()

    core_resp = ReasoningCoreResponse(**core_resp_data)

    outcome_quality = (
        ReasoningOutcomeQuality.CAUTIOUS
        if is_high_stakes_task(task)
        else ReasoningOutcomeQuality.UNKNOWN
    )

    entry = ReasoningMemoryEntry(
        id=task.task_id,
        task=task,
        response=core_resp,
        tags=ReasoningTraceTag(
            domain="philosophy",
            subdomain="religion",
            theme=case_id,
            user_label=None,
        ),
        created_at=datetime.utcnow(),
        user_id=user_id,
        outcome_quality=outcome_quality,
    )
    append_memory_entry(entry)

    return PhilosophyHSEthicsPracticeResponse(
        task_id=task.task_id,
        key_conclusions=core_resp.key_conclusions,
        open_questions=core_resp.open_questions,
        outcome_quality=outcome_quality,
    )

@router.post(
    "/religion/practice/religious_pluralism",
    response_model=PhilosophyHSEthicsPracticeResponse,
    tags=["philosophy-hs-religion"],
)
async def hs_religion_practice_religious_pluralism(
    raw_request: Request,
    user_id: str = "raymond",
) -> PhilosophyHSEthicsPracticeResponse:
    """
    HS philosophy of religion: practice thinking about religious pluralism.
    Focus on understanding and reasons, not promoting or attacking any tradition.
    """
    dilemma_text = (
        "In many schools and communities, students meet people from different religious and non-religious "
        "backgrounds who have conflicting beliefs about God, salvation, and the meaning of life. Some say "
        "only one religion can be fully true others say many paths might lead to the same ultimate reality "
        "or that no single tradition has the whole picture. In a pluralistic society, how should someone "
        "think about religious disagreement and pluralism while still taking truth and other people's "
        "deep commitments seriously?"
    )

    case_id = "canonical:religion_religious_pluralism"

    task = ReasoningTask(
        task_id=case_id,
        natural_language_task=dilemma_text,
        domain_tag="philosophy",
        subdomain_tag="religion",
        given_facts=[],
        assumptions=[],
        constraints=[],
        desired_output_kind=ReasoningTaskKind.ANALYSIS,
        allowed_tools=[
            "philosophy_logic_lesson",
            "philosophy_methods_lesson",
            "philosophy_metaphysics_lesson",
        ],
    )

    core_req = ReasoningCoreRequest(
        task=task,
        max_steps=16,
    )

    import httpx

    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as http_client:
        response = await http_client.post(
            "/prime/reasoning/core",
            json=core_req.model_dump(),
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"reasoning_core returned {response.status_code}: {response.text}",
            )
        core_resp_data = response.json()

    core_resp = ReasoningCoreResponse(**core_resp_data)

    outcome_quality = (
        ReasoningOutcomeQuality.CAUTIOUS
        if is_high_stakes_task(task)
        else ReasoningOutcomeQuality.UNKNOWN
    )

    entry = ReasoningMemoryEntry(
        id=task.task_id,
        task=task,
        response=core_resp,
        tags=ReasoningTraceTag(
            domain="philosophy",
            subdomain="religion",
            theme=case_id,
            user_label=None,
        ),
        created_at=datetime.utcnow(),
        user_id=user_id,
        outcome_quality=outcome_quality,
    )
    append_memory_entry(entry)

    return PhilosophyHSEthicsPracticeResponse(
        task_id=task.task_id,
        key_conclusions=core_resp.key_conclusions,
        open_questions=core_resp.open_questions,
        outcome_quality=outcome_quality,
    )

@router.post(
    "/aesthetics/practice/what_counts_as_art",
    response_model=PhilosophyHSEthicsPracticeResponse,
    tags=["philosophy-hs-aesthetics"],
)
async def hs_aesthetics_practice_what_counts_as_art(
    raw_request: Request,
    user_id: str = "raymond",
) -> PhilosophyHSEthicsPracticeResponse:
    """
    HS aesthetics practice: what counts as art?
    Neutral, HS-level question about definitions and criteria.
    """
    dilemma_text = (
        "Imagine you see an ordinary-looking object, like a chair or a pile of bricks, displayed in a museum "
        "as a work of art. The same kind of object at home or on the street would not be treated as art at all. "
        "Some people say that anything can be art if an artist or the art world presents it that way. Others say "
        "there must be something special about the object itself, its form, or the feelings it expresses. "
        "What should count as art, and what kinds of reasons or criteria could someone use to draw that line?"
    )

    case_id = "canonical:aesthetics_what_counts_as_art"

    task = ReasoningTask(
        task_id=case_id,
        natural_language_task=dilemma_text,
        domain_tag="philosophy",
        subdomain_tag="aesthetics",
        given_facts=[],
        assumptions=[],
        constraints=[],
        desired_output_kind=ReasoningTaskKind.ANALYSIS,
        allowed_tools=[
            "philosophy_logic_lesson",
            "philosophy_methods_lesson",
        ],
    )

    core_req = ReasoningCoreRequest(
        task=task,
        max_steps=16,
    )

    import httpx

    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as http_client:
        response = await http_client.post(
            "/prime/reasoning/core",
            json=core_req.model_dump(),
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"reasoning_core returned {response.status_code}: {response.text}",
            )
        core_resp = ReasoningCoreResponse(**response.json())

    outcome_quality = (
        ReasoningOutcomeQuality.CAUTIOUS
        if is_high_stakes_task(task)
        else ReasoningOutcomeQuality.UNKNOWN
    )

    entry = ReasoningMemoryEntry(
        id=task.task_id,
        task=task,
        response=core_resp,
        tags=ReasoningTraceTag(
            domain="philosophy",
            subdomain="aesthetics",
            theme=case_id,
            user_label=None,
        ),
        created_at=datetime.utcnow(),
        user_id=user_id,
        outcome_quality=outcome_quality,
    )
    append_memory_entry(entry)

    return PhilosophyHSEthicsPracticeResponse(
        task_id=task.task_id,
        key_conclusions=core_resp.key_conclusions,
        open_questions=core_resp.open_questions,
        outcome_quality=outcome_quality,
    )

@router.post(
    "/aesthetics/practice/beauty_eye_of_beholder",
    response_model=PhilosophyHSEthicsPracticeResponse,
    tags=["philosophy-hs-aesthetics"],
)
async def hs_aesthetics_practice_beauty_eye_of_beholder(
    raw_request: Request,
    user_id: str = "raymond",
) -> PhilosophyHSEthicsPracticeResponse:
    """
    HS aesthetics practice: is beauty purely subjective or is there more to it?
    """
    dilemma_text = (
        "People often say that 'beauty is in the eye of the beholder' to mean that everyone has their own "
        "taste and there is no point arguing about beauty. But others think there are at least some shared "
        "standards for beauty in art, nature, or design, and that some judgments of beauty can be more "
        "reasonable than others. Is beauty simply a matter of personal opinion, or is there something more "
        "objective about it, and how could someone tell the difference?"
    )

    case_id = "canonical:aesthetics_beauty_eye_of_beholder"

    task = ReasoningTask(
        task_id=case_id,
        natural_language_task=dilemma_text,
        domain_tag="philosophy",
        subdomain_tag="aesthetics",
        given_facts=[],
        assumptions=[],
        constraints=[],
        desired_output_kind=ReasoningTaskKind.ANALYSIS,
        allowed_tools=[
            "philosophy_logic_lesson",
            "philosophy_methods_lesson",
        ],
    )

    core_req = ReasoningCoreRequest(
        task=task,
        max_steps=16,
    )

    import httpx

    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as http_client:
        response = await http_client.post(
            "/prime/reasoning/core",
            json=core_req.model_dump(),
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"reasoning_core returned {response.status_code}: {response.text}",
            )
        core_resp = ReasoningCoreResponse(**response.json())

    outcome_quality = (
        ReasoningOutcomeQuality.CAUTIOUS
        if is_high_stakes_task(task)
        else ReasoningOutcomeQuality.UNKNOWN
    )

    entry = ReasoningMemoryEntry(
        id=task.task_id,
        task=task,
        response=core_resp,
        tags=ReasoningTraceTag(
            domain="philosophy",
            subdomain="aesthetics",
            theme=case_id,
            user_label=None,
        ),
        created_at=datetime.utcnow(),
        user_id=user_id,
        outcome_quality=outcome_quality,
    )
    append_memory_entry(entry)

    return PhilosophyHSEthicsPracticeResponse(
        task_id=task.task_id,
        key_conclusions=core_resp.key_conclusions,
        open_questions=core_resp.open_questions,
        outcome_quality=outcome_quality,
    )

@router.post(
    "/aesthetics/practice/objective_meaning_in_art",
    response_model=PhilosophyHSEthicsPracticeResponse,
    tags=["philosophy-hs-aesthetics"],
)
async def hs_aesthetics_practice_objective_meaning_in_art(
    raw_request: Request,
    user_id: str = "raymond",
) -> PhilosophyHSEthicsPracticeResponse:
    """
    HS aesthetics practice: objective meaning vs pure interpretation in art.
    """
    dilemma_text = (
        "When people discuss a movie, song, poem, or painting, they often disagree about what it 'really' "
        "means. Some say that only the artist's intention decides the true meaning, others think that any "
        "interpretation is acceptable as long as someone finds it meaningful, and still others think there "
        "are better and worse readings based on the work itself and its context. Do stories, music, and "
        "images have any objective meaning, or is it all interpretation, and what would count as a good "
        "reason for preferring one interpretation over another?"
    )

    case_id = "canonical:aesthetics_objective_meaning_in_art"

    task = ReasoningTask(
        task_id=case_id,
        natural_language_task=dilemma_text,
        domain_tag="philosophy",
        subdomain_tag="aesthetics",
        given_facts=[],
        assumptions=[],
        constraints=[],
        desired_output_kind=ReasoningTaskKind.ANALYSIS,
        allowed_tools=[
            "philosophy_logic_lesson",
            "philosophy_methods_lesson",
        ],
    )

    core_req = ReasoningCoreRequest(
        task=task,
        max_steps=16,
    )

    import httpx

    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as http_client:
        response = await http_client.post(
            "/prime/reasoning/core",
            json=core_req.model_dump(),
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"reasoning_core returned {response.status_code}: {response.text}",
            )
        core_resp = ReasoningCoreResponse(**response.json())

    outcome_quality = (
        ReasoningOutcomeQuality.CAUTIOUS
        if is_high_stakes_task(task)
        else ReasoningOutcomeQuality.UNKNOWN
    )

    entry = ReasoningMemoryEntry(
        id=task.task_id,
        task=task,
        response=core_resp,
        tags=ReasoningTraceTag(
            domain="philosophy",
            subdomain="aesthetics",
            theme=case_id,
            user_label=None,
        ),
        created_at=datetime.utcnow(),
        user_id=user_id,
        outcome_quality=outcome_quality,
    )
    append_memory_entry(entry)

    return PhilosophyHSEthicsPracticeResponse(
        task_id=task.task_id,
        key_conclusions=core_resp.key_conclusions,
        open_questions=core_resp.open_questions,
        outcome_quality=outcome_quality,
    )

@router.post(
    "/history/practice/ancient_vs_earlymodern_epistemology",
    response_model=HSHistoryPracticeWithRubricResponse,
    tags=["philosophy-hs-history"],
)
async def hs_history_practice_ancient_vs_earlymodern_epistemology(
    raw_request: Request,
    user_id: str = "raymond",
    run_rubric: bool = False,
) -> HSHistoryPracticeWithRubricResponse:
    """
    PRIME practice: compare ancient Greek and early modern views on knowledge and reason.
    """

    dilemma_text = (
        "Ancient Greek philosophers such as Plato and Aristotle asked what knowledge is and how it "
        "differs from opinion, often linking knowledge to virtue and the good life. Early modern "
        "philosophers such as Descartes, Locke, and Hume revisited questions about certainty, "
        "experience, and the foundations of science in a new scientific and religious context. "
        "Compare how ancient Greek and early modern thinkers understand what knowledge is, where it "
        "comes from, and why it matters. What deep similarities and differences in their pictures of "
        "the knower and the world should PRIME keep track of?"
    )

    case_id = "canonical:history_ancient_vs_earlymodern_epistemology"

    task = ReasoningTask(
        task_id=f"hs_history_ancient_vs_earlymodern_epistemology_{datetime.utcnow().isoformat()}",
        kind=ReasoningTaskKind.ANALYSIS,
        natural_language_task=dilemma_text,
        domain_tag="philosophy",
        subdomain_tag="history",
        difficulty=DifficultyLevel.INTERMEDIATE,
        context_tags=[case_id],
        theme="hs.history.ancient_vs_earlymodern_epistemology",
        tools_allowed=[
            "philosophy_history_lesson",
            "philosophy_methods_lesson",
        ],
    )

    core_req = ReasoningCoreRequest(
        user_id=user_id,
        task=task,
        high_stakes=is_high_stakes_task(task),
    )

    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as http_client:
        core_resp_raw = await http_client.post(
            "/prime/reasoning/core",
            json=core_req.model_dump(mode="json"),
        )
        if core_resp_raw.status_code != 200:
            raise HTTPException(
                status_code=core_resp_raw.status_code,
                detail=f"Reasoning core error: {core_resp_raw.text}",
            )
        core_resp_data = core_resp_raw.json()

    core_resp = ReasoningCoreResponse(**core_resp_data)

    outcome_quality = ReasoningOutcomeQuality.GOOD

    rubric_result: PhilosophyRubricEvaluateResponse | None = None

    if run_rubric:
        synthesized_answer = " ".join(core_resp.key_conclusions or [])
        rubric_req = PhilosophyRubricEvaluateRequest(
            question=dilemma_text,
            answer=synthesized_answer,
            context="hs.history",
        )

        async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as http_client:
            rubric_resp_raw = await http_client.post(
                "/prime/humanities/philosophy/rubric/evaluate-answer",
                json=rubric_req.model_dump(mode="json"),
            )
            if rubric_resp_raw.status_code == 200:
                rubric_result = PhilosophyRubricEvaluateResponse(
                    **rubric_resp_raw.json()
                )

    memory_entry = ReasoningMemoryEntry(
        id=task.task_id,
        task=task,
        response=core_resp,
        tags=ReasoningTraceTag(
            domain="philosophy",
            subdomain="history",
            level="hs",
            theme="hs.history.ancient_vs_earlymodern_epistemology",
        ),
        created_at=datetime.utcnow(),
        user_id=user_id,
        outcome_quality=outcome_quality,
        rubric_scores=rubric_result.scores if rubric_result else None,
        rubric_overall_comment=rubric_result.overall_comment if rubric_result else None,
    )
    append_memory_entry(memory_entry)

    return HSHistoryPracticeWithRubricResponse(
        task_id=task.task_id,
        key_conclusions=core_resp.key_conclusions,
        open_questions=core_resp.open_questions,
        outcome_quality=outcome_quality,
        rubric=rubric_result,
    )

@router.post(
    "/history/practice/medieval_vs_modern_faith_reason",
    response_model=HSHistoryPracticeWithRubricResponse,
    tags=["philosophy-hs-history"],
)
async def hs_history_practice_medieval_vs_modern_faith_reason(
    raw_request: Request,
    user_id: str = "raymond",
    run_rubric: bool = False,
) -> HSHistoryPracticeWithRubricResponse:
    """
    PRIME practice: compare medieval Christian/Islamic/Jewish faith–reason debates with modern secular views.
    """

    dilemma_text = (
        "Medieval Christian, Islamic, and Jewish philosophers tried to reconcile faith and reason, "
        "using Aristotle and other sources to argue about God, the soul, and law. Modern and "
        "contemporary philosophers often treat reason, science, and secular politics as more "
        "independent from religious authority. Compare how medieval and modern traditions think about "
        "the roles of faith and reason. How should PRIME map continuities and breaks between these "
        "pictures when it reasons about religion, science, and politics today?"
    )

    case_id = "canonical:history_medieval_vs_modern_faith_reason"

    task = ReasoningTask(
        task_id=f"hs_history_medieval_vs_modern_faith_reason_{datetime.utcnow().isoformat()}",
        kind=ReasoningTaskKind.ANALYSIS,
        natural_language_task=dilemma_text,
        domain_tag="philosophy",
        subdomain_tag="history",
        difficulty=DifficultyLevel.INTERMEDIATE,
        context_tags=[case_id],
        theme="hs.history.medieval_vs_modern_faith_reason",
        tools_allowed=[
            "philosophy_history_lesson",
            "philosophy_methods_lesson",
            "philosophy_religion_lesson",
        ],
    )

    core_req = ReasoningCoreRequest(
        user_id=user_id,
        task=task,
        high_stakes=is_high_stakes_task(task),
    )

    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as http_client:
        core_resp_raw = await http_client.post(
            "/prime/reasoning/core",
            json=core_req.model_dump(mode="json"),
        )
        if core_resp_raw.status_code != 200:
            raise HTTPException(
                status_code=core_resp_raw.status_code,
                detail=f"Reasoning core error: {core_resp_raw.text}",
            )
        core_resp_data = core_resp_raw.json()

    core_resp = ReasoningCoreResponse(**core_resp_data)

    outcome_quality = ReasoningOutcomeQuality.GOOD

    rubric_result: PhilosophyRubricEvaluateResponse | None = None

    if run_rubric:
        synthesized_answer = " ".join(core_resp.key_conclusions or [])
        rubric_req = PhilosophyRubricEvaluateRequest(
            question=dilemma_text,
            answer=synthesized_answer,
            context="hs.history",
        )

        async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as http_client:
            rubric_resp_raw = await http_client.post(
                "/prime/humanities/philosophy/rubric/evaluate-answer",
                json=rubric_req.model_dump(mode="json"),
            )
            if rubric_resp_raw.status_code == 200:
                rubric_result = PhilosophyRubricEvaluateResponse(
                    **rubric_resp_raw.json()
                )

    # Now that we know rubric_result (if any), log to memory.
    memory_entry = ReasoningMemoryEntry(
        id=task.task_id,
        task=task,
        response=core_resp,
        tags=ReasoningTraceTag(
            domain="philosophy",
            subdomain="history",
            level="hs",
            theme="hs.history.medieval_vs_modern_faith_reason",
        ),
        created_at=datetime.utcnow(),
        user_id=user_id,
        outcome_quality=outcome_quality,
        rubric_scores=rubric_result.scores if rubric_result else None,
        rubric_overall_comment=rubric_result.overall_comment if rubric_result else None,
    )
    append_memory_entry(memory_entry)

    return HSHistoryPracticeWithRubricResponse(
        task_id=task.task_id,
        key_conclusions=core_resp.key_conclusions,
        open_questions=core_resp.open_questions,
        outcome_quality=outcome_quality,
        rubric=rubric_result,
    )


@router.post(
    "/history/practice/ancient_vs_modern_person",
    response_model=HSHistoryPracticeWithRubricResponse,
    tags=["philosophy-hs-history"],
)
async def hs_history_practice_ancient_vs_modern_person(
    raw_request: Request,
    user_id: str = "raymond",
    run_rubric: bool = False,
) -> HSHistoryPracticeWithRubricResponse:
    """
    PRIME practice: compare ancient and modern ideas of the person and the good life.
    """

    dilemma_text = (
        "Ancient philosophies such as Aristotle's virtue ethics and the Hellenistic schools saw the "
        "person as shaped by character, roles in the city, and alignment with nature or logos. Many "
        "modern philosophies emphasize individual rights, autonomy, authenticity, and freedom from "
        "oppression. Compare ancient and modern ideas of what a person is and what a good life looks "
        "like. Which structural contrasts should PRIME keep in mind when it reasons about ethics, "
        "politics, and education?"
    )

    case_id = "canonical:history_ancient_vs_modern_person"

    task = ReasoningTask(
        task_id=f"hs_history_ancient_vs_modern_person_{datetime.utcnow().isoformat()}",
        kind=ReasoningTaskKind.ANALYSIS,
        natural_language_task=dilemma_text,
        domain_tag="philosophy",
        subdomain_tag="history",
        difficulty=DifficultyLevel.INTERMEDIATE,
        context_tags=[case_id],
        theme="hs.history.ancient_vs_modern_person",
        tools_allowed=[
            "philosophy_history_lesson",
            "philosophy_methods_lesson",
            "philosophy_ethics_lesson",
        ],
    )

    core_req = ReasoningCoreRequest(
        user_id=user_id,
        task=task,
        high_stakes=is_high_stakes_task(task),
    )

    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as http_client:
        core_resp_raw = await http_client.post(
            "/prime/reasoning/core",
            json=core_req.model_dump(mode="json"),
        )
        if core_resp_raw.status_code != 200:
            raise HTTPException(
                status_code=core_resp_raw.status_code,
                detail=f"Reasoning core error: {core_resp_raw.text}",
            )
        core_resp_data = core_resp_raw.json()

    core_resp = ReasoningCoreResponse(**core_resp_data)

    outcome_quality = ReasoningOutcomeQuality.GOOD

    rubric_result: PhilosophyRubricEvaluateResponse | None = None

    if run_rubric:
        synthesized_answer = " ".join(core_resp.key_conclusions or [])
        rubric_req = PhilosophyRubricEvaluateRequest(
            question=dilemma_text,
            answer=synthesized_answer,
            context="hs.history",
        )

        async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as http_client:
            rubric_resp_raw = await http_client.post(
                "/prime/humanities/philosophy/rubric/evaluate-answer",
                json=rubric_req.model_dump(mode="json"),
            )
            if rubric_resp_raw.status_code == 200:
                rubric_result = PhilosophyRubricEvaluateResponse(
                    **rubric_resp_raw.json()
                )

    memory_entry = ReasoningMemoryEntry(
        id=task.task_id,
        task=task,
        response=core_resp,
        tags=ReasoningTraceTag(
            domain="philosophy",
            subdomain="history",
            level="hs",
            theme="hs.history.ancient_vs_modern_person",
        ),
        created_at=datetime.utcnow(),
        user_id=user_id,
        outcome_quality=outcome_quality,
        rubric_scores=rubric_result.scores if rubric_result else None,
        rubric_overall_comment=rubric_result.overall_comment if rubric_result else None,
    )
    append_memory_entry(memory_entry)

    return HSHistoryPracticeWithRubricResponse(
        task_id=task.task_id,
        key_conclusions=core_resp.key_conclusions,
        open_questions=core_resp.open_questions,
        outcome_quality=outcome_quality,
        rubric=rubric_result,
    )

class PhilosophyRubricDimension(str, Enum):
    CLARITY = "clarity"
    CHARITY = "charity"
    RIGOR = "rigor"
    HISTORY_AWARENESS = "history_awareness"


class PhilosophyRubricScore(BaseModel):
    dimension: PhilosophyRubricDimension
    score_1_to_5: int
    explanation: str


class PhilosophyRubricRequest(BaseModel):
    question: str
    answer: str
    context: Optional[str] = None  # e.g., HS, undergrad, etc.


class PhilosophyRubricResponse(BaseModel):
    scores: List[PhilosophyRubricScore]
    overall_comment: str

@router.post(
    "/rubric/evaluate-answer",
    response_model=PhilosophyRubricResponse,
    tags=["philosophy-rubric"],
)
async def philosophy_rubric_evaluate_answer(
    req: PhilosophyRubricRequest,
) -> PhilosophyRubricResponse:
    """
    Evaluate a philosophical answer along key dimensions for PRIME's self-improvement.
    Dimensions: clarity, charity, rigor, history-awareness.
    """

    # PRIME can later call reasoning_core here too; for v1 we keep it simple and prompt the base model.

    prompt = (
        "You are evaluating a philosophical answer using a 1-5 rubric.\n"
        "Dimensions:\n"
        "- Clarity: Is the answer clearly structured and understandable?\n"
        "- Charity: Does it present opposing views fairly and avoid straw-manning?\n"
        "- Rigor: Does it use reasons, distinctions, and counterexamples carefully?\n"
        "- History-awareness: Does it situate ideas in relation to major traditions or figures when relevant?\n\n"
        f"Context (level): {req.context or 'unspecified'}\n"
        f"Question: {req.question}\n"
        f"Answer: {req.answer}\n\n"
        "For each dimension, give a score from 1 (very weak) to 5 (excellent), plus a one-sentence explanation.\n"
        "Then give a brief overall comment (2-3 sentences) on how to improve.\n"
    )

    # Here you call your local model API; placeholder:
    # model_resp = await call_internal_llm(prompt)
    # parsed = parse_model_resp_into_scores(model_resp)

    # For now, stub a neutral mid-level response so the endpoint is wired:
    scores = [
        PhilosophyRubricScore(
            dimension=PhilosophyRubricDimension.CLARITY,
            score_1_to_5=3,
            explanation="The answer is partly clear but its structure and key claims could be sharper.",
        ),
        PhilosophyRubricScore(
            dimension=PhilosophyRubricDimension.CHARITY,
            score_1_to_5=3,
            explanation="It mentions alternative views but does not fully develop them in their strongest form.",
        ),
        PhilosophyRubricScore(
            dimension=PhilosophyRubricDimension.RIGOR,
            score_1_to_5=3,
            explanation="Some reasons and distinctions are present, but counterarguments are not systematically addressed.",
        ),
        PhilosophyRubricScore(
            dimension=PhilosophyRubricDimension.HISTORY_AWARENESS,
            score_1_to_5=2,
            explanation="The answer hints at historical ideas but rarely names specific traditions or figures.",
        ),
    ]

    overall_comment = (
        "Overall, this is a promising partial answer, but it would benefit from a clearer structure, "
        "more careful presentation of competing views, and explicit references to key historical "
        "figures or schools where relevant."
    )

    return PhilosophyRubricResponse(
        scores=scores,
        overall_comment=overall_comment,
    )

class HSPhilosophyHistoryPeriod(BaseModel):
    id: str
    label: str
    timespan: str
    regions: List[str]
    core_questions: List[str]
    example_figures: List[str]
    suggested_hs_practice_endpoint: Optional[str] = None


class HSPhilosophyHistoryOverview(BaseModel):
    title: str
    period_overview: str
    periods: List[HSPhilosophyHistoryPeriod]

class HSHistoryContextToPracticeRequest(BaseModel):
    period_id: str
    branch: Literal["history"] = "history"
    run_rubric: bool = True


class HSHistoryContextToPracticeResponse(BaseModel):
    period_id: str
    branch: str
    short_context: str
    hs_practice_endpoint_used: str
    practice_result: HSHistoryPracticeWithRubricResponse

@router.get(
    "/history/overview-planner",
    response_model=HSPhilosophyHistoryOverview,
    tags=["philosophy-hs-history"],
)
async def hs_philosophy_history_overview_planner() -> HSPhilosophyHistoryOverview:
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as http_client:
        resp = await http_client.get("/prime/history/philosophy/lh1overview")
        if resp.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"history/philosophy lh1overview returned {resp.status_code}: {resp.text}",
            )
        lesson_data = resp.json()

    lesson = HistoryLesson(**lesson_data)

    periods_hs: List[HSPhilosophyHistoryPeriod] = []
    for p in lesson.periods:
        pid = p.get("id", "")
        label = p.get("label", "")
        timespan = p.get("timespan", "")
        regions = p.get("regions", []) or []
        core_questions = p.get("corequestions", []) or []

        ex_figs: List[str] = []
        for ex in p.get("exampletraditionsandfigures", []) or []:
            figs = ex.get("figures", [])
            if figs:
                ex_figs.extend(figs)
        ex_figs = sorted(set(ex_figs))[:4]

        suggested: Optional[str] = None
        if pid == "ancientaxial":
            suggested = "/prime/humanities/philosophy/hs/metaphysics/practice/personal_identity_over_time"
        elif pid == "medievalislamic":
            suggested = "/prime/humanities/philosophy/hs/religion/practice/faith_and_reason"
        elif pid == "earlymodern":
            suggested = "/prime/humanities/philosophy/hs/epistemology/practice/trusting_experts"
        elif pid in ("moderncontemporary", "worldphilosophies"):
            suggested = "/prime/humanities/philosophy/hs/political/practice/equality_vs_fairness"

        periods_hs.append(
            HSPhilosophyHistoryPeriod(
                id=pid,
                label=label,
                timespan=timespan,
                regions=regions,
                core_questions=core_questions[:2],
                example_figures=ex_figs,
                suggested_hs_practice_endpoint=suggested,
            )
        )

    return HSPhilosophyHistoryOverview(
        title=lesson.title,
        period_overview=lesson.period_overview,
        periods=periods_hs,
    )

@router.post(
    "/history/sequence/context_to_practice",
    response_model=HSHistoryContextToPracticeResponse,
    tags=["philosophy-hs-history"],
)
async def hs_history_sequence_context_to_practice(
    req: HSHistoryContextToPracticeRequest,
) -> HSHistoryContextToPracticeResponse:

    """
    Sequence endpoint: given a period_id and branch, fetch a short context from the history overview,
    run one HS history practice case (with rubric), and return everything bundled.
    """

    # 1. Fetch the HS history overview and select the relevant period.
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as http_client:
        overview_resp = await http_client.get(
            "/prime/humanities/philosophy/hs/history/overview-planner"
        )
        if overview_resp.status_code != 200:
            raise HTTPException(
                status_code=overview_resp.status_code,
                detail=f"HS history overview-planner error: {overview_resp.text}",
            )
        overview_data = overview_resp.json()

    overview = HSPhilosophyHistoryOverview(**overview_data)

    period = None
    for p in overview.periods:
        if p.id == req.period_id:
            period = p
            break

    if period is None:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown period_id '{req.period_id}' for HS philosophy history.",
        )

    # Build a short context string.
    core_qs = period.core_questions or []
    core_q_snippet = " ".join(core_qs[:2])
    regions_snippet = ", ".join(period.regions or [])
    short_context = (
        f"{period.label} ({period.timespan}) in regions {regions_snippet}. "
        f"Core questions include: {core_q_snippet}"
    )

    # 2. Select a HS practice endpoint. For now, we hard-wire mapping from period_id to one of the existing HS history practice endpoints.
    # You can expand this later or vary by branch; here branch is fixed as 'history'.
    period_to_practice_endpoint: dict[str, str] = {
        "ancientaxial": "/prime/humanities/philosophy/hs/history/practice/ancient_vs_earlymodern_epistemology",
        "medievalislamic": "/prime/humanities/philosophy/hs/history/practice/medieval_vs_modern_faith_reason",
        "earlymodern": "/prime/humanities/philosophy/hs/history/practice/ancient_vs_earlymodern_epistemology",
        "moderncontemporary": "/prime/humanities/philosophy/hs/history/practice/ancient_vs_modern_person",
        "worldphilosophies": "/prime/humanities/philosophy/hs/history/practice/ancient_vs_modern_person",
    }

    practice_endpoint = period_to_practice_endpoint.get(req.period_id)
    if practice_endpoint is None:
        # Fallback: use one generic HS history practice case.
        practice_endpoint = "/prime/humanities/philosophy/hs/history/practice/ancient_vs_modern_person"

    # 3. Call the selected HS practice endpoint with run_rubric set as requested.
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as http_client:
        practice_resp_raw = await http_client.post(
            practice_endpoint,
            params={"run_rubric": req.run_rubric},
        )
        if practice_resp_raw.status_code != 200:
            raise HTTPException(
                status_code=practice_resp_raw.status_code,
                detail=f"HS history practice error from {practice_endpoint}: {practice_resp_raw.text}",
            )
        practice_data = practice_resp_raw.json()

    practice_result = HSHistoryPracticeWithRubricResponse(**practice_data)

    return HSHistoryContextToPracticeResponse(
        period_id=req.period_id,
        branch=req.branch,
        short_context=short_context,
        hs_practice_endpoint_used=practice_endpoint,
        practice_result=practice_result,
    )

class HSPhilosophyCatalogOverview(BaseModel):
    figures: list[HSPhilosophyFigure]
    works: list[HSPhilosophyWork]


@router.get(
    "/lane2/catalog/overview",
    response_model=HSPhilosophyCatalogOverview,
    name="philosophy_hs_catalog_overview",
)
async def hs_catalog_overview() -> HSPhilosophyCatalogOverview:
    figures = [
        HSPhilosophyFigure(
            id="figure.bentham",
            name="Jeremy Bentham",
            birth_year=1748,
            death_year=1832,
            region="England",
            traditions=["utilitarianism"],
            main_works=["work.bentham_introduction"],
            main_concepts=["ethics.concept.utilitarianism"],
        ),
        HSPhilosophyFigure(
            id="figure.mill",
            name="John Stuart Mill",
            birth_year=1806,
            death_year=1873,
            region="England",
            traditions=["utilitarianism", "liberalism"],
            main_works=["work.mill_utilitarianism"],
            main_concepts=[
                "ethics.concept.utilitarianism",
                "political.concept_libertarianism",
            ],
        ),
        HSPhilosophyFigure(
            id="figure.kant",
            name="Immanuel Kant",
            birth_year=1724,
            death_year=1804,
            region="Prussia",
            traditions=["deontology", "Enlightenment"],
            main_works=["work.kant_groundwork"],
            main_concepts=[
                "ethics.concept.kantian_deontology",
                "epistemology.concept.skepticism",
            ],
        ),
        HSPhilosophyFigure(
            id="figure.aristotle",
            name="Aristotle",
            birth_year=-384,
            death_year=-322,
            region="Ancient Greece",
            traditions=["virtue_ethics"],
            main_works=["work.aristotle_nicomachean_ethics"],
            main_concepts=["ethics.concept.virtue_ethics"],
        ),
        HSPhilosophyFigure(
            id="figure.gilligan",
            name="Carol Gilligan",
            birth_year=1936,
            death_year=None,
            region="United States",
            traditions=["care_ethics"],
            main_works=["work.gilligan_in_a_different_voice"],
            main_concepts=["ethics.concept.care_ethics"],
        ),
        HSPhilosophyFigure(
            id="figure.noddings",
            name="Nel Noddings",
            birth_year=1929,
            death_year=2022,
            region="United States",
            traditions=["care_ethics"],
            main_works=["work.noddings_caring"],
            main_concepts=["ethics.concept.care_ethics"],
        ),
        HSPhilosophyFigure(
            id="figure.rawls",
            name="John Rawls",
            birth_year=1921,
            death_year=2002,
            region="United States",
            traditions=["political_liberalism"],
            main_works=["work.rawls_theory_of_justice"],
            main_concepts=["political.concept_rawlsian_justice"],
        ),
        HSPhilosophyFigure(
            id="figure.nozick",
            name="Robert Nozick",
            birth_year=1938,
            death_year=2002,
            region="United States",
            traditions=["libertarianism"],
            main_works=["work.nozick_anarchy_state_utopia"],
            main_concepts=["political.concept_libertarianism"],
        ),
    ]

    works = [
        HSPhilosophyWork(
            id="work.bentham_introduction",
            title="An Introduction to the Principles of Morals and Legislation",
            author_id="figure.bentham",
            year=1789,
            notes=["Classic early statement of utilitarianism."],
        ),
        HSPhilosophyWork(
            id="work.mill_utilitarianism",
            title="Utilitarianism",
            author_id="figure.mill",
            year=1861,
            notes=["Refined utilitarianism with higher and lower pleasures."],
        ),
        HSPhilosophyWork(
            id="work.kant_groundwork",
            title="Groundwork of the Metaphysics of Morals",
            author_id="figure.kant",
            year=1785,
            notes=["Core text for Kantian deontology and the categorical imperative."],
        ),
        HSPhilosophyWork(
            id="work.aristotle_nicomachean_ethics",
            title="Nicomachean Ethics",
            author_id="figure.aristotle",
            year=None,
            notes=["Foundational text for virtue ethics."],
        ),
        HSPhilosophyWork(
            id="work.gilligan_in_a_different_voice",
            title="In a Different Voice",
            author_id="figure.gilligan",
            year=1982,
            notes=["Key work developing care ethics and challenging traditional moral theory."],
        ),
        HSPhilosophyWork(
            id="work.noddings_caring",
            title="Caring: A Feminine Approach to Ethics and Moral Education",
            author_id="figure.noddings",
            year=1984,
            notes=["Extends care ethics into education and everyday relationships."],
        ),
        HSPhilosophyWork(
            id="work.rawls_theory_of_justice",
            title="A Theory of Justice",
            author_id="figure.rawls",
            year=1971,
            notes=["Major statement of justice as fairness."],
        ),
        HSPhilosophyWork(
            id="work.nozick_anarchy_state_utopia",
            title="Anarchy, State, and Utopia",
            author_id="figure.nozick",
            year=1974,
            notes=["Libertarian response to Rawls on rights and the state."],
        ),
    ]

    return HSPhilosophyCatalogOverview(figures=figures, works=works)


async def _run_bridge_for_hs_question(
    question_text: str,
) -> Optional[BridgeResponse]:
    """
    Run the K‑8 bridge orchestration on the HS question, so HS lane 1
    always sees the 'kid-level' signal first.
    """
    # Default: use K8 signals and lane2 branching.
    bridge_req = BridgeRequest(
        question_text=question_text,
        use_k8_signals=True,
        use_lane2_branching=True,
    )

    # Reuse the existing Bridge endpoint logic directly.
    from app.prime.humanities.philosophy.endpoints_bridge import philosophy_bridge

    try:
        bridge_resp: BridgeResponse = await philosophy_bridge(bridge_req)
    except Exception:
        # If anything fails, HS lane still works with its own heuristics.
        return None

    return bridge_resp

async def _run_ethics_four_lens(dilemma: str) -> EthicsFourLensResponse:
    """
    Run the L3 four-lens ethics orchestration on a dilemma text.
    """
    req = EthicsFourLensDilemmaRequest(dilemma_text=dilemma)
    return await philosophy_ethics_l3_fourlens(req)

class HSMethodsConceptOverview(BaseModel):
    concepts: List[MethodsConceptId]


class HSMethodsConceptPracticeRequest(BaseModel):
    student_answer: str


@router.get(
    "/m1/methods-concepts/overview",
    response_model=HSMethodsConceptOverview,
    name="philosophy_hs_m1_methods_concepts_overview",
)
async def hs_methods_concepts_overview() -> HSMethodsConceptOverview:
    concepts = list(MethodsConceptId)
    return HSMethodsConceptOverview(concepts=concepts)


@router.get(
    "/m1/methods-concepts/{concept_id}",
    response_model=MethodsConceptLesson,
    name="philosophy_hs_m1_methods_concept",
)
async def hs_methods_concept_detail(
    concept_id: MethodsConceptId,
) -> MethodsConceptLesson:
    raise NotImplementedError("HS methods concept detail not yet implemented.")


@router.post(
    "/m1/methods-concepts/{concept_id}/practice",
    response_model=MethodsConceptPracticeSet,
    name="philosophy_hs_m1_methods_concept_practice",
)
async def hs_methods_concept_practice(
    concept_id: MethodsConceptId,
    req: HSMethodsConceptPracticeRequest,
) -> MethodsConceptPracticeSet:
    raise NotImplementedError("HS methods concept practice not yet implemented.")


class HSMethodsPlannerRequest(BaseModel):
    question_text: str


class HSMethodsPlannerResponse(BaseModel):
    original_question: str
    suggested_concepts: List[MethodsConceptId]


@router.post(
    "/m1/methods-concepts/planner",
    response_model=HSMethodsPlannerResponse,
    name="philosophy_hs_m1_methods_concepts_planner",
)
async def hs_methods_concepts_planner(
    req: HSMethodsPlannerRequest,
) -> HSMethodsPlannerResponse:
    lowered = req.question_text.lower()
    suggested: List[MethodsConceptId] = []

    if any(w in lowered for w in ["read", "reading", "text", "article", "paper"]):
        suggested.append(MethodsConceptId.READING_PHILOSOPHY)

    if any(w in lowered for w in ["argument", "premise", "conclusion", "reason"]):
        suggested.append(MethodsConceptId.ARGUMENT_RECONSTRUCTION)

    if any(w in lowered for w in ["good reason", "bad reason", "evaluate", "critique"]):
        suggested.append(MethodsConceptId.EVALUATION)

    if any(w in lowered for w in ["essay", "paragraph", "write", "writing"]):
        suggested.append(MethodsConceptId.PHILOSOPHICAL_PROSE)

    if not suggested:
        suggested = [MethodsConceptId.READING_PHILOSOPHY]

    return HSMethodsPlannerResponse(
        original_question=req.question_text,
        suggested_concepts=suggested,
    )

@router.get(
    "/teacher/warmups",
    response_model=PhilosophyWarmupResponse,
    tags=["philosophy-teacher-meta"],
)
async def get_philosophy_warmups(
    n: int = Query(3, ge=1, le=20),
    branches: list[str] | None = Query(
        None,
        description="Optional list of branches to sample from "
                    "(e.g. ['ethics','epistemology','logic']).",
    ),
) -> PhilosophyWarmupResponse:
    """
    Return N HS-level warmup prompts across philosophy branches.

    - `n`: number of warmups to return.
    - `branches`: optional filter by branch; if omitted, sample from all.
    """
    pool = PHILOSOPHY_WARMUPS_HS
    if branches:
        allowed = set(branches)
        pool = [w for w in PHILOSOPHY_WARMUPS_HS if w.branch in allowed]

    if not pool:
        return PhilosophyWarmupResponse(warmups=[])

    # Sample without replacement if possible, otherwise allow repeats.
    if n >= len(pool):
        selected = pool.copy()
        random.shuffle(selected)
    else:
        selected = random.sample(pool, n)

    return PhilosophyWarmupResponse(warmups=selected)

@router.get(
    "/teacher/practice_sets",
    response_model=PhilosophyPracticeSetResponse,
    summary="Get a mixed-branch HS practice set",
)
async def get_hs_philosophy_practice_sets(
    n: int = Query(5, ge=1, le=20, description="Number of practice items to return"),
    branches: list[str] | None = Query(
        default=None,
        description="Optional HS philosophy branches to include (e.g., ethics, epistemology, history).",
    ),
    include_units: list[str] | None = Query(
        default=None,
        description="Optional HS syllabus unit ids to restrict practice items to.",
    ),
) -> PhilosophyPracticeSetResponse:
    """
    Return a mixed-branch HS practice set built from canonical practice endpoints
    defined on HS-level philosophy syllabus units.

    This is a meta layer: it does *not* execute practice endpoints, it only
    surfaces structured references to them so PRIME or a teacher can call
    the underlying endpoints as needed.
    """

    if not PHILOSOPHY_HS_PRACTICE_POOL:
        return PhilosophyPracticeSetResponse(items=[])

    # Filter by branches and/or unit ids if provided.
    filtered_pool: list[tuple[str, str, str]] = []

    for branch, unit_id, practice_endpoint in PHILOSOPHY_HS_PRACTICE_POOL:
        if branches is not None and branch not in branches:
            continue
        if include_units is not None and unit_id not in include_units:
            continue
        filtered_pool.append((branch, unit_id, practice_endpoint))

    if not filtered_pool:
        return PhilosophyPracticeSetResponse(items=[])

    # Cap n at the size of the filtered pool to avoid ValueError from random.sample.
    sample_size = min(n, len(filtered_pool))
    sampled_slots = sample(filtered_pool, sample_size)

    items: list[PhilosophyPracticeItem] = []

    for idx, (branch, unit_id, practice_endpoint) in enumerate(sampled_slots):
        item_id = f"hs.practice.meta.{branch}.{unit_id}.{idx}"
        label = f"HS {branch} practice from {unit_id}"

        items.append(
            PhilosophyPracticeItem(
                id=item_id,
                level="hs",
                branch=branch,
                syllabus_unit_id=unit_id,
                practice_endpoint=practice_endpoint,
                label=label,
            )
        )

    return PhilosophyPracticeSetResponse(items=items)

@router.post(
    "/teacher/reflection",
    response_model=PhilosophyReflectionSummary,
    summary="Summarize recent HS practice and extract general principles",
)
async def hs_philosophy_teacher_reflection(
    sessions: list[PhilosophyReflectionSession],
) -> PhilosophyReflectionSummary:
    """
    Take a list of recent HS practice sessions (with rubric scores and notes)
    and return: (1) a summary of strengths/weaknesses, (2) generalized
    principles PRIME should carry forward, keyed by rubric dimensions and HS units.
    """

    if not sessions:
        return PhilosophyReflectionSummary(
            strengths=[],
            weaknesses=[],
            principles=[],
        )

    # Aggregate rubric scores by dimension.
    dimension_scores: dict[str, list[float]] = {}
    for session in sessions:
        for score in session.rubric_scores:
            dim_id = score.dimension  # existing field name
            if dim_id not in dimension_scores:
                dimension_scores[dim_id] = []
            dimension_scores[dim_id].append(float(score.score_1_to_5))

    strengths: list[str] = []
    weaknesses: list[str] = []
    principles: list[PhilosophyReflectionPrinciple] = []

    # Simple heuristic: high average => strength, low average => weakness.
    for dim_id, scores in dimension_scores.items():
        if not scores:
            continue
        avg = sum(scores) / len(scores)
        if avg >= 4.0:
            strengths.append(
                f"Consistently strong on rubric dimension '{dim_id}' "
                f"(average score around {avg:.1f})."
            )
        elif avg <= 2.5:
            weaknesses.append(
                f"Needs more support on rubric dimension '{dim_id}' "
                f"(average score around {avg:.1f})."
            )

    # Collect related HS units per dimension.
    related_units_by_dim: dict[str, set[str]] = {}
    for session in sessions:
        for score in session.rubric_scores:
            dim_id = score.dimension
            if dim_id not in related_units_by_dim:
                related_units_by_dim[dim_id] = set()
            related_units_by_dim[dim_id].add(session.syllabus_unit_id)

    for dim_id, unit_ids in related_units_by_dim.items():
        principle_id = f"hs.reflection.{dim_id}"
        units_list = sorted(unit_ids)

        text = (
            f"When working on HS units {', '.join(units_list)}, PRIME should pay special attention to "
            f"rubric dimension '{dim_id}': explicitly naming criteria, checking examples against those "
            f"criteria, and stating what is going well and what needs revision."
        )

        principles.append(
            PhilosophyReflectionPrinciple(
                id=principle_id,
                rubric_dimension_id=dim_id,
                related_units=units_list,
                text=text,
            )
        )

    return PhilosophyReflectionSummary(
        strengths=strengths,
        weaknesses=weaknesses,
        principles=principles,
    )

class HSCaseSummary(BaseModel):
    case_id: str
    domain: str
    subdomain: str
    theme: Optional[str]
    last_seen_at: datetime
    last_outcome_quality: Optional[ReasoningOutcomeQuality]


class HSCasebookIndexResponse(BaseModel):
    domain: str
    subdomain: Optional[str]
    cases: list[HSCaseSummary]


@router.get(
    "/casebook/index",
    response_model=HSCasebookIndexResponse,
)
async def hs_casebook_index(
    domain: Literal["philosophy"] = "philosophy",
    subdomain: Optional[str] = None,
) -> HSCasebookIndexResponse:
    """
    List canonical HS philosophy cases seen in reasoning_memory.jsonl,
    grouped by (domain, subdomain).
    """
    # Collect latest entry per (task_id, subdomain)
    latest: dict[tuple[str, str], ReasoningMemoryEntry] = {}

    for entry in iter_memory_entries() or []:
        if entry.tags.domain != domain:
            continue
        if subdomain and entry.tags.subdomain != subdomain:
            continue

        key = (entry.task.task_id, entry.tags.subdomain or "")
        prev = latest.get(key)
        if prev is None or entry.created_at > prev.created_at:
            latest[key] = entry

    cases: list[HSCaseSummary] = []
    for (task_id, sd), entry in latest.items():
        cases.append(
            HSCaseSummary(
                case_id=task_id,
                domain=entry.tags.domain,
                subdomain=sd,
                theme=entry.tags.theme,
                last_seen_at=entry.created_at,
                last_outcome_quality=entry.outcome_quality,
            )
        )

    # Sort newest first
    cases.sort(key=lambda c: c.last_seen_at, reverse=True)

    return HSCasebookIndexResponse(
        domain=domain,
        subdomain=subdomain,
        cases=cases,
    )