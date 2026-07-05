"""
ResQAI – Firebase Admin SDK / Demo Mode Client
Returns real Firestore client OR in-memory mock based on DEMO_MODE env var.
"""
import json
import os
from functools import lru_cache
from typing import Optional

from app.core.logging import get_logger

logger = get_logger(__name__)

_firebase_app = None


def _is_demo() -> bool:
    return os.getenv("DEMO_MODE", "false").lower() in ("true", "1", "yes")


# ── Firestore client ──────────────────────────────────────────────────────────

def get_firestore_client():
    """Return Firestore client (real or mock based on DEMO_MODE)."""
    if _is_demo():
        from app.demo.firestore_mock import get_mock_firestore
        return get_mock_firestore()

    initialize_firebase()
    from firebase_admin import firestore
    return firestore.client()


# ── Firebase Auth client ──────────────────────────────────────────────────────

def get_auth_client():
    """Return Firebase Admin auth module (real or stub)."""
    if _is_demo():
        return _DemoAuthStub()

    initialize_firebase()
    from firebase_admin import auth
    return auth


class _DemoAuthStub:
    """Stub Firebase Auth for demo mode — no-op operations."""

    class EmailAlreadyExistsError(Exception):
        pass

    def create_user(self, **kwargs):
        import uuid
        class _User:
            uid = str(uuid.uuid4())
        return _User()

    def set_custom_user_claims(self, uid: str, claims: dict):
        from app.demo import store
        store.update_user(uid, claims)

    def verify_id_token(self, token: str, check_revoked: bool = False) -> dict:
        from app.demo.auth_service import verify_token
        return verify_token(token)

    def update_user(self, uid: str, **kwargs):
        pass

    def delete_user(self, uid: str):
        pass

    def revoke_refresh_tokens(self, uid: str):
        pass

    def get_user(self, uid: str):
        from app.demo import store
        u = store.get_user(uid)
        if not u:
            raise Exception("User not found")
        return u


def get_storage_client():
    """Return Firebase Storage (stub in demo mode)."""
    if _is_demo():
        return None
    initialize_firebase()
    from firebase_admin import storage
    return storage


# ── Firebase initialisation ───────────────────────────────────────────────────

def initialize_firebase():
    """Initialize Firebase Admin SDK. Skip in demo mode."""
    global _firebase_app

    if _is_demo():
        logger.info("DEMO_MODE=true — Firebase initialization skipped")
        # Seed demo data on first call
        from app.demo.store import seed_demo_data
        seed_demo_data()
        return None

    if _firebase_app is not None:
        return _firebase_app

    try:
        import firebase_admin
        from firebase_admin import credentials

        # Priority 1: JSON string env var (Cloud Run)
        sa_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
        if sa_json:
            sa_dict = json.loads(sa_json)
            cred = credentials.Certificate(sa_dict)
            logger.info("Firebase: initialized from JSON env var")
        else:
            # Priority 2: Service account file
            sa_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "./firebase-service-account.json")
            if sa_path and os.path.exists(sa_path):
                cred = credentials.Certificate(sa_path)
                logger.info("Firebase: initialized from file", path=sa_path)
            else:
                # Priority 3: Application Default Credentials
                cred = credentials.ApplicationDefault()
                logger.info("Firebase: initialized with Application Default Credentials")

        project_id = os.getenv("FIREBASE_PROJECT_ID", "resqai-dev")
        storage_bucket = os.getenv("FIREBASE_STORAGE_BUCKET", "resqai-dev.appspot.com")

        _firebase_app = firebase_admin.initialize_app(
            cred,
            {"projectId": project_id, "storageBucket": storage_bucket},
        )
        logger.info("Firebase Admin SDK initialized", project=project_id)
        return _firebase_app

    except Exception as e:
        logger.error("Firebase initialization failed", error=str(e))
        raise


# ── Collection Name Constants ─────────────────────────────────────────────────

class Collections:
    USERS = "users"
    INCIDENTS = "incidents"
    RESOURCES = "resources"
    NOTIFICATIONS = "notifications"
    ANALYTICS = "analytics"
    REPORTS = "reports"
    FEEDBACK = "feedback"
    SETTINGS = "settings"
    AUDIT_LOGS = "auditLogs"
    INCIDENT_COMMENTS = "comments"
    INCIDENT_STATUS_HISTORY = "statusHistory"
    RESOURCE_DEPLOYMENT_HISTORY = "deploymentHistory"
    USER_SESSIONS = "sessions"
