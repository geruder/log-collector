from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class MetricBase(BaseModel):
    device_id: str = Field(..., min_length=1, max_length=128, examples=["server-01"])
    metric_type: str = Field(..., min_length=1, max_length=64, examples=["cpu_usage"])
    value: float = Field(..., examples=[42.5])
    unit: str | None = Field(default=None, max_length=16, examples=["percent"])


class MetricCreate(MetricBase):
    timestamp: datetime | None = None


class MetricResponse(MetricBase):
    id: UUID
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class MetricSearchParams(BaseModel):
    device_id: str | None = None
    metric_type: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    limit: int = Field(default=50, ge=1, le=500)
    offset: int = Field(default=0, ge=0)