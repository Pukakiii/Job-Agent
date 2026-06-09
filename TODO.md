# Project TODO

First-wave tasks for MVP foundation. Pick work from your section; **Joint Tasks** are open to any contributor (including new joiners via PR).

See [contributing-rules.md](contributing-rules.md) for branch naming and PR conventions.

---

## Assigned to Pukakiii

*Frontend, UI/UX, infra, and data-layer setup.*

(docker-orchestration.md)

- [ ] **Initialize Next.js frontend** — Run `create-next-app` in `frontend/` with `--src-dir` (TypeScript, Tailwind, App Router); wire config into the existing folder scaffold per [code-architecture.md](code-architecture.md#frontend-folder-structure); add `src/lib/api/client.ts` typed against backend base URL
- [ ] **App shell UI** — Layout, navigation, design tokens, and pages under `src/app/(dashboard)/` (jobs, CVs, applications, documents, outreach, settings) matching [system-requirements.md](system-requirements.md) screen list

---

## Assigned to Kyryll

*Backend API, auth, and data-access layer.*

- [ ] **Docker local stack** — Add `infra/docker/docker-compose.yml` (postgres/pgvector, Redis, Ollama with model pull + healthcheck, `api`, `worker`) and a multi-stage Dockerfile shared by both entrypoints (`uvicorn` vs `arq`) per [docker-orchestration.md]
- [ ] **Data models + initial migration** — Add SQLAlchemy models (`User`, `CV`, `Job`, `Search`, `SearchResult`) with pgvector `Vector(768)`, repositories skeleton, and Alembic `init` migration (`CREATE EXTENSION vector`, HNSW index) per [data-layer.md](data-layer.md)
- [ ] **Backend core scaffolding** — Implement `core/config.py`, `core/db.py`, app factory with async lifespan (Redis pool, DB engine), versioned router at `/api/v1`, and domain error envelope per [code-architecture.md](code-architecture.md)
- [ ] **JWT authentication** — Integrate `fastapi-users` (register, login, JWT refresh), `api/deps.py` (`get_db`, `current_active_user`), and `api/v1/routes/auth.py` per [code-architecture.md](code-architecture.md)
- [ ] **API route scaffolding** — Add thin v1 routes and Pydantic schemas for CV upload, job read, and search trigger (`schemas/`, `api/v1/routes/`) delegating to placeholder services
- [ ] **Repository layer** — Implement `job_repo.py` (vector search, idempotent upsert) and `search_repo.py` (`save_search`, `get_with_results`) per [data-layer.md](data-layer.md)

---

## Joint Tasks

*Open to Pukakiii, Kyryll, or external contributors.*

- [ ] **ARQ worker skeleton** — Add `workers/settings.py` and `workers/tasks.py` with `scrape_board` and `embed_jobs` stubs wired to `IngestionService` placeholder ([ADR 001](adr/001-queue-tool.md))
- [ ] **Test harness** — `tests/conftest.py` with `httpx.AsyncClient`, dependency overrides, and a passing health-check test per [code-architecture.md](code-architecture.md)
- [ ] **First job source adapter** — Implement pluggable `JobSource` protocol and one official API source (e.g. Adzuna) in `integrations/sources/` per [ADR 004](adr/004-jobs-scraping.md)