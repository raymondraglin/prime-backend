from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.prime.math.foundations.number_sense import (
    NumberExample,
    NumberSenseSnapshot,
    CountingLesson,
    NumberReasoningResult,
    InfinitySeed,
    SimpleFraction,
    FractionFamily,
    FractionComparisonResult,
    NumberRange,
    DecimalMoneyExample,
    MoneyAmount,
    MoneyOperationResult,
    WordProblem,
    WordProblemKind,
    ComparisonPracticeRelation,
    ComparisonPracticeItem,
    ComparisonPracticeSet,
    get_example_numbers,
    get_number_sense_snapshot,
    get_counting_to_10_lesson,
    reason_about_small_integer,
    get_infinity_seed,
    get_money_fractions_family,
    compare_money_fractions,
    get_small_integer_range,
    get_positive_integer_range_to_100,
    get_basic_decimal_money_examples,
    perform_money_operation,
    get_basic_money_word_problems,
    generate_basic_comparison_practice,
    check_comparison_answer,
)


from app.prime.curriculum.models import (
    MathConcept,
    MathTeachingPath,
)

from app.prime.curriculum.math_concepts import (
    get_number_arithmetic_foundation_concepts,
    get_number_arithmetic_operations_and_comparisons,
    get_number_arithmetic_foundation_path,
    get_prealgebra_equations_basics,
    get_prealgebra_equations_basics_path,
    get_geometry_early_foundations,
    get_geometry_early_foundations_path,
    get_geometry_early_operations,
)

from app.prime.math.practice.equations import (
    EquationOperation,
    EquationPracticeItem,
    EquationPracticeSet,
    generate_one_step_equation_practice,
    check_one_step_equation_answer,
    EquationTwoStepPracticeItem,
    EquationTwoStepPracticeSet,
    generate_two_step_equation_practice,
    check_two_step_equation_answer,
    EquationBothSidesPracticeItem,
    EquationBothSidesPracticeSet,
    generate_equation_both_sides_practice,
    check_equation_both_sides_answer,
)

from app.prime.math.practice.geometry import (
    AngleType,
    AngleClassificationItem,
    AngleClassificationSet,
    generate_angle_classification_practice,
    PerimeterAreaProblemKind,
    PerimeterAreaItem,
    PerimeterAreaSet,
    generate_perimeter_area_practice,
)

from app.prime.math.practice.inequalities_models import (
    OneStepInequalityPracticeItem,
    OneStepInequalityPracticeSet,
)
from app.prime.math.practice.inequalities_two_step_models import (
    TwoStepInequalityPracticeItem,
    TwoStepInequalityPracticeSet,
)
from app.prime.math.practice.inequalities import (
    generate_one_step_inequality_practice,
    generate_two_step_inequality_practice,
)
from app.prime.math.practice.combine_like_terms import (
    CombineLikeTermsItem,
    CombineLikeTermsSet,
    generate_combine_like_terms_practice,
)
from app.prime.math.practice.distribute_and_combine import (
    DistributeAndCombineItem,
    DistributeAndCombineSet,
    generate_distribute_and_combine_practice,
)
from app.prime.math.practice.systems_2x2 import (
    System2x2Item,
    System2x2Set,
    generate_systems_2x2_practice,
)


import json
from pathlib import Path
from enum import Enum

LOG_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data" / "prime_logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
ATTEMPT_LOG_FILE = LOG_DIR / "attempts.jsonl"


def _append_attempt_to_file(entry: dict) -> None:
    """
    Append a single attempt entry as one JSON line to the attempts log file.
    """
    try:
        with ATTEMPT_LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        # Fail silently for now; we can add better error handling later.
        pass

def _load_recent_attempts(limit: int = 200) -> list[dict]:
    """
    Load recent attempts from the JSONL file, up to 'limit' lines from the end.
    """
    entries: list[dict] = []

    if not ATTEMPT_LOG_FILE.exists():
        return entries

    try:
        with ATTEMPT_LOG_FILE.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except Exception:
        return []

    # Keep only the last 'limit' entries
    if len(entries) > limit:
        entries = entries[-limit:]

    return entries

def _compute_streak(attempts: list[dict]) -> int:
    """
    Compute a signed streak:
    positive = consecutive correct,
    negative = consecutive incorrect,
    from the end of the list.
    """
    if not attempts:
        return 0

    streak = 0
    last_is_correct = attempts[-1].get("is_correct", False)

    for entry in reversed(attempts):
        is_correct = entry.get("is_correct", False)
        if is_correct == last_is_correct:
            streak += 1
        else:
            break

    return streak if last_is_correct else -streak


def _estimate_mastery(total: int, correct: int) -> str:
    """
    Very simple mastery estimate based on accuracy and volume.
    """
    if total == 0:
        return "low"

    accuracy = correct / total

    if total >= 20 and accuracy >= 0.85:
        return "high"
    if total >= 10 and accuracy >= 0.6:
        return "medium"
    return "low"

def _build_concept_index(concepts: list[MathConcept]) -> dict[str, MathConcept]:
    return {c.id: c for c in concepts}

# Very simple in-memory attempt log (per process)
attempt_log: list[dict] = []

# In-memory store for the most recently generated angle practice items (id -> item)
angle_practice_store: dict[str, AngleClassificationItem] = {}

router = APIRouter(
    prefix="/math",
    tags=["prime-math"],
)

class MathReasoningProblem(BaseModel):
    """
    A simple math word problem or equation-solving task.
    This is intentionally generic and language-based so we can reuse it widely.
    """
    problem_id: Optional[str] = None
    natural_language_problem: str
    hints: List[str] = []
    equation: Optional[str] = None  # optional structured equation


class MathReasoningStep(BaseModel):
    """
    One step in a math explanation.
    """
    description: str
    expression: Optional[str] = None
    comment: Optional[str] = None


class MathReasoningResponse(BaseModel):
    """
    Response for a math reasoning episode that PRIME can call from the reasoning core.
    """
    problem_id: Optional[str] = None
    solution_summary: str
    final_answer: str
    steps: List[MathReasoningStep]
    validity_checks: List[str] = []
    warnings: List[str] = []


@router.post(
    "/reason",
    response_model=MathReasoningResponse,
)
async def math_reason(
    problem: MathReasoningProblem,
) -> MathReasoningResponse:
    """
    Very simple placeholder math reasoning endpoint.

    For now, this does not actually parse and solve arbitrary math.
    It produces a structured, explain-like-I'm-5 style response
    that the reasoning core can wrap and critique.

    Later, this is where you can plug in a real solver.
    """
    steps: List[MathReasoningStep] = [
        MathReasoningStep(
            description="Restate the problem in my own words.",
            expression=None,
            comment=problem.natural_language_problem,
        ),
        MathReasoningStep(
            description="Notice that a full symbolic solution engine is not yet integrated.",
            expression=None,
            comment="I can outline how to approach the problem, but I won't compute a precise numeric answer here.",
        ),
    ]

    solution_summary = (
        "This is a math reasoning placeholder. PRIME has identified the problem, "
        "but a full symbolic/numeric solver is not yet wired in. "
        "The reasoning core can still use this to walk through how one would solve it."
    )
    final_answer = "solver_not_yet_implemented"

    validity_checks = [
        "Check that the problem is clearly stated (variables, units, and goal).",
        "Check that the proposed steps match the structure of the problem.",
    ]

    warnings = [
        "This endpoint is a scaffold; it does not compute a definitive numeric answer yet."
    ]

    return MathReasoningResponse(
        problem_id=problem.problem_id,
        solution_summary=solution_summary,
        final_answer=final_answer,
        steps=steps,
        validity_checks=validity_checks,
        warnings=warnings,
    )


class NumberSensePreview(BaseModel):
    description: str
    examples: list[NumberExample]


class NumberSenseFull(BaseModel):
    description: str
    snapshot: NumberSenseSnapshot


class CountingLessonResponse(BaseModel):
    description: str
    lesson: CountingLesson


class NumberPracticeRequest(BaseModel):
    value: int


class NumberPracticeResponse(BaseModel):
    description: str
    reasoning: NumberReasoningResult

class ComparisonPracticeRequest(BaseModel):
    count: int = 10  # how many items to generate


class ComparisonPracticeResponse(BaseModel):
    description: str
    items: list[ComparisonPracticeItem]

class CombineLikeTermsPracticeRequest(BaseModel):
    count: int = 10


class CombineLikeTermsPracticeResponse(BaseModel):
    description: str
    items: list[CombineLikeTermsItem]


class CombineLikeTermsAnswerCheckRequest(BaseModel):
    expression_text: str
    proposed_simplified: str


class CombineLikeTermsAnswerCheckResult(BaseModel):
    is_correct: bool
    correct_simplified: str
    explanation: str


class CombineLikeTermsAnswerCheckResponse(BaseModel):
    description: str
    result: CombineLikeTermsAnswerCheckResult

class DistributeAndCombinePracticeRequest(BaseModel):
    count: int = 10


class DistributeAndCombinePracticeResponse(BaseModel):
    description: str
    items: list[DistributeAndCombineItem]


class DistributeAndCombineAnswerCheckRequest(BaseModel):
    id: str
    expression_text: str
    proposed_simplified: str


class DistributeAndCombineAnswerCheckResult(BaseModel):
    is_correct: bool
    correct_simplified: str
    explanation: str

class Systems2x2PracticeRequest(BaseModel):
    count: int = 10


class Systems2x2PracticeResponse(BaseModel):
    description: str
    items: list[System2x2Item]


class Systems2x2AnswerCheckRequest(BaseModel):
    id: str
    equation1: str
    equation2: str
    proposed_x: int
    proposed_y: int


class Systems2x2AnswerCheckResult(BaseModel):
    is_correct: bool
    correct_x: int
    correct_y: int
    explanation: str


class Systems2x2AnswerCheckResponse(BaseModel):
    description: str
    result: Systems2x2AnswerCheckResult

class DistributeAndCombineAnswerCheckResponse(BaseModel):
    description: str
    result: DistributeAndCombineAnswerCheckResult


class ComparisonAnswerCheckRequest(BaseModel):
    left_value: int
    right_value: int
    # "less_than", "equal", "greater_than"
    answer_relation: str

class InequalityOneStepAnswerCheckRequest(BaseModel):
    inequality_id: str
    inequality_text: str  # e.g. "3x - 2 < 10"
    proposed_solution: str  # e.g. "x < 3"


class InequalityOneStepAnswerCheckResult(BaseModel):
    is_correct: bool
    correct_solution: str
    explanation: str


class InequalityOneStepAnswerCheckResponse(BaseModel):
    description: str
    result: InequalityOneStepAnswerCheckResult


class ComparisonAnswerCheckResult(BaseModel):
    is_correct: bool
    correct_relation: ComparisonPracticeRelation
    explanation: str


class ComparisonAnswerCheckResponse(BaseModel):
    description: str
    result: ComparisonAnswerCheckResult


class EquationPracticeRequest(BaseModel):
    count: int = 10  # how many items to generate

class PracticeKindSummary(BaseModel):
    kind: str
    total_attempts: int
    correct_attempts: int
    incorrect_attempts: int
    recent_streak: int  # positive for correct streak, negative for incorrect streak
    mastery_estimate: str  # "low", "medium", "high"

class PracticeSummaryResponse(BaseModel):
    description: str
    kinds: list[PracticeKindSummary]

class EquationPracticeResponse(BaseModel):
    description: str
    items: list[EquationPracticeItem]

class OneStepInequalityPracticeRequest(BaseModel):
    count: int = 10  # how many items to generate


class OneStepInequalityPracticeResponse(BaseModel):
    description: str
    items: list[OneStepInequalityPracticeItem]

class TwoStepInequalityPracticeRequest(BaseModel):
    count: int = 10


class TwoStepInequalityPracticeResponse(BaseModel):
    description: str
    items: list[TwoStepInequalityPracticeItem]


class InequalityTwoStepAnswerCheckRequest(BaseModel):
    inequality_id: str
    inequality_text: str    # e.g. "3x + 2 < 11"
    proposed_solution: str  # e.g. "x < 3"


class InequalityTwoStepAnswerCheckResult(BaseModel):
    is_correct: bool
    correct_solution: str
    explanation: str


class InequalityTwoStepAnswerCheckResponse(BaseModel):
    description: str
    result: InequalityTwoStepAnswerCheckResult

class EquationBothSidesPracticeRequest(BaseModel):
    count: int = 10  # how many items to generate


class EquationBothSidesPracticeResponse(BaseModel):
    description: str
    items: list[EquationBothSidesPracticeItem]


class EquationBothSidesAnswerCheckRequest(BaseModel):
    equation_text: str
    answer_value: int


class EquationBothSidesAnswerCheckResult(BaseModel):
    is_correct: bool
    correct_value: int
    explanation: str


class EquationBothSidesAnswerCheckResponse(BaseModel):
    description: str
    result: EquationBothSidesAnswerCheckResult


class EquationTwoStepPracticeRequest(BaseModel):
    count: int = 10  # how many items to generate


class EquationTwoStepPracticeResponse(BaseModel):
    description: str
    items: list[EquationTwoStepPracticeItem]


class EquationTwoStepAnswerCheckRequest(BaseModel):
    equation_text: str
    answer_value: int


class EquationTwoStepAnswerCheckResult(BaseModel):
    is_correct: bool
    correct_value: int
    explanation: str


class EquationTwoStepAnswerCheckResponse(BaseModel):
    description: str
    result: EquationTwoStepAnswerCheckResult


class EquationAnswerCheckRequest(BaseModel):
    equation_text: str
    operation: str  # "add" or "subtract"
    answer_value: int


class EquationAnswerCheckResult(BaseModel):
    is_correct: bool
    correct_value: int
    explanation: str


class EquationAnswerCheckResponse(BaseModel):
    description: str
    result: EquationAnswerCheckResult

class AnglePracticeRequest(BaseModel):
    count: int = 10


class AnglePracticeResponse(BaseModel):
    description: str
    items: list[AngleClassificationItem]


class AngleAnswerCheckRequest(BaseModel):
    angle_id: str
    chosen_type: AngleType


class AngleAnswerCheckResult(BaseModel):
    is_correct: bool
    correct_type: AngleType
    explanation: str


class AngleAnswerCheckResponse(BaseModel):
    description: str
    result: AngleAnswerCheckResult


class PerimeterAreaPracticeRequest(BaseModel):
    count: int = 10


class PerimeterAreaPracticeResponse(BaseModel):
    description: str
    items: list[PerimeterAreaItem]


class PerimeterAreaAnswerCheckRequest(BaseModel):
    problem_id: str
    answer_value: int


class PerimeterAreaAnswerCheckResult(BaseModel):
    is_correct: bool
    correct_value: int
    explanation: str


class PerimeterAreaAnswerCheckResponse(BaseModel):
    description: str
    result: PerimeterAreaAnswerCheckResult

class FoundationsResponse(BaseModel):
    description: str
    snapshot: NumberSenseSnapshot
    infinity_seed: InfinitySeed

class FractionsFamilyResponse(BaseModel):
    description: str
    family: FractionFamily

class FractionCompareRequest(BaseModel):
    left_numerator: int
    left_denominator: int
    right_numerator: int
    right_denominator: int

class FractionCompareResponse(BaseModel):
    description: str
    comparison: FractionComparisonResult

class NumberRangeResponse(BaseModel):
    description: str
    range: NumberRange


class DecimalMoneyResponse(BaseModel):
    description: str
    examples: list[DecimalMoneyExample]

class GeometryEarlyFoundationsResponse(BaseModel):
    description: str
    concepts: list[MathConcept]

class GeometryEarlyOperationsResponse(BaseModel):
    description: str
    concepts: list[MathConcept]

class GeometryEarlyTeachingPathResponse(BaseModel):
    description: str
    path: MathTeachingPath

class PrealgebraEquationsTeachingPathResponse(BaseModel):
    description: str
    path: MathTeachingPath

class MoneyOperationRequest(BaseModel):
    left_dollars: int
    left_cents: int
    right_dollars: int
    right_cents: int
    operation: str  # "add" or "subtract"

class MoneyOperationResponse(BaseModel):
    description: str
    result: MoneyOperationResult

class WordProblemsResponse(BaseModel):
    description: str
    problems: list[WordProblem]


class WordProblemCheckRequest(BaseModel):
    problem_id: str
    # For add/subtract problems
    answer_dollars: int | None = None
    answer_cents: int | None = None
    # For comparison problems
    answer_relation: str | None = None  # "less_than", "equal", "greater_than"


class WordProblemCheckResult(BaseModel):
    problem: WordProblem
    is_correct: bool
    feedback: str


class WordProblemCheckResponse(BaseModel):
    description: str
    result: WordProblemCheckResult

class NextProblemKind(str, Enum):
    COMPARISON_BASIC = "comparison_basic"
    EQUATION_ONE_STEP = "equation_one_step"
    EQUATION_TWO_STEP = "equation_two_step"
    EQUATION_BOTH_SIDES = "equation_both_sides"
    GEOMETRY_ANGLE_TYPE = "geometry_angle_type"
    GEOMETRY_PERIMETER_AREA = "geometry_perimeter_area"
    INEQUALITY_ONE_STEP = "inequality_one_step"
    INEQUALITY_TWO_STEP = "inequality_two_step"
    ALGEBRA_COMBINE_LIKE_TERMS = "algebra_combine_like_terms"
    ALGEBRA_DISTRIBUTE_AND_COMBINE = "algebra_distribute_and_combine"
    ALGEBRA_SYSTEMS_2X2 = "algebra_systems_2x2"


class NextProblem(BaseModel):
    kind: NextProblemKind
    payload: dict  # practice item as returned by the corresponding generator


class NextProblemResponse(BaseModel):
    description: str
    problem: NextProblem

class TeachStep(BaseModel):
    order: int
    concept_id: str
    concept_name: str
    headline: str
    rationale: str
    definition: str


class TeachPrealgebraEquationsResponse(BaseModel):
    description: str
    steps: list[TeachStep]
    practice_items: list[EquationPracticeItem]
    next_suggestion: str

class TeachAlgebraTwoStepEquationsResponse(BaseModel):
    description: str
    steps: list[TeachStep]
    practice_items: list[EquationTwoStepPracticeItem]
    next_suggestion: str


class TeachNumberArithmeticResponse(BaseModel):
    description: str
    steps: list[TeachStep]
    practice_items: list[ComparisonPracticeItem]
    next_suggestion: str


class TeachNumberArithmeticResponse(BaseModel):
    description: str
    steps: list[TeachStep]
    practice_items: list[ComparisonPracticeItem]
    next_suggestion: str

class TeachGeometryFoundationsResponse(BaseModel):
    description: str
    steps: list[TeachStep]
    practice_items: list[dict]  # placeholder for future geometry practice
    next_suggestion: str

class TeachBothSidesRequest(BaseModel):
    # Optional: allow the client to specify difficulty or number range later
    min_coeff: int | None = None
    max_coeff: int | None = None


class TeachBothSidesResponse(BaseModel):
    title: str
    key_points: list[str]
    worked_example_equation: str
    worked_example_steps: list[str]
    common_mistakes: list[str]

class TeachDistributeAndCombineResponse(BaseModel):
    description: str
    title: str
    key_points: list[str]
    worked_examples: list[str]
    common_mistakes: list[str]
    next_suggestion: str


class TeachSystems2x2Response(BaseModel):
    description: str
    title: str
    key_points: list[str]
    worked_examples: list[str]
    visuals: list[str]
    common_mistakes: list[str]
    next_suggestion: str


def _normalize_linear_expression(expr_text: str) -> str:
    """
    Normalize a linear expression in x by reusing the combine-like-terms parser.
    """
    expr = expr_text.replace(" ", "")

    total_coef = 0
    total_const = 0
    var = None

    i = 0
    sign = 1

    while i < len(expr):
        if expr[i] == "+":
            sign = 1
            i += 1
        elif expr[i] == "-":
            sign = -1
            i += 1
        else:
            sign = 1

        num_str = ""
        while i < len(expr) and expr[i].isdigit():
            num_str += expr[i]
            i += 1

        if i < len(expr) and expr[i].isalpha():
            if num_str == "":
                coef = 1
            else:
                coef = int(num_str)
            coef *= sign
            v = expr[i]
            if var is None:
                var = v
            total_coef += coef
            i += 1
        else:
            if num_str:
                val = int(num_str) * sign
                total_const += val

    def build_canonical(total_coef: int, total_const: int, var: str | None) -> str:
        def fmt_term(coef: int, v: str, first: bool) -> str:
            if coef == 0:
                return ""
            sign_char = "+" if coef > 0 else "-"
            abs_coef = abs(coef)
            if abs_coef == 1:
                core = v
            else:
                core = f"{abs_coef}{v}"
            if first:
                return core if coef > 0 else f"-{core}"
            else:
                return f" {sign_char} {core}"

        def fmt_const(c: int, first: bool) -> str:
            if c == 0:
                return ""
            sign_char = "+" if c > 0 else "-"
            abs_val = abs(c)
            if first:
                return str(abs_val) if c > 0 else f"-{abs_val}"
            else:
                return f" {sign_char} {abs_val}"

        parts: list[str] = []
        first = True
        if var is None:
            parts.append(str(total_const) if total_const != 0 else "0")
        else:
            t = fmt_term(total_coef, var, first)
            if t:
                parts.append(t)
                first = False
            c = fmt_const(total_const, first)
            if c:
                parts.append(c)
            if not parts:
                parts.append("0")
        return "".join(parts)

    return build_canonical(total_coef, total_const, var)

@router.post(
    "/teach/equation/both-sides",
    response_model=TeachBothSidesResponse,
    tags=["math-teach"],
)
async def teach_equation_both_sides(body: TeachBothSidesRequest | None = None):
    """
    Explain how to solve equations with variables on both sides in clear, student-ready language.
    """
    title = "Equations with Variables on Both Sides"

    key_points = [
        "Goal: get all the variable terms on one side and all the numbers on the other side.",
        "Whatever you add, subtract, multiply, or divide on one side, you must also do on the other side.",
        "Combine like terms on each side before you start moving terms across the equals sign.",
    ]

    worked_example_equation = "3x + 4 = 2x + 9"

    worked_example_steps = [
        "Step 1: Get variables on one side. Subtract 2x from both sides: 3x + 4 - 2x = 2x + 9 - 2x, so x + 4 = 9.",
        "Step 2: Get numbers on the other side. Subtract 4 from both sides: x + 4 - 4 = 9 - 4, so x = 5.",
        "Step 3: Check your answer. Plug x = 5 into the original: 3(5) + 4 = 15 + 4 = 19 and 2(5) + 9 = 10 + 9 = 19, so both sides match.",
    ]

    common_mistakes = [
        "Moving a term across the equals sign without changing its sign (for example, writing 3x + 4 = 2x + 9 ⇒ x + 4 = 9 instead of x + 4 = 9 after subtracting 2x on both sides).",
        "Forgetting to do the same operation to both sides when adding, subtracting, multiplying, or dividing.",
        "Dropping a term when combining like terms or doing arithmetic with negatives.",
    ]

    return TeachBothSidesResponse(
        title=title,
        key_points=key_points,
        worked_example_equation=worked_example_equation,
        worked_example_steps=worked_example_steps,
        common_mistakes=common_mistakes,
    )

@router.post(
    "/teach/algebra/distribute-and-combine",
    response_model=TeachDistributeAndCombineResponse,
    tags=["math-teach"],
)
async def teach_algebra_distribute_and_combine():
    """
    Teach the distributive property and combining like terms together,
    with professor-level precision and elementary-level patience.
    """
    title = "Distribute, Then Combine Like Terms"

    key_points = [
        "The distributive property says a(b + c) = ab + ac: you multiply each term inside the parentheses by the number outside.",
        "You must distribute to *every* term inside the parentheses, not just the first one.",
        "After you distribute, you look for like terms (same variable part) and combine them.",
        "You can think of this as 'expand first, then clean up' the expression.",
    ]

    worked_examples = [
        # Example 1: simple positive coefficients
        (
            "Example 1: 3(x + 2)\n"
            "Step 1: Distribute 3 to both x and 2: 3·x + 3·2 = 3x + 6.\n"
            "Step 2: There are no other like terms, so the simplified form is 3x + 6."
        ),
        # Example 2: negative outside, mix of signs inside
        (
            "Example 2: -2(x - 5)\n"
            "Step 1: Distribute -2: -2·x + (-2)·(-5) = -2x + 10.\n"
            "Step 2: There are no other like terms, so the simplified form is -2x + 10.\n"
            "Notice: multiplying two negatives (-2 and -5) gave a positive 10."
        ),
        # Example 3: distribute and then combine with extra terms
        (
            "Example 3: 3(x + 2) - 2(x - 1)\n"
            "Step 1: Distribute 3: 3(x + 2) = 3x + 6.\n"
            "Step 2: Distribute -2: -2(x - 1) = -2x + 2 (because -2·x = -2x and -2·(-1) = +2).\n"
            "Step 3: Put them together: 3x + 6 - 2x + 2.\n"
            "Step 4: Combine like terms: (3x - 2x) = 1x and (6 + 2) = 8, so the result is x + 8."
        ),
        # Example 4: parentheses plus extra x term
        (
            "Example 4: -3(2x - 1) + x\n"
            "Step 1: Distribute -3: -3(2x - 1) = -6x + 3.\n"
            "Step 2: Bring down the + x: -6x + 3 + x.\n"
            "Step 3: Combine like terms: (-6x + x) = -5x, so the result is -5x + 3."
        ),
    ]

    common_mistakes = [
        "Distributing to only one term: for 3(x + 2), writing 3x + 2 instead of 3x + 6.",
        "Dropping the negative sign: for -2(x - 5), writing -2x - 10 instead of -2x + 10.",
        "Stopping after distributing and forgetting to combine like terms.",
        "Changing the structure inside parentheses incorrectly before distributing, such as rearranging signs without care.",
    ]

    next_suggestion = (
        "Try a few practice problems where you first expand parentheses with distribution "
        "and then combine like terms. Once that feels comfortable, move on to equations "
        "where distribution and combining like terms are used to solve for x."
    )

    description = (
        "A step-by-step explanation of how to use the distributive property and then "
        "combine like terms, with examples that highlight common sign mistakes."
    )

    return TeachDistributeAndCombineResponse(
        description=description,
        title=title,
        key_points=key_points,
        worked_examples=worked_examples,
        common_mistakes=common_mistakes,
        next_suggestion=next_suggestion,
    )

@router.post(
    "/teach/algebra/systems-2x2",
    response_model=TeachSystems2x2Response,
    tags=["math-teach"],
)
async def teach_algebra_systems_2x2():
    """
    Teach systems of two linear equations in two variables (2x2 systems)
    with multiple methods and patient explanations.
    """
    title = "Systems of Two Linear Equations (2×2)"

    key_points = [
        "A system of two linear equations in two variables asks for one pair (x, y) that makes both equations true at the same time.",
        "Geometrically, each equation is a line. The solution is the point where the two lines meet (their intersection).",
        "There are three main kinds of solutions: one solution (lines cross once), no solution (parallel lines), infinitely many solutions (the same line).",
        "Algebraically, you can solve systems by substitution or by elimination. Both methods aim to reduce the system to a single equation in one variable.",
    ]

    worked_examples = [
        # Example 1: substitution
        (
            "Example 1 (Substitution):\n"
            "System:\n"
            "  y = 2x + 1\n"
            "  x + y = 7\n"
            "Step 1: From the first equation, we already have y in terms of x: y = 2x + 1.\n"
            "Step 2: Substitute into the second equation: x + (2x + 1) = 7.\n"
            "Step 3: Combine like terms: 3x + 1 = 7.\n"
            "Step 4: Solve for x: 3x = 6, so x = 2.\n"
            "Step 5: Plug back to find y: y = 2(2) + 1 = 5.\n"
            "Solution: (x, y) = (2, 5)."
        ),
        # Example 2: elimination
        (
            "Example 2 (Elimination):\n"
            "System:\n"
            "  2x + 3y = 13\n"
            "  -2x + y = -1\n"
            "Step 1: Notice the x-terms are 2x and -2x; if we add the equations, x will cancel.\n"
            "Step 2: Add the equations:\n"
            "   (2x + 3y) + (-2x + y) = 13 + (-1)\n"
            "   2x - 2x + 3y + y = 12\n"
            "   4y = 12\n"
            "Step 3: Solve for y: y = 3.\n"
            "Step 4: Substitute y = 3 back into one equation, for example 2x + 3y = 13:\n"
            "   2x + 3(3) = 13 → 2x + 9 = 13 → 2x = 4 → x = 2.\n"
            "Solution: (x, y) = (2, 3)."
        ),
        # Example 3: no solution
        (
            "Example 3 (No solution):\n"
            "System:\n"
            "  y = 2x + 1\n"
            "  y = 2x - 3\n"
            "Both lines have the same slope 2 but different intercepts 1 and -3.\n"
            "That means the lines are parallel and never meet, so there is no solution."
        ),
        # Example 4: infinitely many solutions
        (
            "Example 4 (Infinitely many solutions):\n"
            "System:\n"
            "  2x - y = 4\n"
            "  4x - 2y = 8\n"
            "The second equation is just 2 times the first: if you multiply 2x - y = 4 by 2,\n"
            "you get 4x - 2y = 8.\n"
            "This means both equations describe the same line, so every point on that line is a solution."
        ),
    ]

    visuals = [
        "Imagine each equation as a line on a graph: the solution is where the two lines cross.",
        "For substitution, picture sliding one equation into the other, so everything is written in terms of a single variable.",
        "For elimination, picture lining up the equations so that one variable cancels when you add or subtract the equations.",
    ]

    common_mistakes = [
        "Forgetting to distribute a minus sign or coefficient when substituting an expression (e.g. x + (2x + 1) but mis-writing the +1).",
        "Making arithmetic mistakes when adding or subtracting equations during elimination.",
        "Stopping after finding x or y and forgetting to solve for the other variable.",
        "Not checking the solution in both original equations to confirm it really works.",
    ]

    next_suggestion = (
        "Practice solving several 2×2 systems using both substitution and elimination. "
        "Then connect the algebra to the graph: sketch the lines and see how the point of intersection "
        "matches the (x, y) pair you found."
    )

    description = (
        "A guided introduction to systems of two linear equations in two variables, "
        "showing substitution, elimination, and how to interpret solutions geometrically."
    )

    return TeachSystems2x2Response(
        description=description,
        title=title,
        key_points=key_points,
        worked_examples=worked_examples,
        visuals=visuals,
        common_mistakes=common_mistakes,
        next_suggestion=next_suggestion,
    )

@router.get("/number-sense/preview", response_model=NumberSensePreview)
async def number_sense_preview():
    """
    Simple endpoint to verify PRIME's number-sense foundation wiring.
    """
    examples = get_example_numbers()
    return NumberSensePreview(
        description="PRIME early foundations: numbers, counting, integers, and number sense.",
        examples=examples,
    )


@router.get("/number-sense/core", response_model=NumberSenseFull)
async def number_sense_core():
    """
    More detailed view of PRIME's initial number-sense genetics:
    core numbers plus basic relationships.
    """
    snapshot = get_number_sense_snapshot()
    return NumberSenseFull(
        description="Core number concepts and relationships for PRIME's earliest number sense.",
        snapshot=snapshot,
    )


@router.get("/number-sense/counting-to-10", response_model=CountingLessonResponse)
async def number_sense_counting_to_10():
    """
    PRIME's first explicit counting lesson: 0 through 10, with words and money examples.
    """
    lesson = get_counting_to_10_lesson()
    return CountingLessonResponse(
        description="Counting from 0 to 10 with numerals, words, and simple money links.",
        lesson=lesson,
    )


@router.post("/number-sense/practice", response_model=NumberPracticeResponse)
async def number_sense_practice(payload: NumberPracticeRequest):
    """
    Practice reasoning over a single small integer (0..10).
    PRIME explains where it sits among neighbors and how it can represent money.
    """
    try:
        reasoning = reason_about_small_integer(payload.value)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return NumberPracticeResponse(
        description="Basic reasoning over a small integer using PRIME's counting-to-10 genetics.",
        reasoning=reasoning,
    )


@router.post(
    "/practice/inequalities/one-step/check",
    response_model=InequalityOneStepAnswerCheckResponse,
    tags=["math-practice"],
)
async def inequalities_one_step_check(
    payload: InequalityOneStepAnswerCheckRequest,
):
    """
    Check an answer for a one-step inequality problem.

    For now, we regenerate a batch of inequalities and look up the item by id.
    Later, you can persist a server-side store like angle_practice_store.
    """
    # Generate a pool to search; in future, replace with a store lookup.
    practice_set = generate_one_step_inequality_practice(count=50)
    by_id = {item.id: item for item in practice_set.items}

    if payload.inequality_id not in by_id:
        raise HTTPException(
            status_code=400,
            detail="Unknown inequality_id. Please request a new batch of inequality practice items.",
        )

    item = by_id[payload.inequality_id]
    correct_solution = item.solution_description.strip()
    proposed = payload.proposed_solution.strip()

    is_correct = (proposed == correct_solution)

    if is_correct:
        explanation = (
            f"Correct. {proposed} matches the expected solution. "
            f"{item.explanation}"
        )
    else:
        explanation = (
            f"Not quite. You answered {proposed}, but the expected solution is "
            f"{correct_solution}. {item.explanation}"
        )

    # Log attempt so the adaptive spine can see inequality_one_step performance.
    log_entry = {
        "kind": "inequality_one_step",
        "inequality_id": item.id,
        "inequality_text": item.inequality_text,
        "proposed_solution": proposed,
        "correct_solution": correct_solution,
        "requires_flip": item.requires_flip,
        "is_correct": is_correct,
    }
    attempt_log.append(log_entry)
    _append_attempt_to_file(log_entry)

    result = InequalityOneStepAnswerCheckResult(
        is_correct=is_correct,
        correct_solution=correct_solution,
        explanation=explanation,
    )

    return InequalityOneStepAnswerCheckResponse(
        description="Check result for a one-step inequality problem.",
        result=result,
    )

@router.post(
    "/practice/inequalities/two-step",
    response_model=TwoStepInequalityPracticeResponse,
    tags=["math-practice"],
)
async def inequalities_two_step_practice(
    payload: TwoStepInequalityPracticeRequest,
):
    """
    Generate two-step inequalities of the form ax + b < c or ax + b > c,
    where a can be negative (requiring the inequality sign to flip when dividing).
    """
    practice_set = generate_two_step_inequality_practice(count=payload.count)
    return TwoStepInequalityPracticeResponse(
        description=(
            "Two-step inequalities practice ax + b < c or ax + b > c, "
            "including cases where dividing by a negative requires flipping the inequality."
        ),
        items=practice_set.items,
    )


@router.post(
    "/practice/inequalities/two-step/check",
    response_model=InequalityTwoStepAnswerCheckResponse,
    tags=["math-practice"],
)
async def inequalities_two_step_check(
    payload: InequalityTwoStepAnswerCheckRequest,
):
    """
    Check an answer for a two-step inequality problem.

    For now, we assume the client sends back the correct solution from the
    generated item and we compare against that. This keeps things consistent
    between generate and check.
    """
    correct_solution = payload.proposed_solution.strip()  # client should send the correct solution
    proposed = payload.proposed_solution.strip()
    is_correct = (proposed == correct_solution)

    if is_correct:
        explanation = f"Correct. {proposed} matches the expected solution."
    else:
        explanation = (
            f"Not quite. The expected solution is {correct_solution}, "
            f"not {proposed}."
        )

    log_entry = {
        "kind": "inequality_two_step",
        "inequality_id": payload.inequality_id,
        "inequality_text": payload.inequality_text,
        "proposed_solution": proposed,
        "correct_solution": correct_solution,
        "is_correct": is_correct,
    }
    attempt_log.append(log_entry)
    _append_attempt_to_file(log_entry)

    result = InequalityTwoStepAnswerCheckResult(
        is_correct=is_correct,
        correct_solution=correct_solution,
        explanation=explanation,
    )

    return InequalityTwoStepAnswerCheckResponse(
        description="Check result for a two-step inequality problem.",
        result=result,
    )


@router.post(
    "/practice/comparison/basic",
    response_model=ComparisonPracticeResponse,
    tags=["math-practice"],
)
async def comparison_practice_basic(payload: ComparisonPracticeRequest):
    """
    Generate basic integer comparison practice items (less than, equal, greater than)
    using integers in a small range around zero.
    """
    practice_set = generate_basic_comparison_practice(count=payload.count)
    return ComparisonPracticeResponse(
        description=practice_set.description,
        items=practice_set.items,
    )

@router.post(
    "/practice/comparison/basic/check",
    response_model=ComparisonAnswerCheckResponse,
    tags=["math-practice"],
)
async def comparison_practice_basic_check(payload: ComparisonAnswerCheckRequest):
    """
    Check an answer for a basic integer comparison problem.
    """
    is_correct, explanation, correct_relation = check_comparison_answer(
        left_value=payload.left_value,
        right_value=payload.right_value,
        given_relation=payload.answer_relation,
    )

    result = ComparisonAnswerCheckResult(
        is_correct=is_correct,
        correct_relation=correct_relation,
        explanation=explanation,
    )

    log_entry = {
        "kind": "comparison_basic",
        "left_value": payload.left_value,
        "right_value": payload.right_value,
        "given_relation": payload.answer_relation,
        "is_correct": is_correct,
        "correct_relation": correct_relation.value,
    }
    attempt_log.append(log_entry)
    _append_attempt_to_file(log_entry)


    return ComparisonAnswerCheckResponse(
        description="Check result for a basic integer comparison problem.",
        result=result,
    )

@router.post(
    "/practice/equations/one-step",
    response_model=EquationPracticeResponse,
    tags=["math-practice"],
)
async def equations_one_step_practice(payload: EquationPracticeRequest):
    """
    Generate simple one-step equations of the form x + k = result or x - k = result,
    suitable for early prealgebra equation practice.
    """
    practice_set = generate_one_step_equation_practice(count=payload.count)
    return EquationPracticeResponse(
        description=practice_set.description,
        items=practice_set.items,
    )

@router.post(
    "/practice/equations/two-step",
    response_model=EquationTwoStepPracticeResponse,
    tags=["math-practice"],
)
async def equations_two_step_practice(payload: EquationTwoStepPracticeRequest):
    """
    Generate two-step equations of the form a*x + b = c
    with small integer coefficients and integer solutions.
    """
    practice_set: EquationTwoStepPracticeSet = generate_two_step_equation_practice(
        count=payload.count
    )
    return EquationTwoStepPracticeResponse(
        description=practice_set.description,
        items=practice_set.items,
    )

@router.post(
    "/practice/inequalities/one-step",
    response_model=OneStepInequalityPracticeResponse,
    tags=["math-practice"],
)
async def inequalities_one_step_practice(
    payload: OneStepInequalityPracticeRequest,
):
    """
    Generate simple one-step inequalities of the form ax + b < c or ax + b > c,
    suitable for early inequalities practice.
    """
    practice_set = generate_one_step_inequality_practice(count=payload.count)
    return OneStepInequalityPracticeResponse(
        description="One-step inequalities practice ax + b < c or ax + b > c with positive coefficients.",
        items=practice_set.items,
    )

@router.post(
    "/practice/equations/two-step/check",
    response_model=EquationTwoStepAnswerCheckResponse,
    tags=["math-practice"],
)
async def equations_two_step_practice_check(payload: EquationTwoStepAnswerCheckRequest):
    """
    Check an answer for a two-step equation of the form a*x + b = c.
    """
    is_correct, explanation, correct_value = check_two_step_equation_answer(
        equation_text=payload.equation_text,
        given_solution=payload.answer_value,
    )

    result = EquationTwoStepAnswerCheckResult(
        is_correct=is_correct,
        correct_value=correct_value,
        explanation=explanation,
    )

    log_entry = {
        "kind": "equation_two_step",
        "equation_text": payload.equation_text,
        "given_value": payload.answer_value,
        "is_correct": is_correct,
        "correct_value": correct_value,
    }
    attempt_log.append(log_entry)
    _append_attempt_to_file(log_entry)

    return EquationTwoStepAnswerCheckResponse(
        description="Check result for a two-step equation problem.",
        result=result,
    )

@router.post(
    "/practice/equations/both-sides",
    response_model=EquationBothSidesPracticeResponse,
    tags=["math-practice"],
)
async def equations_both_sides_practice(payload: EquationBothSidesPracticeRequest):
    """
    Generate equations with variables on both sides of the form a*x + b = c*x + d.
    """
    practice_set: EquationBothSidesPracticeSet = generate_equation_both_sides_practice(
        count=payload.count
    )
    return EquationBothSidesPracticeResponse(
        description=practice_set.description,
        items=practice_set.items,
    )


@router.post(
    "/practice/equations/both-sides/check",
    response_model=EquationBothSidesAnswerCheckResponse,
    tags=["math-practice"],
)
async def equations_both_sides_practice_check(
    payload: EquationBothSidesAnswerCheckRequest,
):
    """
    Check an answer for an equation with variables on both sides.
    """
    is_correct, explanation, correct_value = check_equation_both_sides_answer(
        equation_text=payload.equation_text,
        given_solution=payload.answer_value,
    )

    result = EquationBothSidesAnswerCheckResult(
        is_correct=is_correct,
        correct_value=correct_value,
        explanation=explanation,
    )

    log_entry = {
        "kind": "equation_both_sides",
        "equation_text": payload.equation_text,
        "given_value": payload.answer_value,
        "is_correct": is_correct,
        "correct_value": correct_value,
    }
    attempt_log.append(log_entry)
    _append_attempt_to_file(log_entry)

    return EquationBothSidesAnswerCheckResponse(
        description="Check result for an equation with variables on both sides.",
        result=result,
    )

@router.post(
    "/practice/equations/one-step/check",
    response_model=EquationAnswerCheckResponse,
    tags=["math-practice"],
)
async def equations_one_step_practice_check(payload: EquationAnswerCheckRequest):
    """
    Check an answer for a one-step equation of the form x + k = result or x - k = result.
    """
    is_correct, explanation, correct_value = check_one_step_equation_answer(
        equation_text=payload.equation_text,
        operation=payload.operation,
        given_solution=payload.answer_value,
    )

    result = EquationAnswerCheckResult(
        is_correct=is_correct,
        correct_value=correct_value,
        explanation=explanation,
    )

    log_entry = {
        "kind": "equation_one_step",
        "equation_text": payload.equation_text,
        "operation": payload.operation,
        "given_value": payload.answer_value,
        "is_correct": is_correct,
        "correct_value": correct_value,
    }
    attempt_log.append(log_entry)
    _append_attempt_to_file(log_entry)


    return EquationAnswerCheckResponse(
        description="Check result for a one-step equation problem.",
        result=result,
    )

@router.post(
    "/practice/algebra/combine-like-terms",
    response_model=CombineLikeTermsPracticeResponse,
    tags=["math-practice"],
)
async def algebra_combine_like_terms_practice(
    payload: CombineLikeTermsPracticeRequest,
):
    """
    Generate expressions that require combining like terms, e.g. 3x + 4x - 2.
    """
    practice_set = generate_combine_like_terms_practice(count=payload.count)
    return CombineLikeTermsPracticeResponse(
        description="Combine-like-terms practice: simplify expressions by combining like variable terms and constants.",
        items=practice_set.items,
    )

@router.post(
    "/practice/algebra/distribute-and-combine",
    response_model=DistributeAndCombinePracticeResponse,
    tags=["math-practice"],
)
async def algebra_distribute_and_combine_practice(
    payload: DistributeAndCombinePracticeRequest,
):
    """
    Generate expressions that require distributing across parentheses and
    then combining like terms, e.g. 3(x + 2) - 2(x - 1).
    """
    practice_set: DistributeAndCombineSet = generate_distribute_and_combine_practice(
        count=payload.count
    )
    return DistributeAndCombinePracticeResponse(
        description=practice_set.description,
        items=practice_set.items,
    )


@router.post(
    "/practice/algebra/systems-2x2",
    response_model=Systems2x2PracticeResponse,
    tags=["math-practice"],
)
async def algebra_systems_2x2_practice(
    payload: Systems2x2PracticeRequest,
):
    """
    Generate systems of two linear equations in two variables (2x2) with integer solutions.
    """
    practice_set: System2x2Set = generate_systems_2x2_practice(count=payload.count)
    return Systems2x2PracticeResponse(
        description=practice_set.description,
        items=practice_set.items,
    )

@router.post(
    "/practice/algebra/systems-2x2/check",
    response_model=Systems2x2AnswerCheckResponse,
    tags=["math-practice"],
)
async def algebra_systems_2x2_check(
    payload: Systems2x2AnswerCheckRequest,
):
    """
    Check a student's proposed solution (x, y) for a 2x2 linear system.

    Temporary simple behavior: treat the proposed (x, y) as the reference
    so we can exercise the endpoint and logging without a server-side store.
    """
    correct_x = payload.proposed_x
    correct_y = payload.proposed_y

    proposed_x = payload.proposed_x
    proposed_y = payload.proposed_y

    is_correct = (proposed_x == correct_x) and (proposed_y == correct_y)

    if is_correct:
        explanation = (
            f"Correct. (x, y) = ({proposed_x}, {proposed_y}) satisfies both equations."
        )
    else:
        explanation = (
            f"Not quite. The expected solution is (x, y) = ({correct_x}, {correct_y}), "
            f"not ({proposed_x}, {proposed_y})."
        )

    log_entry = {
        "kind": "algebra_systems_2x2",
        "id": payload.id,
        "equation1": payload.equation1,
        "equation2": payload.equation2,
        "proposed_x": proposed_x,
        "proposed_y": proposed_y,
        "correct_x": correct_x,
        "correct_y": correct_y,
        "is_correct": is_correct,
    }
    attempt_log.append(log_entry)
    _append_attempt_to_file(log_entry)

    result = Systems2x2AnswerCheckResult(
        is_correct=is_correct,
        correct_x=correct_x,
        correct_y=correct_y,
        explanation=explanation,
    )

    return Systems2x2AnswerCheckResponse(
        description="Check result for a 2x2 linear system.",
        result=result,
    )


@router.post(
    "/practice/algebra/distribute-and-combine/check",
    response_model=DistributeAndCombineAnswerCheckResponse,
    tags=["math-practice"],
)
async def algebra_distribute_and_combine_check(
    payload: DistributeAndCombineAnswerCheckRequest,
):
    """
    Check an answer for a distribute-and-combine problem.

    We normalize both the original expression and the proposed simplification
    to a canonical linear form, then compare them.
    """
    normalized_original = _normalize_linear_expression(payload.expression_text)
    normalized_proposed = _normalize_linear_expression(payload.proposed_simplified)

    is_correct = normalized_original == normalized_proposed

    if is_correct:
        explanation = (
            f"Correct. {payload.proposed_simplified} is equivalent to "
            f"{normalized_original} after distributing and combining like terms."
        )
    else:
        explanation = (
            f"Not quite. Your answer simplifies to {normalized_proposed}, "
            f"but the correct simplified expression is {normalized_original}."
        )

    log_entry = {
        "kind": "algebra_distribute_and_combine",
        "id": payload.id,
        "expression_text": payload.expression_text,
        "proposed_simplified": payload.proposed_simplified,
        "normalized_original": normalized_original,
        "normalized_proposed": normalized_proposed,
        "is_correct": is_correct,
    }
    attempt_log.append(log_entry)
    _append_attempt_to_file(log_entry)

    result = DistributeAndCombineAnswerCheckResult(
        is_correct=is_correct,
        correct_simplified=normalized_original,
        explanation=explanation,
    )

    return DistributeAndCombineAnswerCheckResponse(
        description="Check result for a distribute-and-combine problem.",
        result=result,
    )

@router.post(
    "/practice/algebra/combine-like-terms/check",
    response_model=CombineLikeTermsAnswerCheckResponse,
    tags=["math-practice"],
)
async def algebra_combine_like_terms_check(
    payload: CombineLikeTermsAnswerCheckRequest,
):
    """
    Check an answer for a combine-like-terms problem.

    We parse the given expression_text and the proposed_simplified,
    combine like terms for the same variable, and compare the normalized forms.
    """

    def parse_and_combine(expr_str: str):
        expr = expr_str.replace(" ", "")
        total_coef = 0
        total_const = 0
        var = None

        i = 0
        sign = 1

        while i < len(expr):
            if expr[i] == "+":
                sign = 1
                i += 1
            elif expr[i] == "-":
                sign = -1
                i += 1
            else:
                sign = 1

            num_str = ""
            while i < len(expr) and expr[i].isdigit():
                num_str += expr[i]
                i += 1

            if i < len(expr) and expr[i].isalpha():
                if num_str == "":
                    coef = 1
                else:
                    coef = int(num_str)
                coef *= sign
                v = expr[i]
                if var is None:
                    var = v
                total_coef += coef
                i += 1
            else:
                if num_str:
                    val = int(num_str) * sign
                    total_const += val

        return total_coef, total_const, var

    def build_canonical(total_coef: int, total_const: int, var: str | None) -> str:
        def fmt_term(coef: int, v: str, first: bool) -> str:
            if coef == 0:
                return ""
            sign_char = "+" if coef > 0 else "-"
            abs_coef = abs(coef)
            if abs_coef == 1:
                core = v
            else:
                core = f"{abs_coef}{v}"
            if first:
                return core if coef > 0 else f"-{core}"
            else:
                return f" {sign_char} {core}"

        def fmt_const(c: int, first: bool) -> str:
            if c == 0:
                return ""
            sign_char = "+" if c > 0 else "-"
            abs_val = abs(c)
            if first:
                return str(abs_val) if c > 0 else f"-{abs_val}"
            else:
                return f" {sign_char} {abs_val}"

        parts = []
        first = True
        if var is None:
            parts.append(str(total_const) if total_const != 0 else "0")
        else:
            t = fmt_term(total_coef, var, first)
            if t:
                parts.append(t)
                first = False
            c = fmt_const(total_const, first)
            if c:
                parts.append(c)
            if not parts:
                parts.append("0")
        return "".join(parts)

    # Normalize the original expression
    coef_orig, const_orig, var = parse_and_combine(payload.expression_text)
    correct = build_canonical(coef_orig, const_orig, var)

    # Normalize the proposed simplification too
    coef_prop, const_prop, var_prop = parse_and_combine(payload.proposed_simplified)
    proposed_normalized = build_canonical(coef_prop, const_prop, var_prop or var or "x")

    is_correct = (proposed_normalized == correct)

    explanation = (
        f"Start with {payload.expression_text}. "
        f"Combine the {var or 'x'}-terms to get {coef_orig}{(var or 'x') if var is not None or coef_orig != 0 else ''} "
        f"and the constant {const_orig}. "
        f"The simplified expression is {correct}."
    )
    if is_correct:
        explanation = f"Correct. {payload.proposed_simplified} is equivalent to {correct}. " + explanation
    else:
        explanation = (
            f"Not quite. Your answer simplifies to {proposed_normalized}, "
            f"but the correct simplified expression is {correct}. "
            + explanation
        )

    log_entry = {
        "kind": "algebra_combine_like_terms",
        "expression_text": payload.expression_text,
        "proposed_simplified": payload.proposed_simplified,
        "normalized_proposed": proposed_normalized,
        "correct_simplified": correct,
        "is_correct": is_correct,
    }
    attempt_log.append(log_entry)
    _append_attempt_to_file(log_entry)

    result = CombineLikeTermsAnswerCheckResult(
        is_correct=is_correct,
        correct_simplified=correct,
        explanation=explanation,
    )

    return CombineLikeTermsAnswerCheckResponse(
        description="Check result for a combine-like-terms problem.",
        result=result,
    )


@router.post(
    "/practice/geometry/angles",
    response_model=AnglePracticeResponse,
    tags=["math-practice"],
)
async def geometry_angle_practice(payload: AnglePracticeRequest):
    """
    Generate angle classification practice items (acute, right, obtuse)
    and store them server-side so they can be checked by angle_id.
    """
    global angle_practice_store

    practice_set: AngleClassificationSet = generate_angle_classification_practice(
        count=payload.count
    )

    # Refresh the in-memory store with the latest batch
    angle_practice_store = {item.id: item for item in practice_set.items}

    return AnglePracticeResponse(
        description=practice_set.description,
        items=practice_set.items,
    )


@router.post(
    "/practice/geometry/angles/check",
    response_model=AngleAnswerCheckResponse,
    tags=["math-practice"],
)
async def geometry_angle_check(payload: AngleAnswerCheckRequest):
    """
    Check an answer for an angle classification problem by angle_id,
    using the last generated batch stored in memory.
    """
    if payload.angle_id not in angle_practice_store:
        raise HTTPException(
            status_code=400,
            detail="Unknown angle_id. Please request a new batch of angle practice items.",
        )

    item = angle_practice_store[payload.angle_id]
    is_correct = payload.chosen_type == item.correct_type

    if is_correct:
        explanation = f"Correct. {item.explanation}"
    else:
        explanation = (
            f"Not quite. The angle {item.degrees}° is {item.correct_type.value}, "
            f"not {payload.chosen_type.value}. {item.explanation}"
        )

    result = AngleAnswerCheckResult(
        is_correct=is_correct,
        correct_type=item.correct_type,
        explanation=explanation,
    )

    log_entry = {
        "kind": "geometry_angle_type",
        "angle_id": item.id,
        "degrees": item.degrees,
        "chosen_type": payload.chosen_type.value,
        "correct_type": item.correct_type.value,
        "is_correct": is_correct,
    }
    attempt_log.append(log_entry)
    _append_attempt_to_file(log_entry)

    return AngleAnswerCheckResponse(
        description="Check result for an angle classification problem.",
        result=result,
    )


@router.post(
    "/practice/geometry/perimeter-area",
    response_model=PerimeterAreaPracticeResponse,
    tags=["math-practice"],
)
async def geometry_perimeter_area_practice(payload: PerimeterAreaPracticeRequest):
    """
    Generate perimeter and area practice items for squares and rectangles.
    """
    practice_set: PerimeterAreaSet = generate_perimeter_area_practice(count=payload.count)
    return PerimeterAreaPracticeResponse(
        description=practice_set.description,
        items=practice_set.items,
    )


@router.post(
    "/practice/geometry/perimeter-area/check",
    response_model=PerimeterAreaAnswerCheckResponse,
    tags=["math-practice"],
)
async def geometry_perimeter_area_check(payload: PerimeterAreaAnswerCheckRequest):
    """
    Check an answer for a perimeter or area geometry problem.
    """
    practice_set: PerimeterAreaSet = generate_perimeter_area_practice(count=50)
    by_id = {item.id: item for item in practice_set.items}

    if payload.problem_id not in by_id:
        raise HTTPException(status_code=400, detail="Unknown problem_id.")

    item = by_id[payload.problem_id]
    is_correct = payload.answer_value == item.correct_value

    if is_correct:
        explanation = f"Correct. {item.explanation}"
    else:
        explanation = (
            f"Not quite. The correct value is {item.correct_value}, not {payload.answer_value}. "
            f"{item.explanation}"
        )

    result = PerimeterAreaAnswerCheckResult(
        is_correct=is_correct,
        correct_value=item.correct_value,
        explanation=explanation,
    )

    log_entry = {
        "kind": "geometry_perimeter_area",
        "problem_id": item.id,
        "kind_detail": item.kind.value,
        "length": item.length,
        "width": item.width,
        "given_value": payload.answer_value,
        "correct_value": item.correct_value,
        "is_correct": is_correct,
    }
    attempt_log.append(log_entry)
    _append_attempt_to_file(log_entry)

    return PerimeterAreaAnswerCheckResponse(
        description="Check result for a perimeter/area geometry problem.",
        result=result,
    )

@router.get("/number-sense/foundations", response_model=FoundationsResponse)
async def number_sense_foundations():
    """
    Foundations bundle: core numbers near zero, basic relationships
    (successor, greater/less than, opposite sign), and a first seed of 'infinity'.
    """
    snapshot = get_number_sense_snapshot()
    infinity_seed = get_infinity_seed()
    return FoundationsResponse(
        description=(
            "PRIME's earliest number foundations: small integers around zero, "
            "comparison language, and the idea that counting can go on without end."
        ),
        snapshot=snapshot,
        infinity_seed=infinity_seed,
    )

@router.get("/fractions/money/basic", response_model=FractionsFamilyResponse)
async def money_fractions_basic():
    """
    Get the basic money-related fractions between 0 and 1 that PRIME knows so far.
    """
    family = get_money_fractions_family()
    return FractionsFamilyResponse(
        description="Basic fractions between 0 and 1 tied to simple money examples.",
        family=family,
    )

@router.get("/number-sense/range/small", response_model=NumberRangeResponse)
async def number_range_small():
    """
    Integers from -10 to 10 as a structured number line segment.
    """
    rng = get_small_integer_range()
    return NumberRangeResponse(
        description="Small integer range around zero, from -10 to 10.",
        range=rng,
    )


@router.get("/number-sense/range/0-100", response_model=NumberRangeResponse)
async def number_range_0_100():
    """
    Integers from 0 to 100 as a structured number line segment.
    """
    rng = get_positive_integer_range_to_100()
    return NumberRangeResponse(
        description="Positive integer range from 0 to 100.",
        range=rng,
    )


@router.get("/decimals/money/basic", response_model=DecimalMoneyResponse)
async def decimals_money_basic():
    """
    Basic decimal values between 0 and 1 with money and fraction connections.
    """
    examples = get_basic_decimal_money_examples()
    return DecimalMoneyResponse(
        description="Basic decimals (0.10, 0.25, 0.50, 0.75, 1.00) with money and fraction links.",
        examples=examples,
    )


@router.post("/money/operate", response_model=MoneyOperationResponse)
async def money_operate(payload: MoneyOperationRequest):
    """
    Perform simple addition or subtraction of small dollar amounts.
    """
    try:
        result = perform_money_operation(
            payload.left_dollars,
            payload.left_cents,
            payload.right_dollars,
            payload.right_cents,
            payload.operation,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return MoneyOperationResponse(
        description="Result of a simple money operation in dollars and cents.",
        result=result,
    )

class NumberArithmeticConceptsResponse(BaseModel):
    description: str
    concepts: list[MathConcept]


@router.get(
    "/concepts/number-arithmetic",
    response_model=NumberArithmeticConceptsResponse,
    tags=["math-concepts"],
)
async def get_number_arithmetic_concepts():
    """
    Core math concepts for school foundation:
    number & arithmetic foundations (zero, one, naturals, negatives, integers).
    """
    concepts = get_number_arithmetic_foundation_concepts()
    return NumberArithmeticConceptsResponse(
        description=(
            "Core math concepts for early number sense: zero, one, natural numbers, "
            "negative numbers, and integers, with examples and brief history notes."
        ),
        concepts=concepts,
    )

class NumberArithmeticOpsCompareConceptsResponse(BaseModel):
    description: str
    concepts: list[MathConcept]

class PrealgebraEquationsBasicsResponse(BaseModel):
    description: str
    concepts: list[MathConcept]

class AttemptLogEntry(BaseModel):
    kind: str
    data: dict


class AttemptLogResponse(BaseModel):
    count: int
    entries: list[dict]


@router.get(
    "/practice/attempt-log",
    response_model=AttemptLogResponse,
    tags=["math-practice"],
)
async def get_attempt_log():
    """
    Return a snapshot of the in-memory attempt log (for debugging / inspection).
    """
    return AttemptLogResponse(
        count=len(attempt_log),
        entries=attempt_log,
    )

@router.get(
    "/concepts/number-arithmetic/ops-and-comparisons",
    response_model=NumberArithmeticOpsCompareConceptsResponse,
    tags=["math-concepts"],
)
async def get_number_arithmetic_operations_and_comparisons_concepts():
    """
    Early-school concepts for basic operations (addition, subtraction) and
    comparison relations (less than, greater than, equal to).
    """
    concepts = get_number_arithmetic_operations_and_comparisons()
    return NumberArithmeticOpsCompareConceptsResponse(
        description=(
            "Early-school number and arithmetic concepts focused on basic operations "
            "(addition, subtraction) and comparison relations (less than, greater than, equal to)."
        ),
        concepts=concepts,
    )

@router.get(
    "/concepts/prealgebra/equations-basics",
    response_model=PrealgebraEquationsBasicsResponse,
    tags=["math-concepts"],
)
async def get_prealgebra_equations_basics_concepts():
    """
    Prealgebra & early algebra concepts for equation thinking:
    expression, equation, unknown, and solving an equation.
    """
    concepts = get_prealgebra_equations_basics()
    return PrealgebraEquationsBasicsResponse(
        description=(
            "Prealgebra and early algebra concepts focused on equation thinking: "
            "expressions, equations, unknowns, and solving equations."
        ),
        concepts=concepts,
    )

@router.get(
    "/concepts/geometry/early-foundations",
    response_model=GeometryEarlyFoundationsResponse,
    tags=["math-concepts"],
)
async def get_geometry_early_foundations_concepts():
    """
    School geometry concepts for early foundations:
    point, line, line segment, ray, angle, and basic shapes.
    """
    concepts = get_geometry_early_foundations()
    return GeometryEarlyFoundationsResponse(
        description=(
            "Early-school geometry concepts focused on basic geometric objects: "
            "points, lines, line segments, rays, angles, and simple shapes."
        ),
        concepts=concepts,
    )

@router.get(
    "/concepts/geometry/early-operations",
    response_model=GeometryEarlyOperationsResponse,
    tags=["math-concepts"],
)
async def get_geometry_early_operations_concepts():
    """
    School geometry concepts for early operations and classifications:
    angle types (right, acute, obtuse), perimeter, and area.
    """
    concepts = get_geometry_early_operations()
    return GeometryEarlyOperationsResponse(
        description=(
            "Early-school geometry operations and classifications: right, acute, and obtuse angles, "
            "and the ideas of perimeter and area for simple shapes."
        ),
        concepts=concepts,
    )

@router.get(
    "/paths/geometry/early-foundations",
    response_model=GeometryEarlyTeachingPathResponse,
    tags=["math-paths"],
)
async def get_geometry_early_foundations_teaching_path():
    """
    Ordered teaching path for early-school geometry foundations.
    """
    path = get_geometry_early_foundations_path()
    return GeometryEarlyTeachingPathResponse(
        description=(
            "Teaching path for early-school geometry foundations, ordering concepts "
            "from points and lines through segments, rays, angles, and basic shapes."
        ),
        path=path,
    )

@router.get("/word-problems/money/basic", response_model=WordProblemsResponse)
async def word_problems_money_basic():
    """
    Get a small bank of basic money-related word problems.
    """
    problems = get_basic_money_word_problems()
    return WordProblemsResponse(
        description="Basic money word problems for addition, subtraction, and comparison.",
        problems=problems,
    )

class NumberArithmeticTeachingPathResponse(BaseModel):
    description: str
    path: MathTeachingPath

@router.get(
    "/paths/number-arithmetic/foundations",
    response_model=NumberArithmeticTeachingPathResponse,
    tags=["math-paths"],
)
async def get_number_arithmetic_foundations_path():
    """
    Ordered teaching path for early number and arithmetic foundations.
    """
    path = get_number_arithmetic_foundation_path()
    return NumberArithmeticTeachingPathResponse(
        description=(
            "Teaching path for early number and arithmetic foundations, ordering concepts "
            "from zero and one through integers, operations, and basic comparisons."
        ),
        path=path,
    )

@router.get(
    "/paths/prealgebra/equations-basics",
    response_model=PrealgebraEquationsTeachingPathResponse,
    tags=["math-paths"],
)
async def get_prealgebra_equations_basics_teaching_path():
    """
    Ordered teaching path for prealgebra & early algebra equation-thinking basics.
    """
    path = get_prealgebra_equations_basics_path()
    return PrealgebraEquationsTeachingPathResponse(
        description=(
            "Teaching path for prealgebra equation basics, ordering concepts from expressions "
            "to equations, unknowns, and solving equations."
        ),
        path=path,
    )

@router.post("/word-problems/money/check", response_model=WordProblemCheckResponse)
async def word_problems_money_check(payload: WordProblemCheckRequest):
    """
    Check an answer to a basic money word problem.
    """
    problems = get_basic_money_word_problems()
    by_id = {p.id: p for p in problems}

    if payload.problem_id not in by_id:
        raise HTTPException(status_code=400, detail="Unknown problem_id.")

    problem = by_id[payload.problem_id]

    # Addition / subtraction problems: check numeric answer
    if problem.kind in {WordProblemKind.MONEY_ADD, WordProblemKind.MONEY_SUBTRACT}:
        if payload.answer_dollars is None or payload.answer_cents is None:
            raise HTTPException(
                status_code=400,
                detail="answer_dollars and answer_cents are required for this problem.",
            )

        given = MoneyAmount(dollars=payload.answer_dollars, cents=payload.answer_cents)
        correct = problem.correct_result

        if correct is None:
            raise HTTPException(status_code=500, detail="Problem missing correct_result.")

        is_correct = given.total_cents() == correct.total_cents()

        if is_correct:
            feedback = (
                f"Correct: {given.format()} matches the expected answer. "
                f"{problem.explanation}"
            )
        else:
            feedback = (
                f"Not quite. You answered {given.format()}, but the expected answer is "
                f"{correct.format()}. {problem.explanation}"
            )

        result = WordProblemCheckResult(
            problem=problem,
            is_correct=is_correct,
            feedback=feedback,
        )
        return WordProblemCheckResponse(
            description="Check result for a money addition/subtraction word problem.",
            result=result,
        )

    # Comparison problems: check relation
    if problem.kind == WordProblemKind.MONEY_COMPARE:
        if payload.answer_relation is None:
            raise HTTPException(
                status_code=400,
                detail="answer_relation is required for this comparison problem.",
            )

        correct_rel = problem.correct_relation
        if correct_rel is None:
            raise HTTPException(status_code=500, detail="Problem missing correct_relation.")

        is_correct = payload.answer_relation == correct_rel

        if is_correct:
            feedback = (
                f"Correct: your relation '{payload.answer_relation}' matches the expected relation. "
                f"{problem.explanation}"
            )
        else:
            feedback = (
                f"Not quite. You answered relation '{payload.answer_relation}', "
                f"but the expected relation is '{correct_rel}'. {problem.explanation}"
            )

        result = WordProblemCheckResult(
            problem=problem,
            is_correct=is_correct,
            feedback=feedback,
        )
        return WordProblemCheckResponse(
            description="Check result for a money comparison word problem.",
            result=result,
        )

    raise HTTPException(status_code=500, detail="Unhandled problem kind.")


@router.post("/fractions/money/compare", response_model=FractionCompareResponse)
async def money_fractions_compare(payload: FractionCompareRequest):
    """
    Compare two basic money fractions (from the predefined family)
    and explain which represents more/less of the whole.
    """
    try:
        comparison = compare_money_fractions(
            payload.left_numerator,
            payload.left_denominator,
            payload.right_numerator,
            payload.right_denominator,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return FractionCompareResponse(
        description="Comparison of two basic money fractions in terms of the whole and money value.",
        comparison=comparison,
    )

@router.get("/number-sense/range/small", response_model=NumberRangeResponse)
async def number_range_small():
    """
    Integers from -10 to 10 as a structured number line segment.
    """
    rng = get_small_integer_range()
    return NumberRangeResponse(
        description="Small integer range around zero, from -10 to 10.",
        range=rng,
    )


@router.get("/number-sense/range/0-100", response_model=NumberRangeResponse)
async def number_range_0_100():
    """
    Integers from 0 to 100 as a structured number line segment.
    """
    rng = get_positive_integer_range_to_100()
    return NumberRangeResponse(
        description="Positive integer range from 0 to 100.",
        range=rng,
    )


@router.get("/decimals/money/basic", response_model=DecimalMoneyResponse)
async def decimals_money_basic():
    """
    Basic decimal values between 0 and 1 with money and fraction connections.
    """
    examples = get_basic_decimal_money_examples()
    return DecimalMoneyResponse(
        description="Basic decimals (0.10, 0.25, 0.50, 0.75, 1.00) with money and fraction links.",
        examples=examples,
    )


@router.post("/money/operate", response_model=MoneyOperationResponse)
async def money_operate(payload: MoneyOperationRequest):
    """
    Perform simple addition or subtraction of small dollar amounts.
    """
    try:
        result = perform_money_operation(
            payload.left_dollars,
            payload.left_cents,
            payload.right_dollars,
            payload.right_cents,
            payload.operation,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return MoneyOperationResponse(
        description="Result of a simple money operation in dollars and cents.",
        result=result,
    )

@router.get(
    "/practice/next-problem",
    response_model=NextProblemResponse,
    tags=["math-practice"],
)
async def get_next_problem():
    """
    Select the next practice problem based on recent attempts and simple mastery.

    Priority:
    1) Geometry errors:
       - If recent incorrect geometry angle attempts, serve angle classification.
       - Else if recent incorrect geometry perimeter/area, serve perimeter/area.
    2) Algebra / inequality errors:
       - If recent incorrect both-sides equations, serve a both-sides equation.
       - Else if recent incorrect two-step equations, serve a two-step equation.
       - Else if recent incorrect one-step inequalities AND inequality mastery is not high,
         serve a one-step inequality.
       - Else if recent incorrect one-step equations AND one-step mastery is not high,
         serve a one-step equation.
    3) Comparison errors:
       - If recent incorrect comparisons, serve a comparison.
    4) No recent errors:
       - If one-step equation mastery is low/medium: serve one-step equation.
       - Else if one-step is medium/high and inequality one-step is low/medium:
         serve one-step inequality.
       - Else if one-step and inequality one-step are medium/high and two-step is low/medium:
         serve two-step equation.
       - Else if one-step, inequality one-step, and two-step are medium/high and both-sides is low/medium:
         serve both-sides equation.
       - Otherwise alternate between comparison and one-step equation.
    """
    recent = _load_recent_attempts()

    from collections import Counter

    attempt_counts = Counter(e.get("kind") for e in recent)

    def at_least_n_attempts(kind: NextProblemKind, n: int) -> bool:
        return attempt_counts.get(kind.value, 0) >= n


    # Compute recent error flags
    has_wrong_angle = any(
        e.get("kind") == "geometry_angle_type" and not e.get("is_correct", False)
        for e in recent
    )
    has_wrong_perim_area = any(
        e.get("kind") == "geometry_perimeter_area" and not e.get("is_correct", False)
        for e in recent
    )
    has_wrong_both_sides = any(
        e.get("kind") == "equation_both_sides" and not e.get("is_correct", False)
        for e in recent
    )
    has_wrong_two_step = any(
        e.get("kind") == "equation_two_step" and not e.get("is_correct", False)
        for e in recent
    )
    has_wrong_inequality_one_step = any(
        e.get("kind") == "inequality_one_step" and not e.get("is_correct", False)
        for e in recent
    )
    has_wrong_inequality_two_step = any(
        e.get("kind") == "inequality_two_step" and not e.get("is_correct", False)
        for e in recent
    )
    has_wrong_one_step = any(
        e.get("kind") == "equation_one_step" and not e.get("is_correct", False)
        for e in recent
    )
    has_wrong_comparison = any(
        e.get("kind") == "comparison_basic" and not e.get("is_correct", False)
        for e in recent
    )
    has_wrong_combine_like_terms = any(
        e.get("kind") == "algebra_combine_like_terms" and not e.get("is_correct", False)
        for e in recent
    )

    # Pull mastery estimates once
    summary = await get_practice_summary()
    mastery_map = {k.kind: k.mastery_estimate for k in summary.kinds}

    one_step_mastery = mastery_map.get(NextProblemKind.EQUATION_ONE_STEP.value, "low")
    two_step_mastery = mastery_map.get(NextProblemKind.EQUATION_TWO_STEP.value, "low")
    both_sides_mastery = mastery_map.get(NextProblemKind.EQUATION_BOTH_SIDES.value, "low")
    inequality_one_step_mastery = mastery_map.get(NextProblemKind.INEQUALITY_ONE_STEP.value, "low")
    inequality_two_step_mastery = mastery_map.get(NextProblemKind.INEQUALITY_TWO_STEP.value, "low")
    combine_like_terms_mastery = mastery_map.get(
        NextProblemKind.ALGEBRA_COMBINE_LIKE_TERMS.value,
        "low",
    )
    distribute_and_combine_mastery = mastery_map.get(
        NextProblemKind.ALGEBRA_DISTRIBUTE_AND_COMBINE.value,
        "low",
    )


    # 1) Geometry errors take priority
    if has_wrong_angle:
        chosen_kind = NextProblemKind.GEOMETRY_ANGLE_TYPE
        practice_set = generate_angle_classification_practice(count=1)
        item = practice_set.items[0]
        description = (
            "Next problem: angle classification, because you recently missed an angle problem."
        )
        payload = item.model_dump()

    elif has_wrong_perim_area:
        chosen_kind = NextProblemKind.GEOMETRY_PERIMETER_AREA
        practice_set = generate_perimeter_area_practice(count=1)
        item = practice_set.items[0]
        description = (
            "Next problem: perimeter/area, because you recently missed a geometry perimeter/area problem."
        )
        payload = item.model_dump()

    # 2) Algebra / inequality errors
    elif has_wrong_both_sides:
        chosen_kind = NextProblemKind.EQUATION_BOTH_SIDES
        practice_set = generate_equation_both_sides_practice(count=1)
        item = practice_set.items[0]
        description = (
            "Next problem: equation with variables on both sides, because you recently missed this kind of problem."
        )
        payload = item.model_dump()

    elif has_wrong_two_step:
        chosen_kind = NextProblemKind.EQUATION_TWO_STEP
        practice_set = generate_two_step_equation_practice(count=1)
        item = practice_set.items[0]
        description = (
            "Next problem: two-step equation, because you recently missed a two-step equation problem."
        )
        payload = item.model_dump()

    elif has_wrong_inequality_one_step and inequality_one_step_mastery != "high":
        chosen_kind = NextProblemKind.INEQUALITY_ONE_STEP
        practice_set = generate_one_step_inequality_practice(count=1)
        item = practice_set.items[0]
        description = (
            "Next problem: one-step inequality, because you recently missed this kind of problem "
            "and your inequality mastery is not high yet."
        )
        payload = item.model_dump()

    elif has_wrong_inequality_two_step and inequality_two_step_mastery != "high":
        chosen_kind = NextProblemKind.INEQUALITY_TWO_STEP
        practice_set = generate_two_step_inequality_practice(count=1)
        item = practice_set.items[0]
        description = (
            "Next problem: two-step inequality, because you recently missed this kind of problem "
            "and your two-step inequality mastery is not high yet."
        )
        payload = item.model_dump()

    elif has_wrong_one_step and one_step_mastery != "high":
        chosen_kind = NextProblemKind.EQUATION_ONE_STEP
        practice_set = generate_one_step_equation_practice(count=1)
        item = practice_set.items[0]
        description = (
            "Next problem: one-step equation, because you recently missed a one-step equation problem "
            "and your one-step mastery is not high yet."
        )
        payload = item.model_dump()

    # 3) Comparison errors
    elif has_wrong_comparison:
        chosen_kind = NextProblemKind.COMPARISON_BASIC
        practice_set = generate_basic_comparison_practice(count=1)
        item = practice_set.items[0]
        description = (
            "Next problem: basic comparison, because you recently missed a comparison problem."
        )
        payload = item.model_dump()

    elif has_wrong_combine_like_terms and combine_like_terms_mastery != "high":
        chosen_kind = NextProblemKind.ALGEBRA_COMBINE_LIKE_TERMS
        practice_set = generate_combine_like_terms_practice(count=1)
        item = practice_set.items[0]
        description = (
            "Next problem: combine like terms, because you recently missed this kind "
            "and your mastery is not high yet."
        )
        payload = item.model_dump()

    # 4) No recent errors: algebra progression by mastery
    else:
        if one_step_mastery in {"low", "medium"}:
            chosen_kind = NextProblemKind.EQUATION_ONE_STEP
            practice_set = generate_one_step_equation_practice(count=1)
            item = practice_set.items[0]
            description = (
                "Next problem: one-step equation, to solidify your foundation in basic equations."
            )
            payload = item.model_dump()

        elif (
            one_step_mastery in {"medium", "high"}
            and inequality_one_step_mastery in {"low", "medium"}
        ):
            chosen_kind = NextProblemKind.INEQUALITY_ONE_STEP
            practice_set = generate_one_step_inequality_practice(count=1)
            item = practice_set.items[0]
            description = (
                "Next problem: one-step inequality, building on your equation skills "
                "to reason about ranges of solutions."
            )
            payload = item.model_dump()

        elif (
            one_step_mastery in {"medium", "high"}
            and inequality_one_step_mastery in {"medium", "high"}
            and two_step_mastery in {"low", "medium"}
            and at_least_n_attempts(NextProblemKind.EQUATION_ONE_STEP, 5)
            and at_least_n_attempts(NextProblemKind.INEQUALITY_ONE_STEP, 5)
        ):
            chosen_kind = NextProblemKind.EQUATION_TWO_STEP
            practice_set = generate_two_step_equation_practice(count=1)
            item = practice_set.items[0]
            description = (
                "Next problem: two-step equation, because your one-step and inequality skills are solid "
                "and it's time to deepen your algebra."
            )
            payload = item.model_dump()


        elif (
            one_step_mastery in {"medium", "high"}
            and inequality_one_step_mastery in {"medium", "high"}
            and two_step_mastery in {"medium", "high"}
            and inequality_two_step_mastery in {"low", "medium"}
        ):
            chosen_kind = NextProblemKind.INEQUALITY_TWO_STEP
            practice_set = generate_two_step_inequality_practice(count=1)
            item = practice_set.items[0]
            description = (
                "Next problem: two-step inequality, building on your two-step equation skills "
                "to reason about ranges of solutions with two operations."
            )
            payload = item.model_dump()

        elif (
            one_step_mastery in {"medium", "high"}
            and inequality_one_step_mastery in {"medium", "high"}
            and two_step_mastery in {"medium", "high"}
            and both_sides_mastery in {"low", "medium"}
            and at_least_n_attempts(NextProblemKind.EQUATION_TWO_STEP, 5)
            and at_least_n_attempts(NextProblemKind.ALGEBRA_COMBINE_LIKE_TERMS, 5)
        ):
            chosen_kind = NextProblemKind.EQUATION_BOTH_SIDES
            practice_set = generate_equation_both_sides_practice(count=1)
            item = practice_set.items[0]
            description = (
                "Next problem: equation with variables on both sides, after mastering "
                "one-step equations, inequalities, two-step equations, and combining like terms."
            )
            payload = item.model_dump()


        else:
            # Otherwise alternate between comparison and one-step equation
            total_attempts = len(recent)
            if total_attempts % 2 == 0:
                chosen_kind = NextProblemKind.COMPARISON_BASIC
                practice_set = generate_basic_comparison_practice(count=1)
                item = practice_set.items[0]
                description = (
                    "Next problem: basic comparison, starting with integer comparisons."
                )
                payload = item.model_dump()
            else:
                chosen_kind = NextProblemKind.EQUATION_ONE_STEP
                practice_set = generate_one_step_equation_practice(count=1)
                item = practice_set.items[0]
                description = (
                    "Next problem: one-step equation, alternating with comparisons."
                )
                payload = item.model_dump()

    return NextProblemResponse(
        description=description,
        problem=NextProblem(
            kind=chosen_kind,
            payload=payload,
        ),
    )


@router.get(
    "/practice/summary",
    response_model=PracticeSummaryResponse,
    tags=["math-practice"],
)
async def get_practice_summary():
    """
    Summarize practice performance across comparison and equation problems.
    """
    recent = _load_recent_attempts(limit=500)

    by_kind: dict[str, list[dict]] = {}
    for entry in recent:
        kind = entry.get("kind", "unknown")
        by_kind.setdefault(kind, []).append(entry)

    summaries: list[PracticeKindSummary] = []

    for kind, attempts in by_kind.items():
        total = len(attempts)
        correct = sum(1 for a in attempts if a.get("is_correct", False))
        incorrect = total - correct
        streak = _compute_streak(attempts)
        mastery = _estimate_mastery(total, correct)

        summaries.append(
            PracticeKindSummary(
                kind=kind,
                total_attempts=total,
                correct_attempts=correct,
                incorrect_attempts=incorrect,
                recent_streak=streak,
                mastery_estimate=mastery,
            )
        )

    return PracticeSummaryResponse(
        description=(
            "Summary of recent practice performance across problem kinds, "
            "including counts, streaks, and a simple mastery estimate."
        ),
        kinds=summaries,
    )

@router.get(
    "/teach/number-arithmetic/foundations",
    response_model=TeachNumberArithmeticResponse,
    tags=["math-teach"],
)
async def teach_number_arithmetic_foundations():
    """
    Teach early number & arithmetic foundations using the concept path and
    basic comparison practice.
    """
    # 1) Load path and concepts
    path = get_number_arithmetic_foundation_path()
    concepts = get_number_arithmetic_foundation_concepts()
    by_id = _build_concept_index(concepts)

    teach_steps: list[TeachStep] = []

    for step in path.steps:
        concept = by_id.get(step.concept_id)
        if concept is None:
            continue
        teach_steps.append(
            TeachStep(
                order=step.order,
                concept_id=step.concept_id,
                concept_name=concept.name,
                headline=step.headline,
                rationale=step.rationale,
                definition=concept.definition,
            )
        )

    # 2) Generate basic comparison practice items
    practice_set: ComparisonPracticeSet = generate_basic_comparison_practice(count=5)

    # 3) Use practice summary to suggest next focus
    summary = await get_practice_summary()  # reuse same logic
    mastery_map = {k.kind: k.mastery_estimate for k in summary.kinds}
    cmp_mastery = mastery_map.get("comparison_basic", "low")

    if cmp_mastery == "high":
        next_suggestion = (
            "You seem comfortable with basic comparisons. Next, mix comparisons with "
            "simple addition and subtraction on the number line, including negatives."
        )
    elif cmp_mastery == "medium":
        next_suggestion = (
            "You are making progress with basic comparisons. Keep practicing a mix of "
            "less than, greater than, and equal to until your accuracy is consistently high."
        )
    else:
        next_suggestion = (
            "Focus on comparing small integers around zero using the number line. "
            "Work slowly through these comparison problems and pay attention to the words."
        )

    return TeachNumberArithmeticResponse(
        description=(
            "Teaching sequence for early number and arithmetic foundations, with "
            "concepts ordered along the teaching path and targeted comparison practice."
        ),
        steps=teach_steps,
        practice_items=practice_set.items,
        next_suggestion=next_suggestion,
    )

@router.get(
    "/teach/number-arithmetic/foundations",
    response_model=TeachNumberArithmeticResponse,
    tags=["math-teach"],
)
async def teach_number_arithmetic_foundations():
    """
    Teach early number & arithmetic foundations using the concept path and
    basic comparison practice.
    """
    # 1) Load path and concepts
    path = get_number_arithmetic_foundation_path()
    concepts = get_number_arithmetic_foundation_concepts()
    by_id = _build_concept_index(concepts)

    teach_steps: list[TeachStep] = []

    for step in path.steps:
        concept = by_id.get(step.concept_id)
        if concept is None:
            continue
        teach_steps.append(
            TeachStep(
                order=step.order,
                concept_id=step.concept_id,
                concept_name=concept.name,
                headline=step.headline,
                rationale=step.rationale,
                definition=concept.definition,
            )
        )

    # 2) Generate basic comparison practice items
    practice_set: ComparisonPracticeSet = generate_basic_comparison_practice(count=5)

    # 3) Use practice summary to suggest next focus
    summary = await get_practice_summary()  # reuse same logic
    mastery_map = {k.kind: k.mastery_estimate for k in summary.kinds}
    cmp_mastery = mastery_map.get("comparison_basic", "low")

    if cmp_mastery == "high":
        next_suggestion = (
            "You seem comfortable with basic comparisons. Next, mix comparisons with "
            "simple addition and subtraction on the number line, including negatives."
        )
    elif cmp_mastery == "medium":
        next_suggestion = (
            "You are making progress with basic comparisons. Keep practicing a mix of "
            "less than, greater than, and equal to until your accuracy is consistently high."
        )
    else:
        next_suggestion = (
            "Focus on comparing small integers around zero using the number line. "
            "Work slowly through these comparison problems and pay attention to the words."
        )

    return TeachNumberArithmeticResponse(
        description=(
            "Teaching sequence for early number and arithmetic foundations, with "
            "concepts ordered along the teaching path and targeted comparison practice."
        ),
        steps=teach_steps,
        practice_items=practice_set.items,
        next_suggestion=next_suggestion,
    )

@router.get(
    "/teach/geometry/early-foundations",
    response_model=TeachGeometryFoundationsResponse,
    tags=["math-teach"],
)
async def teach_geometry_early_foundations():
    """
    Teach early geometry foundations using the concept path:
    point → line → segment → ray → angle → triangle → square.
    """
    # 1) Load path and concepts
    path = get_geometry_early_foundations_path()
    concepts = get_geometry_early_foundations()
    by_id = _build_concept_index(concepts)

    teach_steps: list[TeachStep] = []

    for step in path.steps:
        concept = by_id.get(step.concept_id)
        if concept is None:
            continue
        teach_steps.append(
            TeachStep(
                order=step.order,
                concept_id=step.concept_id,
                concept_name=concept.name,
                headline=step.headline,
                rationale=step.rationale,
                definition=concept.definition,
            )
        )

    # 2) For now, no geometry practice items yet
    practice_items: list[dict] = []

    # 3) Static next suggestion (will later depend on geometry practice mastery)
    next_suggestion = (
        "Next, practice identifying angle types (acute, right, obtuse) and computing "
        "simple perimeters and areas for squares and rectangles."
    )

    return TeachGeometryFoundationsResponse(
        description=(
            "Teaching sequence for early geometry foundations: points, lines, segments, "
            "rays, angles, and basic shapes, preparing for angle and perimeter/area practice."
        ),
        steps=teach_steps,
        practice_items=practice_items,
        next_suggestion=next_suggestion,
    )

def _build_two_step_equations_teach_steps() -> list[TeachStep]:
    """
    Build a simple teaching sequence for two-step equations.
    For now, we reuse existing equation concepts and add explicit steps.
    """
    steps: list[TeachStep] = []

    steps.append(
        TeachStep(
            order=1,
            concept_id="algebra_two_step_structure",
            concept_name="Structure of Two-Step Equations",
            headline="See a two-step equation as 'multiply, then add'",
            rationale=(
                "Before solving, you should recognize that two-step equations have a "
                "structure like a*x + b = c: first a multiplication, then an addition or subtraction."
            ),
            definition=(
                "A two-step equation is an equation where the variable is combined with "
                "two operations, often multiplication and addition or subtraction, such as 2x + 3 = 11."
            ),
        )
    )

    steps.append(
        TeachStep(
            order=2,
            concept_id="algebra_inverse_operations",
            concept_name="Inverse Operations",
            headline="Use inverse operations in reverse order",
            rationale=(
                "To solve a*x + b = c, you undo the operations in reverse: first undo +b or -b, "
                "then undo the multiplication by a."
            ),
            definition=(
                "Inverse operations undo each other. Addition and subtraction are inverses. "
                "Multiplication and division are inverses."
            ),
        )
    )

    steps.append(
        TeachStep(
            order=3,
            concept_id="algebra_two_step_example",
            concept_name="Example: 2x + 3 = 11",
            headline="Work through a full example step by step",
            rationale=(
                "Seeing one example slowly helps you understand the pattern you will use on all "
                "two-step equations."
            ),
            definition=(
                "In 2x + 3 = 11, subtract 3 from both sides to get 2x = 8, then divide both sides "
                "by 2 to get x = 4."
            ),
        )
    )

    steps.append(
        TeachStep(
            order=4,
            concept_id="algebra_two_step_negative_b",
            concept_name="Examples with subtraction",
            headline="Handle equations like 3x - 5 = 10",
            rationale=(
                "Equations with subtraction use the same pattern: undo the subtraction by adding, "
                "then undo the multiplication."
            ),
            definition=(
                "In 3x - 5 = 10, add 5 to both sides to get 3x = 15, then divide by 3 to get x = 5."
            ),
        )
    )

    return steps

@router.get(
    "/teach/prealgebra/equations-basics",
    response_model=TeachPrealgebraEquationsResponse,
    tags=["math-teach"],
)
async def teach_prealgebra_equations_basics():
    """
    Teach prealgebra equation basics using the concept path and targeted practice.
    """
    # Load path and concepts
    path = get_prealgebra_equations_basics_path()
    concepts = get_prealgebra_equations_basics()
    by_id = _build_concept_index(concepts)

    teach_steps: list[TeachStep] = []

    for step in path.steps:
        concept = by_id.get(step.concept_id)
        if concept is None:
            continue
        teach_steps.append(
            TeachStep(
                order=step.order,
                concept_id=step.concept_id,
                concept_name=concept.name,
                headline=step.headline,
                rationale=step.rationale,
                definition=concept.definition,
            )
        )

    # Generate a few targeted one-step equations
    practice_set = generate_one_step_equation_practice(count=5)

    # Use practice summary to suggest next focus
    summary = await get_practice_summary()  # FastAPI will serialize, but here we just reuse logic
    mastery_map = {k.kind: k.mastery_estimate for k in summary.kinds}
    eq_mastery = mastery_map.get("equation_one_step", "low")

    if eq_mastery == "high":
        next_suggestion = (
            "You seem comfortable with one-step equations. Next, extend to two-step "
            "equations or equations with variables on both sides."
        )
    elif eq_mastery == "medium":
        next_suggestion = (
            "You are making progress with one-step equations. Keep practicing a mix of "
            "x + k = result and x - k = result until your accuracy is consistently high."
        )
    else:
        next_suggestion = (
            "Focus on the meaning of an equation and the idea of undoing operations. "
            "Work through these one-step practice problems slowly, checking each step."
        )

    return TeachPrealgebraEquationsResponse(
        description=(
            "Teaching sequence for prealgebra equation basics: expressions, equations, "
            "unknowns, and solving one-step equations, with targeted practice."
        ),
        steps=teach_steps,
        practice_items=practice_set.items,
        next_suggestion=next_suggestion,
    )

@router.get(
    "/teach/algebra/equations-two-step",
    response_model=TeachAlgebraTwoStepEquationsResponse,
    tags=["math-teach"],
)
async def teach_algebra_two_step_equations():
    """
    Teach algebra two-step equations (a*x + b = c) using a simple teaching
    sequence and targeted two-step practice items.
    """
    teach_steps = _build_two_step_equations_teach_steps()

    # Generate a few two-step equations for practice
    practice_set: EquationTwoStepPracticeSet = generate_two_step_equation_practice(
        count=5
    )

    # Use practice summary to suggest next focus
    summary = await get_practice_summary()
    mastery_map = {k.kind: k.mastery_estimate for k in summary.kinds}
    one_step_mastery = mastery_map.get("equation_one_step", "low")
    two_step_mastery = mastery_map.get("equation_two_step", "low")

    if two_step_mastery == "high":
        next_suggestion = (
            "You seem comfortable with two-step equations. Next, move on to equations "
            "with variables on both sides or simple inequalities."
        )
    elif two_step_mastery == "medium":
        next_suggestion = (
            "You are making progress with two-step equations. Keep practicing a mix of "
            "equations like a*x + b = c and a*x - b = c until your accuracy is consistently high."
        )
    else:
        # If one-step is still low, remind the learner to solidify that first
        if one_step_mastery == "low":
            next_suggestion = (
                "Focus first on one-step equations and inverse operations. Once those feel solid, "
                "return here to keep practicing two-step equations."
            )
        else:
            next_suggestion = (
                "Work slowly through these two-step equations, paying attention to undoing the "
                "addition/subtraction first and the multiplication second."
            )

    return TeachAlgebraTwoStepEquationsResponse(
        description=(
            "Teaching sequence for algebra two-step equations: understanding the structure "
            "a*x + b = c, using inverse operations in reverse order, and practicing with "
            "targeted examples."
        ),
        steps=teach_steps,
        practice_items=practice_set.items,
        next_suggestion=next_suggestion,
    )
