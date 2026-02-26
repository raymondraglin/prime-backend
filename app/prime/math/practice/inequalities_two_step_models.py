from pydantic import BaseModel


class TwoStepInequalityPracticeItem(BaseModel):
    id: str
    a: int           # coefficient of x (non-zero, can be negative)
    b: int           # constant added/subtracted on the left side
    c: int           # right-hand side value
    unknown_symbol: str
    inequality_symbol: str   # "<", "<=", ">", ">="
    inequality_text: str     # e.g. "3x + 2 < 11"
    solution_description: str  # e.g. "x < 3"
    explanation: str
    requires_flip: bool      # True when a < 0


class TwoStepInequalityPracticeSet(BaseModel):
    items: list[TwoStepInequalityPracticeItem]
