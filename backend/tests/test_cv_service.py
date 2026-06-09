from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.core.config import settings
from app.exceptions import CVFileTooLarge, CVNotFound, EmptyCVFile, UnsupportedCVType
from app.services.cv_service import CVService

PDF_BYTES = b"%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF\n"


class FakeCVRepo:
    def __init__(self):
        self.rows = {}
        self.fail_create = False

    async def create(self, user_id, s3_key, original_filename, content_type):
        if self.fail_create:
            raise RuntimeError("db boom")
        cv = SimpleNamespace(id=uuid4(), user_id=user_id, s3_key=s3_key,
                             original_filename=original_filename, content_type=content_type)
        self.rows[cv.id] = cv
        return cv

    async def get_by_id(self, cv_id):
        return self.rows.get(cv_id)

    async def list_by_user(self, user_id, limit=20, offset=0):
        rows = [c for c in self.rows.values() if c.user_id == user_id]
        return rows[offset:offset + limit]

    async def delete(self, cv):
        self.rows.pop(cv.id, None)


class FakeS3:
    def __init__(self):
        self.objects = {}
        self.deleted = []

    async def upload_cv(self, s3_key, file_bytes, content_type):
        self.objects[s3_key] = file_bytes

    async def presign_get(self, s3_key, expires_in=300):
        return f"https://signed.example/{s3_key}?exp={expires_in}"

    async def delete_objects(self, s3_keys):
        self.deleted.extend(s3_keys)
        for k in s3_keys:
            self.objects.pop(k, None)


def make_service(cfg=settings):
    repo, s3 = FakeCVRepo(), FakeS3()
    return CVService(repo, s3, cfg), repo, s3


async def test_upload_pdf_stores_bytes_and_creates_row():
    service, repo, s3 = make_service()
    uid = uuid4()
    cv = await service.upload(uid, "resume.pdf", PDF_BYTES)
    assert cv.content_type == "application/pdf"
    assert cv.s3_key.startswith(f"cvs/{uid}/") and cv.s3_key.endswith(".pdf")
    assert s3.objects[cv.s3_key] == PDF_BYTES


async def test_upload_empty_rejected():
    service, *_ = make_service()
    with pytest.raises(EmptyCVFile):
        await service.upload(uuid4(), "x.pdf", b"")


async def test_upload_too_large_rejected():
    small = settings.model_copy(update={"CV_MAX_BYTES": 10})
    service, *_ = make_service(small)
    with pytest.raises(CVFileTooLarge):
        await service.upload(uuid4(), "big.pdf", PDF_BYTES)  # > 10 bytes


async def test_upload_unsupported_type_rejected():
    service, *_ = make_service()
    with pytest.raises(UnsupportedCVType):
        await service.upload(uuid4(), "notes.txt", b"just plain text, not a document")


async def test_upload_sweeps_orphan_on_db_failure():
    service, repo, s3 = make_service()
    repo.fail_create = True
    with pytest.raises(RuntimeError):
        await service.upload(uuid4(), "resume.pdf", PDF_BYTES)
    assert len(s3.deleted) == 1 and s3.objects == {}  # object removed after row failed


async def test_get_download_url_enforces_ownership():
    service, repo, s3 = make_service()
    uid = uuid4()
    cv = await service.upload(uid, "resume.pdf", PDF_BYTES)
    url, ttl = await service.get_download_url(uid, cv.id)
    assert cv.s3_key in url and ttl == settings.CV_DOWNLOAD_URL_TTL_SECONDS
    with pytest.raises(CVNotFound):
        await service.get_download_url(uuid4(), cv.id)   # not the owner
    with pytest.raises(CVNotFound):
        await service.get_download_url(uid, uuid4())      # missing


async def test_delete_removes_object_then_row():
    service, repo, s3 = make_service()
    uid = uuid4()
    cv = await service.upload(uid, "resume.pdf", PDF_BYTES)
    await service.delete(uid, cv.id)
    assert cv.s3_key in s3.deleted
    assert await repo.get_by_id(cv.id) is None
    with pytest.raises(CVNotFound):
        await service.delete(uid, cv.id)  # already gone