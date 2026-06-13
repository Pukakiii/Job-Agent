from uuid import UUID

from arq.connections import ArqRedis
from fastapi import APIRouter, Depends, UploadFile, status

from app.api.deps import get_arq_redis, get_cv_service
from app.core.security import current_active_user
from app.models.user import User
from app.schemas.cv import CVDownloadResponse, CVRead, CVUploadResponse
from app.services.cv_service import CVService
from app.workers.tasks import enqueue_parse_cv

router = APIRouter(prefix="/cvs", tags=["cvs"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=CVUploadResponse)
async def upload_cv(
    file: UploadFile,
    user: User = Depends(current_active_user),
    service: CVService = Depends(get_cv_service),
    redis: ArqRedis = Depends(get_arq_redis),
):
    content = await file.read()
    cv = await service.upload(user.id, file.filename or "cv", content)
    await enqueue_parse_cv(redis, str(cv.id))
    return cv


@router.get("", response_model=list[CVRead])
async def list_cvs(
    limit: int = 20,
    offset: int = 0,
    user: User = Depends(current_active_user),
    service: CVService = Depends(get_cv_service),
):
    return await service.list(user.id, limit=limit, offset=offset)


@router.get("/{cv_id}/download", response_model=CVDownloadResponse)
async def download_cv(
    cv_id: UUID,
    user: User = Depends(current_active_user),
    service: CVService = Depends(get_cv_service),
):
    url, expires_in = await service.get_download_url(user.id, cv_id)
    return CVDownloadResponse(url=url, expires_in=expires_in)


@router.delete("/{cv_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cv(
    cv_id: UUID,
    user: User = Depends(current_active_user),
    service: CVService = Depends(get_cv_service),
):
    await service.delete(user.id, cv_id)