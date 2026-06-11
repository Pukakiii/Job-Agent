from typing import Protocol


class Embedder(Protocol):
    async def embed_batch(self, texts: list[str]) -> list[list[float]]: ...


class OpenAIEmbedder:
    def __init__(self, client, dimensions: int) -> None:
        self._client = client
        self._dimensions = dimensions

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        vectors = await self._client.embed_batch(texts, dimensions=self._dimensions)
        if vectors is None:
            raise RuntimeError("Embedding failed (OpenAI returned no vectors)")
        return vectors
