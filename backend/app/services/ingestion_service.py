import asyncio

from app.core.logger import get_logger
from app.integrations.embeddings import Embedder
from app.integrations.sources.base import JobSource
from app.repositories.job_repo import JobRepository
from app.services.normalization import deduplicate, normalise

logger = get_logger("app.services.ingestion_service")


class IngestionService:
    """Fetch enabled sources (best-effort, in parallel), normalize, dedup across
    sources, embed the batch, and idempotently upsert. HTTP/transport failures in
    one source don't sink the run — the API backbone keeps ingestion functional."""

    def __init__(self, sources: dict[str, JobSource], embedder: Embedder, repo: JobRepository) -> None:
        self.sources = sources
        self.embedder = embedder
        self.repo = repo
        self._scraped = {name for name, s in sources.items() if s.is_scraped}

    async def run(self, query: str, location: str | None = None, sources: list[str] | None = None) -> int:
        names = sources or list(self.sources)
        batches = await asyncio.gather(*[self._safe_fetch(n, query, location) for n in names])
        rows = [row for batch in batches for row in batch]
        if not rows:
            return 0

        rows = deduplicate(rows, self._scraped)
        # Drop jobs with no embeddable text (empty title AND description). Their embed input
        # would be an empty string, which OpenAI rejects with a 400 that sinks the whole
        # batch — and a job with neither title nor description is useless to rank anyway.
        dropped = [r for r in rows if not self._text(r)]
        if dropped:
            logger.warning("Skipping %d job(s) with empty title+description before embedding", len(dropped))
        rows = [r for r in rows if self._text(r)]
        if not rows:
            return 0

        vectors = await self.embedder.embed_batch([self._text(r) for r in rows])
        for row, vec in zip(rows, vectors):
            row["embedding"] = vec
        await self.repo.upsert_many(rows)
        logger.info("Ingested %d jobs for %r", len(rows), query)
        return len(rows)

    async def _safe_fetch(self, name: str, query: str, location: str | None) -> list[dict]:
        try:
            raw = await self.sources[name].fetch(query, location)
        except Exception:
            logger.exception("Source %s failed for %r — skipping", name, query)
            return []
        return [normalise(r, name) for r in raw]

    @staticmethod
    def _text(row: dict) -> str:
        return f"{row['title']}\n\n{row['description']}".strip()
