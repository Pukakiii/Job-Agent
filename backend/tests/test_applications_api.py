"""HTTP API tests for /api/v1/applications endpoints.

Each group of tests exercises one logical concern:

  1. Auth guards           — every endpoint returns 401 without a session
  2. POST /applications    — create: 201 + embedded job, 409 conflict, 422 validation
  3. GET  /applications    — list: empty, with embedded job, status filter
  4. PUT  /applications    — update: mutates status, 404 for unknown/other-user's app
  5. DELETE /applications  — delete: 204 + gone, 404 for unknown id

Tests that need a real Job row seed it directly via pg_url (same pattern as
test_jobs_api.py) so the FK constraint is satisfied and the eager-loaded
`job` object in the response is a real DB round-trip, not a fake.
"""
import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models import Base
from app.models.job import Job


# ---------------------------------------------------------------------------
# Module-level helper — seeds a Job row into the test container DB
# ---------------------------------------------------------------------------

async def _seed_job(
    pg_url: str,
    *,
    title: str = "Python Engineer",
    company: str = "Acme Corp",
    url: str = "https://example.com/job/1",
) -> dict:
    """Insert a minimal Job row and return its id/title/url.

    Uses a short-lived engine pointed at pg_url (the Testcontainer URL).
    The schema is created idempotently so it works regardless of test order.
    """
    engine = create_async_engine(pg_url)
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        job = Job(
            source="test",
            source_job_id=str(uuid.uuid4()),
            content_hash=str(uuid.uuid4()),
            title=title,
            company=company,
            location="Remote",
            url=url,
            description="A seeded test job.",
            embedding=[0.0] * 768,
        )
        session.add(job)
        await session.commit()
        job_id = job.id

    await engine.dispose()
    return {"id": str(job_id), "title": title, "company": company, "url": url}


# ---------------------------------------------------------------------------
# 1. Auth guards
# ---------------------------------------------------------------------------

async def test_list_applications_requires_auth(auth_client):
    resp = await auth_client.get("/api/v1/applications")
    assert resp.status_code == 401


async def test_create_application_requires_auth(auth_client):
    resp = await auth_client.post(
        "/api/v1/applications", json={"job_id": str(uuid.uuid4())}
    )
    assert resp.status_code == 401


async def test_update_application_requires_auth(auth_client):
    resp = await auth_client.put(
        f"/api/v1/applications/{uuid.uuid4()}", json={"status": "applied"}
    )
    assert resp.status_code == 401


async def test_delete_application_requires_auth(auth_client):
    resp = await auth_client.delete(f"/api/v1/applications/{uuid.uuid4()}")
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# 2. POST /applications — create
# ---------------------------------------------------------------------------

async def test_create_application_returns_201_with_embedded_job(
    logged_in_client, pg_url
):
    """201 response body must include the nested job object (eager-load check)."""
    job = await _seed_job(pg_url)

    resp = await logged_in_client.post(
        "/api/v1/applications", json={"job_id": job["id"]}
    )

    assert resp.status_code == 201
    body = resp.json()
    assert body["job_id"] == job["id"]
    assert body["status"] == "saved"             # default status
    assert body["job"] is not None               # embedded job present
    assert body["job"]["id"] == job["id"]
    assert body["job"]["title"] == job["title"]
    assert body["job"]["url"] == job["url"]


async def test_create_application_conflict_returns_409_envelope(
    logged_in_client, pg_url
):
    """Duplicate (user, job) must return 409 with application_conflict code."""
    job = await _seed_job(pg_url, title="Duplicate Job", url="https://example.com/dup")

    await logged_in_client.post("/api/v1/applications", json={"job_id": job["id"]})
    resp = await logged_in_client.post(
        "/api/v1/applications", json={"job_id": job["id"]}
    )

    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "application_conflict"


async def test_create_application_validation_rejects_missing_job_id(logged_in_client):
    """POST with no body → 422 (FastAPI/Pydantic validation, not a domain error)."""
    resp = await logged_in_client.post("/api/v1/applications", json={})
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# 3. GET /applications — list
# ---------------------------------------------------------------------------

async def test_list_applications_returns_empty_for_new_user(logged_in_client):
    resp = await logged_in_client.get("/api/v1/applications")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_list_applications_returns_application_with_embedded_job(
    logged_in_client, pg_url
):
    """List response must embed the job object — proving the eager-load fires
    on the list path, not just the create path."""
    job = await _seed_job(pg_url, title="Listed Job", url="https://example.com/listed")

    await logged_in_client.post("/api/v1/applications", json={"job_id": job["id"]})
    resp = await logged_in_client.get("/api/v1/applications")

    assert resp.status_code == 200
    items = resp.json()
    assert len(items) >= 1
    match = next((a for a in items if a["job_id"] == job["id"]), None)
    assert match is not None
    assert match["job"]["title"] == job["title"]
    assert match["job"]["url"] == job["url"]


async def test_list_applications_filters_by_status(logged_in_client, pg_url):
    """?status= query param must narrow results correctly."""
    job_a = await _seed_job(pg_url, title="Job A", url="https://example.com/a")
    job_b = await _seed_job(pg_url, title="Job B", url="https://example.com/b")

    await logged_in_client.post(
        "/api/v1/applications", json={"job_id": job_a["id"], "status": "applied"}
    )
    await logged_in_client.post(
        "/api/v1/applications", json={"job_id": job_b["id"], "status": "saved"}
    )

    applied = await logged_in_client.get("/api/v1/applications?status=applied")
    saved = await logged_in_client.get("/api/v1/applications?status=saved")

    assert applied.status_code == 200
    assert saved.status_code == 200

    applied_ids = {a["job_id"] for a in applied.json()}
    saved_ids = {a["job_id"] for a in saved.json()}

    assert job_a["id"] in applied_ids
    assert job_b["id"] not in applied_ids
    assert job_b["id"] in saved_ids
    assert job_a["id"] not in saved_ids


# ---------------------------------------------------------------------------
# 4. PUT /applications/{id} — update status
# ---------------------------------------------------------------------------

async def test_update_application_status_returns_updated_envelope(
    logged_in_client, pg_url
):
    job = await _seed_job(pg_url, title="Update Me", url="https://example.com/update")

    create = await logged_in_client.post(
        "/api/v1/applications", json={"job_id": job["id"]}
    )
    app_id = create.json()["id"]

    resp = await logged_in_client.put(
        f"/api/v1/applications/{app_id}",
        json={"status": "interview", "notes": "First round booked"},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "interview"
    assert body["notes"] == "First round booked"
    assert body["job"]["id"] == job["id"]        # embedded job still present after update


async def test_update_application_returns_404_for_unknown_id(logged_in_client):
    resp = await logged_in_client.put(
        f"/api/v1/applications/{uuid.uuid4()}",
        json={"status": "applied"},
    )
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "application_not_found"


async def test_update_application_returns_404_for_other_users_application(
    logged_in_client, auth_client, pg_url
):
    """User B must get 404 (not 403) when trying to update User A's application.

    Ownership leak protection: 404 is intentional — the row's existence is
    not revealed to other users. Same design as job_not_found.
    """
    job = await _seed_job(pg_url, title="Owned Job", url="https://example.com/owned")

    # User A creates an application (logged_in_client is User A)
    create = await logged_in_client.post(
        "/api/v1/applications", json={"job_id": job["id"]}
    )
    app_id = create.json()["id"]

    # User B registers and logs in via a fresh auth_client session
    creds_b = {"email": "userb@test.io", "password": "supersecret456"}
    await auth_client.post("/api/v1/auth/register", json=creds_b)
    await auth_client.post(
        "/api/v1/auth/jwt/login",
        data={"username": creds_b["email"], "password": creds_b["password"]},
    )

    resp = await auth_client.put(
        f"/api/v1/applications/{app_id}", json={"status": "offer"}
    )
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "application_not_found"


# ---------------------------------------------------------------------------
# 5. DELETE /applications/{id}
# ---------------------------------------------------------------------------

async def test_delete_application_returns_204_and_removes_row(
    logged_in_client, pg_url
):
    job = await _seed_job(pg_url, title="Delete Me", url="https://example.com/delete")

    create = await logged_in_client.post(
        "/api/v1/applications", json={"job_id": job["id"]}
    )
    app_id = create.json()["id"]

    delete = await logged_in_client.delete(f"/api/v1/applications/{app_id}")
    assert delete.status_code == 204

    # Confirm it no longer appears in the list
    lst = await logged_in_client.get("/api/v1/applications")
    assert not any(a["id"] == app_id for a in lst.json())


async def test_delete_application_returns_404_for_unknown_id(logged_in_client):
    resp = await logged_in_client.delete(f"/api/v1/applications/{uuid.uuid4()}")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "application_not_found"
