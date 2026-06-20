from app.services.ingestion.edgar_adapter import DOWNSIDE_FORMS, parse_submissions

SAMPLE = {
    "filings": {
        "recent": {
            "form": ["8-K", "4", "10-Q", "424B5", "10-K"],
            "filingDate": ["2026-05-01", "2026-04-28", "2026-04-15", "2026-04-10", "2026-02-20"],
            "accessionNumber": [
                "0000320193-26-000050",
                "0000320193-26-000049",
                "0000320193-26-000040",
                "0000320193-26-000039",
                "0000320193-26-000010",
            ],
            "primaryDocument": ["aapl8k.htm", "f4.htm", "aapl10q.htm", "p.htm", "aapl10k.htm"],
            "primaryDocDescription": ["8-K", "FORM 4", "10-Q", "424B5", "10-K"],
        }
    }
}


def test_parse_filters_to_downside_forms() -> None:
    out = parse_submissions(SAMPLE, cik="0000320193")
    forms = [f["form"] for f in out]
    # Keeps 8-K / 10-Q / 10-K; drops Form 4 and 424B5.
    assert forms == ["8-K", "10-Q", "10-K"]
    assert "4" not in forms
    assert "424B5" not in forms


def test_parse_builds_archive_url() -> None:
    out = parse_submissions(SAMPLE, cik="0000320193")
    first = out[0]
    assert first["accession"] == "0000320193-26-000050"
    assert "Archives/edgar/data/320193/000032019326000050/aapl8k.htm" in first["url"]


def test_parse_respects_limit() -> None:
    out = parse_submissions(SAMPLE, cik="0000320193", limit=1)
    assert len(out) == 1


def test_downside_forms_membership() -> None:
    assert "8-K" in DOWNSIDE_FORMS
    assert "4" not in DOWNSIDE_FORMS
