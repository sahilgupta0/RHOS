#!/usr/bin/env python
"""
RHOS Schema Migration CLI Tool.

Enables manual migration upgrades and rollbacks.
Usage:
  python scripts/run_migrations.py up
  python scripts/run_migrations.py rollback
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.mongodb import init_mongodb, close_mongodb
from app.core.migration_runner import migration_runner

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("migration_cli")


async def main() -> None:
    parser = argparse.ArgumentParser(description="RHOS DB Migration Utility")
    parser.add_argument(
        "action",
        choices=["up", "rollback"],
        default="up",
        nargs="?",
        help="Migration action: 'up' (apply pending) or 'rollback' (revert latest)",
    )
    args = parser.parse_args()

    logger.info("Initializing MongoDB client...")
    init_mongodb()

    try:
        if args.action == "up":
            logger.info("Starting schema upgrades...")
            applied = await migration_runner.run_upgrades()
            if applied:
                logger.info("Applied migrations: %s", ", ".join(applied))
            else:
                logger.info("No migrations needed.")
        elif args.action == "rollback":
            logger.info("Starting schema rollback...")
            rolled_back = await migration_runner.rollback_latest()
            if rolled_back:
                logger.info("Rolled back migration: %s", rolled_back)
            else:
                logger.info("No migration to roll back.")
    except Exception as e:
        logger.error("Migration command failed: %s", e)
        sys.exit(1)
    finally:
        logger.info("Closing MongoDB connections...")
        close_mongodb()


if __name__ == "__main__":
    asyncio.run(main())
