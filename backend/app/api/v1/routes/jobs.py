from uuid import UUID

from arq.connections import ArqRedis
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_arq_redis, get_db
from app.core.security import current_active_user
from app.exceptions import JobNotFound
from app.models.user import User
from app.repositories.job_repo import JobRepository
from app.schemas.job import IngestAccepted, IngestRequest, JobDetail, JobRead
from app.workers.tasks import enqueue_scrape

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=list[JobRead])
async def list_jobs(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await JobRepository(db).list_jobs(limit=limit, offset=offset)


@router.post("/ingest", status_code=status.HTTP_202_ACCEPTED, response_model=IngestAccepted)
async def ingest_jobs(
    body: IngestRequest,
    user: User = Depends(current_active_user),
    redis: ArqRedis = Depends(get_arq_redis),
):
    job_id = await enqueue_scrape(redis, body.query, location=body.location, sources=body.sources)
    return IngestAccepted(job_id=job_id)


@router.get("/{job_id}", response_model=JobDetail)
async def get_job(
    job_id: UUID,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
):
    job = await JobRepository(db).get_by_id(job_id)
    if job is None:
        raise JobNotFound("Job not found.")
    return job
