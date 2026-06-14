import uuid

from app.api.deps import get_arq_redis, get_matching_service
from app.exceptions import CorpusEmpty
from app.main import app
from app.models.search import Search


class StubMatching:
    async def find_matches(self, user_id, cv_id, prompt, location=None):
        s = Search(user_id=user_id, cv_id=cv_id, prompt=prompt)
        s.results = []  # empty shortlist is a valid (serializable) response
        return s


class StubMatchingEmptyCorpus:
    async def find_matches(self, user_id, cv_id, prompt, location=None):
        raise CorpusEmpty("no jobs yet")


class _NoOpRedis:
    async def enqueue_job(self, name, *args, **kwargs):
        class _Job:
            job_id = "noop"

        return _Job()


async def test_create_search_returns_201_and_schema(logged_in_client):
    # get_arq_redis is resolved for every create_search call (FastAPI resolves deps before
    # the body), so it must be overridden even on the 201 path that never enqueues.
    app.dependency_overrides[get_matching_service] = lambda: StubMatching()
    app.dependency_overrides[get_arq_redis] = lambda: _NoOpRedis()
    try:
        resp = await logged_in_client.post(
            "/api/v1/searches",
            json={"cv_id": str(uuid.uuid4()), "prompt": "python role"},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["prompt"] == "python role"
        assert body["results"] == []
    finally:
        app.dependency_overrides.pop(get_matching_service, None)
        app.dependency_overrides.pop(get_arq_redis, None)


async def test_get_search_404_for_missing(logged_in_client):
    resp = await logged_in_client.get(f"/api/v1/searches/{uuid.uuid4()}")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "search_not_found"


async def test_create_search_empty_corpus_triggers_ingest(logged_in_client):
    # Empty corpus -> the route enqueues ingestion and returns 202 (not an error).
    app.dependency_overrides[get_matching_service] = lambda: StubMatchingEmptyCorpus()
    app.dependency_overrides[get_arq_redis] = lambda: _NoOpRedis()
    try:
        resp = await logged_in_client.post(
            "/api/v1/searches",
            json={"cv_id": str(uuid.uuid4()), "prompt": "python", "location": "Warsaw"},
        )
        assert resp.status_code == 202
        body = resp.json()
        assert body["status"] == "ingesting"
        assert body["job_id"] == "noop"
    finally:
        app.dependency_overrides.pop(get_matching_service, None)
        app.dependency_overrides.pop(get_arq_redis, None)
