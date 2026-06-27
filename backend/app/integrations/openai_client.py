"""
AI client — chat completions and embeddings over the OpenAI-compatible API.

A single class talks to any OpenAI-compatible endpoint: OpenAI itself, a local
Ollama (``http://localhost:11434/v1``), or Ollama Cloud (``https://ollama.com/v1``).
Each instance is configured for one role — chat or embeddings — with its own
``base_url``, ``api_key`` and default model, so the two roles can target different
providers. Build instances via :mod:`app.integrations.ai_factory`, not directly.
"""

import logging
from typing import AsyncGenerator

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class OpenAIClient:
    """Async wrapper around one OpenAI-compatible endpoint.

    Args:
        base_url:        ``None`` targets api.openai.com; pass ``".../v1"`` for Ollama.
        api_key:         API key (use ``"ollama"`` for a local Ollama, which ignores it).
        model:           Default model for this client's role (chat *or* embeddings).
        send_dimensions: Whether to forward the Matryoshka ``dimensions`` param — only
                         OpenAI's text-embedding-3-* support it; Ollama rejects it.
    """

    def __init__(
        self,
        *,
        base_url: str | None,
        api_key: str,
        model: str,
        send_dimensions: bool = False,
    ) -> None:
        self._client = AsyncOpenAI(base_url=base_url, api_key=api_key)
        self._model = model
        self._send_dimensions = send_dimensions

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

        Returns the model's reply as a plain string, or None on failure.
        When ``json_mode`` is True the prompt must explicitly ask for JSON.
        """
        kwargs: dict = {
            "model": model or self._model,
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
            logger.exception("[AI] chat() failed")
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
        """Streaming chat completion. Yields incremental text chunks."""
        stream = await self._client.chat.completions.create(
            model=model or self._model,
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
        """Embed a single string and return its vector, or None on failure."""
        try:
            kwargs: dict = {
                "model": model or self._model,
                "input": text,
                "encoding_format": "float",
            }
            if dimensions is not None and self._send_dimensions:
                kwargs["dimensions"] = dimensions
            response = await self._client.embeddings.create(**kwargs)
            return response.data[0].embedding
        except Exception:
            logger.exception("[AI] embed() failed — input: %.80r", text)
            return None

    async def embed_batch(
        self,
        texts: list[str],
        *,
        model: str | None = None,
        dimensions: int | None = None,
    ) -> list[list[float]] | None:
        """Embed a list of strings in a single API call.

        The API preserves input ordering via the ``index`` field, so the returned
        list always matches the order of ``texts``. Returns None on failure.
        """
        if not texts:
            return []
        try:
            kwargs: dict = {
                "model": model or self._model,
                "input": texts,
                "encoding_format": "float",
            }
            if dimensions is not None and self._send_dimensions:
                kwargs["dimensions"] = dimensions
            response = await self._client.embeddings.create(**kwargs)
            # Sort by index to guarantee order matches the input list
            return [d.embedding for d in sorted(response.data, key=lambda d: d.index)]
        except Exception:
            logger.exception("[AI] embed_batch() failed (%d texts)", len(texts))
            return None
