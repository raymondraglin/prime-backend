"""
PRIME Genius Endpoints
File: app/prime/api/genius.py

Self-contained engineering genius API.
No external module dependencies beyond OpenAI and FastAPI.
PRIME's full identity and hacker-level knowledge is baked into the system prompt.

Endpoints:
  POST /prime/ask       -- Ask PRIME anything (8 modes)
  POST /prime/debug     -- Debug broken code
  POST /prime/explain   -- Explain any concept
  POST /prime/generate  -- Generate code from description
  POST /prime/review    -- Review code for bugs/security/quality
  POST /prime/architect -- Design a system
  POST /prime/security  -- Threat model and harden
  GET  /prime/status    -- PRIME's status and capabilities
"""

from __future__ import annotations

import os
import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from openai import OpenAI

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/prime", tags=["PRIME Genius"])

# ---------------------------------------------------------------------------
# PRIME'S IDENTITY -- Baked in. No imports needed.
# ---------------------------------------------------------------------------

PRIME_BASE_IDENTITY = """
======================================================================
YOU ARE PRIME
======================================================================
Role: Elite Principal Software Engineer and Systems Architect
Level: Beyond Senior -- Principal / Architect / 10x

Philosophy:
  Software is thinking made real. Every line of code is a decision.
  Every architecture is a bet on the future. You understand both
  the code and the consequences.

Mission:
  Help Raymond build his empire -- Synergy Unlimited and PRIME.
  Not just working software -- systems that scale, survive, and dominate.

Hacker Creed:
  A true hacker does not just use tools -- they understand the machine
  beneath the tools. You see what others miss: the edge case, the race
  condition, the auth bypass, the memory leak, the bottleneck.
  You are better than the best hackers alive. You know every attack.
  You know every defense. You build systems that cannot be broken.

Raymond's Stack (you know this at master level):
  - Backend: Python, FastAPI, SQLAlchemy, PostgreSQL
  - Frontend: React, TypeScript, Next.js
  - AI: OpenAI API, DeepSeek API, prompt engineering, RAG, embeddings
  - DevOps: Docker, GitHub Actions, PowerShell, Windows
  - Platform: Synergy Unlimited (Healthcare, Criminal Justice, Marketing, Business)
  - Education: PRIME (Adaptive Learning Platform), ALP, BRIE

Your Principles:
  1. Understand the problem completely before writing one line of code.
  2. The best code is no code -- every line is a liability.
  3. Read the error message. All of it. Twice.
  4. If it is not tested, it does not work.
  5. Security is not a feature -- it is a property of the design.
  6. Performance problems are measurement problems first.
  7. Complexity is the enemy. Simple systems survive.
  8. Data outlives code. Design the schema like it matters forever.
  9. The network is unreliable. Design for failure.
  10. The hacker sees what the developer misses: the edge case, the assumption, the gap.
  11. Ship it. Then improve it. Perfect is the enemy of shipped.
  12. Every answer is in service of Raymond's empire.
======================================================================
"""

MODE_PROMPTS = {
    "general": """Answer as PRIME: elite principal engineer. Be direct, expert, and precise.
If the question is ambiguous, state your interpretation then answer it.
Connect your answer to Raymond's stack and mission where relevant.""",

    "debug": """You are PRIME in DEBUG mode. Your job: find the bug and fix it.
1. Read the full error message.
2. Identify the ROOT CAUSE -- not the symptom.
3. Explain what is wrong in plain terms.
4. Show the exact fix with corrected code.
5. Explain WHY this fix works.
6. Note any other issues you spotted.
Do not guess. Be surgical.""",

    "explain": """You are PRIME in EXPLAIN mode.
1. One-sentence definition.
2. How it actually works (the mechanism).
3. A concrete minimal example.
4. Connect it to Raymond's stack when relevant.
5. The most common misconception or gotcha.
Match depth to complexity. Do not over-explain simple things.""",

    "generate": """You are PRIME in GENERATE mode. Write production-quality code.
1. Confirm your understanding of what is being built.
2. Write clean, well-structured code following Raymond's stack conventions.
3. Include type hints (Python) and TypeScript types where applicable.
4. Handle edge cases and errors properly.
5. Note any assumptions and follow-up work needed.
Standards: PEP 8, Pydantic models, FastAPI patterns, parameterized SQL, secure defaults.""",

    "review": """You are PRIME in CODE REVIEW mode. Review like a principal engineer.
For each issue state: Severity (Critical/High/Medium/Low), Location, Problem, Fix.
Review for:
  1. BUGS -- logic errors, null handling, type mismatches
  2. SECURITY -- injection, auth gaps, exposed secrets, insecure defaults
  3. PERFORMANCE -- N+1 queries, missing indexes, blocking I/O
  4. CORRECTNESS -- does it actually do what it claims?
  5. QUALITY -- naming, structure, duplication
End with a summary verdict.""",

    "architecture": """You are PRIME in ARCHITECTURE mode. Design systems that dominate.
1. Clarify requirements: scale, consistency needs, team size.
2. Identify the core tradeoffs.
3. Propose the design with components and interactions.
4. Explain WHY each decision was made.
5. Call out failure modes and mitigations.
6. State what to build first (MVP) and what to defer.
Think in Raymond's context: FastAPI, PostgreSQL, React, AI integrations.""",

    "security": """You are PRIME in SECURITY mode. Think like the best hacker alive.
For any system or code presented:
1. Identify every attack surface.
2. Name specific attack vectors (OWASP Top 10, auth attacks, crypto weaknesses, injection).
3. Rate severity of each vulnerability (Critical/High/Medium/Low).
4. Give the exact hardening fix for each.
5. Recommend the defensive architecture.
Explain the exploit, the impact, and the precise countermeasure. No vague advice.""",

    "teach": """You are PRIME in TEACH mode. Explain for a CS student who is learning.
1. Start with the WHY -- what problem does this solve?
2. Build up from what they already know.
3. Use analogies when they genuinely help.
4. Show a minimal working example.
5. End with one thing they should try themselves.
Be encouraging but precise. Elevate, do not dumb down.""",
}

VALID_MODES = list(MODE_PROMPTS.keys())


# ---------------------------------------------------------------------------
# LLM CALL
# ---------------------------------------------------------------------------

def _call_prime(question: str, mode: str = "general") -> str:
    """Core LLM call. Builds PRIME's full system prompt and sends the question."""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    system_prompt = PRIME_BASE_IDENTITY + "\n" + MODE_PROMPTS.get(mode, MODE_PROMPTS["general"])

    response = client.chat.completions.create(
        model=os.getenv("PRIME_MODEL", "gpt-4o"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": question},
        ],
        temperature=0.3,
        max_tokens=4096,
    )

    return response.choices[0].message.content or ""


# ---------------------------------------------------------------------------
# REQUEST / RESPONSE MODELS
# ---------------------------------------------------------------------------

class AskRequest(BaseModel):
    question: str = Field(..., description="What you want to ask PRIME")
    mode: str = Field(default="general", description="general | debug | explain | generate | review | architecture | security | teach")

class DebugRequest(BaseModel):
    code: str = Field(..., description="The broken code")
    error: str = Field(default="", description="Error message or traceback")
    language: str = Field(default="python")
    context: str = Field(default="", description="What the code is supposed to do")

class ExplainRequest(BaseModel):
    topic: str = Field(..., description="Concept or code to explain")
    language: Optional[str] = Field(default=None)
    level: str = Field(default="engineer", description="student | engineer | expert")

class GenerateRequest(BaseModel):
    description: str = Field(..., description="What to build")
    language: str = Field(default="python")
    framework: str = Field(default="")
    requirements: Optional[List[str]] = Field(default=None)

class ReviewRequest(BaseModel):
    code: str = Field(..., description="Code to review")
    language: str = Field(default="python")
    focus: Optional[List[str]] = Field(default=None, description="security | performance | bugs")

class ArchitectRequest(BaseModel):
    description: str = Field(..., description="System to design")
    constraints: Optional[List[str]] = Field(default=None)
    scale: str = Field(default="startup", description="startup | growth | enterprise")

class ThreatModelRequest(BaseModel):
    system_description: str = Field(..., description="System to threat model")
    code: str = Field(default="")

class PRIMEResponse(BaseModel):
    answer: str
    mode: str
    model: str


# ---------------------------------------------------------------------------
# ENDPOINTS
# ---------------------------------------------------------------------------

@router.get("/status", summary="PRIME status and capabilities")
async def prime_status():
    return {
        "status": "online",
        "model": os.getenv("PRIME_MODEL", "gpt-4o"),
        "identity": "Elite principal engineer. Hacker-level security. Raymond's full stack mastery.",
        "modes": VALID_MODES,
        "endpoints": [
            "POST /prime/ask        -- Ask anything (8 modes)",
            "POST /prime/debug      -- Debug broken code",
            "POST /prime/explain    -- Explain any concept",
            "POST /prime/generate   -- Generate code from description",
            "POST /prime/review     -- Review code",
            "POST /prime/architect  -- Design a system",
            "POST /prime/security   -- Threat model and harden",
            "POST /prime/chat/      -- Full reasoning chat (existing)",
            "GET  /prime/status     -- This endpoint",
        ],
    }


@router.post("/ask", response_model=PRIMEResponse, summary="Ask PRIME anything")
async def ask_prime(req: AskRequest):
    if req.mode not in VALID_MODES:
        raise HTTPException(400, f"Invalid mode '{req.mode}'. Choose from: {VALID_MODES}")
    try:
        answer = _call_prime(req.question, req.mode)
        return PRIMEResponse(answer=answer, mode=req.mode, model=os.getenv("PRIME_MODEL", "gpt-4o"))
    except Exception as e:
        logger.error("PRIME /ask error: %s", e)
        raise HTTPException(500, str(e))


@router.post("/debug", response_model=PRIMEResponse, summary="PRIME debugs your code")
async def debug_code(req: DebugRequest):
    parts = []
    if req.context:
        parts.append(f"CONTEXT: {req.context}")
    parts.append(f"LANGUAGE: {req.language}")
    parts.append(f"\nCODE:\n```{req.language}\n{req.code}\n```")
    if req.error:
        parts.append(f"\nERROR:\n{req.error}")
    parts.append("\nFind the bug. Fix it. Explain why.")
    try:
        answer = _call_prime("\n".join(parts), "debug")
        return PRIMEResponse(answer=answer, mode="debug", model=os.getenv("PRIME_MODEL", "gpt-4o"))
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/explain", response_model=PRIMEResponse, summary="PRIME explains a concept")
async def explain_concept(req: ExplainRequest):
    mode = "teach" if req.level == "student" else "explain"
    parts = [f"Explain: {req.topic}"]
    if req.language:
        parts.append(f"Language context: {req.language}")
    parts.append(f"Explanation level: {req.level}")
    try:
        answer = _call_prime("\n".join(parts), mode)
        return PRIMEResponse(answer=answer, mode=mode, model=os.getenv("PRIME_MODEL", "gpt-4o"))
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/generate", response_model=PRIMEResponse, summary="PRIME generates code")
async def generate_code(req: GenerateRequest):
    parts = [f"Generate code for: {req.description}", f"Language: {req.language}"]
    if req.framework:
        parts.append(f"Framework: {req.framework}")
    if req.requirements:
        parts.append("Requirements:\n" + "\n".join(f"  - {r}" for r in req.requirements))
    try:
        answer = _call_prime("\n".join(parts), "generate")
        return PRIMEResponse(answer=answer, mode="generate", model=os.getenv("PRIME_MODEL", "gpt-4o"))
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/review", response_model=PRIMEResponse, summary="PRIME reviews your code")
async def review_code(req: ReviewRequest):
    parts = [f"Review this {req.language} code:", f"```{req.language}\n{req.code}\n```"]
    if req.focus:
        parts.append(f"Focus areas: {', '.join(req.focus)}")
    try:
        answer = _call_prime("\n".join(parts), "review")
        return PRIMEResponse(answer=answer, mode="review", model=os.getenv("PRIME_MODEL", "gpt-4o"))
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/architect", response_model=PRIMEResponse, summary="PRIME designs a system")
async def architect_system(req: ArchitectRequest):
    parts = [f"Design: {req.description}", f"Scale: {req.scale}"]
    if req.constraints:
        parts.append("Constraints:\n" + "\n".join(f"  - {c}" for c in req.constraints))
    try:
        answer = _call_prime("\n".join(parts), "architecture")
        return PRIMEResponse(answer=answer, mode="architecture", model=os.getenv("PRIME_MODEL", "gpt-4o"))
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/security", response_model=PRIMEResponse, summary="PRIME threat models your system")
async def threat_model(req: ThreatModelRequest):
    parts = [f"Threat model: {req.system_description}"]
    if req.code:
        parts.append(f"\nCode to analyze:\n```\n{req.code}\n```")
    try:
        answer = _call_prime("\n".join(parts), "security")
        return PRIMEResponse(answer=answer, mode="security", model=os.getenv("PRIME_MODEL", "gpt-4o"))
    except Exception as e:
        raise HTTPException(500, str(e))
