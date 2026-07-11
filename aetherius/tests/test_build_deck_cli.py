"""End-to-end tests for scripts/build_deck.py

These invoke the CLI's ``build()`` entry point directly (bypassing argparse)
against the committed SVB-2023 fixture — no network, no DB, fully offline.
"""
from __future__ import annotations

import sys
from argparse import Namespace
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = REPO_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

build_deck = pytest.importorskip("build_deck")

SVB_FIXTURE = REPO_ROOT / "simulations" / "backtest" / "events" / "svb-2023" / "observations.jsonl"


def _base_args(tmp_path: Path, **overrides) -> Namespace:
    """Build a Namespace with sensible defaults for the SVB fixture path."""
    ns = Namespace(
        ticker="SIVB",
        name="SVB Financial Group",
        sector="Regional Banks",
        aliases="Silicon Valley Bank,SVB",
        priority="critical",
        thesis="Concentrated regional-bank position.",
        counterparty=None,
        window="2023-03-06:2023-03-12",
        fixture_jsonl=str(SVB_FIXTURE),
        live=False,
        max_records=100,
        top_evidence_n=8,
        out=str(tmp_path / "deck.html"),
    )
    for k, v in overrides.items():
        setattr(ns, k, v)
    return ns


# ---------------------------------------------------------------------------
# End-to-end build
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not SVB_FIXTURE.exists(), reason="SVB fixture not present")
def test_build_deck_from_fixture_end_to_end(tmp_path: Path) -> None:
    """Fixture path: read observations, score, render, gate, write file."""
    args = _base_args(tmp_path)
    rc = build_deck.build(args)
    assert rc == 0, "expected clean exit"
    out = Path(args.out)
    assert out.exists(), "deck HTML must be written"
    html = out.read_text(encoding="utf-8")
    # Structural checks — the cover, exec summary, and disclaimer must all
    # be present in the rendered artifact.
    assert "Target Stress-Test Deck" in html
    assert "SIVB" in html
    assert "SVB Financial Group" in html
    assert "not investment advice" in html
    # Analyst-supplied thesis lands on the deck.
    assert "Concentrated regional-bank position" in html


@pytest.mark.skipif(not SVB_FIXTURE.exists(), reason="SVB fixture not present")
def test_build_deck_with_counterparties_carries_them_into_html(tmp_path: Path) -> None:
    args = _base_args(
        tmp_path,
        counterparty=[
            "FRC:First Republic Bank:peer:0.6:First Republic",
            "SBNY:Signature Bank:peer:0.6:Signature Bank",
        ],
    )
    rc = build_deck.build(args)
    assert rc == 0
    html = Path(args.out).read_text(encoding="utf-8")
    assert "First Republic Bank" in html
    assert "Signature Bank" in html


# ---------------------------------------------------------------------------
# Argument parsers
# ---------------------------------------------------------------------------

def test_parse_window_iso_dates() -> None:
    a, b = build_deck._parse_window("2023-03-06:2023-03-12")
    assert a.year == 2023 and a.month == 3 and a.day == 6
    assert b.year == 2023 and b.month == 3 and b.day == 12


def test_parse_window_iso_datetimes() -> None:
    a, b = build_deck._parse_window("2023-03-06T09:00:00Z:2023-03-12T21:00:00Z")
    assert a.hour == 9
    assert b.hour == 21


def test_parse_window_rejects_missing_separator() -> None:
    import argparse
    with pytest.raises(argparse.ArgumentTypeError):
        build_deck._parse_window("2023-03-06")


def test_parse_counterparty_minimum_spec() -> None:
    cp = build_deck._parse_counterparty("FRC:First Republic Bank:peer")
    assert cp["ticker"] == "FRC"
    assert cp["company_name"] == "First Republic Bank"
    assert cp["relationship_type"] == "peer"
    # Strength defaults to 0.5, aliases default to empty.
    assert cp["strength"] == 0.5
    assert cp["aliases"] == []


def test_parse_counterparty_full_spec() -> None:
    cp = build_deck._parse_counterparty("FRC:First Republic Bank:peer:0.7:First Republic,FirstRep")
    assert cp["strength"] == 0.7
    assert cp["aliases"] == ["First Republic", "FirstRep"]


def test_parse_counterparty_rejects_too_few_fields() -> None:
    import argparse
    with pytest.raises(argparse.ArgumentTypeError):
        build_deck._parse_counterparty("FRC:only-two-fields")


def test_parse_csv_handles_empty_and_whitespace() -> None:
    assert build_deck._parse_csv(None) == []
    assert build_deck._parse_csv("") == []
    assert build_deck._parse_csv("a, b ,, c ") == ["a", "b", "c"]


# ---------------------------------------------------------------------------
# Mode selection
# ---------------------------------------------------------------------------

def test_build_returns_error_when_no_source_specified(tmp_path: Path) -> None:
    args = _base_args(tmp_path, fixture_jsonl=None, live=False)
    rc = build_deck.build(args)
    assert rc == 2


def test_build_fails_gracefully_on_missing_fixture(tmp_path: Path) -> None:
    args = _base_args(tmp_path, fixture_jsonl=str(tmp_path / "does-not-exist.jsonl"))
    with pytest.raises(FileNotFoundError):
        build_deck.build(args)
