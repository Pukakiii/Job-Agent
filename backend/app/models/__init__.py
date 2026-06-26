from app.models.application import ApplicationStatus, JobApplication
from app.models.base import Base
from app.models.cv import CV
from app.models.generated_document import DocumentType, GeneratedDocument
from app.models.job import Job
from app.models.outreach_email import OutreachEmail, OutreachStatus
from app.models.search import Search
from app.models.search_result import SearchResult
from app.models.user import User

__all__ = [
    "Base",
    "User",
    "CV",
    "Job",
    "Search",
    "SearchResult",
    "ApplicationStatus",
    "JobApplication",
    "DocumentType",
    "GeneratedDocument",
    "OutreachStatus",
    "OutreachEmail",
]
