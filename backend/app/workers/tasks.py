from arq.connections import ArqRedis

from app.core.config import settings
from app.core.db import async_session_factory
from app.core.logger import get_logger
from app.repositories.job_repo import JobRepository
from app.services.ingestion_service import IngestionService

logger = get_logger("app.workers.tasks")


async def scrape_board(
    ctx,
    query: str,
    location: str | None = None,
    sources: list[str] | None = None,
) -> int:
    """One task = one transaction. Sources + embedder live in ctx (set by startup)."""
    async with async_session_factory() as session:
        service = IngestionService(ctx["sources"], ctx["embedder"], JobRepository(session))
        count = await service.run(query, location, sources)
        await session.commit()
        return count


async def nightly_refresh(ctx) -> int:
    """Cron entrypoint: ingest all default queries across all enabled sources."""
    total = 0
    for query in settings.INGEST_DEFAULT_QUERIES:
        total += await scrape_board(ctx, query)
    return total


async def enqueue_scrape(
    redis: ArqRedis,
    query: str,
    location: str | None = None,
    sources: list[str] | None = None,
) -> str:
    """Enqueue an on-demand scrape job. Returns the ARQ job id."""
    return await redis.enqueue_job("scrape_board", query, location=location, sources=sources)
