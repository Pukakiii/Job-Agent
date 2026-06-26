from typing import AsyncIterator
from functools import lru_cache
from fastapi import Depends, Request

from sqlalchemy.ext.asyncio import AsyncSession
from arq.connections import ArqRedis

from app.core.db import async_session_factory
from app.core.config import settings
from app.integrations.ai_factory import get_chat_client, get_embedder
from app.integrations.s3 import S3
from app.repositories.cv_repo import CVRepository
from app.repositories.job_repo import JobRepository
from app.repositories.search_repo import SearchRepository
from app.repositories.application_repo import ApplicationRepository
from app.services.cv_service import CVService
from app.services.matching_service import MatchingService

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

def get_arq_redis(request: Request) -> ArqRedis:
    """The ARQ Redis pool opened in the app lifespan (used to enqueue background jobs)."""
    return request.app.state.redis


def get_matching_service(db: AsyncSession = Depends(get_db)) -> MatchingService:
    return MatchingService(
        CVRepository(db), JobRepository(db), SearchRepository(db),
        get_embedder(), get_chat_client(),
    )


def get_application_repo(
    db: AsyncSession = Depends(get_db),
) -> ApplicationRepository:
    return ApplicationRepository(db)
