"""
API key authentication.
"""

import logging
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader, APIKeyQuery

from app.core.config import settings

logger = logging.getLogger(__name__)

# FastAPI security schemes — both header and query are accepted
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
api_key_query = APIKeyQuery(name="api_key", auto_error=False)


async def get_api_key(
    header_key: str = Security(api_key_header),
    query_key: str = Security(api_key_query),
) -> str:

    key = header_key or query_key

    if not key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "Missing API key",
                "message": (
                    "Provide your API key via the 'X-API-Key' header "
                    "or the 'api_key' query parameter."
                ),
                "hint": "Use 'demo-key-12345' for quick testing.",
            },
        )

    if key not in settings.API_KEYS:
        logger.warning(f"Invalid API key attempt: {key[:8]}...")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Invalid API key",
                "message": "The provided API key is not recognized.",
            },
        )

    return key
