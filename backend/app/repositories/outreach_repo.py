from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.outreach_email import OutreachEmail, OutreachStatus


class OutreachRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        user_id: UUID,
        *,
        to_address: str,
        subject: str,
        body: str,
        job_id: UUID | None = None,
        application_id: UUID | None = None,
        status: OutreachStatus = OutreachStatus.draft,
        sent_at: datetime | None = None,
    ) -> OutreachEmail:
        row = OutreachEmail(
            user_id=user_id,
            job_id=job_id,
            application_id=application_id,
            to_address=to_address,
            subject=subject,
            body=body,
            status=status,
            sent_at=sent_at,
        )
        self.db.add(row)
        await self.db.flush()
        return row

    async def get_by_id(self, email_id: UUID) -> OutreachEmail | None:
        res = await self.db.execute(
            select(OutreachEmail).where(OutreachEmail.id == email_id)
        )
        return res.scalar_one_or_none()

    async def list_by_user(
        self,
        user_id: UUID,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> list[OutreachEmail]:
        res = await self.db.execute(
            select(OutreachEmail)
            .where(OutreachEmail.user_id == user_id)
            .order_by(OutreachEmail.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(res.scalars())

    async def mark_sent(self, email: OutreachEmail) -> OutreachEmail:
        email.status = OutreachStatus.sent
        email.sent_at = datetime.now(timezone.utc)
        await self.db.flush()
        return email

    async def delete(self, email: OutreachEmail) -> None:
        await self.db.delete(email)
