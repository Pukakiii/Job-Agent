from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from app.integrations.openai_client import OpenAIClient


class Embedder(Protocol):
    """Turns text into vectors. `embed_batch` embeds documents (job text on ingest);
    `embed_query` embeds a single search query. They are separate methods because some
    models (e.g. nomic-embed-text) need different task-instruction prefixes for the two
    sides — see the Local Ollama plan. OpenAI ignores the distinction."""

    async def embed_batch(self, texts: list[str]) -> list[list[float]]: ...
    async def embed_query(self, text: str) -> list[float]: ...


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

    async def embed_query(self, text: str) -> list[float]:
        vectors = await self._client.embed_batch([text], dimensions=self._dimensions)
        if not vectors:
            raise RuntimeError("Embedding failed (OpenAI returned no vectors)")
        return vectors[0]


class OllamaEmbedder:
    """nomic-embed-text via Ollama — uses task prefixes for document vs query."""

    DOCUMENT_PREFIX = "search_document: "
    QUERY_PREFIX = "search_query: "

    def __init__(self, client: "OpenAIClient") -> None:
        self._client = client

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        prefixed = [f"{self.DOCUMENT_PREFIX}{t}" for t in texts]
        vectors = await self._client.embed_batch(prefixed)
        if vectors is None:
            raise RuntimeError("Embedding failed (Ollama returned no vectors)")
        return vectors

    async def embed_query(self, text: str) -> list[float]:
        prefixed = f"{self.QUERY_PREFIX}{text}"
        vector = await self._client.embed(prefixed)
        if vector is None:
            raise RuntimeError("Embedding failed (Ollama returned no vector)")
        return vector
