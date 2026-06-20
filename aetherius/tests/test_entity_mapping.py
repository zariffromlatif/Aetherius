from app.services.entity_mapping.service import (
    _contains_phrase,
    _looks_like_ticker,
    extract_entities,
)


def test_stoplist_acronyms_are_not_tickers() -> None:
    for noise in ["CEO", "USD", "GDP", "FED", "AI", "CPI", "SEC", "FDA"]:
        assert not _looks_like_ticker(noise)


def test_real_tickers_pass() -> None:
    for ticker in ["AAPL", "MSFT", "F", "NVDA", "BRK"]:
        assert _looks_like_ticker(ticker)


def test_class_suffix_ticker() -> None:
    assert _looks_like_ticker("BRK.B")


def test_extract_filters_noise_keeps_tickers() -> None:
    text = "The CEO said USD and GDP pressure hit AAPL and MSFT per the SEC filing."
    out = extract_entities(text)
    tickers = {e["ticker"] for e in out}
    assert "AAPL" in tickers
    assert "MSFT" in tickers
    assert "CEO" not in tickers
    assert "USD" not in tickers
    assert "GDP" not in tickers
    assert "SEC" not in tickers


def test_extract_dedupes() -> None:
    out = extract_entities("AAPL AAPL AAPL guidance cut")
    assert sum(1 for e in out if e["ticker"] == "AAPL") == 1


def test_cashtag_gets_higher_confidence() -> None:
    out = extract_entities("$AAPL is at risk")
    aapl = next(e for e in out if e["ticker"] == "AAPL")
    assert aapl["match_confidence"] >= 0.85


def test_word_boundary_prevents_substring_false_positives() -> None:
    text_upper = "SUPPLY CHAIN ISSUES; HE SAID THE CATALYST IS GONE"
    assert not _contains_phrase(text_upper, "AI")
    assert not _contains_phrase(text_upper, "CAT")


def test_word_boundary_matches_standalone_token() -> None:
    assert _contains_phrase("RISK FLAGGED FOR AAPL TODAY", "AAPL")


def test_contains_phrase_handles_empty() -> None:
    assert not _contains_phrase("SOME TEXT", None)
    assert not _contains_phrase("SOME TEXT", "")