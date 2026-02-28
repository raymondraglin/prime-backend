from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.prime.context.database import async_session
from app.prime.goals.models import GoalPriority, GoalStatus, PrimeGoal

logger = logging.getLogger(__name__)


# ─── CREATE ───────────────────────────────────────────────────────────────────

async def create_goal(
    *,
    title: str,
    description: Optional[str] = None,
    priority: str = GoalPriority.medium,
    domain: Optional[str] = None,
    user_id: str = "raymond",
    session_id: Optional[str] = None,
    target_date: Optional[datetime] = None,
    linked_tasks: Optional[list[str]] = None,
    tags: Optional[list[str]] = None,
) -> dict[str, Any]:
    try:
        async with async_session() as db:
            goal = PrimeGoal(
                id=str(uuid4()),
                title=title,
                description=description,
                status=GoalStatus.active,
                priority=priority,
                domain=domain,
                user_id=user_id,
                session_id=session_id,
                target_date=target_date,
                progress=[],
                linked_tasks=linked_tasks or [],
                tags=tags or [],
            )
            db.add(goal)
            await db.commit()
            await db.refresh(goal)
            return {"ok": True, "goal": goal.to_dict()}
    except SQLAlchemyError as exc:
        logger.error("create_goal failed: %s", exc)
        return {"ok": False, "error": str(exc)}


# ─── READ ─────────────────────────────────────────────────────────────────────

async def get_goal(goal_id: str) -> dict[str, Any]:
    try:
        async with async_session() as db:
            result = await db.execute(
                select(PrimeGoal).where(PrimeGoal.id == goal_id)
            )
            goal = result.scalar_one_or_none()
            if not goal:
                return {"ok": False, "error": f"Goal {goal_id} not found"}
            return {"ok": True, "goal": goal.to_dict()}
    except SQLAlchemyError as exc:
        logger.error("get_goal failed: %s", exc)
        return {"ok": False, "error": str(exc)}


async def list_goals(
    *,
    user_id: str = "raymond",
    status: Optional[str] = None,
    domain: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 50,
) -> dict[str, Any]:
    try:
        async with async_session() as db:
            stmt = select(PrimeGoal).where(PrimeGoal.user_id == user_id)
            if status:
                stmt = stmt.where(PrimeGoal.status == status)
            if domain:
                stmt = stmt.where(PrimeGoal.domain == domain)
            if priority:
                stmt = stmt.where(PrimeGoal.priority == priority)
            stmt = stmt.order_by(PrimeGoal.created_at.desc()).limit(limit)
            result = await db.execute(stmt)
            goals = result.scalars().all()
            return {"ok": True, "goals": [g.to_dict() for g in goals], "count": len(goals)}
    except SQLAlchemyError as exc:
        logger.error("list_goals failed: %s", exc)
        return {"ok": False, "error": str(exc)}


async def get_active_goals(user_id: str = "raymond") -> dict[str, Any]:
    return await list_goals(user_id=user_id, status=GoalStatus.active)


# ─── UPDATE ───────────────────────────────────────────────────────────────────

async def update_goal(
    goal_id: str,
    *,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    domain: Optional[str] = None,
    target_date: Optional[datetime] = None,
    outcome: Optional[str] = None,
    linked_tasks: Optional[list[str]] = None,
    tags: Optional[list[str]] = None,
) -> dict[str, Any]:
    try:
        async with async_session() as db:
            result = await db.execute(
                select(PrimeGoal).where(PrimeGoal.id == goal_id)
            )
            goal = result.scalar_one_or_none()
            if not goal:
                return {"ok": False, "error": f"Goal {goal_id} not found"}

            if title is not None:        goal.title        = title
            if description is not None:  goal.description  = description
            if status is not None:       goal.status       = status
            if priority is not None:     goal.priority     = priority
            if domain is not None:       goal.domain       = domain
            if target_date is not None:  goal.target_date  = target_date
            if outcome is not None:      goal.outcome      = outcome
            if linked_tasks is not None: goal.linked_tasks = linked_tasks
            if tags is not None:         goal.tags         = tags

            goal.updated_at = datetime.now(timezone.utc)
            await db.commit()
            await db.refresh(goal)
            return {"ok": True, "goal": goal.to_dict()}
    except SQLAlchemyError as exc:
        logger.error("update_goal failed: %s", exc)
        return {"ok": False, "error": str(exc)}


async def add_progress_note(goal_id: str, *, note: str) -> dict[str, Any]:
    try:
        async with async_session() as db:
            result = await db.execute(
                select(PrimeGoal).where(PrimeGoal.id == goal_id)
            )
            goal = result.scalar_one_or_none()
            if not goal:
                return {"ok": False, "error": f"Goal {goal_id} not found"}

            entry = {"note": note, "timestamp": datetime.now(timezone.utc).isoformat()}
            progress = list(goal.progress or [])
            progress.append(entry)
            goal.progress   = progress
            goal.updated_at = datetime.now(timezone.utc)
            await db.commit()
            await db.refresh(goal)
            return {"ok": True, "goal": goal.to_dict()}
    except SQLAlchemyError as exc:
        logger.error("add_progress_note failed: %s", exc)
        return {"ok": False, "error": str(exc)}


async def complete_goal(goal_id: str, *, outcome: str) -> dict[str, Any]:
    return await update_goal(goal_id, status=GoalStatus.completed, outcome=outcome)


async def pause_goal(goal_id: str) -> dict[str, Any]:
    return await update_goal(goal_id, status=GoalStatus.paused)


async def resume_goal(goal_id: str) -> dict[str, Any]:
    return await update_goal(goal_id, status=GoalStatus.active)


async def abandon_goal(goal_id: str, *, reason: Optional[str] = None) -> dict[str, Any]:
    return await update_goal(goal_id, status=GoalStatus.abandoned, outcome=reason)


# ─── DELETE ───────────────────────────────────────────────────────────────────

async def delete_goal(goal_id: str) -> dict[str, Any]:
    try:
        async with async_session() as db:
            result = await db.execute(
                select(PrimeGoal).where(PrimeGoal.id == goal_id)
            )
            goal = result.scalar_one_or_none()
            if not goal:
                return {"ok": False, "error": f"Goal {goal_id} not found"}
            await db.delete(goal)
            await db.commit()
            return {"ok": True, "deleted": goal_id}
    except SQLAlchemyError as exc:
        logger.error("delete_goal failed: %s", exc)
        return {"ok": False, "error": str(exc)}
