import httpx

from app.core.config import Settings
from app.core.logger import get_logger

logger = get_logger("app.integrations.apify_client")


class ApifyClient:
    """Thin wrapper over Apify's run-sync-get-dataset-items endpoint."""

    def __init__(self, client: httpx.AsyncClient, settings: Settings) -> None:
        self._client = client
        self._settings = settings

    async def run_indeed(
        self, query: str, location: str | None, country: str | None = None
    ) -> list[dict]:
        s = self._settings
        url = f"{s.APIFY_BASE_URL}/acts/{s.APIFY_INDEED_ACTOR}/run-sync-get-dataset-items"
        actor_input: dict = {"position": query, "location": location or "", "maxItems": 50}
        if country:
            # The actor's `country` enum is UPPER-case ISO alpha-2 (e.g. "PL"); it selects
            # the Indeed domain (pl.indeed.com). A lower-case value is rejected with 400.
            actor_input["country"] = country.upper()
        resp = await self._client.post(
            # Token in the Authorization header, not the query string — a token in the URL
            # leaks into httpx error messages and request logs.
            url,
            headers={"Authorization": f"Bearer {s.APIFY_API_TOKEN}"},
            json=actor_input,
            timeout=s.APIFY_TIMEOUT,
        )
        resp.raise_for_status()
        items = resp.json()
        logger.info("Apify Indeed returned %d items for %r", len(items), query)
        return items
