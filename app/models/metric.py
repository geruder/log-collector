import uuid
from datetime import datetime
from sqlalchemy import DateTime, Index, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class Metric(Base):
    __tablename__ = "metrics"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    device_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    metric_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        comment="cpu_usage, memory_usage, disk_io, vb."
    )
    value: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)
    unit: Mapped[str | None] = mapped_column(String(16), nullable=True)

    __table_args__ = (
        Index("ix_metrics_device_type_ts", "device_id", "metric_type", "timestamp"),
    )

    def __repr__(self) -> str:
        return f"<Metric {self.metric_type}={self.value}{self.unit or ''} from {self.device_id}>"