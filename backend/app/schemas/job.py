from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.integrations.sources.base import KNOWN_SOURCES


class JobRead(BaseModel):                 # public view of a posting — no embedding, no hash
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    title: str
    company: str | None
    location: str | None
    url: str


class JobDetail(JobRead):                 # single-job view: includes description + provenance
    description: str
    source: str
    posted_at: datetime | None
    ingested_at: datetime


class IngestRequest(BaseModel):
    query: str = Field(min_length=1)
    location: str | None = None
    sources: list[str] | None = Field(
        default=None,
        description=(
            "Restrict ingestion to specific sources (case-insensitive). "
            f"Known: {', '.join(sorted(KNOWN_SOURCES))}. Omit for all enabled sources."
        ),
    )

    @field_validator("sources")
    @classmethod
    def _normalise_sources(cls, value: list[str] | None) -> list[str] | None:
        """Lower-case + trim each name, drop duplicates, and reject unknown ones — so a
        typo or wrong case (e.g. "Jooble") fails with 422 instead of being silently
        swallowed as a KeyError in the worker. Validates against the universe of known
        sources, not the per-deployment enabled set (the request path can't see that)."""
        if value is None:
            return None
        normalised: list[str] = []
        for raw in value:
            name = raw.strip().lower()
            if name not in KNOWN_SOURCES:
                raise ValueError(
                    f"Unknown source {raw!r}. Valid sources: {', '.join(sorted(KNOWN_SOURCES))}."
                )
            if name not in normalised:
                normalised.append(name)
        return normalised


class IngestAccepted(BaseModel):
    job_id: str
    status: str = "queued"


class JobMatch(BaseModel):                # a search result for the API: posting + per-match data
    model_config = ConfigDict(from_attributes=True)
    job: JobRead
    rank: int
    score: float
    explanation: str

