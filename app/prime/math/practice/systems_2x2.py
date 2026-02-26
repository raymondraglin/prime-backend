from pydantic import BaseModel
from typing import List
import random


class System2x2Item(BaseModel):
    id: str
    equation1: str
    equation2: str
    solution_x: int
    solution_y: int
    method_hint: str
    explanation: str


class System2x2Set(BaseModel):
    description: str
    items: List[System2x2Item]


def _format_equation(a: int, b: int, c: int) -> str:
    """
    Format ax + by = c with nice sign handling.
    """
    parts = []

    # x-term
    if a == 0:
        pass
    elif a == 1:
        parts.append("x")
    elif a == -1:
        parts.append("-x")
    else:
        parts.append(f"{a}x")

    # y-term
    if b != 0:
        sign = "+" if b > 0 else "-"
        abs_b = abs(b)
        if not parts:
            # first term
            if abs_b == 1:
                term = "y"
            else:
                term = f"{abs_b}y"
            if b < 0:
                parts.append(f"-{term}")
            else:
                parts.append(term)
        else:
            if abs_b == 1:
                term = "y"
            else:
                term = f"{abs_b}y"
            parts.append(f" {sign} {term}")

    if not parts:
        # degenerate: 0x + 0y = c
        left = "0"
    else:
        left = "".join(parts)

    return f"{left} = {c}"


def generate_systems_2x2_practice(count: int = 5) -> System2x2Set:
    """
    Generate a set of 2x2 linear systems with integer solutions.
    We build them by choosing a solution (x, y) and random coefficients.
    """
    items: List[System2x2Item] = []

    for i in range(count):
        # Choose a solution (x, y)
        x = random.randint(-5, 5)
        y = random.randint(-5, 5)

        # Choose coefficients for the two equations
        a1 = random.choice([-3, -2, -1, 1, 2, 3])
        b1 = random.choice([-3, -2, -1, 1, 2, 3])
        a2 = random.choice([-3, -2, -1, 1, 2, 3])
        b2 = random.choice([-3, -2, -1, 1, 2, 3])

        # Ensure the system is not degenerate (determinant != 0)
        det = a1 * b2 - a2 * b1
        if det == 0:
            # skip and try again
            continue

        c1 = a1 * x + b1 * y
        c2 = a2 * x + b2 * y

        eq1 = _format_equation(a1, b1, c1)
        eq2 = _format_equation(a2, b2, c2)

        # Simple method hint: if one variable already isolated use substitution, else elimination
        if abs(a1) == 1 and b1 == 0:
            method_hint = "substitution (first equation already gives x)"
        elif abs(b1) == 1 and a1 == 0:
            method_hint = "substitution (first equation already gives y)"
        elif a1 == -a2 or b1 == -b2:
            method_hint = "elimination (add equations to cancel a variable)"
        else:
            method_hint = "elimination (scale and add/subtract to cancel a variable)"

        explanation = (
            f"This system was built so that x = {x} and y = {y} make both equations true. "
            f"If you plug (x, y) = ({x}, {y}) into each equation, both sides match."
        )

        items.append(
            System2x2Item(
                id=f"sys2x2-{i}",
                equation1=eq1,
                equation2=eq2,
                solution_x=x,
                solution_y=y,
                method_hint=method_hint,
                explanation=explanation,
            )
        )

    description = (
        "Systems of two linear equations in two variables. "
        "Solve for (x, y) that makes both equations true."
    )

    return System2x2Set(description=description, items=items)
