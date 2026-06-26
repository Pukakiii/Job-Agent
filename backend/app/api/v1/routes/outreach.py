from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.deps import get_outreach_service
from app.core.security import current_active_user
from app.models.user import User
from app.schemas.outreach import (
    OutreachGenerateRequest,
    OutreachRead,
    OutreachSendRequest,
)
from app.services.outreach_service import OutreachService

router = APIRouter(prefix="/outreach", tags=["outreach"])


@router.post("/generate", status_code=status.HTTP_201_CREATED, response_model=OutreachRead)
async def generate_outreach(
    body: OutreachGenerateRequest,
    user: User = Depends(current_active_user),
    service: OutreachService = Depends(get_outreach_service),
):
    return await service.generate_draft(
        user.id,
        job_id=body.job_id,
        to_address=body.to_address,
        context=body.context,
    )


@router.post("/send", status_code=status.HTTP_201_CREATED, response_model=OutreachRead)
async def send_outreach(
    body: OutreachSendRequest,
    user: User = Depends(current_active_user),
    service: OutreachService = Depends(get_outreach_service),
):
    row = await service.create_and_send(
        user.id,
        to_address=body.to_address,
        subject=body.subject,
        body=body.body,
        job_id=body.job_id,
    )
    return row


@router.get("", response_model=list[OutreachRead])
async def list_outreach(
    limit: int = 20,
    offset: int = 0,
    user: User = Depends(current_active_user),
    service: OutreachService = Depends(get_outreach_service),
):
    return await service.list(user.id, limit=limit, offset=offset)


@router.get("/{email_id}", response_model=OutreachRead)
async def get_outreach(
    email_id: UUID,
    user: User = Depends(current_active_user),
    service: OutreachService = Depends(get_outreach_service),
):
    return await service.get(user.id, email_id)
