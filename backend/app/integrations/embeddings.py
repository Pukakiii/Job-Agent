from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from app.integrations.openai_client import OpenAIClient


class Embedder(Protocol):
    async def embed_batch(self, texts: list[str]) -> list[list[float]]: ...


class OpenAIEmbedder:
    """Wraps OpenAIClient to satisfy the Embedder Protocol at 768 dims.

    Pass an OpenAIClient as `client` — do not pass it directly as an Embedder.
    """

    def __init__(self, client: "OpenAIClient", dimensions: int) -> None:
        self._client = client
        self._dimensions = dimensions

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        vectors = await self._client.embed_batch(texts, dimensions=self._dimensions)
        if vectors is None:
            raise RuntimeError("Embedding failed (OpenAI returned no vectors)")
        return vectors
