"""
ResQAI – Incident Service
Full lifecycle management: create, triage, assign, escalate, resolve.
Includes AI analysis trigger and duplicate detection.
"""
import threading
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.core.exceptions import (
    FirebaseError,
    IncidentNotFoundError,
    PermissionDeniedError,
)
from app.core.logging import get_logger
from app.firebase.client import Collections, get_firestore_client
from app.ai.ai_manager import get_ai_manager
from app.models.enums import (
    IncidentSource,
    IncidentStatus,
    SeverityBand,
    UrgencyLevel,
    UserRole,
)
from app.models.incident import (
    IncidentAssign,
    IncidentComment,
    IncidentCreate,
    IncidentEscalate,
    IncidentFilters,
    IncidentStatusUpdate,
    SOSCreate,
)
from app.middleware.auth import AuthenticatedUser
from app.utils.geo import encode_geohash
from app.utils.ids import generate_incident_id, generate_uuid
from app.utils.priority import compute_priority_score, get_sla_minutes

logger = get_logger(__name__)


class IncidentService:

    def __init__(self):
        self._db = get_firestore_client()

    # ── Create ────────────────────────────────────────────────────────────

    def create_incident(
        self,
        data: IncidentCreate,
        current_user: AuthenticatedUser,
    ) -> Dict[str, Any]:
        """
        Submit a new incident report.
        Saves to Firestore with SUBMITTED status, then triggers AI in background.
        """
        incident_id = generate_incident_id()
        now = datetime.now(timezone.utc)

        # Geohash for proximity queries
        geohash = encode_geohash(
            data.location.coordinates.latitude,
            data.location.coordinates.longitude,
        )

        doc = {
            "incidentId": incident_id,
            "reportedBy": current_user.uid,
            "reporterName": current_user._raw.get("name", "Anonymous") if not data.isAnonymous else "Anonymous",
            "reporterPhone": None,
            "isAnonymous": data.isAnonymous,
            "title": data.title,
            "description": data.description,
            "incidentType": data.incidentType.value,
            "urgencyLevel": data.urgencyLevel.value,
            "affectedPeople": data.affectedPeople,
            "fatalities": data.fatalities or 0,
            "injuries": data.injuries or 0,
            "location": {
                "address": data.location.address,
                "district": data.location.district,
                "state": data.location.state,
                "pincode": data.location.pincode,
                "coordinates": {
                    "latitude": data.location.coordinates.latitude,
                    "longitude": data.location.coordinates.longitude,
                },
                "geohash": geohash,
                "accuracy": data.location.accuracy,
                "locationMethod": data.location.locationMethod.value,
            },
            "mediaFiles": [],
            "status": IncidentStatus.SUBMITTED.value,
            "aiAnalysis": None,
            "assignedTo": {
                "authorityId": None,
                "authorityName": None,
                "assignedAt": None,
                "resources": [],
            },
            "escalation": {
                "isEscalated": False,
                "escalatedAt": None,
                "escalatedBy": None,
                "escalatedTo": None,
                "escalationReason": None,
                "escalationCount": 0,
            },
            "linkedIncidents": [],
            "eventId": None,
            "resolution": {
                "resolvedAt": None,
                "resolvedBy": None,
                "resolutionNote": None,
                "outcome": None,
            },
            "source": data.source.value,
            "version": 1,
            "responseTimeMinutes": None,
            "createdAt": now,
            "updatedAt": now,
        }

        try:
            doc_ref = self._db.collection(Collections.INCIDENTS).document()
            doc_ref.set(doc)
            firestore_id = doc_ref.id
            doc["_firestoreId"] = firestore_id
        except Exception as e:
            raise FirebaseError(message=f"Failed to save incident: {str(e)}")

        # Log status history
        self._add_status_history(
            firestore_id,
            from_status=None,
            to_status=IncidentStatus.SUBMITTED.value,
            changed_by=current_user.uid,
            note="Incident submitted",
        )

        # Trigger AI processing in background thread (non-blocking)
        thread = threading.Thread(
            target=self._run_ai_analysis,
            args=(firestore_id, doc, data),
            daemon=True,
        )
        thread.start()

        sla = get_sla_minutes(data.urgencyLevel.value)
        return {
            "incidentId": incident_id,
            "firestoreId": firestore_id,
            "status": IncidentStatus.SUBMITTED.value,
            "message": "Report received. AI is analyzing your report.",
            "estimatedResponseTime": f"{sla}-{sla + 15} minutes",
            "trackingUrl": f"https://app.resqai.in/track/{incident_id}",
        }

    def create_sos(
        self,
        data: SOSCreate,
        current_user: Optional[AuthenticatedUser],
    ) -> Dict[str, Any]:
        """
        SOS fast-path: creates CRITICAL incident immediately.
        No AI wait — dispatches nearest resource right away.
        """
        incident_id = generate_incident_id()
        now = datetime.now(timezone.utc)
        uid = current_user.uid if current_user else "anonymous"
        geohash = encode_geohash(
            data.coordinates.latitude,
            data.coordinates.longitude,
        )
        doc = {
            "incidentId": incident_id,
            "reportedBy": uid,
            "reporterName": "SOS",
            "reporterPhone": data.phoneNumber,
            "isAnonymous": current_user is None,
            "title": "🆘 SOS Emergency",
            "description": data.description or "SOS emergency activated.",
            "incidentType": "OTHER",
            "urgencyLevel": UrgencyLevel.CRITICAL.value,
            "affectedPeople": 1,
            "fatalities": 0,
            "injuries": 0,
            "location": {
                "address": "SOS Location",
                "district": "Unknown",
                "state": "Unknown",
                "pincode": None,
                "coordinates": {
                    "latitude": data.coordinates.latitude,
                    "longitude": data.coordinates.longitude,
                },
                "geohash": geohash,
                "accuracy": None,
                "locationMethod": "GPS",
            },
            "mediaFiles": [],
            "status": IncidentStatus.SUBMITTED.value,
            "isSOS": True,
            "aiAnalysis": {
                "analysisId": generate_uuid(),
                "severityScore": 10,
                "severityBand": SeverityBand.CRITICAL.value,
                "priorityScore": 1.0,
                "situationSummary": "SOS emergency broadcast received.",
                "reasoning": ["SOS button activated — maximum priority assigned"],
                "resourceRecommendations": [
                    {"resourceType": "RESCUE_TEAM", "quantity": 1, "urgency": "IMMEDIATE", "reason": "SOS response"}
                ],
                "fallbackUsed": False,
            },
            "assignedTo": {"authorityId": None, "authorityName": None, "assignedAt": None, "resources": []},
            "escalation": {"isEscalated": False, "escalationCount": 0},
            "linkedIncidents": [],
            "resolution": {"resolvedAt": None},
            "source": IncidentSource.MOBILE.value,
            "version": 1,
            "createdAt": now,
            "updatedAt": now,
        }

        doc_ref = self._db.collection(Collections.INCIDENTS).document()
        doc_ref.set(doc)
        firestore_id = doc_ref.id

        # Find nearest available resource (best-effort)
        nearest_unit = self._find_nearest_resource(
            data.coordinates.latitude,
            data.coordinates.longitude,
        )

        logger.info("SOS incident created", incident_id=incident_id, uid=uid)
        return {
            "incidentId": incident_id,
            "firestoreId": firestore_id,
            "message": "SOS received. Emergency teams alerted.",
            "nearestUnit": nearest_unit,
        }

    # ── Read ──────────────────────────────────────────────────────────────

    def get_incidents(
        self,
        filters: IncidentFilters,
        current_user: AuthenticatedUser,
    ) -> Dict[str, Any]:
        """Get incidents with role-scoped filtering."""
        query = self._db.collection(Collections.INCIDENTS)

        # Role-based data scoping
        if current_user.role == UserRole.CITIZEN:
            query = query.where("reportedBy", "==", current_user.uid)
        elif current_user.role in (
            UserRole.AUTHORITY, UserRole.DISTRICT_OFFICER, UserRole.NGO, UserRole.VOLUNTEER
        ):
            query = query.where("location.district", "==", current_user.district)
        elif current_user.role == UserRole.STATE_OFFICER:
            query = query.where("location.state", "==", current_user.state)
        # ADMIN: no restriction

        # Apply additional filters
        if filters.district and current_user.is_admin:
            query = query.where("location.district", "==", filters.district)
        if filters.status:
            query = query.where("status", "==", filters.status.value)
        if filters.incidentType:
            query = query.where("incidentType", "==", filters.incidentType.value)

        # Exclude archived unless specifically requested
        docs = list(query.stream())
        incidents = [d.to_dict() | {"_firestoreId": d.id} for d in docs]

        # Severity filter (post-query — Firestore doesn't support nested field inequality)
        if filters.severity:
            incidents = [
                i for i in incidents
                if i.get("aiAnalysis", {}) and
                   i["aiAnalysis"].get("severityBand") == filters.severity.value
            ]

        # Date filters
        if filters.from_date:
            incidents = [
                i for i in incidents
                if i.get("createdAt") and self._ts(i["createdAt"]) >= filters.from_date
            ]
        if filters.to_date:
            incidents = [
                i for i in incidents
                if i.get("createdAt") and self._ts(i["createdAt"]) <= filters.to_date
            ]

        # Sort
        if filters.sort == "severity":
            incidents.sort(
                key=lambda i: (i.get("aiAnalysis") or {}).get("severityScore", 0),
                reverse=True,
            )
        else:
            incidents.sort(
                key=lambda i: self._ts(i.get("createdAt")),
                reverse=True,
            )

        total = len(incidents)
        start = (filters.page - 1) * filters.limit
        page_items = incidents[start: start + filters.limit]

        return {"incidents": page_items, "total": total, "page": filters.page, "limit": filters.limit}

    def get_incident_by_id(
        self,
        firestore_id: str,
        current_user: AuthenticatedUser,
    ) -> Dict[str, Any]:
        doc = self._db.collection(Collections.INCIDENTS).document(firestore_id).get()
        if not doc.exists:
            raise IncidentNotFoundError()

        data = doc.to_dict()
        data["_firestoreId"] = doc.id

        # Access control
        if current_user.role == UserRole.CITIZEN and data.get("reportedBy") != current_user.uid:
            raise PermissionDeniedError()

        return data

    def get_my_incidents(self, current_user: AuthenticatedUser) -> List[Dict[str, Any]]:
        docs = (
            self._db.collection(Collections.INCIDENTS)
            .where("reportedBy", "==", current_user.uid)
            .order_by("createdAt", direction="DESCENDING")
            .limit(50)
            .stream()
        )
        return [d.to_dict() | {"_firestoreId": d.id} for d in docs]

    def get_priority_queue(self, current_user: AuthenticatedUser) -> List[Dict[str, Any]]:
        """Return active incidents sorted by AI priority score."""
        query = self._db.collection(Collections.INCIDENTS).where(
            "status", "not-in", [IncidentStatus.CLOSED.value, IncidentStatus.ARCHIVED.value]
        )
        if current_user.role not in (UserRole.STATE_OFFICER, UserRole.ADMIN):
            query = query.where("location.district", "==", current_user.district)

        docs = list(query.stream())
        incidents = [d.to_dict() | {"_firestoreId": d.id} for d in docs]

        # Sort by severity score (highest first)
        incidents.sort(
            key=lambda i: float((i.get("aiAnalysis") or {}).get("severityScore") or 0),
            reverse=True,
        )
        return incidents

    # ── Update ────────────────────────────────────────────────────────────

    def update_status(
        self,
        firestore_id: str,
        data: IncidentStatusUpdate,
        current_user: AuthenticatedUser,
    ) -> Dict[str, Any]:
        doc_ref = self._db.collection(Collections.INCIDENTS).document(firestore_id)
        doc = doc_ref.get()
        if not doc.exists:
            raise IncidentNotFoundError()

        old_data = doc.to_dict()
        old_status = old_data.get("status")
        now = datetime.now(timezone.utc)

        updates: Dict[str, Any] = {
            "status": data.status.value,
            "updatedAt": now,
        }

        # If resolving, capture resolution time
        if data.status == IncidentStatus.RESOLVED:
            created_at = self._ts(old_data.get("createdAt"))
            if created_at:
                diff = (now - created_at).total_seconds() / 60
                updates["responseTimeMinutes"] = round(diff, 1)
            updates["resolution.resolvedAt"] = now
            updates["resolution.resolvedBy"] = current_user.uid

        doc_ref.update(updates)

        # Log status history
        self._add_status_history(
            firestore_id, old_status, data.status.value, current_user.uid, data.note
        )

        logger.info(
            "Incident status updated",
            firestore_id=firestore_id,
            from_status=old_status,
            to_status=data.status.value,
        )
        return {"status": data.status.value, "updatedAt": now.isoformat()}

    def assign_incident(
        self,
        firestore_id: str,
        data: IncidentAssign,
        current_user: AuthenticatedUser,
    ) -> Dict[str, Any]:
        doc_ref = self._db.collection(Collections.INCIDENTS).document(firestore_id)
        if not doc_ref.get().exists:
            raise IncidentNotFoundError()

        now = datetime.now(timezone.utc)

        # Build assigned resources list
        assigned_resources = []
        for rid in data.resourceIds:
            res_doc = self._db.collection(Collections.RESOURCES).document(rid).get()
            if res_doc.exists:
                rd = res_doc.to_dict()
                assigned_resources.append({
                    "resourceId": rid,
                    "resourceName": rd.get("name", "Unknown"),
                    "resourceType": rd.get("type", "RESCUE_TEAM"),
                    "assignedAt": now,
                    "status": "DISPATCHED",
                })
                # Update resource status to DEPLOYED
                res_doc.reference.update({
                    "status": "DEPLOYED",
                    "statusUpdatedAt": now,
                    "currentAssignment.incidentId": firestore_id,
                    "currentAssignment.assignedAt": now,
                })

        # Load authority name
        auth_doc = self._db.collection(Collections.USERS).document(data.authorityId).get()
        authority_name = auth_doc.to_dict().get("displayName") if auth_doc.exists else "Unknown"

        doc_ref.update({
            "assignedTo.authorityId": data.authorityId,
            "assignedTo.authorityName": authority_name,
            "assignedTo.assignedAt": now,
            "assignedTo.resources": assigned_resources,
            "status": IncidentStatus.ASSIGNED.value,
            "updatedAt": now,
        })

        self._add_status_history(
            firestore_id, None, IncidentStatus.ASSIGNED.value,
            current_user.uid, f"Assigned to {authority_name}"
        )
        return {"status": IncidentStatus.ASSIGNED.value, "assignedAt": now.isoformat()}

    def escalate_incident(
        self,
        firestore_id: str,
        data: IncidentEscalate,
        current_user: AuthenticatedUser,
    ) -> Dict[str, Any]:
        doc_ref = self._db.collection(Collections.INCIDENTS).document(firestore_id)
        doc = doc_ref.get()
        if not doc.exists:
            raise IncidentNotFoundError()

        now = datetime.now(timezone.utc)
        current_count = (doc.to_dict().get("escalation") or {}).get("escalationCount", 0)

        doc_ref.update({
            "escalation.isEscalated": True,
            "escalation.escalatedAt": now,
            "escalation.escalatedBy": current_user.uid,
            "escalation.escalatedTo": data.escalateTo,
            "escalation.escalationReason": data.reason,
            "escalation.escalationCount": current_count + 1,
            "updatedAt": now,
        })
        logger.info("Incident escalated", firestore_id=firestore_id, to=data.escalateTo)
        return {"escalatedTo": data.escalateTo, "escalatedAt": now.isoformat()}

    # ── Comments ──────────────────────────────────────────────────────────

    def add_comment(
        self,
        firestore_id: str,
        data: IncidentComment,
        current_user: AuthenticatedUser,
    ) -> Dict[str, Any]:
        doc = self._db.collection(Collections.INCIDENTS).document(firestore_id).get()
        if not doc.exists:
            raise IncidentNotFoundError()

        now = datetime.now(timezone.utc)
        comment_id = generate_uuid()
        comment = {
            "commentId": comment_id,
            "authorId": current_user.uid,
            "authorName": current_user._raw.get("name", current_user.email),
            "authorRole": current_user.role.value,
            "content": data.content,
            "isInternal": data.isInternal,
            "createdAt": now,
            "updatedAt": now,
        }
        (
            self._db.collection(Collections.INCIDENTS)
            .document(firestore_id)
            .collection(Collections.INCIDENT_COMMENTS)
            .document(comment_id)
            .set(comment)
        )
        return comment

    def get_comments(
        self,
        firestore_id: str,
        current_user: AuthenticatedUser,
    ) -> List[Dict[str, Any]]:
        query = (
            self._db.collection(Collections.INCIDENTS)
            .document(firestore_id)
            .collection(Collections.INCIDENT_COMMENTS)
            .order_by("createdAt")
        )
        # Citizens can't see internal notes
        if current_user.role == UserRole.CITIZEN:
            query = query.where("isInternal", "==", False)

        return [d.to_dict() for d in query.stream()]

    # ── AI Processing ─────────────────────────────────────────────────────

    def _run_ai_analysis(
        self,
        firestore_id: str,
        doc: Dict[str, Any],
        data: IncidentCreate,
    ) -> None:
        """Background thread: run Gemini analysis and write results to Firestore."""
        doc_ref = self._db.collection(Collections.INCIDENTS).document(firestore_id)

        # Mark as AI_PROCESSING
        doc_ref.update({
            "status": IncidentStatus.AI_PROCESSING.value,
            "updatedAt": datetime.now(timezone.utc),
        })

        try:
            # Count active incidents in district for context
            active_count = (
                self._db.collection(Collections.INCIDENTS)
                .where("location.district", "==", data.location.district)
                .where("status", "not-in", [
                    IncidentStatus.CLOSED.value,
                    IncidentStatus.ARCHIVED.value,
                    IncidentStatus.RESOLVED.value,
                ])
                .count()
                .get()[0][0].value
            )
        except Exception:
            active_count = 0

        gemini = get_ai_manager()
        result = gemini.analyze_incident(
            incident_id=doc["incidentId"],
            incident_type=data.incidentType.value,
            description=data.description,
            affected_people=data.affectedPeople,
            district=data.location.district,
            state=data.location.state,
            latitude=data.location.coordinates.latitude,
            longitude=data.location.coordinates.longitude,
            urgency_level=data.urgencyLevel.value,
            fatalities=data.fatalities or 0,
            injuries=data.injuries or 0,
            active_district_incidents=active_count,
        )

        # Check for duplicates
        is_duplicate, dup_score, dup_ref = self._check_duplicates(
            firestore_id,
            data.description,
            doc["location"]["geohash"],
        )

        now = datetime.now(timezone.utc)
        analysis_id = generate_uuid()

        ai_analysis = {
            "analysisId": analysis_id,
            "processedAt": now,
            "modelVersion": settings_model_version(result),
            "classifiedType": result["classification"]["incidentType"],
            "classificationConfidence": result["classification"]["confidence"],
            "severityScore": result["severity"]["score"],
            "severityBand": result["severity"]["band"],
            "priorityScore": result["priority"]["score"],
            "priorityRank": None,  # Set by batch re-rank job
            "resourceRecommendations": result.get("resourceRecommendations", []),
            "situationSummary": result.get("situationSummary", ""),
            "reasoning": result.get("reasoning", []),
            "immediateActions": result.get("immediateActions", []),
            "risks": result.get("risks", []),
            "isDuplicate": is_duplicate,
            "duplicateOf": dup_ref,
            "duplicateScore": dup_score,
            "dataQuality": result.get("dataQuality", "MEDIUM"),
            "dataQualityNote": result.get("dataQualityNote", ""),
            "fallbackUsed": result.get("_fallbackUsed", False),
            "authorityFeedback": None,
            "feedbackNote": None,
        }

        doc_ref.update({
            "aiAnalysis": ai_analysis,
            "status": IncidentStatus.TRIAGED.value,
            "updatedAt": now,
        })

        self._add_status_history(
            firestore_id,
            IncidentStatus.AI_PROCESSING.value,
            IncidentStatus.TRIAGED.value,
            "SYSTEM",
            f"AI analysis complete. Severity: {ai_analysis['severityScore']}/10",
        )

        logger.info(
            "AI analysis complete",
            firestore_id=firestore_id,
            severity=ai_analysis["severityScore"],
            band=ai_analysis["severityBand"],
        )

    def _check_duplicates(
        self,
        current_id: str,
        description: str,
        geohash: str,
    ):
        """Check for duplicate incidents in the same geohash cell (last 2 hours)."""
        from datetime import timedelta
        two_hours_ago = datetime.now(timezone.utc) - timedelta(hours=2)

        geohash_prefix = geohash[:5]  # ~4.9 km radius
        try:
            candidates = (
                self._db.collection(Collections.INCIDENTS)
                .where("location.geohash", ">=", geohash_prefix)
                .where("location.geohash", "<=", geohash_prefix + "\uf8ff")
                .where("status", "not-in", [
                    IncidentStatus.CLOSED.value,
                    IncidentStatus.ARCHIVED.value,
                ])
                .limit(5)
                .stream()
            )
            gemini = get_ai_manager()
            for doc in candidates:
                if doc.id == current_id:
                    continue
                cdata = doc.to_dict()
                created = self._ts(cdata.get("createdAt"))
                if created and created < two_hours_ago:
                    continue
                is_same, confidence, _ = gemini.check_duplicate(
                    description, cdata.get("description", "")
                )
                combined = (0.4 * 0.8) + (0.6 * confidence)  # geo match = 0.8 assumed
                if combined > 0.85:
                    return True, combined, doc.id
                elif combined > 0.65:
                    return True, combined, doc.id  # flag for review
        except Exception as e:
            logger.warning("Duplicate check failed", error=str(e))

        return False, 0.0, None

    # ── Helpers ───────────────────────────────────────────────────────────

    def _add_status_history(
        self,
        firestore_id: str,
        from_status: Optional[str],
        to_status: str,
        changed_by: str,
        note: Optional[str] = None,
    ):
        entry = {
            "fromStatus": from_status,
            "toStatus": to_status,
            "changedBy": changed_by,
            "changedAt": datetime.now(timezone.utc),
            "note": note,
        }
        (
            self._db.collection(Collections.INCIDENTS)
            .document(firestore_id)
            .collection(Collections.INCIDENT_STATUS_HISTORY)
            .add(entry)
        )

    def _find_nearest_resource(self, lat: float, lng: float) -> str:
        """Find description of the nearest available resource."""
        from app.utils.geo import haversine_distance
        try:
            docs = (
                self._db.collection(Collections.RESOURCES)
                .where("status", "==", "AVAILABLE")
                .limit(20)
                .stream()
            )
            best = None
            best_dist = float("inf")
            for doc in docs:
                rd = doc.to_dict()
                loc = (rd.get("currentLocation") or rd.get("baseLocation") or {})
                coords = loc.get("coordinates", {})
                if not coords:
                    continue
                d = haversine_distance(lat, lng, coords["latitude"], coords["longitude"])
                if d < best_dist:
                    best_dist = d
                    best = rd
            if best:
                return f"{best['name']} — {best_dist:.1f} km away"
        except Exception:
            pass
        return "Emergency teams alerted"

    @staticmethod
    def _ts(value) -> Optional[datetime]:
        """Convert Firestore timestamp or datetime to tz-aware datetime."""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        if hasattr(value, "ToDatetime"):
            return value.ToDatetime().replace(tzinfo=timezone.utc)
        return None


def settings_model_version(result: Dict) -> str:
    """Extract the model version string from AI manager result."""
    # AIManager sets modelUsed directly
    if "modelUsed" in result:
        return result["modelUsed"]
    # Fallback for backward compat
    if result.get("_fallbackUsed"):
        return "rule-based-fallback"
    return "mistral-large-latest"
