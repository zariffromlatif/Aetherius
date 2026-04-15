import asyncio
from datetime import datetime, timezone

from app.db.session import SessionLocal
from app.services.ingestion.service import ingest_observation
from sensory_core import run_sensory_core


async def run_crawl_and_store() -> dict:
    await run_sensory_core()
    with open("market_state.md", "r", encoding="utf-8") as f:
        raw_text = f.read()
    db = SessionLocal()
    try:
        row = ingest_observation(
            db=db,
            source_type="crawl4ai",
            source_name="sensory_core",
            source_url="https://news.ycombinator.com",
            title="crawler snapshot",
            raw_text=raw_text,
            observed_at=datetime.now(timezone.utc),
            dedupe_key="sensory_core_market_state",
        )
        return {"stored": row is not None}
    finally:
        db.close()


def run_crawl_and_store_sync() -> dict:
    return asyncio.run(run_crawl_and_store())
