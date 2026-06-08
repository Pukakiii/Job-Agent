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
        self.db.add(cv)
        await self.db.flush()  # populate cv.id / created_at; commit stays with the caller
        return cv

    async def get_by_id(self, cv_id: UUID) -> CV | None:
        res = await self.db.execute(select(CV).where(CV.id == cv_id))
        return res.scalar_one_or_none()

    async def list_by_user(self, user_id: UUID) -> list[CV]:
        res = await self.db.execute(
            select(CV).where(CV.user_id == user_id).order_by(CV.created_at.desc())
        )
        return list(res.scalars())

    async def set_parsing_result(
        self, cv_id: UUID, extracted_text: str, parsed_profile: dict
    ) -> None:
        """Fill in the parsed fields once off-request CV parsing completes."""
        await self.db.execute(
            update(CV)
            .where(CV.id == cv_id)
            .values(extracted_text=extracted_text, parsed_profile=parsed_profile)
        )

    async def s3_keys_for_user(self, user_id: UUID) -> list[str]:
        """The S3 keys to delete before erasing a user's rows (GDPR erasure)."""
        res = await self.db.execute(select(CV.s3_key).where(CV.user_id == user_id))
        return list(res.scalars())
