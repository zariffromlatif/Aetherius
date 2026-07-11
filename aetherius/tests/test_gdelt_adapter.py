from datetime import datetime, timezone

from app.services.ingestion.gdelt_adapter import (
    DOWNSIDE_DOMAINS,
    _article_to_text,
    _fmt_gdelt_datetime,
    _parse_gdelt_seendate,
    build_query,
    parse_articles,
)

SAMPLE_PAYLOAD = {
    "articles": [
        {
            "url": "https://www.reuters.com/business/finance/svb-collapse-2023-03-09/",
            "url_mobile": "",
            "title": "Silicon Valley Bank shares plunge as venture firms pull deposits",
            "seendate": "20230309T140000Z",
            "socialimage": "",
            "domain": "reuters.com",
            "language": "English",
            "sourcecountry": "United States",
        },
        {
            "url": "https://www.bloomberg.com/news/articles/2023-03-08/svb-financial-8k",
            "title": "SVB Financial 8-K discloses $21B securities sale at a loss",
            "seendate": "20230308T213000Z",
            "domain": "bloomberg.com",
            "language": "English",
        },
    ]
}


def test_parse_articles_returns_flat_list() -> None:
    out = parse_articles(SAMPLE_PAYLOAD)
    assert isinstance(out, list)
    assert len(out) == 2
    assert out[0]["domain"] == "reuters.com"


def test_parse_articles_handles_missing_key() -> None:
    assert parse_articles({}) == []
    assert parse_articles({"articles": None}) == []


def test_build_query_single_name_no_alias() -> None:
    q = build_query("Silicon Valley Bank", aliases=None)
    assert '"Silicon Valley Bank"' in q


def test_build_query_multiple_aliases_or_joined() -> None:
    q = build_query(
        "Silicon Valley Bank",
        aliases=["SVB", "SVB Financial Group"],
    )
    # Aliases without spaces stay bare; multi-word aliases get quoted.
    assert '"Silicon Valley Bank"' in q
    assert "SVB" in q
    assert '"SVB Financial Group"' in q
    assert " OR " in q
    # Multi-name query is parenthesized as a phrase-OR block.
    assert q.startswith("(") and q.endswith(")")


def test_build_query_stays_short_no_domain_block() -> None:
    # GDELT caps query length; adapter must not inject domain filters into the
    # query itself. Domain filtering happens in Python after the fetch.
    q = build_query("Silicon Valley Bank", aliases=["SVB"])
    assert "domain:" not in q


def test_fmt_gdelt_datetime_utc() -> None:
    dt = datetime(2023, 3, 9, 14, 0, 0, tzinfo=timezone.utc)
    assert _fmt_gdelt_datetime(dt) == "20230309140000"


def test_fmt_gdelt_datetime_assumes_utc_when_naive() -> None:
    dt = datetime(2023, 3, 9, 14, 0, 0)
    assert _fmt_gdelt_datetime(dt) == "20230309140000"


def test_parse_gdelt_seendate_roundtrips() -> None:
    parsed = _parse_gdelt_seendate("20230309T140000Z")
    assert parsed == datetime(2023, 3, 9, 14, 0, 0, tzinfo=timezone.utc)


def test_parse_gdelt_seendate_falls_back_on_garbage() -> None:
    # Malformed input must not crash the caller mid-ingest.
    parsed = _parse_gdelt_seendate("not-a-date")
    assert parsed.tzinfo is not None


def test_article_to_text_includes_key_fields() -> None:
    text = _article_to_text("Silicon Valley Bank", SAMPLE_PAYLOAD["articles"][0])
    # The query-target name must NOT be injected as a wrapper prefix. If the
    # name appears in the raw text, it must come from the article's own title,
    # not from a "News mention of X:" prefix — that prefix would false-positive
    # X on any adverse headline the query returned in which the actual subject
    # is a different company.
    assert not text.startswith("News mention of")
    assert "News mention of Silicon Valley Bank" not in text
    # Everything else (title, domain, URL) must still be present so downstream
    # scoring has enough to work with.
    assert "reuters.com" in text
    assert "https://www.reuters.com" in text
    assert "shares plunge" in text.lower()


def test_article_to_text_does_not_inject_target_name_when_title_omits_it() -> None:
    # This is the bug the wrapper prefix caused: a Wirecard-scandal article
    # returned by an Adyen query would end up labeled "News mention of Adyen"
    # even though "Adyen" never appeared in the title, then false-positive on
    # Adyen. Guard against that regression here.
    article = {
        "url": "https://finance.yahoo.com/x",
        "title": "Analysts on the Wirecard scandal deepens",
        "domain": "finance.yahoo.com",
        "seendate": "20200622T120000Z",
    }
    text = _article_to_text("Adyen NV", article)
    assert "Adyen" not in text


def test_downside_domains_covers_key_wires() -> None:
    for domain in ("reuters.com", "bloomberg.com", "wsj.com", "ft.com"):
        assert domain in DOWNSIDE_DOMAINS
