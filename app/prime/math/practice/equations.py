from enum import Enum
from typing import List

from pydantic import BaseModel


class EquationOperation(str, Enum):
    ADD = "add"
    SUBTRACT = "subtract"


class EquationPracticeItem(BaseModel):
    id: str
    operation: EquationOperation
    unknown_symbol: str
    equation_text: str
    solution: int
    explanation: str


class EquationPracticeSet(BaseModel):
    description: str
    items: List[EquationPracticeItem]


def generate_one_step_equation_practice(count: int = 10) -> EquationPracticeSet:
    """
    Generate simple one-step equations of the form:
    - x + k = result
    - x - k = result
    where x, k, and result are small integers.
    """
    # Clamp count
    if count < 1:
        count = 1
    if count > 50:
        count = 50

    items: list[EquationPracticeItem] = []
    unknown_symbol = "x"

    # Deterministic generation over a small grid to avoid randomness
    # x in [0, 10], k in [1, 10]
    problem_id = 1
    for x in range(0, 11):
        for k in range(1, 11):
            if len(items) >= count:
                break

            # Alternate between add and subtract to mix types
            if problem_id % 2 == 1:
                # Addition: x + k = result
                op = EquationOperation.ADD
                result = x + k
                equation_text = f"{unknown_symbol} + {k} = {result}"
                explanation = (
                    f"In the equation {equation_text}, we want to find {unknown_symbol}. "
                    f"To undo '+ {k}', subtract {k} from both sides: {result} - {k} = {x}, "
                    f"so {unknown_symbol} = {x}."
                )
            else:
                # Subtraction: x - k = result, ensure result is not negative
                if x < k:
                    continue
                op = EquationOperation.SUBTRACT
                result = x - k
                equation_text = f"{unknown_symbol} - {k} = {result}"
                explanation = (
                    f"In the equation {equation_text}, we want to find {unknown_symbol}. "
                    f"To undo '- {k}', add {k} to both sides: {result} + {k} = {x}, "
                    f"so {unknown_symbol} = {x}."
                )

            items.append(
                EquationPracticeItem(
                    id=f"eq_one_step_{problem_id}",
                    operation=op,
                    unknown_symbol=unknown_symbol,
                    equation_text=equation_text,
                    solution=x,
                    explanation=explanation,
                )
            )
            problem_id += 1
        if len(items) >= count:
            break

    return EquationPracticeSet(
        description=(
            "One-step equation practice for expressions of the form x + k = result "
            "or x - k = result, with small whole numbers."
        ),
        items=items,
    )

def check_one_step_equation_answer(
    equation_text: str,
    operation: str,
    given_solution: int,
) -> tuple[bool, str, int]:
    """
    Check a learner's answer for a one-step equation of the form:
    - x + k = result
    - x - k = result

    Returns (is_correct, explanation, correct_solution).
    """
    # Very simple parser expecting forms like "x + 3 = 7" or "x - 5 = 2"
    try:
        left_side, right_str = equation_text.split("=")
        right_str = right_str.strip()
        right_value = int(right_str)
        left_side = left_side.strip()

        # left_side is like "x + 3" or "x - 5"
        parts = left_side.split()
        # Expecting ["x", "+", "k"] or ["x", "-", "k"]
        if len(parts) != 3 or parts[0] != "x":
            raise ValueError("Unsupported equation format.")

        op_symbol = parts[1]
        k_value = int(parts[2])
    except Exception:
        explanation = (
            "The equation format is not recognized. Expected forms like "
            "'x + 3 = 7' or 'x - 5 = 2'."
        )
        return False, explanation, given_solution

    if operation == EquationOperation.ADD.value:
        # x + k = right_value  =>  x = right_value - k
        correct_solution = right_value - k_value
        op_phrase = f"+ {k_value}"
        undo_phrase = f"subtract {k_value} from both sides"
        undo_example = f"{right_value} - {k_value} = {correct_solution}"
    elif operation == EquationOperation.SUBTRACT.value:
        # x - k = right_value  =>  x = right_value + k
        correct_solution = right_value + k_value
        op_phrase = f"- {k_value}"
        undo_phrase = f"add {k_value} to both sides"
        undo_example = f"{right_value} + {k_value} = {correct_solution}"
    else:
        explanation = "Operation must be 'add' or 'subtract'."
        return False, explanation, given_solution

    is_correct = given_solution == correct_solution

    if is_correct:
        explanation = (
            f"Correct. In the equation {equation_text}, x is combined with {op_phrase}. "
            f"To solve, {undo_phrase}: {undo_example}, so x = {correct_solution}."
        )
    else:
        explanation = (
            f"Not quite. In the equation {equation_text}, x is combined with {op_phrase}. "
            f"To solve, {undo_phrase}: {undo_example}, so the correct value is x = {correct_solution}, "
            f"not {given_solution}."
        )

    return is_correct, explanation, correct_solution

# ============================================================
# Two-step equations: ax + b = c
# ============================================================

class EquationTwoStepPracticeItem(BaseModel):
    id: str
    # We keep a simple linear structure: a * x + b = c
    a: int
    b: int
    c: int
    unknown_symbol: str
    equation_text: str
    solution: int
    explanation: str


class EquationTwoStepPracticeSet(BaseModel):
    description: str
    items: list[EquationTwoStepPracticeItem]

def generate_two_step_equation_practice(count: int = 10) -> EquationTwoStepPracticeSet:
    """
    Generate simple two-step equations of the form:
        a*x + b = c
    where a, b, c are small integers and x is an integer solution.

    We choose small values so that:
        -1 <= x <= 10
        1 <= a <= 5
        -10 <= b <= 10
        and compute c = a*x + b.
    """
    if count < 1:
        count = 1
    if count > 50:
        count = 50

    items: list[EquationTwoStepPracticeItem] = []
    unknown_symbol = "x"
    problem_id = 1

    # Deterministic grid over small integer choices
    for a in range(1, 6):          # 1..5
        for x in range(-1, 11):    # -1..10
            for b in range(-5, 6):  # -5..5
                if len(items) >= count:
                    break

                c = a * x + b
                # Build equation text with explicit + or - for b
                if b >= 0:
                    equation_text = f"{a}{unknown_symbol} + {b} = {c}"
                    b_phrase = f"+ {b}"
                else:
                    equation_text = f"{a}{unknown_symbol} - {abs(b)} = {c}"
                    b_phrase = f"- {abs(b)}"

                # Explanation in early algebra language
                explanation = (
                    f"In the equation {equation_text}, multiply {unknown_symbol} by {a} "
                    f"and then {b_phrase} to get {c}. To solve, first undo {b_phrase} and "
                    f"then undo the multiplication by {a}."
                )

                items.append(
                    EquationTwoStepPracticeItem(
                        id=f"eq_two_step_{problem_id}",
                        a=a,
                        b=b,
                        c=c,
                        unknown_symbol=unknown_symbol,
                        equation_text=equation_text,
                        solution=x,
                        explanation=explanation,
                    )
                )
                problem_id += 1

            if len(items) >= count:
                break
        if len(items) >= count:
            break

    return EquationTwoStepPracticeSet(
        description=(
            "Two-step equation practice for equations of the form a*x + b = c "
            "with small integer coefficients and integer solutions."
        ),
        items=items,
    )

def check_two_step_equation_answer(
    equation_text: str,
    given_solution: int,
) -> tuple[bool, str, int]:
    """
    Check a learner's answer for a two-step equation of the form:
        a*x + b = c
    or
        a*x - d = c   (where d = -b)

    Returns (is_correct, explanation, correct_solution).
    """
    try:
        left_side, right_str = equation_text.split("=")
        right_str = right_str.strip()
        c_value = int(right_str)
        left_side = left_side.strip()

        # left_side is like "2x + 3" or "3x - 5"
        parts = left_side.split()
        # Cases:
        #   ["2x", "+", "3"]
        #   ["3x", "-", "5"]
        if len(parts) != 3:
            raise ValueError("Unsupported equation format.")

        ax_part = parts[0]
        sign = parts[1]
        b_str = parts[2]

        if not ax_part.endswith("x"):
            raise ValueError("Unsupported equation format (missing x).")

        a_str = ax_part[:-1]  # everything before 'x'
        if a_str == "" or a_str == "+":
            a_value = 1
        elif a_str == "-":
            a_value = -1
        else:
            a_value = int(a_str)

        b_value = int(b_str)
        if sign == "-":
            b_value = -b_value

    except Exception:
        explanation = (
            "The equation format is not recognized. Expected forms like "
            "'2x + 3 = 11' or '3x - 5 = 10'."
        )
        return False, explanation, given_solution

    # Equation is a*x + b = c  =>  a*x = c - b  =>  x = (c - b)/a
    numerator = c_value - b_value
    if a_value == 0:
        explanation = "This equation has a = 0, which we do not support in this practice set."
        return False, explanation, given_solution

    # We only support integer solutions in this practice set
    if numerator % a_value != 0:
        correct_solution = numerator / a_value
        explanation = (
            "This equation does not have an integer solution for x in this practice set."
        )
        return False, explanation, int(correct_solution)

    correct_solution = numerator // a_value
    is_correct = given_solution == correct_solution

    if is_correct:
        explanation = (
            f"Correct. To solve {equation_text}, first subtract {b_value} from both sides "
            f"to get {a_value}x = {c_value - b_value}, then divide both sides by {a_value} "
            f"to get x = {correct_solution}."
        )
    else:
        explanation = (
            f"Not quite. To solve {equation_text}, first subtract {b_value} from both sides "
            f"to get {a_value}x = {c_value - b_value}, then divide both sides by {a_value} "
            f"to get x = {correct_solution}, not {given_solution}."
        )

    return is_correct, explanation, correct_solution

# ============================================================
# Equations with variables on both sides: a*x + b = c*x + d
# ============================================================

class EquationBothSidesPracticeItem(BaseModel):
    id: str
    # Equation of the form a*x + b = c*x + d
    a: int
    b: int
    c: int
    d: int
    unknown_symbol: str
    equation_text: str
    solution: int
    explanation: str


class EquationBothSidesPracticeSet(BaseModel):
    description: str
    items: list[EquationBothSidesPracticeItem]

def generate_equation_both_sides_practice(count: int = 10) -> EquationBothSidesPracticeSet:
    """
    Generate simple linear equations with the variable on both sides:
        a*x + b = c*x + d
    where a, b, c, d are small integers and x has an integer solution.

    We choose small values so that:
        -5 <= x <= 5
        1 <= a, c <= 5 and a != c
        -10 <= b, d <= 10
    and we compute d so that x is an integer solution.
    """
    if count < 1:
        count = 1
    if count > 50:
        count = 50

    items: list[EquationBothSidesPracticeItem] = []
    unknown_symbol = "x"
    problem_id = 1

    # Deterministic generation over small integer choices
    for x_val in range(-3, 4):  # -3..3
        for a_val in range(1, 5):  # 1..4
            for c_val in range(1, 5):  # 1..4
                if a_val == c_val:
                    continue  # would give no unique solution
                for b_val in range(-5, 6):  # -5..5
                    if len(items) >= count:
                        break

                    # Choose d so that x_val is a solution:
                    # a*x + b = c*x + d  => d = a*x + b - c*x
                    d_val = a_val * x_val + b_val - c_val * x_val

                    # Build equation text with explicit + or - for b and d
                    if b_val >= 0:
                        left_text = f"{a_val}{unknown_symbol} + {b_val}"
                        b_phrase = f"+ {b_val}"
                    else:
                        left_text = f"{a_val}{unknown_symbol} - {abs(b_val)}"
                        b_phrase = f"- {abs(b_val)}"

                    if d_val >= 0:
                        right_text = f"{c_val}{unknown_symbol} + {d_val}"
                        d_phrase = f"+ {d_val}"
                    else:
                        right_text = f"{c_val}{unknown_symbol} - {abs(d_val)}"
                        d_phrase = f"- {abs(d_val)}"

                    equation_text = f"{left_text} = {right_text}"

                    explanation = (
                        f"In the equation {equation_text}, {unknown_symbol} appears on both sides. "
                        f"To solve, first bring all {unknown_symbol} terms to one side and constants to the other, "
                        f"then divide by the remaining coefficient of {unknown_symbol}."
                    )

                    items.append(
                        EquationBothSidesPracticeItem(
                            id=f"eq_both_sides_{problem_id}",
                            a=a_val,
                            b=b_val,
                            c=c_val,
                            d=d_val,
                            unknown_symbol=unknown_symbol,
                            equation_text=equation_text,
                            solution=x_val,
                            explanation=explanation,
                        )
                    )
                    problem_id += 1

                if len(items) >= count:
                    break
            if len(items) >= count:
                break
        if len(items) >= count:
            break

    return EquationBothSidesPracticeSet(
        description=(
            "Equations with variables on both sides of the form a*x + b = c*x + d, "
            "with small integer coefficients and integer solutions."
        ),
        items=items,
    )

def check_equation_both_sides_answer(
    equation_text: str,
    given_solution: int,
) -> tuple[bool, str, int]:
    """
    Check a learner's answer for an equation with variables on both sides:
        a*x + b = c*x + d

    Returns (is_correct, explanation, correct_solution).
    """
    try:
        left_side, right_side = equation_text.split("=")
        left_side = left_side.strip()
        right_side = right_side.strip()

        # Parse sides like "2x + 3" or "3x - 5"
        def parse_linear_side(side: str) -> tuple[int, int]:
            parts = side.split()
            # Expect ["2x", "+", "3"] or ["2x", "-", "3"]
            if len(parts) != 3:
                raise ValueError("Unsupported equation format.")
            ax_part, sign, const_str = parts
            if not ax_part.endswith("x"):
                raise ValueError("Unsupported equation format (missing x).")
            a_str = ax_part[:-1]
            if a_str == "" or a_str == "+":
                a_val = 1
            elif a_str == "-":
                a_val = -1
            else:
                a_val = int(a_str)

            const_val = int(const_str)
            if sign == "-":
                const_val = -const_val
            return a_val, const_val

        a_val, b_val = parse_linear_side(left_side)
        c_val, d_val = parse_linear_side(right_side)

    except Exception:
        explanation = (
            "The equation format is not recognized. Expected forms like "
            "'2x + 3 = x + 7' or '3x - 5 = x + 1'."
        )
        return False, explanation, given_solution

    # Solve a*x + b = c*x + d  => (a - c)x = d - b  => x = (d - b)/(a - c)
    coef = a_val - c_val
    rhs = d_val - b_val

    if coef == 0:
        explanation = (
            "This equation has the same coefficient of x on both sides, which either "
            "leads to no solution or infinitely many solutions. This practice set assumes "
            "a unique integer solution."
        )
        return False, explanation, given_solution

    if rhs % coef != 0:
        correct_solution_float = rhs / coef
        explanation = (
            "This equation does not have an integer solution for x in this practice set."
        )
        return False, explanation, int(correct_solution_float)

    correct_solution = rhs // coef
    is_correct = given_solution == correct_solution

    if is_correct:
        explanation = (
            f"Correct. To solve {equation_text}, first subtract {c_val}x from both sides to get "
            f"{coef}x + {b_val} = {d_val}, then subtract {b_val} from both sides to get "
            f"{coef}x = {rhs}, and finally divide both sides by {coef} to get x = {correct_solution}."
        )
    else:
        explanation = (
            f"Not quite. To solve {equation_text}, first subtract {c_val}x from both sides to get "
            f"{coef}x + {b_val} = {d_val}, then subtract {b_val} from both sides to get "
            f"{coef}x = {rhs}, and finally divide both sides by {coef} to get x = {correct_solution}, "
            f"not {given_solution}."
        )

    return is_correct, explanation, correct_solution
