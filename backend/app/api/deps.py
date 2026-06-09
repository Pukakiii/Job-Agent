from typing import AsyncIterator
from functools import lru_cache
from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import async_session_factory
from app.core.config import settings
from app.integrations.s3 import S3
from app.repositories.cv_repo import CVRepository
from app.services.cv_service import CVService

async def get_db() -> AsyncIterator[AsyncSession]:
    """Request/task-scoped unit of work: commit on success, roll back on error."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

@lru_cache 
def get_s3() -> S3:
    # One boto3-backed client, reused across requests (thread-safe, no per-call cost).
    return S3(settings.S3_BUCKET_NAME, settings)

def get_cv_service(
    db: AsyncSession = Depends(get_db),
    s3: S3 = Depends(get_s3),
) -> CVService:
    return CVService(CVRepository(db), s3, settings)

