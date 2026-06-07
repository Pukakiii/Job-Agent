from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.job import Job
    from app.models.search import Search


class SearchResult(Base):
    __tablename__ = "search_results"
    search_id:   Mapped[UUID] = mapped_column(ForeignKey("searches.id", ondelete="CASCADE"), primary_key=True)
    job_id:      Mapped[UUID] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), primary_key=True)
    rank:        Mapped[int]
    score:       Mapped[float]
    explanation: Mapped[str] = mapped_column(Text)
    search:      Mapped["Search"] = relationship(back_populates="results")
    job:         Mapped["Job"] = relationship()
