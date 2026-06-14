from datetime import timedelta
from uuid import UUID

from arq.connections import ArqRedis

from app.core.config import settings
from app.core.db import async_session_factory
from app.core.logger import get_logger
from app.integrations.openai_client import OpenAIClient  # noqa: F401  (referenced via ctx)
from app.integrations.s3 import S3  # noqa: F401  (referenced via ctx)
from app.repositories.cv_repo import CVRepository
from app.repositories.job_repo import JobRepository
from app.services.cv_parsing_service import CVParsingService
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
    job = await redis.enqueue_job("scrape_board", query, location=location, sources=sources)
    return job.job_id


async def parse_cv(ctx, cv_id: str) -> None:
    """Parse an uploaded CV off-request. Tolerant of a not-yet-committed row: if the
    CV isn't visible yet, CVNotFound propagates and ARQ retries the job."""
    async with async_session_factory() as session:
        service = CVParsingService(CVRepository(session), ctx["s3"], ctx["openai"])
        await service.run(UUID(cv_id))
        await session.commit()


async def enqueue_parse_cv(redis: ArqRedis, cv_id: str) -> str:
    """Enqueue CV parsing, deferred so the upload request's commit lands first."""
    job = await redis.enqueue_job("parse_cv", cv_id, _defer_by=timedelta(seconds=2))
    return job.job_id
