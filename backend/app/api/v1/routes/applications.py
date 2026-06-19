"""REST endpoints for the job-applications resource.

Routes mirror the frontend client in frontend/src/lib/api/applications.ts:

  GET    /applications           → list (filter by status, paginate)
  POST   /applications           → create
  PUT    /applications/{id}      → update status / notes
  DELETE /applications/{id}      → delete
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_application_repo
from app.core.security import current_active_user
from app.models.application import ApplicationStatus
from app.models.user import User
from app.repositories.application_repo import ApplicationRepository
from app.schemas.application import ApplicationCreate, ApplicationRead, ApplicationUpdate

router = APIRouter(prefix="/applications", tags=["applications"])


# ── helpers ───────────────────────────────────────────────────────────────────

async def _get_own_application(
    application_id: UUID,
    user: User,
    repo: ApplicationRepository,
) -> "JobApplication":  # type: ignore[name-defined]  # noqa: F821
    """Fetch an application that belongs to the requesting user, or 404."""
    from app.models.application import JobApplication  # local import avoids cycle

    app = await repo.get_by_id(application_id)
    if app is None or app.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    return app


# ── endpoints ─────────────────────────────────────────────────────────────────

@router.get("", response_model=list[ApplicationRead])
async def list_applications(
    status: ApplicationStatus | None = None,
    limit: int = 20,
    offset: int = 0,
    user: User = Depends(current_active_user),
    repo: ApplicationRepository = Depends(get_application_repo),
):
    """Return the authenticated user's applications, newest first.

    Optionally filter by ``status``; supports ``limit`` / ``offset`` pagination.
    """
    return await repo.list_by_user(user.id, status=status, limit=limit, offset=offset)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ApplicationRead)
async def create_application(
    body: ApplicationCreate,
    user: User = Depends(current_active_user),
    repo: ApplicationRepository = Depends(get_application_repo),
):
    """Save a job to the user's application board.

    Raises 409 if a ``(user_id, job_id)`` application already exists.
    """
    from sqlalchemy.exc import IntegrityError

    try:
        app = await repo.create(
            user_id=user.id,
            job_id=body.job_id,
            status=body.status,
            notes=body.notes,
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Application for this job already exists",
        )
    return app


@router.put("/{application_id}", response_model=ApplicationRead)
async def update_application(
    application_id: UUID,
    body: ApplicationUpdate,
    user: User = Depends(current_active_user),
    repo: ApplicationRepository = Depends(get_application_repo),
):
    """Update the status (and optionally notes) of an application."""
    app = await _get_own_application(application_id, user, repo)
    return await repo.update_status(app, body.status, body.notes)


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application(
    application_id: UUID,
    user: User = Depends(current_active_user),
    repo: ApplicationRepository = Depends(get_application_repo),
):
    """Remove an application from the user's board."""
    app = await _get_own_application(application_id, user, repo)
    await repo.delete(app)
