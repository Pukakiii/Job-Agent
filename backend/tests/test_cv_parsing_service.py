import io
import json

import pytest
from docx import Document

from app.exceptions import LLMOutputInvalid
from app.models.user import User
from app.repositories.cv_repo import CVRepository
from app.services.cv_parsing_service import CVParsingService

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


class FakeS3:
    def __init__(self, data: bytes):
        self._data = data

    async def download_cv(self, s3_key: str) -> bytes:
        return self._data


class FakeChat:
    def __init__(self, reply):
        self._reply = reply

    async def chat(self, *, system_prompt, user_prompt, json_mode=False, **kw):
        return self._reply


def _docx_bytes(*paragraphs: str) -> bytes:
    buf = io.BytesIO()
    doc = Document()
    for p in paragraphs:
        doc.add_paragraph(p)
    doc.save(buf)
    return buf.getvalue()


async def _make_cv(db) -> "tuple":
    user = User(email="parse@test.io", hashed_password="x",
                is_active=True, is_superuser=False, is_verified=False)
    db.add(user)
    await db.flush()
    cv = await CVRepository(db).create(user.id, f"cvs/{user.id}/a.docx", "a.docx", DOCX_MIME)
    return cv


async def test_run_persists_text_and_profile(db):
    cv = await _make_cv(db)
    reply = json.dumps({
        "name": "Jane", "email": None, "phone": None, "summary": "Py dev",
        "experience": [{"title": "Dev", "company": "ACME", "duration": "2y", "description": "x"}],
    })
    service = CVParsingService(CVRepository(db), FakeS3(_docx_bytes("Jane Doe", "Python")), FakeChat(reply))
    await service.run(cv.id)
    await db.flush()

    refreshed = await CVRepository(db).get_by_id(cv.id)
    assert "Jane Doe" in refreshed.extracted_text
    assert refreshed.parsed_profile["name"] == "Jane"
    assert refreshed.parsed_profile["experience"][0]["company"] == "ACME"


async def test_run_raises_on_invalid_llm_json(db):
    cv = await _make_cv(db)
    service = CVParsingService(CVRepository(db), FakeS3(_docx_bytes("X")), FakeChat("not json at all"))
    with pytest.raises(LLMOutputInvalid):
        await service.run(cv.id)
