from datetime import datetime, timezone

from app.services.ingestion.service import compute_freshness, make_content_hash


def test_hash_consistency() -> None:
    t = "same text"
    assert make_content_hash(t) == make_content_hash(t)


def test_freshness_score_in_range() -> None:
    score = compute_freshness(datetime.now(timezone.utc))
    assert 0.0 <= score <= 1.0
