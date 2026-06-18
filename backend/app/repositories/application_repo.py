from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.application import ApplicationStatus, JobApplication


class ApplicationRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        user_id: UUID,
        job_id: UUID,
        status: ApplicationStatus = ApplicationStatus.saved,
        notes: str | None = None,
        cv_id: UUID | None = None,
    ) -> JobApplication:
        """Insert a new application row.

        Sets ``applied_at`` immediately when the initial status is ``applied``.
        The caller's unit of work commits.
        """
        application = JobApplication(
            user_id=user_id,
            job_id=job_id,
            cv_id=cv_id,
            status=status,
            notes=notes,
            applied_at=datetime.now(timezone.utc) if status == ApplicationStatus.applied else None,
        )
        self.db.add(application)
        await self.db.flush()  # populate id / created_at / updated_at; commit stays with caller
        return application

    async def get_by_id(self, application_id: UUID) -> JobApplication | None:
        return await self.db.get(JobApplication, application_id)

    async def list_by_user(
        self,
        user_id: UUID,
        *,
        status: ApplicationStatus | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[JobApplication]:
        """Return applications for a user, ordered by updated_at DESC.

        When ``status`` is provided only applications with that status are
        returned. Pagination is controlled by ``limit`` / ``offset``.
        """
        stmt = (
            select(JobApplication)
            .where(JobApplication.user_id == user_id)
            .order_by(JobApplication.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        if status is not None:
            stmt = stmt.where(JobApplication.status == status)
        res = await self.db.execute(stmt)
        return list(res.scalars())

    async def update_status(
        self,
        application: JobApplication,
        status: ApplicationStatus,
        notes: str | None = None,
    ) -> JobApplication:
        """Mutate ``application`` in place and flush.

        ``applied_at`` is stamped the first time status becomes ``applied``; a
        second transition to ``applied`` does not overwrite the original
        timestamp. Pass ``notes=None`` to leave the existing notes unchanged.
        """
        if status == ApplicationStatus.applied and application.applied_at is None:
            application.applied_at = datetime.now(timezone.utc)
        application.status = status
        if notes is not None:
            application.notes = notes
        await self.db.flush()
        return application

    async def delete(self, application: JobApplication) -> None:
        await self.db.delete(application)
