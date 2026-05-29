from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from app.models.log import LogLevel


class LogBase(BaseModel):
    """Ortak alanlar - hem create hem response burada."""
    level: LogLevel
    source: str = Field(..., min_length=1, max_length=255, examples=["sensor-01"])
    message: str = Field(..., min_length=1, examples=["Temperature exceeded threshold"])
    log_metadata: dict[str, Any] | None = Field(
        default=None,
        examples=[{"device_ip": "192.168.1.10", "trace_id": "abc-123"}],
    )


class LogCreate(LogBase):
    """POST isteğinde gelecek body."""
    timestamp: datetime | None = Field(
        default=None,
        description="Verilmezse server şimdiki zamanı kullanır."
    )


class LogResponse(LogBase):
    """API'den dönen log objesi."""
    id: UUID
    timestamp: datetime

    # ORM objesinden Pydantic'e dönüşüme izin ver
    model_config = ConfigDict(from_attributes=True)


class LogBulkCreate(BaseModel):
    """Toplu insert için."""
    logs: list[LogCreate] = Field(..., min_length=1, max_length=1000)


class LogSearchParams(BaseModel):
    """GET /logs/search için query parametreleri."""
    level: LogLevel | None = None
    source: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    limit: int = Field(default=50, ge=1, le=500)
    offset: int = Field(default=0, ge=0)    