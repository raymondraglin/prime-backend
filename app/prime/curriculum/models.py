from enum import Enum
from typing import Any, List, Optional, Literal

from datetime import datetime

from pydantic import BaseModel


# ============================================================
# Layer 1: Domains (12-domain backbone)
# ============================================================

class DomainId(str, Enum):
    MATHEMATICS_AND_FORMAL_SCIENCES = "mathematics_and_formal_sciences"
    NATURAL_SCIENCES = "natural_sciences"
    ENGINEERING_AND_TECHNOLOGY = "engineering_and_technology"
    COMPUTER_SCIENCE_AND_INFORMATION_SYSTEMS = "computer_science_and_information_systems"
    BUSINESS_ECONOMICS_AND_MANAGEMENT = "business_economics_and_management"
    LAW_GOVERNANCE_AND_PUBLIC_ADMIN = "law_governance_and_public_administration"
    SOCIAL_AND_BEHAVIORAL_SCIENCES = "social_and_behavioral_sciences"
    HUMANITIES = "humanities"
    HEALTH_MEDICINE_AND_BIOLOGICAL_SYSTEMS = "health_medicine_and_biological_systems"
    EDUCATION_PEDAGOGY_AND_HUMAN_DEVELOPMENT = "education_pedagogy_and_human_development"
    ARTS_DESIGN_AND_COMMUNICATION = "arts_design_and_communication"
    SECURITY_DEFENSE_AND_EMERGENCY_SYSTEMS = "security_defense_and_emergency_systems"


# ============================================================
# Layer 3: Global curriculum levels (cross-domain)
# ============================================================

class CurriculumLevel(str, Enum):
    SCHOOL_FOUNDATION = "school_foundation"        # K–8
    SCHOOL_SECONDARY = "school_secondary"          # 9–12
    UNDERGRAD_INTRO = "undergrad_intro"
    UNDERGRAD_CORE = "undergrad_core"
    UNDERGRAD_ADVANCED = "undergrad_advanced"
    GRAD_MASTERS = "grad_masters"
    GRAD_PHD_CORE = "grad_phd_core"
    GRAD_SPECIALIZED = "grad_specialized"
    DOCTORAL_RESEARCH = "doctoral_research"


# ============================================================
# Layer 2: Subjects within domains (starter set)
# ============================================================

class SubjectId(str, Enum):
    # Math and money subjects you already use
    MATH_FOUNDATIONS = "math_foundations"
    MONEY_FOUNDATIONS_HISTORY = "money_foundations_history"

    # Starter explicit IDs for clarity as we grow
    MATH_THEORETICAL = "math_theoretical"
    MATH_FINANCIAL = "math_financial"
    MONEY_HISTORY = "money_history"

    # Humanities / philosophy subjects
    PHILOSOPHY_CORE = "philosophy_core"
    # Later: PHYSICS, HISTORY, ECONOMICS, etc.


class DifficultyLevel(str, Enum):
    EARLY = "early"           # early grades / intuitive
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    RESEARCH = "research"


class LessonKind(str, Enum):
    CONCEPT = "concept"
    PRACTICE = "practice"
    HISTORY = "history"
    APPLICATION = "application"


class HistoryEra(BaseModel):
    label: str              # e.g., "Ancient", "Classical", "Medieval", "Modern"
    start_year: int | None  # BCE negative, CE positive, None if very approximate
    end_year: int | None
    description: str


class HistoryEvent(BaseModel):
    id: str
    title: str
    era: str                # simple label, e.g., "Ancient", "Classical"
    approx_date: str        # human-readable, e.g., "c. 3400 BCE"
    location: str           # e.g., "Mesopotamia", "China"
    description: str
    significance: str
    related_subjects: list[SubjectId]
    related_lessons: list[str]  # lesson ids this event connects to


class LessonRef(BaseModel):
    """
    Lightweight reference to a lesson inside a subject.
    """
    lesson_id: str
    title: str
    kind: LessonKind
    difficulty: DifficultyLevel


class Lesson(BaseModel):
    """
    Generic lesson container; 'content' can embed subject-specific structures.
    For math, this will include our number_sense structures.
    """
    id: str
    subject: SubjectId
    title: str
    kind: LessonKind
    difficulty: DifficultyLevel
    description: str
    content: dict[str, Any]

    # New global tags for PRIME's backbone
    domain: DomainId | None = None
    level: CurriculumLevel | None = None


class SubjectCurriculum(BaseModel):
    """
    All lessons for a single subject, plus metadata and recommended order.
    """
    subject: SubjectId
    name: str
    description: str
    lessons: list[Lesson]
    recommended_order: list[str]  # list of lesson ids

    # Optional default tags for all lessons in this subject
    domain: DomainId | None = None
    default_level: CurriculumLevel | None = None


class CurriculumSnapshot(BaseModel):
    """
    High-level view of PRIME's curriculum across all subjects.
    """
    subjects: list[SubjectCurriculum]

# ============================================================
# Humanities / philosophy lesson model (generic K–PhD lesson)
# ============================================================
class HSPhilosophyUnit(BaseModel):
    id: str  # e.g., "hs.ethics.core_lenses"
    branch: Literal[
        "ethics",
        "epistemology",
        "metaphysics",
        "political",
        "religion",
        "aesthetics",
        "history",
    ]
    level: Literal["hs"] = "hs"
    title: str
    short_description: str
    core_questions: list[str]
    key_concepts: list[str]
    canonical_practice_endpoints: list[str]
    suggested_sequence_position: int  # rough ladder order within branch

class HSPhilosophyUnitsOverview(BaseModel):
    units: list[HSPhilosophyUnit]


class PhilosophyLesson(BaseModel):
    """
    Bare-bones lesson object for PRIME's philosophy spine.
    Lane 1 will use this to teach 'what philosophy is' in a structured way.
    """
    id: str
    subject: SubjectId
    title: str
    kind: LessonKind
    difficulty: DifficultyLevel
    description: str
    content: dict[str, Any]

    # Curriculum backbone tags
    domain: DomainId | None = None
    level: CurriculumLevel | None = None

class PhilosophySyllabusLevel(str, Enum):
    HS = "hs"
    UN = "un"
    GS = "gs"
    DR = "dr"
    BRIDGE = "bridge"


class PhilosophySyllabusUnit(BaseModel):
    """
    A single unit in PRIME's philosophy ladder at any level.
    """
    id: str  # e.g., "hs.ethics.core_lenses" or "un.ethics.normative_theory"
    level: PhilosophySyllabusLevel
    branch: Literal[
        "ethics",
        "epistemology",
        "metaphysics",
        "political",
        "religion",
        "aesthetics",
        "history",
        "logic",
        "world",
        "applied",
        "meta",
    ]
    title: str
    short_description: str
    core_questions: list[str]
    key_concepts: list[str]
    canonical_practice_endpoints: list[str]

    # Ladder structure
    prerequisites: list[str] = []        # ids of prior units (possibly at lower levels)
    recommended_next_units: list[str] = []  # ids of next units PRIME should progress to


class PhilosophySyllabusLadder(BaseModel):
    """
    A slice of the cross-level ladder PRIME can query.
    """
    units: list[PhilosophySyllabusUnit]

class PhilosophyMetaMapItem(BaseModel):
    """
    Connect a specific HS or UN philosophy syllabus unit to DR-level pillars and frontier questions.
    """
    unit_id: str
    level: str
    branch: str
    dr_pillars: list[str]
    frontier_questions: list[str]
    notes: list[str]


class PhilosophyMetaMapResponse(BaseModel):
    meta_map: PhilosophyMetaMapItem

class PhilosophyWarmupBranch(str):
    ETHICS = "ethics"
    EPISTEMOLOGY = "epistemology"
    METAPHYSICS = "metaphysics"
    LOGIC = "logic"
    POLITICAL = "political"
    HISTORY = "history"
    MIND_AI = "mind_ai"
    WORLD = "world"
    APPLIED = "applied"

class PhilosophyWarmupBranch(str):
    ETHICS = "ethics"
    EPISTEMOLOGY = "epistemology"
    METAPHYSICS = "metaphysics"
    LOGIC = "logic"
    POLITICAL = "political"
    HISTORY = "history"
    MIND_AI = "mind_ai"
    WORLD = "world"
    APPLIED = "applied"


class PhilosophyWarmupItem(BaseModel):
    id: str  # e.g., "hs.ethics.stakeholders_and_harms.w1"
    level: Literal["hs"]
    branch: str  # one of PhilosophyWarmupBranch values
    syllabus_unit_id: str  # links into PHILOSOPHY_SYLLABUS_LADDER
    prompt: str  # short teacher-facing warmup prompt
    suggested_practice_endpoint: str  # one HS practice endpoint

class PhilosophyWarmupItem(BaseModel):
    id: str  # e.g., "hs.ethics.stakeholders_and_harms.w1"
    level: Literal["hs"]
    branch: str  # one of PhilosophyWarmupBranch values
    syllabus_unit_id: str  # links into PHILOSOPHY_SYLLABUS_LADDER
    prompt: str  # short teacher-facing warmup prompt
    suggested_practice_endpoint: str  # one HS practice endpoint


class PhilosophyWarmupResponse(BaseModel):
    warmups: list[PhilosophyWarmupItem]

class PhilosophyPracticeItem(BaseModel):
    id: str
    level: Literal["hs"]
    branch: str
    syllabus_unit_id: str
    practice_endpoint: str
    label: str | None = None


class PhilosophyPracticeSetResponse(BaseModel):
    items: list[PhilosophyPracticeItem]

# ============================================================
# Humanities / philosophy practice models (Lane 1)
# ============================================================


class PhilosophyQuestionKind(str, Enum):
    GENERAL = "general"          # broad life/big questions
    METAPHYSICS = "metaphysics"  # what is real / identity / time
    EPISTEMOLOGY = "epistemology"  # knowledge / evidence / certainty
    ETHICS = "ethics"            # right/wrong, good/bad
    POLITICAL_SOCIAL = "political_social"  # justice, power, rights, institutions
    OTHER = "other"


class PhilosophyPracticeRequest(BaseModel):
    """
    Input for Lane 1 practice: user shares a free-form question or concern.
    """
    question_text: str


class PhilosophyPracticeResponse(BaseModel):
    """
    Response for Lane 1 practice: PRIME classifies the question and
    returns Socratic-style prompts instead of a direct answer.
    """
    original_question: str
    inferred_kind: PhilosophyQuestionKind
    rationale: str
    clarifying_questions: list[str]
    value_prompts: list[str]
    reflection_prompt: str

class PhilosophyArgumentPracticeRequest(BaseModel):
    """
    Input for Lane 1b practice: user supplies a short argument or statement.
    PRIME helps identify premises and conclusion.
    """
    text: str

class PhilosophyArgumentPracticeResponse(BaseModel):
    """
    Response for Lane 1b practice: PRIME proposes a breakdown into premises
    and conclusion, plus questions to refine the argument.
    """
    original_text: str
    guessed_premises: list[str]
    guessed_conclusion: str | None
    explanation: str
    refinement_questions: list[str]

class K8LogicPracticeItemKind(str, Enum):
    SPOT_REASON_VS_CONCLUSION = "spot_reason_vs_conclusion"
    IS_THAT_A_REASON = "is_that_a_reason"
    EVERYONE_DOES_IT = "everyone_does_it"
    FREE_FORM_BELIEF_AND_REASON = "free_form_belief_and_reason"


class K8LogicPracticeRequest(BaseModel):
    """
    K–8 logic practice: very small exercises for reasons vs conclusions
    and simple bad moves.
    """
    item_kind: K8LogicPracticeItemKind
    answer_text: str | None = None


class K8LogicPracticeResponse(BaseModel):
    """
    PRIME's response: restate, gently classify, and invite reflection.
    """
    item_kind: K8LogicPracticeItemKind
    prompt: str
    child_answer: str | None
    prime_paraphrase: str
    prime_feedback: str
    follow_up_question: str

class K8EthicsStoryKind(str, Enum):
    SHARING_SNACKS = "sharing_snacks"
    TEST_ANSWER = "test_answer"
    BROKEN_PROMISE = "broken_promise"


class K8EthicsPracticeRequest(BaseModel):
    """
    K–8 ethics practice: micro-stories about fairness, harm, and promises.
    """
    story_kind: K8EthicsStoryKind
    answer_text: str | None = None


class K8EthicsPracticeResponse(BaseModel):
    """
    PRIME's response: restate, gently frame fairness/harm/trust,
    and invite further reflection.
    """
    story_kind: K8EthicsStoryKind
    story: str
    child_answer: str | None
    prime_paraphrase: str
    prime_feedback: str
    follow_up_question: str

class K8LogicPracticeItemKind(str, Enum):
    SPOT_REASON_VS_CONCLUSION = "spot_reason_vs_conclusion"
    IS_THAT_A_REASON = "is_that_a_reason"
    EVERYONE_DOES_IT = "everyone_does_it"
    FREE_FORM_BELIEF_AND_REASON = "free_form_belief_and_reason"


class K8LogicPracticeRequest(BaseModel):
    """
    K–8 logic practice: very small exercises for reasons vs conclusions
    and simple bad moves.
    """
    item_kind: K8LogicPracticeItemKind
    answer_text: str | None = None


class K8LogicPracticeResponse(BaseModel):
    """
    PRIME's response: restate, gently classify, and invite reflection.
    """
    item_kind: K8LogicPracticeItemKind
    prompt: str
    child_answer: str | None
    prime_paraphrase: str
    prime_feedback: str
    follow_up_question: str


class K8EthicsStoryKind(str, Enum):
    SHARING_SNACKS = "sharing_snacks"
    TEST_ANSWER = "test_answer"
    BROKEN_PROMISE = "broken_promise"


class K8EthicsPracticeRequest(BaseModel):
    """
    K–8 ethics practice: micro-stories about fairness, harm, and promises.
    """
    story_kind: K8EthicsStoryKind
    answer_text: str | None = None


class K8EthicsPracticeResponse(BaseModel):
    """
    PRIME's response: restate, gently frame fairness/harm/trust,
    and invite further reflection.
    """
    story_kind: K8EthicsStoryKind
    story: str
    child_answer: str | None
    prime_paraphrase: str
    prime_feedback: str
    follow_up_question: str


class K8PhilosophyLane(str, Enum):
    LOGIC = "logic"
    ETHICS = "ethics"
    MIND = "mind"
    WORLD = "world"


class K8WorldQuestionTag(str, Enum):
    TIME = "time"
    EXISTENCE = "existence"
    SPACE = "space"
    POSSIBILITY = "possibility"
    OTHER = "other"


class K8WorldPracticeRequest(BaseModel):
    """
    Input for K–8 world/reality practice: a kid's big-world question.
    """
    question_text: str


class K8WorldPracticeResponse(BaseModel):
    """
    Gentle follow-up for a world/reality question, plus simple tags.
    """
    original_question: str
    primary_tag: K8WorldQuestionTag
    secondary_tags: List[K8WorldQuestionTag]
    explanation: str
    follow_up_prompts: List[str]


class K8WorldPlannerRequest(BaseModel):
    """
    High-level planner for K–8 world/reality.
    """
    question_text: str


class K8WorldPlannerResponse(BaseModel):
    """
    Bundles the world lesson with a world practice response.
    """
    original_question: str
    lesson: dict  # serialized PhilosophyLesson
    practice: K8WorldPracticeResponse


class K8MindQuestionTag(str, Enum):
    FEELINGS = "feelings"
    MEMORY = "memory"
    IDENTITY = "identity"
    OTHER = "other"


class K8MindPracticeRequest(BaseModel):
    """
    Input for K–8 mind/self practice: a kid's inner-world question.
    """
    question_text: str


class K8MindPracticeResponse(BaseModel):
    """
    Gentle follow-up for a mind/self question, plus simple tags.
    """
    original_question: str
    primary_tag: K8MindQuestionTag
    secondary_tags: List[K8MindQuestionTag]
    explanation: str
    follow_up_prompts: List[str]


class K8MindPlannerRequest(BaseModel):
    """
    High-level planner for K–8 mind/self.
    """
    question_text: str


class K8MindPlannerResponse(BaseModel):
    """
    Bundles the mind/self lesson with a mind practice response.
    """
    original_question: str
    lesson: dict  # serialized PhilosophyLesson
    practice: K8MindPracticeResponse


class K8PhilosophyPlannerRequest(BaseModel):
    """
    A child's free-form question or thought for K–8 philosophy.

    If include_lane_practice is True, the planner may attach a lane-specific
    practice payload for some lanes (currently mind and world).
    """
    question_text: str
    include_lane_practice: bool = False


class K8PhilosophyPlannerResponse(BaseModel):
    """
    Planner output: which K–8 lane to start in and which lesson id
    PRIME recommends, plus a kid-friendly explanation and starter prompt.

    Optionally includes lane-specific practice payloads for some lanes.
    """
    original_question: str
    chosen_lane: K8PhilosophyLane
    lesson_id: str
    lesson_title: str
    reason: str
    starter_prompt: str
    world_practice: Optional[K8WorldPracticeResponse] = None
    mind_practice: Optional[K8MindPracticeResponse] = None

class K8LogicPlannerRequest(BaseModel):
    """
    High-level planner for K–8 logic seeds.
    """
    question_text: str


class K8LogicPlannerResponse(BaseModel):
    """
    Bundles the K–8 logic lesson with a logic practice response.
    """
    original_question: str
    lesson: dict  # serialized PhilosophyLesson
    practice: K8LogicPracticeResponse


class K8EthicsPlannerRequest(BaseModel):
    """
    High-level planner for K–8 ethics & values.
    """
    question_text: str


class K8EthicsPlannerResponse(BaseModel):
    """
    Bundles the K–8 ethics lesson with an ethics practice response.
    """
    original_question: str
    lesson: dict  # serialized PhilosophyLesson
    practice: K8EthicsPracticeResponse

class K8TeacherViewMode(str, Enum):
    LANE_SUMMARY = "lane_summary"
    LANE_WITH_LESSON = "lane_with_lesson"


class K8TeacherLaneSummary(BaseModel):
    """
    Teacher-facing view of how PRIME classified a K–8 question,
    what the child will see, and how an adult might scaffold it.
    """
    mode: K8TeacherViewMode
    original_question: str
    chosen_lane: K8PhilosophyLane

    # Optional lane-specific tags
    world_primary_tag: Optional[K8WorldQuestionTag] = None
    world_secondary_tags: Optional[List[K8WorldQuestionTag]] = None
    mind_primary_tag: Optional[K8MindQuestionTag] = None
    mind_secondary_tags: Optional[List[K8MindQuestionTag]] = None

    # What the child sees first
    kid_starter_prompt: str

    # Optional brief lesson headline for the adult
    lesson_title: Optional[str] = None

    # Adult guidance
    suggested_teacher_moves: List[str]
    risk_flags: List[str]
    teacher_reflection_prompts: List[str]


class PhilosophyLane1Mode(str, Enum):
    TEACH_WHAT_IS_PHILOSOPHY = "teach_what_is_philosophy"
    PRACTICE_QUESTION_KIND = "practice_question_kind"
    TEACH_ARGUMENT_STRUCTURE = "teach_argument_structure"
    PRACTICE_ARGUMENT_STRUCTURE = "practice_argument_structure"


class PhilosophyLane1PlannerRequest(BaseModel):
    """
    High-level request for Lane 1: route to teach/practice based on mode.
    """
    mode: PhilosophyLane1Mode
    payload: dict[str, Any] | None = None


class PhilosophyLane1PlannerResponse(BaseModel):
    """
    High-level response: echoes mode and wraps the underlying lesson/practice payload.
    """
    mode: PhilosophyLane1Mode
    result: dict[str, Any]

class PhilosophyLane2Mode(str, Enum):
    TEACH_CORE_BRANCHES = "teach_core_branches"
    PRACTICE_CORE_BRANCHES = "practice_core_branches"


class PhilosophyLane2PlannerRequest(BaseModel):
    """
    High-level request for Lane 2: route to core-branches teach/practice.
    """
    mode: PhilosophyLane2Mode
    payload: dict[str, Any] | None = None


class PhilosophyLane2PlannerResponse(BaseModel):
    """
    High-level response for Lane 2.
    """
    mode: PhilosophyLane2Mode
    result: dict[str, Any]

class PhilosophyLane3Mode(str, Enum):
    TEACH_ETHICS_INTRO = "teach_ethics_intro"
    PRACTICE_ETHICS_INTRO = "practice_ethics_intro"


class PhilosophyLane3PlannerRequest(BaseModel):
    mode: PhilosophyLane3Mode
    payload: dict[str, Any] | None = None


class PhilosophyLane3PlannerResponse(BaseModel):
    mode: PhilosophyLane3Mode
    result: dict[str, Any]

class PhilosophyLane4Mode(str, Enum):
    TEACH_ETHICS_DIGITAL = "teach_ethics_digital"
    PRACTICE_ETHICS_DIGITAL = "practice_ethics_digital"


class PhilosophyLane4PlannerRequest(BaseModel):
    mode: PhilosophyLane4Mode
    payload: dict[str, Any] | None = None


class PhilosophyLane4PlannerResponse(BaseModel):
    mode: PhilosophyLane4Mode
    result: dict[str, Any]

class PhilosophyLane5Mode(str, Enum):
    TEACH_CONSEQUENTIALISM_L3 = "teach_consequentialism_l3"
    PRACTICE_CONSEQUENTIALISM_L3 = "practice_consequentialism_l3"
    TEACH_DEONTOLOGY_L3 = "teach_deontology_l3"
    PRACTICE_DEONTOLOGY_L3 = "practice_deontology_l3"
    TEACH_VIRTUE_L3 = "teach_virtue_l3"
    PRACTICE_VIRTUE_L3 = "practice_virtue_l3"
    TEACH_CARE_L3 = "teach_care_l3"
    PRACTICE_CARE_L3 = "practice_care_l3"


class PhilosophyLane5PlannerRequest(BaseModel):
    mode: PhilosophyLane5Mode
    payload: dict[str, Any] | None = None


class PhilosophyLane5PlannerResponse(BaseModel):
    mode: PhilosophyLane5Mode
    result: dict[str, Any]

# ============================================================
# Philosophy Lane 2: core branches (teach + practice)
# ============================================================


class PhilosophyBranch(str, Enum):
    ETHICS = "ethics"
    EPISTEMOLOGY = "epistemology"
    METAPHYSICS = "metaphysics"
    POLITICAL = "political"
    LOGIC = "logic"
    AESTHETICS = "aesthetics"
    OTHER = "other"


class PhilosophyBranchPracticeRequest(BaseModel):
    """
    Input for Lane 2 practice: user supplies a life/question prompt.
    PRIME classifies it by branch and asks deeper, branch-specific questions.
    """
    question_text: str


class PhilosophyBranchPracticeResponse(BaseModel):
    """
    Response for Lane 2 practice: branch classification plus tailored
    questions and value/uncertainty prompts.
    """
    original_question: str
    branch: PhilosophyBranch
    rationale: str
    branch_summary: str
    key_questions: list[str]
    value_or_epistemic_prompts: list[str]
    next_step_suggestion: str

class PhilosophyFigure(BaseModel):
    id: str
    name: str
    birth_year: Optional[int] = None
    death_year: Optional[int] = None
    region: Optional[str] = None
    traditions: list[str] = []
    main_works: list[str] = []  # work ids
    main_ideas: list[str] = []  # idea ids


class PhilosophyIdea(BaseModel):
    id: str
    label: str
    branch: PhilosophyBranch
    summary: str
    key_claims: list[str] = []
    supporting_figures: list[str] = []  # figure ids
    opposing_figures: list[str] = []
    rival_ideas: list[str] = []         # idea ids

# ============================================================
# Philosophy Lane 3: Ethics I (intro normative frameworks)
# ============================================================


class EthicsFramework(str, Enum):
    CONSEQUENTIALISM = "consequentialism"
    DEONTOLOGY = "deontology"
    VIRTUE_ETHICS = "virtue_ethics"
    CARE_ETHICS = "care_ethics"


class EthicsIntroTeachSummary(BaseModel):
    """
    Short summary of an ethical framework for teaching.
    """
    framework: EthicsFramework
    headline: str
    core_question: str
    focus: str
    typical_guiding_principle: str
    strengths: list[str]
    challenges: list[str]
    example_application: str


class EthicsIntroPracticeRequest(BaseModel):
    """
    Input for Ethics I practice: a concrete dilemma, in the user's own words.
    """
    dilemma_text: str


class EthicsFrameworkEvaluation(BaseModel):
    """
    How one framework 'sees' a single dilemma.
    """
    framework: EthicsFramework
    main_question: str
    suggested_focus: str
    tentative_judgment: str
    what_it_values_most: list[str]
    what_it_risks_or_downplays: list[str]


class EthicsIntroPracticeResponse(BaseModel):
    """
    Response for Ethics I practice: four framework perspectives on a dilemma,
    plus prompts about trade-offs and disagreement.
    """
    original_dilemma: str
    evaluations: list[EthicsFrameworkEvaluation]
    comparison_questions: list[str]
    wisdom_prompts: list[str]

# ============================================================
# Philosophy Lane 4: Ethics II (everyday digital & AI ethics)
# ============================================================


class EthicsDigitalContextTag(str, Enum):
    PRIVACY = "privacy"
    MISINFORMATION = "misinformation"
    SOCIAL_MEDIA = "social_media"
    RECOMMENDATION = "recommendation"
    AUTOMATION = "automation"
    HIRING_OR_LENDING = "hiring_or_lending"
    SURVEILLANCE = "surveillance"
    USER_AI_RELATIONSHIP = "user_ai_relationship"
    OTHER = "other"


class EthicsDigitalPracticeRequest(BaseModel):
    """
    Input for Ethics II practice: a digital/AI dilemma in the user's own words.
    Optional context tags help PRIME tune its prompts.
    """
    dilemma_text: str
    context_tags: list[EthicsDigitalContextTag] | None = None


class EthicsDigitalFrameworkEvaluation(BaseModel):
    """
    How one ethical framework views a digital/AI dilemma.
    """
    framework: EthicsFramework
    digital_focus: str
    main_question: str
    tentative_take: str
    values_highlighted: list[str]
    risks_ignored: list[str]


class EthicsDigitalPracticeResponse(BaseModel):
    """
    Response for Ethics II practice: four ethical lenses on a digital/AI dilemma,
    plus comparison and wisdom prompts.
    """
    original_dilemma: str
    context_tags: list[EthicsDigitalContextTag] | None
    evaluations: list[EthicsDigitalFrameworkEvaluation]
    comparison_questions: list[str]
    wisdom_prompts: list[str]

# ============================================================
# Ethics Lane 3: Consequentialism in depth
# ============================================================


class ConsequentialismVariant(str, Enum):
    ACT = "act"
    RULE = "rule"
    TWO_LEVEL = "two_level"
    OTHER = "other"


class EthicsConsequentialismTeachEntry(BaseModel):
    """
    Teaching entry for a core idea or variant within consequentialism.
    """
    title: str
    description: str
    examples: list[str]
    strengths: list[str]
    classic_objections: list[str]


class EthicsConsequentialismTeachLesson(BaseModel):
    """
    Structured content for a consequentialism-in-depth lesson.
    """
    overview: str
    historical_roots: list[str]
    core_principles: list[str]
    variants: list[dict[str, Any]]
    strengths: list[str]
    objections: list[str]
    reflection_questions: list[str]


class EthicsConsequentialismPracticeRequest(BaseModel):
    """
    Input for Consequentialism L3 practice:
    A hard case where consequences and common moral intuitions may conflict.
    """
    dilemma_text: str


class EthicsConsequentialismPracticeAnalysis(BaseModel):
    """
    How a 'committed consequentialist' might analyze the case,
    and how a 'softened' or 'rule-based' consequentialist might respond.
    """
    act_style_summary: str
    rule_or_softened_summary: str
    key_tradeoffs: list[str]
    places_it_feels_wrong: list[str]


class EthicsConsequentialismPracticeResponse(BaseModel):
    """
    Response for Consequentialism L3 practice:
    Shows how consequentialism reasons about a case, and where its limits show up.
    """
    original_dilemma: str
    analysis: EthicsConsequentialismPracticeAnalysis
    self_check_questions: list[str]
    meta_reflection_prompts: list[str]

# ============================================================
# Ethics Lane 3: Deontology in depth
# ============================================================


class DeontologyVariant(str, Enum):
    KANTIAN = "kantian"
    RULE_DEONTOLOGY = "rule_deontology"
    RIGHTS_BASED = "rights_based"
    OTHER = "other"


class EthicsDeontologyTeachEntry(BaseModel):
    """
    Teaching entry for a core idea or variant within deontological ethics.
    """
    title: str
    description: str
    examples: list[str]
    strengths: list[str]
    classic_objections: list[str]


class EthicsDeontologyTeachLesson(BaseModel):
    """
    Structured content for a deontology-in-depth lesson.
    """
    overview: str
    historical_roots: list[str]
    core_principles: list[str]
    variants: list[dict[str, Any]]
    strengths: list[str]
    objections: list[str]
    reflection_questions: list[str]


class EthicsDeontologyPracticeRequest(BaseModel):
    """
    Input for Deontology L3 practice:
    A hard case where duties, rules, or rights may conflict with outcomes.
    """
    dilemma_text: str


class EthicsDeontologyPracticeAnalysis(BaseModel):
    """
    How a deontologist might analyze a case, highlighting duties, permissions,
    and constraints on using people as mere means.
    """
    duty_focused_summary: str
    humanity_formula_summary: str
    key_conflicts_between_duties: list[str]
    limits_on_tradeoffs: list[str]


class EthicsDeontologyPracticeResponse(BaseModel):
    """
    Response for Deontology L3 practice:
    Shows how deontology reasons about a case and where it strains or clashes with intuitions.
    """
    original_dilemma: str
    analysis: EthicsDeontologyPracticeAnalysis
    self_check_questions: list[str]
    meta_reflection_prompts: list[str]

# ============================================================
# Ethics Lane 3: Virtue ethics in depth
# ============================================================


class VirtueEthicsVariant(str, Enum):
    ARISTOTELIAN = "aristotelian"
    CARE_OF_SELF_PRACTICE = "care_of_self_practice"
    CONTEMPORARY_CHARACTER = "contemporary_character"
    OTHER = "other"


class EthicsVirtueTeachEntry(BaseModel):
    """
    Teaching entry for a core idea or variant within virtue ethics.
    """
    title: str
    description: str
    examples: list[str]
    strengths: list[str]
    classic_objections: list[str]


class EthicsVirtueTeachLesson(BaseModel):
    """
    Structured content for a virtue-ethics-in-depth lesson.
    """
    overview: str
    historical_roots: list[str]
    core_principles: list[str]
    variants: list[dict[str, Any]]
    strengths: list[str]
    objections: list[str]
    reflection_questions: list[str]


class EthicsVirtuePracticeRequest(BaseModel):
    """
    Input for Virtue Ethics L3 practice:
    A real or imagined situation where character, habit, and role models matter.
    """
    dilemma_text: str


class EthicsVirtuePracticeAnalysis(BaseModel):
    """
    How a virtue ethicist might analyze a case, focusing on character, habits, and the kind of life being shaped.
    """
    character_focused_summary: str
    relevant_virtues_and_vices: list[str]
    long_term_self_shaping: list[str]
    tensions_with_other_frameworks: list[str]


class EthicsVirtuePracticeResponse(BaseModel):
    """
    Response for Virtue Ethics L3 practice:
    Shows how virtue ethics reasons about a case and highlights character-level questions.
    """
    original_dilemma: str
    analysis: EthicsVirtuePracticeAnalysis
    self_check_questions: list[str]
    meta_reflection_prompts: list[str]

# ============================================================
# Ethics Lane 3: Care / Relational ethics in depth
# ============================================================


class CareEthicsVariant(str, Enum):
    FEMINIST_CARE = "feminist_care"
    CONFUCIAN_RELATIONAL = "confucian_relational"
    GLOBAL_STRUCTURAL_CARE = "global_structural_care"
    OTHER = "other"


class EthicsCareTeachEntry(BaseModel):
    """
    Teaching entry for a core idea or variant within care / relational ethics.
    """
    title: str
    description: str
    examples: list[str]
    strengths: list[str]
    classic_objections: list[str]


class EthicsCareTeachLesson(BaseModel):
    """
    Structured content for a care / relational-ethics-in-depth lesson.
    Analytic in structure, but written in a way that can speak to real relationships.
    """
    overview: str
    historical_roots: list[str]
    core_principles: list[str]
    variants: list[dict[str, Any]]
    strengths: list[str]
    objections: list[str]
    reflection_questions: list[str]


class EthicsCarePracticeRequest(BaseModel):
    """
    Input for Care / Relational Ethics L3 practice:
    A real or imagined situation where relationships, vulnerability, and care are central.
    """
    dilemma_text: str


class EthicsCarePracticeAnalysis(BaseModel):
    """
    How a care / relational ethicist might analyze a case, focusing on relationships,
    needs for care, and power / vulnerability dynamics.
    """
    relationship_focused_summary: str
    care_obligations_and_needs: list[str]
    power_and_vulnerability_analysis: list[str]
    tensions_with_other_frameworks: list[str]


class EthicsCarePracticeResponse(BaseModel):
    """
    Response for Care / Relational Ethics L3 practice:
    Shows how an ethics of care and relationship reasons about a case,
    and invites reflection on concrete relationships and needs.
    """
    original_dilemma: str
    analysis: EthicsCarePracticeAnalysis
    self_check_questions: list[str]
    meta_reflection_prompts: list[str]

# ============================================================
# Ethics Lane 3: Four-lens orchestration
# ============================================================


class EthicsFourLensDilemmaRequest(BaseModel):
    """
    Input for the four-lens orchestration endpoint:
    a single ethical dilemma to be analyzed by all four deep lanes.
    """
    dilemma_text: str


class EthicsSingleLensSummary(BaseModel):
    """
    Summary of how one framework (consequentialism, deontology, virtue, or care)
    approaches the dilemma, with a reference to the detailed practice analysis.
    """
    framework: str  # "consequentialism", "deontology", "virtue", "care"
    headline: str
    key_question: str
    notes: list[str]


class EthicsFourLensResponse(BaseModel):
    """
    Combined view of a dilemma under all four deep ethics lenses.
    """
    original_dilemma: str
    summaries: list[EthicsSingleLensSummary]
    consequentialism: EthicsConsequentialismPracticeResponse
    deontology: EthicsDeontologyPracticeResponse
    virtue: EthicsVirtuePracticeResponse
    care: EthicsCarePracticeResponse

class EthicsMetaPerspectiveMode(str, Enum):
    LEGALISTIC = "legalistic"
    RELATIONAL = "relational"


class EthicsMetaPerspectiveSummary(BaseModel):
    """
    A higher-level perspective built on top of the four ethics lenses.
    LEGALISTIC: rules, rights, institutional duties.
    RELATIONAL: relationships, care, lived context.
    """
    mode: EthicsMetaPerspectiveMode
    headline: str
    key_concerns: list[str]
    alignment_with_frameworks: list[str]
    points_of_tension: list[str] = []


class EthicsMetaPerspectivesResponse(BaseModel):
    """
    Encodes both legalistic and relational perspectives for a single dilemma.
    """
    original_dilemma: str
    legalistic: EthicsMetaPerspectiveSummary
    relational: EthicsMetaPerspectiveSummary

# ============================================================
# Conceptual engineering: core ethics concepts (harm, coercion, etc.)
# ============================================================


class EthicsConceptDimension(BaseModel):
    name: str
    description: str


class EthicsConceptExample(BaseModel):
    id: str
    title: str
    description: str
    is_clear_case: bool  # True = paradigm case, False = borderline/pressure case


class EthicsConceptFrameworkView(BaseModel):
    framework: EthicsFramework
    headline: str
    characterization: str
    tensions: List[str] = []


class EthicsConcept(BaseModel):
    id: str
    name: str
    working_definition: str
    dimensions: List[EthicsConceptDimension] = []
    examples: List[EthicsConceptExample] = []
    contrast_concepts: List[str] = []
    framework_views: List[EthicsConceptFrameworkView] = []
    notes: List[str] = []


class EthicsConceptDiagnosisRequest(BaseModel):
    concept_id: str
    case_id: Optional[str] = None
    case_description: str


class EthicsConceptDimensionAssessment(BaseModel):
    dimension_name: str
    applies: bool
    explanation: str


class EthicsConceptDiagnosisResponse(BaseModel):
    concept_id: str
    concept_name: str
    overall_match: str  # "clear_case", "borderline", "no_match"
    dimension_assessments: List[EthicsConceptDimensionAssessment]
    pressures_on_definition: List[str] = []
    notes: List[str] = []

class EthicsConceptLessonProfessorView(BaseModel):
    """
    Professor-level view: situate the concept across the K–PhD spine
    and connect it to other areas.
    """
    spine_position: str  # e.g., "early seeds in K–8, core in high school ethics, formal in undergrad..."
    connections_to_other_areas: list[str]  # e.g., "political philosophy", "law", "AI ethics"
    deeper_theories: list[str]  # e.g., "rights-based theories", "utilitarian accounts of harm"


class EthicsConceptLessonGradView(BaseModel):
    """
    Grad-student view: tensions, edge cases, and open debates.
    """
    core_tensions: list[str]
    edge_cases: list[str]
    open_questions: list[str]


class EthicsConceptLessonTeacherStep(BaseModel):
    """
    Elementary-teacher view: one small concrete step with a check.
    """
    order: int
    prompt: str
    example: str
    check_question: str


class EthicsConceptLessonTeacherView(BaseModel):
    """
    Sequence of teacher-style steps with simple checks.
    """
    steps: list[EthicsConceptLessonTeacherStep]


class EthicsConceptLesson(BaseModel):
    """
    Full triple-role lesson for a single ethics concept.
    """
    id: str
    concept: EthicsConcept
    subject: SubjectId = SubjectId.PHILOSOPHY_CORE
    domain: DomainId = DomainId.HUMANITIES
    level: CurriculumLevel

    professor_view: EthicsConceptLessonProfessorView
    grad_view: EthicsConceptLessonGradView
    teacher_view: EthicsConceptLessonTeacherView

# =========================================
# Logic & Argumentation core concepts
# =========================================

class LogicConceptId(str, Enum):
    ARGUMENT_STRUCTURE = "logic.concept.argument_structure"
    FALLACIES = "logic.concept.fallacies"
    VALIDITY_SOUNDNESS = "logic.concept.validity_soundness"
    PROOF_METHODS = "logic.concept.proof_methods"
    PREDICATE_LOGIC = "logic.concept.predicate_logic"
    MODAL_NONCLASSICAL = "logic.concept.modal_nonclassical"


class LogicConcept(BaseModel):
    """
    Core logic and argumentation concepts PRIME must master.
    """
    id: LogicConceptId
    name: str
    working_definition: str
    notes: list[str] = []


class LogicConceptLessonProfessorView(BaseModel):
    """
    Professor-level view: place the concept along the K–PhD spine
    and connect it to other domains.
    """
    spine_position: str
    connections_to_other_areas: list[str]
    deeper_theories: list[str]


class LogicConceptLessonGradView(BaseModel):
    """
    Grad-student view: tensions, edge cases, and open research-level questions.
    """
    core_tensions: list[str]
    edge_cases: list[str]
    open_questions: list[str]


class LogicConceptLessonTeacherStep(BaseModel):
    """
    Elementary-teacher view: one tiny, concrete step with a check.
    """
    order: int
    prompt: str
    example: str
    check_question: str


class LogicConceptLessonTeacherView(BaseModel):
    steps: list[LogicConceptLessonTeacherStep]


class LogicConceptPracticeQuestion(BaseModel):
    """
    Concrete practice / reflection, where PRIME both teaches and learns.
    """
    prompt: str
    expected_shape: str  # e.g., "short_text", "multiple_choice", "argument_outline"


class LogicConceptPracticeSet(BaseModel):
    """
    Practice for a concept at a given level, to be extended as you log data.
    """
    concept_id: LogicConceptId
    level: CurriculumLevel
    questions: list[LogicConceptPracticeQuestion]

class LogicConceptLesson(BaseModel):
    """
    Full lesson bundle for a single logic concept:
    - core concept metadata
    - professor (spine) view
    - grad (tensions/edge cases) view
    - teacher (step-by-step) view
    - practice set
    """
    id: str
    concept: LogicConcept
    subject: SubjectId
    domain: DomainId
    level: CurriculumLevel
    professor_view: LogicConceptLessonProfessorView
    grad_view: LogicConceptLessonGradView
    teacher_view: LogicConceptLessonTeacherView
    practice: LogicConceptPracticeSet

class PhilosophyHSEthicsPracticeRequest(BaseModel):
    dilemma_text: str
    user_id: Optional[str] = None
    case_id: Optional[str] = None  # e.g., "canonical:cheating_when_others_cheat"


class PhilosophyHSEthicsPracticeResponse(BaseModel):
    task_id: str
    key_conclusions: List[str]
    open_questions: List[str]
    outcome_quality: "ReasoningOutcomeQuality"

class HistoryLesson(BaseModel):
    id: str
    subject_id: str  # store SubjectId value
    title: str

    period_overview: str
    periods: List[dict[str, Any]]
    crosstraditionnotes: List[str]
    howitshapestoday: List[str]

    domain: DomainId
    level: CurriculumLevel
    kind: LessonKind = LessonKind.HISTORY
# =========================================
# Philosophical Methods & Writing concepts
# =========================================

class MethodsConceptId(str, Enum):
    READING_PHILOSOPHY = "methods.concept.reading_philosophy"
    ARGUMENT_RECONSTRUCTION = "methods.concept.argument_reconstruction"
    EVALUATION = "methods.concept.evaluation"
    PHILOSOPHICAL_PROSE = "methods.concept.philosophical_prose"


class MethodsConcept(BaseModel):
    """
    Core methodological skills: reading, reconstructing, evaluating, and writing.
    """
    id: MethodsConceptId
    name: str
    working_definition: str
    notes: list[str] = []


class MethodsConceptLessonProfessorView(BaseModel):
    spine_position: str
    connections_to_other_areas: list[str]
    deeper_theories: list[str]


class MethodsConceptLessonGradView(BaseModel):
    core_tensions: list[str]
    edge_cases: list[str]
    open_questions: list[str]


class MethodsConceptLessonTeacherStep(BaseModel):
    order: int
    prompt: str
    example: str
    check_question: str


class MethodsConceptLessonTeacherView(BaseModel):
    steps: list[MethodsConceptLessonTeacherStep]


class MethodsConceptPracticeQuestion(BaseModel):
    prompt: str
    expected_shape: str  # e.g. "short_text", "outline", "paragraph"


class MethodsConceptPracticeSet(BaseModel):
    concept_id: MethodsConceptId
    level: CurriculumLevel
    questions: list[MethodsConceptPracticeQuestion]

class MethodsConceptLesson(BaseModel):
    """
    Full lesson bundle for a single methods concept.
    """
    id: str
    concept: MethodsConcept
    subject: SubjectId
    domain: DomainId
    level: CurriculumLevel
    professor_view: MethodsConceptLessonProfessorView
    grad_view: MethodsConceptLessonGradView
    teacher_view: MethodsConceptLessonTeacherView
    practice: MethodsConceptPracticeSet

class MethodsConceptLesson(BaseModel):
    id: str
    concept: MethodsConcept
    subject: SubjectId = SubjectId.PHILOSOPHY_CORE
    domain: DomainId = DomainId.HUMANITIES
    level: CurriculumLevel

    professor_view: MethodsConceptLessonProfessorView
    grad_view: MethodsConceptLessonGradView
    teacher_view: MethodsConceptLessonTeacherView
    practice: MethodsConceptPracticeSet

# =========================================
# Metaphysics core concepts
# =========================================

class MetaphysicsConceptId(str, Enum):
    BEING_EXISTENCE = "metaphysics.concept.being_existence"
    OBJECTS_PROPERTIES = "metaphysics.concept.objects_properties"
    IDENTITY_PERSISTENCE = "metaphysics.concept.identity_persistence"
    CAUSATION = "metaphysics.concept.causation"
    TIME_SPACE = "metaphysics.concept.time_space"
    MODALITY = "metaphysics.concept.modality"
    PERSONAL_IDENTITY = "metaphysics_personal_identity"
    TIME_AND_MODALITY = "metaphysics_time_and_modality"
    FREE_WILL_AND_DETERMINISM = "metaphysics_free_will_and_determinism"

class MetaphysicsConcept(BaseModel):
    """
    Core metaphysical concepts PRIME must understand and use in reasoning.
    """
    id: MetaphysicsConceptId
    name: str
    working_definition: str
    notes: list[str] = []


class MetaphysicsConceptLessonProfessorView(BaseModel):
    spine_position: str
    connections_to_other_areas: list[str]
    deeper_theories: list[str]


class MetaphysicsConceptLessonGradView(BaseModel):
    core_tensions: list[str]
    edge_cases: list[str]
    open_questions: list[str]


class MetaphysicsConceptLessonTeacherStep(BaseModel):
    order: int
    prompt: str
    example: str
    check_question: str


class MetaphysicsConceptLessonTeacherView(BaseModel):
    steps: list[MetaphysicsConceptLessonTeacherStep]


class MetaphysicsConceptPracticeQuestion(BaseModel):
    prompt: str
    expected_shape: str


class MetaphysicsConceptPracticeSet(BaseModel):
    concept_id: MetaphysicsConceptId
    level: CurriculumLevel
    questions: list[MetaphysicsConceptPracticeQuestion]

class MetaphysicsConceptLesson(BaseModel):
    """
    Full lesson bundle for a single metaphysics concept.
    """
    id: str
    concept: MetaphysicsConcept
    subject: SubjectId
    domain: DomainId
    level: CurriculumLevel
    professor_view: MetaphysicsConceptLessonProfessorView
    grad_view: MetaphysicsConceptLessonGradView
    teacher_view: MetaphysicsConceptLessonTeacherView
    practice: MetaphysicsConceptPracticeSet

class MetaphysicsConceptLesson(BaseModel):
    id: str
    concept: MetaphysicsConcept
    subject: SubjectId = SubjectId.PHILOSOPHY_CORE
    domain: DomainId = DomainId.HUMANITIES
    level: CurriculumLevel

    professor_view: MetaphysicsConceptLessonProfessorView
    grad_view: MetaphysicsConceptLessonGradView
    teacher_view: MetaphysicsConceptLessonTeacherView
    practice: MetaphysicsConceptPracticeSet

# ============================================================
# Meta-philosophy: underdetermination and escalation to human
# ============================================================


class MetaPhilosophyAssessment(BaseModel):
    question_kind: str  # e.g., "technical", "ethical", "life_direction", "metaphysical"
    underdetermination_level: str  # "low", "medium", "high"
    frameworks_in_play: list[str] = []
    should_escalate_to_human: bool
    reasons_to_escalate: list[str] = []
    notes: list[str] = []


# ============================================================
# Domain-agnostic reasoning core (multi-step, tool-using)
# ============================================================

class ReasoningToolCall(BaseModel):
    """
    A single tool call the reasoning core can make to PRIME's internal corpus.
    For now, we model it abstractly; concrete layers decide how to route it.
    """
    name: str  # e.g., "philosophy_four_lens", "math_solver"
    input_payload: dict[str, Any]

class ReasoningTaskKind(str, Enum):
    EXPLANATION = "explanation"
    PROOF_OR_CHECK = "proof_or_check"
    DECISION = "decision"
    PLAN = "plan"
    CLASSIFICATION = "classification"
    ANALYSIS = "analysis"
    OTHER = "other"

class ReasoningTask(BaseModel):
    """
    Canonical schema for a reasoning problem, across all domains.
    """
    task_id: str
    natural_language_task: str

    # Optional hints to help the core choose strategies/tools
    domain_tag: str | None = None  # e.g., "philosophy", "math", "law", "medicine"
    subdomain_tag: str | None = None  # e.g., "ethics", "algebra", "contracts"

    given_facts: list[str] = []
    assumptions: list[str] = []
    constraints: list[str] = []  # e.g., "avoid violating human rights", "no long loops"

    desired_output_kind: ReasoningTaskKind = ReasoningTaskKind.EXPLANATION

    # Capabilities the core is allowed to use (by name, not direct code)
    allowed_tools: list[str] = []  # e.g., ["philosophy_four_lens", "math_linear_solver"]


class ReasoningStepKind(str, Enum):
    INTERPRET = "interpret"
    HYPOTHESIZE = "hypothesize"
    DECOMPOSE = "decompose"
    TOOL_CALL = "tool_call"
    DEDUCE = "deduce"
    CRITIQUE = "critique"
    REVISE = "revise"
    SUMMARIZE = "summarize"


class ReasoningStep(BaseModel):
    """
    One internal step of the reasoning core's multi-step loop.
    """
    index: int
    kind: ReasoningStepKind
    description: str  # what this step is trying to do, in human-readable terms
    inputs: list[str] = []  # references to previous steps or facts
    outputs: list[str] = []  # statements, intermediate conclusions, or notes
    tool_call: ReasoningToolCall | None = None  # populated if this step calls a tool
    tool_result_summary: str | None = None  # short summary of what the tool returned
    warnings: list[str] = []  # e.g., "possible contradiction", "low confidence"
    confidence: float | None = None  # optional 0.0 - 1.0


class ReasoningTrace(BaseModel):
    """
    Full reasoning trace: ordered steps plus any global flags.
    """
    steps: list[ReasoningStep]
    overall_confidence: float | None = None
    detected_contradictions: list[str] = []
    notes: list[str] = []


class ReasoningCoreRequest(BaseModel):
    """
    Entry point to the reasoning core.
    """
    task: ReasoningTask
    max_steps: int = 12  # cap on total reasoning steps per call


class ReasoningCoreResponse(BaseModel):
    """
    Output from the reasoning core: structured trace and distilled conclusions.
    """
    task_id: str
    trace: ReasoningTrace
    # A few distilled conclusions, separate from the full trace.
    key_conclusions: list[str]
    open_questions: list[str]

# ============================================================
# Reasoning memory: store and retrieve past reasoning traces
# ============================================================


class ReasoningTraceTag(BaseModel):
    """
    Lightweight tag for a reasoning episode, for retrieval and indexing.
    """
    domain: str  # e.g., "philosophy", "math"
    subdomain: str | None = None  # e.g., "ethics", "algebra"
    theme: str | None = None  # e.g., "career_vs_loyalty", "lying_to_protect"
    user_label: str | None = None  # optional free-form label you assign


class ReasoningOutcomeQuality(str, Enum):
    UNKNOWN = "unknown"
    GOOD = "good"
    MIXED = "mixed"
    BAD = "bad"
    CAUTIOUS = "cautious"

# --- Philosophy answer rubric models (global, reusable) -----------------------

class PhilosophyRubricDimension(str, Enum):
    CLARITY = "clarity"
    CHARITY = "charity"
    RIGOR = "rigor"
    HISTORY_AWARENESS = "history_awareness"


class PhilosophyRubricScore(BaseModel):
    dimension: PhilosophyRubricDimension
    score_1_to_5: int
    explanation: str


class PhilosophyRubricEvaluateRequest(BaseModel):
    question: str
    answer: str
    context: str | None = None  # e.g., "hs.history", "hs.ethics", "un.metaphysics"


class PhilosophyRubricEvaluateResponse(BaseModel):
    scores: list[PhilosophyRubricScore]
    overall_comment: str

class PhilosophyReflectionSession(BaseModel):
    """
    A single HS practice session that we want PRIME to reflect on.
    """
    level: Literal["hs"] = "hs"
    branch: str
    syllabus_unit_id: str
    practice_endpoint: str
    rubric_scores: list[PhilosophyRubricScore]
    prime_notes: str | None = None
    teacher_notes: str | None = None


class PhilosophyReflectionPrinciple(BaseModel):
    """
    A generalized principle or guideline PRIME should carry forward.
    """
    id: str
    rubric_dimension_id: str
    related_units: list[str]
    text: str


class PhilosophyReflectionSummary(BaseModel):
    """
    Summary of recent HS practice sessions plus generalized principles.
    """
    strengths: list[str]
    weaknesses: list[str]
    principles: list[PhilosophyReflectionPrinciple]

class ReasoningMemoryEntry(BaseModel):
    """
    A single stored reasoning trace with tags and basic metadata.
    """
    id: str  # unique id for this memory entry
    task: ReasoningTask
    response: ReasoningCoreResponse
    tags: ReasoningTraceTag

    # Metadata for stronger indexing and analysis
    created_at: datetime
    user_id: str | None = None  # who initiated the task (can be "raymond" for now)
    outcome_quality: ReasoningOutcomeQuality = ReasoningOutcomeQuality.UNKNOWN

    # Optional rubric evaluation for this reasoning episode (when available)
    rubric_scores: list[PhilosophyRubricScore] | None = None
    rubric_overall_comment: str | None = None

class ReasoningMemorySaveRequest(BaseModel):
    """
    Request to save a reasoning core response into memory.
    """
    entry_id: str
    task: ReasoningTask
    response: ReasoningCoreResponse
    tags: ReasoningTraceTag
    user_id: str | None = None
    outcome_quality: ReasoningOutcomeQuality = ReasoningOutcomeQuality.UNKNOWN


class ReasoningMemorySaveResponse(BaseModel):
    """
    Confirmation that a reasoning trace has been stored.
    """
    entry_id: str
    status: str  # e.g., "saved"


class ReasoningMemoryQuery(BaseModel):
    """
    Query for similar traces based on tags.
    For now, simple exact/contains matching on domain/subdomain/theme.
    """
    domain: str | None = None
    subdomain: str | None = None
    theme_contains: str | None = None  # substring search in tags.theme or task text
    limit: int = 5


class ReasoningMemoryQueryResponse(BaseModel):
    """
    Response with a small set of similar reasoning traces.
    """
    query: ReasoningMemoryQuery
    matches: list[ReasoningMemoryEntry]


# ============================================================
# Math-specific levels and subfields (you already defined)
# ============================================================

class MathLevel(str, Enum):
    SCHOOL_FOUNDATION = "school_foundation"      # K–8, early number sense and arithmetic
    SCHOOL_SECONDARY = "school_secondary"        # Algebra 1 → Calculus + school stats
    UNDERGRAD_CORE = "undergrad_core"            # Proof-based core analysis/algebra/topology
    GRAD_CORE = "grad_core"                      # Measure-theoretic analysis, grad algebra/topology
    DOCTORAL_CORE = "doctoral_core"              # PhD core in analysis/algebra/topology/probability
    DOCTORAL_SPECIALIZATION = "doctoral_specialization"  # Specialized research areas


class MathSubfield(str, Enum):
    # School foundation
    NUMBER_ARITHMETIC_FOUNDATIONS = "number_arithmetic_foundations"
    PREALGEBRA_EARLY_ALGEBRA = "prealgebra_early_algebra"
    SCHOOL_GEOMETRY = "school_geometry"
    PROB_STATS_SCHOOL = "prob_stats_school"
    CONSUMER_FINANCIAL_MATH = "consumer_financial_math"

    # Secondary
    ALGEBRA_1 = "algebra_1"
    ALGEBRA_2_FUNCTIONS = "algebra_2_functions"
    TRIG_PRECALC = "trig_precalc"
    CALCULUS_SCHOOL = "calculus_school"

    # Undergrad core
    UNDERGRAD_ANALYSIS = "undergrad_analysis"
    UNDERGRAD_LINEAR_ALGEBRA = "undergrad_linear_algebra"
    UNDERGRAD_ABSTRACT_ALGEBRA = "undergrad_abstract_algebra"
    UNDERGRAD_TOPO_GEOM = "undergrad_topology_geometry"
    UNDERGRAD_DISCRETE_COMBINATORICS = "undergrad_discrete_combinatorics"
    UNDERGRAD_PROB_STATS = "undergrad_probability_statistics"
    UNDERGRAD_DIFFEQ_NUMERICAL = "undergrad_differential_equations_numerical"

    # PhD core
    PHD_ANALYSIS_CORE = "phd_analysis_core"
    PHD_COMPLEX_ANALYSIS_CORE = "phd_complex_analysis_core"
    PHD_ALGEBRA_CORE = "phd_algebra_core"
    PHD_TOPO_GEOM_CORE = "phd_topology_geometry_core"
    PHD_PROBABILITY_CORE = "phd_probability_core"

    # PhD specializations (high-level buckets)
    PHD_SPEC_ALGEBRA_GEOMETRY_NUMBER = "phd_spec_algebra_geometry_number"
    PHD_SPEC_ANALYSIS_PDE = "phd_spec_analysis_pde"
    PHD_SPEC_TOPOLOGY_GEOMETRY = "phd_spec_topology_geometry"
    PHD_SPEC_APPLIED_NUMERICAL = "phd_spec_applied_numerical"
    PHD_SPEC_PROBABILITY_STOCHASTIC = "phd_spec_probability_stochastic"
    PHD_SPEC_STATISTICS_BIOSTAT = "phd_spec_statistics_biostat"


class MathExample(BaseModel):
    """
    A concrete example or counterexample of a math concept.
    """
    name: str                  # Short label for the example
    description: str           # Explanation in plain language
    is_counterexample: bool    # True if this is a counterexample
    details: dict[str, Any] | None = None  # Optional structured payload


class MathConcept(BaseModel):
    """
    A single mathematical concept with vocabulary, examples, and history hooks.
    """
    id: str                             # Unique id, e.g., "math_concept_zero"
    name: str                           # Human-readable name, e.g., "Zero"
    level: MathLevel                    # Overall depth band
    subfield: MathSubfield              # Where in the math universe it belongs
    definition: str                     # Core definition in plain language
    synonyms: list[str]                 # Alternative names, common phrases
    common_notation: list[str]         # Typical symbols / notations (e.g., "0", "ℕ")
    examples: list[MathExample]        # Canonical examples (5–7 over time)
    historical_notes: str | None = None  # Short history / origin notes
    related_concepts: list[str] = []   # IDs of related MathConcepts


class MathTeachingStep(BaseModel):
    """
    A single step in a teaching path over math concepts.
    """
    order: int                          # 1, 2, 3, ...
    concept_id: str                     # e.g., "math_concept_zero"
    headline: str                       # Short label, e.g., "Start at Zero"
    rationale: str                      # Why this step comes here in the path


class MathTeachingPath(BaseModel):
    """
    An ordered path through math concepts with explanations.
    """
    id: str                             # e.g., "number_arithmetic_foundations"
    level: MathLevel
    subfield: MathSubfield
    title: str
    description: str
    steps: list[MathTeachingStep]