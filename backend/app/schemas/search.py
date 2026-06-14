from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.job import JobMatch


class SearchCreate(BaseModel):            # request body
    cv_id: UUID
    prompt: str
    location: str | None = None           # restrict matches to this location (city token)
    include_remote: bool = False          # also include remote listings when location is set


class SearchSummary(BaseModel):           # list item — no results payload
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    prompt: str
    created_at: datetime


class SearchRead(BaseModel):              # response body: the search + its ranked matches
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    prompt: str
    created_at: datetime
    results: list[JobMatch]
