from pydantic import BaseModel


class OneStepInequalityPracticeItem(BaseModel):
    id: str
    a: int
    b: int
    unknown_symbol: str
    inequality_symbol: str  # "<", "<=", ">", ">="
    inequality_text: str
    solution_description: str  # e.g. "x < 4"
    explanation: str
    requires_flip: bool  # True if solving requires flipping the inequality sign


class OneStepInequalityPracticeSet(BaseModel):
    items: list[OneStepInequalityPracticeItem]
