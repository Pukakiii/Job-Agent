import enum
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class DocumentType(str, enum.Enum):
    resume = "resume"
    cover_letter = "cover_letter"


class GeneratedDocument(Base):
    __tablename__ = "generated_documents"

    id:         Mapped[UUID]         = mapped_column(primary_key=True, default=uuid4)
    user_id:    Mapped[UUID]         = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    job_id:     Mapped[UUID]         = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"), index=True
    )
    cv_id:      Mapped[UUID | None]  = mapped_column(
        ForeignKey("cvs.id", ondelete="SET NULL"), nullable=True
    )
    doc_type:   Mapped[DocumentType] = mapped_column(
        Enum(DocumentType, name="documenttype"), nullable=False
    )
    content:    Mapped[str]          = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime]     = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
