"""
ResQAI – Incident Pydantic Models
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
from app.models.enums import (
    IncidentType, IncidentStatus, UrgencyLevel, SeverityBand,
    ResourceType, ResourceUrgency, AiFeedback, LocationMethod,
    ResolutionOutcome, IncidentSource, ResourceAssignmentStatus,
)


# ── Sub-models ────────────────────────────────────────────────────────────────

class Coordinates(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)


class IncidentLocation(BaseModel):
    address: str = Field(..., min_length=5, max_length=500)
    district: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=100)
    pincode: Optional[str] = Field(None, pattern=r"^\d{6}$")
    coordinates: Coordinates
    geohash: Optional[str] = None
    accuracy: Optional[float] = Field(None, ge=0)
    locationMethod: LocationMethod = LocationMethod.GPS


class MediaFile(BaseModel):
    fileId: str
    url: str
    type: str = Field(..., pattern=r"^(image|video|audio|document)$")
    filename: str
    size: int = Field(..., ge=0)
    uploadedAt: Optional[datetime] = None


class ResourceRecommendation(BaseModel):
    resourceType: ResourceType
    quantity: int = Field(..., ge=1)
    urgency: ResourceUrgency
    reason: str


class AIAnalysis(BaseModel):
    analysisId: str
    processedAt: Optional[datetime] = None
    modelVersion: str = "gemini-1.5-pro"
    # Classification
    classifiedType: Optional[IncidentType] = None
    classificationConfidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    # Severity
    severityScore: Optional[float] = Field(None, ge=1.0, le=10.0)
    severityBand: Optional[SeverityBand] = None
    # Priority
    priorityRank: Optional[int] = None
    priorityScore: Optional[float] = Field(None, ge=0.0, le=1.0)
    # Recommendations
    resourceRecommendations: List[ResourceRecommendation] = []
    # Summary & Explainability
    situationSummary: Optional[str] = None
    reasoning: List[str] = []
    immediateActions: List[str] = []
    risks: List[str] = []
    # Duplicate detection
    isDuplicate: bool = False
    duplicateOf: Optional[str] = None
    duplicateScore: Optional[float] = Field(None, ge=0.0, le=1.0)
    # Data quality
    dataQuality: Optional[str] = None
    dataQualityNote: Optional[str] = None
    # Fallback
    fallbackUsed: bool = False
    # Authority feedback
    authorityFeedback: Optional[AiFeedback] = None
    feedbackNote: Optional[str] = None


class AssignedResource(BaseModel):
    resourceId: str
    resourceName: str
    resourceType: ResourceType
    assignedAt: Optional[datetime] = None
    status: ResourceAssignmentStatus = ResourceAssignmentStatus.DISPATCHED


class Assignment(BaseModel):
    authorityId: Optional[str] = None
    authorityName: Optional[str] = None
    assignedAt: Optional[datetime] = None
    resources: List[AssignedResource] = []


class Escalation(BaseModel):
    isEscalated: bool = False
    escalatedAt: Optional[datetime] = None
    escalatedBy: Optional[str] = None
    escalatedTo: Optional[str] = None
    escalationReason: Optional[str] = None
    escalationCount: int = 0


class Resolution(BaseModel):
    resolvedAt: Optional[datetime] = None
    resolvedBy: Optional[str] = None
    resolutionNote: Optional[str] = None
    outcome: Optional[ResolutionOutcome] = None


# ── Request Schemas ───────────────────────────────────────────────────────────

class IncidentCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=20, max_length=2000)
    incidentType: IncidentType
    urgencyLevel: UrgencyLevel
    affectedPeople: int = Field(..., ge=1, le=1_000_000)
    location: IncidentLocation
    fatalities: Optional[int] = Field(None, ge=0)
    injuries: Optional[int] = Field(None, ge=0)
    isAnonymous: bool = False
    source: IncidentSource = IncidentSource.WEB


class SOSCreate(BaseModel):
    coordinates: Coordinates
    description: Optional[str] = Field(None, max_length=500)
    phoneNumber: Optional[str] = Field(None, pattern=r"^\+91[6-9]\d{9}$")


class IncidentStatusUpdate(BaseModel):
    status: IncidentStatus
    note: Optional[str] = Field(None, max_length=500)


class IncidentAssign(BaseModel):
    authorityId: str
    resourceIds: List[str] = Field(..., min_length=1)


class IncidentEscalate(BaseModel):
    reason: str = Field(..., min_length=10, max_length=500)
    escalateTo: str  # Role string


class IncidentComment(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)
    isInternal: bool = False


class AIFeedbackRequest(BaseModel):
    feedback: AiFeedback
    classificationCorrect: Optional[bool] = None
    severityAccurate: Optional[bool] = None
    recommendationsUseful: Optional[bool] = None
    summaryAccurate: Optional[bool] = None
    comment: Optional[str] = Field(None, max_length=500)


# ── Response Schemas ──────────────────────────────────────────────────────────

class IncidentListItem(BaseModel):
    """Lightweight incident for list views."""
    incidentId: str
    title: str
    incidentType: IncidentType
    status: IncidentStatus
    urgencyLevel: UrgencyLevel
    severityScore: Optional[float] = None
    severityBand: Optional[SeverityBand] = None
    priorityRank: Optional[int] = None
    district: str
    state: str
    affectedPeople: int
    createdAt: Optional[datetime] = None
    reportedBy: Optional[str] = None
    reporterName: Optional[str] = None


class IncidentResponse(BaseModel):
    """Full incident detail response."""
    incidentId: str
    title: str
    description: str
    incidentType: IncidentType
    status: IncidentStatus
    urgencyLevel: UrgencyLevel
    affectedPeople: int
    fatalities: Optional[int] = None
    injuries: Optional[int] = None
    isAnonymous: bool = False
    location: IncidentLocation
    mediaFiles: List[MediaFile] = []
    aiAnalysis: Optional[AIAnalysis] = None
    assignedTo: Assignment = Assignment()
    escalation: Escalation = Escalation()
    resolution: Resolution = Resolution()
    linkedIncidents: List[str] = []
    source: IncidentSource = IncidentSource.WEB
    reportedBy: str
    reporterName: Optional[str] = None
    reporterPhone: Optional[str] = None
    responseTimeMinutes: Optional[float] = None
    version: int = 1
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


class IncidentCreateResponse(BaseModel):
    incidentId: str
    status: IncidentStatus
    message: str
    estimatedResponseTime: str
    trackingUrl: str


class IncidentComment_Response(BaseModel):
    commentId: str
    authorId: str
    authorName: str
    authorRole: str
    content: str
    isInternal: bool
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


# ── Filter / Query Params ─────────────────────────────────────────────────────

class IncidentFilters(BaseModel):
    district: Optional[str] = None
    status: Optional[IncidentStatus] = None
    incidentType: Optional[IncidentType] = None
    severity: Optional[SeverityBand] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    sort: str = "severity"
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)
