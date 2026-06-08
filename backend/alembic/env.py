import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# pgvector types must be imported so autogenerate renders the Vector column
# correctly instead of emitting a broken definition.
from pgvector.sqlalchemy import Vector  # noqa: F401

from app.core.config import get_settings
from app.core.logger import get_logger
from app.models.base import Base
from app import models  # noqa: F401  populates Base.metadata with every table

config = context.config

# Alembic's own logging (migration progress) from the ini file.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

logger = get_logger("alembic.env")
settings = get_settings()

# Inject the real async URL; the placeholder in alembic.ini is never used.
config.set_main_option("sqlalchemy.url", settings.database_url)
logger.info("Running migrations against %s:%s/%s", settings.POSTGRES_HOST, settings.POSTGRES_PORT, settings.POSTGRES_DB)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Emit SQL to stdout without a DB connection (`alembic upgrade --sql`)."""
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations through the async engine via run_sync."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
