---
Applies to: AI integration (embeddings, LLM, scoring, generation)
---

### Embeddings

- Default model: nomic-embed-text via Ollama (768-dim vectors)
- Optional: text-embedding-3-small via OpenAI (BYOK)
- Always prefix CV queries with search_query: when embedding for similarity search
- Store all vectors in pgvector — do not store embeddings in application memory

### LLM usage

- Default local model: gemma3:4b via Ollama
- Optional: BYOK providers (OpenAI, Anthropic, Google, OpenRouter)
- Never hardcode model names in business logic — read from config/environment
- All LLM calls go through the AI client in integrations/ — no direct SDK calls in services

### Scoring and analysis

- Scoring, fit explanation, and scam detection run as ARQ workers — not in request handlers
- Store all AI outputs (scores, flags, explanations) in the DB — never recompute on every request
- Scam flags must be stored on the job record and surfaced to the frontend

### Generation

- Resume snapshots and cover letters are stored as generated artifacts — never regenerate on read
- Generation tasks run via ARQ — enqueue and return 202, poll for completion
