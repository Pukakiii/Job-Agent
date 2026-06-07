# AI Job Agent Platform

An AI-first job search platform that collects jobs from multiple sources, deduplicates and caches postings, performs semantic matching with embeddings, scores opportunities with AI, generates tailored resumes and cover letters, sends outreach emails, and tracks applications end-to-end.

---

## Table of Contents

* [Overview](#overview)
* [Documentation](#documentation)
* [Core Capabilities](#core-capabilities)
* [System Architecture](#system-architecture)
* [Technology Stack](#technology-stack)
* [Project Structure](#project-structure)
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
* [Contributing](#contributing)
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

The architecture is intentionally simple enough for an MVP, but structured enough to grow into a production-grade system. Detailed requirements and architectural decisions live in [docs/](docs/).

---

## Documentation

| Document | Description |
|----------|-------------|
| [System Requirements](docs/system-requirements.md) | MVP feature checklist and business logic |
| [Tech Stack](docs/tech-stack.md) | Approved technologies |
| [ADR 001: Queue Tool](docs/adr/001-queue-tool.md) | ARQ + Redis for async workers |
| [ADR 002: AI Layer](docs/adr/002-ai-layer-stack.md) | Embeddings, pgvector, local/API models |
| [ADR 003: Apply Automation](docs/adr/003-apply-automation.md) | Direct-apply links instead of browser automation |
| [ADR 004: Jobs Scraping](docs/adr/004-jobs-scraping.md) | Apify + official APIs, pluggable sources |

---

## Core Capabilities

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

Jobs are ingested asynchronously by ARQ workers, normalized, embedded, and stored in PostgreSQL with pgvector. When a user uploads a CV, the system performs semantic similarity search, re-ranks results with a language model, and surfaces the best matches with explanations. Resume, cover letter, and email generation run through the same AI layer. Users complete the final apply step in their own browser via direct links to original postings — see [ADR 003](docs/adr/003-apply-automation.md).

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

Monorepo layout. Scaffold directories exist; application code is still early-stage.

```text
job-agent/
├── backend/
│   ├── alembic/                 # migrations (scaffold)
│   ├── app/
│   │   ├── api/                 # route handlers
│   │   ├── core/                # config, security, dependencies
│   │   ├── db/                  # session, base models
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # business logic, AI, ingestion
│   │   └── main.py              # FastAPI entry (health check)
│   ├── tests/
│   └── pyproject.toml
├── docs/
│   ├── adr/
│   │   ├── 001-queue-tool.md
│   │   ├── 002-ai-layer-stack.md
│   │   ├── 003-apply-automation.md
│   │   └── 004-jobs-scraping.md
│   ├── system-requirements.md
│   └── tech-stack.md
├── frontend/                    # scaffold — Next.js not yet initialized
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── styles/
│   └── package.json
├── infra/
│   ├── docker/
│   └── deployment/
├── .cursor/rules/               # agent rules for collaborators
├── .env.example
├── README.md
└── .gitignore
```

---

## Data Model

Entity relationships and persistence rules are defined in [System Requirements](docs/system-requirements.md). Core domains include jobs, CVs, embeddings, AI analysis outputs, applications, and emails.

---

## Main Workflows

### 1. Job ingestion

```text
Official APIs / Apify → ARQ workers → normalize → deduplicate → jobs
```

* Workers collect jobs from pluggable sources (see [ADR 004](docs/adr/004-jobs-scraping.md)).
* Each source normalizes into a unified internal format.
* The system checks whether the job URL already exists.
* New postings are inserted; repeated postings update `last_seen_at`.
* Missing postings can later be marked inactive.

### 2. Embedding and indexing

```text
New job → embed → pgvector → AI analysis → persisted results
```

* Only new or modified jobs are embedded.
* Embeddings are stored in pgvector for semantic search.
* AI analysis (scoring, categorization, scam check) runs asynchronously via workers.

### 3. Semantic matching

```text
CV upload → parse profile → embed → similarity search → LLM re-rank → ranked jobs
```

* User uploads a CV stored in S3.
* CV is parsed into a structured profile and embedded.
* Similarity search retrieves top matches from pgvector.
* A language model re-ranks results and generates fit explanations.

### 4. Resume, cover letter, and email generation

```text
Job + CV → AI generation → stored snapshot
```

* Tailored resume and cover letter snapshots are created for the target job.
* Outreach emails are drafted and sent via Postmark or Gmail API.
* All outputs are persisted for reuse and auditing.

### 5. Apply and track

```text
Top matches → direct apply links → user applies → application record → status pipeline
```

* The system surfaces up to 10 relevant jobs with links to original postings.
* The user completes the apply step in their own browser (see [ADR 003](docs/adr/003-apply-automation.md)).
* Application records track status: `saved`, `applied`, `interview`, `offer`, `rejected`.
* Statistics are computed from the existing tables.

---

## Local Development Setup

### Prerequisites

* Python 3.11+
* Node.js 18+
* PostgreSQL 15+ (with pgvector extension)
* Redis
* Docker (recommended)
* Git

### Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend setup

```bash
cd frontend
npm install
npm run dev
```

> The `frontend/` directory is scaffolded; run `npx create-next-app` or add Next.js dependencies before `npm run dev`.

### Database setup

1. Create a PostgreSQL database with the pgvector extension enabled.
2. Configure the backend connection string.
3. Run Alembic migrations.

---

## Environment Variables

Create a `.env` file in the backend directory. Some variables are planned for upcoming implementation.

```env
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/job_agent
SECRET_KEY=change-me
ENVIRONMENT=development

REDIS_URL=redis://localhost:6379

# AI — local
OLLAMA_BASE_URL=http://localhost:11434

# AI — API / BYOK (optional)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# Scraping
APIFY_API_TOKEN=

# CV storage (planned)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
S3_BUCKET_NAME=
S3_REGION=

# Email — choose Postmark or Gmail
POSTMARK_API_TOKEN=
POSTMARK_SENDER_EMAIL=

GMAIL_CLIENT_ID=
GMAIL_CLIENT_SECRET=
GMAIL_REFRESH_TOKEN=
GMAIL_SENDER_EMAIL=

FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
```

A committed `.env.example` is recommended once the backend configuration stabilizes.

---

## Database Migrations

Use Alembic for all schema changes.

```bash
alembic revision --autogenerate -m "init core tables"
alembic upgrade head
```

Rules:

* Never edit production schema directly.
* Always generate migrations for model changes.
* Keep migrations small and readable.
* Test migrations locally before deployment.

---

## API Overview

The backend exposes a REST API. Endpoints below are the target surface; only `GET /health` is implemented today.

### Health

* `GET /health`

### Jobs

* `GET /jobs`
* `GET /jobs/{id}`
* `POST /jobs`
* `PATCH /jobs/{id}`

### Applications

* `GET /applications`
* `POST /applications`
* `PATCH /applications/{id}`

### AI

* `POST /ai/score-job`
* `POST /ai/generate-resume`
* `POST /ai/generate-cover-letter`
* `POST /ai/scam-check`
* `POST /ai/match-jobs`

### Email

* `POST /emails/send`
* `GET /emails`

### Ingestion

* `POST /ingest/jobs`
* `POST /ingest/run`

These endpoints can evolve, but the separation should stay clear.

---

## AI Layer

The AI layer handles two distinct phases: ingestion and query. See [ADR 002](docs/adr/002-ai-layer-stack.md) for full detail.

### Ingestion phase

* Normalize scraped jobs
* Generate embeddings (`nomic-embed-text` locally or `text-embedding-3-small` via API)
* Store vectors in pgvector
* Run AI analysis (scoring, categorization, scam check)

### Query phase

* Parse uploaded CV into a structured profile
* Embed CV and perform similarity search against job embeddings
* Re-rank top results with a language model
* Generate fit explanations, strengths, and weaknesses

### Generation tasks

* Resume generation
* Cover letter generation
* Outreach email generation

### Example AI outputs

* `score` — numeric fit score
* `summary` — short explanation of fit
* `strengths` — matching skills or reasons to apply
* `weaknesses` — missing requirements or risks
* `risk_score` — scam-risk measure
* `flags` — suspicious patterns or red flags

### Design rules

* Use structured outputs whenever possible.
* Store results in the database.
* Keep generation predictable and auditable.
* Long-running tasks run through ARQ workers.

---

## Scraping and Ingestion

Ingestion uses a pluggable source interface. Official APIs (Adzuna, Jooble, Careerjet, and regional sources) form the backbone; Apify actors supplement boards without sanctioned APIs (Indeed, optionally LinkedIn). See [ADR 004](docs/adr/004-jobs-scraping.md).

### Ingestion goals

* Normalize raw job data from heterogeneous sources
* Detect duplicates across sources (API source wins over scraped duplicate)
* Avoid repeated inserts
* Update `last_seen_at` for known jobs
* Mark old postings inactive when appropriate
* Run ingestion asynchronously via ARQ workers

### Important rule

Ingestion feeds the backend — it is not the core system. The backend owns business logic, persistence, and the semantic index.

---

## Email Automation

The platform supports AI-assisted email drafting and sending through Postmark or Gmail API.

### Email behavior

* Generate subject and body automatically
* Send through the configured provider
* Save each message in `emails`
* Track status such as `draft`, `sent`, or `failed`

### Why email is separate from application tracking

A job can have:

* no email yet
* one outreach email
* multiple follow-up emails
* one tracked application record

These are related but not identical objects.

---

## Frontend Overview

The frontend is built with Next.js and focuses on visibility, control, and workflow management.

### Suggested screens

* Jobs dashboard with semantic match rankings
* Job detail page with AI analysis and scam flags
* CV management and upload
* Resume and cover letter generation views
* Email generation view
* Applications Kanban board
* Statistics overview
* Settings (AI provider, email, account)

### Frontend responsibilities

* Display backend data
* Trigger actions (match, generate, send)
* Show job scores, explanations, and scam flags
* Present direct apply links for top matches
* Show application pipeline
* Support fast browsing and filtering

---

## Deployment

A production deployment uses:

* Docker containers
* Managed PostgreSQL with pgvector
* Redis for ARQ queue and caching
* FastAPI API server + ARQ worker processes
* Next.js frontend host
* S3-compatible object storage for CVs
* Secure secret management
* Apify credentials for scraped sources
* Postmark or Gmail OAuth credentials
* Scheduled ingestion jobs via ARQ cron

### Recommended deployment order

1. Database (PostgreSQL + pgvector) and Redis
2. Backend API
3. ARQ workers
4. Frontend
5. S3 bucket for CV storage
6. AI service configuration (local Ollama or API keys)
7. Email and scraping service configuration

---

## Roadmap

### Phase 1: Foundation

* Backend skeleton with FastAPI and PostgreSQL
* User authentication (JWT via fastapi-users)
* Core tables and Alembic migrations
* Basic CRUD endpoints

### Phase 2: Ingestion and embeddings

* Pluggable job sources (official APIs + Apify)
* ARQ workers for async ingestion
* Job normalization, caching, and deduplication
* pgvector embeddings and semantic index

### Phase 3: AI matching and analysis

* CV upload and S3 storage
* Semantic similarity search and LLM re-ranking
* AI scoring, explanations, and scam checks

### Phase 4: Generation and outreach

* Resume and cover letter generation
* Email generation and sending
* Direct apply link surfacing

### Phase 5: UI and tracking

* Next.js dashboard
* Job detail views and Kanban board
* Application status tracking and statistics

### Phase 6: Hardening

* Validation and error handling
* Logging and monitoring
* Rate limiting
* Test coverage
* Deployment polishing

---

## Contributing

This project should stay readable and modular.

### Contribution guidelines

* Keep services focused and small.
* Prefer explicit schemas and typed responses.
* Do not introduce unnecessary abstractions.
* Add migrations for schema changes.
* Document new endpoints and workflows in `docs/`.
* Record significant architectural decisions as ADRs in `docs/adr/`.
* Keep automation safe, traceable, and debuggable.

---

## License

TBD
