"""
ResQAI – Incidents API Router
Full incident lifecycle: create, read, update, assign, escalate, comment, SOS, AI feedback.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, UploadFile, File, status
from fastapi import Form
from typing import List

from app.core.responses import success_response, created_response, paginated_response
from app.middleware.auth import (
    AuthenticatedUser,
    get_current_user,
    get_optional_user,
    require_roles,
)
from app.models.enums import (
    IncidentStatus, IncidentType, SeverityBand, UserRole
)
from app.models.incident import (
    AIFeedbackRequest,
    IncidentAssign,
    IncidentComment,
    IncidentCreate,
    IncidentEscalate,
    IncidentFilters,
    IncidentStatusUpdate,
    SOSCreate,
)
from app.services.incident_service import IncidentService

router = APIRouter(prefix="/incidents", tags=["Incidents"])

_AUTHORITY_ROLES = (
    UserRole.AUTHORITY, UserRole.DISTRICT_OFFICER,
    UserRole.STATE_OFFICER, UserRole.ADMIN,
)


def _svc() -> IncidentService:
    return IncidentService()


# ── SOS (before /{id} to avoid path collision) ─────────────────────────────

@router.post("/sos", status_code=status.HTTP_201_CREATED)
async def submit_sos(
    data: SOSCreate,
    current_user: Optional[AuthenticatedUser] = Depends(get_optional_user),
    svc: IncidentService = Depends(_svc),
):
    """Submit an SOS emergency — highest priority, no AI wait."""
    result = svc.create_sos(data, current_user)
    return created_response(result, "SOS received. Emergency teams alerted.")


# ── Priority queue ────────────────────────────────────────────────────────────

@router.get("/priority")
async def get_priority_queue(
    current_user: AuthenticatedUser = Depends(
        require_roles(*_AUTHORITY_ROLES)
    ),
    svc: IncidentService = Depends(_svc),
):
    """Active incidents sorted by AI severity score (highest first)."""
    incidents = svc.get_priority_queue(current_user)
    return success_response(incidents)


# ── My incidents ──────────────────────────────────────────────────────────────

@router.get("/my")
async def get_my_incidents(
    current_user: AuthenticatedUser = Depends(get_current_user),
    svc: IncidentService = Depends(_svc),
):
    """Return all incidents reported by the current user."""
    incidents = svc.get_my_incidents(current_user)
    return success_response(incidents)


# ── Create ────────────────────────────────────────────────────────────────────

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_incident(
    data: IncidentCreate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    svc: IncidentService = Depends(_svc),
):
    """Submit a new incident report. AI analysis triggered asynchronously."""
    result = svc.create_incident(data, current_user)
    return created_response(result)


# ── List ──────────────────────────────────────────────────────────────────────

@router.get("")
async def list_incidents(
    district: Optional[str] = Query(None),
    status: Optional[IncidentStatus] = Query(None),
    incident_type: Optional[IncidentType] = Query(None, alias="type"),
    severity: Optional[SeverityBand] = Query(None),
    sort: str = Query("severity"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: AuthenticatedUser = Depends(get_current_user),
    svc: IncidentService = Depends(_svc),
):
    """List incidents. Results scoped by role automatically."""
    filters = IncidentFilters(
        district=district,
        status=status,
        incidentType=incident_type,
        severity=severity,
        sort=sort,
        page=page,
        limit=limit,
    )
    result = svc.get_incidents(filters, current_user)
    return paginated_response(
        result["incidents"], result["total"], result["page"], result["limit"]
    )


# ── Detail ────────────────────────────────────────────────────────────────────

@router.get("/{incident_id}")
async def get_incident(
    incident_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
    svc: IncidentService = Depends(_svc),
):
    """Get full incident details including AI analysis."""
    incident = svc.get_incident_by_id(incident_id, current_user)
    return success_response(incident)


# ── Status update ─────────────────────────────────────────────────────────────

@router.put("/{incident_id}/status")
async def update_status(
    incident_id: str,
    data: IncidentStatusUpdate,
    current_user: AuthenticatedUser = Depends(
        require_roles(*_AUTHORITY_ROLES)
    ),
    svc: IncidentService = Depends(_svc),
):
    """Update incident operational status."""
    result = svc.update_status(incident_id, data, current_user)
    return success_response(result)


# ── Assign ────────────────────────────────────────────────────────────────────

@router.put("/{incident_id}/assign")
async def assign_incident(
    incident_id: str,
    data: IncidentAssign,
    current_user: AuthenticatedUser = Depends(
        require_roles(*_AUTHORITY_ROLES)
    ),
    svc: IncidentService = Depends(_svc),
):
    """Assign authority and resources to an incident."""
    result = svc.assign_incident(incident_id, data, current_user)
    return success_response(result)


# ── Escalate ──────────────────────────────────────────────────────────────────

@router.post("/{incident_id}/escalate")
async def escalate_incident(
    incident_id: str,
    data: IncidentEscalate,
    current_user: AuthenticatedUser = Depends(
        require_roles(*_AUTHORITY_ROLES)
    ),
    svc: IncidentService = Depends(_svc),
):
    """Escalate incident to higher authority level."""
    result = svc.escalate_incident(incident_id, data, current_user)
    return success_response(result)


# ── Comments ──────────────────────────────────────────────────────────────────

@router.post("/{incident_id}/comments", status_code=status.HTTP_201_CREATED)
async def add_comment(
    incident_id: str,
    data: IncidentComment,
    current_user: AuthenticatedUser = Depends(get_current_user),
    svc: IncidentService = Depends(_svc),
):
    """Add a comment or internal note to an incident."""
    comment = svc.add_comment(incident_id, data, current_user)
    return created_response(comment)


@router.get("/{incident_id}/comments")
async def get_comments(
    incident_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
    svc: IncidentService = Depends(_svc),
):
    """Get all comments on an incident (citizens see public comments only)."""
    comments = svc.get_comments(incident_id, current_user)
    return success_response(comments)


# ── AI Feedback ───────────────────────────────────────────────────────────────

@router.post("/{incident_id}/ai-feedback")
async def submit_ai_feedback(
    incident_id: str,
    data: AIFeedbackRequest,
    current_user: AuthenticatedUser = Depends(
        require_roles(*_AUTHORITY_ROLES)
    ),
    svc: IncidentService = Depends(_svc),
):
    """Submit feedback on the AI recommendation for an incident."""
    from datetime import datetime, timezone
    from app.firebase.client import get_firestore_client, Collections
    db = get_firestore_client()
    doc_ref = db.collection(Collections.INCIDENTS).document(incident_id)
    doc = doc_ref.get()
    if not doc.exists:
        from app.core.exceptions import IncidentNotFoundError
        raise IncidentNotFoundError()

    doc_ref.update({
        "aiAnalysis.authorityFeedback": data.feedback.value,
        "aiAnalysis.feedbackNote": data.comment,
        "updatedAt": datetime.now(timezone.utc),
    })
    return success_response(None, "Feedback recorded.")
