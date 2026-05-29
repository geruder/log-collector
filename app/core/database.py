from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.core.config import get_settings

settings = get_settings()

# Async engine - asyncpg driver kullanıyor
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,  # debug=True iken SQL sorgularını loglar
    pool_size=10,  # eşzamanlı bağlantı havuzu
    max_overflow=20,  # ihtiyaç halinde ek bağlantı
    pool_pre_ping=True,  # ölü bağlantıları otomatik tespit et
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # commit sonrası ORM objeleri lazy-load yapmasın
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI Depends ile inject edilecek session dependency.

    Her request için yeni session açar, request bitince kapatır.
    Exception olursa otomatik rollback yapar.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()