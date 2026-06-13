import pytest

from app.integrations.embeddings import OpenAIEmbedder


class _FakeOpenAIClient:
    def __init__(self, vectors): self.vectors = vectors; self.calls = []
    async def embed_batch(self, texts, *, dimensions=None):
        self.calls.append((list(texts), dimensions))
        return self.vectors


async def test_openai_embedder_requests_configured_dim_and_returns_vectors():
    fake = _FakeOpenAIClient([[0.0] * 768, [1.0] * 768])
    emb = OpenAIEmbedder(client=fake, dimensions=768)
    out = await emb.embed_batch(["a", "b"])
    assert out == [[0.0] * 768, [1.0] * 768]
    assert fake.calls == [(["a", "b"], 768)]  # dimension forwarded


async def test_openai_embedder_raises_when_client_returns_none():
    fake = _FakeOpenAIClient(None)
    emb = OpenAIEmbedder(client=fake, dimensions=768)
    with pytest.raises(RuntimeError):
        await emb.embed_batch(["a"])
