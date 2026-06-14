from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job


class JobRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def search_by_vector(
        self, query_vector: list[float], limit: int = 20, location: str | None = None
    ) -> list[Job]:
        """Nearest jobs to the query embedding by cosine distance (ORM objects).

        When `location` is given, restrict to jobs whose location matches it (case-
        insensitive substring) or are remote; rank by cosine within that subset. Jobs
        with a NULL location are excluded by the filter (location can't be confirmed)."""
        stmt = select(Job)
        if location and location.strip():
            like = f"%{location.strip()}%"
            stmt = stmt.where(or_(Job.location.ilike(like), Job.location.ilike("%remote%")))
        stmt = stmt.order_by(Job.embedding.cosine_distance(query_vector)).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.scalars())

    async def get_by_id(self, job_id: UUID) -> Job | None:
        """Return the Job with the given id, or None if not found."""
        return await self.db.get(Job, job_id)

    async def list_jobs(self, limit: int = 20, offset: int = 0) -> list[Job]:
        """Jobs ordered by ingested_at DESC, id; paginated by limit/offset."""
        res = await self.db.execute(
            select(Job).order_by(Job.ingested_at.desc(), Job.id).limit(limit).offset(offset)
        )
        return list(res.scalars())

    async def get_by_id(self, job_id: UUID) -> Job | None:
        """Return the Job with the given id, or None if not found."""
        return await self.db.get(Job, job_id)

    async def list_jobs(self, limit: int = 20, offset: int = 0) -> list[Job]:
        """Jobs ordered by ingested_at DESC, id; paginated by limit/offset."""
        res = await self.db.execute(
            select(Job).order_by(Job.ingested_at.desc(), Job.id).limit(limit).offset(offset)
        )
        return list(res.scalars())

    async def upsert_many(self, rows: list[dict]) -> None:
        """Idempotently insert or update a batch of jobs, keyed by (source, source_job_id)."""
        stmt = insert(Job).values(rows)
        stmt = stmt.on_conflict_do_update(
            constraint="uq_job_origin",
            set_={
                "title": stmt.excluded.title,
                "description": stmt.excluded.description,
                "embedding": stmt.excluded.embedding,
                "ingested_at": func.now(),
            },
        )
        await self.db.execute(stmt)
