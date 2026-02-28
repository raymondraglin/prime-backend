# app/prime/evals/runner.py
"""
PRIME Eval Runner

Runs all (or selected) EvalTasks and produces a scored report.

Usage:
    python -m app.prime.evals.runner              # run all tasks
    python -m app.prime.evals.runner eng-001      # run one task by id prefix
    python -m app.prime.evals.runner schema       # run all tasks in a category

Output:
    Prints a summary table to stdout.
    Writes app/prime/evals/results/YYYY-MM-DD_HHMMSS.json for trend tracking.
"""

from __future__ import annotations

import asyncio
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

RESULTS_DIR = Path(__file__).parent / "results"


async def _run_task(task, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run a single EvalTask and return a result dict.
    Uses build_chat_messages + prime_llm.chat (non-tool path for simplicity).
    Tool-call enforcement is checked by inspecting whether the response cites
    a file path or tool-output marker — a heuristic until a full tool harness
    is wired in.
    """
    from app.prime.llm.prompt_builder import build_chat_messages
    from app.prime.llm.client import prime_llm

    messages = build_chat_messages(
        user_message=task.prompt,
        context=context,
        engineer_mode=task.engineer_mode,
    )

    try:
        resp = await prime_llm.chat(messages)
        output = resp.text
        error = None
    except Exception as e:
        output = ""
        error = str(e)

    # Score each regex check
    check_results = []
    for pattern in task.checks:
        matched = bool(re.search(pattern, output))
        check_results.append({"pattern": pattern, "passed": matched})

    passed = all(c["passed"] for c in check_results) and error is None

    return {
        "id": task.id,
        "category": task.category,
        "passed": passed,
        "error": error,
        "checks": check_results,
        "output_preview": output[:400],
        "prompt": task.prompt,
    }


async def run_evals(
    filter_str: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    from app.prime.evals.tasks import TASKS

    context = context or {}

    tasks = TASKS
    if filter_str:
        tasks = [
            t for t in TASKS
            if filter_str in t.id or filter_str in t.category
        ]

    print(f"\n[PRIME EVALS] Running {len(tasks)} task(s)...\n")
    results = []
    for task in tasks:
        result = await _run_task(task, context)
        status = "✅ PASS" if result["passed"] else "❌ FAIL"
        print(f"  {status}  [{result['category']:12s}]  {result['id']}")
        if not result["passed"]:
            for c in result["checks"]:
                mark = "  ✓" if c["passed"] else "  ✗"
                print(f"             {mark} {c['pattern']}")
            if result["error"]:
                print(f"             ERROR: {result['error']}")
        results.append(result)

    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    pct = round(100 * passed / total) if total else 0
    print(f"\n[PRIME EVALS] {passed}/{total} passed ({pct}%)\n")

    # Save results
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
    out_path = RESULTS_DIR / f"{ts}.json"
    out_path.write_text(
        json.dumps({"timestamp": ts, "passed": passed, "total": total, "results": results}, indent=2)
    )
    print(f"[PRIME EVALS] Results saved → {out_path}\n")
    return results


if __name__ == "__main__":
    filter_arg = sys.argv[1] if len(sys.argv) > 1 else None
    asyncio.run(run_evals(filter_arg))
