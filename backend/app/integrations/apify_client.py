import httpx

from app.core.config import Settings
from app.core.logger import get_logger

logger = get_logger("app.integrations.apify_client")


class ApifyClient:
    """Thin wrapper over Apify's run-sync-get-dataset-items endpoint."""

    def __init__(self, client: httpx.AsyncClient, settings: Settings) -> None:
        self._client = client
        self._settings = settings

    async def run_indeed(self, query: str, location: str | None) -> list[dict]:
        s = self._settings
        url = f"{s.APIFY_BASE_URL}/acts/{s.APIFY_INDEED_ACTOR}/run-sync-get-dataset-items"
        actor_input = {"position": query, "location": location or "", "maxItems": 50}
        resp = await self._client.post(
            url, params={"token": s.APIFY_API_TOKEN}, json=actor_input, timeout=s.APIFY_TIMEOUT,
        )
        resp.raise_for_status()
        items = resp.json()
        logger.info("Apify Indeed returned %d items for %r", len(items), query)
        return items
