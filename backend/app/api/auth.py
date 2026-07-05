"""
ResQAI – Auth API Router
Supports both Firebase mode and Demo mode transparently.
"""
import os
from fastapi import APIRouter, Depends, Request, status

from app.core.responses import success_response, created_response
from app.middleware.auth import AuthenticatedUser, get_current_user
from app.models.user import FcmTokenRequest, UserCreate, UserUpdate

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _is_demo() -> bool:
    return os.getenv("DEMO_MODE", "false").lower() in ("true", "1", "yes")


def _get_service():
    """Return DemoAuthService or Firebase AuthService based on DEMO_MODE."""
    if _is_demo():
        from app.demo.auth_service import DemoAuthService
        return DemoAuthService()
    from app.services.auth_service import AuthService
    return AuthService()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate):
    """Register a new user account."""
    service = _get_service()
    result = await service.register(data)
    return created_response(result, "Account created successfully.")


@router.post("/login")
async def login(request: Request):
    """Authenticate user and return tokens."""
    body = await request.json()
    email = body.get("email", "")
    password = body.get("password", "")
    if not email or not password:
        from app.core.exceptions import ValidationError
        raise ValidationError(message="Email and password are required.")
    service = _get_service()
    result = await service.login(email, password)
    return success_response(result)


@router.post("/refresh")
async def refresh_token(request: Request):
    """Refresh access token."""
    body = await request.json()
    refresh = body.get("refreshToken", "")
    if not refresh:
        from app.core.exceptions import ValidationError
        raise ValidationError(message="refreshToken is required.")
    service = _get_service()
    result = await service.refresh_token(refresh)
    return success_response(result)


@router.post("/logout")
async def logout(current_user: AuthenticatedUser = Depends(get_current_user)):
    """Logout — client discards tokens."""
    if not _is_demo():
        from app.firebase.client import get_auth_client
        try:
            get_auth_client().revoke_refresh_tokens(current_user.uid)
        except Exception:
            pass
    return success_response(None, "Logged out successfully.")


@router.post("/forgot-password")
async def forgot_password(request: Request):
    """Send password reset email."""
    body = await request.json()
    email = body.get("email", "")
    service = _get_service()
    await service.send_password_reset(email)
    return success_response(None, "If that email is registered, a reset link has been sent.")


@router.get("/me")
async def get_me(current_user: AuthenticatedUser = Depends(get_current_user)):
    """Get current user profile."""
    service = _get_service()
    profile = await service.get_profile(current_user.uid)
    return success_response(profile)


@router.put("/profile")
async def update_profile(
    data: UserUpdate,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Update user profile."""
    service = _get_service()
    result = await service.update_profile(current_user.uid, data)
    return success_response(result, "Profile updated.")


@router.post("/fcm-token")
async def register_fcm_token(
    data: FcmTokenRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Register FCM token."""
    service = _get_service()
    await service.register_fcm_token(current_user.uid, data.token)
    return success_response(None, "FCM token registered.")
