# Project TODO

Second-wave tasks for MVP foundation. Pick work from your section; **Joint Tasks** are open to any contributor (including new joiners via PR).

Each item is scoped to **one commit** — small, reviewable, and modular. See [contributing-rules.md](docs/contributing-rules.md) for branch naming and PR conventions. Assignees are grouped by [team roles](.cursor/rules/roles.mdc) — check that file when picking or adding tasks.

---

## Current stage

**Done (foundation):** Backend core (`config`, `db`, app factory, CORS), SQLAlchemy models + Alembic initial migration (pgvector HNSW), JWT auth (`fastapi-users`), repositories (`job_repo`, `search_repo`, `cv_repo`), S3 integration, and repository-layer tests (Testcontainers + moto).

**Not started / in progress:** API routes beyond auth, service layer, ARQ workers, Docker Compose, job-source adapters, AI integrations, and frontend feature pages (route groups, layouts, dashboard shell).

**Done (frontend foundation):** Next.js 16 initialized via `create-next-app` (App Router, TypeScript, Tailwind CSS v4, ESLint) with default `layout.tsx`, `page.tsx`, and `globals.css`.

---

## Assigned to Pukakiii

*Per [team roles](.cursor/rules/roles.mdc): **Frontend Developer**, **UI/UX Designer** — UI, design system, React components, and client-side API modules.*

- [x] **Initialize Next.js app** — Add `next`, `react`, `tailwindcss`, and App Router config to `frontend/`; create `layout.tsx`, `page.tsx`, `globals.css`, and `next.config.ts` per [code-architecture.md](docs/code-architecture.md#frontend-folder-structure)
- [ ] **Design tokens and Tailwind theme** — Define color palette, typography scale, spacing, and radius in `tailwind.config.ts` + CSS variables in `globals.css`
- [ ] **API client base** — Add `src/lib/api/client.ts` with base URL, credentials, JSON parsing, and domain error envelope handling
- [ ] **Auth API module** — Add `src/lib/api/auth.ts` with typed `login`, `register`, and `logout` calls against `/api/v1/auth`
- [ ] **Login page** — Build `(auth)/login/page.tsx` with email/password form, validation, and error display
- [ ] **Register page** — Build `(auth)/register/page.tsx` with sign-up form and post-register redirect
- [ ] **Auth session hook** — Add `src/features/auth/useAuth.ts` for current user state, loading, and cookie-backed session persistence
- [ ] **Route protection middleware** — Add `src/middleware.ts` to redirect unauthenticated users away from `(dashboard)` routes
- [ ] **Shared UI primitives** — Add `Button`, `Input`, `Label`, and `Card` under `src/components/ui/`
- [ ] **Dashboard shell layout** — Add `(dashboard)/layout.tsx` with sidebar nav linking jobs, CVs, applications, documents, outreach, and settings
- [ ] **Jobs page scaffold** — Add `(dashboard)/jobs/page.tsx` with empty state and list container ready for API data
- [ ] **CVs page scaffold** — Add `(dashboard)/cvs/page.tsx` with upload dropzone placeholder and active-CV selector UI
- [ ] **Applications page scaffold** — Add `(dashboard)/applications/page.tsx` with Kanban column layout (saved / applied / interview / offer / rejected)
- [ ] **Documents page scaffold** — Add `(dashboard)/documents/page.tsx` for resume and cover-letter generation placeholders
- [ ] **Outreach page scaffold** — Add `(dashboard)/outreach/page.tsx` with email list and compose panel placeholders
- [ ] **Settings page scaffold** — Add `(dashboard)/settings/page.tsx` with account info and AI-instruction fields
- [ ] **Jobs API module** — Add `src/lib/api/jobs.ts` with `getJob` and list helpers mirroring backend schemas
- [ ] **CVs API module** — Add `src/lib/api/cvs.ts` with upload, list, and set-active helpers
- [ ] **Searches API module** — Add `src/lib/api/searches.ts` with `triggerSearch` and `getSearchHistory` helpers
- [ ] **Loading and error UI** — Add shared `LoadingSkeleton` and `ErrorBanner` components for consistent async states

---

## Assigned to Kyryll

*Per [team roles](.cursor/rules/roles.mdc): **Backend Developer** — API routes, service layer, workers, and local infra.*

- [X] **Docker Compose stack** — Add `infra/docker/docker-compose.yml` with postgres/pgvector, Redis, Ollama (model pull + healthcheck), `api`, and `worker` per [docker-orchestration.md](docs/docker-orchestration.md)
- [X] **Multi-stage Dockerfile** — Add shared backend image with `uvicorn` (api) and `arq` (worker) entrypoints
- [X] **CV API routes** — Add `api/v1/routes/cv.py` (upload, list, set active) wired to `cv_repo` and S3; register in `router.py`
- [X] **Jobs API routes** — Add `api/v1/routes/jobs.py` (get by id, list with pagination) delegating to `job_repo`
- [X] **Searches API routes** — Add `api/v1/routes/searches.py` (trigger match, retrieve history) delegating to `search_repo`
- [X] **CV service** — Add `services/cv_service.py` orchestrating S3 upload, text extraction stub, and `cv_repo` persistence
- [X] **Matching service stub** — Add `services/matching_service.py` with embed → vector search → re-rank placeholder interface
- [X] **Ingestion service stub** — Add `services/ingestion_service.py` with normalise → dedupe → embed → store pipeline skeleton
- [X] **ARQ worker settings** — Implement `workers/settings.py` with Redis URL, task registry, and cron hooks per [ADR 001](docs/adr/001-queue-tool.md)
- [X] **ARQ task stubs** — Add `workers/tasks.py` with `scrape_board` and `embed_jobs` delegating to `IngestionService`

---

## Joint Tasks

*Per [team roles](.cursor/rules/roles.mdc): **QA & Documentation** (Pukakiii, Kyryll), plus cross-cutting work any assignee or external contributor can pick up. Each item should still land as a single commit.*

- [X] **`.env.example` files** — Document required backend and frontend env vars (DB, Redis, S3, JWT secret, API URL) without secrets
- [X] **API health-check test** — Extend `tests/` with `httpx.AsyncClient` hitting `GET /health` through the app factory per [code-architecture.md](docs/code-architecture.md)
- [X] **Auth route integration tests** — Add register → login → protected-endpoint flow test using dependency overrides
- [X] **CV upload route tests** — Add API tests for upload and list endpoints (moto S3 + Testcontainers DB)
- [X] **JobSource protocol** — Add pluggable `JobSource` ABC in `integrations/sources/base.py` per [ADR 004](docs/adr/004-jobs-scraping.md)
- [X] **Adzuna source adapter** — Implement first official API source in `integrations/sources/adzuna.py`
- [X] **OpenAI client integration** — Add `integrations/openai_client.py` for embeddings and chat completions (env-gated)
- [ ] **Postmark client stub** — Add `integrations/postmark.py` with send-email interface (no live calls required)
- [X] **Application model + migration** — Add `Application` ORM model (user, job, status, notes) and Alembic revision
- [ ] **Application repository** — Add `repositories/application_repo.py` with CRUD and status-transition queries
- [ ] **Applications API routes** — Add `api/v1/routes/applications.py` and Pydantic schemas; register in `router.py`
- [ ] **Applications API module (frontend)** — Add `src/lib/api/applications.ts` mirroring backend application endpoints
- [ ] **Wire login flow E2E** — Connect frontend login/register pages to live auth API and verify session cookie round-trip
- [ ] **Wire CV upload UI** — Connect CVs page upload control to `POST /api/v1/cvs` once backend route exists
- [ ] **CI workflow** — Add GitHub Actions job running backend `pytest` and frontend `lint` on pull requests
