"""
PRIME Intent Classifier
File: app/prime/agent/intent.py

Turns each inbound message into a typed IntentDecision that tells the
orchestrator exactly what to do: which tools to allow, whether to inject
the engineer contract, how many tool rounds are permitted, and whether
web or exec capabilities are needed.

Philosophy:
  Rules run first — fast, deterministic, zero API cost.
  Rules miss triggers optional LLM-assist classification (stub; wire in
  when you want probabilistic upgrade over pure keywords).

  Least-privilege tool policy: PRIME only gets the tools it actually
  needs for the stated intent. GENERAL_CHAT gets nothing.
"""

from __future__ import annotations

import re
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class IntentType(str, Enum):
    CODE_ASSIST  = "code_assist"
    REPO_QA      = "repo_qa"
    DB_QA        = "db_qa"
    WEB_RESEARCH = "web_research"
    PLANNING     = "planning"
    GENERAL_CHAT = "general_chat"


class RiskLevel(str, Enum):
    LOW    = "low"
    MEDIUM = "medium"
    HIGH   = "high"


class ToolPolicy(str, Enum):
    NONE     = "none"
    ALLOWED  = "allowed"
    REQUIRED = "required"


class ResponseMode(str, Enum):
    NORMAL    = "normal"
    STREAMING = "streaming"
    JSON      = "json"


class IntentDecision(BaseModel):
    intent:           IntentType
    risk_level:       RiskLevel
    tool_policy:      ToolPolicy
    engineer_mode:    bool
    allowed_tools:    list[str]
    force_first_tool: bool
    max_tool_rounds:  int
    needs_web:        bool
    needs_exec:       bool
    should_stream:    bool
    response_mode:    ResponseMode


# ---------------------------------------------------------------------------
# Signal pattern banks
# ---------------------------------------------------------------------------

_CODE_SIGNALS = [
    r"\bfix\b", r"\bbug\b", r"\berror\b", r"\btraceback\b", r"\bexception\b",
    r"\bpatch\b", r"\brefactor\b", r"\bwhy (is|does|did|are)\b",
    r"\b(endpoint|router|migration|schema|model|column|table|index)\b",
    r"```", r"\.py\b", r"\.ts\b",
    r"\b(POST|GET|PUT|DELETE|PATCH)\b",
    r"\b[45][0-9]{2}\b",
    r"\b(fastapi|sqlalchemy|pydantic|alembic|uvicorn)\b",
]

_REPO_SIGNALS = [
    r"(what.{0,10}in|show me|read|look at|check).{0,30}(file|directory|folder|repo|codebase)",
    r"\bapp/\w+",
    r"(where is|where are|find|search).{0,40}(defined|imported|called|used)",
    r"how many (places|files|modules)",
    r"\bimport\b.{0,50}\bfrom\b",
    r"(list|show).{0,20}(files|modules|routes|endpoints)",
]

_DB_SIGNALS = [
    r"\b(SELECT|INSERT|UPDATE|DELETE|ALTER TABLE|CREATE TABLE|DROP)\b",
    r"\b(migration|postgres|pgvector|sqlalchemy|alembic)\b",
    r"\b(null value|NOT NULL|foreign key|primary key|index on)\b",
    r"\b(UndefinedColumn|IntegrityError|OperationalError|DataError)\b",
]

_WEB_SIGNALS = [
    r"(latest|current|recent|today.?s?|news|update)",
    r"(documentation|docs|api reference)",
    r"(look up|search for|find out|check online|google)",
    r"(what version|current release|latest release)",
]

_PLANNING_SIGNALS = [
    r"(should we|what do you think|best approach|recommend|plan|strategy|roadmap)",
    r"(architecture|design pattern|tradeoff|pros and cons)",
    r"(compare|vs\.?|versus|better option|which is better)",
]

_HIGH_RISK_SIGNALS = [
    r"\b(delete all|drop table|truncate|wipe|destroy)\b",
    r"\b(production|prod\b|live server)\b",
    r"irreversible|cannot be undone",
]

_MEDIUM_RISK_SIGNALS = [
    r"\b(deploy|alter table|update.*all)\b",
]


def _matches(text: str, patterns: list[str]) -> bool:
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def detect_intent(
    user_text: str,
    *,
    route_hint: Optional[str] = None,
) -> IntentDecision:
    """
    Classify a user message and return an IntentDecision.

    route_hint values:
      "engineer"  -- force engineer_mode + tool access regardless of text
      "chat"      -- force GENERAL_CHAT regardless of text
    """
    text = user_text

    if route_hint == "chat":
        return _general_chat()

    # Risk level
    if _matches(text, _HIGH_RISK_SIGNALS):
        risk = RiskLevel.HIGH
    elif _matches(text, _MEDIUM_RISK_SIGNALS + _CODE_SIGNALS + _DB_SIGNALS + _REPO_SIGNALS):
        risk = RiskLevel.MEDIUM
    else:
        risk = RiskLevel.LOW

    # Priority-ordered intent routing
    if route_hint == "engineer" or _matches(text, _REPO_SIGNALS):
        return IntentDecision(
            intent=IntentType.REPO_QA,
            risk_level=risk,
            tool_policy=ToolPolicy.REQUIRED,
            engineer_mode=True,
            allowed_tools=["read_file", "list_directory", "search_codebase"],
            force_first_tool=True,
            max_tool_rounds=5,
            needs_web=False,
            needs_exec=False,
            should_stream=False,
            response_mode=ResponseMode.NORMAL,
        )

    if _matches(text, _DB_SIGNALS):
        return IntentDecision(
            intent=IntentType.DB_QA,
            risk_level=risk,
            tool_policy=ToolPolicy.REQUIRED,
            engineer_mode=True,
            allowed_tools=["read_file", "query_database", "search_codebase"],
            force_first_tool=True,
            max_tool_rounds=4,
            needs_web=False,
            needs_exec=False,
            should_stream=False,
            response_mode=ResponseMode.NORMAL,
        )

    if _matches(text, _CODE_SIGNALS):
        return IntentDecision(
            intent=IntentType.CODE_ASSIST,
            risk_level=risk,
            tool_policy=ToolPolicy.ALLOWED,
            engineer_mode=True,
            allowed_tools=["read_file", "list_directory", "search_codebase"],
            force_first_tool=False,
            max_tool_rounds=5,
            needs_web=False,
            needs_exec=False,
            should_stream=False,
            response_mode=ResponseMode.NORMAL,
        )

    if _matches(text, _WEB_SIGNALS):
        return IntentDecision(
            intent=IntentType.WEB_RESEARCH,
            risk_level=risk,
            tool_policy=ToolPolicy.ALLOWED,
            engineer_mode=False,
            allowed_tools=["web_search", "fetch_url"],
            force_first_tool=False,
            max_tool_rounds=3,
            needs_web=True,
            needs_exec=False,
            should_stream=False,
            response_mode=ResponseMode.NORMAL,
        )

    if _matches(text, _PLANNING_SIGNALS):
        return IntentDecision(
            intent=IntentType.PLANNING,
            risk_level=risk,
            tool_policy=ToolPolicy.ALLOWED,
            engineer_mode=False,
            allowed_tools=["read_file", "search_codebase", "web_search"],
            force_first_tool=False,
            max_tool_rounds=3,
            needs_web=True,
            needs_exec=False,
            should_stream=False,
            response_mode=ResponseMode.NORMAL,
        )

    return _general_chat()


def _general_chat() -> IntentDecision:
    return IntentDecision(
        intent=IntentType.GENERAL_CHAT,
        risk_level=RiskLevel.LOW,
        tool_policy=ToolPolicy.NONE,
        engineer_mode=False,
        allowed_tools=[],
        force_first_tool=False,
        max_tool_rounds=0,
        needs_web=False,
        needs_exec=False,
        should_stream=False,
        response_mode=ResponseMode.NORMAL,
    )
