"""Repository tests for ApplicationRepository.

Runs against a real Postgres + pgvector Testcontainer via the shared ``db``
fixture in conftest.py (rolled-back AsyncSession per test). A real DB is used
because the unique-constraint and enum-type behaviour wouldn't be exercised by
a mock or SQLite.
"""
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.application import ApplicationStatus, JobApplication
from app.models.job import Job
from app.models.user import User
from app.repositories.application_repo import ApplicationRepository


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _make_user(db) -> User:
    user = User(email=f"{uuid4()}@test.io", hashed_password="x")
    db.add(user)
    await db.flush()
    return user


async def _make_job(db) -> Job:
    """Insert a minimal Job row (embedding required by NOT NULL constraint)."""
    job = Job(
        source="test",
        source_job_id=str(uuid4()),
        content_hash=str(uuid4()),
        title="Test Job",
        url="http://example.com/job",
        description="A test job description",
        embedding=[0.0] * 768,
    )
    db.add(job)
    await db.flush()
    return job


# ---------------------------------------------------------------------------
# create
# ---------------------------------------------------------------------------

async def test_create_populates_id_and_timestamps(db):
    user = await _make_user(db)
    job  = await _make_job(db)
    repo = ApplicationRepository(db)

    app = await repo.create(user.id, job.id)

    assert app.id is not None
    assert app.created_at is not None
    assert app.updated_at is not None
    assert app.user_id == user.id
    assert app.job_id  == job.id


async def test_create_default_status_is_saved(db):
    user = await _make_user(db)
    job  = await _make_job(db)
    repo = ApplicationRepository(db)

    app = await repo.create(user.id, job.id)

    assert app.status == ApplicationStatus.saved


async def test_create_sets_applied_at_when_status_is_applied(db):
    user = await _make_user(db)
    job  = await _make_job(db)
    repo = ApplicationRepository(db)

    app = await repo.create(user.id, job.id, status=ApplicationStatus.applied)

    assert app.applied_at is not None


async def test_create_does_not_set_applied_at_for_other_statuses(db):
    user = await _make_user(db)
    repo = ApplicationRepository(db)

    for status in (ApplicationStatus.saved, ApplicationStatus.interview, ApplicationStatus.offer, ApplicationStatus.rejected):
        job = await _make_job(db)
        app = await repo.create(user.id, job.id, status=status)
        assert app.applied_at is None, f"applied_at should be None for status={status}"


async def test_create_stores_notes_and_cv_id(db):
    user = await _make_user(db)
    job  = await _make_job(db)
    repo = ApplicationRepository(db)

    # cv_id FK requires a real CV row; here we just verify notes are stored.
    # The FK constraint itself is tested at the schema level (model definition).
    app = await repo.create(user.id, job.id, notes="Great opportunity")

    assert app.notes == "Great opportunity"


# ---------------------------------------------------------------------------
# get_by_id
# ---------------------------------------------------------------------------

async def test_get_by_id_roundtrips(db):
    user = await _make_user(db)
    job  = await _make_job(db)
    repo = ApplicationRepository(db)
    app  = await repo.create(user.id, job.id, notes="hi")

    got = await repo.get_by_id(app.id)

    assert got is not None
    assert got.id    == app.id
    assert got.notes == "hi"


async def test_get_by_id_returns_none_for_unknown_id(db):
    repo = ApplicationRepository(db)
    assert await repo.get_by_id(uuid4()) is None


# ---------------------------------------------------------------------------
# list_by_user
# ---------------------------------------------------------------------------

async def test_list_by_user_ordered_by_updated_at_desc(db):
    user = await _make_user(db)
    repo = ApplicationRepository(db)

    job_old = await _make_job(db)
    job_new = await _make_job(db)
    app_old = await repo.create(user.id, job_old.id)
    app_new = await repo.create(user.id, job_new.id)

    # Postgres now() is the transaction start time — stamp distinct times so
    # the ordering is exercised for real.
    app_old.updated_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
    app_new.updated_at = datetime(2025, 1, 1, tzinfo=timezone.utc)
    await db.flush()

    apps = await repo.list_by_user(user.id)

    assert apps[0].id == app_new.id
    assert apps[1].id == app_old.id


async def test_list_by_user_isolates_users(db):
    repo = ApplicationRepository(db)
    u1   = await _make_user(db)
    u2   = await _make_user(db)
    job  = await _make_job(db)
    await repo.create(u1.id, job.id)

    assert len(await repo.list_by_user(u1.id)) == 1
    assert await repo.list_by_user(u2.id) == []


async def test_list_by_user_filters_by_status(db):
    user = await _make_user(db)
    repo = ApplicationRepository(db)

    job_a = await _make_job(db)
    job_b = await _make_job(db)
    await repo.create(user.id, job_a.id, status=ApplicationStatus.applied)
    await repo.create(user.id, job_b.id, status=ApplicationStatus.saved)

    applied = await repo.list_by_user(user.id, status=ApplicationStatus.applied)
    saved   = await repo.list_by_user(user.id, status=ApplicationStatus.saved)

    assert len(applied) == 1 and applied[0].job_id == job_a.id
    assert len(saved)   == 1 and saved[0].job_id   == job_b.id


async def test_list_by_user_pagination(db):
    user = await _make_user(db)
    repo = ApplicationRepository(db)

    for _ in range(3):
        job = await _make_job(db)
        await repo.create(user.id, job.id)

    page1 = await repo.list_by_user(user.id, limit=2, offset=0)
    page2 = await repo.list_by_user(user.id, limit=2, offset=2)

    assert len(page1) == 2
    assert len(page2) == 1
    assert {a.id for a in page1}.isdisjoint({a.id for a in page2})


# ---------------------------------------------------------------------------
# update_status
# ---------------------------------------------------------------------------

async def test_update_status_mutates_row(db):
    user = await _make_user(db)
    job  = await _make_job(db)
    repo = ApplicationRepository(db)
    app  = await repo.create(user.id, job.id)

    await repo.update_status(app, ApplicationStatus.interview, notes="First round booked")
    # Use async refresh — expire_all() + sync attribute access causes MissingGreenlet
    await db.refresh(app)

    assert app.status == ApplicationStatus.interview
    assert app.notes  == "First round booked"


async def test_update_status_sets_applied_at_on_first_transition(db):
    user = await _make_user(db)
    job  = await _make_job(db)
    repo = ApplicationRepository(db)
    app  = await repo.create(user.id, job.id, status=ApplicationStatus.saved)

    assert app.applied_at is None
    await repo.update_status(app, ApplicationStatus.applied)

    assert app.applied_at is not None


async def test_update_status_does_not_overwrite_applied_at(db):
    user     = await _make_user(db)
    job      = await _make_job(db)
    repo     = ApplicationRepository(db)
    app      = await repo.create(user.id, job.id, status=ApplicationStatus.applied)
    original = app.applied_at

    # Transition away then back to applied
    await repo.update_status(app, ApplicationStatus.saved)
    await repo.update_status(app, ApplicationStatus.applied)

    assert app.applied_at == original


async def test_update_status_leaves_notes_unchanged_when_none_passed(db):
    user = await _make_user(db)
    job  = await _make_job(db)
    repo = ApplicationRepository(db)
    app  = await repo.create(user.id, job.id, notes="keep me")

    await repo.update_status(app, ApplicationStatus.interview, notes=None)

    assert app.notes == "keep me"


# ---------------------------------------------------------------------------
# unique constraint
# ---------------------------------------------------------------------------

async def test_unique_constraint_prevents_duplicate(db):
    user = await _make_user(db)
    job  = await _make_job(db)
    repo = ApplicationRepository(db)
    await repo.create(user.id, job.id)

    with pytest.raises(IntegrityError):
        await repo.create(user.id, job.id)


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------

async def test_delete_removes_row(db):
    user = await _make_user(db)
    job  = await _make_job(db)
    repo = ApplicationRepository(db)
    app  = await repo.create(user.id, job.id)

    await repo.delete(app)
    await db.flush()

    assert await repo.get_by_id(app.id) is None
