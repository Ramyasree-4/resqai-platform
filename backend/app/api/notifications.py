"""
ResQAI – Notifications API Router
GET notifications, mark read, broadcast.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query

from app.core.responses import success_response, paginated_response
from app.middleware.auth import (
    AuthenticatedUser,
    get_current_user,
    require_roles,
)
from app.models.enums import UserRole
from app.models.notification import BroadcastCreate
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])


def _svc() -> NotificationService:
    return NotificationService()


@router.get("")
async def list_notifications(
    is_read: Optional[bool] = Query(None, alias="isRead"),
    notification_type: Optional[str] = Query(None, alias="type"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    current_user: AuthenticatedUser = Depends(get_current_user),
    svc: NotificationService = Depends(_svc),
):
    """Get notifications for the authenticated user."""
    result = svc.get_user_notifications(
        current_user.uid, is_read, notification_type, page, limit
    )
    return paginated_response(
        result["notifications"], result["total"], result["page"], result["limit"]
    )


@router.put("/read-all")
async def mark_all_read(
    current_user: AuthenticatedUser = Depends(get_current_user),
    svc: NotificationService = Depends(_svc),
):
    """Mark all current user's notifications as read."""
    count = svc.mark_all_read(current_user.uid)
    return success_response({"marked": count}, f"{count} notifications marked as read.")


@router.put("/{notification_id}/read")
async def mark_as_read(
    notification_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
    svc: NotificationService = Depends(_svc),
):
    """Mark a specific notification as read."""
    svc.mark_as_read(notification_id, current_user.uid)
    return success_response(None, "Notification marked as read.")


@router.post("/broadcast")
async def send_broadcast(
    data: BroadcastCreate,
    current_user: AuthenticatedUser = Depends(
        require_roles(UserRole.STATE_OFFICER, UserRole.ADMIN)
    ),
    svc: NotificationService = Depends(_svc),
):
    """Send a broadcast alert to all users in a district/state."""
    result = svc.send_broadcast(data, current_user.uid)
    return success_response(result)
