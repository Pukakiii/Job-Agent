# Tech Stack 

- Frontend: Next.js (App Router, `src/` directory), TypeScript, Tailwind CSS — feature-based layout under `frontend/src/` (see [code-architecture.md](code-architecture.md#frontend-folder-structure))
- Backend: FastAPI
- Scraping: Apify for Indeed/LinkedIn + Official API if exist / other scrapping tools
- AI layer: 
    - Embedding model: text-embedding-3-small / local (nomic-embed-text)
    - LLM: API / local (gemma3 4B) 
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