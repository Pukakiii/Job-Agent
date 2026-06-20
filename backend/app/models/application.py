import enum
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base
from app.models.job import Job


class ApplicationStatus(str, enum.Enum):
    """Lifecycle stages of a single job application.

    Values are intentionally kept identical to the frontend ApplicationStatus
    type in frontend/src/lib/api/applications.ts so the DB ENUM never rejects
    a value the API receives.
    """
    saved        = "saved"
    applied      = "applied"
    interview    = "interview"
    offer        = "offer"
    rejected     = "rejected"


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

    # Relationships
    # lazy="raise" prevents accidental implicit loads — always use selectinload explicitly.
    job: Mapped["Job"] = relationship("Job", lazy="raise")

    

    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="uq_application_user_job"),
    )
