---
applyTo: "**"
---


### FastAPI conventions

- All routes live under /api/v1 with plural resource nouns
- Route handlers must be thin — validate input, call a service, return a response
- Use Pydantic schemas (in schemas/) for all request and response shapes — no raw dicts
- Return consistent error envelopes — never expose raw exception messages to clients
- Async endpoints for all I/O-bound operations

### SQLAlchemy and repositories

- All DB access goes through repository classes in repositories/
- Use SQLAlchemy 2.0-style queries (select(), not legacy query())
- Never use lazy loading in async contexts — use explicit joinedload or selectinload
- Repository methods must be typed — input and return types explicit

### ARQ workers

- Workers live in workers/ — one file per domain (ingestion, embedding, email)
- Workers must be idempotent — safe to retry on failure
- Log task start, completion, and errors — no silent failures
- Never call workers synchronously from request handlers — enqueue only

### Testing

- Use pytest with async support (pytest-asyncio)
- Test every service method and repository method
- Use a test database — never run tests against the development or production DB
- Mock external integrations (Apify, S3, AI APIs) in unit tests
