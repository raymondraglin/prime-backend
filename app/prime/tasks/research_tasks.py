# app/prime/tasks/research_tasks.py
"""
PRIME Research Tasks

Async Celery task for the full research pipeline.
Runs plan → conduct → synthesize in the background.

Usage:
  task = run_research_async.delay(query="...", depth="standard")
  task_id = task.id
  # Poll GET /prime/tasks/status/{task_id} for progress
"""
from __future__ import annotations

import asyncio
from app.prime.tasks.celery_app import celery_app


@celery_app.task(bind=True, name="prime.research.run")
def run_research_async(self, query: str, depth: str = "standard", domain: str | None = None, context: dict | None = None):
    """
    Run the full research pipeline asynchronously.

    Args:
        query   : research query
        depth   : quick | standard | deep
        domain  : optional domain filter
        context : optional session context

    Returns:
        dict with report, citations, plan, findings
    """
    from app.prime.research.planner import plan_research
    from app.prime.research.conductor import research_sub_question
    from app.prime.research.synthesizer import synthesize_findings
    from datetime import datetime, timezone

    self.update_state(state="STARTED", meta={"stage": "planning", "progress": 0})

    try:
        # Plan
        plan = asyncio.run(plan_research(query, depth))
        self.update_state(state="STARTED", meta={"stage": "conducting", "progress": 20, "plan": plan})

        # Conduct (concurrent)
        tasks = [research_sub_question(sq, context=context or {}, depth=depth) for sq in plan]
        findings = asyncio.run(asyncio.gather(*tasks))
        self.update_state(state="STARTED", meta={"stage": "synthesizing", "progress": 70})

        # Synthesize
        report, citations = asyncio.run(synthesize_findings(query, findings, depth))
        self.update_state(state="STARTED", meta={"stage": "finalizing", "progress": 95})

        sources_consulted = len({c.get("source", "") for f in findings for c in f.get("citations", []) if c.get("source")})

        result = {
            "query": query,
            "depth": depth,
            "report": report,
            "citations": citations,
            "plan": plan,
            "findings": findings,
            "sub_questions_answered": len(findings),
            "sources_consulted": sources_consulted,
            "assembled_at": datetime.now(timezone.utc).isoformat(),
        }

        return result

    except Exception as exc:
        self.update_state(state="FAILURE", meta={"error": str(exc)})
        raise
