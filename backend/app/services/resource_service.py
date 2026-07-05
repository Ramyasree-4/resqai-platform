"""
ResQAI – Resource Service
CRUD + location tracking + nearby search for rescue resources.
"""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.core.exceptions import FirebaseError, ResourceNotFoundError
from app.core.logging import get_logger
from app.firebase.client import Collections, get_firestore_client
from app.models.resource import (
    ResourceCreate,
    ResourceLocationUpdate,
    ResourceStatusUpdate,
    ResourceUpdate,
)
from app.middleware.auth import AuthenticatedUser
from app.utils.geo import estimated_arrival_minutes, haversine_distance
from app.utils.ids import generate_resource_id

logger = get_logger(__name__)


class ResourceService:

    def __init__(self):
        self._db = get_firestore_client()

    def create_resource(
        self, data: ResourceCreate, current_user: AuthenticatedUser
    ) -> Dict[str, Any]:
        resource_id = generate_resource_id()
        now = datetime.now(timezone.utc)

        doc = {
            "resourceId": resource_id,
            "name": data.name,
            "type": data.type.value,
            "subType": data.subType,
            "organizationId": data.organizationId,
            "organizationName": data.organizationName,
            "district": data.district,
            "state": data.state,
            "contactName": data.contactName,
            "contactPhone": data.contactPhone,
            "contactEmail": data.contactEmail,
            "status": "AVAILABLE",
            "statusUpdatedAt": now,
            "statusUpdatedBy": current_user.uid,
            "capacity": data.capacity.model_dump() if data.capacity else None,
            "currentAssignment": {
                "incidentId": None,
                "incidentTitle": None,
                "assignedAt": None,
                "estimatedReturn": None,
            },
            "baseLocation": {
                "address": data.baseLocation.address,
                "district": data.baseLocation.district,
                "coordinates": {
                    "latitude": data.baseLocation.coordinates.latitude,
                    "longitude": data.baseLocation.coordinates.longitude,
                },
            },
            "currentLocation": {
                "coordinates": {
                    "latitude": data.baseLocation.coordinates.latitude,
                    "longitude": data.baseLocation.coordinates.longitude,
                },
                "updatedAt": now,
                "updatedBy": "INITIAL",
            },
            "capabilities": data.capabilities,
            "isActive": True,
            "notes": data.notes,
            "registeredAt": now,
            "createdBy": current_user.uid,
            "updatedAt": now,
        }

        try:
            doc_ref = self._db.collection(Collections.RESOURCES).document()
            doc_ref.set(doc)
            doc["_firestoreId"] = doc_ref.id
        except Exception as e:
            raise FirebaseError(message=f"Failed to create resource: {str(e)}")

        logger.info("Resource created", resource_id=resource_id, type=data.type.value)
        return doc

    def list_resources(
        self,
        district: Optional[str] = None,
        resource_type: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Dict[str, Any]:
        query = self._db.collection(Collections.RESOURCES).where("isActive", "==", True)

        if district:
            query = query.where("district", "==", district)
        if resource_type:
            query = query.where("type", "==", resource_type)
        if status:
            query = query.where("status", "==", status)

        docs = list(query.stream())
        resources = [d.to_dict() | {"_firestoreId": d.id} for d in docs]
        total = len(resources)
        start = (page - 1) * limit
        return {
            "resources": resources[start: start + limit],
            "total": total,
            "page": page,
            "limit": limit,
        }

    def get_resource_by_id(self, firestore_id: str) -> Dict[str, Any]:
        doc = self._db.collection(Collections.RESOURCES).document(firestore_id).get()
        if not doc.exists:
            raise ResourceNotFoundError()
        return doc.to_dict() | {"_firestoreId": doc.id}

    def update_resource(
        self, firestore_id: str, data: ResourceUpdate, current_user: AuthenticatedUser
    ) -> Dict[str, Any]:
        doc_ref = self._db.collection(Collections.RESOURCES).document(firestore_id)
        if not doc_ref.get().exists:
            raise ResourceNotFoundError()

        updates = data.model_dump(exclude_none=True)
        updates["updatedAt"] = datetime.now(timezone.utc)

        doc_ref.update(updates)
        return self.get_resource_by_id(firestore_id)

    def update_status(
        self, firestore_id: str, data: ResourceStatusUpdate, current_user: AuthenticatedUser
    ) -> Dict[str, Any]:
        doc_ref = self._db.collection(Collections.RESOURCES).document(firestore_id)
        if not doc_ref.get().exists:
            raise ResourceNotFoundError()

        now = datetime.now(timezone.utc)
        doc_ref.update({
            "status": data.status.value,
            "statusUpdatedAt": now,
            "statusUpdatedBy": current_user.uid,
            "updatedAt": now,
        })
        logger.info("Resource status updated", firestore_id=firestore_id, status=data.status.value)
        return {"status": data.status.value, "updatedAt": now.isoformat()}

    def update_location(
        self, firestore_id: str, data: ResourceLocationUpdate, current_user: AuthenticatedUser
    ) -> Dict[str, Any]:
        doc_ref = self._db.collection(Collections.RESOURCES).document(firestore_id)
        if not doc_ref.get().exists:
            raise ResourceNotFoundError()

        now = datetime.now(timezone.utc)
        doc_ref.update({
            "currentLocation.coordinates.latitude": data.coordinates.latitude,
            "currentLocation.coordinates.longitude": data.coordinates.longitude,
            "currentLocation.updatedAt": now,
            "currentLocation.updatedBy": data.updatedBy,
            "updatedAt": now,
        })
        return {"updated": True}

    def get_nearby_resources(
        self,
        lat: float,
        lng: float,
        radius_km: float = 50.0,
        resource_type: Optional[str] = None,
        status: str = "AVAILABLE",
    ) -> List[Dict[str, Any]]:
        """Return available resources within radius, sorted by distance."""
        query = self._db.collection(Collections.RESOURCES).where("isActive", "==", True)
        if status:
            query = query.where("status", "==", status)
        if resource_type:
            query = query.where("type", "==", resource_type)

        docs = list(query.stream())
        results = []

        for doc in docs:
            rd = doc.to_dict()
            loc = rd.get("currentLocation") or rd.get("baseLocation") or {}
            coords = (loc.get("coordinates") or {})
            if not coords.get("latitude"):
                continue

            dist = haversine_distance(lat, lng, coords["latitude"], coords["longitude"])
            if dist > radius_km:
                continue

            results.append({
                "resourceId": rd.get("resourceId"),
                "firestoreId": doc.id,
                "name": rd.get("name"),
                "type": rd.get("type"),
                "status": rd.get("status"),
                "distanceKm": round(dist, 2),
                "estimatedArrivalMinutes": estimated_arrival_minutes(dist),
                "coordinates": coords,
            })

        results.sort(key=lambda r: r["distanceKm"])
        return results

    def delete_resource(self, firestore_id: str) -> None:
        doc_ref = self._db.collection(Collections.RESOURCES).document(firestore_id)
        if not doc_ref.get().exists:
            raise ResourceNotFoundError()
        doc_ref.update({"isActive": False, "updatedAt": datetime.now(timezone.utc)})
