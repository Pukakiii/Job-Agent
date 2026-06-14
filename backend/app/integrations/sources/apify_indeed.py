from app.core.countries import parse_location
from app.core.logger import get_logger
from app.integrations.sources.base import RawJob

logger = get_logger("app.integrations.sources.apify_indeed")


class ApifyIndeedSource:
    name = "indeed"
    is_scraped = True  # best-effort scraped layer; loses to API sources on dedup

    def __init__(self, apify) -> None:
        self._apify = apify

    async def fetch(self, query: str, location: str | None = None) -> list[RawJob]:
        # Split "Warszawa, PL" into the city (Indeed's location field) and the ISO code
        # (which selects the Indeed domain, e.g. pl.indeed.com — without it the actor
        # defaults to indeed.com / US and ignores a foreign city).
        city, country, _ = parse_location(location)
        items = await self._apify.run_indeed(query, city or location, country=country)
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
