from app.core.config import settings
from app.integrations.postmark import PostmarkClient


async def test_send_email_noops_without_token():
    cfg = settings.model_copy(update={
        "POSTMARK_API_TOKEN": None,
        "POSTMARK_SENDER_EMAIL": None,
    })
    client = PostmarkClient(cfg)
    message_id = await client.send_email(
        "user@example.com",
        "Hello",
        "<p>Hi</p>",
        tag="test",
    )
    assert message_id.startswith("stub-")
