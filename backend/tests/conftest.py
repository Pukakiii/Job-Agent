"""Shared test fixtures for the data layer.

Repository tests run against a *real* Postgres with pgvector (via Testcontainers),
because the whole point is exercising pgvector queries, the upsert constraint, and
the real types — a mock or SQLite wouldn't.
"""
import boto3
import pytest
import pytest_asyncio
from moto import mock_aws
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from app.core.config import settings
from app.integrations.s3 import S3
from app.models import Base


@pytest.fixture(scope="session")
def pg_url() -> str:
    """Start one pgvector Postgres container for the whole test session.

    Sync fixture (Testcontainers is synchronous); yields an asyncpg URL.
    """
    with PostgresContainer("pgvector/pgvector:pg16", driver="asyncpg") as pg:
        yield pg.get_connection_url()


@pytest_asyncio.fixture
async def db(pg_url):
    """A rolled-back AsyncSession per test.

    Schema is created once (CREATE EXTENSION + create_all are idempotent). The
    session never commits and is rolled back at teardown, so each test sees an
    empty schema — clean isolation without truncating tables.
    """
    engine = create_async_engine(pg_url)
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session
        await session.rollback()

    await engine.dispose()


@pytest.fixture
def s3() -> S3:
    """An S3 wrapper backed by moto's in-memory mock (no real AWS/MinIO).

    Endpoint is forced to None so moto intercepts; SSE off so no KMS is needed.
    """
    with mock_aws():
        cfg = settings.model_copy(
            update={"S3_ENDPOINT_URL": None, "S3_PUBLIC_ENDPOINT_URL": None, "S3_SSE": None}
        )
        boto3.client("s3", region_name=cfg.S3_REGION).create_bucket(Bucket=cfg.S3_BUCKET_NAME)
        yield S3(cfg.S3_BUCKET_NAME, cfg)
