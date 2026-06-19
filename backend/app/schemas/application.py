"""Pydantic schemas for the job-applications resource.

Shapes align with the frontend ApplicationStatus type and the Application
interface in frontend/src/lib/api/applications.ts.
"""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.application import ApplicationStatus


# ── Request bodies ────────────────────────────────────────────────────────────

class ApplicationCreate(BaseModel):
    """POST /applications"""
    job_id: UUID
    status: ApplicationStatus = ApplicationStatus.saved
    notes: str | None = None


class ApplicationUpdate(BaseModel):
    """PUT /applications/{id}"""
    status: ApplicationStatus
    notes: str | None = None


# ── Response body ─────────────────────────────────────────────────────────────

class ApplicationRead(BaseModel):
    """Returned by every endpoint that surfaces an application."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_id: UUID
    cv_id: UUID | None
    status: ApplicationStatus
    notes: str | None
    applied_at: datetime | None
    created_at: datetime
    updated_at: datetime
