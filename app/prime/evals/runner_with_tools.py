# app/prime/evals/runner_with_tools.py
"""
PRIME Eval Runner (With Tools)

Differs from runner.py in two ways:
  1. Uses chat_with_tools() so PRIME can actually call read_file,
     search_codebase, query_database, etc. during evals.
  2. Runs ALL tasks -- including those with requires_tools=True
     (e.g. ingest-001-image-flow) that plain runner always skips.

This runner also enforces must_call_tool=True tasks: if PRIME did not
call at least one tool on a must_call_tool task, the task FAILS even
if the output matches all regex checks. No guessing allowed.

Usage:
    python -m app.prime.evals.runner_with_tools          # run all tasks
    python -m app.prime.evals.runner_with_tools ingest   # filter by id/category
    python -m app.prime.evals.runner_with_tools tool-001 # run one task by id

Output:
    Prints a summary table to stdout.
    Writes app/prime/evals/results/tools_YYYY-MM-DD_HHMMSS.json

TEMPERATURE NOTE:
    Same as runner.py -- eval temp is fixed at 0.2 for reproducibility.
    Production PRIME runs at 0.85.
"""

from __future__ import annotations

from dotenv import load_dotenv
load_dotenv()

import asyncio
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

RESULTS_DIR = Path(__file__).parent / "results"
EVAL_TEMPERATURE = 0.2


async def _run_task_with_tools(task, context: Dict[str, Any]) -> Dict[str, Any]:
    from app.prime.llm.prompt_builder import build_chat_messages
    from app.prime.llm.client import PrimeLLMClient, LLMConfig
    from app.prime.tools.prime_tools import TOOL_DEFINITIONS

    eval_config = LLMConfig(temperature=EVAL_TEMPERATURE)
    eval_llm = PrimeLLMClient(config=eval_config)

    messages = build_chat_messages(
        user_message=task.prompt,
        context=context,
        engineer_mode=task.engineer_mode,
    )

    tool_calls_made: list = []
    output = ""
    error = None

    try:
        resp = await eval_llm.chat_with_tools(
            messages=messages,
            tools=TOOL_DEFINITIONS,
            max_tool_rounds=6,
        )
        output = resp.text
        tool_calls_made = resp.tool_calls or []
    except Exception as exc:
        # Graceful fallback: try plain chat so we still score non-tool checks
        try:
            fallback = await eval_llm.chat(messages)
            output = fallback.text
        except Exception:
            output = ""
        error = str(exc)

    # --- Check regex patterns ---
    check_results = []
    for pattern in task.checks:
        matched = bool(re.search(pattern, output))
        check_results.append({"pattern": pattern, "passed": matched})

    regex_passed = all(c["passed"] for c in check_results)

    # --- Enforce must_call_tool ---
    tool_call_ok = True
    tool_call_note = None
    if task.must_call_tool and not tool_calls_made:
        tool_call_ok = False
        tool_call_note = "FAIL: must_call_tool=True but zero tool calls were made"

    passed = regex_passed and tool_call_ok and error is None

    return {
        "id":             task.id,
        "category":       task.category,
        "passed":         passed,
        "error":          error,
        "checks":         check_results,
        "tool_calls_made": [tc.get("name", str(tc)) if isinstance(tc, dict) else str(tc)
                            for tc in tool_calls_made],
        "tool_call_note": tool_call_note,
        "output_preview": output[:400],
        "prompt":         task.prompt,
        "skipped":        False,
        "requires_tools": task.requires_tools,
        "must_call_tool": task.must_call_tool,
        "temperature":    EVAL_TEMPERATURE,
    }


async def run_evals_with_tools(
    filter_str: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    from app.prime.evals.tasks import TASKS

    context = context or {}
    tasks = TASKS

    if filter_str:
        tasks = [t for t in TASKS if filter_str in t.id or filter_str in t.category]

    tool_required = [t for t in tasks if t.requires_tools]
    print(f"\n[PRIME EVALS/TOOLS] Running {len(tasks)} task(s) "
          f"({len(tool_required)} tool-required) at temperature={EVAL_TEMPERATURE}...\n")

    results = []
    for task in tasks:
        result = await _run_task_with_tools(task, context)
        status = "\u2705 PASS" if result["passed"] else "\u274c FAIL"
        tool_badge = " [tool]" if result["requires_tools"] else ""
        print(f"  {status}  [{result['category']:12s}]  {result['id']}{tool_badge}")

        if not result["passed"]:
            for c in result["checks"]:
                mark = "  \u2713" if c["passed"] else "  \u2717"
                print(f"             {mark} {c['pattern']}")
            if result.get("tool_call_note"):
                print(f"             \u2717 {result['tool_call_note']}")
            if result["error"]:
                print(f"             ERROR: {result['error']}")

        results.append(result)

    passed  = sum(1 for r in results if r["passed"])
    scored  = len(results)
    pct     = round(100 * passed / scored) if scored else 0

    print(f"\n[PRIME EVALS/TOOLS] {passed}/{scored} passed ({pct}%)\n")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
    out_path = RESULTS_DIR / f"tools_{ts}.json"
    out_path.write_text(
        json.dumps(
            {
                "timestamp":   ts,
                "runner":      "runner_with_tools",
                "passed":      passed,
                "scored":      scored,
                "skipped":     0,
                "temperature": EVAL_TEMPERATURE,
                "results":     results,
            },
            indent=2,
        )
    )
    print(f"[PRIME EVALS/TOOLS] Results saved \u2192 {out_path}\n")
    return results


if __name__ == "__main__":
    args = sys.argv[1:]
    filter_arg = next((a for a in args if not a.startswith("--")), None)
    asyncio.run(run_evals_with_tools(filter_arg))
