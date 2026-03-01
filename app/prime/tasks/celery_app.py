# app/prime/tasks/celery_app.py
"""
PRIME Celery Application

Distributed task queue for long-running operations:
  - Research pipeline (plan → conduct → synthesize)
  - Corpus embedding (10k+ chunks)
  - Document ingestion (PDF, DOCX, audio transcription)

Architecture:
  Broker:  Redis (task queue)
  Backend: Redis (result storage)
  Workers: Separate processes via `celery -A app.prime.tasks.celery_app worker`

Task lifecycle:
  1. API endpoint creates task → returns task_id immediately
  2. Celery worker picks up task from Redis queue
  3. Task runs async, updates state (PENDING → STARTED → SUCCESS/FAILURE)
  4. Client polls GET /prime/tasks/status/{task_id} for progress

Configuration:
  CELERY_BROKER_URL   -- Redis connection (default: redis://localhost:6379/0)
  CELERY_RESULT_BACKEND -- Redis connection for results
"""
from __future__ import annotations

import os
from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "prime_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "app.prime.tasks.research_tasks",
        "app.prime.tasks.embed_tasks",
        "app.prime.tasks.ingest_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,        # 1 hour hard limit
    task_soft_time_limit=3300,   # 55 min soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)
