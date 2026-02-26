from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from app.prime.curriculum.models import (
    LogicConceptId,
    MethodsConceptId,
    MethodsConceptLesson,
    MetaphysicsConceptId,
    MetaphysicsConceptLesson,
    PhilosophyLesson,
)


# This module defines internal tool schemas and call functions
# that the reasoning core can use to pull from PRIME's philosophy
# foundations lanes (Logic L1, Methods M1, Metaphysics B1).


# ---------- Tool input / output models ----------


class PhilosophyLogicLessonToolInput(BaseModel):
    concept_id: LogicConceptId


class PhilosophyLogicLessonToolOutput(BaseModel):
    lesson: PhilosophyLesson


class PhilosophyMethodsLessonToolInput(BaseModel):
    concept_id: MethodsConceptId


class PhilosophyMethodsLessonToolOutput(BaseModel):
    lesson: MethodsConceptLesson


class PhilosophyMetaphysicsLessonToolInput(BaseModel):
    concept_id: MetaphysicsConceptId


class PhilosophyMetaphysicsLessonToolOutput(BaseModel):
    lesson: MetaphysicsConceptLesson


# ---------- Tool call functions (directly call endpoints) ----------

# We import the internal FastAPI endpoint functions instead of doing HTTP.
# This keeps everything in-process and type-safe.

from app.prime.humanities.philosophy.endpoints import (  # noqa: E402
    philosophy_logic_l1_concept,        # you may need to adjust names to match
    philosophy_methods_m1_concept,
    philosophy_metaphysics_b1_concept,
)


async def call_philosophy_logic_lesson_tool(
    payload: PhilosophyLogicLessonToolInput,
) -> PhilosophyLogicLessonToolOutput:
    """
    Tool wrapper: get a Logic foundation lesson.
    NOTE: The underlying endpoint currently does not accept a 'concept_id' keyword,
    so this wrapper ignores the payload for now and relies on the endpoint's
    internal selection of concept.
    """
    lesson: LogicConceptLesson = await philosophy_logic_l1_concept()
    return PhilosophyLogicLessonToolOutput(lesson=lesson)


async def call_philosophy_methods_lesson_tool(
    payload: PhilosophyMethodsLessonToolInput,
) -> PhilosophyMethodsLessonToolOutput:
    """
    Tool wrapper: get a Methods/Writing foundation lesson for a given concept_id.
    """
    # async def philosophy_methods_m1_concept(concept_id: MethodsConceptId) -> MethodsConceptLesson: ...
    lesson: MethodsConceptLesson = await philosophy_methods_m1_concept(
        concept_id=payload.concept_id
    )
    return PhilosophyMethodsLessonToolOutput(lesson=lesson)


async def call_philosophy_metaphysics_lesson_tool(
    payload: PhilosophyMetaphysicsLessonToolInput,
) -> PhilosophyMetaphysicsLessonToolOutput:
    """
    Tool wrapper: get a Metaphysics foundation lesson for a given concept_id.
    """
    # async def philosophy_metaphysics_b1_concept(concept_id: MetaphysicsConceptId) -> MetaphysicsConceptLesson: ...
    lesson: MetaphysicsConceptLesson = await philosophy_metaphysics_b1_concept(
        concept_id=payload.concept_id
    )
    return PhilosophyMetaphysicsLessonToolOutput(lesson=lesson)


# ---------- Simple registry so the reasoning core can look up tools by name ----------


TOOL_REGISTRY: dict[str, dict[str, Any]] = {
    # Philosophy foundations lanes
    "philosophy_logic_lesson": {
        "input_model": PhilosophyLogicLessonToolInput,
        "output_model": PhilosophyLogicLessonToolOutput,
        "func": call_philosophy_logic_lesson_tool,
        "description": "Retrieve a Logic foundation lesson for a given LogicConceptId.",
    },
    "philosophy_methods_lesson": {
        "input_model": PhilosophyMethodsLessonToolInput,
        "output_model": PhilosophyMethodsLessonToolOutput,
        "func": call_philosophy_methods_lesson_tool,
        "description": "Retrieve a Methods & Writing foundation lesson for a given MethodsConceptId.",
    },
    "philosophy_metaphysics_lesson": {
        "input_model": PhilosophyMetaphysicsLessonToolInput,
        "output_model": PhilosophyMetaphysicsLessonToolOutput,
        "func": call_philosophy_metaphysics_lesson_tool,
        "description": "Retrieve a Metaphysics foundation lesson for a given MetaphysicsConceptId.",
    },
}
