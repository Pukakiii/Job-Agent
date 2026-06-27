"""Tests for the AI provider split — chat and embeddings resolved independently."""

from unittest.mock import patch

import pytest

from app.core.config import settings
from app.integrations.ai_factory import clear_ai_caches, get_embedder
from app.integrations.embeddings import OllamaEmbedder, OpenAIEmbedder


@pytest.fixture(autouse=True)
def _clear_caches():
    clear_ai_caches()
    yield
    clear_ai_caches()


# ── endpoint resolution ─────────────────────────────────────────────────────

def test_chat_endpoint_ollama_cloud():
    with patch.multiple(
        settings,
        CHAT_PROVIDER="ollama",
        OLLAMA_BASE_URL="https://ollama.com",
        OLLAMA_API_KEY="key-123",
        OLLAMA_CHAT_MODEL="gpt-oss:120b",
    ):
        ep = settings.chat_endpoint()
    assert ep.base_url == "https://ollama.com/v1"
    assert ep.api_key == "key-123"
    assert ep.model == "gpt-oss:120b"
    assert ep.send_dimensions is False


def test_embed_endpoint_local_override_while_chat_is_cloud():
    # Setup A: chat hits the cloud, embeddings stay on a local Ollama.
    with patch.multiple(
        settings,
        EMBED_PROVIDER="ollama",
        OLLAMA_BASE_URL="https://ollama.com",
        OLLAMA_API_KEY="cloud-key",
        OLLAMA_EMBED_BASE_URL="http://localhost:11434",
        OLLAMA_EMBED_MODEL="nomic-embed-text",
    ):
        ep = settings.embed_endpoint()
    assert ep.base_url == "http://localhost:11434/v1"
    assert ep.model == "nomic-embed-text"
    assert ep.send_dimensions is False


def test_embed_endpoint_openai():
    # Setup B: embeddings via OpenAI (sends the Matryoshka dimensions param).
    with patch.multiple(
        settings,
        EMBED_PROVIDER="openai",
        OPENAI_API_KEY="sk-test",
        OPENAI_EMBED_MODEL="text-embedding-3-small",
    ):
        ep = settings.embed_endpoint()
    assert ep.base_url is None  # OpenAI default host
    assert ep.api_key == "sk-test"
    assert ep.model == "text-embedding-3-small"
    assert ep.send_dimensions is True


# ── embedder selection ──────────────────────────────────────────────────────

def test_embedder_is_ollama_when_embed_provider_ollama():
    with patch.object(settings, "EMBED_PROVIDER", "ollama"):
        clear_ai_caches()
        embedder = get_embedder()
    assert isinstance(embedder, OllamaEmbedder)


def test_embedder_is_openai_when_embed_provider_openai():
    with patch.multiple(settings, EMBED_PROVIDER="openai", OPENAI_API_KEY="sk-test"):
        clear_ai_caches()
        embedder = get_embedder()
    assert isinstance(embedder, OpenAIEmbedder)
