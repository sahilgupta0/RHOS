"""
RHOS FastAPI Application.

Main application factory with middleware, routes, and lifespan events.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import get_settings
from app.core.firebase_init import init_firebase
from app.core.logging_config import setup_logging
from app.core.mongodb import close_mongodb, init_mongodb
from app.core.rate_limiter import limiter
from app.middleware.cors import setup_cors
from app.middleware.error_handler import setup_error_handlers
from app.middleware.logging_middleware import LoggingMiddleware

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    # Startup
    setup_logging()
    logger.info("Starting RHOS Backend...")

    settings = get_settings()
    logger.info("Auth mode: %s", settings.auth_mode)
    logger.info("Gemini configured: %s", settings.is_gemini_configured)

    # Initialize Firebase
    init_firebase()

    # Initialize MongoDB
    init_mongodb()

    # Apply database schema migrations automatically on startup
    from app.core.migration_runner import migration_runner

    try:
        logger.info("Applying pending database migrations on startup...")
        await migration_runner.run_upgrades()
    except Exception as e:
        logger.error("Failed to run database migrations on startup: %s", e)

    logger.info("RHOS Backend started successfully.")
    yield
    # Shutdown
    close_mongodb()
    logger.info("RHOS Backend shutting down.")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="RHOS — Rural Health Operating System",
        description=(
            "AI-powered Clinical Decision Support & Care Coordination System "
            "for Rural Primary Healthcare. This is a CDSS tool — not an AI doctor. "
            "All medical decisions are made by qualified healthcare professionals."
        ),
        version=settings.app_version,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Rate limiter
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Middleware
    setup_cors(app)
    app.add_middleware(LoggingMiddleware)

    # Error handlers
    setup_error_handlers(app)

    # Register routes
    _register_routes(app)

    return app


def _register_routes(app: FastAPI) -> None:
    """Register all API route modules."""
    from app.api import (
        analytics,
        auth,
        consultation,
        health,
        patient,
        prompts,
        speech,
        upload,
    )

    app.include_router(health.router, tags=["Health"])
    app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
    app.include_router(patient.router, tags=["Patients"])
    app.include_router(consultation.router, tags=["Consultation"])
    app.include_router(analytics.router, tags=["Analytics"])
    app.include_router(upload.router, tags=["Upload"])
    app.include_router(speech.router, tags=["Speech"])
    app.include_router(prompts.router, tags=["Prompts"])


# Create the application instance
app = create_app()
