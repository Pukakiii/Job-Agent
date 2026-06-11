# OpenAI Integration

Documents the async OpenAI client used for chat completions and embeddings.

- **Source:** [`backend/app/integrations/openai_client.py`](../backend/app/integrations/openai_client.py)
- **Config:** [`backend/app/core/config.py`](../backend/app/core/config.py)
- **SDK:** [`openai`](https://github.com/openai/openai-python) (official Python SDK, `AsyncOpenAI`)

---

## Table of Contents

- [Configuration](#configuration)
- [Usage](#usage)
  - [Instantiation](#instantiation)
  - [Chat — non-streaming](#chat--non-streaming)
  - [Chat — streaming](#chat--streaming)
  - [Chat — JSON mode](#chat--json-mode)
  - [Embeddings — single text](#embeddings--single-text)
  - [Embeddings — batch](#embeddings--batch)
- [Default models](#default-models)
- [Error handling](#error-handling)
- [Adding the client as a FastAPI dependency](#adding-the-client-as-a-fastapi-dependency)

---

## Configuration

Set the following variables in `infra/secret/.env.backend`:

```env
# Required — leave unset to disable OpenAI features entirely
OPENAI_API_KEY=sk-...

# Optional — override the defaults
OPENAI_CHAT_MODEL=gpt-4o-mini          # default
OPENAI_EMBED_MODEL=text-embedding-3-small  # default
```

> **Note:** `OPENAI_API_KEY` is `None` by default. The client will raise a `ValueError` at first use if the key is not set. Features that call OpenAI should be guarded or only called when the key is present.

---

## Usage

### Instantiation

```python
from app.integrations.openai_client import OpenAIClient

client = OpenAIClient()
```

The underlying `AsyncOpenAI` instance is a **module-level singleton** — it is created once per process and reused across all `OpenAIClient` instances. There is no per-request connection overhead.

---

### Chat — non-streaming

Returns the complete response as a `str`, or `None` if the call fails.

```python
reply = await client.chat(
    system_prompt="You are a professional CV reviewer.",
    user_prompt="Summarise the key skills from this CV: ...",
)

if reply:
    print(reply)
```

**Optional parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `model` | `str \| None` | `settings.OPENAI_CHAT_MODEL` | Override the model for this call |
| `max_tokens` | `int` | `4096` | Maximum tokens in the response |
| `temperature` | `float` | `0.2` | Sampling temperature (0 = deterministic) |
| `json_mode` | `bool` | `False` | Force a valid JSON object response |

---

### Chat — streaming

Yields text chunks incrementally as they arrive. Errors before the first chunk are raised directly.

```python
async for chunk in client.stream_chat(
    system_prompt="You are a job-matching assistant.",
    user_prompt="Explain why this candidate matches the role.",
):
    print(chunk, end="", flush=True)
```

Useful for streaming responses to the frontend via a [Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events) endpoint.

---

### Chat — JSON mode

When `json_mode=True`, the API guarantees a valid JSON object response. Your prompt **must** explicitly ask for JSON output.

```python
import json

raw = await client.chat(
    system_prompt="Extract structured data and return valid JSON.",
    user_prompt=f"Extract skills and experience from: {cv_text}",
    json_mode=True,
)

data = json.loads(raw) if raw else {}
```

---

### Embeddings — single text

Returns a `list[float]` vector, or `None` on failure.

```python
vector = await client.embed("Software engineer with 5 years Python experience")
# vector → [0.012, -0.034, ..., 0.091]  (1536 floats for text-embedding-3-small)
```

---

### Embeddings — batch

Embeds multiple texts in a **single API call**. Returns an ordered `list[list[float]]` matching the input order, or `None` on failure. Pass an empty list to get `[]` without making an API call.

```python
job_descriptions = [
    "Backend engineer — Python, FastAPI, PostgreSQL",
    "Data scientist — ML, PyTorch, Python",
    "DevOps engineer — Kubernetes, Terraform, CI/CD",
]

vectors = await client.embed_batch(job_descriptions)
# vectors[0] → embedding for "Backend engineer..."
# vectors[1] → embedding for "Data scientist..."
```

---

## Default models

| Setting | Default | Notes |
|---|---|---|
| `OPENAI_CHAT_MODEL` | `gpt-4o-mini` | Fast and cost-effective for most tasks |
| `OPENAI_EMBED_MODEL` | `text-embedding-3-small` | 1536 dimensions; good trade-off of quality vs cost |

To use a more capable model for a specific call without changing the global default, pass the `model` parameter:

```python
reply = await client.chat(
    system_prompt="...",
    user_prompt="...",
    model="gpt-4o",  # override for this call only
)
```

---

## Error handling

| Method | On failure |
|---|---|
| `chat()` | Logs the exception and returns `None` |
| `stream_chat()` | Raises the exception before the first chunk |
| `embed()` | Logs the exception and returns `None` |
| `embed_batch()` | Logs the exception and returns `None` |

Always guard `None`-returning methods before use:

```python
vector = await client.embed(text)
if vector is None:
    # handle failure — skip, retry, or raise
    raise RuntimeError("Embedding failed")
```

---

## Adding the client as a FastAPI dependency

Wire `OpenAIClient` through FastAPI's dependency injection so it is reused per-request without repeated instantiation cost:

```python
# app/api/deps.py
from functools import lru_cache
from app.integrations.openai_client import OpenAIClient

@lru_cache
def get_openai() -> OpenAIClient:
    return OpenAIClient()
```

```python
# In a route
from fastapi import Depends
from app.api.deps import get_openai
from app.integrations.openai_client import OpenAIClient

@router.post("/analyse")
async def analyse_cv(
    cv_text: str,
    openai: OpenAIClient = Depends(get_openai),
):
    result = await openai.chat(
        system_prompt="You are a CV analysis assistant.",
        user_prompt=f"Analyse this CV:\n\n{cv_text}",
        json_mode=True,
    )
    return {"analysis": result}
```
