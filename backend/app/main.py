from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from arq import create_pool
from arq.connections import RedisSettings

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.db import engine, init_db
from app.core.logger import configure_logging, get_logger
from app.api.errors import register_error_handlers

logger = get_logger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    await init_db()
    app.state.redis = await create_pool(RedisSettings.from_dsn(settings.REDIS_URL))
    logger.info("API startup complete.")
    yield
    await app.state.redis.aclose()
    await engine.dispose()
    logger.info("API shutdown complete.")


_TAGS: list[dict] = [
    {
        "name": "auth",
        "description": "Register, log in, log out, and manage the current user session.",
    },
    {
        "name": "users",
        "description": "Current-user profile (me) and account management.",
    },
    {
        "name": "cvs",
        "description": (
            "Upload CVs (PDF/DOCX), list and download them, and delete them. "
            "Uploading triggers asynchronous text extraction and LLM profile parsing."
        ),
    },
    {
        "name": "searches",
        "description": (
            "Run a semantic job search against the ingested corpus: embed a query built "
            "from the selected CV + free-text prompt, vector-search 20 candidates, "
            "LLM-rerank into up to 10 explained matches, and persist the result."
        ),
    },
    {
        "name": "jobs",
        "description": (
            "Browse the ingested job corpus (paginated) and fetch a single posting, "
            "plus trigger an on-demand ingestion run (enqueued to the background worker)."
        ),
    },
]

app = FastAPI(
    title="Job Agent API",
    description=(
        "Backend for an automated job-discovery assistant. "
        "Ingests listings from Adzuna, Jooble, and Apify (Indeed/LinkedIn), "
        "embeds them with `text-embedding-3-small`, and matches them against "
        "uploaded CVs via pgvector similarity search + GPT-4o-mini reranking. "
        "Users supply the CV and a prompt; the API returns ranked apply-links."
    ),
    version="0.1.0",
    openapi_tags=_TAGS,
    lifespan=lifespan,
)

register_error_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,  # required so the browser sends/stores the auth cookie
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)


@app.get("/health")
def health():
    return {"status": "ok"}
