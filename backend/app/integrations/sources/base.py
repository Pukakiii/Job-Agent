from datetime import datetime
from typing import Protocol, runtime_checkable

from pydantic import BaseModel


class RawJob(BaseModel):
    """The common shape every source maps its response into, before normalization."""
    source_job_id: str
    title: str
    url: str
    description: str = ""
    company: str | None = None
    location: str | None = None
    posted_at: datetime | None = None


@runtime_checkable
class JobSource(Protocol):
    name: str
    is_scraped: bool  # scraped sources lose to sanctioned APIs on dedup

    async def fetch(self, query: str, location: str | None = None) -> list[RawJob]: ...


# The canonical set of source identifiers the system knows about. build_sources()
# registers a subset of these (only the ones enabled + credentialed for a given
# deployment); API request validation (schemas.job.IngestRequest) checks user-supplied
# names against this set so a typo or wrong case fails loudly instead of being silently
# swallowed as a KeyError inside the worker.
KNOWN_SOURCES: frozenset[str] = frozenset({"adzuna", "jooble", "indeed"})
