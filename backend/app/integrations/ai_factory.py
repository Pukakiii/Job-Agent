"""Factory helpers for the AI chat client and embedder."""

from __future__ import annotations

from functools import lru_cache

from app.core.config import settings
from app.integrations.embeddings import Embedder, OllamaEmbedder, OpenAIEmbedder
from app.integrations.openai_client import OpenAIClient


@lru_cache
def get_chat_client() -> OpenAIClient:
    return OpenAIClient()


@lru_cache
def get_embedder() -> Embedder:
    client = get_chat_client()
    if settings.ai_provider == "openai":
        return OpenAIEmbedder(client, dimensions=settings.EMBED_DIM)
    return OllamaEmbedder(client)


def clear_ai_caches() -> None:
    """Reset cached clients (for tests)."""
    get_chat_client.cache_clear()
    get_embedder.cache_clear()
