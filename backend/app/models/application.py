import enum
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ApplicationStatus(str, enum.Enum):
    """Lifecycle stages of a single job application."""
    saved        = "saved"
    applied      = "applied"
    interviewing = "interviewing"
    offered      = "offered"
    rejected     = "rejected"
    withdrawn    = "withdrawn"


class JobApplication(Base):
    """One row per (user, job) application attempt.

    ``cv_id`` is nullable — a user may save a job before deciding which CV to
    use.  The service layer is responsible for setting ``applied_at`` when the
    status transitions to ``ApplicationStatus.applied``.
    """
    __tablename__ = "job_applications"

    id:         Mapped[UUID]              = mapped_column(primary_key=True, default=uuid4)
    user_id:    Mapped[UUID]              = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    job_id:     Mapped[UUID]              = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"), index=True
    )
    cv_id:      Mapped[UUID | None]       = mapped_column(
        ForeignKey("cvs.id", ondelete="SET NULL"), index=True, nullable=True
    )
    status:     Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus, name="applicationstatus"),
        default=ApplicationStatus.saved,
        nullable=False,
    )
    applied_at: Mapped[datetime | None]   = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    notes:      Mapped[str | None]        = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime]          = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime]          = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="uq_application_user_job"),
    )
