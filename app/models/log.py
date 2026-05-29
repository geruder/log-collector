import enum
import uuid
from datetime import datetime
from sqlalchemy import DateTime, Enum, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class LogLevel(str, enum.Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Log(Base):
    __tablename__ = "logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,                # tarihe göre filtreleme hızlı olsun
    )
    level: Mapped[LogLevel] = mapped_column(
        Enum(LogLevel, name="log_level_enum"),
        nullable=False,
        index=True,                # level'a göre filtreleme hızlı olsun
    )
    source: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    log_metadata: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Esnek ek veri - cihaz bilgisi, trace_id, vb."
    )

    # Composite index - sık beraber filtrelenen alanlar
    __table_args__ = (
        Index("ix_logs_timestamp_level", "timestamp", "level"),
    )

    def __repr__(self) -> str:
        return f"<Log {self.level.value} from {self.source} at {self.timestamp}>"