"""
ResQAI – AI API Router
Trigger analysis, get results, cluster analysis, situation summary.
"""
from fastapi import APIRouter, Depends, status

from app.core.responses import success_response
from app.middleware.auth import (
    AuthenticatedUser,
    get_current_user,
    require_roles,
)
from app.models.enums import UserRole
from app.services.incident_service import IncidentService

router = APIRouter(prefix="/ai", tags=["AI"])

_AUTHORITY_ROLES = (
    UserRole.AUTHORITY, UserRole.DISTRICT_OFFICER,
    UserRole.STATE_OFFICER, UserRole.ADMIN,
)


@router.post("/analyze", status_code=status.HTTP_202_ACCEPTED)
async def trigger_analysis(
    request_body: dict,
    current_user: AuthenticatedUser = Depends(
        require_roles(UserRole.ADMIN)
    ),
):
    """Manually trigger AI analysis for an incident (admin / re-process)."""
    incident_id = request_body.get("incidentId", "")
    if not incident_id:
        from app.core.exceptions import ValidationError
        raise ValidationError(message="incidentId is required.")

    from app.firebase.client import get_firestore_client, Collections
    from app.core.exceptions import IncidentNotFoundError
    import threading

    db = get_firestore_client()
    doc = db.collection(Collections.INCIDENTS).document(incident_id).get()
    if not doc.exists:
        raise IncidentNotFoundError()

    data_dict = doc.to_dict()
    svc = IncidentService()

    # Re-trigger AI in background
    from app.models.incident import IncidentCreate, IncidentLocation, Coordinates
    coords = data_dict["location"]["coordinates"]
    loc = IncidentLocation(
        address=data_dict["location"]["address"],
        district=data_dict["location"]["district"],
        state=data_dict["location"]["state"],
        pincode=data_dict["location"].get("pincode"),
        coordinates=Coordinates(
            latitude=coords["latitude"],
            longitude=coords["longitude"],
        ),
    )
    create_data = IncidentCreate(
        title=data_dict["title"],
        description=data_dict["description"],
        incidentType=data_dict["incidentType"],
        urgencyLevel=data_dict["urgencyLevel"],
        affectedPeople=data_dict["affectedPeople"],
        location=loc,
    )
    t = threading.Thread(
        target=svc._run_ai_analysis,
        args=(incident_id, data_dict, create_data),
        daemon=True,
    )
    t.start()

    return success_response(None, "AI analysis queued.")


@router.get("/analysis/{incident_id}")
async def get_ai_analysis(
    incident_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Retrieve AI analysis result for an incident."""
    from app.firebase.client import get_firestore_client, Collections
    from app.core.exceptions import IncidentNotFoundError

    db = get_firestore_client()
    doc = db.collection(Collections.INCIDENTS).document(incident_id).get()
    if not doc.exists:
        raise IncidentNotFoundError()

    ai_analysis = doc.to_dict().get("aiAnalysis")
    return success_response(ai_analysis)


@router.get("/summary/{incident_id}")
async def get_situation_summary(
    incident_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Get or regenerate AI situation summary for an incident."""
    from app.firebase.client import get_firestore_client, Collections
    from app.core.exceptions import IncidentNotFoundError
    from datetime import datetime, timezone
    from app.gemini.service import get_gemini_service

    db = get_firestore_client()
    doc = db.collection(Collections.INCIDENTS).document(incident_id).get()
    if not doc.exists:
        raise IncidentNotFoundError()

    data = doc.to_dict()
    ai = data.get("aiAnalysis") or {}
    assigned = [r.get("resourceName", "") for r in (data.get("assignedTo") or {}).get("resources", [])]

    gemini = get_gemini_service()
    summary = gemini.generate_situation_summary(
        classified_type=ai.get("classifiedType", data.get("incidentType", "OTHER")),
        severity_score=float(ai.get("severityScore") or 5),
        severity_band=ai.get("severityBand", "MEDIUM"),
        affected_people=data.get("affectedPeople", 0),
        district=data["location"]["district"],
        state=data["location"]["state"],
        status=data.get("status", "SUBMITTED"),
        assigned_resources=assigned,
        description=data.get("description", ""),
    )

    return success_response({
        "summary": summary,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
    })


@router.post("/cluster-analysis")
async def cluster_analysis(
    request_body: dict,
    current_user: AuthenticatedUser = Depends(
        require_roles(*_AUTHORITY_ROLES)
    ),
):
    """Detect incident clusters in a district within a time window."""
    district = request_body.get("district", current_user.district or "")
    window_hours = int(request_body.get("windowHours", 2))

    from app.firebase.client import get_firestore_client, Collections
    from datetime import datetime, timedelta, timezone
    from app.utils.geo import haversine_distance
    import math

    db = get_firestore_client()
    since = datetime.now(timezone.utc) - timedelta(hours=window_hours)

    docs = list(
        db.collection(Collections.INCIDENTS)
        .where("location.district", "==", district)
        .stream()
    )
    incidents = []
    for d in docs:
        dd = d.to_dict()
        created = dd.get("createdAt")
        if hasattr(created, "ToDatetime"):
            created = created.ToDatetime().replace(tzinfo=timezone.utc)
        if isinstance(created, datetime) and created >= since:
            incidents.append(dd)

    # Simple density-based clustering: group within 5 km
    clusters = []
    visited = set()

    for i, inc in enumerate(incidents):
        if i in visited:
            continue
        group = [inc]
        visited.add(i)
        coords_i = inc["location"]["coordinates"]
        for j, other in enumerate(incidents):
            if j in visited or j == i:
                continue
            coords_j = other["location"]["coordinates"]
            if haversine_distance(
                coords_i["latitude"], coords_i["longitude"],
                coords_j["latitude"], coords_j["longitude"],
            ) <= 5.0:
                group.append(other)
                visited.add(j)

        if len(group) >= 2:
            avg_lat = sum(g["location"]["coordinates"]["latitude"] for g in group) / len(group)
            avg_lng = sum(g["location"]["coordinates"]["longitude"] for g in group) / len(group)
            types = [g.get("incidentType", "OTHER") for g in group]
            dominant = max(set(types), key=types.count)
            severities = [
                float((g.get("aiAnalysis") or {}).get("severityScore") or 5)
                for g in group
            ]
            clusters.append({
                "center": {"latitude": avg_lat, "longitude": avg_lng},
                "incidentCount": len(group),
                "dominantType": dominant,
                "avgSeverity": round(sum(severities) / len(severities), 1),
                "affectedArea": "~5 km radius",
            })

    return success_response({
        "clustersDetected": len(clusters),
        "clusters": clusters,
        "district": district,
        "windowHours": window_hours,
    })
