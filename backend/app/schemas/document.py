from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.generated_document import DocumentType


class DocumentGenerateRequest(BaseModel):
    job_id: UUID
    cv_id: UUID | None = None
    doc_type: DocumentType


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_id: UUID
    cv_id: UUID | None
    doc_type: DocumentType
    content: str
    created_at: datetime
