from __future__ import annotations

from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="Corvus MFG Daily Risk Brief",
    description="Lean manufacturing production-risk brief demo.",
    version="0.1.0",
)
app.include_router(router)
