from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.prime.goals.schemas import (
    GoalAbandonRequest,
    GoalCompleteRequest,
    GoalCreateRequest,
    GoalDeleteResponse,
    GoalListResponse,
    GoalProgressRequest,
    GoalResponse,
    GoalUpdateRequest,
)
from app.prime.goals.store import (
    abandon_goal,
    add_progress_note,
    complete_goal,
    create_goal,
    delete_goal,
    get_active_goals,
    get_goal,
    list_goals,
    pause_goal,
    resume_goal,
    update_goal,
)

router = APIRouter(prefix="/prime/goals", tags=["prime-goals"])


# ─── CREATE ───────────────────────────────────────────────────────────────────

@router.post("", response_model=GoalResponse, summary="Create Goal")
async def create_goal_endpoint(body: GoalCreateRequest) -> GoalResponse:
    result = await create_goal(
        title=body.title,
        description=body.description,
        priority=body.priority,
        domain=body.domain,
        session_id=body.session_id,
        target_date=body.target_date,
        linked_tasks=body.linked_tasks,
        tags=body.tags,
    )
    if not result["ok"]:
        raise HTTPException(status_code=500, detail=result.get("error"))
    return GoalResponse(**result)


# ─── READ ─────────────────────────────────────────────────────────────────────

@router.get("/active", response_model=GoalListResponse, summary="List Active Goals")
async def list_active_goals_endpoint(
    user_id: str = Query("raymond"),
) -> GoalListResponse:
    result = await get_active_goals(user_id=user_id)
    if not result["ok"]:
        raise HTTPException(status_code=500, detail=result.get("error"))
    return GoalListResponse(**result)


@router.get("", response_model=GoalListResponse, summary="List Goals")
async def list_goals_endpoint(
    user_id:  str            = Query("raymond"),
    status:   Optional[str] = Query(None),
    domain:   Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    limit:    int            = Query(50, ge=1, le=200),
) -> GoalListResponse:
    result = await list_goals(
        user_id=user_id,
        status=status,
        domain=domain,
        priority=priority,
        limit=limit,
    )
    if not result["ok"]:
        raise HTTPException(status_code=500, detail=result.get("error"))
    return GoalListResponse(**result)


@router.get("/{goal_id}", response_model=GoalResponse, summary="Get Goal")
async def get_goal_endpoint(goal_id: str) -> GoalResponse:
    result = await get_goal(goal_id)
    if not result["ok"]:
        raise HTTPException(status_code=404, detail=result.get("error"))
    return GoalResponse(**result)


# ─── UPDATE ───────────────────────────────────────────────────────────────────

@router.patch("/{goal_id}", response_model=GoalResponse, summary="Update Goal")
async def update_goal_endpoint(goal_id: str, body: GoalUpdateRequest) -> GoalResponse:
    result = await update_goal(
        goal_id,
        title=body.title,
        description=body.description,
        status=body.status,
        priority=body.priority,
        domain=body.domain,
        target_date=body.target_date,
        outcome=body.outcome,
        linked_tasks=body.linked_tasks,
        tags=body.tags,
    )
    if not result["ok"]:
        raise HTTPException(status_code=404, detail=result.get("error"))
    return GoalResponse(**result)


@router.post("/{goal_id}/progress", response_model=GoalResponse, summary="Add Progress Note")
async def add_progress_endpoint(goal_id: str, body: GoalProgressRequest) -> GoalResponse:
    result = await add_progress_note(goal_id, note=body.note)
    if not result["ok"]:
        raise HTTPException(status_code=404, detail=result.get("error"))
    return GoalResponse(**result)


@router.post("/{goal_id}/complete", response_model=GoalResponse, summary="Complete Goal")
async def complete_goal_endpoint(goal_id: str, body: GoalCompleteRequest) -> GoalResponse:
    result = await complete_goal(goal_id, outcome=body.outcome)
    if not result["ok"]:
        raise HTTPException(status_code=404, detail=result.get("error"))
    return GoalResponse(**result)


@router.post("/{goal_id}/pause", response_model=GoalResponse, summary="Pause Goal")
async def pause_goal_endpoint(goal_id: str) -> GoalResponse:
    result = await pause_goal(goal_id)
    if not result["ok"]:
        raise HTTPException(status_code=404, detail=result.get("error"))
    return GoalResponse(**result)


@router.post("/{goal_id}/resume", response_model=GoalResponse, summary="Resume Goal")
async def resume_goal_endpoint(goal_id: str) -> GoalResponse:
    result = await resume_goal(goal_id)
    if not result["ok"]:
        raise HTTPException(status_code=404, detail=result.get("error"))
    return GoalResponse(**result)


@router.post("/{goal_id}/abandon", response_model=GoalResponse, summary="Abandon Goal")
async def abandon_goal_endpoint(goal_id: str, body: GoalAbandonRequest) -> GoalResponse:
    result = await abandon_goal(goal_id, reason=body.reason)
    if not result["ok"]:
        raise HTTPException(status_code=404, detail=result.get("error"))
    return GoalResponse(**result)


# ─── DELETE ───────────────────────────────────────────────────────────────────

@router.delete("/{goal_id}", response_model=GoalDeleteResponse, summary="Delete Goal")
async def delete_goal_endpoint(goal_id: str) -> GoalDeleteResponse:
    result = await delete_goal(goal_id)
    if not result["ok"]:
        raise HTTPException(status_code=404, detail=result.get("error"))
    return GoalDeleteResponse(**result)
