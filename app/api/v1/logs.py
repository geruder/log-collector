from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.crud import log as crud_log
from app.models.log import LogLevel
from app.schemas.log import (
    LogBulkCreate,
    LogCreate,
    LogResponse,
)

router = APIRouter(prefix="/logs", tags=["logs"])


@router.post(
    "",
    response_model=LogResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tek bir log kaydı oluştur",
)
async def create_log(
    log_in: LogCreate,
    db: AsyncSession = Depends(get_db),
) -> LogResponse:
    log = await crud_log.create_log(db, log_in)
    return log


@router.post(
    "/bulk",
    status_code=status.HTTP_201_CREATED,
    summary="Toplu log kaydı (max 1000 adet)",
)
async def create_logs_bulk(
    payload: LogBulkCreate,
    db: AsyncSession = Depends(get_db),
) -> dict:
    count = await crud_log.create_logs_bulk(db, payload.logs)
    return {"inserted": count}


@router.get(
    "/search",
    response_model=list[LogResponse],
    summary="Logları filtreleyerek listele",
)
async def search_logs(
    level: LogLevel | None = Query(default=None, description="Log seviyesi filtresi"),
    source: str | None = Query(default=None, description="Kaynak cihaz/servis adı"),
    start_date: datetime | None = Query(default=None, description="ISO 8601 formatında"),
    end_date: datetime | None = Query(default=None, description="ISO 8601 formatında"),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> list[LogResponse]:
    logs = await crud_log.search_logs(
        db,
        level=level,
        source=source,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )
    return logs


@router.get(
    "/{log_id}",
    response_model=LogResponse,
    summary="ID ile log getir",
)
async def get_log(
    log_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> LogResponse:
    log = await crud_log.get_log_by_id(db, log_id)
    if log is None:
        raise HTTPException(status_code=404, detail="Log not found")
    return log