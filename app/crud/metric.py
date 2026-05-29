from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.metric import Metric
from app.schemas.metric import MetricCreate


async def create_metric(db: AsyncSession, metric_in: MetricCreate) -> Metric:
    data = metric_in.model_dump(exclude_none=True)
    metric = Metric(**data)
    db.add(metric)
    await db.commit()
    await db.refresh(metric)
    return metric


async def search_metrics(
    db: AsyncSession,
    device_id: str | None = None,
    metric_type: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Metric]:
    stmt = select(Metric)

    if device_id is not None:
        stmt = stmt.where(Metric.device_id == device_id)
    if metric_type is not None:
        stmt = stmt.where(Metric.metric_type == metric_type)
    if start_date is not None:
        stmt = stmt.where(Metric.timestamp >= start_date)
    if end_date is not None:
        stmt = stmt.where(Metric.timestamp <= end_date)

    stmt = stmt.order_by(Metric.timestamp.desc()).limit(limit).offset(offset)

    result = await db.execute(stmt)
    return list(result.scalars().all())