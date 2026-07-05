"""
ResQAI – Authentication & Authorization Middleware
Supports two modes:
  1. Firebase JWT — when Firebase is configured
  2. Demo JWT    — when DEMO_MODE=true or Firebase unavailable
"""
import os
from typing import List, Optional

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.exceptions import (
    AuthenticationError,
    InsufficientRoleError,
    InvalidTokenError,
    TokenExpiredError,
)
from app.core.logging import get_logger
from app.models.enums import UserRole

logger = get_logger(__name__)
security = HTTPBearer(auto_error=False)

# ── Detect demo mode ───────────────────────────────────────────────────────────
def _is_demo_mode() -> bool:
    return os.getenv("DEMO_MODE", "false").lower() in ("true", "1", "yes")


class AuthenticatedUser:
    """Holds decoded token claims for the current request."""

    def __init__(self, decoded_token: dict):
        self.uid: str = decoded_token.get("uid", decoded_token.get("user_id", ""))
        self.email: str = decoded_token.get("email", "")
        self.role: UserRole = UserRole(decoded_token.get("role", UserRole.CITIZEN))
        self.district: Optional[str] = decoded_token.get("district")
        self.state: Optional[str] = decoded_token.get("state")
        self.organization_id: Optional[str] = decoded_token.get("organizationId")
        self._raw = decoded_token

    def has_role(self, *roles: UserRole) -> bool:
        return self.role in roles

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

    @property
    def is_authority_or_above(self) -> bool:
        return self.role in (
            UserRole.AUTHORITY, UserRole.DISTRICT_OFFICER,
            UserRole.STATE_OFFICER, UserRole.ADMIN,
        )

    @property
    def is_state_or_above(self) -> bool:
        return self.role in (UserRole.STATE_OFFICER, UserRole.ADMIN)


def _verify_demo_token(token: str) -> dict:
    """Verify a demo-mode JWT token."""
    from app.demo.auth_service import verify_token
    return verify_token(token)


def _verify_firebase_token(token: str) -> dict:
    """Verify a Firebase ID token."""
    from app.firebase.client import get_auth_client
    auth = get_auth_client()
    try:
        return auth.verify_id_token(token, check_revoked=True)
    except Exception as e:
        err = str(e).lower()
        if "expired" in err:
            raise TokenExpiredError()
        if "revoked" in err:
            raise InvalidTokenError(message="Token has been revoked.")
        raise InvalidTokenError(message=f"Invalid token: {str(e)}")


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> AuthenticatedUser:
    """FastAPI dependency: verify Bearer JWT (Firebase or Demo mode)."""
    if not credentials:
        raise AuthenticationError(message="Authorization header is missing.")

    token = credentials.credentials

    if _is_demo_mode():
        # Demo mode — use local JWT verification
        try:
            decoded = _verify_demo_token(token)
            return AuthenticatedUser(decoded)
        except AuthenticationError:
            raise
        except Exception as e:
            raise InvalidTokenError(message=f"Invalid demo token: {str(e)}")
    else:
        # Production mode — use Firebase
        try:
            decoded = _verify_firebase_token(token)
            return AuthenticatedUser(decoded)
        except (TokenExpiredError, InvalidTokenError, AuthenticationError):
            raise
        except Exception as e:
            logger.error("Token verification failed", error=str(e))
            raise AuthenticationError(message="Token verification failed.")


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[AuthenticatedUser]:
    """Optional auth — returns None if no token provided."""
    if not credentials:
        return None
    try:
        return await get_current_user(credentials)
    except (AuthenticationError, TokenExpiredError, InvalidTokenError):
        return None


def require_roles(*allowed_roles: UserRole):
    """Role guard dependency factory."""
    async def dependency(
        current_user: AuthenticatedUser = Depends(get_current_user),
    ) -> AuthenticatedUser:
        if current_user.role not in allowed_roles:
            raise InsufficientRoleError(
                message=f"Role '{current_user.role}' not authorized. "
                        f"Required: {[r.value for r in allowed_roles]}",
            )
        return current_user
    return dependency


# ── Pre-built role dependencies ───────────────────────────────────────────────
RequireAdmin = Depends(require_roles(UserRole.ADMIN))
RequireAuthority = Depends(require_roles(
    UserRole.AUTHORITY, UserRole.DISTRICT_OFFICER, UserRole.STATE_OFFICER, UserRole.ADMIN,
))
RequireDistrictOfficer = Depends(require_roles(
    UserRole.DISTRICT_OFFICER, UserRole.STATE_OFFICER, UserRole.ADMIN,
))
RequireStateOfficer = Depends(require_roles(UserRole.STATE_OFFICER, UserRole.ADMIN))
