import logging
from uuid import UUID

from app.core.config import Settings
from app.exceptions import JobNotFound, LLMOutputInvalid, OutreachNotFound
from app.integrations.ai_factory import get_chat_client
from app.integrations.postmark import PostmarkClient
from app.models.outreach_email import OutreachEmail, OutreachStatus
from app.repositories.job_repo import JobRepository
from app.repositories.outreach_repo import OutreachRepository

logger = logging.getLogger(__name__)

_DRAFT_PROMPT = """You are helping a job seeker write a professional outreach email to a recruiter
or hiring manager. Return JSON with keys: subject, body. Keep it concise and specific to the role."""


class OutreachService:
    def __init__(
        self,
        repo: OutreachRepository,
        job_repo: JobRepository,
        postmark: PostmarkClient,
        settings: Settings,
    ):
        self.repo = repo
        self.job_repo = job_repo
        self.postmark = postmark
        self.settings = settings
        self.chat = get_chat_client()

    async def generate_draft(
        self,
        user_id: UUID,
        *,
        job_id: UUID | None = None,
        to_address: str,
        context: str = "",
    ) -> OutreachEmail:
        job_text = ""
        if job_id is not None:
            job = await self.job_repo.get_by_id(job_id)
            if job is None:
                raise JobNotFound("Job not found.")
            job_text = (
                f"Role: {job.title}\nCompany: {job.company or 'Unknown'}\n"
                f"Description:\n{(job.description or '')[:4000]}"
            )

        raw = await self.chat.chat(
            system_prompt=_DRAFT_PROMPT,
            user_prompt=f"{job_text}\n\nAdditional context:\n{context}",
            json_mode=True,
        )
        if not raw:
            raise LLMOutputInvalid("Email draft generation failed.")

        import json

        try:
            payload = json.loads(raw)
            subject = str(payload.get("subject", "Follow-up"))
            body = str(payload.get("body", ""))
        except (json.JSONDecodeError, TypeError):
            subject = "Follow-up"
            body = raw

        return await self.repo.create(
            user_id,
            to_address=to_address,
            subject=subject,
            body=body,
            job_id=job_id,
            status=OutreachStatus.draft,
        )

    async def list(
        self,
        user_id: UUID,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> list[OutreachEmail]:
        return await self.repo.list_by_user(user_id, limit=limit, offset=offset)

    async def get(self, user_id: UUID, email_id: UUID) -> OutreachEmail:
        row = await self.repo.get_by_id(email_id)
        if row is None or row.user_id != user_id:
            raise OutreachNotFound("Outreach email not found.")
        return row

    async def send(self, user_id: UUID, email_id: UUID) -> OutreachEmail:
        row = await self.get(user_id, email_id)
        message_id = await self.postmark.send_email(
            row.to_address,
            row.subject,
            row.body,
            tag="outreach",
        )
        logger.info("Outreach email queued/sent: %s", message_id)
        return await self.repo.mark_sent(row)

    async def create_and_send(
        self,
        user_id: UUID,
        *,
        to_address: str,
        subject: str,
        body: str,
        job_id: UUID | None = None,
    ) -> OutreachEmail:
        row = await self.repo.create(
            user_id,
            to_address=to_address,
            subject=subject,
            body=body,
            job_id=job_id,
            status=OutreachStatus.draft,
        )
        return await self.send(user_id, row.id)
