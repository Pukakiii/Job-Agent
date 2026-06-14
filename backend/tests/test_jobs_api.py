"""HTTP API tests for /api/v1/jobs endpoints.

Driven by strict TDD: each test was written before the corresponding
production code existed, then production code was written to make it pass.
"""
import uuid

import pytest
from pydantic import ValidationError
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.deps import get_arq_redis
from app.main import app
from app.models.job import Job
from app.schemas.job import IngestRequest


# ---------------------------------------------------------------------------
# Auth guard tests — no login needed, just the unauthenticated client
# ---------------------------------------------------------------------------


async def test_list_jobs_requires_auth(auth_client):
    resp = await auth_client.get("/api/v1/jobs")
    assert resp.status_code == 401


async def test_get_job_requires_auth(auth_client):
    resp = await auth_client.get(f"/api/v1/jobs/{uuid.uuid4()}")
    assert resp.status_code == 401


async def test_ingest_requires_auth(auth_client):
    resp = await auth_client.post("/api/v1/jobs/ingest", json={"query": "x"})
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Domain error tests — need an authenticated session
# ---------------------------------------------------------------------------


async def test_get_job_returns_404_for_missing(logged_in_client):
    resp = await logged_in_client.get(f"/api/v1/jobs/{uuid.uuid4()}")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "job_not_found"


# ---------------------------------------------------------------------------
# Validation tests
# ---------------------------------------------------------------------------
# FastAPI resolves route dependencies before validating the request body, so
# get_arq_redis (which reads app.state.redis) must be overridden here too —
# otherwise the test crashes on State.redis before the 422 can be produced.


class _NoOpRedis:
    async def enqueue_job(self, name, *args, **kwargs):
        class _Job:
            job_id = "noop"

        return _Job()


async def test_ingest_validation_rejects_missing_query(logged_in_client):
    app.dependency_overrides[get_arq_redis] = lambda: _NoOpRedis()
    try:
        resp = await logged_in_client.post("/api/v1/jobs/ingest", json={})
        assert resp.status_code == 422
    finally:
        app.dependency_overrides.pop(get_arq_redis, None)


async def test_ingest_validation_rejects_empty_query(logged_in_client):
    app.dependency_overrides[get_arq_redis] = lambda: _NoOpRedis()
    try:
        resp = await logged_in_client.post("/api/v1/jobs/ingest", json={"query": ""})
        assert resp.status_code == 422
    finally:
        app.dependency_overrides.pop(get_arq_redis, None)


# ---------------------------------------------------------------------------
# Ingest endpoint — enqueues via ARQ, returns 202
# ---------------------------------------------------------------------------


async def test_ingest_returns_202_and_job_id(logged_in_client):
    app.dependency_overrides[get_arq_redis] = lambda: _NoOpRedis()
    try:
        resp = await logged_in_client.post(
            "/api/v1/jobs/ingest",
            json={"query": "python", "location": "berlin"},
        )
        assert resp.status_code == 202
        body = resp.json()
        assert body["job_id"] == "noop"
        assert body["status"] == "queued"
    finally:
        app.dependency_overrides.pop(get_arq_redis, None)


# ---------------------------------------------------------------------------
# List jobs — seeds the shared DB, then verifies the lean JobRead shape
# ---------------------------------------------------------------------------


async def test_list_jobs_returns_seeded_jobs(logged_in_client, pg_url):
    # Seed a job directly into the shared test DB so it's visible to the app.
    engine = create_async_engine(pg_url)
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        from app.models import Base
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        job = Job(
            source="test_source",
            source_job_id="test-123",
            content_hash="abc123",
            title="Senior Python Engineer",
            company="Acme Corp",
            location="Berlin",
            url="https://example.com/jobs/1",
            description="A great Python role.",
            embedding=[0.0] * 768,
        )
        session.add(job)
        await session.commit()

    await engine.dispose()

    resp = await logged_in_client.get("/api/v1/jobs")
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert len(body) >= 1

    # Find our seeded job
    titles = [j["title"] for j in body]
    assert "Senior Python Engineer" in titles

    seeded = next(j for j in body if j["title"] == "Senior Python Engineer")
    assert seeded["url"] == "https://example.com/jobs/1"

    # Lean shape: no description or embedding exposed
    assert "description" not in seeded
    assert "embedding" not in seeded


async def test_get_job_returns_detail_shape(logged_in_client, pg_url):
    # Seed a job, capture its id, then fetch the single-job detail view over HTTP.
    engine = create_async_engine(pg_url)
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        from app.models import Base

        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        job = Job(
            source="adzuna",
            source_job_id="detail-1",
            content_hash="hash-detail-1",
            title="Backend Engineer",
            company="Globex",
            location="Remote",
            url="https://example.com/jobs/detail-1",
            description="Work on the ingestion pipeline.",
            embedding=[0.0] * 768,
        )
        session.add(job)
        await session.commit()
        job_id = job.id  # expire_on_commit=False keeps this readable after commit

    await engine.dispose()

    resp = await logged_in_client.get(f"/api/v1/jobs/{job_id}")
    assert resp.status_code == 200
    body = resp.json()

    # JobDetail exposes the posting + provenance...
    assert body["id"] == str(job_id)
    assert body["title"] == "Backend Engineer"
    assert body["description"] == "Work on the ingestion pipeline."
    assert body["source"] == "adzuna"
    assert "posted_at" in body
    assert "ingested_at" in body
    # ...but never the embedding vector or the cross-source dedup hash.
    assert "embedding" not in body
    assert "content_hash" not in body


# ---------------------------------------------------------------------------
# Ingest source-name validation/normalization (the case-sensitivity footgun)
# ---------------------------------------------------------------------------


def test_ingest_request_normalizes_source_case_and_dedupes():
    # Mixed case + surrounding whitespace + a duplicate -> canonical lowercase, deduped.
    req = IngestRequest(query="x", sources=["Jooble", "INDEED ", "jooble"])
    assert req.sources == ["jooble", "indeed"]


def test_ingest_request_rejects_unknown_source():
    with pytest.raises(ValidationError):
        IngestRequest(query="x", sources=["linkedin"])


async def test_ingest_rejects_unknown_source_returns_422(logged_in_client):
    app.dependency_overrides[get_arq_redis] = lambda: _NoOpRedis()
    try:
        resp = await logged_in_client.post(
            "/api/v1/jobs/ingest", json={"query": "x", "sources": ["bogus"]}
        )
        assert resp.status_code == 422
    finally:
        app.dependency_overrides.pop(get_arq_redis, None)


async def test_ingest_forwards_normalized_sources_to_worker(logged_in_client):
    # Prove the worker receives canonical lowercase names (so self.sources[name] hits).
    captured = {}

    class _CapturingRedis:
        async def enqueue_job(self, name, *args, **kwargs):
            captured["sources"] = kwargs.get("sources")

            class _Job:
                job_id = "noop"

            return _Job()

    app.dependency_overrides[get_arq_redis] = lambda: _CapturingRedis()
    try:
        resp = await logged_in_client.post(
            "/api/v1/jobs/ingest",
            json={"query": "Software Engineer", "location": "Warsaw", "sources": ["Jooble", "INDEED"]},
        )
        assert resp.status_code == 202
        assert captured["sources"] == ["jooble", "indeed"]
    finally:
        app.dependency_overrides.pop(get_arq_redis, None)
