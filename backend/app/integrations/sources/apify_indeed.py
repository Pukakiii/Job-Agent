from app.core.logger import get_logger
from app.integrations.sources.base import RawJob

logger = get_logger("app.integrations.sources.apify_indeed")


class ApifyIndeedSource:
    name = "indeed"
    is_scraped = True  # best-effort scraped layer; loses to API sources on dedup

    def __init__(self, apify) -> None:
        self._apify = apify

    async def fetch(self, query: str, location: str | None = None) -> list[RawJob]:
        items = await self._apify.run_indeed(query, location)
        jobs: list[RawJob] = []
        for r in items:
            url = r.get("url") or r.get("link") or ""
            jobs.append(RawJob(
                source_job_id=str(r.get("id") or url),
                title=r.get("positionName") or r.get("title") or "",
                url=url,
                description=r.get("description", ""),
                company=r.get("company") or None,
                location=r.get("location") or None,
            ))
        return jobs
