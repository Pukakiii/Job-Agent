"""Tests for Ollama vs OpenAI AI provider selection."""

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


def test_embedder_uses_ollama_when_no_openai_key():
    with patch.object(settings, "OPENAI_API_KEY", None):
        clear_ai_caches()
        embedder = get_embedder()
    assert isinstance(embedder, OllamaEmbedder)


def test_embedder_uses_openai_when_key_set():
    with patch.object(settings, "OPENAI_API_KEY", "sk-test"):
        clear_ai_caches()
        embedder = get_embedder()
    assert isinstance(embedder, OpenAIEmbedder)
