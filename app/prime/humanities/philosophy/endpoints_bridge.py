from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.prime.curriculum.models import (
    K8PhilosophyPlannerRequest,
    K8PhilosophyPlannerResponse,
    K8TeacherLaneSummary,
    K8PhilosophyLane,
    K8WorldQuestionTag,
    K8MindQuestionTag,
    PhilosophyBranch,
    PhilosophyBranchPracticeRequest,
    PhilosophyBranchPracticeResponse,
    LogicConceptId,
    MethodsConceptId,
    MetaphysicsConceptId,
    EthicsFramework,
)

from app.prime.humanities.philosophy.endpoints_k8 import (
    philosophy_k8_planner,
    philosophy_k8_teacher_view,
)


router = APIRouter()


class BridgeRequest(BaseModel):
    question_text: str
    use_k8_signals: bool = True
    use_lane2_branching: bool = True


class BridgeMappedLesson(BaseModel):
    lesson_id: str
    title: str
    reason: str


class BridgeLogicTargets(BaseModel):
    primary_lesson: Optional[BridgeMappedLesson] = None
    secondary_lessons: List[BridgeMappedLesson] = []
    logic_concept_ids: List[LogicConceptId] = []


class BridgeEthicsTargets(BaseModel):
    primary_lesson: Optional[BridgeMappedLesson] = None
    secondary_lessons: List[BridgeMappedLesson] = []
    ethics_frameworks: List[EthicsFramework] = []


class BridgeMetaphysicsTargets(BaseModel):
    primary_lesson: Optional[BridgeMappedLesson] = None
    secondary_lessons: List[BridgeMappedLesson] = []
    metaphysics_concept_ids: List[MetaphysicsConceptId] = []


class BridgeMethodsTargets(BaseModel):
    primary_lesson: Optional[BridgeMappedLesson] = None
    secondary_lessons: List[BridgeMappedLesson] = []
    methods_concept_ids: List[MethodsConceptId] = []


class BridgeResponse(BaseModel):
    original_question: str
    lane: Optional[K8PhilosophyLane] = None
    world_primary_tag: Optional[K8WorldQuestionTag] = None
    mind_primary_tag: Optional[K8MindQuestionTag] = None
    lane2_branch: Optional[PhilosophyBranch] = None

    logic_targets: BridgeLogicTargets
    ethics_targets: BridgeEthicsTargets
    metaphysics_targets: BridgeMetaphysicsTargets
    methods_targets: BridgeMethodsTargets


def _pick_logic_targets(qtext: str) -> List[LogicConceptId]:
    concepts: List[LogicConceptId] = [LogicConceptId.ARGUMENT_STRUCTURE]

    # If you later add more, use the correct enum names:
    # concepts.append(LogicConceptId.FALLACIES)
    # concepts.append(LogicConceptId.VALIDITY_SOUNDNESS)
    # concepts.append(LogicConceptId.PREDICATE_LOGIC)
    # concepts.append(LogicConceptId.PROOF_METHODS)
    # concepts.append(LogicConceptId.MODAL_NON_CLASSICAL)

    return concepts


def _pick_ethics_targets(
    question_text: str,
    lane: Optional[K8PhilosophyLane],
) -> BridgeEthicsTargets:
    text = question_text.lower()
    lessons: List[BridgeMappedLesson] = []
    frameworks: List[EthicsFramework] = []

    if lane == K8PhilosophyLane.ETHICS or any(
        w in text
        for w in [
            "fair",
            "unfair",
            "promise",
            "honest",
            "dishonest",
            "cheat",
            "harm",
            "hurt",
            "kind",
        ]
    ):
        lessons.append(
            BridgeMappedLesson(
                lesson_id="philo.l3.ethics-intro",
                title="Ethical Theories I: Consequences, Rules, Virtues, and Care",
                reason=(
                    "Question about fairness, harm, promises, or kindness → "
                    "map to four core ethical frameworks."
                ),
            )
        )
        frameworks = [
            EthicsFramework.CONSEQUENTIALISM,
            EthicsFramework.DEONTOLOGY,
            EthicsFramework.VIRTUE_ETHICS,
            EthicsFramework.CARE_ETHICS,
        ]

    primary = lessons[0] if lessons else None
    secondaries = lessons[1:] if len(lessons) > 1 else []

    return BridgeEthicsTargets(
        primary_lesson=primary,
        secondary_lessons=secondaries,
        ethics_frameworks=frameworks,
    )


def _pick_metaphysics_targets(
    question_text: str,
    world_primary_tag: Optional[K8WorldQuestionTag],
) -> BridgeMetaphysicsTargets:
    text = question_text.lower()
    lessons: List[BridgeMappedLesson] = []
    ids: List[MetaphysicsConceptId] = []

    if world_primary_tag == K8WorldQuestionTag.TIME:
        ids.append(MetaphysicsConceptId.TIME_SPACE)
        lessons.append(
            BridgeMappedLesson(
                lesson_id="metaphysics.concept.time_space",
                title="Metaphysics of Time and Space",
                reason="WORLD tag TIME → map to time & space metaphysics.",
            )
        )
    elif world_primary_tag == K8WorldQuestionTag.EXISTENCE:
        ids.append(MetaphysicsConceptId.BEING_EXISTENCE)
        lessons.append(
            BridgeMappedLesson(
                lesson_id="metaphysics.concept.being_existence",
                title="Being and Existence",
                reason="WORLD tag EXISTENCE → map to being/existence.",
            )
        )
    else:
        if any(w in text for w in ["universe", "nothing", "why is there something"]):
            ids.append(MetaphysicsConceptId.BEING_EXISTENCE)
        lessons.append(
            BridgeMappedLesson(
                lesson_id="metaphysics.concept.being_existence",
                title="Being and Existence",
                reason="Generic big-world question; default to being/existence.",
            )
        )

    primary = lessons[0] if lessons else None
    secondaries = lessons[1:] if len(lessons) > 1 else []

    return BridgeMetaphysicsTargets(
        primary_lesson=primary,
        secondary_lessons=secondaries,
        metaphysics_concept_ids=ids,
    )


def _pick_methods_targets(qtext: str) -> List[MethodsConceptId]:
    ids: List[MethodsConceptId] = []

    # Always start with basic reading philosophy skills
    ids.append(MethodsConceptId.READING_PHILOSOPHY)

    # Optionally, you can add more methods concepts later:
    # ids.append(MethodsConceptId.ARGUMENT_RECONSTRUCTION)
    # ids.append(MethodsConceptId.EVALUATION)
    # ids.append(MethodsConceptId.PHILOSOPHICAL_PROSE)

    return ids


@router.post("/bridge", response_model=BridgeResponse)
async def philosophy_bridge(request: BridgeRequest) -> BridgeResponse:
    qtext = request.question_text

    k8_lane: Optional[K8PhilosophyLane] = None
    world_primary: Optional[K8WorldQuestionTag] = None
    mind_primary: Optional[K8MindQuestionTag] = None
    lane2_branch: Optional[PhilosophyBranch] = None

    if request.use_k8_signals:
        planner_req = K8PhilosophyPlannerRequest(
            question_text=qtext,
            include_lane_practice=True,
        )
        planner_resp: K8PhilosophyPlannerResponse = await philosophy_k8_planner(
            planner_req
        )
        k8_lane = planner_resp.chosen_lane

        teacher_req = K8PhilosophyPlannerRequest(
            question_text=qtext,
            include_lane_practice=True,
        )
        teacher_summary: K8TeacherLaneSummary = await philosophy_k8_teacher_view(
            teacher_req
        )
        world_primary = teacher_summary.world_primary_tag
        mind_primary = teacher_summary.mind_primary_tag

    if request.use_lane2_branching:
        lane2_req = PhilosophyBranchPracticeRequest(question_text=qtext)
        # For now, skip lane2 and leave lane2_branch as None.
        # When ready, wire:
        # lane2_resp: PhilosophyBranchPracticeResponse = await philosophy_lane2_core_branches_practice(lane2_req)
        # lane2_branch = lane2_resp.branch

    logic_ids = _pick_logic_targets(qtext)
    ethics_targets = _pick_ethics_targets(qtext, k8_lane)
    metaphysics_targets = _pick_metaphysics_targets(qtext, world_primary)
    methods_ids = _pick_methods_targets(qtext)

    logic_targets = BridgeLogicTargets(
        primary_lesson=None,
        secondary_lessons=[],
        logic_concept_ids=logic_ids,
    )
    methods_targets = BridgeMethodsTargets(
        primary_lesson=None,
        secondary_lessons=[],
        methods_concept_ids=methods_ids,
    )

    return BridgeResponse(
        original_question=qtext,
        lane=k8_lane,
        world_primary_tag=world_primary,
        mind_primary_tag=mind_primary,
        lane2_branch=lane2_branch,
        logic_targets=logic_targets,
        ethics_targets=ethics_targets,
        metaphysics_targets=metaphysics_targets,
        methods_targets=methods_targets,
    )
