"""Shared test fixtures for the data layer.

Repository tests run against a *real* Postgres with pgvector (via Testcontainers),
because the whole point is exercising pgvector queries, the upsert constraint, and
the real types — a mock or SQLite wouldn't.

Driver note: asyncpg 0.31.0 has a bug on Python 3.14 Windows (SCRAM-SHA-256
auth fails in the C extension). Tests use psycopg3 (psycopg[binary]) as the
SQLAlchemy driver instead — the app still uses asyncpg in production.

psycopg3 requires SelectorEventLoop on Windows (ProactorEventLoop is not
supported). The _asyncio_loop_factory fixture below forces SelectorEventLoop
for all async tests; pytest-asyncio 1.x passes this factory to asyncio.Runner.
"""
import asyncio
import sys

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
def _asyncio_loop_factory():
    # psycopg3 requires SelectorEventLoop on Windows; return None elsewhere to let
    # pytest-asyncio pick the platform default.
    if sys.platform == "win32":
        return asyncio.SelectorEventLoop
    return None


@pytest.fixture(scope="session")
def pg_url() -> str:
    """Start one pgvector Postgres container for the whole test session.

    Sync fixture (Testcontainers is synchronous); yields a psycopg URL.
    """
    with PostgresContainer("pgvector/pgvector:pg16", driver="psycopg") as pg:
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


@pytest_asyncio.fixture
async def auth_client(pg_url):
    """httpx client bound to the app, with get_db overridden to a committing
    session on the test container. Fresh schema per test for isolation.
    httpx's cookie jar carries the auth cookie across requests automatically.
    """
    from httpx import ASGITransport, AsyncClient

    from app.api.deps import get_db
    from app.main import app

    engine = create_async_engine(pg_url)
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_db():
        async with factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def logged_in_client(auth_client):
    """auth_client with a registered and logged-in user.

    Use this when the test exercises a protected endpoint and needs a valid
    session cookie already set.  auth_client stays unauthenticated so that
    tests which verify 401 responses continue to work.
    """
    creds = {"email": "auth@test.io", "password": "supersecret123"}
    await auth_client.post("/api/v1/auth/register", json=creds)
    await auth_client.post(
        "/api/v1/auth/jwt/login",
        data={"username": creds["email"], "password": creds["password"]},
    )
    yield auth_client

@pytest_asyncio.fixture
async def cv_client(pg_url):
    """Authenticated httpx client with a per-test DB (committing) and a moto-backed
    S3 override, plus a registered+logged-in user (cookie set)."""
    from httpx import ASGITransport, AsyncClient

    from app.api.deps import get_db, get_s3
    from app.main import app

    engine = create_async_engine(pg_url)
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_db():
        async with factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    with mock_aws():
        cfg = settings.model_copy(
            update={"S3_ENDPOINT_URL": None, "S3_PUBLIC_ENDPOINT_URL": None, "S3_SSE": None}
        )
        boto3.client("s3", region_name=cfg.S3_REGION).create_bucket(Bucket=cfg.S3_BUCKET_NAME)
        test_s3 = S3(cfg.S3_BUCKET_NAME, cfg)

        from app.api.deps import get_arq_redis

        class _NoOpRedis:
            async def enqueue_job(self, name, *args, **kwargs):
                class _Job:
                    job_id = "noop"
                return _Job()

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_s3] = lambda: test_s3
        app.dependency_overrides[get_arq_redis] = lambda: _NoOpRedis()

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            creds = {"email": "cv@test.io", "password": "supersecret123"}
            await client.post("/api/v1/auth/register", json=creds)
            await client.post(
                "/api/v1/auth/jwt/login",
                data={"username": creds["email"], "password": creds["password"]},
            )
            yield client

        app.dependency_overrides.clear()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
