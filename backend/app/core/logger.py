import logging
import sys

from app.core.config import settings

_DEFAULT_LEVEL = "DEBUG" if settings.ENVIRONMENT == "development" else "INFO"
_LOG_FORMAT = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"
_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


def configure_logging() -> None:
    """Set up root logging. Call once at API and worker startup."""
    level_name = (settings.LOG_LEVEL or _DEFAULT_LEVEL).upper()
    level = getattr(logging, level_name, logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

    # Quiet noisy third-party loggers; raise these deliberately when debugging.
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("aiosqlite").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Module-level logger: `log = get_logger(__name__)`."""
    return logging.getLogger(name)
