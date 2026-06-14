import json

import httpx

from app.core.config import settings
from app.integrations.apify_client import ApifyClient


def _client(captured: dict) -> httpx.AsyncClient:
    async def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["auth"] = request.headers.get("Authorization")
        captured["body"] = json.loads(request.content)
        return httpx.Response(200, content=json.dumps([{"id": "1", "positionName": "Dev", "url": "u"}]))

    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


async def test_run_indeed_authenticates_via_header_not_url():
    captured: dict = {}
    cfg = settings.model_copy(update={"APIFY_API_TOKEN": "secret-token"})
    async with _client(captured) as client:
        items = await ApifyClient(client, cfg).run_indeed("dev", "Warszawa", country="pl")

    # Token goes in the Authorization header, never the URL (URLs leak into logs/errors).
    assert captured["auth"] == "Bearer secret-token"
    assert "secret-token" not in captured["url"]
    # country is upper-cased for the actor's enum (pl -> PL); lower-case is rejected (400)
    assert captured["body"]["country"] == "PL"
    assert captured["body"]["position"] == "dev"
    assert items[0]["id"] == "1"


async def test_run_indeed_omits_country_when_absent():
    captured: dict = {}
    cfg = settings.model_copy(update={"APIFY_API_TOKEN": "t"})
    async with _client(captured) as client:
        await ApifyClient(client, cfg).run_indeed("dev", "Berlin")

    assert "country" not in captured["body"]
