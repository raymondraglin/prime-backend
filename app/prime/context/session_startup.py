from __future__ import annotations

import logging
from typing import Any, Optional

from app.prime.goals.store import get_active_goals

logger = logging.getLogger(__name__)

_PRIORITY_EMOJI = {"high": "🔴", "medium": "🟡", "low": "🟢"}


def _format_goal(goal: dict[str, Any]) -> str:
    emoji    = _PRIORITY_EMOJI.get(goal.get("priority", "medium"), "🟡")
    title    = goal.get("title", "Untitled")
    domain   = goal.get("domain") or "general"
    gid      = goal.get("id", "")
    lines = [f"{emoji} [{domain.upper()}] {title}  (goal_id: {gid})"]
    desc     = goal.get("description") or ""
    progress = goal.get("progress") or []
    tasks    = goal.get("linked_tasks") or []

    lines = [f"{emoji} [{domain.upper()}] {title}  (id: {gid}...)"]
    if desc:
        lines.append(f"   Goal: {desc}")
    if tasks:
        lines.append(f"   Tasks: {', '.join(tasks)}")
    if progress:
        last = progress[-1]
        lines.append(f"   Last update: {last.get('note', '')}  ({last.get('timestamp', '')[:10]})")
    return "\n".join(lines)


async def build_session_context(user_id: str = "raymond") -> str:
    try:
        result = await get_active_goals(user_id=user_id)
        if not result.get("ok") or not result.get("goals"):
            return ""

        goals = result["goals"]
        count = len(goals)
        header = (
            f"── ACTIVE GOALS ({count}) ─────────────────────────────\n"
            "You have the following open goals. Resume them naturally during this session.\n"
        )
        body = "\n\n".join(_format_goal(g) for g in goals)
        footer = "\n─────────────────────────────────────────────────────"
        return f"\n{header}\n{body}{footer}\n"

    except Exception as exc:
        logger.warning("build_session_context failed: %s", exc)
        return ""


async def get_session_prime_context(
    *,
    user_id: str = "raymond",
    extra_context: Optional[str] = None,
) -> dict[str, Any]:
    goal_block = await build_session_context(user_id=user_id)

    # ADD: also pull raw goals for the hook
    raw_result  = await get_active_goals(user_id=user_id)
    raw_goals   = raw_result.get("goals", []) if raw_result.get("ok") else []

    sections: list[str] = []
    if goal_block:
        sections.append(goal_block)
    if extra_context:
        sections.append(extra_context)

    return {
        "has_goals":    bool(goal_block),
        "goal_context": goal_block,
        "goals_raw":    raw_goals,           # ← NEW
        "full_context": "\n".join(sections),
    }

