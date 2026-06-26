# Project TODO

Second-wave tasks for MVP foundation. Pick work from your assignee section.

Each item is scoped to **one commit** — small, reviewable, and modular. See [contributing-rules.md](docs/contributing-rules.md) for branch naming and PR conventions. Assignees are grouped by [team roles](ai-agents/roles.md) — check that file when picking or adding tasks.

---

## Current stage

**Done (backend foundation):** Core (`config`, `db`, app factory, CORS), SQLAlchemy models + Alembic initial migration (pgvector HNSW), JWT auth (`fastapi-users`), repositories (`job_repo`, `search_repo`, `cv_repo`), S3 integration, repository-layer tests (Testcontainers + moto), Docker Compose stack, CV API routes + `cv_service`.

**Done (frontend foundation):** Next.js 16 (App Router, TypeScript, Tailwind v4), design tokens, API client, auth API module, shared UI primitives + `FormField`, login/register pages, `AuthProvider` + `useAuth`, route-protection middleware, dashboard shell + all scaffold pages, typed API modules (`jobs`, `cvs`, `searches`, `applications`), Safari compatibility fixes.

**Done (MVP v1 remediation — PR #36, CI green):** Live-backend-only frontend (MSW removed). Docker Compose stack + S3 bucket bootstrap. Ollama AI provider (OpenAI BYOK fallback). Active CV selection. Documents + outreach APIs and UI. Postmark stub. Auth rate limiting (production only).

**Not started / post-MVP:** Scam-risk UI, drag-and-drop Kanban, Playwright E2E, full account profile editing, ARQ `send_followup_email` task.

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
- [x] **Fixed sidebar navigation** — Pin brand header and main nav links so they stay visible while the nav list scrolls independently on long viewports
- [x] **Fixed sidebar footer** — Pin Settings and Logout at the bottom of the sidebar so they remain visible while main content scrolls

### Next up — polish & wiring

- [x] **Wire dashboard shell components** — Use `sidebar-footer` (logout), `sidebar-nav`, and `dashboard-header` in layout instead of inline nav; ensure logout calls `AuthProvider`
- [x] **Loading and error UI** — Add shared `LoadingSkeleton` and `ErrorBanner` components for consistent async states
- [x] **Reusable empty state** — Extract a shared `EmptyState` component (icon, title, description, CTA) used across jobs, CVs, applications, documents, and outreach scaffolds
- [x] **Toast notifications** — Add success/error toasts for upload, search, save, and logout actions

### Next up — wire pages to live data

_Backend jobs, searches, CV, and applications routes are live._

- [x] **Wire overview dashboard stats** — Replace hardcoded `0` stat cards with live counts (jobs, applications, CVs, searches)
- [x] **Wire jobs page to API** — Connect jobs scaffold to `listJobs`; render job cards with title, company, location, and match score
- [x] **Job detail view** — Add job detail drawer showing full description, AI relevance score/explanation, and external apply URL
- [x] **Wire search trigger** — Connect "Run new search" on jobs page to `triggerSearch` with 202 ingest polling; refresh on 201
- [x] **Wire CV upload UI** — Connect CVs page upload control to `POST /api/v1/cvs`; show upload progress and validation errors
- [x] **Wire CV list** — Load CVs via `listCVs`, display file metadata, and wire delete actions (latest CV used for search)
- [x] **Wire settings account section** — Populate email from `getMe`
- [x] **Wire applications page to API** — Connect Kanban to `listApplications` and status updates
- [x] **Jobs list filtering** — Wire the jobs page search input to client-side filter (title, company) over fetched results
- [x] **Responsive sidebar** — Collapsible sidebar or mobile drawer so dashboard nav works on small screens
- [x] **Wire login flow E2E (live backend)** — `jobagent_auth` cookie, live backend only (MSW removed from dev), manual E2E checklist in `frontend/README.md`
- [x] **Frontend CI polish** — `npm run lint` in `.github/workflows/frontend-tests.yml`
- [x] **Documents job picker** — Add job-selection step before "Generate resume" / "Generate cover letter" buttons on documents page
- [x] **Outreach compose panel** — Build compose form (recipient, subject, body) in the outreach preview pane; stub send until Postmark lands
- [x] **Applications Kanban interactions** — Status-change controls on Kanban cards

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
- [x] **CI workflow (backend)** — Add GitHub Actions job running backend `pytest` on pull requests
- [x] **ARQ worker settings** — Implement `workers/settings.py` with Redis URL, task registry, and cron hooks per [ADR 001](docs/adr/001-queue-tool.md)
- [x] **ARQ task stubs** — Add `workers/tasks.py` with `scrape_board` and `embed_jobs` delegating to `IngestionService`

---

## Assigned to Thịnh Phương

_Per [team roles](ai-agents/roles.md): **Backend Developer**, **QA & Documentation** — API routes, service layer, workers, local infra, and AI pipeline research._

### Research & proposals

_Post-MVP only — start these after the MVP release, not during MVP foundation work. Pre-implementation research only — no pipeline or matching code changes. For each task: (1) open a GitHub issue, (2) fill in the linked doc using the required format below. Doc and issue should cover the same content; the doc is the durable project record._

- [ ] **Job embedding & retrieval** _(post-MVP — do not start until after MVP release)_ — Research how jobs should be embedded at ingest and retrieved at query time in our pgvector matching pipeline. Review `IngestionService`, `MatchingService`, `JobRepository.search_by_vector`, and `Embedder` against [ADR 002](docs/adr/002-ai-layer-stack.md) and [ai-layer.md](ai-agents/ai-layer.md).

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

- [ ] **Knowledge-graph job recommendation** _(post-MVP — do not start until after MVP release)_ — Research whether a knowledge-graph–hybrid approach could improve job recommendation (speed, relevance, explainability) compared to the current vector-only pipeline (embed → pgvector cosine search → LLM rerank).

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

- [x] **Application model + migration** — Add `backend/app/models/application.py` with `user_id` (FK), `job_id` (FK), `status` (enum: `saved` | `applied` | `interview` | `offer` | `rejected`), `notes` (nullable text), `created_at` / `updated_at`. Unique constraint on `(user_id, job_id)`. Alembic revision creating `applications` table. Export from `models/__init__.py`. Align status values with [`frontend/src/lib/api/applications.ts`](frontend/src/lib/api/applications.ts).

- [x] **Postmark client stub** — Add `backend/app/integrations/postmark.py` with a `PostmarkClient` class exposing `send_email(to, subject, html_body, *, tag=None) -> str` (returns a stub message ID). Add `POSTMARK_API_TOKEN` and `POSTMARK_SENDER_EMAIL` to `Settings` in `backend/app/core/config.py` (vars already in `.env.example`). When token is unset, log and no-op instead of calling Postmark. Add `backend/tests/test_postmark_client.py` using `httpx.MockTransport` (pattern: `test_apify_client.py`). Do not wire `send_followup_email` in `workers/tasks.py` yet — that is a follow-up once outreach templates exist.

- [x] **Application repository** — Add `backend/app/repositories/application_repo.py` with `ApplicationRepository(db)` methods: `create(user_id, job_id, status, notes)`, `get_by_id`, `list_by_user(user_id, *, status=None, limit, offset)` ordered by `updated_at desc`, `update_status(application, status, notes)`, `delete(application)`. Flush without commit (pattern: `cv_repo.py`). Add `backend/tests/test_application_repo.py` with Testcontainers `db` fixture. _Depends on Application model + migration._

- [x] **Applications API routes** — Add `backend/app/schemas/application.py` (`ApplicationRead`, `ApplicationCreate`, `ApplicationUpdate`) and `backend/app/api/v1/routes/applications.py` with auth-guarded endpoints matching the frontend client:
  - `GET /api/v1/applications` — list (optional `status`, `limit`, `offset`)
  - `POST /api/v1/applications` — create (body: `job_id`, optional `status`, `notes`)
  - `PUT /api/v1/applications/{id}` — update status/notes (user must own row)
  - `DELETE /api/v1/applications/{id}` — delete (user must own row)
  Register in `backend/app/api/v1/router.py`. Add `ApplicationNotFound` to `exceptions.py`. Add `backend/tests/test_applications_api.py` (auth guards, 404 envelope, validation — pattern: `test_jobs_api.py`). Optionally embed `job` summary on read responses to match frontend `Application.job?`. _Depends on Application repository._

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
