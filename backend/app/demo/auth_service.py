"""
ResQAI – Demo Authentication Service
Full auth without Firebase — uses JWT + in-memory store.
Works for hackathon demo with no external dependencies.
"""
import hashlib
import hmac
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import JWTError, jwt

from app.core.exceptions import (
    AuthenticationError,
    DuplicateEmailError,
    UserNotFoundError,
)
from app.core.logging import get_logger
from app.demo import store
from app.models.user import UserCreate, UserUpdate

logger = get_logger(__name__)

# ── JWT config ─────────────────────────────────────────────────────────────────
def _jwt_secret() -> str:
    return os.getenv("JWT_SECRET_KEY", "resqai-demo-secret-key-32chars!!")

ALGORITHM = "HS256"
ACCESS_EXPIRE_MINUTES = 60
REFRESH_EXPIRE_DAYS = 7


def _hash_password(password: str, salt: str) -> str:
    return hmac.new(
        (salt + password).encode(),
        password.encode(),
        hashlib.sha256,
    ).hexdigest()


def _make_token(uid: str, role: str, district: str, state: str,
                expires_delta: timedelta) -> str:
    payload = {
        "uid": uid,
        "role": role,
        "district": district,
        "state": state,
        "exp": datetime.now(timezone.utc) + expires_delta,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, _jwt_secret(), algorithm=ALGORITHM)


def verify_token(token: str) -> Dict[str, Any]:
    """Verify JWT and return payload. Raises AuthenticationError on failure."""
    try:
        payload = jwt.decode(token, _jwt_secret(), algorithms=[ALGORITHM])
        if not payload.get("uid"):
            raise AuthenticationError(message="Invalid token payload.")
        return payload
    except JWTError as e:
        raise AuthenticationError(message=f"Invalid or expired token: {str(e)}")


class DemoAuthService:
    """
    Drop-in replacement for AuthService when Firebase is not available.
    Uses JWT + in-memory dictionary store.
    """

    async def register(self, data: UserCreate) -> Dict[str, Any]:
        # Check duplicate email
        if store.get_user_by_email(data.email):
            raise DuplicateEmailError()

        uid = str(uuid.uuid4())
        salt = uuid.uuid4().hex
        password_hash = _hash_password(data.password, salt)
        now = datetime.now(timezone.utc)

        user_doc = {
            "uid": uid,
            "email": data.email,
            "displayName": data.displayName,
            "phoneNumber": getattr(data, "phoneNumber", None),
            "role": data.role.value,
            "district": data.district,
            "state": data.state,
            "pincode": None,
            "address": getattr(data, "address", None),
            "isVerified": True,   # Auto-verified in demo mode
            "isActive": True,
            "hasDisability": False,
            "mfaEnabled": False,
            "emergencyContacts": [],
            "authProviders": ["password"],
            "notificationPreferences": {"pushEnabled": True, "smsEnabled": True, "emailEnabled": True, "language": "en"},
            "fcmTokens": [],
            "loginCount": 1,
            "_passwordHash": password_hash,
            "_salt": salt,
            "createdAt": now,
            "updatedAt": now,
            "lastLoginAt": now,
        }
        store.create_user(uid, user_doc)

        token = _make_token(uid, data.role.value, data.district, data.state,
                            timedelta(minutes=ACCESS_EXPIRE_MINUTES))
        refresh = _make_token(uid, data.role.value, data.district, data.state,
                              timedelta(days=REFRESH_EXPIRE_DAYS))

        logger.info("Demo user registered", uid=uid, role=data.role.value)
        return {
            "uid": uid,
            "email": data.email,
            "displayName": data.displayName,
            "role": data.role.value,
            "token": token,
            "refreshToken": refresh,
            "expiresIn": ACCESS_EXPIRE_MINUTES * 60,
            "user": {
                "uid": uid,
                "displayName": data.displayName,
                "email": data.email,
                "role": data.role.value,
                "district": data.district,
                "state": data.state,
            },
        }

    async def login(self, email: str, password: str) -> Dict[str, Any]:
        user = store.get_user_by_email(email)
        if not user:
            raise AuthenticationError(message="Invalid email or password.")

        # Verify password
        expected = _hash_password(password, user["_salt"])
        if not hmac.compare_digest(expected, user["_passwordHash"]):
            raise AuthenticationError(message="Invalid email or password.")

        if not user.get("isActive", True):
            raise AuthenticationError(message="Account is disabled.")

        uid = user["uid"]
        role = user.get("role", "CITIZEN")
        district = user.get("district", "")
        state = user.get("state", "")

        store.update_user(uid, {
            "lastLoginAt": datetime.now(timezone.utc),
            "loginCount": user.get("loginCount", 0) + 1,
        })

        token = _make_token(uid, role, district, state, timedelta(minutes=ACCESS_EXPIRE_MINUTES))
        refresh = _make_token(uid, role, district, state, timedelta(days=REFRESH_EXPIRE_DAYS))

        logger.info("Demo user logged in", uid=uid, role=role)
        return {
            "uid": uid,
            "token": token,
            "refreshToken": refresh,
            "expiresIn": ACCESS_EXPIRE_MINUTES * 60,
            "user": {
                "uid": uid,
                "displayName": user.get("displayName"),
                "email": user.get("email"),
                "role": role,
                "district": district,
                "state": state,
            },
        }

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        payload = verify_token(refresh_token)
        uid = payload["uid"]
        user = store.get_user(uid)
        if not user:
            raise AuthenticationError(message="User not found.")
        new_token = _make_token(
            uid, payload["role"], payload.get("district", ""), payload.get("state", ""),
            timedelta(minutes=ACCESS_EXPIRE_MINUTES)
        )
        return {"token": new_token, "expiresIn": ACCESS_EXPIRE_MINUTES * 60}

    async def send_password_reset(self, email: str) -> None:
        pass  # No-op in demo mode

    async def get_profile(self, uid: str) -> Dict[str, Any]:
        user = store.get_user(uid)
        if not user:
            raise UserNotFoundError()
        return {k: v for k, v in user.items() if not k.startswith("_")}

    async def update_profile(self, uid: str, data: UserUpdate) -> Dict[str, Any]:
        updates = {k: v for k, v in data.model_dump(exclude_none=True).items()}
        updates["updatedAt"] = datetime.now(timezone.utc)
        store.update_user(uid, updates)
        return await self.get_profile(uid)

    async def register_fcm_token(self, uid: str, token: str) -> None:
        user = store.get_user(uid)
        if user:
            tokens = user.get("fcmTokens", [])
            if token not in tokens:
                tokens.append(token)
            store.update_user(uid, {"fcmTokens": tokens})

    async def update_role(self, uid: str, new_role, district: Optional[str] = None) -> None:
        updates = {"role": new_role.value if hasattr(new_role, "value") else new_role}
        if district:
            updates["district"] = district
        store.update_user(uid, updates)

    async def deactivate_user(self, uid: str) -> None:
        store.update_user(uid, {"isActive": False})

    def list_users(self, role=None, district=None, is_active=None, page=1, limit=20):
        return store.list_users(role=role, district=district, is_active=is_active, page=page, limit=limit)
