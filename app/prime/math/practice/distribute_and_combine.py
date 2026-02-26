from pydantic import BaseModel
from typing import List
import random


class DistributeAndCombineItem(BaseModel):
    id: str
    expression_text: str
    simplified_text: str
    explanation: str


class DistributeAndCombineSet(BaseModel):
    description: str
    items: List[DistributeAndCombineItem]


def _format_term(coeff: int, var: str = "x") -> str:
    if coeff == 0:
        return ""
    if coeff == 1:
        return f"{var}"
    if coeff == -1:
        return f"-{var}"
    return f"{coeff}{var}"


def _canonical_linear(a: int, b: int, var: str = "x") -> str:
    var_part = _format_term(a, var)
    const_part = ""
    if b != 0:
        sign = "+" if b > 0 else "-"
        const_part = f" {sign} {abs(b)}" if var_part else f"{b}"
    if not var_part and not const_part:
        return "0"
    return f"{var_part}{const_part}".strip()


def generate_distribute_and_combine_practice(count: int = 5) -> DistributeAndCombineSet:
    items: List[DistributeAndCombineItem] = []

    for i in range(count):
        # Pattern: a(bx + c) + dx + e
        a = random.choice([-3, -2, -1, 1, 2, 3])
        b = random.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5])
        c = random.randint(-9, 9)
        d = random.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5])
        e = random.randint(-9, 9)

        outer = f"{a}({_canonical_linear(b, c)})"
        tail = _canonical_linear(d, e)

        expression_text = f"{outer} + {tail}"

        # Distribute and combine
        dist_a = a * b
        dist_c = a * c
        A = dist_a + d
        B = dist_c + e

        simplified_text = _canonical_linear(A, B)

        explanation = (
            f"Distribute {a} across the parentheses: "
            f"{a}·({b}x + {c}) = {dist_a}x + {dist_c}. "
            f"Then combine like terms: ({dist_a}x + {d}x) = {A}x "
            f"and ({dist_c} + {e}) = {B}, giving {simplified_text}."
        )

        items.append(
            DistributeAndCombineItem(
                id=f"dist-{i}",
                expression_text=expression_text,
                simplified_text=simplified_text,
                explanation=explanation,
            )
        )

    return DistributeAndCombineSet(
        description="Apply the distributive property and combine like terms to simplify.",
        items=items,
    )
