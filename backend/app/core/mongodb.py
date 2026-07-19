"""
RHOS MongoDB Initialization.

Singleton initialization of Motor MongoDB client.
"""

from __future__ import annotations

import logging

from motor.motor_asyncio import AsyncIOMotorClient

from app.config import get_settings

logger = logging.getLogger(__name__)

_mongo_client: AsyncIOMotorClient | None = None
_mongo_db = None


def init_mongodb() -> None:
    """Initialize Async MongoDB client. Safe to call multiple times."""
    global _mongo_client, _mongo_db

    if _mongo_client is not None:
        return

    settings = get_settings()
    uri = settings.mongodb_uri

    if not uri:
        logger.warning(
            "MONGODB_URI is not set in .env. "
            "MongoDB features will be unavailable. "
            "Set MONGODB_URI in .env to enable."
        )
        return

    if "<db_password>" in uri:
        logger.warning(
            "MONGODB_URI contains '<db_password>' placeholder. "
            "Please update the password in .env to connect to MongoDB."
        )

    try:
        # Connect to MongoDB using Motor
        _mongo_client = AsyncIOMotorClient(uri)
        _mongo_db = _mongo_client[settings.mongodb_db_name]
        logger.info(
            "MongoDB Async client initialized successfully (Database: %s).",
            settings.mongodb_db_name,
        )
    except Exception as e:
        logger.error("Failed to initialize MongoDB: %s", e)


def get_mongodb_client() -> AsyncIOMotorClient | None:
    """Get the MongoDB client instance."""
    return _mongo_client


def get_mongodb_db():
    """Get the MongoDB database instance."""
    if _mongo_db is None:
        init_mongodb()
    return _mongo_db


def close_mongodb() -> None:
    """Close the MongoDB client connection."""
    global _mongo_client, _mongo_db
    if _mongo_client is not None:
        _mongo_client.close()
        logger.info("MongoDB client connection closed.")
        _mongo_client = None
        _mongo_db = None
