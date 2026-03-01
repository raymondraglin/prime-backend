# app/prime/research/routes.py
"""
PRIME Research Endpoint

POST /prime/research/
  Runs the full multi-step research pipeline:
    1. Plan   -- LLM decomposes query into N sub-questions
    2. Conduct -- each sub-question is researched with tool access (concurrent)
    3. Synthesize -- all findings are woven into a final report

  Depth levels:
    quick    -> 3 sub-questions, 2 tool rounds each
    standard -> 5 sub-questions, 4 tool rounds each  (default)
    deep     -> 7 sub-questions, 6 tool rounds each

Response fields:
    report                 -- final synthesized prose
    citations              -- merged citation list from all phases
    plan                   -- the sub-questions PRIME generated
    findings               -- per-sub-question answers + citations
    sub_questions_answered -- int
    sources_consulted      -- unique source count
    assembled_at           -- ISO timestamp
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/prime/research", tags=["PRIME Research"])

_VALID_DEPTHS = {"quick", "standard", "deep"}


class ResearchRequest(BaseModel):
    query:   str
    depth:   str        = "standard"    # quick | standard | deep
    domain:  Optional[str] = None
    context: dict[str, Any] = Field(default_factory=dict)


class ResearchResponse(BaseModel):
    query:                  str
    depth:                  str
    report:                 str
    citations:              list[dict] = Field(default_factory=list)
    plan:                   list[dict] = Field(default_factory=list)
    findings:               list[dict] = Field(default_factory=list)
    sub_questions_answered: int        = 0
    sources_consulted:      int        = 0
    assembled_at:           str


@router.post("/", response_model=ResearchResponse)
async def run_research(req: ResearchRequest):
    if not req.query.strip():
        raise HTTPException(400, "Query cannot be empty.")
    if req.depth not in _VALID_DEPTHS:
        raise HTTPException(400, f"depth must be one of: {', '.join(sorted(_VALID_DEPTHS))}")

    try:
        from app.prime.research.planner    import plan_research
        from app.prime.research.conductor  import research_sub_question
        from app.prime.research.synthesizer import synthesize_findings

        # ── 1. Plan ──────────────────────────────────────────────────────────
        plan = await plan_research(req.query, req.depth)

        # ── 2. Conduct (concurrent) ───────────────────────────────────────────
        tasks    = [
            research_sub_question(sq, context=req.context, depth=req.depth)
            for sq in plan
        ]
        findings = list(await asyncio.gather(*tasks))

        # ── 3. Synthesize ─────────────────────────────────────────────────────
        report, citations = await synthesize_findings(req.query, findings, req.depth)

        sources_consulted = len({
            c.get("source", "")
            for f in findings
            for c in f.get("citations", [])
            if c.get("source")
        })

        return ResearchResponse(
            query                  = req.query,
            depth                  = req.depth,
            report                 = report,
            citations              = citations,
            plan                   = plan,
            findings               = findings,
            sub_questions_answered = len(findings),
            sources_consulted      = sources_consulted,
            assembled_at           = datetime.now(timezone.utc).isoformat(),
        )

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(500, f"Research pipeline error: {exc}") from exc
