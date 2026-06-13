import uuid

from app.api.deps import get_matching_service
from app.main import app
from app.models.search import Search
from app.models.search_result import SearchResult


class StubMatching:
    async def find_matches(self, user_id, cv_id, prompt):
        s = Search(user_id=user_id, cv_id=cv_id, prompt=prompt)
        s.results = []  # empty shortlist is a valid (serializable) response
        return s


async def test_create_search_returns_201_and_schema(auth_client):
    app.dependency_overrides[get_matching_service] = lambda: StubMatching()
    try:
        resp = await auth_client.post(
            "/api/v1/searches",
            json={"cv_id": str(uuid.uuid4()), "prompt": "python role"},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["prompt"] == "python role"
        assert body["results"] == []
    finally:
        app.dependency_overrides.pop(get_matching_service, None)


async def test_get_search_404_for_missing(auth_client):
    resp = await auth_client.get(f"/api/v1/searches/{uuid.uuid4()}")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "search_not_found"
