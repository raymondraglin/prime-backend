from dotenv import load_dotenv
load_dotenv()

import json
import logging
import os
import pathlib
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router
from app.prime.context.endpoints import router as prime_context_router
from app.core.auth_endpoints import router as auth_router
from app.prime.api.chat import router as prime_chat_router
from app.prime.api.genius import router as prime_genius_router
from app.prime.api.repo import router as prime_repo_router
from app.prime.ingest.router import router as prime_ingest_router
from app.prime.goals.routes import router as goals_router
from app.prime.agent.routes import router as prime_agent_router

logger = logging.getLogger("prime.startup")

# ---------------------------------------------------------------------------
# Startup assertions -- fail loud and early, never silently
# ---------------------------------------------------------------------------
_REQUIRED_ENV: list[tuple[str, str]] = [
    ("SECRET_KEY",      "JWT signing key -- auth will fail at runtime without this"),
    ("OPENAI_API_KEY",  "OpenAI API key -- all LLM calls will fail without this"),
    ("DATABASE_URL",    "Postgres connection string -- all DB operations will fail without this"),
]

def _assert_env() -> None:
    missing = [
        (key, hint)
        for key, hint in _REQUIRED_ENV
        if not os.getenv(key)
    ]
    if missing:
        lines = ["\n[PRIME] FATAL: missing required environment variables:\n"]
        for key, hint in missing:
            lines.append(f"  {key}\n    \u2192 {hint}")
        lines.append("\nSet these in your .env file (see .env.example) and restart.\n")
        logger.critical("\n".join(lines))
        sys.exit(1)

_assert_env()

# ---------------------------------------------------------------------------

app = FastAPI(title="PRIME", version="1.0.0")

origins = [
    "http://localhost:3000",
    "https://localhost:3000",
    "https://*.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def run_migrations():
    """Create any missing tables on startup so the app is self-healing."""
    try:
        import sqlalchemy
        db_url = os.getenv("DATABASE_URL", "")
        sync_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
        engine = sqlalchemy.create_engine(sync_url)
        with engine.connect() as conn:
            conn.execute(sqlalchemy.text("""
                CREATE TABLE IF NOT EXISTS prime_goals (
                    id           VARCHAR(36)  PRIMARY KEY,
                    title        VARCHAR(255) NOT NULL,
                    description  TEXT,
                    status       VARCHAR(50)  NOT NULL DEFAULT 'active',
                    priority     VARCHAR(50)  NOT NULL DEFAULT 'medium',
                    domain       VARCHAR(100),
                    user_id      VARCHAR(100) NOT NULL DEFAULT 'raymond',
                    session_id   VARCHAR(255),
                    target_date  TIMESTAMPTZ,
                    outcome      TEXT,
                    progress     JSONB        NOT NULL DEFAULT '[]'::jsonb,
                    linked_tasks JSONB        NOT NULL DEFAULT '[]'::jsonb,
                    tags         JSONB        NOT NULL DEFAULT '[]'::jsonb,
                    created_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
                    updated_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW()
                )
            """))
            conn.commit()
        logger.info("[startup] prime_goals table ready.")
    except Exception as exc:
        logger.warning("[startup] Migration warning: %s", exc)


def _db_ping() -> str:
    """Returns 'ok' if DB is reachable, 'unreachable' otherwise."""
    try:
        import sqlalchemy
        db_url = os.getenv("DATABASE_URL", "")
        sync_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
        engine = sqlalchemy.create_engine(sync_url, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.execute(sqlalchemy.text("SELECT 1"))
        return "ok"
    except Exception:
        return "unreachable"


def _last_eval() -> dict | None:
    """Returns pass stats from the most recent eval results file."""
    try:
        results_dir = pathlib.Path("app/prime/evals/results")
        files = sorted(results_dir.glob("*.json"))
        if not files:
            return None
        data = json.loads(files[-1].read_text(encoding="utf-8"))
        passed  = data.get("passed", 0)
        scored  = data.get("scored", 0)
        skipped = data.get("skipped", 0)
        pct     = round(passed / scored * 100, 1) if scored else 0.0
        return {
            "file":      files[-1].name,
            "passed":    passed,
            "scored":    scored,
            "skipped":   skipped,
            "score_pct": pct,
        }
    except Exception:
        return None


@app.get("/health")
def health():
    db     = _db_ping()
    evals  = _last_eval()
    status = "ok" if db == "ok" else "degraded"
    return {
        "status":      status,
        "version":     "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "db":          db,
        "last_eval":   evals,
    }


app.include_router(auth_router)
app.include_router(api_router)
app.include_router(prime_context_router)
app.include_router(prime_chat_router)    # POST /prime/chat/
app.include_router(prime_genius_router)  # POST /prime/ask, /prime/debug, /prime/generate, etc.
app.include_router(prime_repo_router)    # POST /prime/repo/index, /prime/repo/ask, etc.
app.include_router(prime_ingest_router)  # POST /prime/ingest/image/, /pdf/, /audio/, /document/
app.include_router(goals_router)         # POST/GET /prime/goals/
app.include_router(prime_agent_router)   # POST /prime/agent/chat, /prime/agent/stream
