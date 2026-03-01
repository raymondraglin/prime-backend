# app/prime/research/conductor.py
"""
PRIME Research Conductor

Executes one focused sub-question using a full tool loop.

For each sub-question the conductor:
  1. Builds a targeted system prompt (RESEARCH MODE, citation rules)
  2. Runs chat_with_tools() with up to 4 tool rounds
  3. Returns a finding dict: {index, sub_question, focus, answer, citations, tool_calls_made}

All sub-questions are dispatched concurrently by routes.py via asyncio.gather.
Each conductor run is independent and stateless -- no shared message history.

Depth caps per sub-question:
  quick    -> max_tool_rounds=2
  standard -> max_tool_rounds=4
  deep     -> max_tool_rounds=6
"""
from __future__ import annotations

from typing import Any

_DEPTH_ROUNDS = {"quick": 2, "standard": 4, "deep": 6}


async def research_sub_question(
    sub_q: dict,
    context: dict[str, Any] | None = None,
    depth: str = "standard",
) -> dict:
    """
    Research one sub-question using the full tool loop.

    Args:
        sub_q:   {index, question, focus}
        context: optional session context (memories, projects, etc.)
        depth:   controls max_tool_rounds per sub-question

    Returns:
        finding dict: {index, sub_question, focus, answer, citations, tool_calls_made}
    """
    from app.prime.llm.client import PrimeLLMClient, LLMConfig, LLMMessage
    from app.prime.tools.prime_tools import TOOL_DEFINITIONS
    from app.prime.identity import PRIME_IDENTITY
    from app.prime.llm.prompt_builder import CITATION_RULES

    max_rounds = _DEPTH_ROUNDS.get(depth, 4)
    client     = PrimeLLMClient(config=LLMConfig(temperature=0.3))

    system = (
        PRIME_IDENTITY
        + "\n\n## RESEARCH MODE\n"
        "You are answering ONE focused research question. Your job:\n"
        "  1. Use tools to find the actual evidence (read files, search codebase, query DB).\n"
        "  2. State your finding clearly and concisely.\n"
        "  3. Cite every source using [CITE: ...] inline.\n"
        "  4. Do not pad. Do not hedge. If the answer is short, that is fine.\n"
        + CITATION_RULES
    )

    messages = [
        LLMMessage(role="system", content=system),
        LLMMessage(
            role="user",
            content=(
                f"Research sub-question {sub_q['index']}: {sub_q['question']}\n"
                + (f"Focus area: {sub_q['focus']}\n" if sub_q.get("focus") else "")
            ),
        ),
    ]

    try:
        resp = await client.chat_with_tools(
            messages=messages,
            tools=TOOL_DEFINITIONS,
            max_tool_rounds=max_rounds,
        )
        answer    = resp.text
        citations = resp.citations or []
        tc_made   = [tc.get("name", "") for tc in (resp.tool_calls or [])]
    except Exception as exc:
        answer    = f"[conductor error: {exc}]"
        citations = []
        tc_made   = []

    return {
        "index":           sub_q["index"],
        "sub_question":    sub_q["question"],
        "focus":           sub_q.get("focus", ""),
        "answer":          answer,
        "citations":       citations,
        "tool_calls_made": tc_made,
    }
