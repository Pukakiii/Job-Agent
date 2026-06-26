from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cv import CV


class CVRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        user_id: UUID,
        s3_key: str,
        original_filename: str,
        content_type: str,
    ) -> CV:
        """Insert the metadata row for a newly uploaded CV.

        The service has already put the bytes in S3; extracted_text and
        parsed_profile are filled in later by set_parsing_result. The caller's
        unit of work commits.
        """
        cv = CV(
            user_id=user_id,
            s3_key=s3_key,
            original_filename=original_filename,
            content_type=content_type,
        )
        existing = await self.list_by_user(user_id, limit=1)
        if not existing:
            cv.is_active = True
        self.db.add(cv)
        await self.db.flush()  # populate cv.id / created_at; commit stays with the caller
        return cv

    async def get_by_id(self, cv_id: UUID) -> CV | None:
        res = await self.db.execute(select(CV).where(CV.id == cv_id))
        return res.scalar_one_or_none()

    async def list_by_user(self, user_id: UUID, limit: int = 20, offset: int = 0) -> list[CV]:
        res = await self.db.execute(
            select(CV)
            .where(CV.user_id == user_id)
            .order_by(CV.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(res.scalars())

    async def get_active_or_latest(self, user_id: UUID) -> CV | None:
        res = await self.db.execute(
            select(CV).where(CV.user_id == user_id, CV.is_active.is_(True))
        )
        active = res.scalar_one_or_none()
        if active is not None:
            return active
        cvs = await self.list_by_user(user_id, limit=1)
        return cvs[0] if cvs else None

    async def set_active(self, user_id: UUID, cv_id: UUID) -> CV | None:
        cv = await self.get_by_id(cv_id)
        if cv is None or cv.user_id != user_id:
            return None
        await self.db.execute(
            update(CV).where(CV.user_id == user_id).values(is_active=False)
        )
        await self.db.execute(
            update(CV).where(CV.id == cv_id).values(is_active=True)
        )
        await self.db.flush()
        return await self.get_by_id(cv_id)

    async def delete(self, cv: CV) -> None:
        await self.db.delete(cv)

    async def set_parsing_result(
        self,
        cv_id: UUID,
        extracted_text: str,
        parsed_profile: dict,
        embedding: list[float] | None = None,
    ) -> None:
        """Fill in the parsed fields once off-request CV parsing completes.

        `embedding` is the cached CV vector (None if embedding was skipped/failed —
        matching falls back to embedding the query text live)."""
        await self.db.execute(
            update(CV)
            .where(CV.id == cv_id)
            .values(
                extracted_text=extracted_text,
                parsed_profile=parsed_profile,
                embedding=embedding,
            )
        )

    async def s3_keys_for_user(self, user_id: UUID) -> list[str]:
        """The S3 keys to delete before erasing a user's rows (GDPR erasure)."""
        res = await self.db.execute(select(CV.s3_key).where(CV.user_id == user_id))
        return list(res.scalars())
