from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_matching_service
from app.core.security import current_active_user
from app.exceptions import SearchNotFound
from app.models.user import User
from app.repositories.search_repo import SearchRepository
from app.schemas.search import SearchCreate, SearchRead, SearchSummary
from app.services.matching_service import MatchingService

router = APIRouter(prefix="/searches", tags=["searches"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=SearchRead)
async def create_search(
    body: SearchCreate,
    user: User = Depends(current_active_user),
    service: MatchingService = Depends(get_matching_service),
):
    return await service.find_matches(user.id, body.cv_id, body.prompt)


@router.get("", response_model=list[SearchSummary])
async def list_searches(
    limit: int = 20,
    offset: int = 0,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await SearchRepository(db).list_by_user(user.id, limit=limit, offset=offset)


@router.get("/{search_id}", response_model=SearchRead)
async def get_search(
    search_id: UUID,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
):
    search = await SearchRepository(db).get_with_results(search_id)
    if search is None or search.user_id != user.id:
        raise SearchNotFound("Search not found.")
    return search
