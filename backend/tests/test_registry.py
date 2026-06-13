import httpx

from app.core.config import settings
from app.workers.registry import build_sources


def _client() -> httpx.AsyncClient:
    return httpx.AsyncClient()


def test_build_sources_excludes_disabled():
    cfg = settings.model_copy(update={"ADZUNA_ENABLED": False, "JOOBLE_ENABLED": False, "INDEED_ENABLED": False})
    assert build_sources(_client(), cfg) == {}


def test_build_sources_excludes_missing_credentials():
    cfg = settings.model_copy(
        update={
            "ADZUNA_ENABLED": True, "ADZUNA_APP_ID": None, "ADZUNA_APP_KEY": None,
            "JOOBLE_ENABLED": True, "JOOBLE_API_KEY": None,
            "INDEED_ENABLED": True, "APIFY_API_TOKEN": None,
        }
    )
    assert build_sources(_client(), cfg) == {}


def test_build_sources_includes_adzuna_when_credentialed():
    cfg = settings.model_copy(
        update={
            "ADZUNA_ENABLED": True, "ADZUNA_APP_ID": "id", "ADZUNA_APP_KEY": "key",
            "JOOBLE_ENABLED": False,
            "INDEED_ENABLED": False,
        }
    )
    sources = build_sources(_client(), cfg)
    assert set(sources) == {"adzuna"}
    assert sources["adzuna"].is_scraped is False


def test_build_sources_indeed_requires_token():
    cfg = settings.model_copy(
        update={
            "ADZUNA_ENABLED": False,
            "JOOBLE_ENABLED": False,
            "INDEED_ENABLED": True, "APIFY_API_TOKEN": "tok",
        }
    )
    sources = build_sources(_client(), cfg)
    assert set(sources) == {"indeed"}
    assert sources["indeed"].is_scraped is True
