from uuid import UUID

import anyio

from app.core.logger import get_logger
from app.exceptions import CVNotFound, LLMOutputInvalid
from app.integrations.openai_client import OpenAIClient
from app.integrations.s3 import S3
from app.integrations.text_extract import extract_text
from app.repositories.cv_repo import CVRepository
from app.schemas.cv import CVProfile

logger = get_logger("app.services.cv_parsing_service")

_SYSTEM_PROMPT = (
    "You extract structured data from a CV. Return ONLY a JSON object with keys: "
    "name, email, phone, summary, experience. 'experience' is a list of objects with "
    "keys title, company, duration, description. Use null when a field is unknown. "
    "Do not invent information that is not present in the CV."
)


class CVParsingService:
    """Off-request CV parsing: download the bytes, extract text (off-thread, since the
    parsers are blocking/CPU-bound), LLM-extract a structured profile, persist both
    onto the cvs row. HTTP-agnostic — raises domain exceptions."""

    def __init__(self, repo: CVRepository, s3: S3, openai: OpenAIClient):
        self.repo = repo
        self.s3 = s3
        self.openai = openai

    async def run(self, cv_id: UUID) -> None:
        cv = await self.repo.get_by_id(cv_id)
        if cv is None:
            raise CVNotFound(f"CV {cv_id} not found for parsing.")

        data = await self.s3.download_cv(cv.s3_key)
        # Blocking parse — never run it directly on the event loop.
        text = await anyio.to_thread.run_sync(extract_text, cv.content_type, data)

        profile = await self._extract_profile(text)
        await self.repo.set_parsing_result(cv_id, text, profile.model_dump())
        logger.info(
            "Parsed CV %s (%d chars, %d experiences)",
            cv_id, len(text), len(profile.experience or []),
        )

    async def _extract_profile(self, cv_text: str) -> CVProfile:
        raw = await self.openai.chat(
            system_prompt=_SYSTEM_PROMPT,
            user_prompt=f"CV text:\n\n{cv_text}",
            json_mode=True,
        )
        if not raw:
            raise LLMOutputInvalid("CV profile extraction returned no output.")
        try:
            return CVProfile.model_validate_json(raw)
        except ValueError as exc:  # pydantic ValidationError subclasses ValueError
            raise LLMOutputInvalid(f"CV profile JSON failed validation: {exc}") from exc
