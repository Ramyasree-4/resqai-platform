"""
ResQAI – Authentication Service
Handles Firebase Auth operations: register, login, token refresh,
custom claims, and profile management.
"""
import httpx
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from firebase_admin import auth

from app.config import settings           # module-level instance — always fresh
from app.core.exceptions import (
    AuthenticationError,
    DuplicateEmailError,
    FirebaseError,
    UserNotFoundError,
)
from app.core.logging import get_logger
from app.firebase.client import Collections, get_auth_client, get_firestore_client
from app.models.enums import UserRole
from app.models.user import UserCreate, UserUpdate

logger = get_logger(__name__)

FIREBASE_AUTH_REST = "https://identitytoolkit.googleapis.com/v1/accounts"


def _web_api_key() -> str:
    """Always resolve the Firebase Web API Key at call time — never cached."""
    import os
    return (
        os.getenv("FIREBASE_WEB_API_KEY")
        or settings.FIREBASE_WEB_API_KEY
        or ""
    )


class AuthService:

    def __init__(self):
        self._db = get_firestore_client()
        self._auth = get_auth_client()

    # ── Registration ──────────────────────────────────────────────────────

    async def register(self, data: UserCreate) -> Dict[str, Any]:
        # 1. Create Firebase Auth user
        try:
            fb_user = self._auth.create_user(
                email=data.email,
                password=data.password,
                display_name=data.displayName,
                phone_number=data.phoneNumber if data.phoneNumber else None,
            )
        except self._auth.EmailAlreadyExistsError:
            raise DuplicateEmailError()
        except Exception as e:
            logger.error("Firebase create_user failed", error=str(e))
            raise FirebaseError(message=f"Failed to create user: {str(e)}")

        # 2. Set custom claims
        claims = {"role": data.role.value, "district": data.district, "state": data.state}
        try:
            self._auth.set_custom_user_claims(fb_user.uid, claims)
        except Exception as e:
            try:
                self._auth.delete_user(fb_user.uid)
            except Exception:
                pass
            raise FirebaseError(message=f"Failed to set user claims: {str(e)}")

        # 3. Save user document in Firestore
        now = datetime.now(timezone.utc)
        user_doc = {
            "uid": fb_user.uid,
            "email": data.email,
            "displayName": data.displayName,
            "phoneNumber": data.phoneNumber,
            "role": data.role.value,
            "district": data.district,
            "state": data.state,
            "pincode": None,
            "address": getattr(data, "address", None),
            "isVerified": False,
            "isActive": True,
            "hasDisability": False,
            "disabilityDetails": None,
            "organizationId": None,
            "organizationName": None,
            "designation": None,
            "badgeNumber": None,
            "emergencyContacts": [],
            "authProviders": ["password"],
            "mfaEnabled": False,
            "notificationPreferences": {
                "pushEnabled": True, "smsEnabled": True,
                "emailEnabled": True, "language": "en",
            },
            "fcmTokens": [],
            "loginCount": 0,
            "createdAt": now,
            "updatedAt": now,
            "lastLoginAt": None,
            "lastLoginIP": None,
            "createdBy": None,
        }
        try:
            self._db.collection(Collections.USERS).document(fb_user.uid).set(user_doc)
        except Exception as e:
            try:
                self._auth.delete_user(fb_user.uid)
            except Exception:
                pass
            raise FirebaseError(message=f"Failed to save user profile: {str(e)}")

        # 4. Sign in via REST to get tokens
        tokens = await self._sign_in_rest(data.email, data.password)

        logger.info("User registered", uid=fb_user.uid, role=data.role.value)
        return {
            "uid": fb_user.uid,
            "email": data.email,
            "displayName": data.displayName,
            "role": data.role.value,
            "token": tokens["idToken"],
            "refreshToken": tokens["refreshToken"],
            "expiresIn": int(tokens.get("expiresIn", 3600)),
            "user": {
                "uid": fb_user.uid,
                "displayName": data.displayName,
                "email": data.email,
                "role": data.role.value,
                "district": data.district,
                "state": data.state,
            },
        }

    # ── Login ─────────────────────────────────────────────────────────────

    async def login(self, email: str, password: str) -> Dict[str, Any]:
        tokens = await self._sign_in_rest(email, password)
        uid = tokens["localId"]
        user_doc = await self._get_user_doc(uid)

        self._db.collection(Collections.USERS).document(uid).update({
            "lastLoginAt": datetime.now(timezone.utc),
            "loginCount": (user_doc.get("loginCount", 0) + 1),
        })

        logger.info("User logged in", uid=uid, role=user_doc.get("role"))
        return {
            "uid": uid,
            "token": tokens["idToken"],
            "refreshToken": tokens["refreshToken"],
            "expiresIn": int(tokens.get("expiresIn", 3600)),
            "user": {
                "uid": uid,
                "displayName": user_doc.get("displayName"),
                "email": user_doc.get("email"),
                "role": user_doc.get("role"),
                "district": user_doc.get("district"),
                "state": user_doc.get("state"),
            },
        }

    # ── Token Refresh ─────────────────────────────────────────────────────

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        url = f"https://securetoken.googleapis.com/v1/token?key={_web_api_key()}"
        payload = {"grant_type": "refresh_token", "refresh_token": refresh_token}
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, timeout=10)
        if resp.status_code != 200:
            raise AuthenticationError(message="Invalid or expired refresh token.")
        data = resp.json()
        return {"token": data["id_token"], "expiresIn": int(data.get("expires_in", 3600))}

    # ── Password Reset ────────────────────────────────────────────────────

    async def send_password_reset(self, email: str) -> None:
        url = f"{FIREBASE_AUTH_REST}:sendOobCode?key={_web_api_key()}"
        payload = {"requestType": "PASSWORD_RESET", "email": email}
        async with httpx.AsyncClient() as client:
            await client.post(url, json=payload, timeout=10)

    # ── Profile ───────────────────────────────────────────────────────────

    async def get_profile(self, uid: str) -> Dict[str, Any]:
        return await self._get_user_doc(uid)

    async def update_profile(self, uid: str, data: UserUpdate) -> Dict[str, Any]:
        updates: Dict[str, Any] = {"updatedAt": datetime.now(timezone.utc)}
        for field, value in data.model_dump(exclude_none=True).items():
            updates[field] = value if isinstance(value, dict) else value
        if data.displayName:
            try:
                self._auth.update_user(uid, display_name=data.displayName)
            except Exception:
                pass
        self._db.collection(Collections.USERS).document(uid).update(updates)
        return await self._get_user_doc(uid)

    async def register_fcm_token(self, uid: str, token: str) -> None:
        from google.cloud.firestore import ArrayUnion
        self._db.collection(Collections.USERS).document(uid).update({
            "fcmTokens": ArrayUnion([token]),
            "updatedAt": datetime.now(timezone.utc),
        })

    async def update_role(
        self, uid: str, new_role: UserRole, district: Optional[str] = None
    ) -> None:
        claims: Dict[str, Any] = {"role": new_role.value}
        if district:
            claims["district"] = district
        try:
            self._auth.set_custom_user_claims(uid, claims)
        except Exception as e:
            raise FirebaseError(message=f"Failed to update role claims: {str(e)}")
        self._db.collection(Collections.USERS).document(uid).update({
            "role": new_role.value,
            "updatedAt": datetime.now(timezone.utc),
        })

    async def deactivate_user(self, uid: str) -> None:
        try:
            self._auth.update_user(uid, disabled=True)
        except Exception as e:
            raise FirebaseError(message=f"Failed to disable user: {str(e)}")
        self._db.collection(Collections.USERS).document(uid).update({
            "isActive": False, "updatedAt": datetime.now(timezone.utc),
        })

    def list_users(
        self,
        role: Optional[str] = None,
        district: Optional[str] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Dict[str, Any]:
        query = self._db.collection(Collections.USERS)
        if role:
            query = query.where("role", "==", role)
        if district:
            query = query.where("district", "==", district)
        if is_active is not None:
            query = query.where("isActive", "==", is_active)
        all_docs = list(query.stream())
        users = [doc.to_dict() for doc in all_docs]
        total = len(users)
        start = (page - 1) * limit
        return {"users": users[start:start + limit], "total": total, "page": page, "limit": limit}

    # ── Internal helpers ──────────────────────────────────────────────────

    async def _sign_in_rest(self, email: str, password: str) -> Dict[str, Any]:
        """Call Firebase REST signInWithPassword — always resolves API key fresh."""
        key = _web_api_key()
        url = f"{FIREBASE_AUTH_REST}:signInWithPassword?key={key}"
        payload = {"email": email, "password": password, "returnSecureToken": True}
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, timeout=15)
        if resp.status_code != 200:
            try:
                error_msg = resp.json().get("error", {}).get("message", "LOGIN_FAILED")
            except Exception:
                error_msg = "LOGIN_FAILED"
            if error_msg in ("EMAIL_NOT_FOUND", "INVALID_PASSWORD", "INVALID_LOGIN_CREDENTIALS"):
                raise AuthenticationError(message="Invalid email or password.")
            if "TOO_MANY_ATTEMPTS" in error_msg:
                raise AuthenticationError(message="Account temporarily locked.")
            raise AuthenticationError(message=f"Authentication failed: {error_msg}")
        return resp.json()

    async def _get_user_doc(self, uid: str) -> Dict[str, Any]:
        doc = self._db.collection(Collections.USERS).document(uid).get()
        if not doc.exists:
            raise UserNotFoundError()
        data = doc.to_dict()
        for field in ("createdAt", "updatedAt", "lastLoginAt"):
            if field in data and hasattr(data[field], "ToDatetime"):
                data[field] = data[field].ToDatetime()
        return data
