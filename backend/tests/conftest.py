import os
import pytest
from unittest.mock import MagicMock

# ── Set Test Environment Variables ──
os.environ["JWT_SECRET_KEY"] = "mock-secret-key-at-least-32-chars-long-123456789"
os.environ["AUTH_MODE"] = "local"
os.environ["MONGODB_URI"] = "mongodb://localhost:27017"
os.environ["MONGODB_DB_NAME"] = "rhos_test"

# ── Mock Classes ──

class MockAsyncCursor:
    def __init__(self, data):
        self.data = data
        self.index = 0

    def sort(self, *args, **kwargs):
        return self

    def skip(self, offset):
        self.data = self.data[offset:]
        return self

    def limit(self, limit):
        self.data = self.data[:limit]
        return self

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.index >= len(self.data):
            raise StopAsyncIteration
        val = self.data[self.index]
        self.index += 1
        return val

class MockCollection:
    def __init__(self, name, db_store):
        self.name = name
        self.db_store = db_store

    async def find_one(self, filter, *args, **kwargs):
        import copy
        docs = [copy.deepcopy(d) for d in self.db_store.get(self.name, {}).values()]
        if filter:
            for d in docs:
                match = True
                for k, v in filter.items():
                    if k == "_id" and d.get("_id") != v:
                        match = False
                    elif k != "_id" and d.get(k) != v:
                        match = False
                if match:
                    return d
            return None
        return docs[0] if docs else None

    async def insert_one(self, document, *args, **kwargs):
        import copy
        doc_id = document.get("_id")
        if not doc_id:
            import uuid
            doc_id = uuid.uuid4().hex
            document["_id"] = doc_id
        if self.name not in self.db_store:
            self.db_store[self.name] = {}
        self.db_store[self.name][doc_id] = copy.deepcopy(document)
        return document

    async def update_one(self, filter, update, *args, **kwargs):
        import copy
        doc_id = filter.get("_id")
        if not doc_id:
            existing = await self.find_one(filter)
            if existing:
                doc_id = existing["_id"]
        if self.name in self.db_store and doc_id in self.db_store[self.name]:
            set_data = update.get("$set", {})
            self.db_store[self.name][doc_id].update(copy.deepcopy(set_data))
        return None

    async def replace_one(self, filter, replacement, upsert=False, *args, **kwargs):
        import copy
        doc_id = filter.get("_id")
        if not doc_id:
            existing = await self.find_one(filter)
            if existing:
                doc_id = existing["_id"]
            elif upsert:
                doc_id = replacement.get("_id") or replacement.get("id") or "generated-id"
        
        if self.name not in self.db_store:
            self.db_store[self.name] = {}
            
        if doc_id:
            replacement["_id"] = doc_id
            self.db_store[self.name][doc_id] = copy.deepcopy(replacement)
        return None

    async def delete_one(self, filter, *args, **kwargs):
        doc_id = filter.get("_id")
        if not doc_id:
            existing = await self.find_one(filter)
            if existing:
                doc_id = existing["_id"]
        if self.name in self.db_store and doc_id in self.db_store[self.name]:
            del self.db_store[self.name][doc_id]
        return None

    def find(self, filter=None, *args, **kwargs):
        import copy
        docs = [copy.deepcopy(d) for d in self.db_store.get(self.name, {}).values()]
        if filter:
            filtered = []
            for d in docs:
                match = True
                for k, v in filter.items():
                    if k == "_id" and d.get("_id") != v:
                        match = False
                    elif k != "_id" and d.get(k) != v:
                        match = False
                if match:
                    filtered.append(d)
            docs = filtered
        return MockAsyncCursor(docs)

    async def count_documents(self, filter=None, *args, **kwargs):
        import copy
        docs = [copy.deepcopy(d) for d in self.db_store.get(self.name, {}).values()]
        if filter:
            filtered = []
            for d in docs:
                match = True
                for k, v in filter.items():
                    if k == "_id" and d.get("_id") != v:
                        match = False
                    elif k != "_id" and d.get(k) != v:
                        match = False
                if match:
                    filtered.append(d)
            return len(filtered)
        return len(docs)

class MockDatabase:
    def __init__(self, db_store):
        self.db_store = db_store
        self.collections = {}

    def __getitem__(self, name):
        if name not in self.collections:
            self.collections[name] = MockCollection(name, self.db_store)
        return self.collections[name]

# ── Setup Global Mock Store ──

GLOBAL_DB_STORE = {
    "users": {},
    "patients": {
        "p001": {
            "_id": "p001",
            "name": "Dinesh Sharma",
            "age": 45,
            "gender": "Male",
            "phone": "+91-925769943",
            "village_id": "v001",
            "asha_worker_id": "asha-001",
            "is_active": True,
            "created_at": "2026-07-19T00:00:00Z",
            "updated_at": "2026-07-19T00:00:00Z",
        }
    },
    "medical_history": {
        "h001": {
            "_id": "h001",
            "patient_id": "p001",
            "condition": "Hypertension",
            "diagnosed_date": "2025-01-10",
            "status": "active",
        }
    },
    "vitals": {
        "v001": {
            "_id": "v001",
            "patient_id": "p001",
            "recorded_at": "2026-07-19T10:00:00Z",
            "bp_sys": 130,
            "bp_dia": 85,
            "pulse": 72,
            "temperature": 98.6,
            "weight": 70.5,
        }
    },
    "allergies": {
        "a001": {
            "_id": "a001",
            "patient_id": "p001",
            "allergen": "Penicillin",
            "severity": "high",
        }
    },
    "consultations": {
        "c001": {
            "_id": "c001",
            "patient_id": "p001",
            "doctor_id": "demo-doctor-001",
            "status": "completed",
            "created_at": "2026-07-19T11:00:00Z",
            "chief_complaint": "Headache and mild fever",
            "summary": "Hypertension patient with fever.",
        }
    }
}

# ── Monkeypatch app.core.mongodb BEFORE importing app.main ──
import app.core.mongodb as mongodb_module
mock_db = MockDatabase(GLOBAL_DB_STORE)
mongodb_module._mongo_db = mock_db
mongodb_module._mongo_client = MagicMock()
mongodb_module.init_mongodb = lambda: None
mongodb_module.close_mongodb = lambda: None

# ── Mock Gemini AI Module BEFORE importing app.main ──
import app.services.gemini as gemini_module
mock_model = MagicMock()
mock_response = MagicMock()
mock_response.text = '{"safety": "safe", "interactions": "none", "recommendations": "safe to proceed"}'
mock_model.generate_content.return_value = mock_response
gemini_module._model = mock_model
# Also mock generate_text and analyze_image
async def mock_generate_text(*args, **kwargs):
    return '{"priority": "MEDIUM", "reasoning": "mocked reasoning", "confidence": 0.9, "recommendations": []}'
async def mock_analyze_image(*args, **kwargs):
    return "Mocked visible image findings."
gemini_module.generate_text = mock_generate_text
gemini_module.analyze_image = mock_analyze_image

# Now import fastapi app safely
from app.main import app as fastapi_app
from app.core.security import create_access_token
from fastapi.testclient import TestClient

@pytest.fixture(scope="session", autouse=True)
def mock_db_setup():
    """Globally mock MongoDB database using in-memory store."""
    yield GLOBAL_DB_STORE

@pytest.fixture
def client():
    """FastAPI TestClient fixture."""
    with TestClient(fastapi_app) as test_client:
        yield test_client

@pytest.fixture
def auth_header():
    """Helper fixture to generate Bearer token for demo doctor."""
    token_data = {
        "sub": "demo-doctor-001",
        "email": "doctor@rhos.in",
        "name": "Dr. Priya Sharma",
        "role": "doctor",
    }
    token = create_access_token(token_data)
    return {"Authorization": f"Bearer {token}"}
