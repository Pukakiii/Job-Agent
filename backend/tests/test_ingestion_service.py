from sqlalchemy import func, select

from app.integrations.sources.base import RawJob
from app.models.job import Job
from app.repositories.job_repo import JobRepository
from app.services.ingestion_service import IngestionService


class FakeSource:
    def __init__(self, name, is_scraped, jobs): self.name = name; self.is_scraped = is_scraped; self._jobs = jobs
    async def fetch(self, query, location=None): return self._jobs


class FakeEmbedder:
    async def embed_batch(self, texts): return [[float(len(t) % 7)] * 768 for t in texts]


def _raw(i, title="Python Dev", company="ACME", location="Berlin"):
    return RawJob(source_job_id=str(i), title=title, url=f"http://j/{i}", description="d",
                  company=company, location=location)


async def _count(db):
    return await db.scalar(select(func.count()).select_from(Job))


async def test_run_ingests_and_embeds(db):
    sources = {"adzuna": FakeSource("adzuna", False, [_raw(1), _raw(2, title="Data Eng")])}
    service = IngestionService(sources, FakeEmbedder(), JobRepository(db))
    n = await service.run("python")
    await db.flush()
    assert n == 2 and await _count(db) == 2
    vec = await db.scalar(select(Job.embedding).limit(1))
    assert len(list(vec)) == 768  # 768-dim vector persisted


async def test_run_is_idempotent(db):
    sources = {"adzuna": FakeSource("adzuna", False, [_raw(1)])}
    service = IngestionService(sources, FakeEmbedder(), JobRepository(db))
    await service.run("python"); await db.flush()
    await service.run("python"); await db.flush()
    assert await _count(db) == 1  # ON CONFLICT, no duplicate


async def test_run_dedups_cross_source_api_wins(db):
    # same listing on an API source and the scraped source -> one row, API kept
    same = dict(title="Python Dev", company="ACME", location="Berlin")
    sources = {
        "indeed": FakeSource("indeed", True, [_raw(10, **same)]),
        "adzuna": FakeSource("adzuna", False, [_raw(20, **same)]),
    }
    service = IngestionService(sources, FakeEmbedder(), JobRepository(db))
    n = await service.run("python"); await db.flush()
    assert n == 1
    src = await db.scalar(select(Job.source))
    assert src == "adzuna"


async def test_run_empty_returns_zero(db):
    sources = {"adzuna": FakeSource("adzuna", False, [])}
    service = IngestionService(sources, FakeEmbedder(), JobRepository(db))
    assert await service.run("python") == 0
