from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.deps import get_document_service
from app.core.security import current_active_user
from app.models.generated_document import DocumentType
from app.models.user import User
from app.schemas.document import DocumentGenerateRequest, DocumentRead
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/generate", status_code=status.HTTP_201_CREATED, response_model=DocumentRead)
async def generate_document(
    body: DocumentGenerateRequest,
    user: User = Depends(current_active_user),
    service: DocumentService = Depends(get_document_service),
):
    return await service.generate(user.id, body.job_id, body.doc_type, body.cv_id)


@router.get("", response_model=list[DocumentRead])
async def list_documents(
    doc_type: DocumentType | None = None,
    limit: int = 20,
    offset: int = 0,
    user: User = Depends(current_active_user),
    service: DocumentService = Depends(get_document_service),
):
    return await service.list(user.id, doc_type=doc_type, limit=limit, offset=offset)


@router.get("/{doc_id}", response_model=DocumentRead)
async def get_document(
    doc_id: UUID,
    user: User = Depends(current_active_user),
    service: DocumentService = Depends(get_document_service),
):
    return await service.get(user.id, doc_id)


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    doc_id: UUID,
    user: User = Depends(current_active_user),
    service: DocumentService = Depends(get_document_service),
):
    await service.delete(user.id, doc_id)
