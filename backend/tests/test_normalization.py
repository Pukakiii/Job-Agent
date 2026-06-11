from app.integrations.sources.base import RawJob
from app.services.normalization import content_hash, deduplicate, normalise


def _raw(**kw):
    base = dict(source_job_id="x", title="Python Dev", url="http://a", description="d",
                company="ACME", location="Berlin")
    base.update(kw)
    return RawJob(**base)


def test_normalise_maps_all_job_columns():
    row = normalise(_raw(), "adzuna")
    assert row["source"] == "adzuna"
    assert row["source_job_id"] == "x"
    assert set(row) == {
        "source", "source_job_id", "content_hash", "title",
        "company", "location", "url", "description", "posted_at",
    }


def test_content_hash_is_stable_and_cross_source_identical():
    # same logical listing on two boards -> same content_hash
    a = normalise(_raw(source_job_id="A1"), "adzuna")
    b = normalise(_raw(source_job_id="B1"), "indeed")
    assert a["content_hash"] == b["content_hash"]
    assert content_hash("Python Dev", "ACME", "Berlin") == a["content_hash"]


def test_deduplicate_api_source_wins_over_scraped():
    rows = [
        normalise(_raw(source_job_id="B1"), "indeed"),    # scraped
        normalise(_raw(source_job_id="A1"), "adzuna"),    # API
    ]
    out = deduplicate(rows, scraped_sources={"indeed"})
    assert len(out) == 1
    assert out[0]["source"] == "adzuna"  # API won despite arriving second


def test_deduplicate_keeps_distinct_listings():
    rows = [normalise(_raw(title="A"), "adzuna"), normalise(_raw(title="B"), "adzuna")]
    assert len(deduplicate(rows, scraped_sources=set())) == 2
