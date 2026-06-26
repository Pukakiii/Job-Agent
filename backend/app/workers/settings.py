import httpx
from arq import cron
from arq.connections import RedisSettings

from app.core.config import settings
from app.core.logger import configure_logging, get_logger
from app.integrations.ai_factory import get_chat_client, get_embedder
from app.integrations.s3 import S3
from app.workers.registry import build_sources
from app.workers.tasks import nightly_refresh, parse_cv, scrape_board

logger = get_logger("app.workers.settings")


async def startup(ctx) -> None:
    configure_logging()
    if settings.OPENAI_API_KEY:
        logger.info("AI provider: OpenAI (%s)", settings.OPENAI_CHAT_MODEL)
    else:
        logger.info("AI provider: Ollama at %s", settings.OLLAMA_BASE_URL)
    client = httpx.AsyncClient()
    ctx["http_client"] = client
    ctx["sources"] = build_sources(client, settings)
    ctx["embedder"] = get_embedder()
    ctx["openai"] = get_chat_client()
    s3 = S3(settings.S3_BUCKET_NAME, settings)
    await s3.ensure_bucket()
    ctx["s3"] = s3
    logger.info("Worker started with sources: %s", list(ctx["sources"]))


async def shutdown(ctx) -> None:
    await ctx["http_client"].aclose()


class WorkerSettings:
    # nightly_refresh is in functions (not just cron_jobs) so it can be
    # manually enqueued for an ad-hoc full refresh.
    functions = [scrape_board, nightly_refresh, parse_cv]
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    cron_jobs = [cron(nightly_refresh, hour=3, minute=0)]
    on_startup = startup
    on_shutdown = shutdown
