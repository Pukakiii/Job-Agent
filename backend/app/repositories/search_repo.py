from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.search import Search
from app.models.search_result import SearchResult


class SearchRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_with_results(self, search_id: UUID) -> Search | None:
        # selectinload the results (and each result's job) to avoid N+1 queries
        # when the caller later accesses search.results / result.job.
        res = await self.db.execute(
            select(Search)
            .where(Search.id == search_id)
            .options(selectinload(Search.results).selectinload(SearchResult.job))
        )
        return res.scalar_one_or_none()

    async def list_by_user(self, user_id: UUID, limit: int = 20, offset: int = 0) -> list[Search]:
        res = await self.db.execute(
            select(Search)
            .where(Search.user_id == user_id)
            .order_by(Search.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(res.scalars())

    async def save_search(
        self,
        user_id: UUID,
        cv_id: UUID,
        prompt: str,
        ranked: list[tuple[UUID, float, str]],
    ) -> Search:
        search = Search(user_id=user_id, cv_id=cv_id, prompt=prompt)
        search.results = [
            SearchResult(job_id=job_id, rank=i + 1, score=score, explanation=explanation)
            for i, (job_id, score, explanation) in enumerate(ranked)
        ]
        self.db.add(search)
        await self.db.flush()  # populate search.id; the caller's unit of work commits
        return search
