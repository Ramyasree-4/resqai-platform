"""
ResQAI – Analytics & Report Pydantic Models
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from app.models.enums import AnalyticsPeriod, AnalyticsScope, ReportType, ReportStatus


class IncidentTypeBreakdown(BaseModel):
    FLOOD: int = 0
    CYCLONE: int = 0
    EARTHQUAKE: int = 0
    LANDSLIDE: int = 0
    FIRE: int = 0
    MEDICAL: int = 0
    INDUSTRIAL: int = 0
    DROUGHT: int = 0
    CIVIL_UNREST: int = 0
    OTHER: int = 0


class SeverityBreakdown(BaseModel):
    LOW: int = 0
    MEDIUM: int = 0
    HIGH: int = 0
    CRITICAL: int = 0


class StatusBreakdown(BaseModel):
    SUBMITTED: int = 0
    TRIAGED: int = 0
    ASSIGNED: int = 0
    IN_PROGRESS: int = 0
    RESOLVED: int = 0


class IncidentMetrics(BaseModel):
    total: int = 0
    new: int = 0
    resolved: int = 0
    active: int = 0
    byType: IncidentTypeBreakdown = IncidentTypeBreakdown()
    bySeverity: SeverityBreakdown = SeverityBreakdown()
    byStatus: StatusBreakdown = StatusBreakdown()


class ResponseMetrics(BaseModel):
    avgResponseTimeMinutes: float = 0.0
    medianResponseTimeMinutes: float = 0.0
    p95ResponseTimeMinutes: float = 0.0
    avgResolutionTimeHours: float = 0.0
    slaBreachCount: int = 0
    escalationCount: int = 0


class ResourceMetrics(BaseModel):
    totalAvailable: int = 0
    totalDeployed: int = 0
    utilizationRate: float = 0.0
    deploymentCount: int = 0


class AIMetrics(BaseModel):
    incidentsProcessed: int = 0
    avgProcessingTimeMs: float = 0.0
    recommendationsAccepted: int = 0
    recommendationsOverridden: int = 0
    duplicatesDetected: int = 0
    fallbackActivations: int = 0


class UserMetrics(BaseModel):
    activeUsers: int = 0
    newRegistrations: int = 0
    reportingUsers: int = 0


class AnalyticsRecord(BaseModel):
    analyticsId: str
    period: AnalyticsPeriod
    date: str
    hour: Optional[int] = None
    scope: AnalyticsScope
    district: Optional[str] = None
    state: Optional[str] = None
    incidents: IncidentMetrics = IncidentMetrics()
    response: ResponseMetrics = ResponseMetrics()
    resources: ResourceMetrics = ResourceMetrics()
    ai: AIMetrics = AIMetrics()
    users: UserMetrics = UserMetrics()
    computedAt: Optional[datetime] = None
    isComplete: bool = False


# ── Dashboard Stats ───────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    activeIncidents: int = 0
    criticalIncidents: int = 0
    resolvedToday: int = 0
    avgResponseTimeMinutes: float = 0.0
    resourcesDeployed: int = 0
    resourcesAvailable: int = 0
    pendingAssignment: int = 0
    sosReceived: int = 0
    aiAccuracyRate: float = 0.0


class MapIncidentPoint(BaseModel):
    incidentId: str
    title: str
    incidentType: str
    status: str
    latitude: float
    longitude: float
    severityBand: Optional[str] = None
    severityScore: Optional[float] = None


class MapResourcePoint(BaseModel):
    resourceId: str
    name: str
    type: str
    status: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class HeatmapPoint(BaseModel):
    lat: float
    lng: float
    weight: float


class MapData(BaseModel):
    incidents: List[MapIncidentPoint] = []
    resources: List[MapResourcePoint] = []
    heatmapData: List[HeatmapPoint] = []


class IncidentTrendDataset(BaseModel):
    total: List[int] = []
    critical: List[int] = []
    resolved: List[int] = []


class IncidentTrendData(BaseModel):
    labels: List[str] = []
    datasets: IncidentTrendDataset = IncidentTrendDataset()


# ── Reports ───────────────────────────────────────────────────────────────────

class ReportSection(BaseModel):
    heading: str
    content: str
    data: Optional[Any] = None


class ReportCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    type: ReportType
    district: Optional[str] = None
    state: Optional[str] = None
    fromDate: datetime
    toDate: datetime
    format: str = Field(default="PDF", pattern=r"^(PDF|CSV|BOTH)$")
    includeCharts: bool = True


class ReportResponse(BaseModel):
    reportId: str
    title: str
    type: ReportType
    status: ReportStatus
    generatedBy: str
    district: Optional[str] = None
    state: Optional[str] = None
    fromDate: Optional[datetime] = None
    toDate: Optional[datetime] = None
    summary: Optional[str] = None
    sections: List[ReportSection] = []
    pdfUrl: Optional[str] = None
    csvUrl: Optional[str] = None
    generatedAt: Optional[datetime] = None
    createdAt: Optional[datetime] = None
    expiresAt: Optional[datetime] = None


class AnalyticsExportRequest(BaseModel):
    format: str = Field(default="PDF", pattern=r"^(PDF|CSV|BOTH)$")
    from_date: datetime
    to_date: datetime
    district: Optional[str] = None
    state: Optional[str] = None
    includeCharts: bool = True
