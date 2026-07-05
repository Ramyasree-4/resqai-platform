"""
ResQAI – Resources API Router
CRUD + status/location updates + nearby search.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, status

from app.core.responses import created_response, success_response, paginated_response
from app.middleware.auth import (
    AuthenticatedUser,
    get_current_user,
    require_roles,
)
from app.models.enums import ResourceStatus, ResourceType, UserRole
from app.models.resource import (
    ResourceCreate,
    ResourceLocationUpdate,
    ResourceStatusUpdate,
    ResourceUpdate,
)
from app.services.resource_service import ResourceService

router = APIRouter(prefix="/resources", tags=["Resources"])

_ADMIN_ROLES = (UserRole.DISTRICT_OFFICER, UserRole.STATE_OFFICER, UserRole.ADMIN)
_AUTHORITY_ROLES = (
    UserRole.AUTHORITY, UserRole.DISTRICT_OFFICER, UserRole.STATE_OFFICER, UserRole.ADMIN
)


def _svc() -> ResourceService:
    return ResourceService()


@router.get("/nearby")
async def get_nearby_resources(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(50.0, ge=1, le=500, alias="radiusKm"),
    resource_type: Optional[ResourceType] = Query(None, alias="type"),
    res_status: Optional[ResourceStatus] = Query(ResourceStatus.AVAILABLE, alias="status"),
    current_user: AuthenticatedUser = Depends(get_current_user),
    svc: ResourceService = Depends(_svc),
):
    """Find available resources near a coordinate, sorted by distance."""
    results = svc.get_nearby_resources(
        lat, lng, radius_km,
        resource_type.value if resource_type else None,
        res_status.value if res_status else None,
    )
    return success_response({"resources": results})


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_resource(
    data: ResourceCreate,
    current_user: AuthenticatedUser = Depends(require_roles(*_ADMIN_ROLES)),
    svc: ResourceService = Depends(_svc),
):
    """Create a new resource entry in the registry."""
    result = svc.create_resource(data, current_user)
    return created_response(result)


@router.get("")
async def list_resources(
    district: Optional[str] = Query(None),
    resource_type: Optional[ResourceType] = Query(None, alias="type"),
    res_status: Optional[ResourceStatus] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: AuthenticatedUser = Depends(
        require_roles(*_AUTHORITY_ROLES)
    ),
    svc: ResourceService = Depends(_svc),
):
    """List resources with optional filters."""
    result = svc.list_resources(
        district=district,
        resource_type=resource_type.value if resource_type else None,
        status=res_status.value if res_status else None,
        page=page,
        limit=limit,
    )
    return paginated_response(result["resources"], result["total"], result["page"], result["limit"])


@router.get("/{resource_id}")
async def get_resource(
    resource_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
    svc: ResourceService = Depends(_svc),
):
    """Get resource details by Firestore ID."""
    return success_response(svc.get_resource_by_id(resource_id))


@router.put("/{resource_id}")
async def update_resource(
    resource_id: str,
    data: ResourceUpdate,
    current_user: AuthenticatedUser = Depends(require_roles(*_ADMIN_ROLES)),
    svc: ResourceService = Depends(_svc),
):
    """Update resource details."""
    result = svc.update_resource(resource_id, data, current_user)
    return success_response(result)


@router.put("/{resource_id}/status")
async def update_resource_status(
    resource_id: str,
    data: ResourceStatusUpdate,
    current_user: AuthenticatedUser = Depends(
        require_roles(*_AUTHORITY_ROLES)
    ),
    svc: ResourceService = Depends(_svc),
):
    """Update resource availability status."""
    result = svc.update_status(resource_id, data, current_user)
    return success_response(result)


@router.put("/{resource_id}/location")
async def update_resource_location(
    resource_id: str,
    data: ResourceLocationUpdate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    svc: ResourceService = Depends(_svc),
):
    """Update resource GPS location (field units)."""
    result = svc.update_location(resource_id, data, current_user)
    return success_response(result)


@router.delete("/{resource_id}")
async def delete_resource(
    resource_id: str,
    current_user: AuthenticatedUser = Depends(require_roles(UserRole.ADMIN)),
    svc: ResourceService = Depends(_svc),
):
    """Soft-delete (deactivate) a resource."""
    svc.delete_resource(resource_id)
    return success_response(None, "Resource deactivated.")
