from fastapi import FastAPI

from app.api.routes import router as api_router

app = FastAPI()

# Single unified router that already includes math, philosophy, reasoning, etc.
app.include_router(api_router)

