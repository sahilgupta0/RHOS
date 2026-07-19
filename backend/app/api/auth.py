"""
RHOS Authentication Endpoints.

Login, register, and user profile.
Supports both Firebase Auth and local JWT modes.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status

from app.config import get_settings
from app.core.firebase_init import is_firebase_initialized
from app.core.mongodb import get_mongodb_db
from app.core.security import (create_access_token, hash_password,
                               verify_password)
from app.dependencies import CurrentUser
from app.schemas import (AuthResponse, LoginRequest, RegisterRequest,
                         UserResponse)

logger = logging.getLogger(__name__)

router = APIRouter()

# Demo users for local auth mode
DEMO_USERS = {
    "doctor@rhos.in": {
        "id": "demo-doctor-001",
        "email": "doctor@rhos.in",
        "name": "Dr. Priya Sharma",
        "role": "doctor",
        "phone": "+91-9876543210",
        "hospital_name": "PHC Khandela",
        "hashed_password": hash_password("doctor123"),
    },
    "nurse@rhos.in": {
        "id": "demo-nurse-001",
        "email": "nurse@rhos.in",
        "name": "Nurse Anita Devi",
        "role": "nurse",
        "phone": "+91-9876543211",
        "hospital_name": "PHC Khandela",
        "hashed_password": hash_password("nurse123"),
    },
    "admin@rhos.in": {
        "id": "demo-admin-001",
        "email": "admin@rhos.in",
        "name": "Admin Rajesh Kumar",
        "role": "admin",
        "phone": "+91-9876543212",
        "hospital_name": "District Hospital Sikar",
        "hashed_password": hash_password("admin123"),
    },
    "patient@rhos.in": {
        "id": "demo-patient-001",
        "email": "patient@rhos.in",
        "name": "Dinesh Sharma",
        "role": "patient",
        "phone": "+91-925769943",
        "hospital_name": "PHC Khandela",
        "patient_id": "P001",
        "hashed_password": hash_password("patient123"),
    },
}


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """
    Login with email/password.

    In 'local' mode, authenticates against demo users.
    In 'firebase' mode, verifies Firebase ID token.
    """
    settings = get_settings()

    if settings.auth_mode == "firebase" and is_firebase_initialized():
        return await _firebase_login(request)
    else:
        return await _local_login(request)


@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """Register a new user."""
    settings = get_settings()

    if settings.auth_mode == "firebase" and is_firebase_initialized():
        return await _firebase_register(request)
    else:
        return await _local_register(request)


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: CurrentUser):
    """Get the current authenticated user's profile."""
    return current_user


# ── Local Auth Implementation ──────────────────────────────────────────────────


async def _local_login(request: LoginRequest) -> AuthResponse:
    """Authenticate against local demo users in MongoDB."""
    db = get_mongodb_db()
    user = None
    if db is not None:
        user = await db["users"].find_one({"email": request.email})

    if not user:
        # Fallback to DEMO_USERS in-memory for initialization/fallback
        user = DEMO_USERS.get(request.email)
        if user and db is not None:
            # Sync user back to MongoDB
            db_user = user.copy()
            db_user["_id"] = db_user.pop("id", f"local-{uuid.uuid4().hex[:8]}")
            await db["users"].replace_one({"_id": db_user["_id"]}, db_user, upsert=True)

    if not user or not verify_password(request.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    user_id = user.get("id") or user.get("_id")
    token = create_access_token(
        {
            "sub": user_id,
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
            "patient_id": user.get("patient_id", ""),
        }
    )

    return AuthResponse(
        access_token=token,
        user=UserResponse(
            id=user_id,
            email=user["email"],
            name=user["name"],
            role=user["role"],
            phone=user.get("phone", ""),
            hospital_name=user.get("hospital_name", ""),
            patient_id=user.get("patient_id", ""),
        ),
    )


async def _local_register(request: RegisterRequest) -> AuthResponse:
    """Register a new user in local mode (adds to MongoDB and in-memory store)."""
    db = get_mongodb_db()
    if db is not None:
        existing = await db["users"].find_one({"email": request.email})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists.",
            )

    if request.email in DEMO_USERS:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists.",
        )

    user_id = f"local-{uuid.uuid4().hex[:8]}"
    role_str = request.role.value if hasattr(request.role, "value") else request.role
    patient_id = ""

    if role_str == "patient":
        patient_id = f"P{uuid.uuid4().hex[:6].upper()}"
        # Save a patient document in the patients collection in MongoDB
        if db is not None:
            await db["patients"].insert_one(
                {
                    "_id": patient_id,
                    "name": request.name,
                    "age": 30,  # Default age
                    "gender": "Male",  # Default gender
                    "phone": request.phone,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "is_active": True,
                }
            )

        # Append to CSV
        try:
            import csv
            import os

            settings = get_settings()
            csv_path = os.path.join(settings.datasets_path, "patients.csv")
            if os.path.exists(csv_path):
                with open(csv_path, "a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(
                        [
                            patient_id,
                            request.name,
                            30,
                            "Male",
                            "O+",
                            "V001",
                            "",
                            request.phone,
                            "",
                            "True",
                        ]
                    )
        except Exception as csv_err:
            logger.error("Error appending to patients.csv: %s", csv_err)

    new_user = {
        "id": user_id,
        "email": request.email,
        "name": request.name,
        "role": role_str,
        "phone": request.phone,
        "hospital_name": "",
        "patient_id": patient_id,
        "hashed_password": hash_password(request.password),
    }

    if db is not None:
        db_user = new_user.copy()
        db_user["_id"] = db_user.pop("id")
        await db["users"].insert_one(db_user)

    DEMO_USERS[request.email] = new_user

    token = create_access_token(
        {
            "sub": user_id,
            "email": request.email,
            "name": request.name,
            "role": new_user["role"],
            "patient_id": patient_id,
        }
    )

    return AuthResponse(
        access_token=token,
        user=UserResponse(
            id=user_id,
            email=request.email,
            name=request.name,
            role=request.role,
            phone=request.phone,
            patient_id=patient_id,
        ),
    )


# ── Firebase Auth Implementation ──────────────────────────────────────────────


async def _firebase_login(request: LoginRequest) -> AuthResponse:
    """Verify Firebase auth token (client sends ID token as password)."""
    try:
        from firebase_admin import auth as firebase_auth

        # In Firebase mode, the "password" field contains the Firebase ID token
        decoded = firebase_auth.verify_id_token(request.password)
        uid = decoded["uid"]

        # Get or create user in MongoDB
        db = get_mongodb_db()
        if db is not None:
            user_doc = await db["users"].find_one({"_id": uid})
            if user_doc:
                user_data = user_doc
                user_data["email"] = user_doc.get("email", "")
                user_data["name"] = user_doc.get("name", "User")
                user_data["role"] = user_doc.get("role", "doctor")
            else:
                user_data = {
                    "_id": uid,
                    "email": decoded.get("email", request.email),
                    "name": decoded.get("name", "User"),
                    "role": "doctor",
                    "firebase_uid": uid,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
                await db["users"].insert_one(user_data)
        else:
            user_data = {
                "email": decoded.get("email", ""),
                "name": decoded.get("name", "User"),
                "role": "doctor",
            }

        # Create our own JWT for API auth
        token = create_access_token(
            {
                "sub": uid,
                "email": user_data.get("email", ""),
                "name": user_data.get("name", "User"),
                "role": user_data.get("role", "doctor"),
            }
        )

        return AuthResponse(
            access_token=token,
            user=UserResponse(
                id=uid,
                email=user_data.get("email", ""),
                name=user_data.get("name", "User"),
                role=user_data.get("role", "doctor"),
            ),
        )
    except Exception as e:
        logger.error("Firebase login error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firebase authentication failed.",
        )


async def _firebase_register(request: RegisterRequest) -> AuthResponse:
    """Register a new user with Firebase Auth."""
    try:
        from firebase_admin import auth as firebase_auth

        firebase_user = firebase_auth.create_user(
            email=request.email,
            password=request.password,
            display_name=request.name,
        )

        # Store in MongoDB
        db = get_mongodb_db()
        if db is not None:
            await db["users"].insert_one(
                {
                    "_id": firebase_user.uid,
                    "email": request.email,
                    "name": request.name,
                    "role": (
                        request.role.value
                        if hasattr(request.role, "value")
                        else request.role
                    ),
                    "phone": request.phone,
                    "firebase_uid": firebase_user.uid,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            )

        token = create_access_token(
            {
                "sub": firebase_user.uid,
                "email": request.email,
                "name": request.name,
                "role": (
                    request.role.value
                    if hasattr(request.role, "value")
                    else request.role
                ),
            }
        )

        return AuthResponse(
            access_token=token,
            user=UserResponse(
                id=firebase_user.uid,
                email=request.email,
                name=request.name,
                role=request.role,
            ),
        )
    except Exception as e:
        logger.error("Firebase registration error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}",
        )
