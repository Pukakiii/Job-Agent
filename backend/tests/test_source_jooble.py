import json

import httpx

from app.core.config import settings
from app.integrations.sources.jooble import JoobleSource


def _client(payload: dict) -> httpx.AsyncClient:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST" and request.url.path.endswith("/KEY")
        body = json.loads(request.content)
        assert body["keywords"] == "python"
        return httpx.Response(200, content=json.dumps(payload))
    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


async def test_jooble_fetch_parses_jobs():
    payload = {"jobs": [{
        "title": "Python Dev", "company": "ACME", "location": "Berlin",
        "link": "http://jooble/abc", "snippet": "python work", "updated": "2026-06-01T00:00:00.0000000",
    }]}
    cfg = settings.model_copy(update={"JOOBLE_API_KEY": "KEY"})
    async with _client(payload) as client:
        src = JoobleSource(client, cfg)
        jobs = await src.fetch("python", "berlin")
    assert src.name == "jooble" and src.is_scraped is False
    assert jobs[0].source_job_id == "http://jooble/abc"  # link as id fallback
    assert jobs[0].company == "ACME" and jobs[0].description == "python work"
