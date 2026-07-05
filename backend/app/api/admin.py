"""
ResQAI – Admin API Router
User management, audit logs, system settings, platform stats.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query

from app.core.responses import success_response, created_response, paginated_response
from app.middleware.auth import (
    AuthenticatedUser,
    require_roles,
)
from app.models.enums import UserRole
from app.models.user import UserCreate
from app.services.auth_service import AuthService
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/admin", tags=["Admin"])

RequireAdmin = Depends(require_roles(UserRole.ADMIN))


def _auth_svc() -> AuthService:
    return AuthService()


def _analytics_svc() -> AnalyticsService:
    return AnalyticsService()


# ── Users ─────────────────────────────────────────────────────────────────────

@router.get("/users")
async def list_users(
    role: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None, alias="isActive"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: AuthenticatedUser = RequireAdmin,
    svc: AuthService = Depends(_auth_svc),
):
    """List all users with optional filters."""
    result = svc.list_users(role=role, district=district, is_active=is_active, page=page, limit=limit)
    return paginated_response(result["users"], result["total"], result["page"], result["limit"])


@router.post("/users")
async def create_user(
    data: UserCreate,
    current_user: AuthenticatedUser = RequireAdmin,
    svc: AuthService = Depends(_auth_svc),
):
    """Admin: create a new user account (authority, NGO, etc.)."""
    result = await svc.register(data)
    return created_response(result)


@router.put("/users/{uid}/role")
async def update_user_role(
    uid: str,
    request_body: dict,
    current_user: AuthenticatedUser = RequireAdmin,
    svc: AuthService = Depends(_auth_svc),
):
    """Update a user's role."""
    new_role = UserRole(request_body.get("role"))
    district = request_body.get("district")
    await svc.update_role(uid, new_role, district)
    return success_response(None, f"User role updated to {new_role.value}.")


@router.put("/users/{uid}/deactivate")
async def deactivate_user(
    uid: str,
    current_user: AuthenticatedUser = RequireAdmin,
    svc: AuthService = Depends(_auth_svc),
):
    """Deactivate a user account."""
    await svc.deactivate_user(uid)
    return success_response(None, "User deactivated.")


# ── Audit Logs ────────────────────────────────────────────────────────────────

@router.get("/audit-logs")
async def get_audit_logs(
    user_id: Optional[str] = Query(None, alias="userId"),
    action: Optional[str] = Query(None),
    resource: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: AuthenticatedUser = RequireAdmin,
):
    """Retrieve platform audit logs."""
    from app.firebase.client import get_firestore_client, Collections
    db = get_firestore_client()
    q = db.collection(Collections.AUDIT_LOGS).order_by("timestamp", direction="DESCENDING")
    if user_id:
        q = q.where("userId", "==", user_id)
    if action:
        q = q.where("action", "==", action)
    if resource:
        q = q.where("resource", "==", resource)

    docs = list(q.stream())
    logs = [d.to_dict() | {"_firestoreId": d.id} for d in docs]
    total = len(logs)
    start = (page - 1) * limit
    return paginated_response(logs[start: start + limit], total, page, limit)


# ── System Stats ──────────────────────────────────────────────────────────────

@router.get("/system-stats")
async def get_system_stats(
    current_user: AuthenticatedUser = RequireAdmin,
    svc: AnalyticsService = Depends(_analytics_svc),
):
    """Platform-wide system health and statistics."""
    result = svc.get_system_stats()
    return success_response(result)


# ── Settings ──────────────────────────────────────────────────────────────────

@router.get("/settings")
async def get_settings(
    current_user: AuthenticatedUser = RequireAdmin,
):
    """Get current system settings."""
    from app.firebase.client import get_firestore_client, Collections
    db = get_firestore_client()
    doc = db.collection(Collections.SETTINGS).document("system").get()
    return success_response(doc.to_dict() if doc.exists else {})


@router.put("/settings")
async def update_settings(
    request_body: dict,
    current_user: AuthenticatedUser = RequireAdmin,
):
    """Update system settings."""
    from app.firebase.client import get_firestore_client, Collections
    from datetime import datetime, timezone
    db = get_firestore_client()
    request_body["updatedAt"] = datetime.now(timezone.utc)
    request_body["updatedBy"] = current_user.uid
    db.collection(Collections.SETTINGS).document("system").set(request_body, merge=True)
    return success_response(None, "Settings updated.")
