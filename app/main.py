from dotenv import load_dotenv
load_dotenv()

import logging
import os

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

logger = logging.getLogger("prime.startup")

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
        # SQLAlchemy sync engine needs postgresql://, not postgresql+asyncpg://
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


@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(auth_router)
app.include_router(api_router)
app.include_router(prime_context_router)
app.include_router(prime_chat_router)   # POST /prime/chat/
app.include_router(prime_genius_router) # POST /prime/ask, /prime/debug, /prime/generate, etc.
app.include_router(prime_repo_router)   # POST /prime/repo/index, /prime/repo/ask, etc.
app.include_router(prime_ingest_router) # POST /prime/ingest/image/, /pdf/, /audio/, /document/
app.include_router(goals_router)
