from dotenv import load_dotenv
load_dotenv()

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

app = FastAPI(title="PRIME", version="1.0.0")

# Base origins always allowed
_base_origins = [
    "http://localhost:3000",
    "https://localhost:3000",
]

# Additional origins injected via environment variable (comma-separated)
_extra_raw = os.getenv("ALLOWED_ORIGINS", "")
_extra_origins = [o.strip() for o in _extra_raw.split(",") if o.strip()]

origins = _base_origins + _extra_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "PRIME", "version": "1.0.0"}


app.include_router(auth_router)
app.include_router(api_router)
app.include_router(prime_context_router)
app.include_router(prime_chat_router)    # POST /prime/chat/
app.include_router(prime_genius_router)  # POST /prime/ask, /prime/debug, /prime/generate, etc.
app.include_router(prime_repo_router)    # POST /prime/repo/index, /prime/repo/ask, etc.
app.include_router(prime_ingest_router)  # POST /prime/ingest/image/, /pdf/, /audio/, /document/
app.include_router(goals_router)
