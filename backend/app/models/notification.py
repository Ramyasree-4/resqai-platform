"""
ResQAI – Notification Pydantic Models
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.enums import NotificationType, NotificationPriority


class ChannelStatus(BaseModel):
    sent: bool = False
    sentAt: Optional[datetime] = None
    deliveredAt: Optional[datetime] = None
    messageId: Optional[str] = None
    error: Optional[str] = None


class NotificationChannels(BaseModel):
    push: ChannelStatus = ChannelStatus()
    sms: ChannelStatus = ChannelStatus()
    email: ChannelStatus = ChannelStatus()


class NotificationCreate(BaseModel):
    recipientId: Optional[str] = None
    recipientRole: Optional[str] = None
    district: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=200)
    body: str = Field(..., min_length=1, max_length=1000)
    type: NotificationType
    relatedIncidentId: Optional[str] = None
    relatedResourceId: Optional[str] = None
    actionUrl: Optional[str] = None
    priority: NotificationPriority = NotificationPriority.NORMAL
    expiresAt: Optional[datetime] = None


class BroadcastCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    body: str = Field(..., min_length=1, max_length=1000)
    targetDistrict: Optional[str] = None
    targetState: Optional[str] = None
    channels: List[str] = Field(default=["push"], max_length=3)
    priority: NotificationPriority = NotificationPriority.URGENT


class NotificationResponse(BaseModel):
    notificationId: str
    recipientId: Optional[str] = None
    title: str
    body: str
    type: NotificationType
    relatedIncidentId: Optional[str] = None
    actionUrl: Optional[str] = None
    isRead: bool = False
    readAt: Optional[datetime] = None
    priority: NotificationPriority
    channels: NotificationChannels = NotificationChannels()
    createdAt: Optional[datetime] = None
    expiresAt: Optional[datetime] = None
