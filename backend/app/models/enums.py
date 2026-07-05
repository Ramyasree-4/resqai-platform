"""
ResQAI – Shared Enumerations
All enum values match the Firestore schema exactly.
"""
from enum import Enum


class UserRole(str, Enum):
    CITIZEN = "CITIZEN"
    AUTHORITY = "AUTHORITY"
    NGO = "NGO"
    VOLUNTEER = "VOLUNTEER"
    DISTRICT_OFFICER = "DISTRICT_OFFICER"
    STATE_OFFICER = "STATE_OFFICER"
    ADMIN = "ADMIN"


class IncidentType(str, Enum):
    FLOOD = "FLOOD"
    CYCLONE = "CYCLONE"
    EARTHQUAKE = "EARTHQUAKE"
    LANDSLIDE = "LANDSLIDE"
    FIRE = "FIRE"
    MEDICAL = "MEDICAL"
    INDUSTRIAL = "INDUSTRIAL"
    DROUGHT = "DROUGHT"
    CIVIL_UNREST = "CIVIL_UNREST"
    OTHER = "OTHER"


class IncidentStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    AI_PROCESSING = "AI_PROCESSING"
    TRIAGED = "TRIAGED"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    ARCHIVED = "ARCHIVED"


class UrgencyLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SeverityBand(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ResourceType(str, Enum):
    RESCUE_TEAM = "RESCUE_TEAM"
    AMBULANCE = "AMBULANCE"
    FIRE_TRUCK = "FIRE_TRUCK"
    RESCUE_BOAT = "RESCUE_BOAT"
    HELICOPTER = "HELICOPTER"
    POLICE_UNIT = "POLICE_UNIT"
    MEDICAL_UNIT = "MEDICAL_UNIT"
    NGO_UNIT = "NGO_UNIT"
    SHELTER = "SHELTER"
    HOSPITAL = "HOSPITAL"
    RELIEF_CAMP = "RELIEF_CAMP"


class ResourceStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    DEPLOYED = "DEPLOYED"
    MAINTENANCE = "MAINTENANCE"
    UNAVAILABLE = "UNAVAILABLE"


class ResourceAssignmentStatus(str, Enum):
    DISPATCHED = "DISPATCHED"
    EN_ROUTE = "EN_ROUTE"
    ON_SCENE = "ON_SCENE"
    RETURNING = "RETURNING"


class NotificationType(str, Enum):
    INCIDENT_STATUS = "INCIDENT_STATUS"
    NEW_INCIDENT = "NEW_INCIDENT"
    ASSIGNMENT = "ASSIGNMENT"
    ESCALATION = "ESCALATION"
    BROADCAST = "BROADCAST"
    RESOURCE_UPDATE = "RESOURCE_UPDATE"
    SYSTEM = "SYSTEM"
    CLUSTER_ALERT = "CLUSTER_ALERT"


class NotificationPriority(str, Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    URGENT = "URGENT"


class IncidentSource(str, Enum):
    WEB = "WEB"
    MOBILE = "MOBILE"
    SMS = "SMS"
    API = "API"


class AnalyticsPeriod(str, Enum):
    HOURLY = "HOURLY"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"


class AnalyticsScope(str, Enum):
    NATIONAL = "NATIONAL"
    STATE = "STATE"
    DISTRICT = "DISTRICT"


class ReportType(str, Enum):
    SITUATION = "SITUATION"
    DAILY_SUMMARY = "DAILY_SUMMARY"
    ANALYTICS = "ANALYTICS"
    AUDIT = "AUDIT"


class ReportStatus(str, Enum):
    GENERATING = "GENERATING"
    READY = "READY"
    FAILED = "FAILED"


class FeedbackTarget(str, Enum):
    AI_ANALYSIS = "AI_ANALYSIS"
    PLATFORM = "PLATFORM"
    INCIDENT = "INCIDENT"


class AiFeedback(str, Enum):
    ACCEPTED = "ACCEPTED"
    OVERRIDDEN = "OVERRIDDEN"


class ResourceUrgency(str, Enum):
    IMMEDIATE = "IMMEDIATE"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class LocationMethod(str, Enum):
    GPS = "GPS"
    MANUAL = "MANUAL"
    IP = "IP"


class ResolutionOutcome(str, Enum):
    RESCUED = "RESCUED"
    FALSE_ALARM = "FALSE_ALARM"
    REFERRED = "REFERRED"
    DECEASED = "DECEASED"
