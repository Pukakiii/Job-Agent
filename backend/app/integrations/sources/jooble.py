from datetime import datetime

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import Settings
from app.core.logger import get_logger
from app.integrations.sources.base import RawJob

logger = get_logger("app.integrations.sources.jooble")

_RETRY = dict(
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.HTTPStatusError)),
    wait=wait_exponential(multiplier=1, max=10),
    stop=stop_after_attempt(3),
    reraise=True,
)


def _parse_updated(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.split(".")[0])
    except ValueError:
        return None


class JoobleSource:
    name = "jooble"
    is_scraped = False

    def __init__(self, client: httpx.AsyncClient, settings: Settings) -> None:
        self._client = client
        self._settings = settings

    @retry(**_RETRY)
    async def _post(self, url: str, body: dict) -> dict:
        resp = await self._client.post(url, json=body, timeout=self._settings.SOURCE_HTTP_TIMEOUT)
        resp.raise_for_status()
        return resp.json()

    async def fetch(self, query: str, location: str | None = None) -> list[RawJob]:
        s = self._settings
        url = f"{s.JOOBLE_BASE_URL}/{s.JOOBLE_API_KEY}"
        data = await self._post(url, {"keywords": query, "location": location or ""})
        jobs: list[RawJob] = []
        for r in data.get("jobs", []):
            link = r.get("link", "")
            jobs.append(RawJob(
                source_job_id=str(r.get("id") or link),
                title=r.get("title", ""),
                url=link,
                description=r.get("snippet", ""),
                company=r.get("company") or None,
                location=r.get("location") or None,
                posted_at=_parse_updated(r.get("updated")),
            ))
        logger.info("Jooble returned %d jobs for %r", len(jobs), query)
        return jobs
