"""Factory helpers for the AI chat client and embedder.

Chat and embeddings are resolved independently from settings (see
``Settings.chat_endpoint`` / ``embed_endpoint``), so they can target different
providers — e.g. Ollama Cloud chat + local-Ollama or OpenAI embeddings.
"""

from __future__ import annotations

from functools import lru_cache

from app.core.config import settings
from app.integrations.embeddings import Embedder, OllamaEmbedder, OpenAIEmbedder
from app.integrations.openai_client import OpenAIClient


@lru_cache
def get_chat_client() -> OpenAIClient:
    ep = settings.chat_endpoint()
    return OpenAIClient(base_url=ep.base_url, api_key=ep.api_key, model=ep.model)


@lru_cache
def get_embed_client() -> OpenAIClient:
    ep = settings.embed_endpoint()
    return OpenAIClient(
        base_url=ep.base_url,
        api_key=ep.api_key,
        model=ep.model,
        send_dimensions=ep.send_dimensions,
    )


@lru_cache
def get_embedder() -> Embedder:
    client = get_embed_client()
    if settings.EMBED_PROVIDER == "openai":
        return OpenAIEmbedder(client, dimensions=settings.EMBED_DIM)
    return OllamaEmbedder(client)


def clear_ai_caches() -> None:
    """Reset cached clients (for tests)."""
    get_chat_client.cache_clear()
    get_embed_client.cache_clear()
    get_embedder.cache_clear()
