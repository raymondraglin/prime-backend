from app.prime.curriculum.models import (
    MathLevel,
    MathSubfield,
    MathConcept,
    MathExample,
    MathTeachingPath,
    MathTeachingStep,
)

from app.prime.curriculum.models import MathTeachingPath, MathTeachingStep


def get_number_arithmetic_foundation_concepts() -> list[MathConcept]:
    """
    Seed concepts for School foundation → Number & arithmetic foundations.
    This uses the same core ideas as your early number-sense lessons.
    """
    concepts: list[MathConcept] = []

    # Zero
    concepts.append(
        MathConcept(
            id="math_concept_zero",
            name="Zero",
            level=MathLevel.SCHOOL_FOUNDATION,
            subfield=MathSubfield.NUMBER_ARITHMETIC_FOUNDATIONS,
            definition=(
                "Zero represents having no objects or quantity. It is the neutral point on the "
                "number line between positive and negative numbers."
            ),
            synonyms=["0", "nothing", "no objects"],
            common_notation=["0"],
            examples=[
                MathExample(
                    name="No apples example",
                    description="If you had 3 apples and gave away all 3, you now have zero apples.",
                    is_counterexample=False,
                ),
                MathExample(
                    name="Number line anchor",
                    description="On the number line, zero is the point that separates positive and negative numbers.",
                    is_counterexample=False,
                ),
            ],
            historical_notes=(
                "Different ancient cultures represented 'nothing' in different ways, but a fully developed "
                "symbol for zero as a number emerged clearly in the Hindu-Arabic numeral system."
            ),
            related_concepts=["math_concept_natural_numbers", "math_concept_negative_numbers"],
        )
    )

    # One
    concepts.append(
        MathConcept(
            id="math_concept_one",
            name="One",
            level=MathLevel.SCHOOL_FOUNDATION,
            subfield=MathSubfield.NUMBER_ARITHMETIC_FOUNDATIONS,
            definition=(
                "One represents a single object or unit. It is the basic building block for counting and "
                "measuring quantities."
            ),
            synonyms=["1", "single", "unit"],
            common_notation=["1"],
            examples=[
                MathExample(
                    name="One object",
                    description="A single apple on a table is an example of 'one'.",
                    is_counterexample=False,
                ),
                MathExample(
                    name="One dollar",
                    description="One dollar is a concrete example of the number one in money contexts.",
                    is_counterexample=False,
                ),
            ],
            historical_notes=(
                "The idea of 'one' as a unit appears in every counting system. Many numeral systems use a "
                "simple mark or symbol to represent one, and build larger numbers from it."
            ),
            related_concepts=["math_concept_zero", "math_concept_natural_numbers"],
        )
    )

    # Natural numbers (0, 1, 2, 3, ...)
    concepts.append(
        MathConcept(
            id="math_concept_natural_numbers",
            name="Natural Numbers",
            level=MathLevel.SCHOOL_FOUNDATION,
            subfield=MathSubfield.NUMBER_ARITHMETIC_FOUNDATIONS,
            definition=(
                "Natural numbers are the counting numbers we use to count objects. Depending on convention, "
                "they may start at 1 or at 0 and continue 2, 3, 4, and so on."
            ),
            synonyms=["counting numbers"],
            common_notation=["ℕ", "N"],
            examples=[
                MathExample(
                    name="Counting apples",
                    description="When you count apples as 1, 2, 3, you are using natural numbers.",
                    is_counterexample=False,
                ),
                MathExample(
                    name="Including zero (some conventions)",
                    description="In many modern contexts, natural numbers include 0, 1, 2, 3, ...",
                    is_counterexample=False,
                ),
                MathExample(
                    name="Non-example: fractions",
                    description="Numbers like 1/2 or 2.5 are not natural numbers.",
                    is_counterexample=True,
                ),
            ],
            historical_notes=(
                "People used counting numbers long before formal mathematics. Different cultures had "
                "different symbols and words, but the idea of counting objects with 1, 2, 3 is universal."
            ),
            related_concepts=["math_concept_zero", "math_concept_one"],
        )
    )

    # Negative numbers (intro concept)
    concepts.append(
        MathConcept(
            id="math_concept_negative_numbers",
            name="Negative Numbers",
            level=MathLevel.SCHOOL_FOUNDATION,
            subfield=MathSubfield.NUMBER_ARITHMETIC_FOUNDATIONS,
            definition=(
                "Negative numbers are numbers less than zero. They can represent ideas like owing money or "
                "temperatures below zero."
            ),
            synonyms=["numbers less than zero"],
            common_notation=["-1", "-2", "-3", "..."],
            examples=[
                MathExample(
                    name="Owing money",
                    description="If you owe someone $2, you can think of this as having -2 dollars.",
                    is_counterexample=False,
                ),
                MathExample(
                    name="Below zero temperature",
                    description="A temperature of -5 degrees is 5 degrees below zero on the thermometer.",
                    is_counterexample=False,
                ),
            ],
            historical_notes=(
                "Negative numbers took longer to be widely accepted in mathematics. They were used in some "
                "ancient calculations but were not fully embraced until much later in the history of algebra."
            ),
            related_concepts=["math_concept_zero", "math_concept_integers"],
        )
    )

    # Integers (… -2, -1, 0, 1, 2, …)
    concepts.append(
        MathConcept(
            id="math_concept_integers",
            name="Integers",
            level=MathLevel.SCHOOL_FOUNDATION,
            subfield=MathSubfield.NUMBER_ARITHMETIC_FOUNDATIONS,
            definition=(
                "Integers are the whole numbers together with their negatives and zero: ..., -2, -1, 0, 1, 2, ...."
            ),
            synonyms=["whole numbers with negatives"],
            common_notation=["ℤ", "Z"],
            examples=[
                MathExample(
                    name="Number line points",
                    description="The marked points at equal steps on the number line, such as -2, -1, 0, 1, 2, are integers.",
                    is_counterexample=False,
                ),
                MathExample(
                    name="Non-example: 1/2",
                    description="A number like 1/2 is not an integer because it is not a whole number.",
                    is_counterexample=True,
                ),
            ],
            historical_notes=(
                "Integers extend the natural numbers by adding negatives. This made it easier to handle debts, "
                "temperatures, and algebraic equations with solutions less than zero."
            ),
            related_concepts=["math_concept_natural_numbers", "math_concept_negative_numbers"],
        )
    )

    return concepts

def get_number_arithmetic_operations_and_comparisons() -> list[MathConcept]:
    """
    Seed concepts for School foundation → Number & arithmetic foundations:
    basic operations (addition, subtraction) and comparison relations
    (less than, greater than, equal to).
    """
    concepts: list[MathConcept] = []

    # Addition
    concepts.append(
        MathConcept(
            id="math_concept_addition",
            name="Addition",
            level=MathLevel.SCHOOL_FOUNDATION,
            subfield=MathSubfield.NUMBER_ARITHMETIC_FOUNDATIONS,
            definition=(
                "Addition is putting two or more numbers together to find the total or sum."
            ),
            synonyms=["adding", "sum", "plus"],
            common_notation=["+", "a + b", "sum"],
            examples=[
                MathExample(
                    name="Combining objects",
                    description="If you have 2 apples and get 3 more, 2 + 3 = 5 apples in all.",
                    is_counterexample=False,
                ),
                MathExample(
                    name="Money example",
                    description="Adding $4 and $6 gives $10: 4 + 6 = 10.",
                    is_counterexample=False,
                ),
                MathExample(
                    name="Non-example: just writing numbers",
                    description=(
                        "Writing '2 3' without a plus sign is not addition; it does not "
                        "tell us to combine the numbers."
                    ),
                    is_counterexample=True,
                ),
            ],
            historical_notes=(
                "Addition is one of the oldest arithmetic operations, used in counting "
                "and trade in many ancient cultures."
            ),
            related_concepts=[
                "math_concept_zero",
                "math_concept_one",
                "math_concept_natural_numbers",
                "math_concept_integers",
                "math_concept_subtraction",
                "math_concept_greater_than",
                "math_concept_less_than",
                "math_concept_equal_to",
            ],
        )
    )

    # Subtraction
    concepts.append(
        MathConcept(
            id="math_concept_subtraction",
            name="Subtraction",
            level=MathLevel.SCHOOL_FOUNDATION,
            subfield=MathSubfield.NUMBER_ARITHMETIC_FOUNDATIONS,
            definition=(
                "Subtraction is taking one number away from another to find how many are left, "
                "called the difference."
            ),
            synonyms=["taking away", "difference", "minus"],
            common_notation=["-", "a - b", "difference"],
            examples=[
                MathExample(
                    name="Taking away objects",
                    description="If you have 7 apples and give away 4, 7 - 4 = 3 apples left.",
                    is_counterexample=False,
                ),
                MathExample(
                    name="Temperature drop",
                    description=(
                        "If the temperature goes from 10 degrees down to 3 degrees, "
                        "the change is 10 - 3 = 7 degrees."
                    ),
                    is_counterexample=False,
                ),
                MathExample(
                    name="Non-example: reversed order",
                    description=(
                        "Saying 3 - 7 = 4 is incorrect; subtraction is not commutative and "
                        "3 - 7 is less than zero."
                    ),
                    is_counterexample=True,
                ),
            ],
            historical_notes=(
                "Subtraction appears alongside addition in early arithmetic. Naming the minuend, "
                "subtrahend, and difference helped formalize the operation."
            ),
            related_concepts=[
                "math_concept_zero",
                "math_concept_natural_numbers",
                "math_concept_negative_numbers",
                "math_concept_integers",
                "math_concept_addition",
                "math_concept_greater_than",
                "math_concept_less_than",
                "math_concept_equal_to",
            ],
        )
    )

    # Less than
    concepts.append(
        MathConcept(
            id="math_concept_less_than",
            name="Less Than",
            level=MathLevel.SCHOOL_FOUNDATION,
            subfield=MathSubfield.NUMBER_ARITHMETIC_FOUNDATIONS,
            definition=(
                "The phrase 'less than' and the symbol '<' are used when the first number "
                "is smaller than the second number."
            ),
            synonyms=["smaller than", "fewer than"],
            common_notation=["<", "a < b"],
            examples=[
                MathExample(
                    name="Whole number comparison",
                    description="3 < 5 because 3 is a smaller number than 5.",
                    is_counterexample=False,
                ),
                MathExample(
                    name="Money comparison",
                    description="$2 is less than $10, so 2 < 10.",
                    is_counterexample=False,
                ),
                MathExample(
                    name="Non-example: reversed relation",
                    description="Saying 8 < 4 is incorrect, because 8 is greater than 4.",
                    is_counterexample=True,
                ),
            ],
            historical_notes=(
                "Comparison symbols such as '<' and '>' became standard relatively late in "
                "the history of arithmetic, helping to quickly express number relationships."
            ),
            related_concepts=[
                "math_concept_greater_than",
                "math_concept_equal_to",
                "math_concept_natural_numbers",
                "math_concept_integers",
            ],
        )
    )

    # Greater than
    concepts.append(
        MathConcept(
            id="math_concept_greater_than",
            name="Greater Than",
            level=MathLevel.SCHOOL_FOUNDATION,
            subfield=MathSubfield.NUMBER_ARITHMETIC_FOUNDATIONS,
            definition=(
                "The phrase 'greater than' and the symbol '>' are used when the first number "
                "is larger than the second number."
            ),
            synonyms=["more than", "larger than"],
            common_notation=[">", "a > b"],
            examples=[
                MathExample(
                    name="Whole number comparison",
                    description="9 > 4 because 9 is a larger number than 4.",
                    is_counterexample=False,
                ),
                MathExample(
                    name="Temperature comparison",
                    description="20 degrees is greater than 5 degrees, so 20 > 5.",
                    is_counterexample=False,
                ),
                MathExample(
                    name="Non-example: equal numbers",
                    description="Saying 7 > 7 is incorrect, because 7 is equal to 7, not greater.",
                    is_counterexample=True,
                ),
            ],
            historical_notes=(
                "Greater-than comparisons are introduced early as 'more than' in counting and "
                "measurement activities before children see the '>' symbol."
            ),
            related_concepts=[
                "math_concept_less_than",
                "math_concept_equal_to",
                "math_concept_natural_numbers",
                "math_concept_integers",
            ],
        )
    )

    # Equal to
    concepts.append(
        MathConcept(
            id="math_concept_equal_to",
            name="Equal To",
            level=MathLevel.SCHOOL_FOUNDATION,
            subfield=MathSubfield.NUMBER_ARITHMETIC_FOUNDATIONS,
            definition=(
                "The phrase 'equal to' and the symbol '=' are used when two quantities have "
                "the same value."
            ),
            synonyms=["same as", "has the same value as"],
            common_notation=["=", "a = b"],
            examples=[
                MathExample(
                    name="Simple equality",
                    description="3 + 2 = 5 means the total on the left is the same as the number on the right.",
                    is_counterexample=False,
                ),
                MathExample(
                    name="Different expressions, same value",
                    description="4 + 1 and 2 + 3 are equal because both make 5, so 4 + 1 = 2 + 3.",
                    is_counterexample=False,
                ),
                MathExample(
                    name="Non-example: unequal values",
                    description="Saying 2 + 2 = 5 is incorrect, because 2 + 2 equals 4, not 5.",
                    is_counterexample=True,
                ),
            ],
            historical_notes=(
                "The '=' sign was introduced in the 16th century to avoid writing 'is equal to' "
                "over and over in equations."
            ),
            related_concepts=[
                "math_concept_addition",
                "math_concept_subtraction",
                "math_concept_less_than",
                "math_concept_greater_than",
                "math_concept_natural_numbers",
            ],
        )
    )

    return concepts

def get_number_arithmetic_foundation_path() -> MathTeachingPath:
    """
    Ordered path for early number & arithmetic foundations.
    """
    steps: list[MathTeachingStep] = []

    # 1. Zero
    steps.append(
        MathTeachingStep(
            order=1,
            concept_id="math_concept_zero",
            headline="Start with Zero as the anchor",
            rationale=(
                "Zero is the neutral point on the number line and the idea of 'none'. "
                "It anchors later ideas about positive and negative numbers."
            ),
        )
    )

    # 2. One
    steps.append(
        MathTeachingStep(
            order=2,
            concept_id="math_concept_one",
            headline="Introduce One as a single unit",
            rationale=(
                "One is the basic counting unit. Understanding 'one' as a single object "
                "sets up counting and measuring."
            ),
        )
    )

    # 3. Natural numbers
    steps.append(
        MathTeachingStep(
            order=3,
            concept_id="math_concept_natural_numbers",
            headline="Extend to Natural Numbers for counting",
            rationale=(
                "Natural numbers generalize counting beyond 0 and 1 to 2, 3, 4, and so on, "
                "forming the backbone of early arithmetic."
            ),
        )
    )

    # 4. Negative numbers
    steps.append(
        MathTeachingStep(
            order=4,
            concept_id="math_concept_negative_numbers",
            headline="Introduce Negative Numbers for 'less than zero'",
            rationale=(
                "Negative numbers allow learners to represent debts, temperatures below zero, "
                "and positions to the left of zero on the number line."
            ),
        )
    )

    # 5. Integers
    steps.append(
        MathTeachingStep(
            order=5,
            concept_id="math_concept_integers",
            headline="Unify with Integers as whole numbers and their negatives",
            rationale=(
                "Integers combine natural numbers, zero, and negative numbers into a single system "
                "that supports basic algebra and number line reasoning."
            ),
        )
    )

    # 6. Addition
    steps.append(
        MathTeachingStep(
            order=6,
            concept_id="math_concept_addition",
            headline="Build Addition as combining quantities",
            rationale=(
                "Once learners know whole numbers, addition lets them combine quantities and think "
                "about totals and sums in many contexts."
            ),
        )
    )

    # 7. Subtraction
    steps.append(
        MathTeachingStep(
            order=7,
            concept_id="math_concept_subtraction",
            headline="Introduce Subtraction as taking away and differences",
            rationale=(
                "Subtraction complements addition by modeling 'taking away' and 'how much more', "
                "which appears naturally in stories and word problems."
            ),
        )
    )

    # 8. Less than
    steps.append(
        MathTeachingStep(
            order=8,
            concept_id="math_concept_less_than",
            headline="Use 'Less Than' to compare smaller quantities",
            rationale=(
                "The 'less than' relation and '<' symbol help learners compare numbers and reason "
                "about which quantities are smaller."
            ),
        )
    )

    # 9. Greater than
    steps.append(
        MathTeachingStep(
            order=9,
            concept_id="math_concept_greater_than",
            headline="Use 'Greater Than' to compare larger quantities",
            rationale=(
                "The 'greater than' relation and '>' symbol complete the basic comparison story, "
                "supporting number line reasoning and word problems."
            ),
        )
    )

    # 10. Equal to
    steps.append(
        MathTeachingStep(
            order=10,
            concept_id="math_concept_equal_to",
            headline="Stabilize with 'Equal To' and the '=' symbol",
            rationale=(
                "The idea of equality ties arithmetic together: equations state that two expressions "
                "have the same value, preparing students for pre-algebra."
            ),
        )
    )

    return MathTeachingPath(
        id="number_arithmetic_foundations",
        level=MathLevel.SCHOOL_FOUNDATION,
        subfield=MathSubfield.NUMBER_ARITHMETIC_FOUNDATIONS,
        title="Number & Arithmetic Foundations Path",
        description=(
            "An ordered path through early number and arithmetic ideas, starting from zero and "
            "counting and building up to integers, operations, and basic comparisons."
        ),
        steps=steps,
    )

def get_prealgebra_equations_basics() -> list[MathConcept]:
    """
    Seed concepts for School foundation → Prealgebra & early algebra:
    basic equation-thinking vocabulary (expression, equation, unknown, solve).
    """
    concepts: list[MathConcept] = []

    # Expression
    concepts.append(
        MathConcept(
            id="math_concept_expression",
            name="Expression",
            level=MathLevel.SCHOOL_FOUNDATION,
            subfield=MathSubfield.PREALGEBRA_EARLY_ALGEBRA,
            definition=(
                "An expression is a math phrase made from numbers, symbols, and operations, "
                "but it does not have an equals sign."
            ),
            synonyms=["math phrase", "numerical expression"],
            common_notation=["3 + 4", "2 * 5", "a + 3"],
            examples=[
                MathExample(
                    name="Simple numerical expression",
                    description="'3 + 4' is an expression because it shows a calculation but has no equals sign.",
                    is_counterexample=False,
                ),
                MathExample(
                    name="Expression with a letter",
                    description="'a + 3' is an expression that can stand for many possible values depending on a.",
                    is_counterexample=False,
                ),
                MathExample(
                    name="Non-example: equation",
                    description="'3 + 4 = 7' is not just an expression; it is an equation because it has an equals sign.",
                    is_counterexample=True,
                ),
            ],
            historical_notes=(
                "Expressions became more common as algebraic notation developed, allowing mathematicians "
                "to write general rules and patterns compactly."
            ),
            related_concepts=[
                "math_concept_equation",
                "math_concept_unknown",
            ],
        )
    )

    # Equation
    concepts.append(
        MathConcept(
            id="math_concept_equation",
            name="Equation",
            level=MathLevel.SCHOOL_FOUNDATION,
            subfield=MathSubfield.PREALGEBRA_EARLY_ALGEBRA,
            definition=(
                "An equation is a math statement that two expressions have the same value, "
                "shown with an equals sign."
            ),
            synonyms=["math sentence", "equality statement"],
            common_notation=["=", "a + 3 = 7"],
            examples=[
                MathExample(
                    name="Simple equation",
                    description="'3 + 4 = 7' is an equation because it uses '=' to say both sides are equal.",
                    is_counterexample=False,
                ),
                MathExample(
                    name="Equation with unknown",
                    description="'x + 5 = 9' is an equation that can be solved to find the value of x.",
                    is_counterexample=False,
                ),
                MathExample(
                    name="Non-example: expression only",
                    description="'2 * 6' is not an equation because it has no equals sign.",
                    is_counterexample=True,
                ),
            ],
            historical_notes=(
                "Equations and the '=' symbol were formalized to avoid writing 'is equal to' repeatedly, "
                "making algebraic reasoning more efficient."
            ),
            related_concepts=[
                "math_concept_expression",
                "math_concept_unknown",
                "math_concept_solve_equation",
                "math_concept_equal_to",
            ],
        )
    )

    # Unknown
    concepts.append(
        MathConcept(
            id="math_concept_unknown",
            name="Unknown",
            level=MathLevel.SCHOOL_FOUNDATION,
            subfield=MathSubfield.PREALGEBRA_EARLY_ALGEBRA,
            definition=(
                "An unknown is a value in a math problem that we do not know yet and often "
                "represent with a letter like x or a blank."
            ),
            synonyms=["missing number", "variable (early sense)"],
            common_notation=["x", "?", "__"],
            examples=[
                MathExample(
                    name="Missing number in an equation",
                    description="In 'x + 3 = 7', x is the unknown number we want to find.",
                    is_counterexample=False,
                ),
                MathExample(
                    name="Blank as unknown",
                    description="In '__ + 5 = 9', the blank stands for the unknown number that makes the equation true.",
                    is_counterexample=False,
                ),
                MathExample(
                    name="Non-example: known number",
                    description="In '4 + 3 = 7', 4 is not an unknown; its value is already given.",
                    is_counterexample=True,
                ),
            ],
            historical_notes=(
                "Using letters to stand for unknown quantities became standard in algebra, "
                "allowing general methods for solving many problems at once."
            ),
            related_concepts=[
                "math_concept_equation",
                "math_concept_solve_equation",
            ],
        )
    )

    # Solve an equation
    concepts.append(
        MathConcept(
            id="math_concept_solve_equation",
            name="Solve an Equation",
            level=MathLevel.SCHOOL_FOUNDATION,
            subfield=MathSubfield.PREALGEBRA_EARLY_ALGEBRA,
            definition=(
                "To solve an equation means to find the value of the unknown that makes the equation true."
            ),
            synonyms=["find the solution", "find the missing number"],
            common_notation=["solve x + 3 = 7", "solution to an equation"],
            examples=[
                MathExample(
                    name="Simple solving example",
                    description="To solve 'x + 3 = 7', we find x = 4 because 4 + 3 = 7 makes the equation true.",
                    is_counterexample=False,
                ),
                MathExample(
                    name="Check a solution",
                    description="If we think x = 5 for 'x + 3 = 7', checking 5 + 3 = 8 shows this is not a solution.",
                    is_counterexample=False,
                ),
                MathExample(
                    name="Non-example: just computing",
                    description="Finding 3 + 4 = 7 is not 'solving an equation' because there is no unknown.",
                    is_counterexample=True,
                ),
            ],
            historical_notes=(
                "Systematic methods for solving equations are a core part of algebra, building on "
                "earlier ideas from arithmetic and balance scales."
            ),
            related_concepts=[
                "math_concept_equation",
                "math_concept_unknown",
                "math_concept_equal_to",
            ],
        )
    )

    return concepts

def get_prealgebra_equations_basics_path() -> MathTeachingPath:
    """
    Ordered path for prealgebra & early algebra equation-thinking basics.
    """
    steps: list[MathTeachingStep] = []

    # 1. Expression
    steps.append(
        MathTeachingStep(
            order=1,
            concept_id="math_concept_expression",
            headline="Start with Expressions as math phrases",
            rationale=(
                "Expressions are math phrases made of numbers, symbols, and operations "
                "without an equals sign. Learners must first recognize and read these phrases."
            ),
        )
    )

    # 2. Equation
    steps.append(
        MathTeachingStep(
            order=2,
            concept_id="math_concept_equation",
            headline="Introduce Equations as equality statements",
            rationale=(
                "Equations use an equals sign to say that two expressions have the same value, "
                "turning phrases into statements that can be true or false."
            ),
        )
    )

    # 3. Unknown
    steps.append(
        MathTeachingStep(
            order=3,
            concept_id="math_concept_unknown",
            headline="Highlight the Unknown as the missing value",
            rationale=(
                "Marking a value as unknown (with a letter or blank) helps students focus on "
                "what needs to be found to make an equation true."
            ),
        )
    )

    # 4. Solve an equation
    steps.append(
        MathTeachingStep(
            order=4,
            concept_id="math_concept_solve_equation",
            headline="Solve Equations by finding the unknown",
            rationale=(
                "Solving an equation means finding the unknown value that makes both sides equal, "
                "connecting arithmetic operations to the idea of balancing."
            ),
        )
    )

    return MathTeachingPath(
        id="prealgebra_equations_basics",
        level=MathLevel.SCHOOL_FOUNDATION,
        subfield=MathSubfield.PREALGEBRA_EARLY_ALGEBRA,
        title="Prealgebra Equation Basics Path",
        description=(
            "An ordered path through basic equation-thinking ideas: expressions, equations, "
            "unknowns, and solving equations."
        ),
        steps=steps,
    )

def get_geometry_early_foundations() -> list[MathConcept]:
    """
    Seed concepts for School foundation → School geometry:
    basic geometric objects (point, line, line segment, ray, angle, simple shapes).
    """
    concepts: list[MathConcept] = []

    # Point
    concepts.append(
        MathConcept(
            id="math_concept_point",
            name="Point",
            level=MathLevel.SCHOOL_FOUNDATION,
            subfield=MathSubfield.SCHOOL_GEOMETRY,
            definition=(
                "A point shows an exact location in space. It has no length, width, or thickness."
            ),
            synonyms=["location", "dot (informal)"],
            common_notation=["A", "B", "P"],
            examples=[
                MathExample(
                    name="Dot on paper",
                    description="A small dot on a piece of paper can stand for a point named A.",
                    is_counterexample=False,
                ),
                MathExample(
                    name="Marked corner",
                    description="A corner of a room can be labeled as point P to mark its location.",
                    is_counterexample=False,
                ),
                MathExample(
                    name="Non-example: a region",
                    description="A shaded area is not a single point; it covers many locations.",
                    is_counterexample=True,
                ),
            ],
            historical_notes=(
                "Points are one of the basic building blocks in geometry, used since ancient Greek mathematics."
            ),
            related_concepts=[
                "math_concept_line",
                "math_concept_line_segment",
                "math_concept_ray",
                "math_concept_angle",
            ],
        )
    )

    # Line
    concepts.append(
        MathConcept(
            id="math_concept_line",
            name="Line",
            level=MathLevel.SCHOOL_FOUNDATION,
            subfield=MathSubfield.SCHOOL_GEOMETRY,
            definition=(
                "A line is a straight path that goes on forever in both directions. "
                "It has no thickness."
            ),
            synonyms=["straight line"],
            common_notation=["line AB", "←→AB"],
            examples=[
                MathExample(
                    name="Straight edge path",
                    description="The path traced by a ruler edge, extended without end, models a line.",
                    is_counterexample=False,
                ),
                MathExample(
                    name="Non-example: line segment",
                    description="A short piece of a line with two endpoints is a segment, not an infinite line.",
                    is_counterexample=True,
                ),
            ],
            historical_notes=(
                "Lines were described in Euclid's Elements as 'breadthless length', forming the basis of classical geometry."
            ),
            related_concepts=[
                "math_concept_point",
                "math_concept_line_segment",
                "math_concept_ray",
            ],
        )
    )

    # Line segment
    concepts.append(
        MathConcept(
            id="math_concept_line_segment",
            name="Line Segment",
            level=MathLevel.SCHOOL_FOUNDATION,
            subfield=MathSubfield.SCHOOL_GEOMETRY,
            definition=(
                "A line segment is a straight part of a line with two endpoints."
            ),
            synonyms=["segment"],
            common_notation=["segment AB", "AB"],
            examples=[
                MathExample(
                    name="Edge of a book",
                    description="The straight edge of a book from one corner to another is like a line segment.",
                    is_counterexample=False,
                ),
                MathExample(
                    name="Non-example: curved side",
                    description="A curved side is not a line segment because it is not straight.",
                    is_counterexample=True,
                ),
            ],
            historical_notes=(
                "Segments let us measure distances between points, unlike infinite lines."
            ),
            related_concepts=[
                "math_concept_point",
                "math_concept_line",
                "math_concept_ray",
            ],
        )
    )

    # Ray
    concepts.append(
        MathConcept(
            id="math_concept_ray",
            name="Ray",
            level=MathLevel.SCHOOL_FOUNDATION,
            subfield=MathSubfield.SCHOOL_GEOMETRY,
            definition=(
                "A ray starts at one point and goes on forever in one direction."
            ),
            synonyms=["half-line"],
            common_notation=["ray AB", "→AB"],
            examples=[
                MathExample(
                    name="Flashlight beam",
                    description="Light from a flashlight can be modeled as a ray starting at the bulb and going outward.",
                    is_counterexample=False,
                ),
                MathExample(
                    name="Non-example: segment",
                    description="A segment that stops at two endpoints is not a ray.",
                    is_counterexample=True,
                ),
            ],
            historical_notes=(
                "Rays help describe directions and angles in geometry."
            ),
            related_concepts=[
                "math_concept_point",
                "math_concept_line",
                "math_concept_line_segment",
                "math_concept_angle",
            ],
        )
    )

    # Angle
    concepts.append(
        MathConcept(
            id="math_concept_angle",
            name="Angle",
            level=MathLevel.SCHOOL_FOUNDATION,
            subfield=MathSubfield.SCHOOL_GEOMETRY,
            definition=(
                "An angle is formed by two rays that share the same starting point, called the vertex."
            ),
            synonyms=["corner angle", "vertex angle"],
            common_notation=["∠ABC"],
            examples=[
                MathExample(
                    name="Corner of a square",
                    description="Each corner of a square is a right angle, formed by two line segments meeting.",
                    is_counterexample=False,
                ),
                MathExample(
                    name="Clock hands",
                    description="The hands of a clock make different angles as they move.",
                    is_counterexample=False,
                ),
                MathExample(
                    name="Non-example: single ray",
                    description="A single ray by itself is not an angle; you need two rays.",
                    is_counterexample=True,
                ),
            ],
            historical_notes=(
                "Studying angles is central to geometry, from basic shapes to trigonometry."
            ),
            related_concepts=[
                "math_concept_point",
                "math_concept_ray",
                "math_concept_line_segment",
                "math_concept_triangle",
            ],
        )
    )

    # Triangle
    concepts.append(
        MathConcept(
            id="math_concept_triangle",
            name="Triangle",
            level=MathLevel.SCHOOL_FOUNDATION,
            subfield=MathSubfield.SCHOOL_GEOMETRY,
            definition=(
                "A triangle is a shape made of three line segments that meet to form three angles."
            ),
            synonyms=["3-sided polygon"],
            common_notation=["△ABC"],
            examples=[
                MathExample(
                    name="Triangular road sign",
                    description="Many warning road signs have a triangular shape with three straight sides.",
                    is_counterexample=False,
                ),
                MathExample(
                    name="Non-example: shape with four sides",
                    description="A shape with four sides is not a triangle; it is a quadrilateral.",
                    is_counterexample=True,
                ),
            ],
            historical_notes=(
                "Triangles are one of the most studied shapes in geometry because knowing side lengths and angles "
                "tells us a lot about the shape."
            ),
            related_concepts=[
                "math_concept_angle",
                "math_concept_line_segment",
            ],
        )
    )

    # Square
    concepts.append(
        MathConcept(
            id="math_concept_square",
            name="Square",
            level=MathLevel.SCHOOL_FOUNDATION,
            subfield=MathSubfield.SCHOOL_GEOMETRY,
            definition=(
                "A square is a shape with four equal sides and four right angles."
            ),
            synonyms=["4 equal-sided rectangle (informal)"],
            common_notation=["square ABCD"],
            examples=[
                MathExample(
                    name="Square tile",
                    description="A floor tile with four equal sides and four right corners is a square.",
                    is_counterexample=False,
                ),
                MathExample(
                    name="Non-example: rectangle with unequal sides",
                    description="A rectangle with two long and two short sides is not a square.",
                    is_counterexample=True,
                ),
            ],
            historical_notes=(
                "Squares appear in tiling, area calculations, and coordinate geometry."
            ),
            related_concepts=[
                "math_concept_line_segment",
                "math_concept_angle",
                "math_concept_triangle",
            ],
        )
    )

    return concepts

def get_geometry_early_operations() -> list[MathConcept]:
    """
    Early geometry operations and classifications:
    angle types (right, acute, obtuse), perimeter, and area of rectangles/squares.
    """
    concepts: list[MathConcept] = []

    # Right angle
    concepts.append(
        MathConcept(
            id="math_concept_right_angle",
            name="Right Angle",
            level=MathLevel.SCHOOL_FOUNDATION,
            subfield=MathSubfield.SCHOOL_GEOMETRY,
            definition=(
                "A right angle is an angle that measures exactly 90 degrees, like the corner of a square."
            ),
            synonyms=["square corner"],
            common_notation=["90 degrees", "right angle mark"],
            examples=[
                MathExample(
                    name="Corner of paper",
                    description="The corner of a sheet of paper is a right angle.",
                    is_counterexample=False,
                ),
                MathExample(
                    name="Non-example: too narrow",
                    description="An angle much smaller than a square corner is not a right angle; it is acute.",
                    is_counterexample=True,
                ),
            ],
            historical_notes=(
                "Right angles appear in many building and design tasks and are central to coordinate geometry."
            ),
            related_concepts=[
                "math_concept_angle",
                "math_concept_acute_angle",
                "math_concept_obtuse_angle",
                "math_concept_square",
            ],
        )
    )

    # Acute angle
    concepts.append(
        MathConcept(
            id="math_concept_acute_angle",
            name="Acute Angle",
            level=MathLevel.SCHOOL_FOUNDATION,
            subfield=MathSubfield.SCHOOL_GEOMETRY,
            definition=(
                "An acute angle is an angle that is smaller than a right angle; it measures less than 90 degrees."
            ),
            synonyms=["sharp angle"],
            common_notation=["angle < 90 degrees"],
            examples=[
                MathExample(
                    name="Narrow corner",
                    description="The angle at the tip of a narrow triangle is often an acute angle.",
                    is_counterexample=False,
                ),
                MathExample(
                    name="Non-example: right angle",
                    description="An angle exactly like a square corner is not acute; it is a right angle.",
                    is_counterexample=True,
                ),
            ],
            historical_notes=(
                "Classifying angles as acute, right, and obtuse helps students describe and compare shapes."
            ),
            related_concepts=[
                "math_concept_angle",
                "math_concept_right_angle",
                "math_concept_obtuse_angle",
            ],
        )
    )

    # Obtuse angle
    concepts.append(
        MathConcept(
            id="math_concept_obtuse_angle",
            name="Obtuse Angle",
            level=MathLevel.SCHOOL_FOUNDATION,
            subfield=MathSubfield.SCHOOL_GEOMETRY,
            definition=(
                "An obtuse angle is an angle that is larger than a right angle but smaller than a straight line; "
                "it measures more than 90 degrees and less than 180 degrees."
            ),
            synonyms=["wide angle"],
            common_notation=["90 degrees < angle < 180 degrees"],
            examples=[
                MathExample(
                    name="Wide corner",
                    description="An angle that opens wider than a square corner but is not straight is obtuse.",
                    is_counterexample=False,
                ),
                MathExample(
                    name="Non-example: acute angle",
                    description="An angle that is smaller than a right angle is not obtuse; it is acute.",
                    is_counterexample=True,
                ),
            ],
            historical_notes=(
                "Recognizing obtuse angles helps learners analyze polygons and understand triangle types."
            ),
            related_concepts=[
                "math_concept_angle",
                "math_concept_right_angle",
                "math_concept_acute_angle",
            ],
        )
    )

    # Perimeter
    concepts.append(
        MathConcept(
            id="math_concept_perimeter",
            name="Perimeter",
            level=MathLevel.SCHOOL_FOUNDATION,
            subfield=MathSubfield.SCHOOL_GEOMETRY,
            definition=(
                "Perimeter is the total distance around the outside of a shape."
            ),
            synonyms=["distance around", "boundary length"],
            common_notation=["P", "perimeter"],
            examples=[
                MathExample(
                    name="Walking around a field",
                    description="Walking once around the edge of a rectangular field traces its perimeter.",
                    is_counterexample=False,
                ),
                MathExample(
                    name="Square perimeter formula",
                    description="For a square with side length s, the perimeter is 4 * s.",
                    is_counterexample=False,
                ),
                MathExample(
                    name="Non-example: area",
                    description="Counting the number of tiles inside a floor finds area, not perimeter.",
                    is_counterexample=True,
                ),
            ],
            historical_notes=(
                "Perimeter is used in tasks like fencing a yard or framing a picture, where only the boundary matters."
            ),
            related_concepts=[
                "math_concept_square",
                "math_concept_triangle",
                "math_concept_area",
            ],
        )
    )

    # Area
    concepts.append(
        MathConcept(
            id="math_concept_area",
            name="Area",
            level=MathLevel.SCHOOL_FOUNDATION,
            subfield=MathSubfield.SCHOOL_GEOMETRY,
            definition=(
                "Area is the amount of flat space a shape covers on a surface."
            ),
            synonyms=["space inside"],
            common_notation=["A", "area"],
            examples=[
                MathExample(
                    name="Covering a table",
                    description="The area of a table tells how much surface you have to cover with a cloth.",
                    is_counterexample=False,
                ),
                MathExample(
                    name="Rectangle area formula",
                    description="For a rectangle with length L and width W, the area is L * W.",
                    is_counterexample=False,
                ),
                MathExample(
                    name="Non-example: perimeter",
                    description="Measuring only the edge of a shape finds perimeter, not area.",
                    is_counterexample=True,
                ),
            ],
            historical_notes=(
                "Area is used in planning floors, fields, and many real-world spaces and leads toward understanding volume."
            ),
            related_concepts=[
                "math_concept_square",
                "math_concept_triangle",
                "math_concept_perimeter",
            ],
        )
    )

    return concepts

def get_geometry_early_foundations_path() -> MathTeachingPath:
    """
    Ordered path for early-school geometry foundations.
    """
    steps: list[MathTeachingStep] = []

    # 1. Point
    steps.append(
        MathTeachingStep(
            order=1,
            concept_id="math_concept_point",
            headline="Start with Points as locations",
            rationale=(
                "Points are the simplest geometric idea: an exact location. "
                "They are the building blocks for all other geometry objects."
            ),
        )
    )

    # 2. Line
    steps.append(
        MathTeachingStep(
            order=2,
            concept_id="math_concept_line",
            headline="Extend to Lines as infinite straight paths",
            rationale=(
                "Lines connect points and show straight paths that continue forever, "
                "preparing students to think about direction and alignment."
            ),
        )
    )

    # 3. Line segment
    steps.append(
        MathTeachingStep(
            order=3,
            concept_id="math_concept_line_segment",
            headline="Introduce Segments for measurable distances",
            rationale=(
                "Line segments are finite parts of lines with endpoints, so they can be "
                "measured and used to build shapes."
            ),
        )
    )

    # 4. Ray
    steps.append(
        MathTeachingStep(
            order=4,
            concept_id="math_concept_ray",
            headline="Add Rays for one-way directions",
            rationale=(
                "Rays model one-way directions (like light beams) and are essential for "
                "defining angles."
            ),
        )
    )

    # 5. Angle
    steps.append(
        MathTeachingStep(
            order=5,
            concept_id="math_concept_angle",
            headline="Form Angles from rays",
            rationale=(
                "Angles describe how two rays meet at a point, letting learners talk about "
                "corners, turns, and rotations."
            ),
        )
    )

    # 6. Triangle
    steps.append(
        MathTeachingStep(
            order=6,
            concept_id="math_concept_triangle",
            headline="Build Triangles from segments and angles",
            rationale=(
                "Triangles are the simplest closed shapes built from segments and angles, "
                "and are central to later geometry."
            ),
        )
    )

    # 7. Square
    steps.append(
        MathTeachingStep(
            order=7,
            concept_id="math_concept_square",
            headline="Use Squares for equal sides and right angles",
            rationale=(
                "Squares combine equal segments and right angles, making them a natural "
                "example for perimeter and area."
            ),
        )
    )

    return MathTeachingPath(
        id="geometry_early_foundations",
        level=MathLevel.SCHOOL_FOUNDATION,
        subfield=MathSubfield.SCHOOL_GEOMETRY,
        title="Early Geometry Foundations Path",
        description=(
            "An ordered path through early geometry ideas, starting from points and lines "
            "and building up to angles and basic shapes."
        ),
        steps=steps,
    )
