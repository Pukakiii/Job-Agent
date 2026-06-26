import enum
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class OutreachStatus(str, enum.Enum):
    draft = "draft"
    sent = "sent"
    failed = "failed"


class OutreachEmail(Base):
    __tablename__ = "outreach_emails"

    id:             Mapped[UUID]           = mapped_column(primary_key=True, default=uuid4)
    user_id:        Mapped[UUID]           = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    job_id:         Mapped[UUID | None]    = mapped_column(
        ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True
    )
    application_id: Mapped[UUID | None]    = mapped_column(
        ForeignKey("job_applications.id", ondelete="SET NULL"), nullable=True
    )
    to_address:     Mapped[str]            = mapped_column(Text, nullable=False)
    subject:        Mapped[str]            = mapped_column(Text, nullable=False)
    body:           Mapped[str]            = mapped_column(Text, nullable=False)
    status:         Mapped[OutreachStatus] = mapped_column(
        Enum(OutreachStatus, name="outreachstatus"),
        default=OutreachStatus.draft,
        nullable=False,
    )
    sent_at:        Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at:     Mapped[datetime]       = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
