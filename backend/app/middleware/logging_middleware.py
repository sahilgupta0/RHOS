"""
RHOS Logging Middleware.

Request/response logging for debugging and monitoring.
"""

from __future__ import annotations

import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that logs request/response details."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = str(uuid.uuid4())[:8]
        start_time = time.time()

        # Log request
        logger.info(
            "[%s] %s %s",
            request_id,
            request.method,
            request.url.path,
        )

        # Process request
        response = await call_next(request)

        # Log response
        duration = round((time.time() - start_time) * 1000, 2)
        logger.info(
            "[%s] %s %s → %s (%sms)",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            duration,
        )

        # Add request ID header
        response.headers["X-Request-ID"] = request_id
        return response
