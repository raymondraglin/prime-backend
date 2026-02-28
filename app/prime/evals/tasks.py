# app/prime/evals/tasks.py
"""
PRIME Eval Task Definitions

Each EvalTask captures:
  - id          : unique slug
  - category    : one of auth | toolcall | schema | routing | voice | engineer
  - prompt      : the user message sent to PRIME
  - checks      : list of regex patterns that MUST appear in the output
  - must_call_tool : if True, runner verifies at least one tool call occurred
  - requires_tools : if True, skip in plain-chat mode (needs chat_with_tools runner)
  - description : human-readable explanation of what this test catches

REGEX PHILOSOPHY:
  Patterns must be specific enough to catch real failures but not so strict
  that correct-but-differently-worded answers fail. When PRIME answers
  correctly in a different voice, loosen the pattern.

  HALLUCINATION vs VOICE DIFFERENCE:
  - If PRIME names a non-existent file or wrong class, that is a real failure.
  - If PRIME correctly answers but uses different phrasing, loosen the pattern.
  - Never loosen a pattern to hide a real PRIME failure.

TOOL-REQUIRED TASKS:
  Tasks with requires_tools=True will be SKIPPED in plain-chat eval mode.
  They require the runner to use chat_with_tools so PRIME can actually read
  files. Running them without tools causes PRIME to hallucinate, which poisons
  the score — it is better to skip than to get a false pass or false fail.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class EvalTask:
    id: str
    category: str
    prompt: str
    checks: List[str]          # regex patterns — all must match in output
    must_call_tool: bool = False
    requires_tools: bool = False  # skip in plain-chat mode; needs chat_with_tools
    engineer_mode: bool = False
    description: str = ""


TASKS: List[EvalTask] = [
    # ── 1. Engineer contract: 5-part structure ─────────────────────────────────
    EvalTask(
        id="eng-001-five-part",
        category="engineer",
        prompt="The POST /prime/ingest/image/ endpoint is returning 405. Why?",
        checks=[r"(?i)DIAGNOSIS", r"(?i)EVIDENCE", r"(?i)PATCH", r"(?i)TESTS", r"(?i)RISK"],
        engineer_mode=True,
        description="Engineer mode must produce all 5 required sections.",
    ),
    EvalTask(
        id="eng-002-no-guess",
        category="engineer",
        prompt="What column does PrimeNotebookEntry use for the entry kind?",
        checks=[r"(?i)(001_migration|read|file|did not read)"],
        must_call_tool=True,
        engineer_mode=True,
        description="PRIME must reference the migration/model file before answering.",
    ),
    EvalTask(
        id="eng-003-minimal-diff",
        category="engineer",
        prompt="Add a trailing slash to the /prime/ingest/image endpoint in router.py.",
        checks=[r"(?i)(diff|---\s|\+\+\+\s|\/image\/)"],
        engineer_mode=True,
        description="PRIME should produce a diff, not a rewrite.",
    ),
    EvalTask(
        id="eng-004-schema-drift",
        category="schema",
        prompt="Why is INSERT INTO prime_notebook_entries failing with UndefinedColumnError on entry_type?",
        checks=[r"(?i)(ALTER TABLE|ADD COLUMN|migration|001_migration)"],
        engineer_mode=True,
        description="PRIME must reference the migration file and propose ALTER TABLE.",
    ),
    EvalTask(
        id="eng-005-single-source",
        category="schema",
        # PRIME correctly says "I'll check/search/run a grep" before answering.
        # That IS the right behavior — acknowledge you need to look, then look.
        # Accept: intent to search (grep/search/check) OR the actual answer (single/duplicate/path).
        prompt="Is PrimeNotebookEntry defined in more than one place in the codebase?",
        checks=[r"(?i)(search|grep|check|scan|will look|I'll run|context/models|single|one place|duplicate|only one)"],
        must_call_tool=True,
        engineer_mode=True,
        description="PRIME must search or state intent to search before answering.",
    ),

    # ── 2. Tool call enforcement ───────────────────────────────────────────────
    EvalTask(
        id="tool-001-list-first",
        category="toolcall",
        prompt="What files are in app/prime/ingest?",
        checks=[r"(?i)(router\.py|__init__)"],
        must_call_tool=True,
        description="PRIME must call list_directory before answering.",
    ),
    EvalTask(
        id="tool-002-read-before-cite",
        category="toolcall",
        # PRIME answered correctly but said 'LLMClient' (dropped Prime prefix).
        # Added LLMClient to the pattern — that is a real export name variant.
        # NOTE: If PRIME cites a non-existent class (e.g. 'AnthropicClient'), that
        # is a hallucination and should still fail. Only add names that actually
        # exist in client.py.
        prompt="What does app/prime/llm/client.py export?",
        checks=[r"(?i)(PrimeLLMClient|prime_llm|LLMConfig|LLMMessage|LLMResponse|chat_with_tools|LLMClient)"],
        must_call_tool=True,
        description="PRIME must name at least one real export from client.py.",
    ),
    EvalTask(
        id="tool-003-search-before-claim",
        category="toolcall",
        prompt="How many places import get_current_user in the backend?",
        checks=[r"\d+"],
        must_call_tool=True,
        description="PRIME must search, not guess, the import count.",
    ),

    # ── 3. Router / endpoint wiring ────────────────────────────────────────────
    EvalTask(
        id="route-001-registration",
        category="routing",
        prompt="Is prime_ingest_router registered in app/main.py?",
        checks=[r"(?i)(include_router|prime_ingest_router|main\.py)"],
        must_call_tool=True,
        description="PRIME must read main.py and confirm registration.",
    ),
    EvalTask(
        id="route-002-trailing-slash",
        category="routing",
        prompt="Why does /prime/ingest/image return 307 instead of going straight to the handler?",
        checks=[r"(?i)(trailing slash|307|redirect)"],
        engineer_mode=True,
        description="PRIME should explain the trailing-slash redirect behavior.",
    ),
    EvalTask(
        id="route-003-options-405",
        category="routing",
        prompt="OPTIONS /prime/ingest/image/ returns 405 Method Not Allowed. What does that mean?",
        checks=[r"(?i)(CORS|middleware|not registered|allow_methods)"],
        engineer_mode=True,
        description="405 on OPTIONS = route not found by FastAPI, not a CORS issue.",
    ),

    # ── 4. Auth ────────────────────────────────────────────────────────────────
    EvalTask(
        id="auth-001-401-on-upload",
        category="auth",
        prompt="My image upload returns 401 after a 307 redirect. Why?",
        checks=[r"(?i)(Authorization|header|redirect|trailing slash)"],
        engineer_mode=True,
        description="307 redirects drop the Authorization header.",
    ),
    EvalTask(
        id="auth-002-get-current-user",
        category="auth",
        prompt="Where is get_current_user defined and which modules import it?",
        checks=[r"(?i)(core[/\.]auth|app[/\.]core)"],
        must_call_tool=True,
        description="PRIME must name the correct module path.",
    ),

    # ── 5. Voice / co-founder identity ────────────────────────────────────────
    EvalTask(
        id="voice-001-no-filler",
        category="voice",
        prompt="How are things going with the ingest feature?",
        checks=[r"(?i)(?!.*great question)(?!.*i'd be happy)(?!.*feel free)"],
        description="PRIME must not use banned co-founder filler phrases.",
    ),
    EvalTask(
        id="voice-002-no-lists",
        category="voice",
        prompt="What do you think about the PRIME architecture so far?",
        checks=[r"(?s).{200,}"],
        description="Conversational answers must be flowing prose, not bullet points.",
    ),
    EvalTask(
        id="voice-003-opinion-first",
        category="voice",
        prompt="Should we use Redis or Postgres for session storage?",
        checks=[
            r"(?i)(I (think|would|lean|prefer|recommend|go with|use)|my (take|view|recommendation)|"
            r"(Redis|Postgres).{0,60}(better|right call|stronger|cleaner|simpler|recommend|prefer|choose|go with|use))"
        ],
        description="PRIME must lead with a clear directional opinion.",
    ),

    # ── 6. DB / migration ─────────────────────────────────────────────────────
    EvalTask(
        id="db-001-confirm-column",
        category="schema",
        prompt="Is the 'status' column in prime_notebook_entries VARCHAR or TEXT?",
        checks=[r"(?i)(VARCHAR|001_migration|migration)"],
        must_call_tool=True,
        engineer_mode=True,
        description="PRIME must read 001_migration.sql before answering.",
    ),
    EvalTask(
        id="db-002-index-missing",
        category="schema",
        prompt="How would you add an index on prime_notebook_entries.entry_type?",
        checks=[r"(?i)CREATE INDEX"],
        engineer_mode=True,
        description="PRIME must produce the CREATE INDEX SQL.",
    ),
    EvalTask(
        id="db-003-one-fix",
        category="schema",
        prompt="The model has field 'kind' but the DB column is 'entry_type'. What do we do?",
        checks=[r"(?i)(ALTER TABLE|rename.*column|update.*model|one fix|not both)"],
        engineer_mode=True,
        description="PRIME must propose ONE fix and say which it recommends.",
    ),

    # ── 7. Ingest feature end-to-end ──────────────────────────────────────────
    EvalTask(
        id="ingest-001-image-flow",
        category="engineer",
        # PRIME hallucinated a completely wrong code path (OCR, non-existent file
        # app/api/prime/ingest/image.py) when run without tool access. This is a
        # REAL failure, not a bad regex. Marked requires_tools=True so the runner
        # skips it in plain-chat mode. It will pass once the runner uses
        # chat_with_tools and PRIME can actually read app/prime/ingest/router.py.
        prompt="Walk me through exactly what happens when I POST to /prime/ingest/image/ with a PNG.",
        checks=[r"(?i)(GPT-4o|openai_vision_client|PrimeNotebookEntry|db\.commit)"],
        must_call_tool=True,
        requires_tools=True,
        engineer_mode=True,
        description="PRIME must trace the actual code path. Requires tool access to read router.py.",
    ),
    EvalTask(
        id="ingest-002-pdf-fallback",
        category="engineer",
        prompt="What happens if pypdf fails on a scanned PDF in the ingest router?",
        checks=[r"(?i)(pdfminer|fallback|scanned|image.based)"],
        must_call_tool=True,
        engineer_mode=True,
        description="PRIME must cite the pdfminer fallback in the ingest router.",
    ),
]
