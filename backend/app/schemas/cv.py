from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID

class CVProfile(BaseModel):
    """Structured representation of a CV's content, extracted by parsing the raw text.
    This is what powers the "semantic" part of our search: it's embedded and indexed
    in the DB, and used as context for generation.
    """
    model_config = ConfigDict(from_attributes=True)
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    summary: str | None = None
    experience: list[dict] | None = None  # each dict has "title", "company", "duration", "description"

class CVUploadResponse(BaseModel):        # never exposes s3_key
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    original_filename: str
    created_at: datetime

class CVRead(BaseModel):                  # list item - never exposes s3_key
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    original_filename: str
    content_type: str 
    created_at: datetime

class CVDownloadResponse(BaseModel): 
    url: str
    expires_in: int  
