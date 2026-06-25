# Job Agent — Frontend

Next.js 16 app for the Job Agent dashboard. Talks to the FastAPI backend at `/api/v1` (proxied in development).

## Prerequisites

- Node.js 20+
- Backend running at `http://localhost:8000` (see root [README](../README.md))

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
| `NEXT_PUBLIC_ENABLE_MSW` | `true` in `.env.example` | Default API mode when no browser override is set |

### MSW vs live backend

**Toggle at runtime (dev only):** open **Settings → Developer** and choose **Use mocks** or **Use live API**. The choice is stored in `localStorage` and the page reloads. **Reset to env default** clears the override.

| Mode | When to use | Requirements |
|------|-------------|--------------|
| **Mock API (MSW)** | No backend running; quick UI dev | `NEXT_PUBLIC_ENABLE_MSW=true` or Settings toggle |
| **Live backend** | Real auth, CV upload, search | Docker Compose up; toggle off or `NEXT_PUBLIC_ENABLE_MSW=false` |

In development, API calls always use same-origin `/api/v1/*` so auth cookies work with middleware. MSW intercepts in the browser when enabled; otherwise Next.js rewrites proxy to the backend.

**Offline mocks:** set `NEXT_PUBLIC_ENABLE_MSW=true` in `.env.local`, or use Settings → Developer → **Use mocks**. MSW intercepts `/api/v1/*` and sets a dev cookie so middleware allows dashboard access.

**Live backend:** set `NEXT_PUBLIC_ENABLE_MSW=false` or use **Use live API** in Settings. Auth uses the `jobagent_auth` HttpOnly cookie set by the backend on login.

## Scripts

```bash
npm run dev      # Start dev server (http://localhost:3000)
npm test         # Vitest unit tests
npm run lint     # ESLint
npm run build    # Production build
```

## Manual live E2E checklist

Run with backend + Postgres + Redis up and `NEXT_PUBLIC_ENABLE_MSW=false`:

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
- `src/mocks/` — MSW handlers (enabled via `NEXT_PUBLIC_ENABLE_MSW`)
- `src/features/auth/` — Auth context and hooks
