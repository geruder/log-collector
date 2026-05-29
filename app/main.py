from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.database import get_db
from app.core.exceptions import register_exception_handlers

settings = get_settings()

app = FastAPI(
    title="Log Collector API",
    description="Asenkron log ve metrik toplama servisi",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

register_exception_handlers(app)

# v1 router'ını /api/v1 öneki ile dahil et
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}


@app.get("/health/db", tags=["health"])
async def db_health(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT 1"))
    return {"db": "ok", "result": result.scalar()}