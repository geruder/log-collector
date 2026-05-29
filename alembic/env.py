import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# --- Settings ve modelleri import et ---
from app.core.config import get_settings
from app.models.base import Base
# Modelleri import etmek autogenerate için ŞART — yoksa Alembic onları görmez
from app.models.log import Log  # noqa: F401
from app.models.metric import Metric  # noqa: F401

config = context.config

# Settings'ten gelen URL'yi Alembic'e ver
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Autogenerate'in karşılaştıracağı şema
target_metadata = Base.metadata