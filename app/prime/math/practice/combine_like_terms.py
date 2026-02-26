import random
from typing import List
from pydantic import BaseModel


class CombineLikeTermsItem(BaseModel):
    id: str
    expression_text: str          # e.g. "3x + 4x - 2"
    simplified_text: str          # e.g. "7x - 2"
    variable_symbol: str          # e.g. "x"
    explanation: str


class CombineLikeTermsSet(BaseModel):
    items: List[CombineLikeTermsItem]


def _format_term(coefficient: int, var: str, is_first: bool) -> str:
    if coefficient == 0:
        return ""

    sign = "+" if coefficient > 0 else "-"
    abs_coef = abs(coefficient)

    if abs_coef == 1:
        core = var
    else:
        core = f"{abs_coef}{var}"

    if is_first:
        return f"{core}" if coefficient > 0 else f"-{core}"
    else:
        return f" {sign} {core}"


def _format_constant(constant: int, is_first: bool) -> str:
    if constant == 0:
        return ""

    sign = "+" if constant > 0 else "-"
    abs_val = abs(constant)

    if is_first:
        return f"{abs_val}" if constant > 0 else f"-{abs_val}"
    else:
        return f" {sign} {abs_val}"


def _build_expression(a: int, b: int, c: int, var: str) -> str:
    parts: List[str] = []
    first = True

    for coef in [a, b]:
        term = _format_term(coef, var, is_first=first)
        if term:
            parts.append(term)
            first = False

    const = _format_constant(c, is_first=first)
    if const:
        parts.append(const)

    if not parts:
        return "0"

    return "".join(parts)


def _build_simplified_text(total_coef: int, c: int, var: str) -> str:
    parts: List[str] = []
    first = True

    term = _format_term(total_coef, var, is_first=first)
    if term:
        parts.append(term)
        first = False

    const = _format_constant(c, is_first=first)
    if const:
        parts.append(const)

    if not parts:
        return "0"

    return "".join(parts)


def generate_combine_like_terms_practice(
    count: int = 10,
    min_coef: int = -9,
    max_coef: int = 9,
    min_const: int = -20,
    max_const: int = 20,
    variable_symbol: str = "x",
) -> CombineLikeTermsSet:
    """
    Generate expressions that require combining like terms, e.g. 3x + 4x - 2.
    """
    items: List[CombineLikeTermsItem] = []

    for i in range(count):
        a = 0
        b = 0
        while a == 0:
            a = random.randint(min_coef, max_coef)
        while b == 0:
            b = random.randint(min_coef, max_coef)
        c = random.randint(min_const, max_const)

        expr = _build_expression(a, b, c, variable_symbol)
        total_coef = a + b
        simplified = _build_simplified_text(total_coef, c, variable_symbol)

        explanation_parts = [
            f"Start with {expr}.",
            f"Combine the {variable_symbol}-terms: {a}{variable_symbol} and {b}{variable_symbol} "
            f"to get {total_coef}{variable_symbol}.",
        ]
        if c != 0:
            explanation_parts.append(
                f"The constant term {c} stays the same, so the simplified expression is {simplified}."
            )
        else:
            explanation_parts.append(
                f"There is no constant term, so the simplified expression is {simplified}."
            )

        explanation = " ".join(explanation_parts)

        items.append(
            CombineLikeTermsItem(
                id=f"combine_like_{i + 1}",
                expression_text=expr,
                simplified_text=simplified,
                variable_symbol=variable_symbol,
                explanation=explanation,
            )
        )

    return CombineLikeTermsSet(items=items)
