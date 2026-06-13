from sqlalchemy import func, select

from app.integrations.sources.base import RawJob
from app.models.job import Job
from app.workers.tasks import scrape_board


class FakeSource:
    name = "adzuna"
    is_scraped = False

    async def fetch(self, query, location=None):
        return [
            RawJob(
                source_job_id="1",
                title="Python Dev",
                url="http://j/1",
                description="d",
                company="ACME",
                location="Berlin",
            )
        ]


class FakeEmbedder:
    async def embed_batch(self, texts):
        return [[0.5] * 768 for _ in texts]


async def test_scrape_board_persists(db, monkeypatch):
    # scrape_board opens its own session via async_session_factory; redirect that
    # to the test session so the db fixture's rollback still isolates the test.
    import app.workers.tasks as tasks

    class _Factory:
        async def __aenter__(self):
            return db

        async def __aexit__(self, *exc):
            return False

    monkeypatch.setattr(tasks, "async_session_factory", lambda: _Factory())
    monkeypatch.setattr(db, "commit", db.flush)

    ctx = {"sources": {"adzuna": FakeSource()}, "embedder": FakeEmbedder()}
    count = await scrape_board(ctx, "python")
    assert count == 1
    assert await db.scalar(select(func.count()).select_from(Job)) == 1
