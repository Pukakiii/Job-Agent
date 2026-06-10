# Backend Docker Setup

Documents the two files that define how the backend is packaged and what it depends on at runtime:

- [`infra/docker/backend/Dockerfile.backend`](../infra/docker/backend/Dockerfile.backend) — multi-stage production image
- [`infra/docker/backend/requirements.txt`](../infra/docker/backend/requirements.txt) — runtime Python dependencies

---

## Table of Contents

- [requirements.txt](#requirementstxt)
  - [Why two files?](#why-two-files)
  - [Keeping requirements.txt up to date](#keeping-requirementstxt-up-to-date)
    - [Adding a new package](#adding-a-new-package)
    - [Removing a package](#removing-a-package)
    - [Pinning a version](#pinning-a-version)
  - [Package inventory](#package-inventory)
- [Dockerfile.backend](#dockerfilebackend)
  - [Why multi-stage?](#why-multi-stage)
  - [Stage 1 — builder](#stage-1--builder)
  - [Stage 2 — runner](#stage-2--runner)
  - [Build context](#build-context)
  - [Shared image — api vs worker](#shared-image--api-vs-worker)
  - [Running Alembic migrations](#running-alembic-migrations)

---

## requirements.txt

`requirements.txt` is the **pip-installable dependency list** used by the Docker build. It is deliberately separate from `backend/pyproject.toml`.

### Why two files?

| File | Used by | Purpose |
|---|---|---|
| `backend/pyproject.toml` | Local dev, `pip install -e .`, tooling | Source of truth; also carries dev dependencies, build system, and tool config |
| `infra/docker/backend/requirements.txt` | Docker build only | Flat list of runtime packages for fast, reproducible `pip install` inside the image |

The two must stay in sync — `requirements.txt` mirrors the `[project.dependencies]` section of `pyproject.toml`. Dev-only packages (`pytest`, `ruff`, etc.) are intentionally excluded to keep the image lean.

### Keeping requirements.txt up to date

Whenever you add, remove, or change a runtime dependency, update **both** files.

#### Adding a new package

1. Add the package to `pyproject.toml` under `[project.dependencies]`:
   ```toml
   dependencies = [
       ...
       "httpx",       # existing
       "tenacity",    # ← new package
   ]
   ```

2. Add the same package (without quotes or trailing commas) to `requirements.txt`:
   ```
   httpx
   tenacity
   ```

3. Rebuild the Docker image so the new package is installed:
   ```bash
   docker compose build api
   # or rebuild everything
   docker compose up --build
   ```

#### Removing a package

Remove it from **both** `pyproject.toml` and `requirements.txt`, then rebuild.

#### Pinning a version

Versions are intentionally unpinned — `pip` resolves the latest compatible version at build time. If you need to pin (e.g. to fix a known-good version or avoid a breaking release):

```
# requirements.txt
fastapi==0.115.0
```

```toml
# pyproject.toml
dependencies = [
    "fastapi==0.115.0",
]
```

> **Tip:** To lock the entire dependency tree (including transitive deps), use `pip-compile` from [`pip-tools`](https://pip-tools.readthedocs.io):
> ```bash
> pip install pip-tools
> pip-compile backend/pyproject.toml --output-file infra/docker/backend/requirements.txt
> ```
> This generates a fully pinned `requirements.txt` from `pyproject.toml` in one command and keeps the two files in sync automatically.

### Package inventory

| Package | Role |
|---|---|
| `fastapi` | ASGI web framework |
| `uvicorn[standard]` | ASGI server (with `uvloop` + `httptools` for performance) |
| `sqlalchemy[asyncio]` | ORM + async engine |
| `alembic` | Database migrations |
| `anyio` | Async concurrency primitives (used by boto3 offload) |
| `pydantic` | Data validation and serialisation |
| `pydantic-settings` | Settings management (reads env vars / `.env`) |
| `asyncpg` | Async PostgreSQL driver used by SQLAlchemy |
| `pgvector` | `pgvector` type support for SQLAlchemy (vector columns) |
| `arq` | Redis-backed async job queue (background worker) |
| `redis` | Redis client used by `arq` |
| `fastapi-users[sqlalchemy]` | Auth (JWT, cookies, user management) wired to SQLAlchemy |
| `httpx` | Async HTTP client (tests, internal service calls) |
| `boto3` | AWS / MinIO S3 client (CV storage) |
| `python-multipart` | Multipart form parsing required by FastAPI file upload |
| `filetype` | MIME-type detection from file bytes (CV validation) |


## Dockerfile.backend

The Dockerfile uses a **two-stage build** to produce a small, secure production image.

### Why multi-stage?

The first stage (`builder`) needs compilers (`build-essential`, `libpq-dev`) to build C extensions like `asyncpg` and `pgvector`. Those tools add hundreds of megabytes and are not needed at runtime. Multi-stage builds let us compile in one layer and copy only the compiled output into a clean final image.

```
 ┌─────────────────────────────────────────┐
 │  Stage 1: builder (python:3.11-slim)    │
 │                                         │
 │  apt: build-essential, libpq-dev        │
 │  python -m venv /opt/venv               │
 │  pip install -r requirements.txt        │
 └───────────────┬─────────────────────────┘
                 │  COPY --from=builder /opt/venv /opt/venv
                 ▼
 ┌─────────────────────────────────────────┐
 │  Stage 2: runner (python:3.11-slim)     │
 │                                         │
 │  apt: curl (healthcheck only)           │
 │  Non-root user: appuser (uid 10001)     │
 │  /opt/venv  ← compiled packages         │
 │  /app       ← backend source code       │
 └─────────────────────────────────────────┘
```

### Stage 1 — builder

| Step | What it does |
|---|---|
| `FROM python:3.11-slim AS builder` | Minimal Debian-based Python image; no extras |
| `ENV PYTHONDONTWRITEBYTECODE=1` | Skips `.pyc` files — irrelevant in containers |
| `ENV PYTHONUNBUFFERED=1` | Forces stdout/stderr to flush immediately (important for log streaming) |
| `apt-get install build-essential libpq-dev` | C compiler + PostgreSQL headers needed to build `asyncpg` and `psycopg` |
| `python -m venv /opt/venv` | Creates an isolated virtual environment at a fixed path |
| `pip install -r requirements.txt` | Installs all runtime packages into the venv; `--no-cache-dir` keeps the layer lean |

### Stage 2 — runner

| Step | What it does |
|---|---|
| `FROM python:3.11-slim AS runner` | Fresh base — no build tools |
| `ENV PYTHONPATH=/app` | Lets Python find `app.*` imports without installing the package |
| `ENV PATH="/opt/venv/bin:$PATH"` | Activates the virtual environment globally |
| `apt-get install curl` | Required only for the Docker healthcheck (`curl -f http://localhost:8000/health`) |
| `groupadd / useradd appuser` | Creates a dedicated non-root user (uid/gid 10001); running as root inside a container is a security risk |
| `COPY --from=builder /opt/venv /opt/venv` | Pulls the compiled packages from stage 1 — no compilers land in the final image |
| `COPY backend/app /app/app` | Application source code |
| `COPY backend/alembic* /app/` | Alembic migration scripts and config (needed to run `alembic upgrade head`) |
| `chown -R appuser:appgroup /app` | Gives the non-root user ownership of its working directory |
| `USER appuser` | Drops root privileges |
| `EXPOSE 8000` | Documents the port; does not publish it (Compose handles that) |
| `CMD ["uvicorn", ...]` | Default command for the `api` service |

### Build context

The build context is the **project root** (`.`), not `infra/docker/backend/`. This is required because the `COPY` instructions reference paths from both `backend/` and `infra/docker/backend/`:

```yaml
# docker-compose.yaml
api:
  build:
    context: .                                      # ← project root
    dockerfile: infra/docker/backend/Dockerfile.backend
```

### Shared image — api vs worker

The `api` and `worker` services in Compose both use the **same image** (`job-agent-backend:latest`). The only difference is the entrypoint command:

| Service | Command |
|---|---|
| `api` | `uvicorn app.main:app --host 0.0.0.0 --port 8000` (default `CMD`) |
| `worker` | `arq app.workers.settings.WorkerSettings` (overrides `CMD` in Compose) |

This means only one Docker build is needed for both services, and both always run the same version of the code.

### Running Alembic migrations

Migrations are not baked into startup. Run them as a one-off after the first boot or after any schema change:

```bash
docker compose run --rm api alembic upgrade head
```

This spins up a temporary `api` container, runs the migration against the live `postgres` service, then removes itself.
