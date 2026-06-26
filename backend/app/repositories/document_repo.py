from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.generated_document import DocumentType, GeneratedDocument


class DocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        user_id: UUID,
        job_id: UUID,
        cv_id: UUID | None,
        doc_type: DocumentType,
        content: str,
    ) -> GeneratedDocument:
        doc = GeneratedDocument(
            user_id=user_id,
            job_id=job_id,
            cv_id=cv_id,
            doc_type=doc_type,
            content=content,
        )
        self.db.add(doc)
        await self.db.flush()
        return doc

    async def get_by_id(self, doc_id: UUID) -> GeneratedDocument | None:
        res = await self.db.execute(
            select(GeneratedDocument).where(GeneratedDocument.id == doc_id)
        )
        return res.scalar_one_or_none()

    async def list_by_user(
        self,
        user_id: UUID,
        *,
        doc_type: DocumentType | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[GeneratedDocument]:
        stmt = select(GeneratedDocument).where(GeneratedDocument.user_id == user_id)
        if doc_type is not None:
            stmt = stmt.where(GeneratedDocument.doc_type == doc_type)
        stmt = stmt.order_by(GeneratedDocument.created_at.desc()).limit(limit).offset(offset)
        res = await self.db.execute(stmt)
        return list(res.scalars())

    async def delete(self, doc: GeneratedDocument) -> None:
        await self.db.delete(doc)
