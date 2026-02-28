# app/prime/evals/runner.py
"""
PRIME Eval Runner

Runs all (or selected) EvalTasks and produces a scored report.

Usage:
    python -m app.prime.evals.runner              # run all tasks
    python -m app.prime.evals.runner eng-001      # run one task by id prefix
    python -m app.prime.evals.runner schema       # run all tasks in a category
    python -m app.prime.evals.runner --include-tool-required  # include tool tasks

TEMPERATURE NOTE:
    Production PRIME runs at temperature=0.85 for natural, varied responses.
    Eval mode runs at temperature=0.2 so scores are stable and repeatable.
    A score that varies run-to-run because of randomness is not a score —
    it's noise. Keep eval temp low. Keep production temp high.

Output:
    Prints a summary table to stdout.
    Writes app/prime/evals/results/YYYY-MM-DD_HHMMSS.json for trend tracking.

NOTE ON TOOL-REQUIRED TASKS:
    Tasks with requires_tools=True are skipped in default mode because running
    them without actual file access causes PRIME to hallucinate. They are
    scored separately once the runner is wired with chat_with_tools.
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

# Low temperature for eval runs — keeps scores stable and repeatable.
# Production PRIME uses 0.85. Do not raise this without a clear reason.
EVAL_TEMPERATURE = 0.2


async def _run_task(task, context: Dict[str, Any]) -> Dict[str, Any]:
    from app.prime.llm.prompt_builder import build_chat_messages
    from app.prime.llm.client import PrimeLLMClient, LLMConfig

    # Override temperature for eval stability
    eval_config = LLMConfig(temperature=EVAL_TEMPERATURE)
    eval_llm = PrimeLLMClient(config=eval_config)

    messages = build_chat_messages(
        user_message=task.prompt,
        context=context,
        engineer_mode=task.engineer_mode,
    )

    try:
        resp = await eval_llm.chat(messages)
        output = resp.text
        error = None
    except Exception as e:
        output = ""
        error = str(e)

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
        "skipped": False,
        "temperature": EVAL_TEMPERATURE,
    }


async def run_evals(
    filter_str: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    include_tool_required: bool = False,
) -> List[Dict[str, Any]]:
    from app.prime.evals.tasks import TASKS

    context = context or {}

    tasks = TASKS
    if filter_str:
        tasks = [t for t in TASKS if filter_str in t.id or filter_str in t.category]

    skipped = [t for t in tasks if t.requires_tools and not include_tool_required]
    runnable = [t for t in tasks if not t.requires_tools or include_tool_required]

    if skipped:
        print(f"\n[PRIME EVALS] Skipping {len(skipped)} tool-required task(s):")
        for t in skipped:
            print(f"  \u23ed SKIP  [{t.category:12s}]  {t.id}  \u2014 {t.description[:60]}")

    print(f"\n[PRIME EVALS] Running {len(runnable)} task(s) at temperature={EVAL_TEMPERATURE}...\n")
    results = []

    for task in runnable:
        result = await _run_task(task, context)
        status = "\u2705 PASS" if result["passed"] else "\u274c FAIL"
        print(f"  {status}  [{result['category']:12s}]  {result['id']}")
        if not result["passed"]:
            for c in result["checks"]:
                mark = "  \u2713" if c["passed"] else "  \u2717"
                print(f"             {mark} {c['pattern']}")
            if result["error"]:
                print(f"             ERROR: {result['error']}")
        results.append(result)

    for task in skipped:
        results.append({
            "id": task.id,
            "category": task.category,
            "passed": False,
            "error": "skipped: requires tool access",
            "checks": [],
            "output_preview": "",
            "prompt": task.prompt,
            "skipped": True,
            "temperature": EVAL_TEMPERATURE,
        })

    passed = sum(1 for r in results if r["passed"])
    skipped_count = sum(1 for r in results if r.get("skipped"))
    scored = len(results) - skipped_count
    pct = round(100 * passed / scored) if scored else 0

    print(f"\n[PRIME EVALS] {passed}/{scored} passed ({pct}%)  |  {skipped_count} skipped (tool-required)\n")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
    out_path = RESULTS_DIR / f"{ts}.json"
    out_path.write_text(
        json.dumps(
            {"timestamp": ts, "passed": passed, "scored": scored,
             "skipped": skipped_count, "temperature": EVAL_TEMPERATURE,
             "results": results},
            indent=2,
        )
    )
    print(f"[PRIME EVALS] Results saved \u2192 {out_path}\n")
    return results


if __name__ == "__main__":
    args = sys.argv[1:]
    include_tools = "--include-tool-required" in args
    filter_arg = next((a for a in args if not a.startswith("--")), None)
    asyncio.run(run_evals(filter_arg, include_tool_required=include_tools))
