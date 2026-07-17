"""
RHOS MongoDB Seed Script.

Loads generated synthetic CSV datasets and seeds them into MongoDB collections
using efficient upserts.
"""

from __future__ import annotations

import csv
import os
import sys

# Add backend directory to path to import app config
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend"))

from app.config import get_settings
from pymongo import MongoClient, ReplaceOne

DATASETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "datasets")

# Collections mapping CSV to MongoDB
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

    print(f"Seeding {len(records)} records from {csv_name} to MongoDB collection '{collection_name}'...")
    # Clear the collection to ensure only cleaned/filtered records exist
    db[collection_name].delete_many({})

    operations = []
    for record in records:
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
        # Map ID to _id for MongoDB compatibility
        doc_data["_id"] = doc_id

        # Use ReplaceOne with upsert=True to support idempotent seeding
        operations.append(ReplaceOne({"_id": doc_id}, doc_data, upsert=True))

    if operations:
        # Perform bulk write for efficiency
        result = db[collection_name].bulk_write(operations)
        print(f"Completed seeding '{collection_name}'. Matched: {result.matched_count}, Upserted: {result.upserted_count}, Modified: {result.modified_count}")


def main():
    settings = get_settings()
    uri = settings.mongodb_uri

    if not uri:
        print("Error: MONGODB_URI is not set in .env. Please configure your .env file.")
        sys.exit(1)

    if "<db_password>" in uri:
        print("Error: MONGODB_URI contains '<db_password>' placeholder. Please replace it with your actual password in .env before seeding.")
        sys.exit(1)

    print("Connecting to MongoDB...")
    try:
        client = MongoClient(uri)
        db = client[settings.mongodb_db_name]
        # Force a connection test
        client.admin.command('ping')
        print("Connected to MongoDB successfully. Starting seed process...")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        sys.exit(1)

    for csv_name, collection_name in COLLECTIONS.items():
        try:
            seed_collection(db, csv_name, collection_name)
        except Exception as e:
            print(f"Failed to seed {csv_name}: {e}")

    # Seed demo users into MongoDB users collection
    print("Seeding demo users into 'users' collection...")
    try:
        from app.core.security import hash_password
        demo_users = [
            {
                "_id": "demo-doctor-001",
                "email": "doctor@rhos.in",
                "name": "Dr. Priya Sharma",
                "role": "doctor",
                "phone": "+91-9876543210",
                "hospital_name": "PHC Khandela",
                "hashed_password": hash_password("doctor123"),
            },
            {
                "_id": "demo-nurse-001",
                "email": "nurse@rhos.in",
                "name": "Nurse Anita Devi",
                "role": "nurse",
                "phone": "+91-9876543211",
                "hospital_name": "PHC Khandela",
                "hashed_password": hash_password("nurse123"),
            },
            {
                "_id": "demo-admin-001",
                "email": "admin@rhos.in",
                "name": "Admin Rajesh Kumar",
                "role": "admin",
                "phone": "+91-9876543212",
                "hospital_name": "District Hospital Sikar",
                "hashed_password": hash_password("admin123"),
            },
            {
                "_id": "demo-patient-001",
                "email": "patient@rhos.in",
                "name": "Dinesh Sharma",
                "role": "patient",
                "phone": "+91-925769943",
                "hospital_name": "PHC Khandela",
                "patient_id": "P001",
                "hashed_password": hash_password("patient123"),
            }
        ]
        
        user_ops = [ReplaceOne({"_id": u["_id"]}, u, upsert=True) for u in demo_users]
        user_result = db["users"].bulk_write(user_ops)
        print(f"Completed seeding 'users'. Matched: {user_result.matched_count}, Upserted: {user_result.upserted_count}")
    except Exception as e:
        print(f"Failed to seed demo users: {e}")

    print("Database seeding completed.")


if __name__ == "__main__":
    main()
