import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode

async def run_sensory_core():
    # 1. Finalized Configuration for Phase 2
    config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        magic=True,                # Activates stealth and pattern-learning
        flatten_shadow_dom=True,   # Unlocks hidden pricing/product data
        # FIX: Change 'wait_for' to 'wait_until' for page states
        wait_until="networkidle",  
        page_timeout=30000         # Reduce to 30s for faster testing
    )

    # 2. Initialize the Crawler
    async with AsyncWebCrawler() as crawler:
        # Test with a simple URL first to ensure connectivity
        target_url = "https://news.ycombinator.com"
        
        print(f"--- Sensory Capture: Accessing {target_url} ---")
        
        # 3. Execute the crawl
        result = await crawler.arun(url=target_url, config=config)

        if result.success:
            with open("market_state.md", "w", encoding="utf-8") as f:
                f.write(result.markdown)
            print("Successfully captured Market State.")
        else:
            print(f"Sensory Failure: {result.error_message}")
            # If Proxy direct failed persists, try setting magic=False for one run
            # to verify your local internet connection is reaching the site.

if __name__ == "__main__":
    asyncio.run(run_sensory_core())