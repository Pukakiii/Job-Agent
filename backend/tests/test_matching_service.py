import json

import pytest

from app.exceptions import CorpusEmpty, CVNotFound, CVNotParsed, NoMatchesFound
from app.models.user import User
from app.repositories.cv_repo import CVRepository
from app.repositories.job_repo import JobRepository
from app.repositories.search_repo import SearchRepository
from app.services.matching_service import MatchingService

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


class FakeEmbedder:
    async def embed_batch(self, texts):
        return [[0.1] * 768 for _ in texts]

    async def embed_query(self, text):
        return [0.1] * 768


class RecordingEmbedder(FakeEmbedder):
    """Records every embed_query input so tests can assert what got embedded."""
    def __init__(self):
        self.queries: list[str] = []

    async def embed_query(self, text):
        self.queries.append(text)
        return [0.1] * 768


class FakeChat:
    """Returns a fixed rerank payload (built from indices the test controls)."""
    def __init__(self, matches):
        self._matches = matches

    async def chat(self, *, system_prompt, user_prompt, json_mode=False, **kw):
        return json.dumps({"matches": self._matches})


async def _user(db, email="m@test.io"):
    u = User(email=email, hashed_password="x", is_active=True, is_superuser=False, is_verified=False)
    db.add(u)
    await db.flush()
    return u


async def _parsed_cv(db, user_id):
    cv = await CVRepository(db).create(user_id, f"cvs/{user_id}/a.docx", "a.docx", DOCX_MIME)
    await CVRepository(db).set_parsing_result(cv.id, "Python engineer, 5 years", {"name": "Jo"})
    return cv


async def _seed_jobs(db, n):
    rows = [{
        "source": "adzuna", "source_job_id": str(i), "content_hash": f"h{i}",
        "title": f"Job {i}", "company": "ACME", "location": "Berlin",
        "url": f"http://j/{i}", "description": "python work", "embedding": [0.1] * 768,
    } for i in range(n)]
    await JobRepository(db).upsert_many(rows)
    await db.flush()


def _service(db, matches):
    return MatchingService(
        CVRepository(db), JobRepository(db), SearchRepository(db),
        FakeEmbedder(), FakeChat(matches),
    )


async def test_find_matches_persists_ranked_results(db):
    user = await _user(db)
    cv = await _parsed_cv(db, user.id)
    await _seed_jobs(db, 5)
    matches = [{"index": 0, "score": 0.9, "explanation": "great"},
               {"index": 2, "score": 0.7, "explanation": "good"}]
    search = await _service(db, matches).find_matches(user.id, cv.id, "python role")
    await db.flush()

    assert len(search.results) == 2
    assert [r.rank for r in search.results] == [1, 2]          # rank-ordered
    assert search.results[0].explanation == "great"
    assert search.results[0].job.url.startswith("http://j/")   # job eager-loaded


async def test_find_matches_caps_at_ten(db):
    user = await _user(db, "cap@test.io")
    cv = await _parsed_cv(db, user.id)
    await _seed_jobs(db, 20)
    matches = [{"index": i, "score": 1.0 - i / 100, "explanation": "x"} for i in range(20)]
    search = await _service(db, matches).find_matches(user.id, cv.id, "python")
    assert len(search.results) == 10  # ADR-003 hard cap


async def test_find_matches_drops_out_of_range_and_duplicate_indices(db):
    user = await _user(db, "dup@test.io")
    cv = await _parsed_cv(db, user.id)
    await _seed_jobs(db, 3)
    matches = [{"index": 0, "score": 0.9, "explanation": "a"},
               {"index": 0, "score": 0.8, "explanation": "dupe"},
               {"index": 99, "score": 0.7, "explanation": "out of range"}]
    search = await _service(db, matches).find_matches(user.id, cv.id, "python")
    assert len(search.results) == 1


async def test_find_matches_rejects_foreign_cv(db):
    owner = await _user(db, "owner@test.io")
    other = await _user(db, "other@test.io")
    cv = await _parsed_cv(db, owner.id)
    await _seed_jobs(db, 2)
    with pytest.raises(CVNotFound):
        await _service(db, []).find_matches(other.id, cv.id, "python")


async def test_find_matches_requires_parsed_cv(db):
    user = await _user(db, "unparsed@test.io")
    cv = await CVRepository(db).create(user.id, f"cvs/{user.id}/a.docx", "a.docx", DOCX_MIME)
    await _seed_jobs(db, 2)
    with pytest.raises(CVNotParsed):
        await _service(db, []).find_matches(user.id, cv.id, "python")


async def test_find_matches_empty_corpus_signals_ingest(db):
    user = await _user(db, "empty@test.io")
    cv = await _parsed_cv(db, user.id)  # no jobs seeded
    with pytest.raises(CorpusEmpty):
        await _service(db, []).find_matches(user.id, cv.id, "python")


async def test_find_matches_uses_cached_cv_embedding(db):
    user = await _user(db, "cache@test.io")
    cv = await CVRepository(db).create(user.id, f"cvs/{user.id}/a.docx", "a.docx", DOCX_MIME)
    await CVRepository(db).set_parsing_result(
        cv.id, "Python engineer, 5 years", {"name": "Jo"}, embedding=[0.2] * 768
    )
    cid = cv.id
    await _seed_jobs(db, 3)
    rec = RecordingEmbedder()
    svc = MatchingService(
        CVRepository(db), JobRepository(db), SearchRepository(db),
        rec, FakeChat([{"index": 0, "score": 0.9, "explanation": "x"}]),
    )
    await svc.find_matches(user.id, cid, "remote backend")

    # With a cached CV vector, only the short prompt is embedded — not the full CV text.
    assert rec.queries == ["remote backend"]


async def test_find_matches_falls_back_to_full_text_without_cached_embedding(db):
    user = await _user(db, "nocache@test.io")
    cv = await _parsed_cv(db, user.id)  # parsed but no cached embedding
    await _seed_jobs(db, 3)
    rec = RecordingEmbedder()
    svc = MatchingService(
        CVRepository(db), JobRepository(db), SearchRepository(db),
        rec, FakeChat([{"index": 0, "score": 0.9, "explanation": "x"}]),
    )
    await svc.find_matches(user.id, cv.id, "remote backend")

    # Fallback: embeds the combined query text (prompt + summary + extracted_text).
    assert len(rec.queries) == 1
    assert "remote backend" in rec.queries[0]
    assert "Python engineer" in rec.queries[0]


async def test_find_matches_filters_candidates_by_location(db):
    user = await _user(db, "loc@test.io")
    cv = await _parsed_cv(db, user.id)
    await JobRepository(db).upsert_many([
        {"source": "adzuna", "source_job_id": "W", "content_hash": "hw", "title": "Warsaw Dev",
         "company": "A", "location": "Warsaw, PL", "url": "http://j/w", "description": "d",
         "embedding": [0.1] * 768},
        {"source": "adzuna", "source_job_id": "U", "content_hash": "hu", "title": "USA Dev",
         "company": "B", "location": "New York, USA", "url": "http://j/u", "description": "d",
         "embedding": [0.1] * 768},
    ])
    await db.flush()
    # location=Warsaw -> only the Warsaw job is a candidate; FakeChat ranks index 0.
    svc = MatchingService(
        CVRepository(db), JobRepository(db), SearchRepository(db),
        FakeEmbedder(), FakeChat([{"index": 0, "score": 0.9, "explanation": "x"}]),
    )
    search = await svc.find_matches(user.id, cv.id, "dev", location="Warsaw")
    await db.flush()

    assert len(search.results) == 1
    assert "Warsaw" in search.results[0].job.location


async def test_find_matches_all_indices_out_of_range_raises(db):
    user = await _user(db, "oob@test.io")
    cv = await _parsed_cv(db, user.id)
    await _seed_jobs(db, 3)
    # LLM returns only out-of-range indices → ranked list is empty
    matches = [{"index": 99, "score": 0.9, "explanation": "x"},
               {"index": 100, "score": 0.8, "explanation": "y"}]
    with pytest.raises(NoMatchesFound):
        await _service(db, matches).find_matches(user.id, cv.id, "python")
