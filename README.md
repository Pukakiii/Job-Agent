# AI Job Agent Platform

An AI-first job search platform that collects jobs from multiple sources, deduplicates and caches postings, performs semantic matching with embeddings, scores opportunities with AI, generates tailored resumes and cover letters, sends outreach emails, and tracks applications end-to-end.

**Current status:** Early scaffold. Documentation and architectural decisions are in place; application code is minimal (backend health check only, frontend not yet initialized). Active work is tracked in [docs/TODO.md](docs/TODO.md).

---

## Table of Contents

* [Overview](#overview)
* [Documentation](#documentation)
* [Current State](#current-state)
* [Core Capabilities](#core-capabilities)
* [System Architecture](#system-architecture)
* [Technology Stack](#technology-stack)
* [Project Structure](#project-structure)
* [Team & Contributing](#team--contributing)
* [Data Model](#data-model)
* [Main Workflows](#main-workflows)
* [Local Development Setup](#local-development-setup)
* [Environment Variables](#environment-variables)
* [Database Migrations](#database-migrations)
* [API Overview](#api-overview)
* [AI Layer](#ai-layer)
* [Scraping and Ingestion](#scraping-and-ingestion)
* [Email Automation](#email-automation)
* [Frontend Overview](#frontend-overview)
* [Deployment](#deployment)
* [Roadmap](#roadmap)
* [License](#license)

---

## Overview

The platform helps users manage the full job-seeking workflow:

1. Discover jobs from official APIs and supplementary scraping sources
2. Normalize, deduplicate, and cache discovered postings in PostgreSQL
3. Generate embeddings and index jobs in pgvector for semantic search
4. Match uploaded CVs to relevant jobs using vector similarity and LLM re-ranking
5. Score jobs, explain fit, and detect possible scams or low-quality postings
6. Generate tailored resume snapshots and cover letters
7. Compose and send outreach emails
8. Surface direct apply links for the most relevant matches (user applies in their own browser)
9. Track application status and outcomes
10. Compute job-search statistics from stored records

The architecture is intentionally simple enough for an MVP, but structured enough to grow into a production-grade system.

---

## Documentation

| Document | Description |
|----------|-------------|
| [System Requirements](docs/system-requirements.md) | MVP feature checklist and business logic |
| [Tech Stack](docs/tech-stack.md) | Approved technologies |
| [Code Architecture](docs/code-architecture.md) | Layered backend design, AI layer, testing strategy |
| [Data Layer](docs/data-layer.md) | ORM models, pgvector, repositories, migrations |
| [Docker Orchestration](docs/docker-orchestration.md) | Compose topology, healthchecks, volumes |
| [Contributing Rules](docs/contributing-rules.md) | Branch naming, commits, PR workflow |
| [TODO](docs/TODO.md) | Active tasks by assignee |
| [ADR 001: Queue Tool](docs/adr/001-queue-tool.md) | ARQ + Redis for async workers |
| [ADR 002: AI Layer](docs/adr/002-ai-layer-stack.md) | Embeddings, pgvector, local/API models |
| [ADR 003: Apply Automation](docs/adr/003-apply-automation.md) | Direct-apply links instead of browser automation |
| [ADR 004: Jobs Scraping](docs/adr/004-jobs-scraping.md) | Apify + official APIs, pluggable sources |

---

## Current State

What exists today versus what the docs describe as the target:

| Area | Status |
|------|--------|
| Documentation | Complete — requirements, architecture, data layer, Docker plan, ADRs |
| Backend | `GET /health` only; `pyproject.toml` lists target dependencies |
| Database / models | Not implemented — schema defined in [data-layer.md](docs/data-layer.md) |
| Auth | Planned — `fastapi-users` + JWT |
| ARQ workers | Planned — ingestion, embedding, email tasks |
| Frontend | Scaffold `package.json` only — Next.js not initialized |
| Docker / infra | Documented — Compose files not yet added |
| Tests | Not started |

Next steps: see [docs/TODO.md](docs/TODO.md).

---

## Core Capabilities

Target MVP capabilities (from [system-requirements.md](docs/system-requirements.md)):

* User authentication and account management (JWT)
* CV upload, storage, and active-CV selection
* Job collection from official APIs and Apify-backed sources
* Normalization, deduplication, and caching of repeated postings
* Semantic matching via pgvector embeddings
* AI-based job scoring, explanations, and categorization
* Scam and risk detection with stored flags
* Tailored resume and cover letter generation
* Outreach email drafting and sending (Postmark or Gmail API)
* Application tracking with status pipeline
* Direct apply links for top matches (up to 10 relevant jobs)
* Background processing through ARQ workers
* Dashboard for jobs, applications, outreach, and statistics

---

## System Architecture

```mermaid
flowchart LR
  subgraph sources [JobSources]
    APIs[OfficialAPIs]
    Apify[ApifyActors]
  end
  subgraph backend [FastAPIBackend]
    API[RESTAPI]
    Workers[ARQWorkers]
  end
  subgraph storage [Storage]
    PG[(PostgreSQL_pgvector)]
    Redis[(Redis)]
    S3[(S3_CVStorage)]
  end
  subgraph ai [AILayer]
    Embed[Embeddings]
    LLM[LanguageModel]
  end
  APIs --> Workers
  Apify --> Workers
  Workers --> PG
  Workers --> Redis
  API --> PG
  Workers --> Embed
  Workers --> LLM
  API --> S3
```

Jobs are ingested asynchronously by ARQ workers, normalized, embedded, and stored in PostgreSQL with pgvector. When a user uploads a CV, the system performs semantic similarity search, re-ranks results with a language model, and surfaces the best matches with explanations. Users complete the final apply step in their own browser via direct links to original postings — see [ADR 003](docs/adr/003-apply-automation.md).

Backend layering (router → service → repository → ORM) is documented in [code-architecture.md](docs/code-architecture.md).

---

## Technology Stack

| Layer | Technologies |
|-------|-------------|
| Frontend | Next.js, TypeScript, Tailwind CSS |
| Backend | FastAPI, Python, Pydantic, SQLAlchemy, Alembic, fastapi-users (JWT) |
| Database | PostgreSQL + pgvector |
| Queue / cache | ARQ, Redis |
| Scraping | Apify (Indeed, LinkedIn) + official APIs (Adzuna, Jooble, Careerjet, regional) |
| AI (local) | Ollama — `nomic-embed-text`, `gemma3:4b` |
| AI (API / BYOK) | `text-embedding-3-small` + provider LLM (OpenAI, Anthropic, Google, OpenRouter) |
| Email | Postmark or Gmail API |
| CV storage | S3 |
| Infra | Docker |

Full details: [tech-stack.md](docs/tech-stack.md).

---

## Project Structure

Monorepo layout. Target structure from [code-architecture.md](docs/code-architecture.md); **bold** = not yet created.

```text
job-agent/
├── backend/
│   ├── alembic/                 # migrations (scaffold)
│   ├── app/
│   │   ├── api/                 # ** route handlers + v1 router **
│   │   ├── core/                # ** config, db, security **
│   │   ├── integrations/        # ** S3, Apify, AI clients, job sources **
│   │   ├── models/              # ** SQLAlchemy ORM **
│   │   ├── repositories/        # ** data access layer **
│   │   ├── schemas/             # ** Pydantic DTOs **
│   │   ├── services/            # ** business logic **
│   │   ├── workers/             # ** ARQ tasks **
│   │   └── main.py              # FastAPI entry (health check today)
│   ├── tests/                   # ** pytest **
│   └── pyproject.toml
├── docs/
│   ├── adr/                     # architectural decision records
│   ├── code-architecture.md
│   ├── contributing-rules.md
│   ├── data-layer.md
│   ├── docker-orchestration.md
│   ├── system-requirements.md
│   ├── tech-stack.md
│   └── TODO.md                  # active tasks
├── frontend/                    # scaffold — Next.js not yet initialized
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── styles/
│   └── package.json
├── infra/
│   └── docker/                  # ** Compose + Dockerfile (planned) **
├── .cursor/rules/               # agent rules for collaborators
├── .env.example
└── README.md
```

---

## Team & Contributing

**Core developers:** Pukakiii, Kyryll

Work is split in [docs/TODO.md](docs/TODO.md):

* **Assigned to Pukakiii** — data models, Docker infra, frontend init, UI/UX shell
* **Assigned to Kyryll** — backend scaffolding, auth, API routes, repositories
* **Joint Tasks** — workers, tests, ingestion adapters; open to any contributor

Before opening a PR, read [contributing-rules.md](docs/contributing-rules.md) (branch naming, commit prefixes, rebase with `main`).

Guidelines:

* Keep services focused; business logic lives in `services/`, not route handlers
* Long-running work goes through ARQ workers, not request handlers
* Add Alembic migrations for every schema change
* Record significant architecture changes as ADRs in `docs/adr/`
* Do not introduce technologies rejected in ADRs (e.g. Playwright for apply automation)

---

## Data Model

Five core tables: `users`, `cvs`, `jobs`, `searches`, `search_results`. Jobs are shared corpus entities; per-user relevance lives on the search-result join. Full ERD, indexes, and repository patterns: [data-layer.md](docs/data-layer.md).

---

## Main Workflows

### 1. Job ingestion

```text
Official APIs / Apify → ARQ workers → normalize → deduplicate → jobs
```

### 2. Embedding and indexing

```text
New job → embed → pgvector → AI analysis → persisted results
```

### 3. Semantic matching

```text
CV upload → parse profile → embed → similarity search → LLM re-rank → ranked jobs
```

### 4. Resume, cover letter, and email generation

```text
Job + CV → AI generation → stored snapshot
```

### 5. Apply and track

```text
Top matches → direct apply links → user applies → application record → status pipeline
```

Application statuses: `saved`, `applied`, `interview`, `offer`, `rejected`.

---

## Local Development Setup

### Prerequisites

* Python 3.11+
* Node.js 18+
* PostgreSQL 15+ with pgvector (or use Docker Compose once added)
* Redis
* Docker (recommended)
* Git

### Backend (today)

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

Health check: `GET http://localhost:8000/health`

### Frontend (after Next.js init)

```bash
cd frontend
npm install
npm run dev
```

### Docker (planned)

Once `infra/docker/` is in place:

```bash
docker compose -f infra/docker/docker-compose.yml up -d
docker compose -f infra/docker/docker-compose.yml run --rm api alembic upgrade head
```

See [docker-orchestration.md](docs/docker-orchestration.md).

---

## Environment Variables

Copy `.env.example` to `backend/.env` and adjust values.

```env
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/job_agent
SECRET_KEY=change-me
ENVIRONMENT=development
REDIS_URL=redis://localhost:6379
OLLAMA_BASE_URL=http://localhost:11434
# ... see .env.example for scraping, S3, email, and API keys
```

---

## Database Migrations

Use Alembic for all schema changes. Migrations run as a one-off command — not on app startup.

```bash
cd backend
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

Rules: never edit production schema directly; keep migrations small; test locally before deploy.

---

## API Overview

Target REST surface under `/api/v1`. **Implemented today:** `GET /health` only.

| Domain | Planned endpoints |
|--------|-------------------|
| Auth | register, login, JWT refresh (`fastapi-users`) |
| CVs | upload, list, presigned download |
| Searches | trigger match, list past searches |
| Jobs | list, detail (with direct apply URL) |
| Applications | CRUD + status transitions |
| AI | score, generate resume/cover letter, scam check |
| Email | send, list |
| Ingestion | trigger scrape (returns `202`, work via ARQ) |

Conventions: plural resource nouns, paginated lists, consistent error envelope — [code-architecture.md](docs/code-architecture.md).

---

## AI Layer

Two phases per [ADR 002](docs/adr/002-ai-layer-stack.md):

**Ingestion** — embed job corpus (`nomic-embed-text` / `text-embedding-3-small`), store in pgvector, run analysis workers.

**Query** — parse CV → embed with `search_query:` prefix → cosine similarity → LLM re-rank → fit explanations.

Local default: Ollama (`gemma3:4b` + `nomic-embed-text`, 768-dim vectors). BYOK API providers optional.

---

## Scraping and Ingestion

Pluggable `JobSource` interface. Official APIs are primary; Apify supplements boards without sanctioned APIs. API source wins on duplicate. All ingestion runs via ARQ — [ADR 004](docs/adr/004-jobs-scraping.md).

---

## Email Automation

AI-assisted drafting via Postmark or Gmail API. Emails are separate from application records (one job can have multiple outreach messages). Statuses: `draft`, `sent`, `failed`.

---

## Frontend Overview

Next.js App Router dashboard: job matches with scores and scam flags, CV management, document generation, applications Kanban, statistics, settings. Fetches from FastAPI only — no direct DB access. Surfaces direct apply links; no server-side browser automation — [ADR 003](docs/adr/003-apply-automation.md).

---

## Deployment

Target topology (Docker): API + worker containers, managed PostgreSQL/pgvector, Redis, Next.js frontend, S3 for CVs, Ollama or BYOK AI, external Apify/Postmark. Full plan: [docker-orchestration.md](docs/docker-orchestration.md).

Recommended order: database + Redis → migrations → API → workers → frontend → S3 → AI/email/scraping credentials.

---

## Roadmap

### Phase 1: Foundation *(in progress)*

* Backend skeleton, config, layered structure
* Core tables and Alembic migrations
* Docker Compose local stack
* User authentication (JWT)
* Next.js init + app shell

### Phase 2: Ingestion and embeddings

* Pluggable job sources
* ARQ workers for async ingestion
* pgvector index and embedding pipeline

### Phase 3: AI matching and analysis

* CV upload and S3 storage
* Semantic search and LLM re-ranking
* Scoring, explanations, scam checks

### Phase 4: Generation and outreach

* Resume and cover letter generation
* Email generation and sending

### Phase 5: UI and tracking

* Dashboard, job detail, Kanban board
* Application pipeline and statistics

### Phase 6: Hardening

* Validation, logging, rate limiting, test coverage, production deploy polish

---

## License

TBD
