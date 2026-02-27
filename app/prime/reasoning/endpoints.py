from fastapi import APIRouter, Query

from datetime import datetime
from typing import List, Dict, Any, Iterable
from app.prime.reasoning.prime_personality import PRIME_BRAIN_CONFIG
from app.prime.reasoning.prime_personality import PRIME_BRAIN_CONFIG
from app.prime.reasoning.personality_policy import (
    is_high_stakes_task,
    enrich_core_response_with_personality,
)

from app.prime.curriculum.models import (
    ReasoningTask,
    ReasoningTaskKind,
    ReasoningStep,
    ReasoningStepKind,
    ReasoningTrace,
    ReasoningCoreRequest,
    ReasoningCoreResponse,
    ReasoningToolCall,
    EthicsFourLensDilemmaRequest,
    EthicsFourLensResponse,
    ReasoningTraceTag,
    ReasoningOutcomeQuality,
    ReasoningMemoryEntry,
    ReasoningMemorySaveRequest,
    ReasoningMemorySaveResponse,
    ReasoningMemoryQuery,
    ReasoningMemoryQueryResponse,
    EthicsMetaPerspectivesResponse,
    MetaPhilosophyAssessment,
    LogicConceptId,
    MethodsConceptId,
    MetaphysicsConceptId,
)

from app.prime.math.endpoints import (
    math_reason,
    MathReasoningProblem,
    MathReasoningResponse,
)

from app.prime.reasoning.tools import TOOL_REGISTRY
from app.prime.reasoning.tools import (
    PhilosophyLogicLessonToolInput,
    PhilosophyLogicLessonToolOutput,
    PhilosophyMethodsLessonToolInput,
    PhilosophyMethodsLessonToolOutput,
    PhilosophyMetaphysicsLessonToolInput,
    PhilosophyMetaphysicsLessonToolOutput,
)

from app.prime.reasoning.memory import query_recent_practice_for_user

from app.prime.reasoning.memory_store import (
    append_memory_entry,
    load_memory_entries,
    iter_memory_entries,
    search_corpus,
    search_corpus_for_task,
    list_any_corpus_docs,
)

router = APIRouter(prefix="/reasoning", tags=["reasoning-core"])


def find_similar_memory_entries(
    domain: str | None,
    subdomain: str | None,
    theme_hint: str | None,
    limit: int = 5,
) -> list[ReasoningMemoryEntry]:
    """
    Internal helper: find similar reasoning episodes based on tags and theme hint.
    Mirrors the logic of reasoning_memory_query, but used directly by the core.
    """
    matches: list[ReasoningMemoryEntry] = []

    for entry in iter_memory_entries() or []:
        if domain and entry.tags.domain != domain:
            continue
        if subdomain and entry.tags.subdomain != subdomain:
            continue

        if theme_hint:
            theme_text = entry.tags.theme or ""
            task_text = entry.task.natural_language_task or ""
            haystack = (theme_text + " " + task_text).lower()
            if theme_hint.lower() not in haystack:
                continue

        matches.append(entry)
        if len(matches) >= limit:
            break

    return matches

def pick_methods_concept_for_task(task: ReasoningTask) -> MethodsConceptId:
    """
    Heuristic: pick a methods/writing foundation concept based on the task text.
    """
    text = (task.natural_language_task or "").lower()

    # Argument reconstruction, reading arguments, writing philosophy.
    if any(word in text for word in ["reconstruct", "reconstruction", "argument map", "argument mapping"]):
        return MethodsConceptId.ARGUMENT_RECONSTRUCTION

    if any(word in text for word in ["read", "reading", "paper", "article", "essay", "text"]):
        return MethodsConceptId.READING_PHILOSOPHY

    if any(word in text for word in ["write", "writing", "draft", "outline"]):
        return MethodsConceptId.WRITING_PHILOSOPHY

    # Default: reading philosophy as a gentle on-ramp.
    return MethodsConceptId.READING_PHILOSOPHY


def pick_logic_concept_for_task_adaptive(task, user_id: str) -> LogicConceptId:
    recent = query_recent_practice_for_user(
        user_id=user_id,
        domain="philosophy",
        subdomain="logic",
        theme_contains="concept_id=",
        limit=20,
    )

    for entry in recent:
        theme = (entry.tags.theme or "").strip()
        if "concept_id=" in theme:
            raw = theme.split("concept_id=", 1)[1].strip()
            raw = raw.split(",")[0].strip()
            try:
                return LogicConceptId(raw)
            except ValueError:
                continue

    text = (task.natural_language_task or "").lower()
    # Example heuristic; plug in your real one:
    if "argument" in text or "premise" in text or "conclusion" in text:
        return LogicConceptId.ARGUMENT_STRUCTURE
    if "fallacy" in text or "bias" in text:
        return LogicConceptId.FALLACIES
    # default fallback
    return LogicConceptId.ARGUMENT_STRUCTURE


def pick_methods_concept_for_task_adaptive(task, user_id: str) -> MethodsConceptId:
    recent = query_recent_practice_for_user(
        user_id=user_id,
        domain="philosophy",
        subdomain="methods",
        theme_contains="concept_id=",
        limit=20,
    )

    for entry in recent:
        theme = (entry.tags.theme or "").strip()
        if "concept_id=" in theme:
            raw = theme.split("concept_id=", 1)[1].strip()
            raw = raw.split(",")[0].strip()
            try:
                return MethodsConceptId(raw)
            except ValueError:
                continue

    text = (task.natural_language_task or "").lower()
    # Example heuristic
    if "reading" in text or "interpret" in text:
        return MethodsConceptId.READING_PHILOSOPHY
    if "experiment" in text or "empirical" in text:
        return MethodsConceptId.EXPERIMENTAL_METHODS
    return MethodsConceptId.READING_PHILOSOPHY

def pick_metaphysics_concept_for_task_adaptive(
    task: ReasoningTask,
    user_id: str | None = None,
) -> MetaphysicsConceptId:
    """
    Adaptive picker: if recent practice shows repeated work on a particular
    metaphysics concept, prioritize that concept; otherwise fall back to heuristics.
    """
    # Try to find recent metaphysics practice for this user.
    recent_entries = query_recent_practice_for_user(
        user_id=user_id,
        domain="philosophy",
        subdomain="metaphysics",
        theme_contains="concept_id=",
        limit=20,
    )

    # Very simple heuristic: if any practice exists, use the most recent concept_id.
    for entry in recent_entries:
        theme = entry.tags.theme or ""
        if theme.startswith("concept_id="):
            concept_id_value = theme.split("=", 1)[1]
            try:
                return MetaphysicsConceptId(concept_id_value)
            except ValueError:
                continue

    # Fallback to text-based heuristic.
    text = (task.natural_language_task or "").lower()

    if any(w in text for w in ["free will", "determinism", "deterministic"]):
        return MetaphysicsConceptId.FREE_WILL_AND_DETERMINISM

    if any(w in text for w in ["identity", "same person", "over time", "persistence"]):
        return MetaphysicsConceptId.IDENTITY_PERSISTENCE

    if any(w in text for w in ["time", "future", "past", "present", "possible worlds", "modal"]):
        return MetaphysicsConceptId.TIME_SPACE

    if any(w in text for w in ["exist", "existence", "real", "reality", "ontology"]):
        return MetaphysicsConceptId.BEING_EXISTENCE

    return MetaphysicsConceptId.BEING_EXISTENCE


def pick_logic_concept_for_task(task: ReasoningTask) -> LogicConceptId:
    """
    Heuristic: pick a logic foundation concept based on the task text and tags.

    This can be upgraded later to use practice logs and richer tagging.
    """
    text = (task.natural_language_task or "").lower()

    # Argument structure, reasons, support → argument structure.
    if any(word in text for word in ["argument", "premise", "premises", "conclusion", "reasons", "support"]):
        return LogicConceptId.ARGUMENT_STRUCTURE

    # Fallacies, bias, invalid → fallacy lane, if you have it.
    if any(word in text for word in ["fallacy", "fallacies", "bias", "invalid", "logical error"]):
        return LogicConceptId.FALLACIES

    # If the task explicitly mentions logic, default to argument structure.
    if "logic" in text:
        return LogicConceptId.ARGUMENT_STRUCTURE

    # Default: PRIME’s first logic spine concept.
    return LogicConceptId.ARGUMENT_STRUCTURE

@router.post(
    "/core",
    response_model=ReasoningCoreResponse,
)
async def reasoning_core(
    request: ReasoningCoreRequest,
) -> ReasoningCoreResponse:
    """
    Domain-agnostic reasoning core.

    Multi-step reasoning loop that can:
    - Interpret the task and list givens/assumptions/constraints.
    - Optionally consult reasoning memory for similar episodes.
    - Call internal tools (math_reasoner, philosophy foundations lanes, ethics lanes).
    - Self-critique and summarize key conclusions and open questions.
    """
    task: ReasoningTask = request.task
    max_steps = max(3, min(request.max_steps, 24))

    steps: list[ReasoningStep] = []
    notes: list[str] = []
    contradictions: list[str] = []

    # -------------------------------------------------
    # Step 0: Interpret the task
    # -------------------------------------------------
    interpret_description = (
        "Interpret the task, restate it in my own words, and identify the main goal."
    )
    interpret_output = [
        f"Task restatement: {task.natural_language_task}",
        f"Desired output kind: {task.desired_output_kind}",
    ]
    if task.domain_tag:
        interpret_output.append(f"Domain hint: {task.domain_tag}")
    if task.subdomain_tag:
        interpret_output.append(f"Subdomain hint: {task.subdomain_tag}")

    # Optional: special message for analysis tasks
    if task.desired_output_kind == ReasoningTaskKind.ANALYSIS:
        interpret_output.append(
            "Output focus: careful analysis and comparison of options or arguments."
        )

    steps.append(
        ReasoningStep(
            index=0,
            kind=ReasoningStepKind.INTERPRET,
            description=interpret_description,
            inputs=[],
            outputs=interpret_output,
            warnings=[],
            confidence=0.8,
        )
    )

    # -------------------------------------------------
    # Step 0.5: Consult reasoning memory for similar episodes
    # -------------------------------------------------
    similar_memory_summaries: list[str] = []
    prior_conclusion_notes: list[str] = []
    theme_hint = None

    # Simple heuristic for theme hint in philosophy/ethics
    if task.domain_tag == "philosophy" and task.subdomain_tag == "ethics":
        text_lower = task.natural_language_task.lower()
        if "career" in text_lower:
            theme_hint = "career"
        elif "loyalty" in text_lower:
            theme_hint = "loyalty"

    similar_entries: list[ReasoningMemoryEntry] = []
    if task.domain_tag and theme_hint:
        similar_entries = find_similar_memory_entries(
            domain=task.domain_tag,
            subdomain=task.subdomain_tag,
            theme_hint=theme_hint,
            limit=3,
        )

    if similar_entries:
        for entry in similar_entries:
            summary = (
                f"Past episode {entry.id}: task_id={entry.task.task_id}, "
                f"theme={entry.tags.theme}, "
                f"user_label={entry.tags.user_label}, "
                f"outcome_quality={entry.outcome_quality}"
            )
            similar_memory_summaries.append(summary)

            # Pull in past key conclusions as notes for this run.
            if entry.response.key_conclusions:
                prior_conclusion_notes.append(
                    f"Past conclusions from {entry.id}: {entry.response.key_conclusions}"
                )

        # Step: note existence of similar episodes
        steps.append(
            ReasoningStep(
                index=1,
                kind=ReasoningStepKind.DECOMPOSE,
                description=(
                    "Consult reasoning memory for similar past dilemmas and note their existence."
                ),
                inputs=[task.natural_language_task],
                outputs=similar_memory_summaries,
                warnings=[],
                confidence=0.75,
            )
        )

        # Step: explicitly surface prior conclusions as reference points
        steps.append(
            ReasoningStep(
                index=2,
                kind=ReasoningStepKind.DEDUCE,
                description=(
                    "Recall key conclusions from similar past episodes as reference points, "
                    "not as final answers."
                ),
                inputs=[s.description for s in steps if s.index <= 1],
                outputs=prior_conclusion_notes,
                warnings=[],
                confidence=0.75,
            )
        )

        next_index = 3
        notes.append(
            "Similar past episodes found in reasoning memory for this domain/theme. "
            "Past key conclusions have been recalled for comparison."
        )
    else:
        next_index = 1


    # -------------------------------------------------
    # Step 0.75: Consult PRIME's corpus (domain-aware)
    # -------------------------------------------------
    corpus_notes: list[str] = []
    corpus_results = search_corpus_for_task(task, top_k=5)

    if corpus_results:
        for i, item in enumerate(corpus_results, start=1):
            meta = item.get("metadata", {}) or {}
            src = meta.get("source_path", "unknown source")
            dom = meta.get("domain", task.domain_tag or "unknown_domain")
            sub = meta.get("subdomain", task.subdomain_tag or "unknown_subdomain")

            preview = (item.get("text") or "").strip().replace("\n", " ")
            if len(preview) > 280:
                preview = preview[:277] + "..."

            corpus_notes.append(
                f"[{i}] Domain={dom}, Subdomain={sub}, Source={src} :: {preview}"
            )

        steps.append(
            ReasoningStep(
                index=next_index,
                kind=ReasoningStepKind.TOOL_CALL,
                description=(
                    "Consult PRIME's internal corpus for background in this domain "
                    "and subdomain before proceeding."
                ),
                inputs=[task.natural_language_task],
                outputs=corpus_notes,
                warnings=[],
                confidence=0.82,
            )
        )

        next_index += 1

        notes.append(
            "PRIME consulted its internal corpus (curriculum, philosophy, and prior lessons) "
            "for background relevant to this task."
        )

    # -------------------------------------------------
    # Step 1: List givens, assumptions, constraints
    # -------------------------------------------------
    describe_inputs = [
        f"Given facts: {task.given_facts or []}",
        f"Assumptions: {task.assumptions or []}",
        f"Constraints: {task.constraints or []}",
    ]
    steps.append(
        ReasoningStep(
            index=next_index,
            kind=ReasoningStepKind.DEDUCE,
            description="Summarize givens, assumptions, and constraints.",
            inputs=[interpret_output[0]],
            outputs=describe_inputs,
            warnings=[],
            confidence=0.85,
        )
    )
    next_index += 1

    # -------------------------------------------------
    # Step 2: Optional tool calls into PRIME's corpus
    # -------------------------------------------------
    tool_conclusion_notes: list[str] = []
    meta_consensus_points: list[str] = []
    meta_disagreement_points: list[str] = []
    meta_pressure_points: list[str] = []
    meta_perspectives: EthicsMetaPerspectivesResponse | None = None

    # 2a. Math reasoning path
    if (
        task.domain_tag == "math"
        and "math_reasoner" in task.allowed_tools
        and next_index < max_steps
    ):
        math_problem = MathReasoningProblem(
            problem_id=task.task_id,
            natural_language_problem=task.natural_language_task,
            hints=task.given_facts,
        )
        math_resp: MathReasoningResponse = await math_reason(math_problem)

        tool_call_math = ReasoningToolCall(
            name="math_reasoner",
            input_payload={
                "problem_id": math_problem.problem_id,
                "natural_language_problem": math_problem.natural_language_problem,
                "hints": math_problem.hints,
            },
        )

        outputs_for_step_math = [
            f"Math reasoning summary: {math_resp.solution_summary}",
            f"Final answer (if available): {math_resp.final_answer}",
        ]

        steps.append(
            ReasoningStep(
                index=next_index,
                kind=ReasoningStepKind.TOOL_CALL,
                description=(
                    "Call math reasoning endpoint to obtain a structured explanation and tentative answer."
                ),
                inputs=[task.natural_language_task],
                outputs=outputs_for_step_math,
                tool_call=tool_call_math,
                tool_result_summary=math_resp.solution_summary,
                warnings=math_resp.warnings,
                confidence=0.8,
            )
        )
        next_index += 1

        tool_conclusion_notes.append(
            f"Math reasoning path: {math_resp.solution_summary}"
        )
        if math_resp.final_answer != "solver_not_yet_implemented":
            tool_conclusion_notes.append(
                f"Math final answer: {math_resp.final_answer}"
            )
        else:
            tool_conclusion_notes.append(
                "Math final answer is not yet computed; use the outlined reasoning steps as guidance."
            )

    # 2b. Philosophy logic foundations (L1)
    if (
        task.domain_tag == "philosophy"
        and "philosophy_logic_lesson" in task.allowed_tools
        and next_index < max_steps
    ):
        tool_def = TOOL_REGISTRY.get("philosophy_logic_lesson")
        if tool_def is not None:
            LogicInputModel = tool_def["input_model"]
            logic_func = tool_def["func"]

            # TODO: thread real user id once available; using "raymond" as placeholder.
            chosen_logic_concept: LogicConceptId = pick_logic_concept_for_task_adaptive(
                task=task,
                user_id="raymond",
            )

            logic_input = LogicInputModel(concept_id=chosen_logic_concept)
            logic_output: PhilosophyLogicLessonToolOutput = await logic_func(logic_input)
            logic_lesson = logic_output.lesson

            tool_call_logic = ReasoningToolCall(
                name="philosophy_logic_lesson",
                input_payload={
                    "concept_id": chosen_logic_concept,
                },
            )

            # Safe string summary; do not assume professor_view exists on the model.
            try:
                professor_summary = getattr(logic_lesson, "professor_view", None)
                if professor_summary is None:
                    professor_summary = str(logic_lesson)
                else:
                    professor_summary = str(professor_summary)
            except Exception:
                professor_summary = str(logic_lesson)

            outputs_for_step_logic = [
                f"Logic foundation lesson id: {getattr(logic_lesson, 'id', 'unknown')}",
                f"Professor view: {professor_summary}",
            ]

            tool_result_summary_logic = (
                "Retrieved PRIME's logic foundation lesson to ground this reasoning in "
                "explicit argument structure / core logic principles."
            )

            steps.append(
                ReasoningStep(
                    index=next_index,
                    kind=ReasoningStepKind.TOOL_CALL,
                    description=(
                        "Call PRIME's logic foundations lane to anchor reasoning in the "
                        "most relevant logic concept for this task."
                    ),
                    inputs=[task.natural_language_task],
                    outputs=outputs_for_step_logic,
                    tool_call=tool_call_logic,
                    tool_result_summary=tool_result_summary_logic,
                    warnings=[],
                    confidence=0.87,
                )
            )
            next_index += 1

            tool_conclusion_notes.append(
                f"Logic foundation applied: {logic_lesson.id}."
            )

    # 2c. Philosophy methods & writing foundations (M1)
    if (
        task.domain_tag == "philosophy"
        and "philosophy_methods_lesson" in task.allowed_tools
        and next_index < max_steps
    ):
        tool_def = TOOL_REGISTRY.get("philosophy_methods_lesson")
        if tool_def is not None:
            MethodsInputModel = tool_def["input_model"]
            methods_func = tool_def["func"]

            # TODO: thread real user id once available; using "raymond" as placeholder.
            chosen_methods_concept: MethodsConceptId = pick_methods_concept_for_task_adaptive(
                task=task,
                user_id="raymond",
            )

            methods_input = MethodsInputModel(concept_id=chosen_methods_concept)
            methods_output: PhilosophyMethodsLessonToolOutput = await methods_func(
                methods_input
            )
            methods_lesson = methods_output.lesson

            tool_call_methods = ReasoningToolCall(
                name="philosophy_methods_lesson",
                input_payload={
                    "concept_id": chosen_methods_concept,
                },
            )

            professor_summary = ""
            if methods_lesson.professor_view is not None:
                professor_summary = str(methods_lesson.professor_view)

            outputs_for_step_methods = [
                f"Methods foundation lesson id: {methods_lesson.id}",
                f"Professor view: {professor_summary}",
            ]

            tool_result_summary_methods = (
                "Retrieved PRIME's methods & writing foundation lesson to guide how this "
                "task is read, reconstructed, or written."
            )

            steps.append(
                ReasoningStep(
                    index=next_index,
                    kind=ReasoningStepKind.TOOL_CALL,
                    description=(
                        "Call PRIME's methods & writing foundations lane to shape how to read, "
                        "reconstruct, or write about this task."
                    ),
                    inputs=[task.natural_language_task],
                    outputs=outputs_for_step_methods,
                    tool_call=tool_call_methods,
                    tool_result_summary=tool_result_summary_methods,
                    warnings=[],
                    confidence=0.86,
                )
            )
            next_index += 1

            tool_conclusion_notes.append(
                f"Methods foundation applied: {methods_lesson.id}."
            )

    # 2d. Philosophy / ethics tools (four-lens and meta-perspectives)
    # For now, the full L3 four-lens orchestration is handled inside HS endpoints
    # via _run_ethics_four_lens in endpoints_hs.py.
    # The reasoning core will not call four-lens directly until we have a stable,
    # shared orchestration function to import without circular dependencies.
    # We keep meta_* variables initialized so the summary logic works.
    if (
        task.domain_tag == "philosophy"
        and "philosophy_four_lens" in task.allowed_tools
        and next_index < max_steps
    ):
        steps.append(
            ReasoningStep(
                index=next_index,
                kind=ReasoningStepKind.TOOL_CALL,
                description=(
                    "Ethics four-lens analysis is available in HS philosophy lanes; "
                    "core currently defers to lane-specific orchestration."
                ),
                inputs=[task.natural_language_task],
                outputs=[
                    "Four-lens ethics tools are registered but orchestrated at the HS lane level."
                ],
                warnings=[],
                confidence=0.75,
            )
        )
        next_index += 1


        # Extract high-level notes from each lens for later summary.
        tool_conclusion_notes.append(
            "Consequentialism: focuses on overall outcomes and trade-offs."
        )
        tool_conclusion_notes.append(
            "Deontology: emphasizes duties, rights, and red lines."
        )
        tool_conclusion_notes.append(
            "Virtue ethics: focuses on character and the kind of person you become."
        )
        tool_conclusion_notes.append(
            "Care ethics: focuses on relationships, vulnerability, and care."
        )

        # 2e. Philosophy metaphysics foundations (B1)
        if (
            "philosophy_metaphysics_lesson" in task.allowed_tools
            and next_index < max_steps
        ):
            tool_def = TOOL_REGISTRY.get("philosophy_metaphysics_lesson")
            if tool_def is not None:
                MetaphysicsInputModel = tool_def["input_model"]
                metaphysics_func = tool_def["func"]
                
                # TODO: thread real user id once available; using "raymond" as placeholder.
                chosen_metaphysics_concept: MetaphysicsConceptId = pick_metaphysics_concept_for_task_adaptive(
                    task=task,
                    user_id="raymond",
                )

                metaphysics_input = MetaphysicsInputModel(
                    concept_id=chosen_metaphysics_concept
                )
                metaphysics_output: PhilosophyMetaphysicsLessonToolOutput = (
                    await metaphysics_func(metaphysics_input)
                )
                metaphysics_lesson = metaphysics_output.lesson

                tool_call_metaphysics = ReasoningToolCall(
                    name="philosophy_metaphysics_lesson",
                    input_payload={
                        "concept_id": chosen_metaphysics_concept,
                    },
                )

                professor_summary = ""
                if metaphysics_lesson.professor_view is not None:
                    professor_summary = str(metaphysics_lesson.professor_view)

                outputs_for_step_metaphysics = [
                    f"Metaphysics foundation lesson id: {metaphysics_lesson.id}",
                    f"Professor view: {professor_summary}",
                ]

                tool_result_summary_metaphysics = (
                    "Retrieved PRIME's metaphysics foundation lesson to clarify the underlying questions "
                    "about reality, identity, time, or causation in this task."
                )

                steps.append(
                    ReasoningStep(
                        index=next_index,
                        kind=ReasoningStepKind.TOOL_CALL,
                        description=(
                            "Call PRIME's metaphysics foundations lane to clarify the deep questions "
                            "about being, identity, causation, time, or possibility behind this task."
                        ),
                        inputs=[task.natural_language_task],
                        outputs=outputs_for_step_metaphysics,
                        tool_call=tool_call_metaphysics,
                        tool_result_summary=tool_result_summary_metaphysics,
                        warnings=[],
                        confidence=0.86,
                    )
                )
                next_index += 1

                tool_conclusion_notes.append(
                    f"Metaphysics foundation applied: {metaphysics_lesson.id}."
                )

        # TOOL CALL 2: legalistic vs relational meta-perspectives
        if "ethics_meta_perspectives" in task.allowed_tools and next_index < max_steps:
            tool_call_meta = ReasoningToolCall(
                name="ethics_meta_perspectives",
                input_payload={"dilemma_text": task.natural_language_task},
            )

            outputs_for_step_meta = [
                "Meta-perspectives (legalistic vs relational) are currently computed "
                "inside HS philosophy endpoints. The core notes their availability "
                "but defers detailed construction to lane-specific orchestration."
            ]

            tool_result_summary_meta = (
                "Meta-perspectives over ethics lenses are available at the HS lane level. "
                "The core will focus on overall reasoning trace and deference signals."
            )

            steps.append(
                ReasoningStep(
                    index=next_index,
                    kind=ReasoningStepKind.TOOL_CALL,
                    description=(
                        "Acknowledge legalistic and relational meta-perspectives over the ethics analysis, "
                        "while deferring detailed construction to HS lanes."
                    ),
                    inputs=[task.natural_language_task],
                    outputs=outputs_for_step_meta,
                    tool_call=tool_call_meta,
                    tool_result_summary=tool_result_summary_meta,
                    warnings=[],
                    confidence=0.8,
                )
            )
            next_index += 1

    # -------------------------------------------------
    # Optional meta-philosophy limits step
    # -------------------------------------------------
    meta_assessment: MetaPhilosophyAssessment | None = None
    # Meta-philosophy assessment for ethics (moral underdetermination, escalation)
    # is currently implemented inside HS philosophy endpoints. The core will treat
    # high-stakes tasks as cautious by default using is_high_stakes_task(task),
    # and lane-specific meta assessment can be folded in at the lane level.


    # -------------------------------------------------
    # Step 3: Self-critique
    # -------------------------------------------------
    critique_outputs = [
        "Check for missing perspectives or obvious gaps.",
        "Ask whether any important stakeholder, value, or uncertainty has been ignored.",
    ]
    steps.append(
        ReasoningStep(
            index=next_index,
            kind=ReasoningStepKind.CRITIQUE,
            description="High-level self-critique: look for gaps and missing angles.",
            inputs=[s.description for s in steps],
            outputs=critique_outputs,
            warnings=[],
            confidence=0.7,
        )
    )
    next_index += 1

    # -------------------------------------------------
    # Step 4: Summarize key conclusions and open questions
    # -------------------------------------------------
    key_conclusions: list[str] = []
    open_questions: list[str] = []

    if tool_conclusion_notes:
        key_conclusions.extend(tool_conclusion_notes)

    if meta_consensus_points:
        key_conclusions.extend(meta_consensus_points)

    if meta_disagreement_points or meta_pressure_points:
        contradictions.extend(meta_disagreement_points)
        notes.extend(meta_pressure_points)
        key_conclusions.append(
            "There are important tensions between frameworks (e.g., outcomes vs duties, "
            "impartial good vs special relationships, external actions vs inner character)."
        )

    if meta_assessment is not None and meta_assessment.should_escalate_to_human:
        key_conclusions.append(
            "This dilemma is morally underdetermined across serious frameworks. "
            "PRIME can map options and trade-offs, but final judgment should remain with you."
        )

    if meta_perspectives is not None:
        key_conclusions.append(
            "From a relational perspective, central concerns include: "
            + "; ".join(meta_perspectives.relational.key_concerns)
        )
        notes.append(
            "Legalistic vs relational perspectives help contrast rule- and rights-focused reasoning "
            "with relationship- and care-focused reasoning."
        )
        key_conclusions.append(
            "From a legalistic perspective, central concerns include: "
            + "; ".join(meta_perspectives.legalistic.key_concerns)
        )

    loop_cfg = PRIME_BRAIN_CONFIG.conversational_loop

    # Clarify
    open_questions.append(
        f"[Clarify] {loop_cfg.clarify} "
        "Did I capture your real question and what is at stake for you here, "
        "or is something important missing?"
    )

    # Inquire
    open_questions.append(
        f"[Inquire] {loop_cfg.inquire} "
        "Among outcomes, duties, character, and relationships, which do you want "
        "to carry the most weight for this task?"
    )

    # Map
    notes.append(
        f"[Map] {loop_cfg.map} "
        "If you think a relevant framework, precedent, or example is missing, "
        "please name it so PRIME can fold it in."
    )

    # Reflect
    open_questions.append(
        f"[Reflect] {loop_cfg.reflect} "
        "What trade-offs or risks in the current picture worry you most, and does "
        "any group or value feel under‑represented?"
    )

    # Advise (Lightly)
    open_questions.append(
        f"[Advise] {loop_cfg.advise_lightly} "
        "Based on the options and tensions so far, which possible path do you want "
        "PRIME to explore or stress‑test next?"
    )

    # Check & Adjust
    open_questions.append(
        f"[Check] {loop_cfg.check_and_adjust} "
        "If the framing or language here feels off for you, how would you restate "
        "the core question in your own words?"
    )

    # Generic wrap-up
    key_conclusions.append(
        "Different frameworks may agree on some actions and disagree on others. "
        "A complete view should track where they converge and where they pull apart."
    )

    summarize_outputs = [
        f"Key conclusions (high-level): {key_conclusions}",
        f"Open questions to resolve (loop-shaped): {open_questions}",
    ]

    steps.append(
        ReasoningStep(
            index=next_index,
            kind=ReasoningStepKind.SUMMARIZE,
            description="Summarize high-level conclusions and remaining questions.",
            inputs=[s.description for s in steps],
            outputs=summarize_outputs,
            warnings=[],
            confidence=0.8,
        )
    )

    trace = ReasoningTrace(
        steps=steps,
        overall_confidence=0.8,
        detected_contradictions=contradictions,
        notes=notes,
    )

    core_response = ReasoningCoreResponse(
        task_id=task.task_id,
        trace=trace,
        key_conclusions=key_conclusions,
        open_questions=open_questions,
    )

    # Determine if meta assessment indicates escalation.
    meta_should_escalate = False
    if meta_assessment is not None and meta_assessment.should_escalate_to_human:
        meta_should_escalate = True
    # Also escalate automatically for clearly high-stakes tasks.
    elif is_high_stakes_task(task):
        meta_should_escalate = True

    # Apply PRIME's personality policy (IQ/EQ, creed, guardrails) to conclusions.
    core_response = enrich_core_response_with_personality(
        task=task,
        response=core_response,
        meta_should_escalate=meta_should_escalate,
    )

    return core_response


@router.post(
    "/memory/save",
    response_model=ReasoningMemorySaveResponse,
)
async def reasoning_memory_save(
    request: ReasoningMemorySaveRequest,
) -> ReasoningMemorySaveResponse:
    """
    Save a reasoning core response into the reasoning memory store.
    """
    entry = ReasoningMemoryEntry(
        id=request.entry_id,
        task=request.task,
        response=request.response,
        tags=request.tags,
        created_at=datetime.utcnow(),
        user_id=request.user_id or "raymond",
        outcome_quality=request.outcome_quality,
    )
    append_memory_entry(entry)
    return ReasoningMemorySaveResponse(entry_id=request.entry_id, status="saved")


async def reasoning_memory_query(
    request: ReasoningMemoryQuery,
) -> ReasoningMemoryQueryResponse:
    """
    Retrieve a small set of similar reasoning traces based on simple tag and text matching.
    """
    matches: list[ReasoningMemoryEntry] = []

    for entry in iter_memory_entries() or []:
        if request.domain and entry.tags.domain != request.domain:
            continue
        if request.subdomain and entry.tags.subdomain != request.subdomain:
            continue

        if request.theme_contains:
            theme_text = entry.tags.theme or ""
            task_text = entry.task.natural_language_task or ""
            haystack = (theme_text + " " + task_text).lower()
            if request.theme_contains.lower() not in haystack:
                continue

        matches.append(entry)
        if len(matches) >= request.limit:
            break

    return ReasoningMemoryQueryResponse(query=request, matches=matches)

@router.get("/prime/reasoning/corpus-search")
def corpus_search_endpoint(
    q: str = Query(..., description="Natural language query for corpus search"),
    k: int = Query(5, ge=1, le=20, description="Number of results"),
) -> List[Dict[str, Any]]:
    """
    Simple test endpoint to query the PRIME semantic corpus.
    """
    results = search_corpus(q, top_k=k)
    return results

@router.get("/prime/reasoning/corpus-any")
def corpus_any_endpoint() -> List[Dict[str, Any]]:
    """
    Debug: return a few arbitrary documents from the corpus without similarity search.
    """
    return list_any_corpus_docs(limit=3)
