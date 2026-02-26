from fastapi import FastAPI

from app.api.routes import router as api_router

app = FastAPI(
    title="PRIME Control Center",
    version="0.1.0",
    description="Private backend for Prime Reasoning Intelligence & Management Engine.",
)

app.include_router(api_router, prefix="/api")


@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "ok", "service": "prime-backend"}
