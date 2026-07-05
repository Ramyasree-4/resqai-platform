"""
ResQAI – User Pydantic Models
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.models.enums import UserRole


class EmergencyContact(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., pattern=r"^\+?[1-9]\d{7,14}$")
    relationship: str = Field(..., min_length=1, max_length=50)


class NotificationPreferences(BaseModel):
    pushEnabled: bool = True
    smsEnabled: bool = True
    emailEnabled: bool = True
    language: str = Field(default="en", pattern=r"^(en|hi|or|bn|ta|te|mr|gu|kn|ml)$")


class UserBase(BaseModel):
    email: EmailStr
    displayName: str = Field(..., min_length=2, max_length=100)
    phoneNumber: Optional[str] = Field(None, pattern=r"^\+91[6-9]\d{9}$")
    district: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=100)
    pincode: Optional[str] = Field(None, pattern=r"^\d{6}$")


class UserCreate(UserBase):
    """Schema for user registration."""
    password: str = Field(..., min_length=8, max_length=128)
    role: UserRole = UserRole.CITIZEN
    address: Optional[str] = Field(None, max_length=500)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Min 8 chars, 1 uppercase, 1 digit — no special char required."""
        errors = []
        if len(v) < 8:
            errors.append("at least 8 characters")
        if not any(c.isupper() for c in v):
            errors.append("at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            errors.append("at least one digit")
        if errors:
            raise ValueError(f"Password must contain: {', '.join(errors)}")
        return v


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    displayName: Optional[str] = Field(None, min_length=2, max_length=100)
    phoneNumber: Optional[str] = Field(None, pattern=r"^\+91[6-9]\d{9}$")
    district: Optional[str] = Field(None, min_length=2, max_length=100)
    state: Optional[str] = Field(None, min_length=2, max_length=100)
    address: Optional[str] = Field(None, max_length=500)
    notificationPreferences: Optional[NotificationPreferences] = None
    emergencyContacts: Optional[List[EmergencyContact]] = Field(None, max_length=3)
    hasDisability: Optional[bool] = None
    disabilityDetails: Optional[str] = Field(None, max_length=500)


class UserResponse(UserBase):
    """Full user response (safe — no password)."""
    uid: str
    role: UserRole
    isVerified: bool = False
    isActive: bool = True
    hasDisability: bool = False
    disabilityDetails: Optional[str] = None
    organizationId: Optional[str] = None
    organizationName: Optional[str] = None
    designation: Optional[str] = None
    badgeNumber: Optional[str] = None
    address: Optional[str] = None
    emergencyContacts: List[EmergencyContact] = []
    notificationPreferences: NotificationPreferences = NotificationPreferences()
    mfaEnabled: bool = False
    fcmTokens: List[str] = []
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    lastLoginAt: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UserPublicResponse(BaseModel):
    """Limited user info for public/cross-reference views."""
    uid: str
    displayName: str
    role: UserRole
    district: str
    state: str
    organizationName: Optional[str] = None


class FcmTokenRequest(BaseModel):
    token: str = Field(..., min_length=10)
