"""
Simple in-memory TTL cache.
"""

import time
import logging
from typing import Any, Dict, Optional, Tuple

from app.core.config import settings

logger = logging.getLogger(__name__)

# cache store
_store: Dict[str, Tuple[Any, float]] = {}


def _make_key(sector: str) -> str:
    return f"analysis:{sector.lower().strip()}"


def get(sector: str) -> Optional[Any]:
    key = _make_key(sector)
    entry = _store.get(key)

    if entry is None:
        logger.debug(f"Cache miss for sector '{sector}'")
        return None
    value, expiry = entry
    if time.time() > expiry:
        del _store[key]
        logger.debug(f"Cache expired for key '{key}'")
        return None
    logger.info(f"Cache hit for sector '{sector}'")
    return value


def set(sector: str, value: Any) -> None:
    key = _make_key(sector)
    expiry = time.time() + settings.CACHE_TTL_SECONDS
    _store[key] = (value, expiry)
    logger.info(
        f"Cached analysis for sector '{sector}' "
        f"(TTL: {settings.CACHE_TTL_SECONDS}s)"
    )


def invalidate(sector: str) -> bool:
    key = _make_key(sector)
    if key in _store:
        del _store[key]
        return True
    return False


def stats() -> dict:
    now = time.time()
    active = {k: v for k, v in _store.items() if v[1] > now}
    return {
        "total_entries": len(_store),
        "active_entries": len(active),
        "ttl_seconds": settings.CACHE_TTL_SECONDS,
        "cached_sectors": [k.replace("analysis:", "") for k in active],
    }
