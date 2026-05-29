from datetime import datetime
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.crud import metric as crud_metric
from app.schemas.metric import MetricCreate, MetricResponse

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.post(
    "",
    response_model=MetricResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tek bir metrik kaydı oluştur",
)
async def create_metric(
    metric_in: MetricCreate,
    db: AsyncSession = Depends(get_db),
) -> MetricResponse:
    metric = await crud_metric.create_metric(db, metric_in)
    return metric


@router.get(
    "",
    response_model=list[MetricResponse],
    summary="Metrikleri filtreleyerek listele",
)
async def list_metrics(
    device_id: str | None = Query(default=None),
    metric_type: str | None = Query(default=None),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> list[MetricResponse]:
    return await crud_metric.search_metrics(
        db,
        device_id=device_id,
        metric_type=metric_type,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )