import hashlib

from app.integrations.sources.base import RawJob


def _norm(text: str | None) -> str:
    return (text or "").strip().lower()


def content_hash(title: str, company: str | None, location: str | None) -> str:
    """Stable cross-source identity for a listing (same job on two boards -> same hash)."""
    payload = "|".join((_norm(title), _norm(company), _norm(location)))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def normalise(raw: RawJob, source: str) -> dict:
    """Map a source's RawJob onto the Job table columns (minus id/embedding/ingested_at)."""
    return {
        "source": source,
        "source_job_id": raw.source_job_id,
        "content_hash": content_hash(raw.title, raw.company, raw.location),
        "title": raw.title,
        "company": raw.company,
        "location": raw.location,
        "url": raw.url,
        "description": raw.description,
        "posted_at": raw.posted_at,
    }


def deduplicate(rows: list[dict], scraped_sources: set[str]) -> list[dict]:
    """Collapse rows sharing a content_hash. A row from a sanctioned API source
    replaces one from a scraped source; otherwise first-seen wins. Order preserved."""
    chosen: dict[str, dict] = {}
    order: list[str] = []
    for row in rows:
        h = row["content_hash"]
        if h not in chosen:
            chosen[h] = row
            order.append(h)
            continue
        incumbent = chosen[h]
        if incumbent["source"] in scraped_sources and row["source"] not in scraped_sources:
            chosen[h] = row  # API beats scraped
    return [chosen[h] for h in order]
