"""
ResQAI – Analytics & Dashboard API Router
Dashboard stats, map data, incident trends, analytics summary, reports.
"""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query

from app.core.responses import success_response
from app.middleware.auth import (
    AuthenticatedUser,
    get_current_user,
    require_roles,
)
from app.models.enums import UserRole
from app.models.analytics import ReportCreate, AnalyticsExportRequest
from app.services.analytics_service import AnalyticsService

router = APIRouter(tags=["Analytics & Dashboard"])

_AUTHORITY_ROLES = (
    UserRole.AUTHORITY, UserRole.DISTRICT_OFFICER,
    UserRole.STATE_OFFICER, UserRole.ADMIN,
)


def _svc() -> AnalyticsService:
    return AnalyticsService()


# ── Dashboard ─────────────────────────────────────────────────────────────────

@router.get("/dashboard/stats")
async def get_dashboard_stats(
    district: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    period: str = Query("today", pattern=r"^(today|week|month)$"),
    current_user: AuthenticatedUser = Depends(require_roles(*_AUTHORITY_ROLES)),
    svc: AnalyticsService = Depends(_svc),
):
    """Dashboard KPI cards data."""
    result = svc.get_dashboard_stats(current_user, district, state, period)
    return success_response(result)


@router.get("/dashboard/map-data")
async def get_map_data(
    district: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    include_resolved: bool = Query(False, alias="includeResolved"),
    current_user: AuthenticatedUser = Depends(require_roles(*_AUTHORITY_ROLES)),
    svc: AnalyticsService = Depends(_svc),
):
    """All active incidents and resources for map rendering."""
    result = svc.get_map_data(current_user, district, state, include_resolved)
    return success_response(result)


@router.get("/dashboard/incident-trend")
async def get_incident_trend(
    district: Optional[str] = Query(None),
    days: int = Query(7, ge=1, le=90),
    current_user: AuthenticatedUser = Depends(require_roles(*_AUTHORITY_ROLES)),
    svc: AnalyticsService = Depends(_svc),
):
    """Incident counts for each of the past N days (for charts)."""
    result = svc.get_incident_trend(current_user, district, days)
    return success_response(result)


# ── Analytics ─────────────────────────────────────────────────────────────────

@router.get("/analytics/summary")
async def get_analytics_summary(
    district: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    current_user: AuthenticatedUser = Depends(require_roles(*_AUTHORITY_ROLES)),
    svc: AnalyticsService = Depends(_svc),
):
    """Aggregated analytics summary for a time period."""
    result = svc.get_analytics_summary(current_user, district, state, from_date, to_date)
    return success_response(result)


@router.get("/analytics/response-time")
async def get_response_time(
    current_user: AuthenticatedUser = Depends(require_roles(*_AUTHORITY_ROLES)),
    svc: AnalyticsService = Depends(_svc),
):
    """Response time breakdown by incident type."""
    result = svc.get_response_time_analytics(current_user)
    return success_response(result)


@router.get("/analytics/resource-utilization")
async def get_resource_utilization(
    current_user: AuthenticatedUser = Depends(get_current_user),
    svc: AnalyticsService = Depends(_svc),
):
    """Resource utilization rates by type."""
    result = svc.get_resource_utilization(current_user)
    return success_response(result)


@router.post("/analytics/export")
async def export_analytics(
    data: AnalyticsExportRequest,
    current_user: AuthenticatedUser = Depends(require_roles(*_AUTHORITY_ROLES)),
    svc: AnalyticsService = Depends(_svc),
):
    """Request analytics export (PDF/CSV). Returns report ID."""
    from app.models.analytics import ReportCreate
    from app.models.enums import ReportType
    report_data = ReportCreate(
        title=f"Analytics Export {data.from_date.date()} to {data.to_date.date()}",
        type=ReportType.ANALYTICS,
        district=data.district,
        state=data.state,
        fromDate=data.from_date,
        toDate=data.to_date,
    )
    result = svc.create_report(report_data, current_user)
    return success_response(result)
