# Project TODO

Second-wave tasks for MVP foundation. Pick work from your assignee section.

Each item is scoped to **one commit** — small, reviewable, and modular. See [contributing-rules.md](docs/contributing-rules.md) for branch naming and PR conventions. Assignees are grouped by [team roles](ai-agents/roles.md) — check that file when picking or adding tasks.

---

## Current stage

**Done (backend foundation):** Core (`config`, `db`, app factory, CORS), SQLAlchemy models + Alembic initial migration (pgvector HNSW), JWT auth (`fastapi-users`), repositories (`job_repo`, `search_repo`, `cv_repo`), S3 integration, repository-layer tests (Testcontainers + moto), Docker Compose stack, CV API routes + `cv_service`.

**Done (frontend foundation):** Next.js 16 (App Router, TypeScript, Tailwind v4), design tokens, API client, auth API module, shared UI primitives + `FormField`, login/register pages, `AuthProvider` + `useAuth`, route-protection middleware, dashboard shell + all scaffold pages, typed API modules (`jobs`, `cvs`, `searches`, `applications`), Safari compatibility fixes.

**Not started / in progress:** Applications backend (model + repo + service + routes), AI analysis + document generation APIs, Postmark integration, loading/error UI, wiring dashboard pages to live API data, E2E auth integration, frontend CI workflow.

**Recently completed (backend):** Jobs, searches, and CV API routes; CV service + CV parsing/normalization; functional matching (location filtering) and ingestion (dedupe, country-aware location); ARQ worker settings + task stubs; Adzuna, Jooble, and Apify/Indeed source adapters (+ Apify client); OpenAI client integration; backend CI (pytest matrix) and verify-ai-rules CI workflows.

**Recently completed (frontend):** Dashboard shell now uses extracted `SidebarNav`, `SidebarFooter`, `DashboardHeader`, and brand components; all dashboard page scaffolds in place; dark theme toggle. Frontend remains at scaffold stage — live API wiring and polish are now owned by Abdul 'Aziz.

---

## Assigned to Pukakiii

_Per [team roles](ai-agents/roles.md): **Frontend Developer**, **UI/UX Designer** — UI, design system, React components, and client-side API modules._

_Order follows app flow: foundation → auth → API client modules → route protection → dashboard shell → page scaffolds → polish & wiring._

### Foundation

- [x] **Initialize Next.js app** — Add `next`, `react`, `tailwindcss`, and App Router config to `frontend/`; create `layout.tsx`, `page.tsx`, `globals.css`, and `next.config.ts` per [code-architecture.md](docs/code-architecture.md#frontend-folder-structure)
- [x] **Design tokens and Tailwind theme** — Define color palette, typography scale, spacing, and radius in `tailwind.config.ts` + CSS variables in `globals.css`
- [x] **Root layout** — Add `src/app/layout.tsx` with html/body shell, Geist font setup, dark color-scheme, and metadata for "Job Agent"
- [x] **Homepage** — Add `src/app/page.tsx` landing page with hero section, headline, subheadline, and CTA button linking to /login
- [x] **Safari compatibility** — Hex-first CSS tokens, `100dvh` fallbacks, Particles/BlurFade fixes, `-webkit-backdrop-filter` on glass surfaces
- [x] **Shared UI primitives** — Add `Button`, `Input`, `Label`, and `Card` under `src/components/ui/`
- [x] **FormField composition** — Add `components/forms/form-field.tsx` for label + input + error message in auth forms

### API client (before pages that import types)

- [x] **API client base** — Add `src/lib/api/client.ts` with base URL, credentials, JSON parsing, and domain error envelope handling
- [x] **Auth API module** — Add `src/lib/api/auth.ts` with typed `login`, `register`, `logout`, and `getMe` calls
- [x] **Jobs API module** — Add `src/lib/api/jobs.ts` with `listJobs`, `getJob`, and `getJobScore` helpers mirroring backend schemas
- [x] **CVs API module** — Add `src/lib/api/cvs.ts` with upload, list, set-active, and delete helpers
- [x] **Searches API module** — Add `src/lib/api/searches.ts` with `triggerSearch`, `getSearch`, `listSearches`, and `getSearchResults` helpers
- [x] **Applications API module** — Add `src/lib/api/applications.ts` mirroring backend application endpoints

### Auth flow

- [x] **Login page** — Build `(auth)/login/page.tsx` with email/password form, validation, error display, and `?registered=true` success banner
- [x] **Fix login page layout and styling** — Fix card centering, remove premature validation errors, fix input default border color, tighten border radius, fix title position outside card, and align spacing to DESIGN_REFERENCES.md
- [x] **Register page** — Build `(auth)/register/page.tsx` with sign-up form and post-register redirect to `/login?registered=true`
- [x] **Auth session hook** — Add `src/features/auth/AuthProvider.tsx` + `useAuth.ts` for current user state, loading, and cookie-backed session persistence
- [x] **Route protection middleware** — Add `src/middleware.ts` to redirect unauthenticated users away from `/dashboard` routes (cookie presence check)

### Dashboard shell & pages

- [x] **Dashboard shell layout** — Add `(dashboard)/layout.tsx` with sidebar nav linking overview, jobs, CVs, applications, documents, outreach, and settings
- [x] **Dashboard overview page** — Add `(dashboard)/dashboard/page.tsx` as the `/dashboard` landing view
- [x] **Jobs page scaffold** — Add `(dashboard)/dashboard/jobs/page.tsx` with empty state, stat cards, and list container ready for API data
- [x] **CVs page scaffold** — Add `(dashboard)/dashboard/cvs/page.tsx` with upload dropzone placeholder and active-CV selector UI
- [x] **Applications page scaffold** — Add `(dashboard)/dashboard/applications/page.tsx` with Kanban column layout (saved / applied / interview / offer / rejected)
- [x] **Documents page scaffold** — Add `(dashboard)/dashboard/documents/page.tsx` for resume and cover-letter generation placeholders
- [x] **Outreach page scaffold** — Add `(dashboard)/dashboard/outreach/page.tsx` with email list and compose panel placeholders
- [x] **Settings page scaffold** — Add `(dashboard)/dashboard/settings/page.tsx` with account info and AI-instruction fields

### UI polish & shell

- [x] **Dark theme** — Add theme provider + toggle (header or settings); persist user preference; audit pages and shared components under `.dark` tokens in `globals.css`
- [x] **Wire dashboard shell components** — Use `sidebar-footer` (logout), `sidebar-nav`, and `dashboard-header` in layout instead of inline nav; ensure logout calls `AuthProvider`

_Remaining frontend wiring, polish, and content-feature work has been handed off to Abdul 'Aziz — see that section below._

---

## Assigned to Kyryll

_Per [team roles](ai-agents/roles.md): **Backend Developer** — API routes, service layer, workers, and local infra._

- [x] **Docker Compose stack** — Add `infra/docker/docker-compose.yml` with postgres/pgvector, Redis, Ollama (model pull + healthcheck), `api`, and `worker` per [docker-orchestration.md](docs/docker-orchestration.md)
- [x] **Multi-stage Dockerfile** — Add shared backend image with `uvicorn` (api) and `arq` (worker) entrypoints
- [x] **CV API routes** — Add `api/v1/routes/cv.py` (upload, list, set active) wired to `cv_repo` and S3; register in `router.py`
- [x] **Jobs API routes** — Add `api/v1/routes/jobs.py` (get by id, list with pagination) delegating to `job_repo`
- [x] **Searches API routes** — Add `api/v1/routes/searches.py` (trigger match, retrieve history) delegating to `search_repo`
- [x] **CV service** — Add `services/cv_service.py` orchestrating S3 upload, text extraction, and `cv_repo` persistence
- [x] **CV parsing service** — Add `services/cv_parsing_service.py` + `services/normalization.py` for text extraction and field normalisation
- [x] **Matching service** — `services/matching_service.py` with embed → vector search → re-rank, including tolerant location filtering (city OR country, remote opt-in)
- [x] **Ingestion service** — `services/ingestion_service.py` normalise → dedupe → embed → store pipeline with country-aware location and empty-record skipping
- [x] **ARQ worker settings** — Implement `workers/settings.py` with Redis URL, task registry, and cron hooks per [ADR 001](docs/adr/001-queue-tool.md)
- [x] **ARQ task stubs** — Add `workers/tasks.py` with `scrape_board` and `embed_jobs` delegating to `IngestionService`
- [x] **Jooble source adapter** — Implement `integrations/sources/jooble.py` against the `JobSource` protocol
- [x] **Apify/Indeed source adapter** — Implement `integrations/sources/apify_indeed.py` + `integrations/apify_client.py` (token kept server-side)
- [x] **CI workflow (backend)** — `.github/workflows/backend-tests.yml` running `pytest` matrix (py3.11/3.13) on push/PR with Testcontainers + moto
- [x] **verify-ai-rules CI workflow** — `.github/workflows/verify-ai-rules.yml` keeping `.github/instructions/*` in sync with `ai-agents/*`

---

## Assigned to Thịnh Phương

_Per [team roles](ai-agents/roles.md): **Backend Developer**, **QA & Documentation** — API routes, service layer, workers, local infra, and AI pipeline research._

### Research & proposals

_Pre-implementation work only — no pipeline or matching code changes. For each task: (1) open a GitHub issue, (2) fill in the linked doc using the required format below. Doc and issue should cover the same content; the doc is the durable project record._

- [ ] **Job embedding & retrieval** — Research how jobs should be embedded at ingest and retrieved at query time in our pgvector matching pipeline. Review `IngestionService`, `MatchingService`, `JobRepository.search_by_vector`, and `Embedder` against [ADR 002](docs/adr/002-ai-layer-stack.md) and [ai-layer.md](ai-agents/ai-layer.md).

  **Deliverables:**
  1. **GitHub issue** — Open an issue on the repo. Labels: `enhancement`, `research`, `ai-layer`. Link [ADR 002](docs/adr/002-ai-layer-stack.md).
  2. **Documentation** — Write [docs/research/job-embedding-retrieval.md](docs/research/job-embedding-retrieval.md) (currently empty — you create the full doc). Include the GitHub issue URL at the top.

  **Required format (issue + doc):**
  - Header — owner, status, GitHub issue URL, related links
  - **Current pipeline** — summary of how ingest and query work today (reference key files)
  - **Problem statement** — what is unclear, suboptimal, or missing
  - **Research questions** — embed input format, query vector construction (CV + prompt), retrieval params (candidate limit, filters, HNSW), doc-vs-code gaps (e.g. nomic task prefixes), re-embed strategy
  - **Why the recommended approach is better** — comparison table: current vs recommended
  - **Recommendations & phased plan** — embed strategy, retrieval strategy, phased implementation table, MVP non-goals
  - **Risks & open questions**
  - **Evaluation approach** — how to measure retrieval quality before/after changes
  - **References**

- [ ] **Knowledge-graph job recommendation** — Research whether a knowledge-graph–hybrid approach could improve job recommendation (speed, relevance, explainability) compared to the current vector-only pipeline (embed → pgvector cosine search → LLM rerank).

  **Deliverables:**
  1. **GitHub issue** — Open an issue on the repo. Labels: `enhancement`, `research`, `ai-layer`. Link [ADR 002](docs/adr/002-ai-layer-stack.md) and [job-embedding-retrieval.md](docs/research/job-embedding-retrieval.md).
  2. **Documentation** — Write [docs/research/kg-recommendation-proposal.md](docs/research/kg-recommendation-proposal.md) (currently empty — you create the full doc). Include the GitHub issue URL at the top.

  **Required format (issue + doc):**
  - Header — owner, status, GitHub issue URL, related links
  - **Current baseline** — summary of the vector-only pipeline and its limitations
  - **Problem statement** — gaps that vector search alone does not address
  - **Why KG-hybrid could be better** — comparison table: vector-only vs KG-hybrid (speed, relevance, explainability, structured relations)
  - **Proposed approach** — entity types, relationship types, hybrid retrieval flow
  - **Phased implementation plan** — Phase 0 / 1 / 2 table with explicit MVP non-goals
  - **Risks & open questions** — maintenance, extraction accuracy, overlap with pgvector
  - **Recommended next steps** — prioritised actions after team review
  - **References**

### Backend & QA

_Fresh set scoped to current `main`. The Applications domain does not exist yet — no model, repo, service, routes, or migration. Order follows dependencies: model → repo → service → routes → tests._

- [ ] **Application model + migration** — Add `Application` ORM model (user, job, status, notes, timestamps) and Alembic revision; mirror existing `models/cv.py` and `models/search_result.py`
- [ ] **Application repository** — Add `repositories/application_repo.py` with CRUD and status-transition queries; mirror `repositories/cv_repo.py`
- [ ] **Application service** — Add `services/application_service.py` orchestrating repo persistence and status transitions; mirror `services/cv_service.py`
- [ ] **Applications API routes + schemas** — Add `api/v1/routes/applications.py` and Pydantic schemas; register in `api/v1/router.py` alongside auth/cv/jobs/searches
- [ ] **Postmark client** — Implement send-email interface in the existing empty `integrations/postmark.py` (no live calls required)
- [ ] **Tests: job source adapters** — Add adapter tests covering `integrations/sources/jooble.py` and `integrations/sources/apify_indeed.py`
- [ ] **Tests: ingestion + normalization** — Cover `services/normalization.py` and ingestion dedupe / country-aware location logic
- [ ] **Tests: applications endpoints** — Add API tests for the applications routes (Testcontainers DB) once routes land
- [ ] **Document non-Adzuna job sources** — Update [ADR 004](docs/adr/004-jobs-scraping.md) / [data-layer.md](docs/data-layer.md) to cover the Jooble and Apify/Indeed sources

---

## Assigned to Abdul 'Aziz

_Per [team roles](ai-agents/roles.md): **Frontend Developer**, **QA & Documentation** — UI, design system, React components, client-side API modules, and testing._

_Fresh set. The dashboard pages are scaffold-only on `main` (hardcoded empty arrays); the typed API modules under `src/lib/api/` already exist and just need wiring. Backend jobs/searches/CV routes are live; applications routes depend on Thịnh Phương._

### Wire pages to live data

- [ ] **Wire jobs page to API** — Connect the jobs scaffold to `listJobs`; render job cards with title, company, location, and match score
- [ ] **Wire CVs page** — Connect upload control to `POST /api/v1/cvs`, load CVs via `listCVs`, and wire set-active/delete actions
- [ ] **Wire overview dashboard stats** — Replace hardcoded `0` stat cards with live counts (jobs, applications, CVs) or skeletons while loading
- [ ] **Wire settings account section** — Populate email/name from `getMe`; enable save when a profile-update endpoint exists
- [ ] **Wire applications Kanban** — Connect the Kanban to `listApplications` and status updates _(blocked on Thịnh Phương — Applications API)_

### Shared UI & polish

- [ ] **Loading and error UI** — Add shared `LoadingSkeleton` and `ErrorBanner` components for consistent async states
- [ ] **Reusable empty state** — Extract a shared `EmptyState` component (icon, title, description, CTA) used across jobs, CVs, applications, documents, and outreach
- [ ] **Toast notifications** — Add success/error toasts for upload, search, save, and logout actions
- [ ] **Fixed sidebar navigation & footer** — Pin the brand header, nav links, and Settings/Logout so they stay visible while content scrolls
- [ ] **Responsive sidebar** — Collapsible sidebar or mobile drawer so dashboard nav works on small screens
- [ ] **Outreach + documents API modules** — Fill the empty `src/lib/api/outreach.ts` and `src/lib/api/documents.ts` modules mirroring backend endpoints

### Content features (scaffold → functional UI)

- [ ] **Job detail view** — Add a job detail page or drawer showing full description, AI relevance score/explanation, risk flags, and external apply URL
- [ ] **Wire search trigger** — Connect "Run new search" on the jobs page to `triggerSearch` and poll `getSearchResults`; refresh the job list on completion
- [ ] **Jobs list filtering** — Wire the jobs page search input to a client-side filter (title, company) over fetched results
- [ ] **Applications Kanban interactions** — Add drag-and-drop or status-change controls on Kanban cards once the API supports transitions
- [ ] **Documents job picker** — Add a job-selection step before "Generate resume" / "Generate cover letter" on the documents page
- [ ] **Outreach compose panel** — Build a compose form (recipient, subject, body) in the outreach preview pane; stub send until Postmark lands

### QA

- [ ] **Wire login flow E2E** — Connect frontend login/register pages to live auth API and verify session cookie round-trip
- [ ] **CI workflow (frontend)** — Add GitHub Actions job running frontend `lint` on pull requests

---

## Completed — earlier foundation (Pukakiii & Kyryll)

_Historical items delivered by Pukakiii and Kyryll — kept for reference only._

- [x] **`.env.example` files** — Document required backend and frontend env vars (DB, Redis, S3, JWT secret, API URL) without secrets
- [x] **API health-check test** — Extend `tests/` with `httpx.AsyncClient` hitting `GET /health` through the app factory per [code-architecture.md](docs/code-architecture.md)
- [x] **Auth route integration tests** — Add register → login → protected-endpoint flow test using dependency overrides
- [x] **CV upload route tests** — Add API tests for upload and list endpoints (moto S3 + Testcontainers DB)
- [x] **JobSource protocol** — Add pluggable `JobSource` ABC in `integrations/sources/base.py` per [ADR 004](docs/adr/004-jobs-scraping.md)
- [x] **Adzuna source adapter** — Implement first official API source in `integrations/sources/adzuna.py`
- [x] **OpenAI client integration** — Add `integrations/openai_client.py` for embeddings and chat completions (env-gated)
