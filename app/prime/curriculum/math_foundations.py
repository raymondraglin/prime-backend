from app.prime.curriculum.models import (
    SubjectId,
    DifficultyLevel,
    LessonKind,
    Lesson,
    SubjectCurriculum,
    DomainId,
    CurriculumLevel,
)

from app.prime.math.foundations.number_sense import (
    NumberSenseSnapshot,
    CountingLesson,
    FractionFamily,
    NumberRange,
    DecimalMoneyExample,
    WordProblem,
    get_number_sense_snapshot,
    get_counting_to_10_lesson,
    get_money_fractions_family,
    get_small_integer_range,
    get_positive_integer_range_to_100,
    get_basic_decimal_money_examples,
    get_basic_money_word_problems,
)
from app.prime.curriculum.math_history import get_early_numeration_history
from app.prime.curriculum.math_concepts import (
    get_number_arithmetic_foundation_concepts,
)


def build_math_foundations_curriculum() -> SubjectCurriculum:
    """
    Wrap PRIME's early math genetics (number sense, counting, fractions)
    into a generic curriculum structure.
    """
    # 1) Number sense around zero + comparison language
    snapshot: NumberSenseSnapshot = get_number_sense_snapshot()
    lesson_number_foundations = Lesson(
        id="math_fnd_number_foundations",
        subject=SubjectId.MATH_FOUNDATIONS,
        title="Numbers Around Zero and Comparison Language",
        kind=LessonKind.CONCEPT,
        difficulty=DifficultyLevel.EARLY,
        description=(
            "Small integers around zero (-2, -1, 0, 1, 2), "
            "with 'more/less' and 'greater/less than' language."
        ),
        content={
            "snapshot": snapshot.model_dump(),
        },
    )

    # 2) Concepts: Number & arithmetic foundations (zero, one, naturals, negatives, integers)
    number_arithmetic_concepts = get_number_arithmetic_foundation_concepts()
    lesson_number_arithmetic_concepts = Lesson(
        id="math_fnd_concepts_number_arithmetic",
        subject=SubjectId.MATH_FOUNDATIONS,
        title="Concepts: Number and Arithmetic Foundations",
        kind=LessonKind.CONCEPT,
        difficulty=DifficultyLevel.EARLY,
        description=(
            "Core mathematical concepts for early number sense: zero, one, natural numbers, "
            "negative numbers, and integers, with examples and brief history notes."
        ),
        content={
            "concepts": [c.model_dump() for c in number_arithmetic_concepts],
        },
    )

    # 3) Counting to 10 with money examples
    counting_lesson: CountingLesson = get_counting_to_10_lesson()
    lesson_counting_0_10 = Lesson(
        id="math_fnd_counting_0_10",
        subject=SubjectId.MATH_FOUNDATIONS,
        title="Counting from 0 to 10 with Money Examples",
        kind=LessonKind.PRACTICE,
        difficulty=DifficultyLevel.EARLY,
        description=(
            "Counting numbers from 0 through 10 using numerals, words, "
            "and small money examples like $1, $5, and $10."
        ),
        content={
            "counting_lesson": counting_lesson.model_dump(),
        },
    )

    # 4) Basic money fractions between 0 and 1
    fractions_family: FractionFamily = get_money_fractions_family()
    lesson_money_fractions = Lesson(
        id="math_fnd_money_fractions",
        subject=SubjectId.MATH_FOUNDATIONS,
        title="Basic Money Fractions Between 0 and 1",
        kind=LessonKind.CONCEPT,
        difficulty=DifficultyLevel.EARLY,
        description=(
            "Simple fractions like 1/2, 1/4, 3/4, and 1/3, "
            "grounded in parts of a dollar."
        ),
        content={
            "fractions_family": fractions_family.model_dump(),
        },
    )

    # 5) Integer number line from -10 to 10
    small_range: NumberRange = get_small_integer_range()
    lesson_small_range = Lesson(
        id="math_fnd_range_-10_10",
        subject=SubjectId.MATH_FOUNDATIONS,
        title="Integer Number Line from -10 to 10",
        kind=LessonKind.CONCEPT,
        difficulty=DifficultyLevel.EARLY,
        description="A small integer number line segment around zero, from -10 to 10.",
        content={"range": small_range.model_dump()},
    )

    # 6) Integer number line from 0 to 100
    positive_range: NumberRange = get_positive_integer_range_to_100()
    lesson_range_0_100 = Lesson(
        id="math_fnd_range_0_100",
        subject=SubjectId.MATH_FOUNDATIONS,
        title="Integer Number Line from 0 to 100",
        kind=LessonKind.CONCEPT,
        difficulty=DifficultyLevel.EARLY,
        description="Positive integers from 0 to 100 on the number line.",
        content={"range": positive_range.model_dump()},
    )

    # 7) Basic decimals with money examples
    decimal_examples: list[DecimalMoneyExample] = get_basic_decimal_money_examples()
    lesson_basic_decimals = Lesson(
        id="math_fnd_decimals_basic",
        subject=SubjectId.MATH_FOUNDATIONS,
        title="Basic Decimals With Money Examples",
        kind=LessonKind.CONCEPT,
        difficulty=DifficultyLevel.EARLY,
        description=(
            "Decimals like 0.10, 0.25, 0.50, 0.75, and 1.00 tied to money and fractions."
        ),
        content={
            "examples": [ex.model_dump() for ex in decimal_examples],
        },
    )

    # 8) Basic money word problems (add/subtract/compare)
    word_problems: list[WordProblem] = get_basic_money_word_problems()
    lesson_money_word_problems = Lesson(
        id="math_fnd_word_problems_money_basic",
        subject=SubjectId.MATH_FOUNDATIONS,
        title="Basic Money Word Problems",
        kind=LessonKind.PRACTICE,
        difficulty=DifficultyLevel.EARLY,
        description=(
            "Simple word problems using money: adding, subtracting, "
            "and comparing amounts in dollars and cents."
        ),
        content={
            "problems": [wp.model_dump() for wp in word_problems],
        },
    )

    # 9) History of early numeration systems
    early_numeration_events = get_early_numeration_history()
    lesson_early_numeration_history = Lesson(
        id="math_fnd_history_early_numeration",
        subject=SubjectId.MATH_FOUNDATIONS,
        title="History of Early Numeration Systems",
        kind=LessonKind.HISTORY,
        difficulty=DifficultyLevel.EARLY,
        description=(
            "A timeline of how humans moved from tally marks to positional numeral systems "
            "with zero and decimal fractions."
        ),
        content={
            "events": [ev.model_dump() for ev in early_numeration_events],
        },
    )

    recommended_order = [
        lesson_number_foundations.id,
        lesson_number_arithmetic_concepts.id,
        lesson_counting_0_10.id,
        lesson_money_fractions.id,
        lesson_small_range.id,
        lesson_range_0_100.id,
        lesson_basic_decimals.id,
        lesson_money_word_problems.id,
        lesson_early_numeration_history.id,
    ]

    return SubjectCurriculum(
        subject=SubjectId.MATH_FOUNDATIONS,
        name="Math Foundations: Early Number Sense",
        description=(
            "PRIME's earliest math curriculum: numbers around zero, "
            "core number concepts, counting to 10, basic money-related fractions, "
            "integer ranges, basic decimals tied to money, simple money word problems, "
            "and the early history of numeration systems."
        ),
        lessons=[
            lesson_number_foundations,
            lesson_number_arithmetic_concepts,
            lesson_counting_0_10,
            lesson_money_fractions,
            lesson_small_range,
            lesson_range_0_100,
            lesson_basic_decimals,
            lesson_money_word_problems,
            lesson_early_numeration_history,
        ],
        recommended_order=recommended_order,
        domain=DomainId.MATHEMATICS_AND_FORMAL_SCIENCES,
        default_level=CurriculumLevel.SCHOOL_FOUNDATION,
    )

