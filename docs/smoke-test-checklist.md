# MVP v1 Smoke Test Checklist

Run with backend, Postgres, Redis, and MinIO up. Set `NEXT_PUBLIC_ENABLE_MSW=false` in `frontend/.env.local`.

## Infrastructure

- [ ] `docker compose -f infra/docker/docker-compose.yml up` starts postgres, redis, minio, api, worker
- [ ] `GET http://localhost:8000/health` returns 200
- [ ] `cd frontend && npm run dev` serves http://localhost:3000

## Auth

- [ ] Register at `/register` creates an account
- [ ] Login at `/login` sets `jobagent_auth` cookie and redirects to `/dashboard`
- [ ] `/dashboard` requires auth; logout clears session

## CVs

- [ ] Upload PDF on `/dashboard/cvs` — file appears in list
- [ ] Delete CV removes it from list

## Jobs & search

- [ ] `/dashboard/jobs` lists ingested jobs
- [ ] Run semantic search returns ranked results or 202 ingest polling
- [ ] Job detail drawer shows description, score, and explanation

## Applications

- [ ] `/dashboard/applications` Kanban loads applications
- [ ] Status advance (saved → applied → interview → offer) persists

## Dashboard & settings

- [ ] `/dashboard` overview shows live counts
- [ ] `/dashboard/settings` shows email from `GET /users/me`

## CI

- [ ] Backend `pytest` passes
- [ ] Frontend `npm test`, `npm run lint`, `npm run build` pass
