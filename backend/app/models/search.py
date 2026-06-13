from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.search_result import SearchResult


class Search(Base):
    __tablename__ = "searches"
    id:         Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id:    Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    cv_id:      Mapped[UUID | None] = mapped_column(ForeignKey("cvs.id", ondelete="SET NULL"))
    prompt:     Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )
    results:    Mapped[list["SearchResult"]] = relationship(
        back_populates="search",
        cascade="all, delete-orphan",
        order_by="SearchResult.rank",
    )

    def __init__(self, **kwargs: object) -> None:
        if "id" not in kwargs:
            kwargs["id"] = uuid4()
        if "created_at" not in kwargs:
            kwargs["created_at"] = datetime.now(timezone.utc)
        super().__init__(**kwargs)
