from datetime import datetime, timezone
from uuid import uuid4

from app.models.user import User
from app.repositories.cv_repo import CVRepository


async def _make_user(db) -> User:
    user = User(email=f"{uuid4()}@test.io", hashed_password="x")
    db.add(user)
    await db.flush()
    return user


async def test_create_populates_id_and_timestamp(db):
    user = await _make_user(db)
    repo = CVRepository(db)

    cv = await repo.create(user.id, f"cvs/{user.id}/a.pdf", "resume.pdf", "application/pdf")

    assert cv.id is not None
    assert cv.created_at is not None  # server_default fetched via RETURNING on flush
    assert cv.user_id == user.id


async def test_get_by_id_roundtrips(db):
    user = await _make_user(db)
    repo = CVRepository(db)
    cv = await repo.create(user.id, "cvs/k.pdf", "resume.pdf", "application/pdf")

    got = await repo.get_by_id(cv.id)

    assert got.original_filename == "resume.pdf"
    assert got.content_type == "application/pdf"


async def test_list_by_user_is_newest_first(db):
    user = await _make_user(db)
    repo = CVRepository(db)
    old = await repo.create(user.id, "cvs/old.pdf", "old.pdf", "application/pdf")
    new = await repo.create(user.id, "cvs/new.pdf", "new.pdf", "application/pdf")
    # Postgres now() is the transaction start time, so both rows would otherwise
    # share a created_at within one test transaction. Stamp distinct times so the
    # "newest first" ordering is actually exercised.
    old.created_at = datetime(2020, 1, 1, tzinfo=timezone.utc)
    new.created_at = datetime(2021, 1, 1, tzinfo=timezone.utc)
    await db.flush()

    cvs = await repo.list_by_user(user.id)

    assert [c.original_filename for c in cvs] == ["new.pdf", "old.pdf"]


async def test_list_by_user_isolates_users(db):
    repo = CVRepository(db)
    u1, u2 = await _make_user(db), await _make_user(db)
    await repo.create(u1.id, "cvs/u1.pdf", "u1.pdf", "application/pdf")

    assert len(await repo.list_by_user(u1.id)) == 1
    assert await repo.list_by_user(u2.id) == []


async def test_set_parsing_result_updates_row(db):
    user = await _make_user(db)
    repo = CVRepository(db)
    cv = await repo.create(user.id, "cvs/k.pdf", "resume.pdf", "application/pdf")
    cid = cv.id

    await repo.set_parsing_result(cid, "extracted text", {"name": "Jane"})
    db.expire_all()  # force a fresh read so we see the UPDATE
    refreshed = await repo.get_by_id(cid)

    assert refreshed.extracted_text == "extracted text"
    assert refreshed.parsed_profile == {"name": "Jane"}


async def test_s3_keys_for_user_returns_all_keys(db):
    user = await _make_user(db)
    repo = CVRepository(db)
    await repo.create(user.id, "cvs/a.pdf", "a.pdf", "application/pdf")
    await repo.create(user.id, "cvs/b.pdf", "b.pdf", "application/pdf")

    keys = await repo.s3_keys_for_user(user.id)

    assert sorted(keys) == ["cvs/a.pdf", "cvs/b.pdf"]

async def test_delete_removes_row(db):
    user = await _make_user(db)
    repo = CVRepository(db)
    cv = await repo.create(user.id, "cvs/k.pdf", "resume.pdf", "application/pdf")
    await repo.delete(cv)
    assert await repo.get_by_id(cv.id) is None


async def test_list_by_user_pagination(db):
    user = await _make_user(db)
    repo = CVRepository(db)
    for i in range(3):
        await repo.create(user.id, f"cvs/{i}.pdf", f"f{i}.pdf", "application/pdf")
    page = await repo.list_by_user(user.id, limit=2, offset=0)
    assert len(page) == 2
    page2 = await repo.list_by_user(user.id, limit=2, offset=2)
    assert len(page2) == 1