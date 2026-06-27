# Tech Stack 

- Frontend: Next.js (App Router, `src/` directory), TypeScript, Tailwind CSS — feature-based layout under `frontend/src/` (see [code-architecture.md](code-architecture.md#frontend-folder-structure))
- Backend: FastAPI
- Scraping: Apify for Indeed/LinkedIn + Official API if exist / other scrapping tools
- AI layer (chat and embeddings chosen independently — `CHAT_PROVIDER` / `EMBED_PROVIDER`):
    - Embeddings: local Ollama (`nomic-embed-text`) or OpenAI (`text-embedding-3-small`), 768-dim
    - Chat/LLM: local Ollama (`gemma3:4b`), Ollama Cloud, or OpenAI (`gpt-4o-mini`)
- Database: PostgreSQL + pgvector
- API: REST
- Validation: Pydantic
- Migrations: Alembic + SQLAlchemy
- Email: Postmark / gmail API
- Auth: JWT + fastapi-users
- Queue: ARQ
- Cache: Redis
- CV storage: S3
- Containerization: Docker