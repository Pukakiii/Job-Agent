from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.countries import parse_location
from app.models.job import Job


class JobRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def search_by_vector(
        self,
        query_vector: list[float],
        limit: int = 20,
        location: str | None = None,
        include_remote: bool = False,
    ) -> list[Job]:
        """Nearest jobs to the query embedding by cosine distance (ORM objects).

        When `location` is given (e.g. "Warszawa, PL"), restrict to jobs whose location
        matches the city token OR the country name — boards label inconsistently (Jooble
        returns coarse "Poland", Indeed returns "Warszawa"), so matching either keeps both.
        Rank by cosine within that subset. `include_remote` additionally keeps remote
        listings. Jobs with a NULL location are excluded (location can't be confirmed)."""
        stmt = select(Job)
        city, _, country_name = parse_location(location)
        if city:
            clauses = [Job.location.ilike(f"%{city}%")]
            if country_name:
                clauses.append(Job.location.ilike(f"%{country_name}%"))
            if include_remote:
                clauses.append(Job.location.ilike("%remote%"))
            stmt = stmt.where(or_(*clauses))
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
