from functools import lru_cache
from pathlib import Path
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict

# Repo-root .env, resolved from this file so it loads regardless of CWD
# (config.py -> core -> app -> backend -> repo root). OS env vars still take
# precedence, so containers that inject env are unaffected.
_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str | None = None  # falls back to a per-environment default

    # Database settings
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_PORT: int = 9000
    MINIO_CONSOLE_PORT: int = 9001

    # S3 / object storage. S3_ENDPOINT_URL=None targets real AWS; set it
    # (e.g. http://localhost:9000 local, http://minio:9000 in Compose) for MinIO.
    S3_ENDPOINT_URL: str | None = None
    # Endpoint used only to build presigned URLs — must be reachable by the client
    # (browser). Defaults to S3_ENDPOINT_URL; override when storage sits on a private
    # network (e.g. MinIO at http://minio:9000 internally, public URL for clients).
    S3_PUBLIC_ENDPOINT_URL: str | None = None
    S3_BUCKET_NAME: str = "cvs"
    S3_REGION: str = "us-east-1"
    # Server-side encryption algorithm sent on upload (e.g. "AES256"). Leave unset
    # for local MinIO without a KMS; set to "AES256" against real AWS S3.
    S3_SSE: str | None = None

    @property
    def database_url(self) -> str:
        """Async SQLAlchemy URL, assembled from the POSTGRES_* parts."""
        user = quote_plus(self.POSTGRES_USER)
        password = quote_plus(self.POSTGRES_PASSWORD)
        return (
            f"postgresql+asyncpg://{user}:{password}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
