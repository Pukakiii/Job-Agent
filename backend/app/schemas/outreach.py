from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.outreach_email import OutreachStatus


class OutreachGenerateRequest(BaseModel):
    to_address: str = Field(min_length=3)
    job_id: UUID | None = None
    context: str = ""


class OutreachSendRequest(BaseModel):
    to_address: str = Field(min_length=3)
    subject: str = Field(min_length=1)
    body: str = Field(min_length=1)
    job_id: UUID | None = None


class OutreachRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_id: UUID | None
    application_id: UUID | None
    to_address: str
    subject: str
    body: str
    status: OutreachStatus
    sent_at: datetime | None
    created_at: datetime
