"""
Sliding-window rate limiter
"""

import time
import logging
from collections import defaultdict, deque
from typing import Deque, Dict

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._buckets: Dict[str, Deque[float]] = defaultdict(deque)

    def _get_client_id(self, request: Request) -> str:
        api_key = request.headers.get("X-API-Key") or request.query_params.get("api_key")

        if api_key:
            return f"key:{api_key}"

        return f"ip:{request.client.host}"

    def _is_allowed(self, client_id: str):
        now = time.time()
        window = settings.RATE_LIMIT_WINDOW_SECONDS
        limit = settings.RATE_LIMIT_REQUESTS

        bucket = self._buckets[client_id]

        while bucket and bucket[0] <= now - window:
            bucket.popleft()

        if len(bucket) >= limit:
            retry_after = int(window - (now - bucket[0])) + 1
            return False, 0, retry_after

        bucket.append(now)
        remaining = limit - len(bucket)

        logger.info(f"{client_id} → remaining: {remaining}")

        return True, remaining, 0

    async def dispatch(self, request: Request, call_next):

        if request.url.path in ["/", "/docs", "/openapi.json"]:
            return await call_next(request)

        client_id = self._get_client_id(request)
        allowed, remaining, retry_after = self._is_allowed(client_id)

        if not allowed:
            logger.warning(f"Rate limit exceeded: {client_id}")

            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded"},
                headers={"Retry-After": str(retry_after)},
            )

        response: Response = await call_next(request)

        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response