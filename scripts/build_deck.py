"""Build a Target Stress-Test Deck for a public-equity ticker and window.

Two operating modes:

  1. Fixture mode (--fixture-jsonl PATH): reads observations from a local
     JSONL file (typically simulations/backtest/events/<event>/observations.jsonl).
     Fully offline, deterministic, and reproducible. Use this for sample decks
     you send to prospects and for regression demos.

  2. Live mode (default): pulls observations directly from GDELT DOC 2.0 for
     the target company (and optional counterparties) across the analysis
     window. Requires internet access. Optionally also queries SEC EDGAR
     for recent filings via --with-edgar.

Both modes hand off to services.reporting.target_stress_test.build_deck_data,
then render the deck template, run the quality gates, and write a
self-contained HTML file that a browser can print to PDF.

Examples
--------

    # From a fixture, fastest path for a sample deck
    python scripts/build_deck.py \\
      --ticker SIVB --name "SVB Financial Group" \\
      --sector "Regional Banks" --aliases "Silicon Valley Bank,SVB" \\
      --window 2023-03-06:2023-03-12 \\
      --fixture-jsonl simulations/backtest/events/svb-2023/observations.jsonl \\
      --out sivb-stress-test.html

    # Live GDELT pull for a real target on the last 90 days
    python scripts/build_deck.py \\
      --ticker WDI --name "Wirecard AG" --aliases "Wirecard" \\
      --window 2020-06-15:2020-06-30 \\
      --live --out wdi-stress-test.html
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = REPO_ROOT / "aetherius"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

# Imports below live under aetherius/ so must come after the sys.path fixup.
from app.services.ingestion.gdelt_adapter import (  # noqa: E402
    DOWNSIDE_DOMAINS,
    _article_to_text,
    _parse_gdelt_seendate,
    fetch_articles,
)
from app.services.reporting.target_stress_test import (  # noqa: E402
    build_deck_data,
    deck_quality_gates,
    render_deck_html,
)


def _parse_window(value: str) -> tuple[datetime, datetime]:
    """Parse ``YYYY-MM-DD:YYYY-MM-DD`` or ``YYYY-MM-DDT..Z:YYYY-MM-DDT..Z``.

    Datetimes contain their own ``:`` characters (in the time component), so
    a naive ``split(":", 1)`` is wrong for the ISO-with-time form. We anchor
    on the boundary between the two timestamps: either the ``Z:`` between two
    UTC-suffixed datetimes, or the ``:`` between two date-only forms.
    """
    if "Z:" in value:
        a, b = value.split("Z:", 1)
        a = a + "Z"
    elif ":" in value and "T" not in value:
        a, b = value.split(":", 1)
    else:
        raise argparse.ArgumentTypeError(
            "--window must be START:END where both are ISO dates "
            "(YYYY-MM-DD) or both are UTC datetimes (YYYY-MM-DDTHH:MM:SSZ)"
        )

    def _to_dt(s: str) -> datetime:
        if "T" not in s:
            s = s + "T00:00:00Z"
        return datetime.fromisoformat(s.replace("Z", "+00:00"))

    return _to_dt(a), _to_dt(b)


def _parse_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [x.strip() for x in value.split(",") if x.strip()]


def _parse_counterparty(spec: str) -> dict:
    """Parse a counterparty spec: ``TICKER:Name:relationship:strength[:aliases,pipe|sep]``.

    Example: ``FRC:First Republic Bank:peer:0.6:First Republic``
    """
    parts = spec.split(":")
    if len(parts) < 3:
        raise argparse.ArgumentTypeError(
            "counterparty must be TICKER:Name:relationship[:strength[:aliases,csv]]"
        )
    ticker, name, rel = parts[0], parts[1], parts[2]
    strength = float(parts[3]) if len(parts) >= 4 and parts[3] else 0.5
    aliases = [a.strip() for a in parts[4].split(",") if a.strip()] if len(parts) >= 5 else []
    return {
        "ticker": ticker,
        "company_name": name,
        "relationship_type": rel,
        "strength": strength,
        "aliases": aliases,
        "priority_level": "high",
    }


def _load_fixture_observations(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"fixture not found: {path}")
    obs: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            obs.append(json.loads(line))
    return obs


def _live_fetch_observations(
    company_name: str,
    aliases: list[str],
    counterparties: list[dict],
    window_start: datetime,
    window_end: datetime,
    max_records_per_target: int,
) -> tuple[list[dict], dict[str, int]]:
    """Pull GDELT articles for target + counterparties and coerce to observations.

    Returns ``(observations, per_target_counts)`` where ``per_target_counts``
    maps each target/counterparty to the number of articles GDELT returned for
    it, so the caller can warn when a target came back empty (rate-limited).
    """

    def _pull(name: str, ali: list[str]) -> list[dict]:
        try:
            articles = fetch_articles(
                company_name=name,
                aliases=ali,
                window_start=window_start,
                window_end=window_end,
                max_records=max_records_per_target,
                domain_whitelist=DOWNSIDE_DOMAINS,
            )
        except Exception as e:  # noqa: BLE001
            print(f"  ! GDELT error for {name!r}: {e}", file=sys.stderr)
            return []
        out: list[dict] = []
        for a in articles:
            url = (a.get("url") or "").strip()
            if not url:
                continue
            dt = _parse_gdelt_seendate(a.get("seendate") or "")
            out.append(
                {
                    "observed_at": dt.isoformat().replace("+00:00", "Z"),
                    "source_type": "news",
                    "source_name": a.get("domain") or "GDELT news",
                    "source_url": url,
                    "title": (a.get("title") or "").strip(),
                    "raw_text": _article_to_text(name, a),
                    "source_confidence": 0.75,
                }
            )
        return out

    observations: list[dict] = []
    seen_urls: set[str] = set()
    # Per-target pulled counts so the caller can warn loudly when a target
    # returned nothing (the rate-limit / bad-query smell — see the 429 behavior
    # documented in gdelt_adapter). A silently thin deck is a trust-breaker.
    per_target_counts: dict[str, int] = {}
    print(f"  [target] fetching GDELT for {company_name!r} + {aliases} ...", flush=True)
    target_rows = _pull(company_name, aliases)
    per_target_counts[company_name] = len(target_rows)
    for row in target_rows:
        if row["source_url"] not in seen_urls:
            seen_urls.add(row["source_url"])
            observations.append(row)
    for cp in counterparties:
        cp_name = cp.get("company_name") or cp["ticker"]
        cp_aliases = cp.get("aliases") or []
        print(f"  [{cp['ticker']}] fetching GDELT for {cp_name!r} + {cp_aliases} ...", flush=True)
        cp_rows = _pull(cp_name, cp_aliases)
        per_target_counts[cp["ticker"]] = len(cp_rows)
        for row in cp_rows:
            if row["source_url"] not in seen_urls:
                seen_urls.add(row["source_url"])
                observations.append(row)
    return observations, per_target_counts


def build(args: argparse.Namespace) -> int:
    window_start, window_end = _parse_window(args.window)

    target = {
        "ticker": args.ticker,
        "company_name": args.name or args.ticker,
        "sector": args.sector,
        "aliases": _parse_csv(args.aliases),
        "priority_level": args.priority,
        "thesis": args.thesis,
    }

    counterparties = [_parse_counterparty(spec) for spec in (args.counterparty or [])]

    if args.fixture_jsonl:
        print(f"Loading observations from fixture: {args.fixture_jsonl}", flush=True)
        observations = _load_fixture_observations(Path(args.fixture_jsonl))
    elif args.live:
        print("Pulling live observations from GDELT DOC 2.0 ...", flush=True)
        observations, per_target_counts = _live_fetch_observations(
            company_name=target["company_name"],
            aliases=target["aliases"],
            counterparties=counterparties,
            window_start=window_start,
            window_end=window_end,
            max_records_per_target=args.max_records,
        )
        # Loud warning on any target that returned zero. GDELT rate-limits (429)
        # cause a target to come back empty, which silently thins the deck. A
        # client paying for coverage on a name must not get a deck whose subject
        # returned nothing without a loud signal to re-run.
        empty = [name for name, n in per_target_counts.items() if n == 0]
        if empty:
            print(
                f"  ⚠ WARNING: {len(empty)} of {len(per_target_counts)} target(s) "
                f"returned 0 articles: {', '.join(empty)}",
                file=sys.stderr,
                flush=True,
            )
            print(
                "    This is almost always GDELT rate-limiting (429), not an "
                "absence of news. Wait a minute and re-run before delivering.",
                file=sys.stderr,
                flush=True,
            )
        # Hard stop if the PRIMARY target came back empty — the deck's own
        # subject has no coverage, so it is not deliverable.
        if per_target_counts.get(target["company_name"], 0) == 0:
            print(
                "  ✗ ABORT: the primary target returned 0 articles. The deck "
                "would have no coverage on its own subject. Re-run after the "
                "rate limit clears; not writing a deck.",
                file=sys.stderr,
                flush=True,
            )
            return 3
    else:
        print(
            "ERROR: provide either --fixture-jsonl PATH or --live",
            file=sys.stderr,
        )
        return 2

    print(f"Loaded {len(observations)} observation(s).", flush=True)

    deck = build_deck_data(
        target=target,
        counterparties=counterparties,
        observations=observations,
        window_start=window_start,
        window_end=window_end,
        top_evidence_n=args.top_evidence_n,
    )
    html = render_deck_html(deck)
    ok, issues = deck_quality_gates(deck, html)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")

    md = deck["metadata"]
    print("Deck rendered:", out_path, flush=True)
    print(
        f"  observations_in_window : {md['observations_in_window']}",
        f"  scored_matches         : {md['scored_matches']}",
        f"  shippable_flags        : {md['shippable_flags']}",
        f"  peak_severity          : {md['peak_severity']}",
        f"  first_elevated_flag_at : {md['first_elevated_flag_at']}",
        sep="\n",
        flush=True,
    )
    if ok:
        print("  quality gates          : PASS", flush=True)
    else:
        print("  quality gates          : FAIL", file=sys.stderr, flush=True)
        for issue in issues:
            print(f"    - {issue}", file=sys.stderr, flush=True)
        # Non-zero exit but the deck file was still written so the analyst
        # can inspect the failure without rerunning the ingestion path.
        return 1

    print(
        "\nTo produce a PDF: open the HTML in a browser and use "
        "'File > Print > Save as PDF' (letter, portrait, default margins).",
        flush=True,
    )
    return 0


def _default_window() -> str:
    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=90)
    return f"{start.isoformat()}:{end.isoformat()}"


def main() -> int:
    p = argparse.ArgumentParser(
        prog="build_deck",
        description="Build a Target Stress-Test Deck (HTML) for a ticker and window.",
    )
    p.add_argument("--ticker", required=True, help="Primary target ticker (e.g. SIVB).")
    p.add_argument("--name", help="Company name (defaults to --ticker).")
    p.add_argument("--sector", help="Optional sector tag for the cover page.")
    p.add_argument("--aliases", help='CSV of aliases, e.g. "Silicon Valley Bank,SVB".')
    p.add_argument(
        "--priority",
        default="critical",
        choices=("low", "normal", "high", "critical"),
        help="Target priority level (default: critical).",
    )
    p.add_argument("--thesis", help="One-line analyst thesis printed on the summary page.")
    p.add_argument(
        "--counterparty",
        action="append",
        help=(
            "Counterparty spec: TICKER:Name:relationship[:strength[:aliases,csv]]. "
            "Repeatable. Example: FRC:First Republic Bank:peer:0.6:First Republic"
        ),
    )
    p.add_argument(
        "--window",
        default=_default_window(),
        help="Analysis window START:END (ISO dates). Defaults to the last 90 days.",
    )
    p.add_argument("--fixture-jsonl", help="Load observations from a JSONL fixture instead of GDELT.")
    p.add_argument("--live", action="store_true", help="Pull live observations from GDELT DOC 2.0.")
    p.add_argument("--max-records", type=int, default=100, help="Max GDELT records per target in --live mode.")
    p.add_argument("--top-evidence-n", type=int, default=8, help="Cap for the top-evidence section.")
    p.add_argument("--out", required=True, help="Output HTML path.")
    args = p.parse_args()

    if args.fixture_jsonl and args.live:
        print("ERROR: --fixture-jsonl and --live are mutually exclusive", file=sys.stderr)
        return 2
    return build(args)


if __name__ == "__main__":
    raise SystemExit(main())
