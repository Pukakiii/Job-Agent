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
