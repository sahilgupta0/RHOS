"""
RHOS Synthetic Dataset Generator.

Generates 12 CSV files containing realistic synthetic Indian rural healthcare data.
"""

from __future__ import annotations

import csv
import os
import random
from datetime import date, datetime, timedelta

DATASETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "datasets")

# Indian names & locations for realism
FIRST_NAMES_MALE = ["Ramesh", "Suresh", "Rajesh", "Mohan", "Raju", "Amit", "Vijay", "Sanjay", "Anil", "Sunil", "Vikram", "Dinesh", "Karan", "Hari", "Gopal", "Ram", "Shyam", "Arjun", "Ajay", "Rahul"]
FIRST_NAMES_FEMALE = ["Sunita", "Anita", "Geeta", "Sita", "Radha", "Priya", "Pooja", "Rekha", "Maya", "Kiran", "Pinky", "Meena", "Asha", "Lata", "Kamla", "Sarla", "Durga", "Parvati", "Rani", "Jyoti"]
LAST_NAMES = ["Kumar", "Singh", "Lal", "Sharma", "Verma", "Jat", "Meena", "Gupta", "Yadav", "Choudhary", "Sharma", "Sharma", "Prasad", "Saini", "Gurjar", "Bunkar"]

VILLAGES = [
    {"id": "V001", "name": "Khandela", "population": 8500, "lat": 27.6087, "lng": 75.5009, "distance": 4.2},
    {"id": "V002", "name": "Ringus", "population": 12000, "lat": 27.3533, "lng": 75.5683, "distance": 12.8},
    {"id": "V003", "name": "Neem Ka Thana", "population": 15000, "lat": 27.7397, "lng": 75.7876, "distance": 22.5},
    {"id": "V004", "name": "Sri Madhopur", "population": 9800, "lat": 27.4719, "lng": 75.5975, "distance": 8.0},
    {"id": "V005", "name": "Chomu", "population": 25000, "lat": 27.1672, "lng": 75.7208, "distance": 28.0},
    {"id": "V006", "name": "Phulera", "population": 14000, "lat": 26.8775, "lng": 75.2411, "distance": 32.5},
]

ASHA_WORKERS = [
    {"id": "AW001", "name": "Sarla Devi", "village_id": "V001", "phone": "+91-9988776601"},
    {"id": "AW002", "name": "Kamlesh Bai", "village_id": "V001", "phone": "+91-9988776602"},
    {"id": "AW003", "name": "Santosh Kanwar", "village_id": "V002", "phone": "+91-9988776603"},
    {"id": "AW004", "name": "Suman Sharma", "village_id": "V003", "phone": "+91-9988776604"},
    {"id": "AW005", "name": "Rajbala Jat", "village_id": "V004", "phone": "+91-9988776605"},
    {"id": "AW006", "name": "Meera Gurjar", "village_id": "V005", "phone": "+91-9988776606"},
]

HOSPITALS = [
    {"id": "H001", "name": "Khandela PHC", "type": "PHC", "district": "Sikar", "beds": 10, "lat": 27.6080, "lng": 75.5015},
    {"id": "H002", "name": "Ringus CHC", "type": "CHC", "district": "Sikar", "beds": 30, "lat": 27.3525, "lng": 75.5690},
    {"id": "H003", "name": "Sikar District Hospital", "type": "District Hospital", "district": "Sikar", "beds": 250, "lat": 27.6120, "lng": 75.1390},
]

DISEASES = [
    "Hypertension", "Type 2 Diabetes", "Acute Respiratory Infection", "Malaria", 
    "Dengue Fever", "Tuberculosis", "Anemia", "Gastroenteritis", "Pneumonia", "Skin Infection"
]

SYMPTOMS_DB = [
    {"name": "Fever", "category": "General", "severity_range": "Mild-Severe"},
    {"name": "Cough", "category": "Respiratory", "severity_range": "Mild-Moderate"},
    {"name": "Shortness of Breath", "category": "Respiratory", "severity_range": "Moderate-Severe"},
    {"name": "Chest Pain", "category": "Cardiovascular", "severity_range": "Severe"},
    {"name": "Abdominal Pain", "category": "Gastrointestinal", "severity_range": "Mild-Severe"},
    {"name": "Diarrhea", "category": "Gastrointestinal", "severity_range": "Mild-Moderate"},
    {"name": "Vomiting", "category": "Gastrointestinal", "severity_range": "Mild-Moderate"},
    {"name": "Headache", "category": "Neurological", "severity_range": "Mild-Moderate"},
    {"name": "Joint Pain", "category": "Musculoskeletal", "severity_range": "Mild-Moderate"},
    {"name": "Skin Rash", "category": "Dermatological", "severity_range": "Mild-Moderate"},
]

MEDICINES_DB = [
    {"name": "Paracetamol", "generic_name": "Paracetamol", "category": "Analgesic/Antipyretic", "interactions": "Alcohol, Warfarin"},
    {"name": "Metformin", "generic_name": "Metformin", "category": "Antidiabetic", "interactions": "Contrast dye, Alcohol"},
    {"name": "Amlodipine", "generic_name": "Amlodipine", "category": "Antihypertensive", "interactions": "NSAIDs, Beta-blockers"},
    {"name": "Amoxicillin", "generic_name": "Amoxicillin", "category": "Antibiotic", "interactions": "Oral contraceptives, Methotrexate"},
    {"name": "Omeprazole", "generic_name": "Omeprazole", "category": "Proton Pump Inhibitor", "interactions": "Clopidogrel, Ketoconazole"},
    {"name": "Atorvastatin", "generic_name": "Atorvastatin", "category": "Lipid-lowering", "interactions": "Grapefruit juice, Cyclosporine"},
    {"name": "Losartan", "generic_name": "Losartan", "category": "Antihypertensive", "interactions": "NSAIDs, Potassium supplements"},
    {"name": "Cetirizine", "generic_name": "Cetirizine", "category": "Antihistamine", "interactions": "Alcohol, CNS depressants"},
]

ALLERGENS = ["Penicillin", "Sulfa drugs", "Aspirin", "Ibuprofen", "Peanuts", "Dust", "Pollen"]


def ensure_dir():
    os.makedirs(DATASETS_DIR, exist_ok=True)


def generate_patients(n=300):
    ensure_dir()
    filepath = os.path.join(DATASETS_DIR, "patients.csv")
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "age", "gender", "blood_group", "village_id", "asha_worker_id", "phone", "aadhaar", "is_active"])
        for i in range(1, n + 1):
            gender = random.choice(["Male", "Female"])
            first = random.choice(FIRST_NAMES_MALE) if gender == "Male" else random.choice(FIRST_NAMES_FEMALE)
            last = random.choice(LAST_NAMES)
            name = f"{first} {last}"
            age = random.randint(1, 85)
            bg = random.choice(["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
            village = random.choice(VILLAGES)
            asha = [a for a in ASHA_WORKERS if a["village_id"] == village["id"]]
            asha_id = random.choice(asha)["id"] if asha else ""
            phone = f"+91-9{random.randint(10000000, 99999999)}"
            aadhaar = f"XXXX-XXXX-{random.randint(1000, 9999)}"
            writer.writerow([f"P{i:03d}", name, age, gender, bg, village["id"], asha_id, phone, aadhaar, "True"])
    print(f"Generated {filepath}")


def generate_medical_history(n=400):
    filepath = os.path.join(DATASETS_DIR, "medical_history.csv")
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "patient_id", "condition", "diagnosed_date", "status", "notes"])
        for i in range(1, n + 1):
            patient_id = f"P{random.randint(1, 300):03d}"
            condition = random.choice(DISEASES)
            diag_date = date.today() - timedelta(days=random.randint(30, 2000))
            status = random.choice(["active", "resolved", "chronic", "managed"])
            writer.writerow([f"MH{i:03d}", patient_id, condition, diag_date.isoformat(), status, "Managed at local PHC"])
    print(f"Generated {filepath}")


def generate_visits(n=500):
    filepath = os.path.join(DATASETS_DIR, "visits.csv")
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "patient_id", "date", "type", "chief_complaint", "doctor_id"])
        for i in range(1, n + 1):
            patient_id = f"P{random.randint(1, 300):03d}"
            visit_date = datetime.now() - timedelta(days=random.randint(0, 365), hours=random.randint(0, 23))
            visit_type = random.choice(["walk-in", "appointment", "follow-up", "emergency"])
            complaint = f"Complaining of {random.choice(SYMPTOMS_DB)['name'].lower()}"
            writer.writerow([f"V{i:03d}", patient_id, visit_date.isoformat(), visit_type, complaint, "demo-doctor-001"])
    print(f"Generated {filepath}")


def generate_vitals(n=500):
    filepath = os.path.join(DATASETS_DIR, "vitals.csv")
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "patient_id", "visit_id", "recorded_at", "bp_systolic", "bp_diastolic", "heart_rate", "temperature", "spo2", "weight"])
        for i in range(1, n + 1):
            patient_id = f"P{random.randint(1, 300):03d}"
            visit_id = f"V{i:03d}"
            recorded_at = datetime.now() - timedelta(days=random.randint(0, 365))
            sys = random.randint(100, 160)
            dia = random.randint(60, 100)
            hr = random.randint(60, 110)
            temp = round(random.uniform(36.2, 39.5), 1)
            spo2 = random.randint(90, 100)
            weight = round(random.uniform(40.0, 90.0), 1)
            writer.writerow([f"VT{i:03d}", patient_id, visit_id, recorded_at.isoformat(), sys, dia, hr, temp, spo2, weight])
    print(f"Generated {filepath}")


def generate_medicines(n=200):
    filepath = os.path.join(DATASETS_DIR, "medicines.csv")
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "generic_name", "category", "dosage_forms", "contraindications", "interactions"])
        for i in range(1, n + 1):
            ref = MEDICINES_DB[i % len(MEDICINES_DB)]
            name = f"{ref['name']} {random.choice(['100mg', '500mg', '5mg', '10mg'])}"
            writer.writerow([f"M{i:03d}", name, ref["generic_name"], ref["category"], "Tablet", "None", ref["interactions"]])
    print(f"Generated {filepath}")


def generate_allergies(n=250):
    filepath = os.path.join(DATASETS_DIR, "allergies.csv")
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "patient_id", "allergen", "severity", "reaction", "noted_date"])
        for i in range(1, n + 1):
            patient_id = f"P{random.randint(1, 300):03d}"
            allergen = random.choice(ALLERGENS)
            severity = random.choice(["mild", "moderate", "severe"])
            reaction = random.choice(["Skin rash", "Itching", "Swelling", "Anaphylaxis", "Shortness of breath"])
            noted_date = date.today() - timedelta(days=random.randint(100, 3000))
            writer.writerow([f"A{i:03d}", patient_id, allergen, severity, reaction, noted_date.isoformat()])
    print(f"Generated {filepath}")


def generate_hospitals():
    filepath = os.path.join(DATASETS_DIR, "hospitals.csv")
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "type", "district", "beds", "specialties", "lat", "lng"])
        for h in HOSPITALS:
            writer.writerow([h["id"], h["name"], h["type"], h["district"], h["beds"], "General Medicine", h["lat"], h["lng"]])
    print(f"Generated {filepath}")


def generate_asha_workers():
    filepath = os.path.join(DATASETS_DIR, "asha_workers.csv")
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "village_id", "phone", "patients_assigned", "active_since"])
        for a in ASHA_WORKERS:
            writer.writerow([a["id"], a["name"], a["village_id"], a["phone"], random.randint(30, 80), "2018-05-15"])
    print(f"Generated {filepath}")


def generate_villages():
    filepath = os.path.join(DATASETS_DIR, "villages.csv")
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "district", "state", "population", "nearest_hospital_id", "lat", "lng"])
        for v in VILLAGES:
            writer.writerow([v["id"], v["name"], "Sikar", "Rajasthan", v["population"], "H001", v["lat"], v["lng"]])
    print(f"Generated {filepath}")


def generate_appointments(n=400):
    filepath = os.path.join(DATASETS_DIR, "appointments.csv")
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "patient_id", "doctor_id", "date", "time", "status", "type"])
        for i in range(1, n + 1):
            patient_id = f"P{random.randint(1, 300):03d}"
            app_date = date.today() + timedelta(days=random.randint(-15, 30))
            app_time = f"{random.randint(9, 15):02d}:{random.choice([0, 15, 30, 45]):02d}"
            status = random.choice(["scheduled", "completed", "cancelled", "no-show"])
            writer.writerow([f"AP{i:03d}", patient_id, "demo-doctor-001", app_date.isoformat(), app_time, status, "General Checkup"])
    print(f"Generated {filepath}")


def generate_referrals(n=200):
    filepath = os.path.join(DATASETS_DIR, "referrals.csv")
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "patient_id", "from_hospital", "to_hospital", "reason", "urgency", "date"])
        for i in range(1, n + 1):
            patient_id = f"P{random.randint(1, 300):03d}"
            urgency = random.choice(["routine", "urgent", "emergency"])
            ref_date = date.today() - timedelta(days=random.randint(0, 180))
            writer.writerow([f"R{i:03d}", patient_id, "Khandela PHC", "Sikar District Hospital", "Specialist evaluation required", urgency, ref_date.isoformat()])
    print(f"Generated {filepath}")


def generate_symptoms():
    filepath = os.path.join(DATASETS_DIR, "symptoms.csv")
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "category", "body_system", "severity_range", "common_conditions"])
        for i, s in enumerate(SYMPTOMS_DB, 1):
            writer.writerow([f"S{i:03d}", s["name"], s["category"], s["category"], s["severity_range"], "Various"])
    print(f"Generated {filepath}")


def main():
    generate_patients()
    generate_medical_history()
    generate_visits()
    generate_vitals()
    generate_medicines()
    generate_allergies()
    generate_hospitals()
    generate_asha_workers()
    generate_villages()
    generate_appointments()
    generate_referrals()
    generate_symptoms()


if __name__ == "__main__":
    main()
