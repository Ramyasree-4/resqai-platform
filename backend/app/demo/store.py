"""
ResQAI – In-Memory Demo Store
Replaces Firestore for hackathon demo mode.
All data lives in memory — resets on server restart.
"""
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# ── In-memory collections ──────────────────────────────────────────────────────
_users: Dict[str, Dict] = {}
_incidents: Dict[str, Dict] = {}
_resources: Dict[str, Dict] = {}
_notifications: Dict[str, Dict] = {}
_settings: Dict[str, Dict] = {}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _id() -> str:
    return str(uuid.uuid4())


# ── USERS ──────────────────────────────────────────────────────────────────────

def create_user(uid: str, data: Dict) -> Dict:
    _users[uid] = {**data, "uid": uid}
    return _users[uid]


def get_user(uid: str) -> Optional[Dict]:
    return _users.get(uid)


def get_user_by_email(email: str) -> Optional[Dict]:
    for u in _users.values():
        if u.get("email") == email:
            return u
    return None


def update_user(uid: str, updates: Dict) -> Optional[Dict]:
    if uid not in _users:
        return None
    _users[uid].update(updates)
    return _users[uid]


def list_users(role=None, district=None, is_active=None, page=1, limit=20) -> Dict:
    users = list(_users.values())
    if role:
        users = [u for u in users if u.get("role") == role]
    if district:
        users = [u for u in users if u.get("district") == district]
    if is_active is not None:
        users = [u for u in users if u.get("isActive") == is_active]
    total = len(users)
    start = (page - 1) * limit
    return {"users": users[start:start + limit], "total": total, "page": page, "limit": limit}


# ── INCIDENTS ──────────────────────────────────────────────────────────────────

def create_incident(data: Dict) -> str:
    doc_id = _id()
    _incidents[doc_id] = {**data, "_firestoreId": doc_id}
    return doc_id


def get_incident(doc_id: str) -> Optional[Dict]:
    return _incidents.get(doc_id)


def update_incident(doc_id: str, updates: Dict) -> None:
    if doc_id in _incidents:
        # Support dot-notation keys like "aiAnalysis.severityScore"
        for key, val in updates.items():
            if "." in key:
                parts = key.split(".", 1)
                if parts[0] not in _incidents[doc_id]:
                    _incidents[doc_id][parts[0]] = {}
                _incidents[doc_id][parts[0]][parts[1]] = val
            else:
                _incidents[doc_id][key] = val


def list_incidents(filters: Dict = None) -> List[Dict]:
    items = list(_incidents.values())
    f = filters or {}
    if f.get("reportedBy"):
        items = [i for i in items if i.get("reportedBy") == f["reportedBy"]]
    if f.get("status"):
        items = [i for i in items if i.get("status") == f["status"]]
    if f.get("incidentType"):
        items = [i for i in items if i.get("incidentType") == f["incidentType"]]
    if f.get("district"):
        items = [i for i in items if (i.get("location") or {}).get("district") == f["district"]]
    if f.get("state"):
        items = [i for i in items if (i.get("location") or {}).get("state") == f["state"]]
    if f.get("status_not_in"):
        items = [i for i in items if i.get("status") not in f["status_not_in"]]
    return items


# ── RESOURCES ─────────────────────────────────────────────────────────────────

def create_resource(data: Dict) -> str:
    doc_id = _id()
    _resources[doc_id] = {**data, "_firestoreId": doc_id}
    return doc_id


def get_resource(doc_id: str) -> Optional[Dict]:
    return _resources.get(doc_id)


def update_resource(doc_id: str, updates: Dict) -> None:
    if doc_id in _resources:
        for key, val in updates.items():
            if "." in key:
                parts = key.split(".", 1)
                if parts[0] not in _resources[doc_id]:
                    _resources[doc_id][parts[0]] = {}
                _resources[doc_id][parts[0]][parts[1]] = val
            else:
                _resources[doc_id][key] = val


def list_resources(filters: Dict = None) -> List[Dict]:
    items = [r for r in _resources.values() if r.get("isActive", True)]
    f = filters or {}
    if f.get("district"):
        items = [r for r in items if r.get("district") == f["district"]]
    if f.get("type"):
        items = [r for r in items if r.get("type") == f["type"]]
    if f.get("status"):
        items = [r for r in items if r.get("status") == f["status"]]
    return items


# ── NOTIFICATIONS ─────────────────────────────────────────────────────────────

def create_notification(data: Dict) -> str:
    doc_id = _id()
    _notifications[doc_id] = {**data, "_firestoreId": doc_id, "notificationId": doc_id}
    return doc_id


def list_notifications(recipient_id: str) -> List[Dict]:
    return [n for n in _notifications.values() if n.get("recipientId") == recipient_id]


def mark_notification_read(doc_id: str) -> None:
    if doc_id in _notifications:
        _notifications[doc_id]["isRead"] = True
        _notifications[doc_id]["readAt"] = _now()


def mark_all_notifications_read(recipient_id: str) -> int:
    count = 0
    for n in _notifications.values():
        if n.get("recipientId") == recipient_id and not n.get("isRead"):
            n["isRead"] = True
            n["readAt"] = _now()
            count += 1
    return count


# ── SETTINGS ──────────────────────────────────────────────────────────────────

def get_settings_doc(doc_id: str) -> Dict:
    return _settings.get(doc_id, {})


def set_settings_doc(doc_id: str, data: Dict) -> None:
    _settings[doc_id] = {**_settings.get(doc_id, {}), **data}


# ── SEED DEMO DATA ─────────────────────────────────────────────────────────────

def seed_demo_data():
    """Seed realistic demo data for hackathon presentation."""
    if _resources:
        return  # Already seeded

    now = _now()

    # Demo resources
    demo_resources = [
        {"resourceId": "RES-DEMO-001", "name": "ODRAF Boat Unit 2", "type": "RESCUE_BOAT",
         "organizationId": "org-odraf", "organizationName": "ODRAF", "district": "Khurda",
         "state": "Odisha", "contactName": "Insp. Ramesh", "contactPhone": "+919123456780",
         "status": "AVAILABLE", "isActive": True,
         "capabilities": ["WATER_RESCUE", "FLOOD_OPERATIONS"],
         "baseLocation": {"address": "ODRAF HQ, BBSR", "district": "Khurda",
                          "coordinates": {"latitude": 20.3293, "longitude": 85.8315}},
         "currentLocation": {"coordinates": {"latitude": 20.3293, "longitude": 85.8315},
                             "updatedAt": now, "updatedBy": "INITIAL"},
         "currentAssignment": {"incidentId": None}, "registeredAt": now, "updatedAt": now},
        {"resourceId": "RES-DEMO-002", "name": "NDRF Medical Team A", "type": "MEDICAL_UNIT",
         "organizationId": "org-ndrf", "organizationName": "NDRF", "district": "Khurda",
         "state": "Odisha", "contactName": "Dr. Priya", "contactPhone": "+919123456781",
         "status": "AVAILABLE", "isActive": True,
         "capabilities": ["MEDICAL_FIRST_AID", "TRAUMA_CARE"],
         "baseLocation": {"address": "NDRF Camp, BBSR", "district": "Khurda",
                          "coordinates": {"latitude": 20.2961, "longitude": 85.8245}},
         "currentLocation": {"coordinates": {"latitude": 20.2961, "longitude": 85.8245},
                             "updatedAt": now, "updatedBy": "INITIAL"},
         "currentAssignment": {"incidentId": None}, "registeredAt": now, "updatedAt": now},
        {"resourceId": "RES-DEMO-003", "name": "Fire Engine Unit 5", "type": "FIRE_TRUCK",
         "organizationId": "org-fire", "organizationName": "Odisha Fire Service", "district": "Khurda",
         "state": "Odisha", "contactName": "Supt. Arun", "contactPhone": "+919123456782",
         "status": "AVAILABLE", "isActive": True, "capabilities": ["FIREFIGHTING", "RESCUE"],
         "baseLocation": {"address": "Fire HQ, Khandagiri", "district": "Khurda",
                          "coordinates": {"latitude": 20.2700, "longitude": 85.7900}},
         "currentLocation": {"coordinates": {"latitude": 20.2700, "longitude": 85.7900},
                             "updatedAt": now, "updatedBy": "INITIAL"},
         "currentAssignment": {"incidentId": None}, "registeredAt": now, "updatedAt": now},
        {"resourceId": "RES-DEMO-004", "name": "District Shelter Camp 1", "type": "SHELTER",
         "organizationId": "org-dist", "organizationName": "District Admin", "district": "Khurda",
         "state": "Odisha", "contactName": "BDO Khurda", "contactPhone": "+919123456783",
         "status": "AVAILABLE", "isActive": True, "capabilities": ["SHELTER", "FOOD_SUPPLY"],
         "capacity": {"total": 500, "current": 120, "available": 380},
         "baseLocation": {"address": "Govt School, Khurda", "district": "Khurda",
                          "coordinates": {"latitude": 20.1800, "longitude": 85.6200}},
         "currentLocation": {"coordinates": {"latitude": 20.1800, "longitude": 85.6200},
                             "updatedAt": now, "updatedBy": "INITIAL"},
         "currentAssignment": {"incidentId": None}, "registeredAt": now, "updatedAt": now},
    ]
    for r in demo_resources:
        doc_id = _id()
        _resources[doc_id] = {**r, "_firestoreId": doc_id}

    # Demo incidents (pre-analyzed)
    demo_incidents = [
        {"incidentId": "INC-2026-DEMO001", "title": "Flash Flood in Khandagiri",
         "description": "Water level rising rapidly. 200+ families trapped on rooftops. Electricity cut. Children and elderly need urgent help.",
         "incidentType": "FLOOD", "urgencyLevel": "CRITICAL", "affectedPeople": 800,
         "status": "TRIAGED", "reportedBy": "demo-citizen-uid", "reporterName": "Demo Citizen",
         "isAnonymous": False, "fatalities": 0, "injuries": 5,
         "location": {"address": "Khandagiri, Bhubaneswar", "district": "Khurda", "state": "Odisha",
                      "coordinates": {"latitude": 20.2961, "longitude": 85.8245}, "geohash": "tgt52v"},
         "aiAnalysis": {"analysisId": "ai-demo-001", "modelVersion": "mistral-large-latest",
                        "classifiedType": "FLOOD", "classificationConfidence": 0.97,
                        "severityScore": 9, "severityBand": "CRITICAL", "priorityScore": 0.92,
                        "situationSummary": "Critical flash flood in Khandagiri affecting 800+ residents. Immediate rescue required.",
                        "reasoning": ["800+ people affected", "Vulnerable populations trapped", "Rising water levels", "Infrastructure loss"],
                        "immediateActions": ["Deploy rescue boats immediately", "Establish medical triage", "Issue district broadcast"],
                        "resourceRecommendations": [{"resourceType": "RESCUE_BOAT", "quantity": 5, "urgency": "IMMEDIATE", "reason": "Water rescue"},
                                                   {"resourceType": "MEDICAL_UNIT", "quantity": 2, "urgency": "HIGH", "reason": "Injuries"}],
                        "risks": ["Secondary flooding", "Electrocution risk"],
                        "fallbackUsed": False, "dataQuality": "HIGH", "isDuplicate": False,
                        "authorityFeedback": None},
         "assignedTo": {"authorityId": None, "authorityName": None, "assignedAt": None, "resources": []},
         "escalation": {"isEscalated": False, "escalationCount": 0},
         "resolution": {"resolvedAt": None},
         "source": "WEB", "version": 1, "createdAt": now, "updatedAt": now, "mediaFiles": [],
         "linkedIncidents": [], "responseTimeMinutes": None, "isSOS": False},
        {"incidentId": "INC-2026-DEMO002", "title": "Building Fire at Industrial Area",
         "description": "Large fire in a chemical warehouse. Smoke visible for miles. Workers trapped.",
         "incidentType": "FIRE", "urgencyLevel": "HIGH", "affectedPeople": 45,
         "status": "ASSIGNED", "reportedBy": "demo-citizen-uid", "reporterName": "Demo Citizen",
         "isAnonymous": False, "fatalities": 0, "injuries": 8,
         "location": {"address": "Mancheswar Industrial Area", "district": "Khurda", "state": "Odisha",
                      "coordinates": {"latitude": 20.3100, "longitude": 85.8600}, "geohash": "tgt5gz"},
         "aiAnalysis": {"analysisId": "ai-demo-002", "modelVersion": "mistral-large-latest",
                        "classifiedType": "FIRE", "classificationConfidence": 0.95,
                        "severityScore": 8, "severityBand": "CRITICAL", "priorityScore": 0.82,
                        "situationSummary": "Industrial fire with chemical risk. 45 workers affected, 8 injured.",
                        "reasoning": ["Chemical warehouse fire", "Workers trapped", "High injury count"],
                        "immediateActions": ["Deploy fire units", "Evacuate 500m radius", "Hazmat team needed"],
                        "resourceRecommendations": [{"resourceType": "FIRE_TRUCK", "quantity": 3, "urgency": "IMMEDIATE", "reason": "Fire suppression"},
                                                   {"resourceType": "AMBULANCE", "quantity": 2, "urgency": "HIGH", "reason": "Injuries"}],
                        "risks": ["Chemical explosion", "Toxic smoke"],
                        "fallbackUsed": False, "dataQuality": "HIGH", "isDuplicate": False,
                        "authorityFeedback": "ACCEPTED"},
         "assignedTo": {"authorityId": "demo-authority-uid", "authorityName": "District Officer",
                        "assignedAt": now, "resources": [{"resourceId": "RES-DEMO-003", "resourceName": "Fire Engine Unit 5", "resourceType": "FIRE_TRUCK", "assignedAt": now, "status": "EN_ROUTE"}]},
         "escalation": {"isEscalated": False, "escalationCount": 0},
         "resolution": {"resolvedAt": None},
         "source": "WEB", "version": 1, "createdAt": now, "updatedAt": now, "mediaFiles": [],
         "linkedIncidents": [], "responseTimeMinutes": None, "isSOS": False},
        {"incidentId": "INC-2026-DEMO003", "title": "Elderly Person Collapsed",
         "description": "Elderly man collapsed in Patia market. Unconscious. Needs ambulance urgently.",
         "incidentType": "MEDICAL", "urgencyLevel": "HIGH", "affectedPeople": 1,
         "status": "RESOLVED", "reportedBy": "demo-citizen-uid", "reporterName": "Demo Citizen",
         "isAnonymous": False, "fatalities": 0, "injuries": 1,
         "location": {"address": "Patia Market, BBSR", "district": "Khurda", "state": "Odisha",
                      "coordinates": {"latitude": 20.3500, "longitude": 85.8200}, "geohash": "tgt5hb"},
         "aiAnalysis": {"analysisId": "ai-demo-003", "modelVersion": "mistral-large-latest",
                        "classifiedType": "MEDICAL", "classificationConfidence": 0.98,
                        "severityScore": 7, "severityBand": "HIGH", "priorityScore": 0.71,
                        "situationSummary": "Medical emergency - elderly person unconscious. Ambulance dispatched.",
                        "reasoning": ["Unconscious patient", "Time-critical condition"],
                        "immediateActions": ["Dispatch ambulance", "First aid on scene"],
                        "resourceRecommendations": [{"resourceType": "AMBULANCE", "quantity": 1, "urgency": "IMMEDIATE", "reason": "Medical emergency"}],
                        "risks": ["Cardiac arrest risk"],
                        "fallbackUsed": False, "dataQuality": "HIGH", "isDuplicate": False,
                        "authorityFeedback": "ACCEPTED"},
         "assignedTo": {"authorityId": "demo-authority-uid", "authorityName": "District Officer",
                        "assignedAt": now, "resources": []},
         "escalation": {"isEscalated": False, "escalationCount": 0},
         "resolution": {"resolvedAt": now, "resolutionNote": "Patient stabilised and transported to AIIMS.", "outcome": "RESCUED"},
         "source": "WEB", "version": 1, "createdAt": now, "updatedAt": now, "mediaFiles": [],
         "linkedIncidents": [], "responseTimeMinutes": 18.0, "isSOS": False},
    ]
    for inc in demo_incidents:
        doc_id = _id()
        _incidents[doc_id] = {**inc, "_firestoreId": doc_id}
