"""
ResQAI – Notification Service
Creates in-app notifications and queues push/SMS/email delivery.
"""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.core.logging import get_logger
from app.firebase.client import Collections, get_firestore_client
from app.models.enums import NotificationPriority, NotificationType
from app.models.notification import BroadcastCreate, NotificationCreate
from app.utils.ids import generate_notification_id

logger = get_logger(__name__)


class NotificationService:

    def __init__(self):
        self._db = get_firestore_client()

    def create_notification(self, data: NotificationCreate) -> Dict[str, Any]:
        """Persist a notification document to Firestore."""
        notif_id = generate_notification_id()
        now = datetime.now(timezone.utc)

        doc = {
            "notificationId": notif_id,
            "recipientId": data.recipientId,
            "recipientRole": data.recipientRole,
            "district": data.district,
            "title": data.title,
            "body": data.body,
            "type": data.type.value,
            "relatedIncidentId": data.relatedIncidentId,
            "relatedResourceId": data.relatedResourceId,
            "actionUrl": data.actionUrl,
            "channels": {
                "push": {"sent": False},
                "sms": {"sent": False},
                "email": {"sent": False},
            },
            "isRead": False,
            "readAt": None,
            "priority": data.priority.value,
            "createdAt": now,
            "expiresAt": data.expiresAt,
            "createdBy": "SYSTEM",
        }

        ref = self._db.collection(Collections.NOTIFICATIONS).document()
        ref.set(doc)
        doc["_firestoreId"] = ref.id

        # Attempt FCM push (fire-and-forget)
        if data.recipientId:
            self._send_push(data.recipientId, data.title, data.body, data.type.value)

        return doc

    def get_user_notifications(
        self,
        uid: str,
        is_read: Optional[bool] = None,
        notification_type: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Dict[str, Any]:
        query = (
            self._db.collection(Collections.NOTIFICATIONS)
            .where("recipientId", "==", uid)
            .order_by("createdAt", direction="DESCENDING")
        )

        docs = list(query.stream())
        notifications = [d.to_dict() | {"_firestoreId": d.id} for d in docs]

        if is_read is not None:
            notifications = [n for n in notifications if n.get("isRead") == is_read]
        if notification_type:
            notifications = [n for n in notifications if n.get("type") == notification_type]

        total = len(notifications)
        start = (page - 1) * limit
        return {
            "notifications": notifications[start: start + limit],
            "total": total,
            "page": page,
            "limit": limit,
        }

    def mark_as_read(self, notif_firestore_id: str, uid: str) -> None:
        doc_ref = self._db.collection(Collections.NOTIFICATIONS).document(notif_firestore_id)
        doc = doc_ref.get()
        if not doc.exists:
            return
        if doc.to_dict().get("recipientId") != uid:
            return
        doc_ref.update({
            "isRead": True,
            "readAt": datetime.now(timezone.utc),
        })

    def mark_all_read(self, uid: str) -> int:
        docs = (
            self._db.collection(Collections.NOTIFICATIONS)
            .where("recipientId", "==", uid)
            .where("isRead", "==", False)
            .stream()
        )
        batch = self._db.batch()
        count = 0
        now = datetime.now(timezone.utc)
        for doc in docs:
            batch.update(doc.reference, {"isRead": True, "readAt": now})
            count += 1
        if count:
            batch.commit()
        return count

    def send_broadcast(
        self, data: BroadcastCreate, sender_uid: str
    ) -> Dict[str, Any]:
        """
        Send broadcast to all users in a district/state.
        In production, this would fan out to FCM topic or user list.
        """
        notif_id = generate_notification_id()
        now = datetime.now(timezone.utc)

        doc = {
            "notificationId": notif_id,
            "recipientId": None,  # broadcast
            "recipientRole": None,
            "district": data.targetDistrict,
            "state": data.targetState,
            "title": data.title,
            "body": data.body,
            "type": NotificationType.BROADCAST.value,
            "channels": {c: {"sent": True, "sentAt": now} for c in data.channels},
            "isRead": False,
            "readAt": None,
            "priority": data.priority.value,
            "createdAt": now,
            "createdBy": sender_uid,
        }

        ref = self._db.collection(Collections.NOTIFICATIONS).document()
        ref.set(doc)

        # Estimate recipient count (placeholder — production uses FCM topic subscription)
        recipient_count = self._estimate_recipients(data.targetDistrict, data.targetState)

        logger.info(
            "Broadcast sent",
            district=data.targetDistrict,
            state=data.targetState,
            recipients_est=recipient_count,
        )
        return {
            "notificationId": notif_id,
            "recipientCount": recipient_count,
            "deliveryStatus": "QUEUED",
        }

    def notify_new_critical_incident(
        self, incident_id: str, district: str, title: str, severity: int
    ) -> None:
        """Notify all authority users in a district of a new critical incident."""
        users_query = (
            self._db.collection(Collections.USERS)
            .where("district", "==", district)
            .where("role", "in", [
                "AUTHORITY", "DISTRICT_OFFICER", "STATE_OFFICER", "ADMIN"
            ])
            .where("isActive", "==", True)
            .stream()
        )
        for user_doc in users_query:
            uid = user_doc.id
            self.create_notification(NotificationCreate(
                recipientId=uid,
                title=f"🔴 New Critical Incident",
                body=f"{title} — Severity {severity}/10 in {district}",
                type=NotificationType.NEW_INCIDENT,
                relatedIncidentId=incident_id,
                priority=NotificationPriority.URGENT,
                actionUrl=f"/incidents/{incident_id}",
            ))

    def notify_incident_status_change(
        self, recipient_uid: str, incident_id: str, new_status: str, message: str
    ) -> None:
        self.create_notification(NotificationCreate(
            recipientId=recipient_uid,
            title=f"Incident Update: {new_status}",
            body=message,
            type=NotificationType.INCIDENT_STATUS,
            relatedIncidentId=incident_id,
            priority=NotificationPriority.NORMAL,
        ))

    # ── Internal helpers ──────────────────────────────────────────────────

    def _send_push(
        self, uid: str, title: str, body: str, notification_type: str
    ) -> None:
        """Fire-and-forget FCM push notification via Firebase Admin SDK."""
        try:
            from firebase_admin import messaging

            user_doc = self._db.collection(Collections.USERS).document(uid).get()
            if not user_doc.exists:
                return
            tokens = user_doc.to_dict().get("fcmTokens", [])
            if not tokens:
                return

            message = messaging.MulticastMessage(
                tokens=tokens,
                notification=messaging.Notification(title=title, body=body),
                data={"type": notification_type},
            )
            response = messaging.send_each_for_multicast(message)
            logger.info(
                "FCM push sent",
                uid=uid,
                success=response.success_count,
                failure=response.failure_count,
            )
        except Exception as e:
            logger.warning("FCM push failed", uid=uid, error=str(e))

    def _estimate_recipients(
        self, district: Optional[str], state: Optional[str]
    ) -> int:
        try:
            query = self._db.collection(Collections.USERS).where("isActive", "==", True)
            if district:
                query = query.where("district", "==", district)
            elif state:
                query = query.where("state", "==", state)
            return query.count().get()[0][0].value
        except Exception:
            return 0
