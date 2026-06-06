# AI Job Agent Platform

An AI-first job search automation platform that collects jobs from multiple sources, deduplicates and caches postings, scores opportunities with AI, generates tailored resumes and cover letters, sends outreach emails automatically, and tracks applications end-to-end.
ation tracking.

---

## Table of Contents

* [Overview](#overview)
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

The platform helps users automate the full job-seeking workflow:

1. Discover jobs from career pages and job boards
2. Deduplicate and cache discovered postings
3. Store normalized jobs in PostgreSQL
4. Score jobs using AI
5. Detect possible scams or low-quality postings
6. Generate a tailored resume snapshot
7. Generate a cover letter
8. Compose and send outreach emails automatically
9. Track application status and outcomes
10. Compute job-search statistics from stored records

The architecture is intentionally simple enough for an MVP, but structured enough to grow into a production-grade system.

---

## Core Capabilities

* Job collection from external sources
* Deduplication and caching of repeated postings
* AI-based job scoring
* Lightweight scam and risk detection
* Tailored resume generation
* Cover letter generation
* Automatic email drafting and sending
* Application tracking with status pipeline
* Persistent storage of AI outputs and generated content
* Dashboard for jobs, applications, and outreach
* Statistics derived directly from the database

---

## System Architecture

![System Architecture](./docs/prototype_architecture.png)

---

## Technology Stack

### Frontend

* Next.js
* TypeScript
* Tailwind CSS

### Backend

* FastAPI
* Python
* SQLAlchemy
* Pydantic
* Alembic

### Database

* PostgreSQL

### Scraping / Automation

* Playwright

### AI

* Ollama for local models
* Optional GPT-4o for higher-accuracy generation or scoring tasks

### Email

* Gmail API

---

## Project Structure

A clean monorepo layout is recommended:

```text
job-autopilot/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── alembic/
│   ├── tests/
│   └── pyproject.toml
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── styles/
│   └── package.json
├── infra/
│   ├── docker/
│   └── deployment/
├── README.md
└── .env.example
```

---

## Data Model

![Data Model](./docs/prototype_database.png)

## Main Workflows

### 1. Job discovery

```text
Scraper → job_cache → jobs
```

* Playwright visits sources.
* The scraper normalizes the job data.
* The system checks whether the job URL already exists.
* New postings are inserted.
* Repeated postings update `last_seen_at`.
* Missing postings can later be marked inactive.

### 2. AI evaluation

```text
Job → scoring → scam check → saved AI output
```

* The backend sends structured data to the AI layer.
* AI returns a score, summary, strengths, weaknesses, and risk flags.
* Results are saved in the database.

### 3. Resume and cover letter generation

```text
Job + user profile → AI generation → stored snapshot
```

* A tailored resume snapshot is created for the target job.
* A cover letter is generated immediately.
* Content is persisted for reuse and auditing.

### 4. Email outreach

```text
AI draft → Gmail API → email status saved
```

* The system composes the email.
* Gmail API sends the email automatically.
* Delivery status is stored.

### 5. Application tracking

```text
Job → application record → status pipeline
```

* Each tracked job can have one or more application records.
* Status values may include: `saved`, `applied`, `interview`, `offer`, `rejected`.
* Statistics are computed from the existing tables.

---

## Local Development Setup

### Prerequisites

* Python 3.11+
* Node.js 18+
* PostgreSQL 15+
* Git
* Playwright browser dependencies

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

### Database setup

1. Create a PostgreSQL database.
2. Configure the backend connection string.
3. Run Alembic migrations.

---

## Environment Variables

Create a `.env` file in the backend directory.

```env
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/job_autopilot
SECRET_KEY=change-me
ENVIRONMENT=development

OLLAMA_BASE_URL=http://localhost:11434
OPENAI_API_KEY=

GMAIL_CLIENT_ID=
GMAIL_CLIENT_SECRET=
GMAIL_REFRESH_TOKEN=
GMAIL_SENDER_EMAIL=

FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
```

Recommended `.env.example` should be committed to the repository.

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

The backend should expose a clean REST API.

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

### Email

* `POST /emails/send`
* `GET /emails`

### Scraping / ingestion

* `POST /ingest/jobs`
* `POST /scrape/run`

These endpoints can evolve, but the separation should stay clear.

---

## AI Layer

AI is a core part of the product.

### AI tasks

* Job scoring
* Job categorization
* Resume generation
* Cover letter generation
* Scam and risk detection
* Outreach email generation

### Design rules

* Use structured outputs whenever possible.
* Store results in the database.
* Avoid a multi-agent setup for the MVP.
* Keep generation predictable and auditable.
* Prefer simple services over heavy orchestration frameworks.

### Example AI outputs

* `score`: numeric fit score
* `summary`: short explanation of fit
* `strengths`: matching skills or reasons to apply
* `weaknesses`: missing requirements or risks
* `risk_score`: simple scam-risk measure
* `flags`: suspicious patterns or red flags

---

## Scraping and Ingestion

Playwright is responsible for collecting jobs from sources such as company career pages and job boards.

### Ingestion goals

* Normalize raw job data
* Detect duplicates
* Avoid repeated inserts
* Update `last_seen_at` for known jobs
* Mark old postings inactive when appropriate

### Important rule

The scraper should not become the core system. It should feed the backend, which manages the real business logic and persistence.

---

## Email Automation

The platform supports automatic email sending.

### Email behavior

* Generate subject and body automatically
* Send through Gmail API
* Save each sent message in `emails`
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

The frontend is built with Next.js and should focus on visibility, control, and workflow management.

### Suggested screens

* Jobs dashboard
* Job detail page
* AI analysis view
* Resume generation view
* Email generation view
* Applications Kanban board
* Statistics overview
* Settings page

### Frontend responsibilities

* Display backend data
* Trigger actions
* Show job scores and scam flags
* Show application pipeline
* Present generated content
* Support fast browsing and filtering

---

## Deployment

A production deployment can use:

* Docker containers
* Managed PostgreSQL
* A server or container platform for FastAPI
* A host for Next.js frontend
* Secure secret management
* Gmail OAuth credentials
* Scheduled scraping jobs or workers

### Recommended deployment order

1. Database
2. Backend API
3. Frontend
4. Scraper jobs
5. AI service configuration
6. Email service configuration

---

## Roadmap

### Phase 1: Foundation

* Repository setup
* Backend skeleton
* PostgreSQL integration
* Core tables
* Alembic migrations
* Basic CRUD endpoints

### Phase 2: Ingestion and scoring

* Playwright scraping
* Job caching and deduplication
* AI scoring
* Scam checks

### Phase 3: Generation and automation

* Resume generation
* Cover letter generation
* Email generation and sending
* Store outputs in the database

### Phase 4: UI and tracking

* Next.js dashboard
* Job detail views
* Status tracking
* Statistics

### Phase 5: Hardening

* Validation and error handling
* Logging
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
* Document new endpoints and workflows.
* Keep automation safe, traceable, and debuggable.

---

## License


---

## Suggested first commit message

```bash
git commit -m "chore: initial project structure and architecture"
```

---

## Suggested next implementation steps

2. Initialize FastAPI and PostgreSQL
3. Add core SQLAlchemy models
4. Create Alembic migrations
5. Build job and application CRUD endpoints
6. Add scraping ingestion
7. Add AI services
8. Add email sending
9. Build the Next.js dashboard

---
