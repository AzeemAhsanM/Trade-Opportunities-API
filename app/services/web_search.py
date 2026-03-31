"""
Web search service — gathers current market data for a sector.
"""

import asyncio
import logging
import re
from typing import List

import httpx

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "TradeOpportunitiesApp/1.0 (contact: azeem@gmail.com)",
    "Accept": "application/json",
}


async def _wikipedia_summary(topic: str) -> str:
    clean = topic.strip().replace(" ", "_")
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{clean}"

    try:
        async with httpx.AsyncClient(headers=HEADERS, timeout=10.0) as client:
            r = await client.get(url)

            if r.status_code == 200:
                data = r.json()
                extract = data.get("extract", "")
                if extract:
                    return extract[:300]

    except Exception as exc:
        logger.warning(f"Wikipedia failed: {topic} → {exc}")

    return ""


async def fetch_sector_data(sector: str) -> dict:
    queries = [
        f"{sector}_industry_in_India",
        f"{sector}_in_India",
        f"India_{sector}",
    ]

    tasks = [_wikipedia_summary(q) for q in queries]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    snippets: List[str] = []

    for r in results:
        if isinstance(r, str) and r:
            snippets.append(r)

    # Always add curated fallback
    snippets.extend(_curated_context(sector))

    # Deduplicate + LIMIT
    seen = set()
    final = []

    for s in snippets:
        key = s[:80]
        if key not in seen:
            seen.add(key)
            final.append(s)

    final = final[:6]

    logger.info(f"Collected {len(final)} snippets for '{sector}'")

    return {
        "snippets": final,
        "sources": ["Wikipedia + Curated"]
    }


def _curated_context(sector: str) -> List[str]:
    return [
        f"India's {sector} sector is growing due to government support and global demand.",
        f"Production Linked Incentive (PLI) schemes boost {sector} manufacturing.",
        f"India exports {sector} products to US, EU, and ASEAN markets.",
        f"Growing domestic consumption is driving expansion in {sector}.",
        f"Digital infrastructure is improving supply chains in {sector}.",
    ]