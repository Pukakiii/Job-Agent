from uuid import uuid4

from app.models.user import User
from app.repositories.job_repo import JobRepository
from app.repositories.search_repo import SearchRepository


def _unit_vec(i: int) -> list[float]:
    v = [0.0] * 768
    v[i] = 1.0
    return v


async def _make_user(db) -> User:
    user = User(email=f"{uuid4()}@test.io", hashed_password="x")
    db.add(user)
    await db.flush()
    return user


async def _make_two_jobs(db) -> list:
    repo = JobRepository(db)
    await repo.upsert_many([
        dict(id=uuid4(), source="adzuna", source_job_id="A1", content_hash="h1",
             title="Python Dev", url="http://a", description="d", embedding=_unit_vec(0)),
        dict(id=uuid4(), source="jooble", source_job_id="B1", content_hash="h2",
             title="Data Eng", url="http://b", description="d", embedding=_unit_vec(5)),
    ])
    await db.flush()
    return await repo.search_by_vector(_unit_vec(0), limit=10)


async def test_save_search_persists_results_with_ranks(db):
    user = await _make_user(db)
    jobs = await _make_two_jobs(db)
    repo = SearchRepository(db)

    ranked = [(jobs[0].id, 0.95, "great fit"), (jobs[1].id, 0.40, "weaker")]
    search = await repo.save_search(user.id, None, "python", ranked)

    assert search.id is not None
    assert len(search.results) == 2
    # rank is assigned from list order (1-based)
    assert [(r.rank, r.score) for r in search.results] == [(1, 0.95), (2, 0.40)]


async def test_get_with_results_loads_results_and_jobs(db):
    user = await _make_user(db)
    jobs = await _make_two_jobs(db)
    repo = SearchRepository(db)
    saved = await repo.save_search(user.id, None, "python", [(jobs[0].id, 0.9, "fit")])

    loaded = await repo.get_with_results(saved.id)

    assert loaded is not None
    assert loaded.prompt == "python"
    # selectinload eager-loaded results and their job -> no lazy I/O needed here
    assert loaded.results[0].rank == 1
    assert loaded.results[0].job.title == "Python Dev"


async def test_get_with_results_returns_none_for_missing(db):
    repo = SearchRepository(db)
    assert await repo.get_with_results(uuid4()) is None
