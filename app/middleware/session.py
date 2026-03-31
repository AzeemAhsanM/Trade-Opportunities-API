"""
in-memory session management.
"""

import time
import uuid
import logging
from typing import Any, Dict, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

_sessions: Dict[str, Dict[str, Any]] = {}

SESSION_TTL_SECONDS = 3600 


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    return _sessions.get(session_id)


def get_all_sessions() -> Dict[str, Dict[str, Any]]:
    return dict(_sessions)


class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        session_id = request.headers.get("X-Session-ID") or str(uuid.uuid4())

        now = time.time()

        if session_id not in _sessions:
            _sessions[session_id] = {
                "session_id": session_id,
                "first_seen": now,
                "last_seen": now,
                "request_count": 0,
                "api_key": (
                    request.headers.get("X-API-Key")
                    or request.query_params.get("api_key")
                    or "anonymous"
                ),
                "sectors_analyzed": [],
            }
        else:
            # Evict if TTL has expired, then recreate
            session = _sessions[session_id]
            if now - session["last_seen"] > SESSION_TTL_SECONDS:
                del _sessions[session_id]
                _sessions[session_id] = {
                    "session_id": session_id,
                    "first_seen": now,
                    "last_seen": now,
                    "request_count": 0,
                    "api_key": (
                        request.headers.get("X-API-Key")
                        or request.query_params.get("api_key")
                        or "anonymous"
                    ),
                    "sectors_analyzed": [],
                }

        _sessions[session_id]["last_seen"] = now
        _sessions[session_id]["request_count"] += 1

        # Inject session into request state so route handlers can access it
        request.state.session_id = session_id
        request.state.session = _sessions[session_id]

        response: Response = await call_next(request)
        response.headers["X-Session-ID"] = session_id
        return response
