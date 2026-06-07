from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger("app.core.db")

engine = create_async_engine(
    settings.database_url,
    pool_size=10,
    max_overflow=5,
    pool_pre_ping=True,
)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def init_db() -> None:
    """Verify the database is reachable. Call once at API/worker startup."""
    logger.info("Initializing database connection...")
    try:
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
        logger.info("Database connection initialized successfully.")
    except Exception as e:
        logger.error("Failed to initialize database connection: %s", e)
        raise
