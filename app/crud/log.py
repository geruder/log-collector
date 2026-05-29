from datetime import datetime
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.log import Log, LogLevel
from app.schemas.log import LogCreate


async def create_log(db: AsyncSession, log_in: LogCreate) -> Log:
    """Tek bir log kaydı oluştur."""
    data = log_in.model_dump(exclude_none=True)
    log = Log(**data)
    db.add(log)
    await db.commit()
    await db.refresh(log)  # server-side default'ları (id, timestamp) çek
    return log


async def create_logs_bulk(db: AsyncSession, logs_in: list[LogCreate]) -> int:
    """Birden fazla log'u tek transaction'da yaz - performans avantajı."""
    logs = [Log(**log.model_dump(exclude_none=True)) for log in logs_in]
    db.add_all(logs)
    await db.commit()
    return len(logs)


async def search_logs(
    db: AsyncSession,
    level: LogLevel | None = None,
    source: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Log]:
    """Filtreli log arama."""
    stmt = select(Log)

    if level is not None:
        stmt = stmt.where(Log.level == level)
    if source is not None:
        stmt = stmt.where(Log.source == source)
    if start_date is not None:
        stmt = stmt.where(Log.timestamp >= start_date)
    if end_date is not None:
        stmt = stmt.where(Log.timestamp <= end_date)

    stmt = stmt.order_by(Log.timestamp.desc()).limit(limit).offset(offset)

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_log_by_id(db: AsyncSession, log_id: UUID) -> Log | None:
    result = await db.execute(select(Log).where(Log.id == log_id))
    return result.scalar_one_or_none()