# Job Agent — Frontend

Next.js 16 app for the Job Agent dashboard. Talks to the live FastAPI backend at `/api/v1` (proxied in development via Next.js rewrites).

## Prerequisites

- Node.js 20+
- Backend stack running at `http://localhost:8000` (Postgres, Redis, MinIO, API, worker — see root [README](../README.md))

## Setup

```bash
cd frontend
cp .env.example .env.local
npm ci
```

### Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend origin used by Next.js `/api/v1` rewrites in dev |

In development, API calls use same-origin `/api/v1/*` so the `jobagent_auth` HttpOnly cookie set by the backend on login works with route middleware.

## Scripts

```bash
npm run dev      # Start dev server (http://localhost:3000)
npm test         # Vitest unit tests (uses MSW node server in test setup only)
npm run lint     # ESLint
npm run build    # Production build
```

## Manual live E2E checklist

Run with backend + Postgres + Redis + MinIO up:

- [ ] Register a new account at `/register`
- [ ] Sign in at `/login` — redirects to `/dashboard`; `jobagent_auth` cookie present
- [ ] `/dashboard` loads without redirect loop
- [ ] Upload a CV on `/dashboard/cvs` — file appears in list
- [ ] Run a semantic search from `/dashboard/jobs` — results or 202 ingest polling
- [ ] Open a job detail — title, company, match score/explanation visible
- [ ] Create/move/delete an application on `/dashboard/applications` Kanban
- [ ] Settings shows email from `GET /users/me`
- [ ] Sign out — cookie cleared, `/dashboard` redirects to `/login`

## Project structure

- `src/app/` — Next.js App Router pages
- `src/lib/api/` — Typed API client modules
- `src/mocks/handlers.ts` — MSW handlers for Vitest only (not used at runtime)
- `src/features/auth/` — Auth context and hooks
