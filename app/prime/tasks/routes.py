# app/prime/tasks/routes.py
"""
PRIME Task Queue Endpoints

POST /prime/tasks/research
  Launch async research pipeline, return task_id.

POST /prime/tasks/embed/corpus
  Launch async corpus embedding, return task_id.

POST /prime/tasks/embed/file
  Launch async file embedding, return task_id.

GET  /prime/tasks/status/{task_id}
  Poll task status and progress.

GET  /prime/tasks/result/{task_id}
  Retrieve completed task result.

DELETE /prime/tasks/{task_id}
  Cancel or delete a task.

NOTE: These endpoints require Redis/Memurai + Celery worker running.
If Redis is unavailable, endpoints will return 503 Service Unavailable.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/prime/tasks", tags=["PRIME Tasks"])


class ResearchTaskRequest(BaseModel):
    query:   str
    depth:   str                = "standard"
    domain:  Optional[str]      = None
    context: dict               = Field(default_factory=dict)


class EmbedCorpusRequest(BaseModel):
    domain: Optional[str] = None


class EmbedFileRequest(BaseModel):
    file_path: str


class TaskResponse(BaseModel):
    task_id: str
    status:  str
    message: str


def _check_celery():
    """Raise 503 if Celery is unavailable."""
    try:
        from app.prime.tasks.celery_app import celery_app
        celery_app.control.inspect().stats()
        return celery_app
    except Exception as exc:
        raise HTTPException(
            503,
            f"Task queue unavailable. Ensure Redis/Memurai and Celery worker are running. Error: {exc}"
        ) from exc


@router.post("/research", response_model=TaskResponse)
async def launch_research_task(req: ResearchTaskRequest):
    """Launch async research pipeline."""
    _check_celery()
    from app.prime.tasks.research_tasks import run_research_async

    task = run_research_async.delay(
        query   = req.query,
        depth   = req.depth,
        domain  = req.domain,
        context = req.context,
    )

    return TaskResponse(
        task_id = task.id,
        status  = "PENDING",
        message = "Research task launched. Poll /prime/tasks/status/{task_id} for progress.",
    )


@router.post("/embed/corpus", response_model=TaskResponse)
async def launch_embed_corpus_task(req: EmbedCorpusRequest):
    """Launch async corpus embedding."""
    _check_celery()
    from app.prime.tasks.embed_tasks import embed_corpus_async

    task = embed_corpus_async.delay(domain=req.domain)

    return TaskResponse(
        task_id = task.id,
        status  = "PENDING",
        message = "Corpus embedding task launched.",
    )


@router.post("/embed/file", response_model=TaskResponse)
async def launch_embed_file_task(req: EmbedFileRequest):
    """Launch async file embedding."""
    _check_celery()
    from app.prime.tasks.embed_tasks import embed_file_async

    task = embed_file_async.delay(file_path=req.file_path)

    return TaskResponse(
        task_id = task.id,
        status  = "PENDING",
        message = "File embedding task launched.",
    )


@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """Poll task status and progress."""
    celery_app = _check_celery()
    from celery.result import AsyncResult
    
    result = AsyncResult(task_id, app=celery_app)

    response = {
        "task_id": task_id,
        "status":  result.state,
    }

    if result.state == "PENDING":
        response["message"] = "Task is waiting in queue."
    elif result.state == "STARTED":
        response["message"] = "Task is running."
        response["meta"]    = result.info or {}
    elif result.state == "SUCCESS":
        response["message"] = "Task completed successfully."
        response["result"]  = result.result
    elif result.state == "FAILURE":
        response["message"] = "Task failed."
        response["error"]   = str(result.info)
    else:
        response["message"] = f"Unknown state: {result.state}"

    return response


@router.get("/result/{task_id}")
async def get_task_result(task_id: str):
    """Retrieve completed task result."""
    celery_app = _check_celery()
    from celery.result import AsyncResult
    
    result = AsyncResult(task_id, app=celery_app)

    if result.state != "SUCCESS":
        raise HTTPException(400, f"Task not complete. Status: {result.state}")

    return {
        "task_id": task_id,
        "status":  result.state,
        "result":  result.result,
    }


@router.delete("/{task_id}")
async def cancel_task(task_id: str):
    """Cancel or delete a task."""
    celery_app = _check_celery()
    from celery.result import AsyncResult
    
    result = AsyncResult(task_id, app=celery_app)
    result.revoke(terminate=True)

    return {
        "task_id": task_id,
        "message": "Task cancelled.",
    }
