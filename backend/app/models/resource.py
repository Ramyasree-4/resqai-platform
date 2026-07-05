"""
ResQAI – Resource Pydantic Models
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.enums import ResourceType, ResourceStatus
from app.models.incident import Coordinates


class ResourceCapacity(BaseModel):
    total: Optional[int] = Field(None, ge=0)
    current: Optional[int] = Field(None, ge=0)
    available: Optional[int] = Field(None, ge=0)


class ResourceBaseLocation(BaseModel):
    address: str = Field(..., max_length=500)
    district: str = Field(..., max_length=100)
    coordinates: Coordinates


class ResourceCurrentLocation(BaseModel):
    coordinates: Coordinates
    updatedAt: Optional[datetime] = None
    updatedBy: str = "MANUAL"


class ResourceCurrentAssignment(BaseModel):
    incidentId: Optional[str] = None
    incidentTitle: Optional[str] = None
    assignedAt: Optional[datetime] = None
    estimatedReturn: Optional[datetime] = None


# ── Request Schemas ───────────────────────────────────────────────────────────

class ResourceCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    type: ResourceType
    subType: Optional[str] = Field(None, max_length=100)
    organizationId: str = Field(..., min_length=1)
    organizationName: str = Field(..., min_length=2, max_length=200)
    district: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=100)
    contactName: str = Field(..., min_length=2, max_length=100)
    contactPhone: str = Field(..., pattern=r"^\+91[6-9]\d{9}$")
    contactEmail: Optional[str] = None
    capabilities: List[str] = []
    baseLocation: ResourceBaseLocation
    capacity: Optional[ResourceCapacity] = None
    notes: Optional[str] = Field(None, max_length=500)


class ResourceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    contactName: Optional[str] = Field(None, min_length=2, max_length=100)
    contactPhone: Optional[str] = Field(None, pattern=r"^\+91[6-9]\d{9}$")
    contactEmail: Optional[str] = None
    capabilities: Optional[List[str]] = None
    capacity: Optional[ResourceCapacity] = None
    notes: Optional[str] = Field(None, max_length=500)


class ResourceStatusUpdate(BaseModel):
    status: ResourceStatus
    note: Optional[str] = Field(None, max_length=500)


class ResourceLocationUpdate(BaseModel):
    coordinates: Coordinates
    updatedBy: str = "MANUAL"


# ── Response Schemas ──────────────────────────────────────────────────────────

class ResourceResponse(BaseModel):
    resourceId: str
    name: str
    type: ResourceType
    subType: Optional[str] = None
    organizationId: str
    organizationName: str
    district: str
    state: str
    contactName: str
    contactPhone: str
    contactEmail: Optional[str] = None
    status: ResourceStatus
    statusUpdatedAt: Optional[datetime] = None
    capacity: Optional[ResourceCapacity] = None
    currentAssignment: ResourceCurrentAssignment = ResourceCurrentAssignment()
    baseLocation: ResourceBaseLocation
    currentLocation: Optional[ResourceCurrentLocation] = None
    capabilities: List[str] = []
    isActive: bool = True
    notes: Optional[str] = None
    registeredAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


class ResourceNearby(BaseModel):
    resourceId: str
    name: str
    type: ResourceType
    status: ResourceStatus
    distanceKm: float
    estimatedArrivalMinutes: int
    coordinates: Optional[Coordinates] = None
