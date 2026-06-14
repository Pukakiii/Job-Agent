from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import func, select

from app.models.job import Job
from app.repositories.job_repo import JobRepository


def _unit_vec(i: int) -> list[float]:
    """An orthogonal unit vector, so cosine ordering between jobs is well-defined."""
    v = [0.0] * 768
    v[i] = 1.0
    return v


def _job_row(source: str, source_job_id: str, title: str, dim: int) -> dict:
    return dict(
        id=uuid4(),
        source=source,
        source_job_id=source_job_id,
        content_hash=f"h-{source_job_id}",
        title=title,
        url=f"http://example.com/{source_job_id}",
        description="desc",
        embedding=_unit_vec(dim),
    )


async def _count_jobs(db) -> int:
    return await db.scalar(select(func.count()).select_from(Job))


async def test_upsert_many_is_idempotent(db):
    repo = JobRepository(db)
    rows = [_job_row("adzuna", "A1", "Python Dev", 0)]

    await repo.upsert_many(rows)
    await repo.upsert_many(rows)  # re-running an ingest must not duplicate
    await db.flush()

    assert await _count_jobs(db) == 1


async def test_upsert_many_updates_on_conflict(db):
    repo = JobRepository(db)
    await repo.upsert_many([_job_row("adzuna", "A1", "Old Title", 0)])
    await db.flush()

    # same (source, source_job_id) -> updates the existing row, no new row
    await repo.upsert_many([_job_row("adzuna", "A1", "New Title", 0)])
    await db.flush()

    assert await _count_jobs(db) == 1
    title = await db.scalar(select(Job.title).where(Job.source_job_id == "A1"))
    assert title == "New Title"


async def test_search_by_vector_orders_by_cosine_distance(db):
    repo = JobRepository(db)
    await repo.upsert_many([
        _job_row("adzuna", "A1", "Closest", 0),
        _job_row("jooble", "B1", "Farther", 5),
    ])
    await db.flush()

    # query points along dimension 0 -> "Closest" (vec[0]) ranks first
    hits = await repo.search_by_vector(_unit_vec(0), limit=10)

    assert [j.title for j in hits] == ["Closest", "Farther"]


async def test_search_by_vector_respects_limit(db):
    repo = JobRepository(db)
    await repo.upsert_many([_job_row("adzuna", f"A{i}", f"Job {i}", i) for i in range(5)])
    await db.flush()

    hits = await repo.search_by_vector(_unit_vec(0), limit=3)

    assert len(hits) == 3


async def test_get_by_id_returns_job(db):
    repo = JobRepository(db)
    row = _job_row("adzuna", "A99", "Target Job", 0)
    await repo.upsert_many([row])
    await db.flush()

    result = await repo.get_by_id(row["id"])

    assert result is not None
    assert result.id == row["id"]
    assert result.title == "Target Job"


async def test_get_by_id_returns_none_when_missing(db):
    repo = JobRepository(db)

    result = await repo.get_by_id(uuid4())

    assert result is None


async def test_list_jobs_orders_by_ingested_at_desc(db):
    repo = JobRepository(db)
    old_row = {**_job_row("adzuna", "OLD1", "Old Job", 0), "ingested_at": datetime(2026, 1, 1, tzinfo=timezone.utc)}
    new_row = {**_job_row("adzuna", "NEW1", "New Job", 1), "ingested_at": datetime(2026, 2, 1, tzinfo=timezone.utc)}
    await repo.upsert_many([old_row, new_row])
    await db.flush()

    jobs = await repo.list_jobs()

    titles = [j.title for j in jobs]
    assert titles.index("New Job") < titles.index("Old Job")


async def test_list_jobs_respects_limit_and_offset(db):
    repo = JobRepository(db)
    rows = [
        {**_job_row("adzuna", f"L{i}", f"Job {i}", i), "ingested_at": datetime(2026, 1, i + 1, tzinfo=timezone.utc)}
        for i in range(5)
    ]
    await repo.upsert_many(rows)
    await db.flush()

    page1 = await repo.list_jobs(limit=2, offset=0)
    page2 = await repo.list_jobs(limit=2, offset=2)

    assert len(page1) == 2
    assert len(page2) == 2
    # pages must not overlap
    page1_ids = {j.id for j in page1}
    page2_ids = {j.id for j in page2}
    assert page1_ids.isdisjoint(page2_ids)
