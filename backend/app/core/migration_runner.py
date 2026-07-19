from __future__ import annotations

import importlib
import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from app.core.mongodb import get_mongodb_db

logger = logging.getLogger(__name__)

MIGRATION_FILE_PATTERN = re.compile(r"^(\d{4})_.*\.py$")


class MigrationRunner:
    """Versioned MongoDB migration runner executing upgrade and downgrade operations."""

    def __init__(self, migrations_dir: Path | None = None):
        if migrations_dir is None:
            self.migrations_dir = Path(__file__).parent.parent / "migrations"
        else:
            self.migrations_dir = migrations_dir

    def _discover_migrations(self) -> list[tuple[str, str]]:
        """Discover migration files in migrations directory, returning sorted list of (version_str, filename)."""
        if not os.path.exists(self.migrations_dir):
            return []

        discovered = []
        for filename in os.listdir(self.migrations_dir):
            match = MIGRATION_FILE_PATTERN.match(filename)
            if match:
                version = match.group(1)
                discovered.append((version, filename))

        # Sort migrations sequentially by version prefix
        discovered.sort(key=lambda x: x[0])
        return discovered

    def _load_migration_module(self, filename: str) -> Any:
        """Dynamically import the migration script module."""
        module_name = f"app.migrations.{filename[:-3]}"
        return importlib.import_module(module_name)

    async def run_upgrades(self) -> list[str]:
        """Apply all pending migrations. Returns list of applied version strings."""
        db = get_mongodb_db()
        if db is None:
            logger.warning(
                "MongoDB is not initialized. Skipping index/schema migrations."
            )
            return []

        applied = []
        discovered = self._discover_migrations()
        if not discovered:
            logger.info("No migrations found in %s", self.migrations_dir)
            return []

        # Ensure history collection exists
        history_col = db["migration_history"]

        for version, filename in discovered:
            # Check if already applied
            existing = await history_col.find_one({"_id": version})
            if existing:
                continue

            logger.info("Applying schema migration %s (%s)...", version, filename)
            try:
                module = self._load_migration_module(filename)
                if hasattr(module, "upgrade"):
                    await module.upgrade(db)

                # Record successful application
                await history_col.insert_one(
                    {
                        "_id": version,
                        "filename": filename,
                        "applied_at": datetime.utcnow().isoformat(),
                    }
                )
                applied.append(version)
                logger.info("Successfully applied schema migration %s", version)
            except Exception as e:
                logger.error("Failed applying schema migration %s: %s", version, e)
                raise RuntimeError(f"Migration {version} failed: {e}") from e

        if not applied:
            logger.info("Database schema is up-to-date. No pending migrations.")
        return applied

    async def rollback_latest(self) -> str | None:
        """Rollback/downgrade the last applied migration. Returns rolled back version or None."""
        db = get_mongodb_db()
        if db is None:
            logger.warning("MongoDB is not initialized. Cannot perform rollback.")
            return None

        history_col = db["migration_history"]

        # Find the latest applied migration in history
        cursor = history_col.find({}).sort("_id", -1).limit(1)
        latest_doc = None
        async for doc in cursor:
            latest_doc = doc
            break

        if not latest_doc:
            logger.info("No applied migrations found to rollback.")
            return None

        version = latest_doc["_id"]
        filename = latest_doc["filename"]

        logger.info("Rolling back schema migration %s (%s)...", version, filename)
        try:
            module = self._load_migration_module(filename)
            if hasattr(module, "downgrade"):
                await module.downgrade(db)

            # Remove from history
            await history_col.delete_one({"_id": version})
            logger.info("Successfully rolled back schema migration %s", version)
            return version
        except Exception as e:
            logger.error("Failed rolling back schema migration %s: %s", version, e)
            raise RuntimeError(f"Rollback of migration {version} failed: {e}") from e


migration_runner = MigrationRunner()
