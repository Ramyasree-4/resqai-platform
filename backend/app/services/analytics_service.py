"""
ResQAI – Analytics Service
Dashboard KPIs, map data, incident trends, and report generation.
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from app.core.logging import get_logger
from app.firebase.client import Collections, get_firestore_client
from app.middleware.auth import AuthenticatedUser
from app.models.enums import IncidentStatus, UserRole
from app.utils.ids import generate_report_id

logger = get_logger(__name__)


class AnalyticsService:

    def __init__(self):
        self._db = get_firestore_client()

    # ── Dashboard Stats ───────────────────────────────────────────────────

    def get_dashboard_stats(
        self,
        current_user: AuthenticatedUser,
        district: Optional[str] = None,
        state: Optional[str] = None,
        period: str = "today",
    ) -> Dict[str, Any]:
        """Compute KPI statistics for the authority dashboard."""

        # Determine time window
        now = datetime.now(timezone.utc)
        if period == "today":
            since = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "week":
            since = now - timedelta(days=7)
        elif period == "month":
            since = now - timedelta(days=30)
        else:
            since = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Base incident query
        q = self._db.collection(Collections.INCIDENTS)
        if current_user.role == UserRole.STATE_OFFICER:
            q = q.where("location.state", "==", current_user.state)
        elif not current_user.is_admin:
            scope_district = district or current_user.district
            if scope_district:
                q = q.where("location.district", "==", scope_district)

        all_incidents = [d.to_dict() for d in q.stream()]

        active = [
            i for i in all_incidents
            if i.get("status") not in (
                IncidentStatus.CLOSED.value,
                IncidentStatus.ARCHIVED.value,
                IncidentStatus.RESOLVED.value,
            )
        ]

        critical = [
            i for i in active
            if (i.get("aiAnalysis") or {}).get("severityBand") == "CRITICAL"
        ]

        resolved_today = [
            i for i in all_incidents
            if i.get("status") == IncidentStatus.RESOLVED.value
            and self._ts(i.get("updatedAt"), now) >= since
        ]

        pending_assignment = [
            i for i in active
            if i.get("status") in (
                IncidentStatus.SUBMITTED.value,
                IncidentStatus.TRIAGED.value,
            )
        ]

        sos_today = [
            i for i in all_incidents
            if i.get("isSOS") and self._ts(i.get("createdAt"), now) >= since
        ]

        # Resource stats
        res_query = self._db.collection(Collections.RESOURCES).where("isActive", "==", True)
        if not current_user.is_admin:
            scope_district = district or current_user.district
            if scope_district:
                res_query = res_query.where("district", "==", scope_district)

        resources = [d.to_dict() for d in res_query.stream()]
        deployed = [r for r in resources if r.get("status") == "DEPLOYED"]
        available = [r for r in resources if r.get("status") == "AVAILABLE"]

        # AI accuracy rate
        ai_accuracy = self._compute_ai_accuracy(all_incidents)

        # Avg response time
        response_times = [
            i["responseTimeMinutes"]
            for i in all_incidents
            if i.get("responseTimeMinutes") is not None
        ]
        avg_response = (
            round(sum(response_times) / len(response_times), 1)
            if response_times
            else 0.0
        )

        return {
            "activeIncidents": len(active),
            "criticalIncidents": len(critical),
            "resolvedToday": len(resolved_today),
            "avgResponseTimeMinutes": avg_response,
            "resourcesDeployed": len(deployed),
            "resourcesAvailable": len(available),
            "pendingAssignment": len(pending_assignment),
            "sosReceived": len(sos_today),
            "aiAccuracyRate": ai_accuracy,
        }

    # ── Map Data ──────────────────────────────────────────────────────────

    def get_map_data(
        self,
        current_user: AuthenticatedUser,
        district: Optional[str] = None,
        state: Optional[str] = None,
        include_resolved: bool = False,
    ) -> Dict[str, Any]:
        """Return incident and resource map markers + heatmap weights."""
        q = self._db.collection(Collections.INCIDENTS)
        if not include_resolved:
            q = q.where("status", "not-in", [
                IncidentStatus.CLOSED.value,
                IncidentStatus.ARCHIVED.value,
                IncidentStatus.RESOLVED.value,
            ])

        if not current_user.is_admin:
            scope = district or current_user.district
            if scope:
                q = q.where("location.district", "==", scope)

        incidents_raw = [d.to_dict() for d in q.stream()]
        incident_points = []
        heatmap = []

        for i in incidents_raw:
            loc = i.get("location", {})
            coords = loc.get("coordinates", {})
            if not coords.get("latitude"):
                continue
            ai = i.get("aiAnalysis") or {}
            severity = float(ai.get("severityScore") or 0)
            incident_points.append({
                "incidentId": i.get("incidentId"),
                "title": i.get("title"),
                "incidentType": i.get("incidentType"),
                "status": i.get("status"),
                "latitude": coords["latitude"],
                "longitude": coords["longitude"],
                "severityBand": ai.get("severityBand"),
                "severityScore": severity,
            })
            heatmap.append({
                "lat": coords["latitude"],
                "lng": coords["longitude"],
                "weight": round(severity / 10.0, 2),
            })

        # Resources
        res_q = self._db.collection(Collections.RESOURCES).where("isActive", "==", True)
        if not current_user.is_admin:
            scope = district or current_user.district
            if scope:
                res_q = res_q.where("district", "==", scope)

        resource_points = []
        for d in res_q.stream():
            rd = d.to_dict()
            loc = rd.get("currentLocation") or rd.get("baseLocation") or {}
            coords = (loc.get("coordinates") or {})
            resource_points.append({
                "resourceId": rd.get("resourceId"),
                "name": rd.get("name"),
                "type": rd.get("type"),
                "status": rd.get("status"),
                "latitude": coords.get("latitude"),
                "longitude": coords.get("longitude"),
            })

        return {
            "incidents": incident_points,
            "resources": resource_points,
            "heatmapData": heatmap,
        }

    # ── Incident Trend ────────────────────────────────────────────────────

    def get_incident_trend(
        self,
        current_user: AuthenticatedUser,
        district: Optional[str] = None,
        days: int = 7,
    ) -> Dict[str, Any]:
        """Return daily incident counts for the past N days."""
        now = datetime.now(timezone.utc)
        labels = []
        totals, criticals, resolveds = [], [], []

        for i in range(days - 1, -1, -1):
            day_start = (now - timedelta(days=i)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            day_end = day_start + timedelta(days=1)
            labels.append(day_start.strftime("%b %d"))

            q = self._db.collection(Collections.INCIDENTS)
            if not current_user.is_admin:
                scope = district or current_user.district
                if scope:
                    q = q.where("location.district", "==", scope)

            day_docs = [
                d.to_dict() for d in q.stream()
                if day_start <= self._ts(d.to_dict().get("createdAt"), now) < day_end
            ]

            totals.append(len(day_docs))
            criticals.append(sum(
                1 for d in day_docs
                if (d.get("aiAnalysis") or {}).get("severityBand") == "CRITICAL"
            ))
            resolveds.append(sum(
                1 for d in day_docs
                if d.get("status") == IncidentStatus.RESOLVED.value
            ))

        return {
            "labels": labels,
            "datasets": {
                "total": totals,
                "critical": criticals,
                "resolved": resolveds,
            },
        }

    # ── Analytics Summary ─────────────────────────────────────────────────

    def get_analytics_summary(
        self,
        current_user: AuthenticatedUser,
        district: Optional[str] = None,
        state: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        q = self._db.collection(Collections.INCIDENTS)
        if not current_user.is_admin:
            scope = district or current_user.district
            if scope:
                q = q.where("location.district", "==", scope)

        all_docs = [d.to_dict() for d in q.stream()]

        if from_date:
            all_docs = [d for d in all_docs if self._ts(d.get("createdAt"), datetime.now(timezone.utc)) >= from_date]
        if to_date:
            all_docs = [d for d in all_docs if self._ts(d.get("createdAt"), datetime.now(timezone.utc)) <= to_date]

        by_type: Dict[str, int] = {}
        by_severity: Dict[str, int] = {}
        by_status: Dict[str, int] = {}

        for d in all_docs:
            itype = d.get("incidentType", "OTHER")
            by_type[itype] = by_type.get(itype, 0) + 1
            band = (d.get("aiAnalysis") or {}).get("severityBand", "MEDIUM")
            by_severity[band] = by_severity.get(band, 0) + 1
            status = d.get("status", "SUBMITTED")
            by_status[status] = by_status.get(status, 0) + 1

        response_times = [
            d["responseTimeMinutes"] for d in all_docs if d.get("responseTimeMinutes")
        ]
        avg_rt = round(sum(response_times) / len(response_times), 1) if response_times else 0.0

        return {
            "total": len(all_docs),
            "byType": by_type,
            "bySeverity": by_severity,
            "byStatus": by_status,
            "avgResponseTimeMinutes": avg_rt,
            "aiAccuracyRate": self._compute_ai_accuracy(all_docs),
        }

    def get_response_time_analytics(
        self, current_user: AuthenticatedUser
    ) -> Dict[str, Any]:
        q = self._db.collection(Collections.INCIDENTS)
        if not current_user.is_admin:
            if current_user.district:
                q = q.where("location.district", "==", current_user.district)

        docs = [d.to_dict() for d in q.stream() if d.to_dict().get("responseTimeMinutes")]
        by_type: Dict[str, List[float]] = {}
        for d in docs:
            t = d.get("incidentType", "OTHER")
            rt = d["responseTimeMinutes"]
            by_type.setdefault(t, []).append(rt)

        return {
            "byType": {
                t: {"avg": round(sum(times) / len(times), 1), "count": len(times)}
                for t, times in by_type.items()
            }
        }

    def get_resource_utilization(self, current_user: AuthenticatedUser) -> Dict[str, Any]:
        q = self._db.collection(Collections.RESOURCES).where("isActive", "==", True)
        if not current_user.is_admin and current_user.district:
            q = q.where("district", "==", current_user.district)

        resources = [d.to_dict() for d in q.stream()]
        by_type: Dict[str, Dict[str, int]] = {}
        for r in resources:
            t = r.get("type", "UNKNOWN")
            s = r.get("status", "UNAVAILABLE")
            by_type.setdefault(t, {"AVAILABLE": 0, "DEPLOYED": 0, "MAINTENANCE": 0, "UNAVAILABLE": 0})
            by_type[t][s] = by_type[t].get(s, 0) + 1

        total = len(resources)
        deployed = sum(1 for r in resources if r.get("status") == "DEPLOYED")
        return {
            "totalResources": total,
            "deployed": deployed,
            "utilizationRate": round(deployed / total, 2) if total else 0.0,
            "byType": by_type,
        }

    # ── Admin Stats ───────────────────────────────────────────────────────

    def get_system_stats(self) -> Dict[str, Any]:
        users_count = self._db.collection(Collections.USERS).count().get()[0][0].value
        incidents_count = self._db.collection(Collections.INCIDENTS).count().get()[0][0].value
        resources_count = self._db.collection(Collections.RESOURCES).count().get()[0][0].value

        return {
            "totalUsers": users_count,
            "totalIncidents": incidents_count,
            "totalResources": resources_count,
            "systemHealth": "HEALTHY",
            "geminiApiUsage": {"requestsToday": 0, "costUSD": 0.0},  # Placeholder
        }

    # ── Report Creation ───────────────────────────────────────────────────

    def create_report(
        self,
        data: Any,
        current_user: AuthenticatedUser,
    ) -> Dict[str, Any]:
        """Queue a report for generation."""
        from datetime import timedelta as td
        report_id = generate_report_id()
        now = datetime.now(timezone.utc)

        doc = {
            "reportId": report_id,
            "title": data.title,
            "type": data.type.value,
            "status": "GENERATING",
            "generatedBy": current_user.uid,
            "district": data.district,
            "state": data.state,
            "fromDate": data.fromDate,
            "toDate": data.toDate,
            "summary": None,
            "sections": [],
            "pdfUrl": None,
            "csvUrl": None,
            "generatedAt": None,
            "createdAt": now,
            "expiresAt": now + td(days=90),
        }

        ref = self._db.collection(Collections.REPORTS).document()
        ref.set(doc)

        # Trigger background generation
        import threading
        t = threading.Thread(
            target=self._generate_report_background,
            args=(ref.id, doc, data, current_user),
            daemon=True,
        )
        t.start()

        return {"reportId": report_id, "message": "Report generation started. You will be notified when ready."}

    def _generate_report_background(self, firestore_id: str, doc: dict, data: Any, user: Any):
        try:
            from app.ai.ai_manager import get_ai_manager
            ai = get_ai_manager()

            stats = self.get_analytics_summary(user, district=doc.get("district"))
            narrative = ai.generate_situation_report(
                district=doc.get("district") or "National",
                state=doc.get("state") or "All States",
                from_date=doc["fromDate"].isoformat() if doc.get("fromDate") else "",
                to_date=doc["toDate"].isoformat() if doc.get("toDate") else "",
                incident_stats=stats,
                response_metrics={"avgResponseTimeMinutes": stats.get("avgResponseTimeMinutes")},
                resource_metrics={},
                top_incidents=[],
            )

            self._db.collection(Collections.REPORTS).document(firestore_id).update({
                "status": "READY",
                "summary": narrative,
                "generatedAt": datetime.now(timezone.utc),
            })
        except Exception as e:
            logger.error("Report generation failed", firestore_id=firestore_id, error=str(e))
            self._db.collection(Collections.REPORTS).document(firestore_id).update(
                {"status": "FAILED"}
            )

    # ── Helpers ───────────────────────────────────────────────────────────

    @staticmethod
    def _ts(value, default: Optional[datetime] = None) -> datetime:
        if value is None:
            return default or datetime.min.replace(tzinfo=timezone.utc)
        if isinstance(value, datetime):
            return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        if hasattr(value, "ToDatetime"):
            return value.ToDatetime().replace(tzinfo=timezone.utc)
        return default or datetime.min.replace(tzinfo=timezone.utc)

    @staticmethod
    def _compute_ai_accuracy(incidents: List[Dict]) -> float:
        feedback_list = [
            i.get("aiAnalysis", {}).get("authorityFeedback")
            for i in incidents
            if (i.get("aiAnalysis") or {}).get("authorityFeedback") is not None
        ]
        if not feedback_list:
            return 0.0
        accepted = sum(1 for f in feedback_list if f == "ACCEPTED")
        return round(accepted / len(feedback_list), 2)
