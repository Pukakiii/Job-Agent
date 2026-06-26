import logging
from uuid import UUID

from app.exceptions import CVNotFound, DocumentNotFound, JobNotFound, LLMOutputInvalid
from app.integrations.ai_factory import get_chat_client
from app.models.generated_document import DocumentType, GeneratedDocument
from app.repositories.cv_repo import CVRepository
from app.repositories.document_repo import DocumentRepository
from app.repositories.job_repo import JobRepository

logger = logging.getLogger(__name__)

_RESUME_PROMPT = """You are a professional resume writer. Tailor the candidate's CV for the job below.
Return only the tailored resume text in markdown — no preamble."""

_COVER_LETTER_PROMPT = """You are a professional cover-letter writer. Write a concise, tailored cover letter
for the candidate and job below. Return only the letter body — no preamble."""


class DocumentService:
    def __init__(
        self,
        doc_repo: DocumentRepository,
        job_repo: JobRepository,
        cv_repo: CVRepository,
    ):
        self.doc_repo = doc_repo
        self.job_repo = job_repo
        self.cv_repo = cv_repo
        self.chat = get_chat_client()

    async def generate(
        self,
        user_id: UUID,
        job_id: UUID,
        doc_type: DocumentType,
        cv_id: UUID | None = None,
    ) -> GeneratedDocument:
        job = await self.job_repo.get_by_id(job_id)
        if job is None:
            raise JobNotFound("Job not found.")

        cv = None
        if cv_id is not None:
            cv = await self.cv_repo.get_by_id(cv_id)
            if cv is None or cv.user_id != user_id:
                raise CVNotFound("CV not found.")
        else:
            cv = await self.cv_repo.get_active_or_latest(user_id)
            if cv is None:
                raise CVNotFound("Upload a CV before generating documents.")

        system_prompt = (
            _RESUME_PROMPT if doc_type == DocumentType.resume else _COVER_LETTER_PROMPT
        )
        user_prompt = (
            f"Job title: {job.title}\n"
            f"Company: {job.company or 'Unknown'}\n"
            f"Job description:\n{(job.description or '')[:6000]}\n\n"
            f"Candidate CV text:\n{(cv.extracted_text or '')[:6000]}"
        )

        content = await self.chat.chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=2048,
        )
        if not content:
            raise LLMOutputInvalid("Document generation failed.")

        return await self.doc_repo.create(
            user_id, job_id, cv.id, doc_type, content.strip()
        )

    async def list(
        self,
        user_id: UUID,
        *,
        doc_type: DocumentType | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[GeneratedDocument]:
        return await self.doc_repo.list_by_user(
            user_id, doc_type=doc_type, limit=limit, offset=offset
        )

    async def get(self, user_id: UUID, doc_id: UUID) -> GeneratedDocument:
        doc = await self.doc_repo.get_by_id(doc_id)
        if doc is None or doc.user_id != user_id:
            raise DocumentNotFound("Document not found.")
        return doc

    async def delete(self, user_id: UUID, doc_id: UUID) -> None:
        doc = await self.get(user_id, doc_id)
        await self.doc_repo.delete(doc)
