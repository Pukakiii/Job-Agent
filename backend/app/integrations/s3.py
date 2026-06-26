import anyio
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from app.core.config import Settings
from app.core.logger import get_logger

logger = get_logger("app.integrations.s3")


class S3:
    """Abstraction over S3 interactions, to keep the rest of the codebase from
    depending on boto3 or any particular S3 client. boto3 is synchronous, so every
    call is offloaded to a worker thread to avoid blocking the event loop. Methods
    raise on failure and do no retries — the caller decides how to react (e.g.
    cleaning up a half-finished upload).
    """

    def __init__(self, bucket_name: str, settings: Settings):
        self.bucket_name = bucket_name
        self.sse = settings.S3_SSE  # e.g. "AES256" on real S3; None for MinIO w/o KMS
        client_kwargs = dict(
            aws_access_key_id=settings.MINIO_ROOT_USER,
            aws_secret_access_key=settings.MINIO_ROOT_PASSWORD,
            region_name=settings.S3_REGION,
            config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
        )
        # Client for byte I/O — talks to storage over whatever path the server uses.
        self.s3 = boto3.client("s3", endpoint_url=settings.S3_ENDPOINT_URL, **client_kwargs)

        # Client for presigning — must use a host the *client* (browser) can reach.
        # Falls back to the I/O endpoint; override via S3_PUBLIC_ENDPOINT_URL when
        # storage is on a private network (signing binds the host, so it can't be
        # swapped after the fact).
        public = settings.S3_PUBLIC_ENDPOINT_URL or settings.S3_ENDPOINT_URL
        self.presign_s3 = (
            self.s3
            if public == settings.S3_ENDPOINT_URL
            else boto3.client("s3", endpoint_url=public, **client_kwargs)
        )

    async def ensure_bucket(self) -> None:
        """Create the CV bucket if it does not exist (MinIO on fresh setup)."""

        def _ensure() -> None:
            try:
                self.s3.head_bucket(Bucket=self.bucket_name)
            except ClientError as exc:
                code = exc.response.get("Error", {}).get("Code", "")
                if code not in ("404", "NoSuchBucket", "403", "NotFound"):
                    raise
                self.s3.create_bucket(Bucket=self.bucket_name)
                logger.info("Created S3 bucket: %s", self.bucket_name)

        await anyio.to_thread.run_sync(_ensure)

    async def upload_cv(self, s3_key: str, file_bytes: bytes, content_type: str) -> None:
        """Put the CV bytes under the given key (encrypted at rest when S3_SSE is set)."""
        extra = {"ServerSideEncryption": self.sse} if self.sse else {}
        try:
            await anyio.to_thread.run_sync(
                lambda: self.s3.put_object(
                    Bucket=self.bucket_name,
                    Key=s3_key,
                    Body=file_bytes,
                    ContentType=content_type,
                    **extra,
                )
            )
            logger.info("Uploaded CV to S3: %s", s3_key)
        except ClientError:
            logger.exception("Failed to upload CV to S3: %s", s3_key)
            raise

    async def download_cv(self, s3_key: str) -> bytes:
        """Read the CV bytes back (used server-side by the parsing worker)."""

        def _get() -> bytes:
            obj = self.s3.get_object(Bucket=self.bucket_name, Key=s3_key)
            return obj["Body"].read()

        try:
            return await anyio.to_thread.run_sync(_get)
        except ClientError:
            logger.exception("Failed to download CV from S3: %s", s3_key)
            raise

    async def presign_get(self, s3_key: str, expires_in: int = 300) -> str:
        """Short-lived presigned GET URL handed to the client for direct download."""
        try:
            return await anyio.to_thread.run_sync(
                lambda: self.presign_s3.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": self.bucket_name, "Key": s3_key},
                    ExpiresIn=expires_in,
                )
            )
        except ClientError:
            logger.exception("Failed to presign CV URL: %s", s3_key)
            raise

    async def delete_objects(self, s3_keys: list[str]) -> None:
        """Delete a batch of objects (used by the GDPR user-deletion sweep)."""
        if not s3_keys:
            return
        try:
            await anyio.to_thread.run_sync(
                lambda: self.s3.delete_objects(
                    Bucket=self.bucket_name,
                    Delete={"Objects": [{"Key": k} for k in s3_keys]},
                )
            )
            logger.info("Deleted %d CV object(s) from S3", len(s3_keys))
        except ClientError:
            logger.exception("Failed to delete CV objects from S3")
            raise
