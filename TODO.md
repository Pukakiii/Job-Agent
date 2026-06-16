# Project TODO

Second-wave tasks for MVP foundation. Pick work from your assignee section.

Each item is scoped to **one commit** — small, reviewable, and modular. See [contributing-rules.md](docs/contributing-rules.md) for branch naming and PR conventions. Assignees are grouped by [team roles](ai-agents/roles.md) — check that file when picking or adding tasks.

---

## Current stage

**Done (backend foundation):** Core (`config`, `db`, app factory, CORS), SQLAlchemy models + Alembic initial migration (pgvector HNSW), JWT auth (`fastapi-users`), repositories (`job_repo`, `search_repo`, `cv_repo`), S3 integration, repository-layer tests (Testcontainers + moto), Docker Compose stack, CV API routes + `cv_service`.

**Done (frontend foundation):** Next.js 16 (App Router, TypeScript, Tailwind v4), design tokens, API client, auth API module, shared UI primitives + `FormField`, login/register pages, `AuthProvider` + `useAuth`, route-protection middleware, dashboard shell + all scaffold pages, typed API modules (`jobs`, `cvs`, `searches`, `applications`), Safari compatibility fixes.

**Not started / in progress:** Applications backend (repo + routes), live matching/ingestion pipelines, AI analysis + document generation APIs, Postmark integration, loading/error UI, wiring dashboard pages to live API data, E2E auth + CV upload integration, CI workflow.

**Recently completed (backend):** Jobs, searches, and CV API routes; service stubs (CV, matching, ingestion); ARQ worker settings + task stubs; Adzuna source adapter; OpenAI client integration.

**Recently completed (frontend):** Dashboard shell now uses extracted `SidebarNav`, `SidebarFooter`, `DashboardHeader`, and brand components; all dashboard page scaffolds in place.

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

### Next up — UI polish (sidebar & theme)

- [x] **Dark theme** — Add theme provider + toggle (header or settings); persist user preference; audit pages and shared components under `.dark` tokens in `globals.css`
- [ ] **Fixed sidebar navigation** — Pin brand header and main nav links so they stay visible while the nav list scrolls independently on long viewports
- [ ] **Fixed sidebar footer** — Pin Settings and Logout at the bottom of the sidebar so they remain visible while main content scrolls

### Next up — polish & wiring

- [x] **Wire dashboard shell components** — Use `sidebar-footer` (logout), `sidebar-nav`, and `dashboard-header` in layout instead of inline nav; ensure logout calls `AuthProvider`
- [ ] **Loading and error UI** — Add shared `LoadingSkeleton` and `ErrorBanner` components for consistent async states
- [ ] **Reusable empty state** — Extract a shared `EmptyState` component (icon, title, description, CTA) used across jobs, CVs, applications, documents, and outreach scaffolds
- [ ] **Toast notifications** — Add success/error toasts for upload, search, save, and logout actions

### Next up — wire pages to live data

_Backend jobs, searches, and CV routes are live; applications routes are still pending (see Thịnh Phương)._

- [ ] **Wire overview dashboard stats** — Replace hardcoded `0` stat cards with live counts (jobs, applications, CVs, outreach drafts) or skeleton placeholders while loading
- [ ] **Wire jobs page to API** — Connect jobs scaffold to `listJobs`; render job cards with title, company, location, and match score
- [ ] **Job detail view** — Add job detail page or drawer showing full description, AI relevance score/explanation, risk flags, and external apply URL
- [ ] **Wire search trigger** — Connect "Run new search" on jobs page to `triggerSearch` and poll `getSearchResults`; refresh job list on completion
- [ ] **Wire CV upload UI** — Connect CVs page upload control to `POST /api/v1/cvs`; show upload progress and validation errors
- [ ] **Wire CV list and active selector** — Load CVs via `listCvs`, display file metadata, and wire set-active/delete actions
- [ ] **Wire settings account section** — Populate email/name from `getMe`; enable save when backend profile update endpoint exists
- [ ] **Wire applications page to API** — Connect Kanban to `listApplications` and status updates once backend routes exist _(blocked on Thịnh Phương — Applications API)_

### Next up — content features (scaffold → functional UI)

_These pages have layout placeholders; they need interactive flows even before full AI backends land._

- [ ] **Jobs list filtering** — Wire the jobs page search input to client-side filter (title, company) over fetched results
- [ ] **Applications Kanban interactions** — Add drag-and-drop or status-change controls on Kanban cards once API supports transitions
- [ ] **Documents job picker** — Add job-selection step before "Generate resume" / "Generate cover letter" buttons on documents page
- [ ] **Outreach compose panel** — Build compose form (recipient, subject, body) in the outreach preview pane; stub send until Postmark lands
- [ ] **Responsive sidebar** — Collapsible sidebar or mobile drawer so dashboard nav works on small screens

---

## Assigned to Kyryll

_Per [team roles](ai-agents/roles.md): **Backend Developer** — API routes, service layer, workers, and local infra._

- [x] **Docker Compose stack** — Add `infra/docker/docker-compose.yml` with postgres/pgvector, Redis, Ollama (model pull + healthcheck), `api`, and `worker` per [docker-orchestration.md](docs/docker-orchestration.md)
- [x] **Multi-stage Dockerfile** — Add shared backend image with `uvicorn` (api) and `arq` (worker) entrypoints
- [x] **CV API routes** — Add `api/v1/routes/cv.py` (upload, list, set active) wired to `cv_repo` and S3; register in `router.py`
- [x] **Jobs API routes** — Add `api/v1/routes/jobs.py` (get by id, list with pagination) delegating to `job_repo`
- [x] **Searches API routes** — Add `api/v1/routes/searches.py` (trigger match, retrieve history) delegating to `search_repo`
- [x] **CV service** — Add `services/cv_service.py` orchestrating S3 upload, text extraction stub, and `cv_repo` persistence
- [x] **Matching service stub** — Add `services/matching_service.py` with embed → vector search → re-rank placeholder interface
- [x] **Ingestion service stub** — Add `services/ingestion_service.py` with normalise → dedupe → embed → store pipeline skeleton
- [x] **ARQ worker settings** — Implement `workers/settings.py` with Redis URL, task registry, and cron hooks per [ADR 001](docs/adr/001-queue-tool.md)
- [x] **ARQ task stubs** — Add `workers/tasks.py` with `scrape_board` and `embed_jobs` delegating to `IngestionService`

---

## Assigned to Thịnh Phương

_Per [team roles](ai-agents/roles.md): **Backend Developer**, **QA & Documentation** — API routes, service layer, workers, and local infra._

- [ ] **Postmark client stub** — Add `integrations/postmark.py` with send-email interface (no live calls required)
- [ ] **Application repository** — Add `repositories/application_repo.py` with CRUD and status-transition queries
- [ ] **Applications API routes** — Add `api/v1/routes/applications.py` and Pydantic schemas; register in `router.py`
- [ ] **CI workflow (backend)** — Add GitHub Actions job running backend `pytest` on pull requests

---

## Assigned to Abdul 'Aziz

_Per [team roles](ai-agents/roles.md): **Frontend Developer**, **QA & Documentation** — UI, design system, React components, client-side API modules, and testing._

- [ ] **Wire login flow E2E** — Connect frontend login/register pages to live auth API and verify session cookie round-trip
- [ ] **CI workflow (frontend)** — Add GitHub Actions job running frontend `lint` on pull requests

---

## Completed cross-team work

_Historical items that spanned multiple roles — kept for reference only._

- [x] **`.env.example` files** — Document required backend and frontend env vars (DB, Redis, S3, JWT secret, API URL) without secrets
- [x] **API health-check test** — Extend `tests/` with `httpx.AsyncClient` hitting `GET /health` through the app factory per [code-architecture.md](docs/code-architecture.md)
- [x] **Auth route integration tests** — Add register → login → protected-endpoint flow test using dependency overrides
- [x] **CV upload route tests** — Add API tests for upload and list endpoints (moto S3 + Testcontainers DB)
- [x] **JobSource protocol** — Add pluggable `JobSource` ABC in `integrations/sources/base.py` per [ADR 004](docs/adr/004-jobs-scraping.md)
- [x] **Adzuna source adapter** — Implement first official API source in `integrations/sources/adzuna.py`
- [x] **OpenAI client integration** — Add `integrations/openai_client.py` for embeddings and chat completions (env-gated)
- [x] **Application model + migration** — Add `Application` ORM model (user, job, status, notes) and Alembic revision
