# CLAUDE.md
 
Job automation backend that discovers relevant job listings, ranks them by CV fit, and surfaces the top matches as direct links. The user completes the apply step themselves — no browser automation.
 
## Stack
 
FastAPI · ARQ + Redis · PostgreSQL + pgvector · SQLAlchemy + Alembic · Pydantic · JWT + fastapi-users · S3 · Postmark · Docker Compose. AI: `text-embedding-3-small` for embeddings, `GPT-4o-mini` for LLM tasks (local Ollama path also supported). Job sources: Adzuna, Jooble, Careerjet (official APIs) + Apify actors for Indeed/LinkedIn (best-effort, switch-off-able).
 
## Architecture
 
Strict layer separation — routers are thin, business logic lives in `services/`, all SQL stays in `repositories/`. `workers/tasks.py` is just an ARQ entry point delegating into `services/`. Two entry paths share one persistence layer: HTTP request path and ARQ background path (scraping, embedding, email).
 
## Key constraints
 
- No business logic in routers; no SQL outside repositories
- Schema models (`schemas/`) and ORM models (`models/`) are kept separate
- Scraped sources are individually switch-off-able; API sources take precedence on deduplication
- Hard cap of 10 job links returned per search
- Run migrations manually: `docker compose run --rm api alembic upgrade head`
 