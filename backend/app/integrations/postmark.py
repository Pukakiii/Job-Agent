import logging
from uuid import uuid4

import httpx

from app.core.config import Settings

logger = logging.getLogger(__name__)


class PostmarkClient:
    """Thin Postmark API wrapper. No-ops when POSTMARK_API_TOKEN is unset."""

    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None):
        self.settings = settings
        self._client = client

    async def send_email(
        self,
        to: str,
        subject: str,
        html_body: str,
        *,
        tag: str | None = None,
    ) -> str:
        token = self.settings.POSTMARK_API_TOKEN
        sender = self.settings.POSTMARK_SENDER_EMAIL

        if not token or not sender:
            stub_id = f"stub-{uuid4()}"
            logger.info(
                "[POSTMARK] No-op send to=%s subject=%r id=%s",
                to,
                subject,
                stub_id,
            )
            return stub_id

        payload = {
            "From": sender,
            "To": to,
            "Subject": subject,
            "HtmlBody": html_body,
            "MessageStream": "outbound",
        }
        if tag:
            payload["Tag"] = tag

        async with httpx.AsyncClient() as client:
            res = await client.post(
                "https://api.postmarkapp.com/email",
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "X-Postmark-Server-Token": token,
                },
                json=payload,
                timeout=30.0,
            )
            res.raise_for_status()
            data = res.json()
            return str(data.get("MessageID", uuid4()))
