from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.job import JobMatch


class SearchCreate(BaseModel):            # request body
    cv_id: UUID
    prompt: str


class SearchRead(BaseModel):              # response body: the search + its ranked matches
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    prompt: str
    created_at: datetime
    results: list[JobMatch]
