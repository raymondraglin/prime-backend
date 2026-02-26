import random
from typing import List

from app.prime.math.practice.inequalities_models import (
    OneStepInequalityPracticeItem,
    OneStepInequalityPracticeSet,
)
from app.prime.math.practice.inequalities_two_step_models import (
    TwoStepInequalityPracticeItem,
    TwoStepInequalityPracticeSet,
)


def generate_one_step_inequality_practice(
    count: int = 5,
    min_a: int = -9,
    max_a: int = 9,
    min_b: int = -10,
    max_b: int = 10,
    min_k: int = -10,
    max_k: int = 10,
) -> OneStepInequalityPracticeSet:
    """
    Generate practice like ax + b < c or ax + b > c where the solution is
    x < K, x > K, x <= K, or x >= K.

    Sometimes a > 0 (no flip when dividing), sometimes a < 0 (flip required).
    """
    items: List[OneStepInequalityPracticeItem] = []

    for i in range(count):
        # choose non-zero coefficient a
        a = 0
        while a == 0:
            a = random.randint(min_a, max_a)

        # choose inequality direction for the *solution* first
        base_symbol = random.choice(["<", ">", "<=", ">="])

        # choose integer solution value k
        k = random.randint(min_k, max_k)

        # choose b, then construct c so inequality is true when x satisfies base_symbol with k
        b = random.randint(min_b, max_b)
        # c = a * k + b ensures that x = k makes ax + b = c
        c = a * k + b

        unknown_symbol = "x"

        # Build left side text, e.g. "3x + 2"
        left = f"{a}{unknown_symbol}"
        if b > 0:
            left += f" + {b}"
        elif b < 0:
            left += f" - {abs(b)}"

        # When solving:
        #   ax + b < c  -> subtract b, then divide by a.
        #   If a < 0, the inequality symbol flips.
        requires_flip = a < 0

        if requires_flip:
            # Flip inequality for the solution
            if base_symbol == "<":
                solution_symbol = ">"
            elif base_symbol == ">":
                solution_symbol = "<"
            elif base_symbol == "<=":
                solution_symbol = ">="
            else:  # ">="
                solution_symbol = "<="
        else:
            solution_symbol = base_symbol

        inequality_text = f"{left} {base_symbol} {c}"
        solution_description = f"{unknown_symbol} {solution_symbol} {k}"

        explanation = (
            f"Start with {inequality_text}. "
            f"Subtract {b} from both sides to undo the addition/subtraction, then divide both sides by {a}. "
        )
        if requires_flip:
            explanation += (
                f"Because you divided by a negative number, you must flip the inequality sign. "
            )
        else:
            explanation += (
                f"Because you divided by a positive number, the inequality sign stays the same. "
            )
        explanation += f"You get {solution_description}."

        items.append(
            OneStepInequalityPracticeItem(
                id=f"ineq_one_step_{i+1}",
                a=a,
                b=b,
                unknown_symbol=unknown_symbol,
                inequality_symbol=base_symbol,
                inequality_text=inequality_text,
                solution_description=solution_description,
                explanation=explanation,
                requires_flip=requires_flip,
            )
        )

    return OneStepInequalityPracticeSet(items=items)

def generate_two_step_inequality_practice(
    count: int = 5,
    min_a: int = -9,
    max_a: int = 9,
    min_b: int = -10,
    max_b: int = 10,
    min_k: int = -10,
    max_k: int = 10,
) -> TwoStepInequalityPracticeSet:
    """
    Generate two-step inequalities of the form ax + b < c.

    Solving requires two steps:
      1. Subtract b from both sides.
      2. Divide both sides by a (flip the inequality if a < 0).

    Both a and b are guaranteed to be non-zero so the problem is always two-step.
    """
    items: List[TwoStepInequalityPracticeItem] = []

    for i in range(count):
        # Choose a non-zero coefficient
        a = 0
        while a == 0:
            a = random.randint(min_a, max_a)

        # Choose a non-zero b so the problem is genuinely two-step
        b = 0
        while b == 0:
            b = random.randint(min_b, max_b)

        # Choose the solution value k and inequality direction
        k = random.randint(min_k, max_k)
        base_symbol = random.choice(["<", ">", "<=", ">="])

        # c is set so that ax + b = c when x = k
        c = a * k + b

        unknown_symbol = "x"

        # Build display text for the left side: e.g. "3x + 2" or "-4x - 7"
        left = f"{a}{unknown_symbol}"
        if b > 0:
            left += f" + {b}"
        elif b < 0:
            left += f" - {abs(b)}"

        requires_flip = a < 0

        # Determine solution symbol (flip if dividing by negative)
        if requires_flip:
            flip_map = {"<": ">", ">": "<", "<=": ">=", ">=": "<="}
            solution_symbol = flip_map[base_symbol]
        else:
            solution_symbol = base_symbol

        inequality_text = f"{left} {base_symbol} {c}"
        solution_description = f"{unknown_symbol} {solution_symbol} {k}"

        # Build explanation
        if b > 0:
            step1 = f"Subtract {b} from both sides to get {a}{unknown_symbol} {base_symbol} {c - b}."
        else:
            step1 = f"Add {abs(b)} to both sides to get {a}{unknown_symbol} {base_symbol} {c - b}."

        step2 = f"Divide both sides by {a}."

        if requires_flip:
            step2 += (
                f" Because you are dividing by a negative number, "
                f"the inequality sign flips from {base_symbol} to {solution_symbol}."
            )
        else:
            step2 += f" The inequality sign stays the same."

        explanation = (
            f"Start with {inequality_text}. "
            f"Step 1: {step1} "
            f"Step 2: {step2} "
            f"You get {solution_description}."
        )

        items.append(
            TwoStepInequalityPracticeItem(
                id=f"ineq_two_step_{i + 1}",
                a=a,
                b=b,
                c=c,
                unknown_symbol=unknown_symbol,
                inequality_symbol=base_symbol,
                inequality_text=inequality_text,
                solution_description=solution_description,
                explanation=explanation,
                requires_flip=requires_flip,
            )
        )

    return TwoStepInequalityPracticeSet(items=items)
