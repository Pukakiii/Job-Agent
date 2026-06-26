"""
OpenAI client — chat completions and embeddings.

Uses the official `openai` Python SDK (AsyncOpenAI) directly against the OpenAI API.
No proxy or intermediary is involved.

Environment variables (set in .env.backend):
    OPENAI_API_KEY       — Required to use any OpenAI feature.
    OPENAI_CHAT_MODEL    — Chat model (default: gpt-4o-mini).
    OPENAI_EMBED_MODEL   — Embedding model (default: text-embedding-3-small).
"""

import logging
from typing import AsyncGenerator

from openai import AsyncOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


# ── Singleton client ──────────────────────────────────────────────────────────

_openai_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    """Return a cached AsyncOpenAI client (initialised once per process)."""
    global _openai_client
    if _openai_client is None:
        if settings.OPENAI_API_KEY:
            _openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            provider = "openai"
        else:
            base = settings.OLLAMA_BASE_URL.rstrip("/")
            _openai_client = AsyncOpenAI(
                base_url=f"{base}/v1",
                api_key="ollama",
            )
            provider = "ollama"
        logger.info(
            "[%s] Client initialised (chat=%s, embed=%s)",
            provider.upper(),
            settings.chat_model,
            settings.embed_model,
        )
    return _openai_client


# ── Public interface ──────────────────────────────────────────────────────────

class OpenAIClient:
    """Async wrapper around AsyncOpenAI for chat completions and embeddings.

    Usage::

        client = OpenAIClient()

        # Non-streaming chat
        reply = await client.chat(
            system_prompt="You are a helpful assistant.",
            user_prompt="Summarise this CV: ...",
        )

        # Streaming chat
        async for chunk in client.stream_chat(system_prompt=..., user_prompt=...):
            print(chunk, end="", flush=True)

        # Single embedding
        vector = await client.embed("Software engineer with 5 years experience")

        # Batch embeddings
        vectors = await client.embed_batch(["job A description", "job B description"])
    """

    def __init__(self) -> None:
        self._client = _get_client()

    # ── Chat completions ──────────────────────────────────────────────────────

    async def chat(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.2,
        json_mode: bool = False,
    ) -> str | None:
        """Non-streaming single-turn chat completion.

        Args:
            system_prompt: Instruction that sets the model's behaviour.
            user_prompt:   The user message / task.
            model:         Override the default chat model for this call.
            max_tokens:    Upper bound on the response length.
            temperature:   Sampling temperature — 0 is fully deterministic.
            json_mode:     When True, forces a valid JSON object response.
                           Your prompt must explicitly ask for JSON output.

        Returns:
            The model's reply as a plain string, or None on failure.
        """
        kwargs: dict = {
            "model": model or settings.chat_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        try:
            response = await self._client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        except Exception:
            logger.exception("[OPENAI] chat() failed")
            return None

    async def stream_chat(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.2,
    ) -> AsyncGenerator[str, None]:
        """Streaming chat completion.

        Yields incremental text chunks as they arrive from the API.
        Authentication or connection errors are raised before the first yield.

        Example::

            async for chunk in client.stream_chat(...):
                print(chunk, end="", flush=True)
        """
        stream = await self._client.chat.completions.create(
            model=model or settings.chat_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
        )
        async for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content

    # ── Embeddings ────────────────────────────────────────────────────────────

    async def embed(
        self,
        text: str,
        *,
        model: str | None = None,
        dimensions: int | None = None,
    ) -> list[float] | None:
        """Embed a single string and return its vector.

        Args:
            text:       The text to embed.
            model:      Override the default embedding model for this call.
            dimensions: Reduced output dimensions (Matryoshka — text-embedding-3-* only).

        Returns:
            A list of floats representing the embedding, or None on failure.
        """
        try:
            kwargs: dict = {
                "model": model or settings.embed_model,
                "input": text,
                "encoding_format": "float",
            }
            if dimensions is not None and settings.ai_provider == "openai":
                kwargs["dimensions"] = dimensions
            response = await self._client.embeddings.create(**kwargs)
            return response.data[0].embedding
        except Exception:
            logger.exception("[OPENAI] embed() failed — input: %.80r", text)
            return None

    async def embed_batch(
        self,
        texts: list[str],
        *,
        model: str | None = None,
        dimensions: int | None = None,
    ) -> list[list[float]] | None:
        """Embed a list of strings in a single API call.

        The OpenAI API preserves input ordering via the `index` field,
        so the returned list always matches the order of `texts`.

        Args:
            texts:      Strings to embed. Empty list returns [] without an API call.
            model:      Override the default embedding model for this call.
            dimensions: Reduced output dimensions (Matryoshka — text-embedding-3-* only).

        Returns:
            An ordered list of embedding vectors, or None on failure.
        """
        if not texts:
            return []
        try:
            kwargs: dict = {
                "model": model or settings.embed_model,
                "input": texts,
                "encoding_format": "float",
            }
            if dimensions is not None and settings.ai_provider == "openai":
                kwargs["dimensions"] = dimensions  # Matryoshka: text-embedding-3-* only
            response = await self._client.embeddings.create(**kwargs)
            # Sort by index to guarantee order matches the input list
            return [d.embedding for d in sorted(response.data, key=lambda d: d.index)]
        except Exception:
            logger.exception("[OPENAI] embed_batch() failed (%d texts)", len(texts))
            return None
