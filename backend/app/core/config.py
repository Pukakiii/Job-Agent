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

    # Auth 
    SECRET_KEY: str 
    ACCESS_TOKEN_LIFETIME_SECONDS: int = 60 * 60 * 24 * 7 # 7 days - persistent sessions
    COOKIE_NAME: str = "jobagent_auth" 
    COOKIE_SECURE: bool = False # set True in production (HTTPS-only cookie)
    FRONTEND_URL: str = "http://localhost:3000" # CORS origin allowed to send the auth cookie

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

    # CV upload
    CV_MAX_BYTES: int = 10 * 1024 * 1024  # 10 MB hard cap
    CV_ALLOWED_MIME: set[str] = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # docx
    }
    CV_DOWNLOAD_URL_TTL_SECONDS: int = 300  # presigned GET lifetime

    # AI — OpenAI (optional; leave OPENAI_API_KEY unset to disable)
    OPENAI_API_KEY: str | None = None
    OPENAI_CHAT_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBED_MODEL: str = "text-embedding-3-small"

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
