import boto3
import pytest
from botocore.exceptions import ClientError
from moto import mock_aws

from app.core.config import settings
from app.integrations.s3 import S3

KEY = "cvs/test/resume.pdf"
DATA = b"%PDF-1.4 fake cv bytes"


async def test_upload_then_download_roundtrips(s3):
    await s3.upload_cv(KEY, DATA, "application/pdf")
    assert await s3.download_cv(KEY) == DATA


async def test_delete_objects_removes_them(s3):
    await s3.upload_cv(KEY, DATA, "application/pdf")
    await s3.delete_objects([KEY])

    with pytest.raises(ClientError):  # NoSuchKey after delete
        await s3.download_cv(KEY)


async def test_delete_objects_noop_on_empty_list(s3):
    # must not raise / must not call S3 with an empty batch
    await s3.delete_objects([])


async def test_presign_get_returns_signed_url(s3):
    await s3.upload_cv(KEY, DATA, "application/pdf")
    url = await s3.presign_get(KEY, expires_in=60)

    assert KEY in url
    assert "X-Amz-Signature=" in url
    assert "X-Amz-Expires=60" in url


async def test_upload_with_sse_sends_header():
    """With S3_SSE set, the encryption header is sent (moto accepts it)."""
    with mock_aws():
        cfg = settings.model_copy(
            update={"S3_ENDPOINT_URL": None, "S3_PUBLIC_ENDPOINT_URL": None, "S3_SSE": "AES256"}
        )
        boto3.client("s3", region_name=cfg.S3_REGION).create_bucket(Bucket=cfg.S3_BUCKET_NAME)
        s3 = S3(cfg.S3_BUCKET_NAME, cfg)

        await s3.upload_cv(KEY, DATA, "application/pdf")

        head = s3.s3.head_object(Bucket=cfg.S3_BUCKET_NAME, Key=KEY)
        assert head["ServerSideEncryption"] == "AES256"
