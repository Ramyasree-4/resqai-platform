# Section 10 – User Roles & Permissions

---

## 10.1 Role Hierarchy

```
                        ┌─────────────┐
                        │    ADMIN    │  ◄── Full platform access
                        └──────┬──────┘
                               │
                    ┌──────────▼──────────┐
                    │   STATE_OFFICER     │  ◄── State-level operations
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  DISTRICT_OFFICER   │  ◄── District-level operations
                    └──────────┬──────────┘
                               │
               ┌───────────────┼───────────────┐
               │               │               │
        ┌──────▼──────┐  ┌─────▼─────┐  ┌─────▼──────┐
        │  AUTHORITY  │  │    NGO    │  │ VOLUNTEER  │
        └─────────────┘  └───────────┘  └────────────┘
                               
                        ┌─────────────┐
                        │   CITIZEN   │  ◄── Public user
                        └─────────────┘
```

---

## 10.2 Role Definitions

### CITIZEN
General public user. Can report emergencies and track their reports.

### AUTHORITY
Local emergency responder, police, fire, NDRF/SDRF team member. Can manage incidents in their assigned area.

### NGO
Non-governmental organization field worker. Can view incidents in their area and coordinate relief activities.

### VOLUNTEER
Registered volunteer. Can receive incident alerts nearby and update their availability.

### DISTRICT_OFFICER
Government district emergency management officer. Full control over all incidents and resources in their district.

### STATE_OFFICER
State Disaster Management Authority (SDMA) officer. Oversight of all districts in their state, can issue broadcasts.

### ADMIN
Platform superadmin. Full access to all system functions, user management, and configuration.

---

## 10.3 Permission Matrix

### Incident Permissions

| Permission | CITIZEN | AUTHORITY | NGO | VOLUNTEER | DISTRICT_OFFICER | STATE_OFFICER | ADMIN |
|-----------|---------|-----------|-----|-----------|-----------------|--------------|-------|
| Submit own incident | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| View own incidents | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| View incidents in own district | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| View incidents in all districts | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| Update incident status | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ |
| Assign resources to incident | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ |
| Escalate incident | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ |
| Close/resolve incident | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ |
| Delete incident | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Add internal note | ❌ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ |
| Add public comment | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Submit SOS | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Override AI recommendation | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ |

---

### Resource Permissions

| Permission | CITIZEN | AUTHORITY | NGO | VOLUNTEER | DISTRICT_OFFICER | STATE_OFFICER | ADMIN |
|-----------|---------|-----------|-----|-----------|-----------------|--------------|-------|
| View resources near location | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| View all resources in district | ❌ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ |
| View all resources in state | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| Add new resource | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| Edit resource details | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| Update resource status | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ |
| Update resource location | ❌ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ |
| Delete resource | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Request resources from state | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| Approve resource requests | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |

---

### Dashboard & Analytics Permissions

| Permission | CITIZEN | AUTHORITY | NGO | VOLUNTEER | DISTRICT_OFFICER | STATE_OFFICER | ADMIN |
|-----------|---------|-----------|-----|-----------|-----------------|--------------|-------|
| View citizen dashboard | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| View authority dashboard | ❌ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ |
| View district analytics | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ |
| View state analytics | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| View national analytics | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Export analytics reports | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ |
| View AI accuracy metrics | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| View map operations view | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

---

### Notification Permissions

| Permission | CITIZEN | AUTHORITY | NGO | VOLUNTEER | DISTRICT_OFFICER | STATE_OFFICER | ADMIN |
|-----------|---------|-----------|-----|-----------|-----------------|--------------|-------|
| Receive own report updates | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Receive district alerts | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Send district broadcast | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| Send state broadcast | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| Send national broadcast | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

---

### User & Admin Permissions

| Permission | CITIZEN | AUTHORITY | NGO | VOLUNTEER | DISTRICT_OFFICER | STATE_OFFICER | ADMIN |
|-----------|---------|-----------|-----|-----------|-----------------|--------------|-------|
| View own profile | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Edit own profile | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| View other users | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| Create user accounts | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Update user roles | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Deactivate users | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| View audit logs | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Configure system settings | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Manage resource registry | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |

---

## 10.4 Role-Specific Dashboard Views

### CITIZEN Dashboard
- My Reports (list + status)
- Report New Incident (prominent CTA)
- SOS Button
- Nearby Resources map
- Notifications

### AUTHORITY Dashboard
- Active Incidents Queue (severity-sorted)
- AI Recommendations Panel
- Resource Map
- Assignment Controls
- Notifications

### NGO Dashboard
- Incident map (read-only operations)
- Relief camp capacity overview
- Volunteer coordination panel
- Communication thread

### VOLUNTEER Dashboard
- Nearby incidents (alerts)
- My availability toggle (On Duty / Off Duty)
- Assigned tasks

### DISTRICT_OFFICER Dashboard
- Full district operations dashboard
- All incidents in district
- Resource inventory management
- District analytics
- Situation reports

### STATE_OFFICER Dashboard
- Multi-district overview
- State-level KPIs and map
- Cross-district resource rebalancing
- State broadcast controls
- Escalated incidents queue

### ADMIN Dashboard
- Platform health metrics
- User management
- Resource registry
- AI performance metrics
- System settings
- Audit logs

---

## 10.5 Authentication Rules

| Role | Registration Method | Requires Verification |
|------|--------------------|-----------------------|
| CITIZEN | Self-registration (web/app) | Email/phone OTP |
| AUTHORITY | Self-registration + Admin approval | ID verification |
| NGO | Organization registration + Admin approval | NGO certificate |
| VOLUNTEER | Self-registration | Email verification |
| DISTRICT_OFFICER | Admin-created | Government ID |
| STATE_OFFICER | Admin-created | Government ID |
| ADMIN | Direct database creation by root admin | — |

**2FA (Two-Factor Authentication) Requirements:**
- DISTRICT_OFFICER: Mandatory
- STATE_OFFICER: Mandatory
- ADMIN: Mandatory
- AUTHORITY: Strongly recommended (configurable)
- Others: Optional

---

## 10.6 Data Scope by Role

Firestore security rules enforce data scoping:

| Role | Reads | Writes |
|------|-------|--------|
| CITIZEN | Own incidents + public resources | Own incidents + SOS |
| AUTHORITY | District incidents + district resources | District incidents (status/assign) |
| NGO | District incidents (read-only) | Own organization data |
| VOLUNTEER | Nearby incidents (limited fields) | Location updates |
| DISTRICT_OFFICER | Full district data | Full district operations |
| STATE_OFFICER | Full state data | State operations + broadcasts |
| ADMIN | All data | All data |

---

*Next: [Application Flow →](./11-application-flow.md)*
