"""
RHOS Error Handler Middleware.

Global exception handlers for consistent error responses.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


def setup_error_handlers(app: FastAPI) -> None:
    """Register global exception handlers."""

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": str(exc.detail),
                "status_code": exc.status_code,
                "error_type": "http_error",
            },
        )

    @app.exception_handler(ConnectionError)
    async def connection_error_handler(request: Request, exc: ConnectionError):
        logger.error("Connection error: %s", exc)
        return JSONResponse(
            status_code=503,
            content={
                "detail": "Service temporarily unavailable. Please try again later.",
                "status_code": 503,
                "error_type": "connection_error",
            },
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        return JSONResponse(
            status_code=422,
            content={
                "detail": str(exc),
                "status_code": 422,
                "error_type": "validation_error",
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error("Unhandled exception: %s", exc, exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "An internal server error occurred.",
                "status_code": 500,
                "error_type": "internal_error",
            },
        )
