from __future__ import annotations

import logging

from pymongo import ASCENDING, TEXT

logger = logging.getLogger(__name__)


async def upgrade(db) -> None:
    """Apply initial collection indexes."""
    logger.info("Running migration: 0001_initial_schema (upgrade)")

    # 1. Users email unique index
    try:
        await db["users"].create_index(
            [("email", ASCENDING)], unique=True, name="idx_users_email_unique"
        )
        logger.info("Created unique index on users.email")
    except Exception as e:
        logger.warning(
            "Could not create users.email index (it may already exist): %s", e
        )

    # 2. Patients name text search index
    try:
        await db["patients"].create_index(
            [("name", TEXT)], name="idx_patients_name_text"
        )
        logger.info("Created text index on patients.name")
    except Exception as e:
        logger.warning("Could not create patients.name index: %s", e)

    # 3. Consultations patient_id + created_at compound index
    try:
        await db["consultations"].create_index(
            [("patient_id", ASCENDING), ("created_at", ASCENDING)],
            name="idx_consultations_patient_created",
        )
        logger.info("Created compound index on consultations(patient_id, created_at)")
    except Exception as e:
        logger.warning("Could not create consultations index: %s", e)


async def downgrade(db) -> None:
    """Remove initial collection indexes."""
    logger.info("Running migration: 0001_initial_schema (downgrade)")

    try:
        await db["users"].drop_index("idx_users_email_unique")
        logger.info("Dropped users.email index")
    except Exception as e:
        logger.warning("Could not drop users.email index: %s", e)

    try:
        await db["patients"].drop_index("idx_patients_name_text")
        logger.info("Dropped patients.name index")
    except Exception as e:
        logger.warning("Could not drop patients.name index: %s", e)

    try:
        await db["consultations"].drop_index("idx_consultations_patient_created")
        logger.info("Dropped consultations index")
    except Exception as e:
        logger.warning("Could not drop consultations index: %s", e)
