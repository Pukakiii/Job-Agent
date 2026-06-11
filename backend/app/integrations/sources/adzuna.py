from datetime import datetime

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import Settings
from app.core.logger import get_logger
from app.integrations.sources.base import RawJob

logger = get_logger("app.integrations.sources.adzuna")

_RETRY = dict(
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.HTTPStatusError)),
    wait=wait_exponential(multiplier=1, max=10),
    stop=stop_after_attempt(3),
    reraise=True,
)


def _parse_created(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


class AdzunaSource:
    name = "adzuna"
    is_scraped = False

    def __init__(self, client: httpx.AsyncClient, settings: Settings) -> None:
        self._client = client
        self._settings = settings

    @retry(**_RETRY)
    async def _get(self, url: str, params: dict) -> dict:
        resp = await self._client.get(url, params=params, timeout=self._settings.SOURCE_HTTP_TIMEOUT)
        resp.raise_for_status()  # 5xx/timeout retried; 4xx surfaces (reraise)
        return resp.json()

    async def fetch(self, query: str, location: str | None = None) -> list[RawJob]:
        s = self._settings
        url = f"{s.ADZUNA_BASE_URL}/jobs/{s.ADZUNA_COUNTRY}/search/1"
        params = {
            "app_id": s.ADZUNA_APP_ID, "app_key": s.ADZUNA_APP_KEY,
            "what": query, "results_per_page": 50,
        }
        if location:
            params["where"] = location
        data = await self._get(url, params)
        jobs: list[RawJob] = []
        for r in data.get("results", []):
            jobs.append(RawJob(
                source_job_id=str(r["id"]),
                title=r.get("title", ""),
                url=r.get("redirect_url", ""),
                description=r.get("description", ""),
                company=(r.get("company") or {}).get("display_name"),
                location=(r.get("location") or {}).get("display_name"),
                posted_at=_parse_created(r.get("created")),
            ))
        logger.info("Adzuna returned %d jobs for %r", len(jobs), query)
        return jobs
