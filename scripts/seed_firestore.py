"""
RHOS Firestore Seed Script.

Loads generated synthetic CSV datasets and seeds them into Firestore collections
using efficient batch writes.
"""

from __future__ import annotations

import csv
import os
import sys

# Add backend directory to path to import app config and init
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend"))

from app.config import get_settings
from app.core.firebase_init import init_firebase, get_firestore_client

DATASETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "datasets")

# Collections mapping CSV to Firestore
COLLECTIONS = {
    "patients.csv": "patients",
    "medical_history.csv": "medical_history",
    "visits.csv": "visits",
    "vitals.csv": "vitals",
    "medicines.csv": "medicines",
    "allergies.csv": "allergies",
    "hospitals.csv": "hospitals",
    "asha_workers.csv": "asha_workers",
    "villages.csv": "villages",
    "appointments.csv": "appointments",
    "referrals.csv": "referrals",
    "symptoms.csv": "symptoms",
}


def read_csv(filename: str) -> list[dict]:
    filepath = os.path.join(DATASETS_DIR, filename)
    if not os.path.exists(filepath):
        print(f"Error: Dataset {filename} not found at {filepath}")
        return []

    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def seed_collection(db, csv_name: str, collection_name: str):
    records = read_csv(csv_name)
    if not records:
        return

    print(f"Seeding {len(records)} records from {csv_name} to Firestore collection '{collection_name}'...")

    batch = db.batch()
    count = 0
    batch_size = 400  # Firestore batch limit is 500

    for record in records:
        # Convert numeric types
        doc_data = {}
        for key, value in record.items():
            if key == "id":
                continue

            # Try to convert values to appropriate type
            if value.lower() == "true":
                doc_data[key] = True
            elif value.lower() == "false":
                doc_data[key] = False
            else:
                try:
                    if "." in value:
                        doc_data[key] = float(value)
                    else:
                        doc_data[key] = int(value)
                except ValueError:
                    doc_data[key] = value

        doc_id = record.get("id")
        doc_ref = db.collection(collection_name).document(doc_id)
        batch.set(doc_ref, doc_data)
        count += 1

        if count >= batch_size:
            batch.commit()
            print(f"Committed batch of {count} documents to '{collection_name}'...")
            batch = db.batch()
            count = 0

    # Commit any remaining documents
    if count > 0:
        batch.commit()
        print(f"Committed remaining {count} documents to '{collection_name}'.")


def main():
    # Set default env path if not set
    os.environ.setdefault("FIREBASE_CREDENTIALS", "./firebase-service-account.json")

    settings = get_settings()
    init_firebase()

    db = get_firestore_client()
    if db is None:
        print("Error: Could not connect to Firestore. Verify FIREBASE_CREDENTIALS in .env or the service account file path.")
        sys.exit(1)

    print("Firebase connected successfully. Starting seed process...")

    for csv_name, collection_name in COLLECTIONS.items():
        try:
            seed_collection(db, csv_name, collection_name)
        except Exception as e:
            print(f"Failed to seed {csv_name}: {e}")

    print("Database seeding completed.")


if __name__ == "__main__":
    main()
