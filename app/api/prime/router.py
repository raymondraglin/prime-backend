from fastapi import APIRouter, Query
from pydantic import BaseModel
import random

router = APIRouter()

class Problem(BaseModel):
    id: str
    topic: str
    difficulty: int
    question: str
    answer: float
    hint: str

class AnswerSubmit(BaseModel):
    problem_id: str
    student_id: str
    answer: float

class AnswerResult(BaseModel):
    correct: bool
    correct_answer: float
    xp_earned: int
    feedback: str
    new_difficulty: int

PROBLEMS = {
    "algebra": [
        {"question": "Solve for x: 2x + 4 = 12", "answer": 4.0, "hint": "Subtract 4 from both sides first.", "difficulty": 1},
        {"question": "Solve for x: 3x - 7 = 14", "answer": 7.0, "hint": "Add 7 to both sides first.", "difficulty": 2},
        {"question": "Solve for x: x² - 9 = 0", "answer": 3.0, "hint": "Factor as (x+3)(x-3) = 0.", "difficulty": 3},
        {"question": "Solve for x: 5x + 2 = 3x + 10", "answer": 4.0, "hint": "Collect x terms on one side.", "difficulty": 2},
    ],
    "geometry": [
        {"question": "Area of a circle with radius 5?", "answer": 78.54, "hint": "Use A = πr²", "difficulty": 1},
        {"question": "Hypotenuse of a right triangle with legs 3 and 4?", "answer": 5.0, "hint": "Use a²+b²=c²", "difficulty": 2},
        {"question": "Perimeter of a rectangle: length=8, width=5?", "answer": 26.0, "hint": "P = 2(l + w)", "difficulty": 1},
    ],
    "statistics": [
        {"question": "Mean of [4, 8, 6, 5, 3, 2, 8, 9, 2, 5]?", "answer": 5.2, "hint": "Sum all values then divide by count.", "difficulty": 2},
        {"question": "Median of [3, 5, 7, 9, 11]?", "answer": 7.0, "hint": "The middle value of a sorted list.", "difficulty": 1},
    ],
}

student_state: dict = {}

@router.get("/hud/problem", response_model=Problem)
def get_problem(
    topic: str = Query(default="algebra"),
    difficulty: int = Query(default=1),
    student_id: str = Query(default="guest"),
):
    bank = PROBLEMS.get(topic, PROBLEMS["algebra"])
    filtered = [p for p in bank if p["difficulty"] == difficulty] or bank
    p = random.choice(filtered)
    pid = f"{topic}_{difficulty}_{random.randint(1000,9999)}"
    return Problem(id=pid, topic=topic, difficulty=difficulty,
                   question=p["question"], answer=p["answer"], hint=p["hint"])

@router.post("/hud/answer", response_model=AnswerResult)
def submit_answer(payload: AnswerSubmit):
    state = student_state.get(payload.student_id, {"difficulty": 1, "streak": 0})
    all_problems = [p for bank in PROBLEMS.values() for p in bank]
    correct_answer = next(
        (p["answer"] for p in all_problems if abs(p["answer"] - payload.answer) < 0.5),
        0.0
    )
    is_correct = abs(payload.answer - correct_answer) < 0.1
    xp = 0
    new_difficulty = state["difficulty"]

    if is_correct:
        state["streak"] = state.get("streak", 0) + 1
        xp = 10 * state["difficulty"]
        if state["streak"] >= 3:
            new_difficulty = min(state["difficulty"] + 1, 5)
            state["streak"] = 0
        feedback = f"Correct! +{xp} XP"
    else:
        state["streak"] = 0
        new_difficulty = max(state["difficulty"] - 1, 1)
        feedback = f"Not quite. The answer was {correct_answer}."

    state["difficulty"] = new_difficulty
    student_state[payload.student_id] = state
    return AnswerResult(correct=is_correct, correct_answer=correct_answer,
                        xp_earned=xp, feedback=feedback, new_difficulty=new_difficulty)

@router.get("/topics")
def get_topics():
    return {"topics": list(PROBLEMS.keys())}
