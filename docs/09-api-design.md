# Section 09 – REST API Design

**Base URL:** `https://api.resqai.in/v1`  
**Content-Type:** `application/json`  
**Authentication:** Bearer token (Firebase JWT) in `Authorization` header  
**API Version:** v1

---

## 9.1 Authentication APIs

### POST `/auth/register`
Register a new user account.

**Auth Required:** No  
**Rate Limit:** 5/hour per IP

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass@123",
  "displayName": "Rajesh Kumar",
  "phoneNumber": "+919876543210",
  "district": "Khurda",
  "state": "Odisha",
  "role": "CITIZEN"
}
```
**Response:** `201 Created`
```json
{
  "success": true,
  "data": {
    "uid": "firebase-uid-abc123",
    "email": "user@example.com",
    "displayName": "Rajesh Kumar",
    "role": "CITIZEN",
    "token": "eyJhbGciOiJSUzI1NiJ9...",
    "refreshToken": "AMf-vBxyz..."
  }
}
```

---

### POST `/auth/login`
Authenticate a user.

**Auth Required:** No

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass@123"
}
```
**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "uid": "firebase-uid-abc123",
    "token": "eyJhbGciOiJSUzI1NiJ9...",
    "refreshToken": "AMf-vBxyz...",
    "expiresIn": 3600,
    "user": {
      "uid": "firebase-uid-abc123",
      "displayName": "Rajesh Kumar",
      "email": "user@example.com",
      "role": "CITIZEN",
      "district": "Khurda"
    }
  }
}
```

---

### POST `/auth/refresh`
Refresh access token.

**Auth Required:** No (uses refresh token)

**Request:**
```json
{
  "refreshToken": "AMf-vBxyz..."
}
```
**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJSUzI1NiJ9...",
    "expiresIn": 3600
  }
}
```

---

### POST `/auth/logout`
Revoke current session.

**Auth Required:** Yes

**Response:** `200 OK`
```json
{ "success": true, "message": "Logged out successfully" }
```

---

### POST `/auth/forgot-password`
Send password reset email.

**Auth Required:** No

**Request:**
```json
{ "email": "user@example.com" }
```
**Response:** `200 OK`
```json
{ "success": true, "message": "Password reset email sent" }
```

---

### GET `/auth/me`
Get current user profile.

**Auth Required:** Yes

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "uid": "firebase-uid-abc123",
    "displayName": "Rajesh Kumar",
    "email": "user@example.com",
    "role": "CITIZEN",
    "district": "Khurda",
    "state": "Odisha",
    "isVerified": true,
    "notificationPreferences": { "pushEnabled": true }
  }
}
```

---

### PUT `/auth/profile`
Update user profile.

**Auth Required:** Yes

**Request:**
```json
{
  "displayName": "Rajesh Kumar",
  "phoneNumber": "+919876543210",
  "notificationPreferences": {
    "pushEnabled": true,
    "smsEnabled": true,
    "language": "hi"
  }
}
```
**Response:** `200 OK`

---

### POST `/auth/fcm-token`
Register FCM device token for push notifications.

**Auth Required:** Yes

**Request:**
```json
{ "token": "fcm-device-token-xyz" }
```
**Response:** `200 OK`

---

## 9.2 Incident APIs

### POST `/incidents`
Submit a new incident report.

**Auth Required:** Yes (CITIZEN, AUTHORITY, VOLUNTEER)

**Request:**
```json
{
  "title": "Flood in residential area",
  "description": "Water level rising rapidly, approximately 200 families trapped on rooftops. Electricity cut off. Children and elderly need immediate help.",
  "incidentType": "FLOOD",
  "urgencyLevel": "CRITICAL",
  "affectedPeople": 800,
  "location": {
    "address": "Bhubaneswar, Khandagiri area",
    "district": "Khurda",
    "state": "Odisha",
    "pincode": "751030",
    "coordinates": {
      "latitude": 20.2961,
      "longitude": 85.8245
    }
  }
}
```
**Response:** `201 Created`
```json
{
  "success": true,
  "data": {
    "incidentId": "INC-2024-00000001",
    "status": "SUBMITTED",
    "message": "Report received. AI is analyzing your report.",
    "estimatedResponseTime": "30-45 minutes",
    "trackingUrl": "https://app.resqai.in/track/INC-2024-00000001"
  }
}
```

---

### POST `/incidents/:id/media`
Upload media files for an incident.

**Auth Required:** Yes  
**Content-Type:** `multipart/form-data`

**Request:** FormData with up to 5 files (images/videos)

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "uploaded": [
      {
        "fileId": "file-uuid-1",
        "url": "https://storage.googleapis.com/resqai-media/...",
        "type": "image"
      }
    ]
  }
}
```

---

### GET `/incidents`
Get incidents list (authority/admin view).

**Auth Required:** Yes (AUTHORITY and above)

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `district` | string | Filter by district |
| `status` | string | Filter by status |
| `type` | string | Filter by incident type |
| `severity` | string | LOW\|MEDIUM\|HIGH\|CRITICAL |
| `from` | ISO date | Start date filter |
| `to` | ISO date | End date filter |
| `sort` | string | `severity` (default)\|`date` |
| `page` | number | Page number (default: 1) |
| `limit` | number | Page size (default: 20, max: 100) |

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "incidents": [
      {
        "incidentId": "INC-2024-00000001",
        "title": "Flood in residential area",
        "incidentType": "FLOOD",
        "status": "TRIAGED",
        "urgencyLevel": "CRITICAL",
        "aiAnalysis": {
          "severityScore": 9,
          "severityBand": "CRITICAL",
          "priorityRank": 1
        },
        "location": {
          "district": "Khurda",
          "state": "Odisha"
        },
        "affectedPeople": 800,
        "createdAt": "2024-01-15T10:30:00Z"
      }
    ],
    "pagination": {
      "total": 142,
      "page": 1,
      "limit": 20,
      "totalPages": 8
    }
  }
}
```

---

### GET `/incidents/my`
Get current user's submitted incidents.

**Auth Required:** Yes

**Response:** `200 OK` (same structure as above, filtered to current user)

---

### GET `/incidents/:id`
Get full incident details.

**Auth Required:** Yes

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "incidentId": "INC-2024-00000001",
    "title": "Flood in residential area",
    "description": "...",
    "incidentType": "FLOOD",
    "status": "ASSIGNED",
    "urgencyLevel": "CRITICAL",
    "affectedPeople": 800,
    "location": { "..." : "..." },
    "mediaFiles": [ { "..." : "..." } ],
    "aiAnalysis": {
      "severityScore": 9,
      "severityBand": "CRITICAL",
      "classifiedType": "FLOOD",
      "classificationConfidence": 0.97,
      "priorityRank": 1,
      "situationSummary": "A critical flood emergency affecting an estimated 800 residents...",
      "reasoning": [
        "High number of affected people (800)",
        "Critical infrastructure loss (electricity)",
        "Vulnerable populations present (children, elderly)",
        "Rapidly rising water levels indicate active danger"
      ],
      "resourceRecommendations": [
        { "resourceType": "RESCUE_BOAT", "quantity": 5, "urgency": "IMMEDIATE" },
        { "resourceType": "MEDICAL_UNIT", "quantity": 2, "urgency": "HIGH" }
      ]
    },
    "assignedTo": {
      "authorityName": "District Collector Khurda",
      "resources": [
        { "resourceName": "ODRAF Boat Unit 3", "status": "EN_ROUTE" }
      ]
    },
    "createdAt": "2024-01-15T10:30:00Z",
    "updatedAt": "2024-01-15T10:35:00Z"
  }
}
```

---

### PUT `/incidents/:id/status`
Update incident status.

**Auth Required:** Yes (AUTHORITY and above)

**Request:**
```json
{
  "status": "IN_PROGRESS",
  "note": "ODRAF team dispatched, ETA 20 minutes"
}
```
**Response:** `200 OK`

---

### PUT `/incidents/:id/assign`
Assign resources to an incident.

**Auth Required:** Yes (AUTHORITY and above)

**Request:**
```json
{
  "authorityId": "user-uid-authority",
  "resourceIds": ["res-001", "res-002"]
}
```
**Response:** `200 OK`

---

### POST `/incidents/:id/escalate`
Escalate an incident to higher authority.

**Auth Required:** Yes (AUTHORITY and above)

**Request:**
```json
{
  "reason": "Incident scope exceeds district capacity. Requesting state-level support.",
  "escalateTo": "STATE_OFFICER"
}
```
**Response:** `200 OK`

---

### POST `/incidents/:id/comments`
Add a comment to an incident.

**Auth Required:** Yes

**Request:**
```json
{
  "content": "Local fire brigade also en route. ETA 15 minutes.",
  "isInternal": true
}
```
**Response:** `201 Created`

---

### GET `/incidents/:id/comments`
Get all comments for an incident.

**Auth Required:** Yes

**Response:** `200 OK` — array of comments

---

### POST `/incidents/sos`
Submit an SOS emergency (minimal data, highest priority).

**Auth Required:** Optional (can be anonymous)

**Request:**
```json
{
  "coordinates": {
    "latitude": 20.2961,
    "longitude": 85.8245
  },
  "description": "Trapped in flood water, 3rd floor",
  "phoneNumber": "+919876543210"
}
```
**Response:** `201 Created`
```json
{
  "success": true,
  "data": {
    "incidentId": "INC-2024-00000002",
    "message": "SOS received. Emergency teams alerted.",
    "nearestUnit": "ODRAF Boat Unit 2 — 2.3 km away"
  }
}
```

---

## 9.3 AI APIs

### POST `/ai/analyze`
Trigger AI analysis for an incident (admin/system use).

**Auth Required:** Yes (ADMIN, SYSTEM)

**Request:**
```json
{ "incidentId": "INC-2024-00000001" }
```
**Response:** `202 Accepted`
```json
{ "success": true, "message": "AI analysis queued" }
```

---

### GET `/ai/analysis/:incidentId`
Get AI analysis results for an incident.

**Auth Required:** Yes

**Response:** `200 OK` — full AI analysis object

---

### POST `/ai/feedback/:analysisId`
Submit feedback on an AI recommendation.

**Auth Required:** Yes (AUTHORITY and above)

**Request:**
```json
{
  "feedback": "ACCEPTED",
  "classificationCorrect": true,
  "severityAccurate": true,
  "recommendationsUseful": true,
  "comment": "Severity assessment was accurate"
}
```
**Response:** `200 OK`

---

### GET `/ai/summary/:incidentId`
Get AI-generated situation summary.

**Auth Required:** Yes

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "summary": "A critical flood emergency is active in the Khandagiri area of Khurda district...",
    "generatedAt": "2024-01-15T10:34:00Z"
  }
}
```

---

### POST `/ai/cluster-analysis`
Request AI cluster analysis for a district.

**Auth Required:** Yes (AUTHORITY and above)

**Request:**
```json
{
  "district": "Khurda",
  "windowHours": 2
}
```
**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "clustersDetected": 2,
    "clusters": [
      {
        "center": { "latitude": 20.30, "longitude": 85.82 },
        "incidentCount": 8,
        "dominantType": "FLOOD",
        "avgSeverity": 7.5,
        "affectedArea": "3.2 km radius"
      }
    ]
  }
}
```

---

## 9.4 Resource APIs

### GET `/resources`
Get all resources.

**Auth Required:** Yes (AUTHORITY and above)

**Query Parameters:** `district`, `type`, `status`, `page`, `limit`

**Response:** `200 OK` — paginated resources list

---

### POST `/resources`
Create a new resource entry.

**Auth Required:** Yes (ADMIN, DISTRICT_OFFICER)

**Request:**
```json
{
  "name": "ODRAF Boat Unit 7",
  "type": "RESCUE_BOAT",
  "organizationId": "org-odraf-001",
  "district": "Khurda",
  "state": "Odisha",
  "contactName": "Inspector Ramesh",
  "contactPhone": "+919123456789",
  "capabilities": ["WATER_RESCUE", "FLOOD_OPERATIONS"],
  "baseLocation": {
    "address": "ODRAF HQ, Bhubaneswar",
    "coordinates": { "latitude": 20.3293, "longitude": 85.8315 }
  }
}
```
**Response:** `201 Created`

---

### GET `/resources/:id`
Get resource details.

**Auth Required:** Yes

**Response:** `200 OK` — full resource object with deployment history

---

### PUT `/resources/:id`
Update resource details.

**Auth Required:** Yes (ADMIN, DISTRICT_OFFICER)

**Response:** `200 OK`

---

### PUT `/resources/:id/status`
Update resource availability status.

**Auth Required:** Yes (AUTHORITY and above)

**Request:**
```json
{
  "status": "MAINTENANCE",
  "note": "Scheduled engine maintenance, back at 18:00"
}
```
**Response:** `200 OK`

---

### PUT `/resources/:id/location`
Update resource GPS location (field app).

**Auth Required:** Yes

**Request:**
```json
{
  "coordinates": { "latitude": 20.2961, "longitude": 85.8245 },
  "updatedBy": "GPS"
}
```
**Response:** `200 OK`

---

### GET `/resources/nearby`
Find resources near a location.

**Auth Required:** Yes

**Query Parameters:** `lat`, `lng`, `radiusKm` (default: 50), `type`, `status=AVAILABLE`

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "resources": [
      {
        "resourceId": "res-001",
        "name": "ODRAF Boat Unit 2",
        "type": "RESCUE_BOAT",
        "status": "AVAILABLE",
        "distanceKm": 2.3,
        "estimatedArrivalMinutes": 8
      }
    ]
  }
}
```

---

## 9.5 Dashboard APIs

### GET `/dashboard/stats`
Get dashboard KPI statistics.

**Auth Required:** Yes (AUTHORITY and above)

**Query Parameters:** `district`, `state`, `period` (today|week|month)

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "activeIncidents": 47,
    "criticalIncidents": 8,
    "resolvedToday": 23,
    "avgResponseTimeMinutes": 38,
    "resourcesDeployed": 15,
    "resourcesAvailable": 34,
    "pendingAssignment": 12,
    "sosReceived": 3,
    "aiAccuracyRate": 0.94
  }
}
```

---

### GET `/dashboard/map-data`
Get all active incidents and resources for map rendering.

**Auth Required:** Yes (AUTHORITY and above)

**Query Parameters:** `district`, `state`, `includeResolved` (boolean)

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "incidents": [
      {
        "incidentId": "INC-2024-00000001",
        "title": "Flood in residential area",
        "incidentType": "FLOOD",
        "status": "ASSIGNED",
        "coordinates": { "latitude": 20.2961, "longitude": 85.8245 },
        "severityBand": "CRITICAL",
        "severityScore": 9
      }
    ],
    "resources": [
      {
        "resourceId": "res-001",
        "name": "ODRAF Boat Unit 2",
        "type": "RESCUE_BOAT",
        "status": "EN_ROUTE",
        "coordinates": { "latitude": 20.3100, "longitude": 85.8100 }
      }
    ],
    "heatmapData": [
      { "lat": 20.2961, "lng": 85.8245, "weight": 0.9 }
    ]
  }
}
```

---

### GET `/dashboard/incident-trend`
Get incident trend data for chart.

**Auth Required:** Yes (AUTHORITY and above)

**Query Parameters:** `district`, `days` (default: 7)

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "labels": ["Jan 9", "Jan 10", "Jan 11", "..."],
    "datasets": {
      "total": [12, 8, 23, 45, 31, 19, 47],
      "critical": [2, 1, 5, 9, 7, 3, 8],
      "resolved": [10, 7, 18, 36, 25, 16, 23]
    }
  }
}
```

---

## 9.6 Analytics APIs

### GET `/analytics/summary`
Get analytics summary for a period.

**Auth Required:** Yes (AUTHORITY and above)

**Query Parameters:** `district`, `state`, `from`, `to`, `granularity` (hourly|daily|weekly)

**Response:** `200 OK` — aggregated analytics object

---

### GET `/analytics/response-time`
Get response time analytics.

**Auth Required:** Yes (AUTHORITY and above)

**Response:** `200 OK` — response time breakdown by type and severity

---

### GET `/analytics/resource-utilization`
Get resource utilization metrics.

**Auth Required:** Yes

**Response:** `200 OK`

---

### POST `/analytics/export`
Request analytics export (PDF/CSV).

**Auth Required:** Yes (AUTHORITY and above)

**Request:**
```json
{
  "format": "PDF",
  "from": "2024-01-01T00:00:00Z",
  "to": "2024-01-31T23:59:59Z",
  "district": "Khurda",
  "includeCharts": true
}
```
**Response:** `202 Accepted`
```json
{
  "success": true,
  "data": {
    "reportId": "report-uuid-001",
    "message": "Report generation started. You will be notified when ready."
  }
}
```

---

## 9.7 Notification APIs

### GET `/notifications`
Get notifications for current user.

**Auth Required:** Yes

**Query Parameters:** `isRead`, `type`, `page`, `limit`

**Response:** `200 OK` — paginated notifications

---

### PUT `/notifications/:id/read`
Mark a notification as read.

**Auth Required:** Yes

**Response:** `200 OK`

---

### PUT `/notifications/read-all`
Mark all notifications as read.

**Auth Required:** Yes

**Response:** `200 OK`

---

### POST `/notifications/broadcast`
Send a broadcast alert to a district/state.

**Auth Required:** Yes (STATE_OFFICER, ADMIN)

**Request:**
```json
{
  "title": "Cyclone Warning",
  "body": "A severe cyclone is expected to make landfall in 6 hours. All residents in coastal areas please evacuate immediately.",
  "targetDistrict": "Puri",
  "targetState": "Odisha",
  "channels": ["push", "sms"],
  "priority": "URGENT"
}
```
**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "recipientCount": 12450,
    "deliveryStatus": "QUEUED"
  }
}
```

---

## 9.8 Admin APIs

### GET `/admin/users`
Get all users (paginated).

**Auth Required:** Yes (ADMIN only)

**Query Parameters:** `role`, `district`, `isActive`, `search`, `page`, `limit`

**Response:** `200 OK` — paginated user list

---

### POST `/admin/users`
Create a new user account (admin-created authority/admin users).

**Auth Required:** Yes (ADMIN only)

**Request:** User creation payload with role

**Response:** `201 Created`

---

### PUT `/admin/users/:uid/role`
Update user role.

**Auth Required:** Yes (ADMIN only)

**Request:**
```json
{
  "role": "DISTRICT_OFFICER",
  "district": "Khurda",
  "reason": "Promoted to district officer"
}
```
**Response:** `200 OK`

---

### PUT `/admin/users/:uid/deactivate`
Deactivate a user account.

**Auth Required:** Yes (ADMIN only)

**Response:** `200 OK`

---

### GET `/admin/audit-logs`
Get audit logs.

**Auth Required:** Yes (ADMIN only)

**Query Parameters:** `userId`, `action`, `resource`, `from`, `to`, `page`, `limit`

**Response:** `200 OK` — paginated audit log

---

### GET `/admin/system-stats`
Get platform-wide system statistics.

**Auth Required:** Yes (ADMIN only)

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "totalUsers": 15430,
    "activeToday": 2341,
    "totalIncidents": 98432,
    "aiProcessingQueue": 12,
    "systemHealth": "HEALTHY",
    "geminiApiUsage": { "requestsToday": 4521, "costUSD": 4.23 }
  }
}
```

---

### PUT `/admin/settings`
Update system settings.

**Auth Required:** Yes (ADMIN only)

**Request:** Partial settings object

**Response:** `200 OK`

---

## 9.9 Standard Error Responses

All errors follow this format:

```json
{
  "success": false,
  "error": {
    "code": "INCIDENT_NOT_FOUND",
    "message": "The requested incident does not exist or you do not have access.",
    "statusCode": 404,
    "timestamp": "2024-01-15T10:30:00Z",
    "requestId": "req-uuid-001"
  }
}
```

**HTTP Status Codes:**

| Code | Meaning |
|------|---------|
| `200` | Success |
| `201` | Created |
| `202` | Accepted (async) |
| `400` | Bad Request (validation error) |
| `401` | Unauthorized (missing/invalid token) |
| `403` | Forbidden (insufficient permissions) |
| `404` | Not Found |
| `409` | Conflict (duplicate resource) |
| `422` | Unprocessable Entity |
| `429` | Too Many Requests (rate limited) |
| `500` | Internal Server Error |
| `503` | Service Unavailable |

---

*Next: [User Roles & Permissions →](./10-user-roles.md)*
