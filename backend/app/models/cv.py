from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class CV(Base):
    __tablename__ = "cvs"
    id:                Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id:           Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    s3_key:            Mapped[str]                                  # location in S3, NOT the bytes
    original_filename: Mapped[str]
    content_type:      Mapped[str]
    extracted_text:    Mapped[str | None] = mapped_column(Text)     # filled after parsing
    parsed_profile:    Mapped[dict | None] = mapped_column(JSONB)   # validated CVProfile (see DTOs)
    created_at:        Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
