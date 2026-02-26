from enum import Enum
from pydantic import BaseModel
from typing import Any, List


class NumberKind(str, Enum):
    NATURAL = "natural"          # 0,1,2,3,...
    COUNTING = "counting"        # 1,2,3,...
    INTEGER = "integer"          # ..., -2,-1,0,1,2,...
    WHOLE = "whole"              # 0,1,2,3,...
    MONEY_UNIT = "money_unit"    # concrete money amounts

class NumberConcept(BaseModel):
    name: str
    symbol: str
    value: int
    kind: NumberKind
    description: str

class NumberRelationship(BaseModel):
    from_symbol: str
    to_symbol: str
    relation: str
    explanation: str

class NumberSenseSnapshot(BaseModel):
    """
    A small, structured snapshot of PRIME's earliest number sense.
    """
    core_numbers: list[NumberConcept]
    relationships: list[NumberRelationship]

class NumberRangePoint(BaseModel):
    value: int
    label: str          # e.g. "-10", "0", "10"
    is_anchor: bool
    description: str

class NumberRange(BaseModel):
    name: str
    start: int
    end: int
    step: int
    points: list[NumberRangePoint]

class InfinitySeed(BaseModel):
    name: str
    description: str
    example_phrase: str

class SimpleFraction(BaseModel):
    numerator: int
    denominator: int
    decimal: float
    as_text: str          # "one half", "one quarter", etc.
    money_example: str    # e.g. "$0.50", "$0.25"
    explanation: str

class FractionFamily(BaseModel):
    name: str
    description: str
    fractions: list[SimpleFraction]

class DecimalMoneyExample(BaseModel):
    decimal: float
    as_text: str          # "one tenth", "one quarter", "one half"
    money_example: str    # "$0.10", "$0.25", "$0.50", ...
    fraction: SimpleFraction | None
    explanation: str

class NumberRepresentation(BaseModel):
    system: str          # "decimal", "binary"
    text: str            # e.g. "5" or "101"
    explanation: str

class ComparisonPracticeRelation(str, Enum):
    LESS_THAN = "less_than"
    EQUAL = "equal"
    GREATER_THAN = "greater_than"


class ComparisonPracticeItem(BaseModel):
    left_value: int
    right_value: int
    correct_relation: ComparisonPracticeRelation
    explanation: str


class ComparisonPracticeSet(BaseModel):
    description: str
    items: List[ComparisonPracticeItem]


def get_core_number_concepts() -> list[NumberConcept]:
    """
    Very small 'genetic core' for PRIME's number sense.

    We will grow this set gradually; right now it's the anchors
    for counting, integers near zero, and a money example.
    """
    return [
        NumberConcept(
            name="minus two",
            symbol="-2",
            value=-2,
            kind=NumberKind.INTEGER,
            description="Two units less than zero; shows moving left on the number line.",
        ),
        NumberConcept(
            name="minus one",
            symbol="-1",
            value=-1,
            kind=NumberKind.INTEGER,
            description="One unit less than zero; first step into negative direction.",
        ),
        NumberConcept(
            name="zero",
            symbol="0",
            value=0,
            kind=NumberKind.NATURAL,
            description="Represents 'no objects'; anchor point on the number line.",
        ),
        NumberConcept(
            name="one",
            symbol="1",
            value=1,
            kind=NumberKind.COUNTING,
            description="Single object; basis for counting and unit quantity.",
        ),
        NumberConcept(
            name="two",
            symbol="2",
            value=2,
            kind=NumberKind.COUNTING,
            description="Two objects; earliest sense of 'more than one'.",
        ),
        NumberConcept(
            name="one dollar",
            symbol="$1",
            value=1,
            kind=NumberKind.MONEY_UNIT,
            description="Concrete example of 'one' as money; connects numbers to value.",
        ),
    ]


def get_basic_relationships() -> list[NumberRelationship]:
    """
    First relationships PRIME should know about numbers.
    Includes successor and basic comparison words.
    """
    return [
        # Successor relationships near zero
        NumberRelationship(
            from_symbol="-2",
            to_symbol="-1",
            relation="successor",
            explanation="-1 is one more than -2 on the number line.",
        ),
        NumberRelationship(
            from_symbol="-1",
            to_symbol="0",
            relation="successor",
            explanation="0 is one more than -1 on the number line.",
        ),
        NumberRelationship(
            from_symbol="0",
            to_symbol="1",
            relation="successor",
            explanation="1 is one more than 0 on the number line.",
        ),
        NumberRelationship(
            from_symbol="1",
            to_symbol="2",
            relation="successor",
            explanation="2 is one more than 1 on the number line.",
        ),

        # Opposite sign around zero
        NumberRelationship(
            from_symbol="1",
            to_symbol="-1",
            relation="opposite_sign",
            explanation="1 and -1 are the same distance from 0 but in opposite directions.",
        ),
        NumberRelationship(
            from_symbol="2",
            to_symbol="-2",
            relation="opposite_sign",
            explanation="2 and -2 are the same distance from 0 but in opposite directions.",
        ),

        # Money example connection
        NumberRelationship(
            from_symbol="1",
            to_symbol="$1",
            relation="money_example",
            explanation="The number 1 can represent one dollar in money contexts.",
        ),

        # Comparison language: greater than / less than
        NumberRelationship(
            from_symbol="-2",
            to_symbol="-1",
            relation="less_than",
            explanation="-2 is less than -1; it lies further left on the number line.",
        ),
        NumberRelationship(
            from_symbol="-1",
            to_symbol="0",
            relation="less_than",
            explanation="-1 is less than 0; it lies to the left on the number line.",
        ),
        NumberRelationship(
            from_symbol="0",
            to_symbol="1",
            relation="less_than",
            explanation="0 is less than 1; it lies to the left on the number line.",
        ),
        NumberRelationship(
            from_symbol="1",
            to_symbol="2",
            relation="less_than",
            explanation="1 is less than 2; it lies to the left on the number line.",
        ),
        NumberRelationship(
            from_symbol="2",
            to_symbol="1",
            relation="greater_than",
            explanation="2 is greater than 1; it lies to the right on the number line.",
        ),
        NumberRelationship(
            from_symbol="1",
            to_symbol="0",
            relation="greater_than",
            explanation="1 is greater than 0; it lies to the right on the number line.",
        ),
        NumberRelationship(
            from_symbol="0",
            to_symbol="-1",
            relation="greater_than",
            explanation="0 is greater than -1; it lies to the right on the number line.",
        ),
        NumberRelationship(
            from_symbol="-1",
            to_symbol="-2",
            relation="greater_than",
            explanation="-1 is greater than -2; it lies to the right on the number line.",
        ),
    ]


def get_number_sense_snapshot() -> NumberSenseSnapshot:
    """
    Return a small, structured view of PRIME's earliest number sense.
    """
    return NumberSenseSnapshot(
        core_numbers=get_core_number_concepts(),
        relationships=get_basic_relationships(),
    )

def get_infinity_seed() -> InfinitySeed:
    """
    A very early concept of 'infinity' for PRIME.
    Not about different sizes of infinity, just that counting can go on without end.
    """
    return InfinitySeed(
        name="basic_infinity",
        description=(
            "When you keep adding 1 to a number, you can always get a bigger number. "
            "There is no 'last number'; this idea is called infinity."
        ),
        example_phrase="0, 1, 2, 3, ... and so on forever.",
    )

def get_money_fractions_family() -> FractionFamily:
    """
    Basic fractions between 0 and 1, grounded in simple money examples.
    """
    fractions: list[SimpleFraction] = [
        SimpleFraction(
            numerator=1,
            denominator=2,
            decimal=0.5,
            as_text="one half",
            money_example="$0.50",
            explanation=(
                "One half means a whole split into 2 equal parts, and you have 1 of them. "
                "If a dollar is split into 2 equal parts, each part is 50 cents."
            ),
        ),
        SimpleFraction(
            numerator=1,
            denominator=4,
            decimal=0.25,
            as_text="one quarter",
            money_example="$0.25",
            explanation=(
                "One quarter means a whole split into 4 equal parts, and you have 1 of them. "
                "If a dollar is split into 4 equal parts, each part is 25 cents."
            ),
        ),
        SimpleFraction(
            numerator=3,
            denominator=4,
            decimal=0.75,
            as_text="three quarters",
            money_example="$0.75",
            explanation=(
                "Three quarters means 3 of the 4 equal parts. "
                "If a dollar is split into 4 parts, three quarters is 75 cents."
            ),
        ),
        SimpleFraction(
            numerator=1,
            denominator=3,
            decimal=1.0 / 3.0,
            as_text="one third",
            money_example="about $0.33",
            explanation=(
                "One third means a whole split into 3 equal parts, and you have 1 of them. "
                "A dollar split into 3 equal parts cannot be exact in cents, but each part is about 33 cents."
            ),
        ),
    ]

    return FractionFamily(
        name="Basic money fractions between 0 and 1",
        description=(
            "Fractions that represent simple parts of a whole dollar: halves, quarters, "
            "three-quarters, and thirds."
        ),
        fractions=fractions,
    )

class FractionComparisonResult(BaseModel):
    left: SimpleFraction
    right: SimpleFraction
    relation: str           # "less_than", "equal", "greater_than"
    explanation: str

class MoneyAmount(BaseModel):
    dollars: int
    cents: int

    def total_cents(self) -> int:
        return self.dollars * 100 + self.cents

    def to_decimal_dollars(self) -> float:
        return self.total_cents() / 100.0

    def format(self) -> str:
        return f"${self.dollars}.{self.cents:02d}"


class MoneyOperationResult(BaseModel):
    left: MoneyAmount
    right: MoneyAmount
    operation: str           # "add" or "subtract"
    result: MoneyAmount
    explanation: str

class WordProblemKind(str, Enum):
    MONEY_ADD = "money_add"
    MONEY_SUBTRACT = "money_subtract"
    MONEY_COMPARE = "money_compare"


class WordProblem(BaseModel):
    id: str
    kind: WordProblemKind
    prompt: str
    # Structured data behind the story
    left_amount: MoneyAmount | None = None
    right_amount: MoneyAmount | None = None
    operation: str | None = None          # "add" or "subtract" for operation problems
    correct_result: MoneyAmount | None = None
    correct_relation: str | None = None   # "less_than", "equal", "greater_than" for compare
    explanation: str


def compare_money_fractions(a_num: int, a_den: int, b_num: int, b_den: int) -> FractionComparisonResult:
    """
    Compare two fractions using the money-fractions family as the source of truth.
    Only supports fractions present in get_money_fractions_family().
    """
    family = get_money_fractions_family()
    key = lambda f: (f.numerator, f.denominator)
    by_key: dict[tuple[int, int], SimpleFraction] = {key(f): f for f in family.fractions}

    a_key = (a_num, a_den)
    b_key = (b_num, b_den)

    if a_key not in by_key or b_key not in by_key:
        raise ValueError("Only the predefined money fractions are supported at this stage.")

    left = by_key[a_key]
    right = by_key[b_key]

    # Compare by decimal value
    if abs(left.decimal - right.decimal) < 1e-9:
        relation = "equal"
        relation_phrase = "the same amount of the whole"
    elif left.decimal < right.decimal:
        relation = "less_than"
        relation_phrase = "less of the whole"
    else:
        relation = "greater_than"
        relation_phrase = "more of the whole"

    explanation_parts: list[str] = [
        f"{left.as_text.capitalize()} ({left.numerator}/{left.denominator}) is worth about {left.money_example}.",
        f"{right.as_text.capitalize()} ({right.numerator}/{right.denominator}) is worth about {right.money_example}.",
    ]

    if relation == "equal":
        explanation_parts.append(
            "They represent the same fraction of a whole, just described differently."
        )
    elif relation == "less_than":
        explanation_parts.append(
            f"{left.as_text.capitalize()} is less of the whole than {right.as_text}."
        )
    else:
        explanation_parts.append(
            f"{left.as_text.capitalize()} is more of the whole than {right.as_text}."
        )

    explanation = " ".join(explanation_parts)

    return FractionComparisonResult(
        left=left,
        right=right,
        relation=relation,
        explanation=explanation,
    )

def build_integer_range(start: int, end: int, step: int = 1) -> NumberRange:
    points: list[NumberRangePoint] = []
    for v in range(start, end + 1, step):
        is_anchor = v in {start, 0, end}
        if v == 0:
            desc = "Zero is the anchor; it separates negative and positive numbers."
        elif v < 0:
            desc = f"{v} is a negative number; it lies to the left of zero on the number line."
        else:
            desc = f"{v} is a positive number; it lies to the right of zero on the number line."

        points.append(
            NumberRangePoint(
                value=v,
                label=str(v),
                is_anchor=is_anchor,
                description=desc,
            )
        )

    name = f"Integers from {start} to {end}"
    return NumberRange(
        name=name,
        start=start,
        end=end,
        step=step,
        points=points,
    )


def get_small_integer_range() -> NumberRange:
    """
    Integers from -10 to 10, for PRIME's early sense of the number line.
    """
    return build_integer_range(-10, 10, 1)


def get_positive_integer_range_to_100() -> NumberRange:
    """
    Positive integers from 0 to 100, stepping by 1.
    """
    return build_integer_range(0, 100, 1)

def get_basic_decimal_money_examples() -> list[DecimalMoneyExample]:
    family = get_money_fractions_family()
    def key(f: SimpleFraction) -> tuple[int, int]:
        return f.numerator, f.denominator

    by_key: dict[tuple[int, int], SimpleFraction] = {key(f): f for f in family.fractions}

    examples: list[DecimalMoneyExample] = []

    # 0.10 (approximate)
    examples.append(
        DecimalMoneyExample(
            decimal=0.10,
            as_text="one tenth",
            money_example="$0.10",
            fraction=None,
            explanation=(
                "One tenth means a whole split into 10 equal parts, and you have 1 of them. "
                "Ten cents is one tenth of a dollar."
            ),
        )
    )

    # 0.25 -> 1/4
    frac_quarter = by_key.get((1, 4))
    examples.append(
        DecimalMoneyExample(
            decimal=0.25,
            as_text="one quarter",
            money_example="$0.25",
            fraction=frac_quarter,
            explanation=(
                "One quarter is 0.25 of a whole, or 25 cents out of a dollar. "
                "It matches the fraction 1/4."
            ),
        )
    )

    # 0.50 -> 1/2
    frac_half = by_key.get((1, 2))
    examples.append(
        DecimalMoneyExample(
            decimal=0.50,
            as_text="one half",
            money_example="$0.50",
            fraction=frac_half,
            explanation=(
                "One half is 0.5 of a whole, or 50 cents out of a dollar. "
                "It matches the fraction 1/2."
            ),
        )
    )

    # 0.75 -> 3/4
    frac_three_quarters = by_key.get((3, 4))
    examples.append(
        DecimalMoneyExample(
            decimal=0.75,
            as_text="three quarters",
            money_example="$0.75",
            fraction=frac_three_quarters,
            explanation=(
                "Three quarters is 0.75 of a whole, or 75 cents out of a dollar. "
                "It matches the fraction 3/4."
            ),
        )
    )

    # 1.00
    examples.append(
        DecimalMoneyExample(
            decimal=1.00,
            as_text="one whole",
            money_example="$1.00",
            fraction=None,
            explanation=(
                "One whole is the full amount; $1.00 is the entire dollar, not a fraction."
            ),
        )
    )

    return examples

def perform_money_operation(
    left_dollars: int,
    left_cents: int,
    right_dollars: int,
    right_cents: int,
    operation: str,
) -> MoneyOperationResult:
    if operation not in {"add", "subtract"}:
        raise ValueError("Operation must be 'add' or 'subtract'.")

    left = MoneyAmount(dollars=left_dollars, cents=left_cents)
    right = MoneyAmount(dollars=right_dollars, cents=right_cents)

    if operation == "add":
        total_cents = left.total_cents() + right.total_cents()
        op_word = "plus"
    else:
        total_cents = left.total_cents() - right.total_cents()
        op_word = "minus"

    result_dollars = int(total_cents // 100)
    result_cents = int(total_cents % 100)

    if result_cents < 0:
        result_cents += 100
        result_dollars -= 1

    result = MoneyAmount(dollars=result_dollars, cents=result_cents)

    explanation = (
        f"{left.format()} {op_word} {right.format()} equals {result.format()}. "
        f"That is {left.to_decimal_dollars():.2f} {op_word} "
        f"{right.to_decimal_dollars():.2f} = {result.to_decimal_dollars():.2f} dollars."
    )

    return MoneyOperationResult(
        left=left,
        right=right,
        operation=operation,
        result=result,
        explanation=explanation,
    )

def make_money_add_problem(
    problem_id: str,
    left_dollars: int,
    left_cents: int,
    right_dollars: int,
    right_cents: int,
) -> WordProblem:
    result = perform_money_operation(
        left_dollars=left_dollars,
        left_cents=left_cents,
        right_dollars=right_dollars,
        right_cents=right_cents,
        operation="add",
    )

    prompt = (
        f"You have {result.left.format()} and you receive {result.right.format()} more. "
        f"How much money do you have now?"
    )

    explanation = (
        f"Start with {result.left.format()} and add {result.right.format()}. "
        f"{result.explanation}"
    )

    return WordProblem(
        id=problem_id,
        kind=WordProblemKind.MONEY_ADD,
        prompt=prompt,
        left_amount=result.left,
        right_amount=result.right,
        operation="add",
        correct_result=result.result,
        explanation=explanation,
    )


def make_money_subtract_problem(
    problem_id: str,
    left_dollars: int,
    left_cents: int,
    right_dollars: int,
    right_cents: int,
) -> WordProblem:
    result = perform_money_operation(
        left_dollars=left_dollars,
        left_cents=left_cents,
        right_dollars=right_dollars,
        right_cents=right_cents,
        operation="subtract",
    )

    prompt = (
        f"You have {result.left.format()} and you spend {result.right.format()}. "
        f"How much money is left?"
    )

    explanation = (
        f"Start with {result.left.format()} and subtract {result.right.format()}. "
        f"{result.explanation}"
    )

    return WordProblem(
        id=problem_id,
        kind=WordProblemKind.MONEY_SUBTRACT,
        prompt=prompt,
        left_amount=result.left,
        right_amount=result.right,
        operation="subtract",
        correct_result=result.result,
        explanation=explanation,
    )


def make_money_compare_problem(
    problem_id: str,
    left_dollars: int,
    left_cents: int,
    right_dollars: int,
    right_cents: int,
) -> WordProblem:
    left = MoneyAmount(dollars=left_dollars, cents=left_cents)
    right = MoneyAmount(dollars=right_dollars, cents=right_cents)

    if left.total_cents() == right.total_cents():
        relation = "equal"
        relation_phrase = "the same amount of money as"
    elif left.total_cents() < right.total_cents():
        relation = "less_than"
        relation_phrase = "less money than"
    else:
        relation = "greater_than"
        relation_phrase = "more money than"

    prompt = (
        f"Alice has {left.format()} and Bob has {right.format()}. "
        f"Who has more money, or do they have the same amount?"
    )

    explanation = (
        f"{left.format()} compared to {right.format()} means {left.format()} is "
        f"{relation_phrase} {right.format()}. "
        f"Alice has {left.to_decimal_dollars():.2f} dollars and Bob has "
        f"{right.to_decimal_dollars():.2f} dollars."
    )

    return WordProblem(
        id=problem_id,
        kind=WordProblemKind.MONEY_COMPARE,
        prompt=prompt,
        left_amount=left,
        right_amount=right,
        correct_relation=relation,
        explanation=explanation,
    )


def get_basic_money_word_problems() -> list[WordProblem]:
    """
    A small bank of early money-related word problems for PRIME.
    """
    problems: list[WordProblem] = []

    # Addition problems
    problems.append(
        make_money_add_problem(
            problem_id="wp_money_add_1",
            left_dollars=1,
            left_cents=0,
            right_dollars=0,
            right_cents=50,
        )
    )
    problems.append(
        make_money_add_problem(
            problem_id="wp_money_add_2",
            left_dollars=2,
            left_cents=25,
            right_dollars=1,
            right_cents=75,
        )
    )

    # Subtraction problems
    problems.append(
        make_money_subtract_problem(
            problem_id="wp_money_sub_1",
            left_dollars=2,
            left_cents=0,
            right_dollars=0,
            right_cents=75,
        )
    )
    problems.append(
        make_money_subtract_problem(
            problem_id="wp_money_sub_2",
            left_dollars=5,
            left_cents=0,
            right_dollars=1,
            right_cents=25,
        )
    )

    # Comparison problems
    problems.append(
        make_money_compare_problem(
            problem_id="wp_money_cmp_1",
            left_dollars=0,
            left_cents=50,
            right_dollars=0,
            right_cents=25,
        )
    )
    problems.append(
        make_money_compare_problem(
            problem_id="wp_money_cmp_2",
            left_dollars=1,
            left_cents=0,
            right_dollars=1,
            right_cents=0,
        )
    )

    return problems

# Small helper we already used in the API (to keep that working)
class NumberExample(BaseModel):
    name: str
    value: int
    description: str


def get_example_numbers() -> list[NumberExample]:
    """
    Backwards-compatible examples list for the preview endpoint.
    """
    concepts = get_core_number_concepts()
    examples: list[NumberExample] = []
    for c in concepts:
        if c.symbol in {"0", "1", "2", "-1"}:
            examples.append(
                NumberExample(
                    name=c.name,
                    value=c.value,
                    description=c.description,
                )
            )
    return examples

class CountingItem(BaseModel):
    numeral: str       # "0", "1", "2", ...
    word: str          # "zero", "one", "two", ...
    value: int         # 0, 1, 2, ...
    binary: str        # "0", "1", "10", etc.
    has_money_example: bool
    money_example: str | None = None
    explanation: str


class CountingLesson(BaseModel):
    name: str
    description: str
    sequence: list[CountingItem]


def get_counting_to_10_lesson() -> CountingLesson:
    """
    Very first explicit counting lesson for PRIME:
    counting from 0 to 10 with words and a simple money connection.
    """
    items: list[CountingItem] = [
        CountingItem(
            numeral="0",
            word="zero",
            value=0,
            binary="0",
            has_money_example=False,
            money_example=None,
            explanation="Zero means no objects; nothing to count.",
        ),
        CountingItem(
            numeral="1",
            word="one",
            value=1,
            binary="1",
            has_money_example=True,
            money_example="$1",
            explanation="One means a single object; one dollar is a concrete example.",
        ),
        CountingItem(
            numeral="2",
            word="two",
            value=2,
            binary="10",
            has_money_example=True,
            money_example="$2",
            explanation="Two means one more than one; you can think of two dollars.",
        ),
        CountingItem(
            numeral="3",
            word="three",
            value=3,
            binary="11",
            has_money_example=True,
            money_example="$3",
            explanation="Three is one more than two; a small handful of things.",
        ),
        CountingItem(
            numeral="4",
            word="four",
            value=4,
            binary="100",
            has_money_example=True,
            money_example="$4",
            explanation="Four is one more than three; often arranged as 2-by-2.",
        ),
        CountingItem(
            numeral="5",
            word="five",
            value=5,
            binary="101",
            has_money_example=True,
            money_example="$5",
            explanation="Five is halfway between 0 and 10; common in money (a $5 bill).",
        ),
        CountingItem(
            numeral="6",
            word="six",
            value=6,
            binary="110",
            has_money_example=True,
            money_example="$6",
            explanation="Six is one more than five; can be seen as 3 pairs.",
        ),
        CountingItem(
            numeral="7",
            word="seven",
            value=7,
            binary="111",
            has_money_example=True,
            money_example="$7",
            explanation="Seven is one more than six; often appears in everyday contexts.",
        ),
        CountingItem(
            numeral="8",
            word="eight",
            value=8,
            binary="1000",
            has_money_example=True,
            money_example="$8",
            explanation="Eight is one more than seven; can be seen as 2 groups of 4.",
        ),
        CountingItem(
            numeral="9",
            word="nine",
            value=9,
            binary="1001",
            has_money_example=True,
            money_example="$9",
            explanation="Nine is one less than ten; close to a full set of ten.",
        ),
        CountingItem(
            numeral="10",
            word="ten",
            value=10,
            binary="1010",
            has_money_example=True,
            money_example="$10",
            explanation="Ten is a full 'bundle'; base of the usual decimal system.",
        ),
    ]


    return CountingLesson(
        name="Counting from 0 to 10",
        description=(
            "PRIME's first explicit counting lesson: numerals, words, and "
            "a simple connection to money values from 0 through 10."
        ),
        sequence=items,
    )

class NumberReasoningResult(BaseModel):
    input_value: int
    numeral: str
    word: str
    binary: str
    predecessor: int | None
    successor: int | None
    has_money_example: bool
    money_example: str | None
    explanation: str


def reason_about_small_integer(n: int) -> NumberReasoningResult:
    """
    Simple, explicit reasoning over an integer in [0, 10] using
    PRIME's counting-to-10 lesson as the source of truth.
    """
    lesson = get_counting_to_10_lesson()
    by_value: dict[int, CountingItem] = {item.value: item for item in lesson.sequence}

    if n not in by_value:
        raise ValueError("Only values from 0 to 10 are supported in this early stage.")

    item = by_value[n]

    # Determine predecessor and successor within 0..10
    predecessor = n - 1 if (n - 1) in by_value else None
    successor = n + 1 if (n + 1) in by_value else None

    # Build a short explanation grounded in neighbors and money
    parts: list[str] = []

    parts.append(f"{item.word.capitalize()} is written as {item.numeral} and represents {item.value} objects.")

    if predecessor is not None:
        prev_item = by_value[predecessor]
        parts.append(f"It is one more than {prev_item.word} ({prev_item.numeral}).")

    if successor is not None:
        next_item = by_value[successor]
        parts.append(f"It is one less than {next_item.word} ({next_item.numeral}).")

    if item.has_money_example and item.money_example:
        parts.append(f"In money, it can be seen as {item.money_example}.")

    # Append the item-specific explanation we wrote earlier
    parts.append(item.explanation)

    explanation = " ".join(parts)

    return NumberReasoningResult(
        input_value=n,
        numeral=item.numeral,
        word=item.word,
        binary=item.binary,
        predecessor=predecessor,
        successor=successor,
        has_money_example=item.has_money_example,
        money_example=item.money_example,
        explanation=explanation,
    )

def generate_basic_comparison_practice(count: int = 10) -> ComparisonPracticeSet:
    """
    Generate basic comparison practice items using integers in a small range.
    Relations: less_than, equal, greater_than.
    """
    # Clamp count to a safe range
    if count < 1:
        count = 1
    if count > 50:
        count = 50

    items: list[ComparisonPracticeItem] = []

    # We use a fixed small range for now: -5 to 5
    values = list(range(-5, 6))

    # Simple deterministic generation: walk pairs through the range
    # to avoid needing randomness for this early stage.
    idx = 0
    total_pairs = len(values) * len(values)

    while len(items) < count and idx < total_pairs:
        left = values[idx // len(values)]
        right = values[idx % len(values)]
        idx += 1

        # Skip the trivial case (0, 0) for variety
        if left == 0 and right == 0:
            continue

        if left < right:
            relation = ComparisonPracticeRelation.LESS_THAN
            explanation = (
                f"On the number line, {left} lies to the left of {right}, "
                f"so {left} is less than {right}."
            )
        elif left > right:
            relation = ComparisonPracticeRelation.GREATER_THAN
            explanation = (
                f"On the number line, {left} lies to the right of {right}, "
                f"so {left} is greater than {right}."
            )
        else:
            relation = ComparisonPracticeRelation.EQUAL
            explanation = (
                f"Both numbers are {left}, so they are equal; they share the same point "
                f"on the number line."
            )

        items.append(
            ComparisonPracticeItem(
                left_value=left,
                right_value=right,
                correct_relation=relation,
                explanation=explanation,
            )
        )

    return ComparisonPracticeSet(
        description=(
            "Basic integer comparison practice with less_than, equal, and greater_than "
            "relations on the number line from -5 to 5."
        ),
        items=items,
    )

def check_comparison_answer(
    left_value: int,
    right_value: int,
    given_relation: str,
) -> tuple[bool, str, ComparisonPracticeRelation]:
    """
    Check a learner's answer for a comparison between two integers.

    given_relation should be one of: "less_than", "equal", "greater_than".
    Returns (is_correct, explanation, correct_relation_enum).
    """
    if left_value < right_value:
        correct_relation = ComparisonPracticeRelation.LESS_THAN
        base_explanation = (
            f"On the number line, {left_value} lies to the left of {right_value}, "
            f"so {left_value} is less than {right_value}."
        )
    elif left_value > right_value:
        correct_relation = ComparisonPracticeRelation.GREATER_THAN
        base_explanation = (
            f"On the number line, {left_value} lies to the right of {right_value}, "
            f"so {left_value} is greater than {right_value}."
        )
    else:
        correct_relation = ComparisonPracticeRelation.EQUAL
        base_explanation = (
            f"Both numbers are {left_value}, so they are equal; they share the same point "
            f"on the number line."
        )

    try:
        learner_relation = ComparisonPracticeRelation(given_relation)
    except ValueError:
        return (
            False,
            "The relation must be one of: 'less_than', 'equal', or 'greater_than'.",
            correct_relation,
        )

    is_correct = learner_relation == correct_relation

    if is_correct:
        explanation = (
            f"Correct. You chose '{learner_relation.value}'. {base_explanation}"
        )
    else:
        explanation = (
            f"Not quite. You chose '{learner_relation.value}', but the correct relation is "
            f"'{correct_relation.value}'. {base_explanation}"
        )

    return is_correct, explanation, correct_relation
