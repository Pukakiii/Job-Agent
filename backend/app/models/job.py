from datetime import datetime
from uuid import UUID, uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Job(Base):
    __tablename__ = "jobs"
    id:            Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    source:        Mapped[str] = mapped_column(index=True)          # "adzuna", "indeed"…
    source_job_id: Mapped[str]                                      # id on the origin board
    content_hash:  Mapped[str] = mapped_column(index=True)          # cross-source dedup
    title:         Mapped[str]
    company:       Mapped[str | None]
    location:      Mapped[str | None]
    url:           Mapped[str]                                      # direct apply link (ADR-003)
    description:   Mapped[str] = mapped_column(Text)
    embedding:     Mapped[list[float]] = mapped_column(Vector(768)) # nomic-embed-text
    posted_at:     Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ingested_at:   Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint("source", "source_job_id", name="uq_job_origin"),)
