# app/prime/research/planner.py
"""
PRIME Research Planner

Breaks a research query into N focused sub-questions using the LLM.
The number of sub-questions is controlled by the depth parameter:
  quick    -> 3 sub-questions
  standard -> 5 sub-questions
  deep     -> 7 sub-questions

Output is a list of dicts: [{index, question, focus}, ...]

Design note:
  The planner runs at temperature=0.1 for maximum determinism.
  We want consistent, non-creative decomposition here. The conductor
  and synthesizer use higher temperatures for actual reasoning.
"""
from __future__ import annotations

import json
import re

from app.prime.llm.client import PrimeLLMClient, LLMConfig, LLMMessage

_DEPTH_MAP = {"quick": 3, "standard": 5, "deep": 7}


async def plan_research(query: str, depth: str = "standard") -> list[dict]:
    """
    Decompose a research query into focused sub-questions.

    Returns:
        list of dicts with keys: index, question, focus
    """
    n = _DEPTH_MAP.get(depth, 5)
    client = PrimeLLMClient(config=LLMConfig(temperature=0.1))

    prompt = (
        f"Break this research query into exactly {n} focused sub-questions.\n\n"
        f"Query: {query}\n\n"
        "Output ONLY a valid JSON array. Each item must have:\n"
        '  "question": the focused sub-question to answer\n'
        '  "focus": one short phrase describing what aspect it covers\n\n'
        "Example:\n"
        '[{"question": "What files handle PDF ingestion?", "focus": "file discovery"},\n'
        ' {"question": "Which function processes the payload?", "focus": "handler logic"}]\n\n'
        "Output ONLY the JSON array. No prose, no markdown, no code fences."
    )

    messages = [LLMMessage(role="user", content=prompt)]

    try:
        resp = await client.chat(messages)
        raw = resp.text.strip()
        # Strip markdown code fences if the model adds them
        raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.MULTILINE)
        raw = re.sub(r"\s*```$",          "", raw, flags=re.MULTILINE)
        parsed = json.loads(raw)
        return [
            {
                "index":    i + 1,
                "question": str(item.get("question", "")),
                "focus":    str(item.get("focus", "")),
            }
            for i, item in enumerate(parsed[:n])
            if item.get("question")
        ]
    except Exception:
        # Regex fallback: pull any quoted question values out
        questions = re.findall(r'"question"\s*:\s*"([^"]+)"', resp.text if 'resp' in dir() else "")
        if questions:
            return [
                {"index": i + 1, "question": q, "focus": ""}
                for i, q in enumerate(questions[:n])
            ]
        # Last resort: treat the full query as a single sub-question
        return [{"index": 1, "question": query, "focus": "full query"}]
