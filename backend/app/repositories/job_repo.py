from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job


class JobRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def search_by_vector(self, query_vector: list[float], limit: int = 20) -> list[Job]:
        """Nearest jobs to the query embedding by cosine distance (ORM objects)."""
        res = await self.db.execute(
            select(Job).order_by(Job.embedding.cosine_distance(query_vector)).limit(limit)
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
