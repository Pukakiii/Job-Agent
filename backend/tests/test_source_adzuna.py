import json

import httpx

from app.core.config import settings
from app.integrations.sources.adzuna import AdzunaSource


def _client(payload: dict) -> httpx.AsyncClient:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert "app_id=" in str(request.url) and "what=python" in str(request.url)
        return httpx.Response(200, content=json.dumps(payload))
    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


async def test_adzuna_fetch_parses_results():
    payload = {"results": [{
        "id": "123", "title": "Python Dev",
        "company": {"display_name": "ACME"},
        "location": {"display_name": "Berlin"},
        "redirect_url": "http://job/123", "description": "Do python.",
        "created": "2026-06-01T00:00:00Z",
    }]}
    cfg = settings.model_copy(update={"ADZUNA_APP_ID": "id", "ADZUNA_APP_KEY": "key"})
    async with _client(payload) as client:
        src = AdzunaSource(client, cfg)
        jobs = await src.fetch("python", "berlin")
    assert src.name == "adzuna" and src.is_scraped is False
    assert len(jobs) == 1
    assert jobs[0].source_job_id == "123" and jobs[0].company == "ACME"
    assert jobs[0].url == "http://job/123"
