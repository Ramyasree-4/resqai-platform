# Section 02 – Functional Requirements

---

## 2.1 Citizen Module

### FR-CIT-001: User Registration & Profile
- Citizens shall be able to register using email, phone number, or Google OAuth
- System shall collect: name, phone, address, district, state, pincode
- Citizens shall complete profile with emergency contacts (up to 3)
- Profile shall include disability/special needs flag for priority rescue tagging

### FR-CIT-002: Incident Reporting
- Citizens shall submit emergency reports via web/mobile form
- Report form shall collect: incident type, description, location (auto GPS or manual), photos/videos (up to 5 files), number of people affected, urgency level (user-stated)
- System shall auto-capture device GPS coordinates if permission granted
- System shall support manual address entry with Google Maps autocomplete fallback
- Citizens shall receive an instant report acknowledgement with a unique Incident ID
- System shall provide estimated response time based on AI assessment

### FR-CIT-003: Incident Tracking
- Citizens shall track their submitted reports in real-time
- Status progression: Submitted → AI Processing → Acknowledged → Assigned → In Progress → Resolved
- Citizens shall receive push/SMS notifications on every status change
- Tracking page shall display assigned rescue team details once assigned

### FR-CIT-004: SOS Emergency Broadcast
- One-tap SOS button shall broadcast GPS location to nearest available rescue units
- SOS shall auto-populate a CRITICAL severity incident with pre-filled AI template
- SOS broadcast shall notify all online authority users in the affected district instantly

### FR-CIT-005: Resource Locator
- Citizens shall view nearest: hospitals, shelters, relief camps, police stations, fire stations
- Map shall show real-time availability status of shelters (capacity indicator)
- Distance and estimated travel time shall be displayed

### FR-CIT-006: Citizen Notifications
- Citizens shall receive notifications via: in-app, push notification, SMS, email
- Notifications include: report status updates, nearby alerts, shelter availability

---

## 2.2 Authority Module

### FR-AUTH-001: Authority Dashboard
- Authorities shall have a real-time operations dashboard
- Dashboard shall display: active incidents count, severity distribution, assigned/unassigned incidents, resource utilization, map overview
- Dashboard shall auto-refresh every 30 seconds with live Firestore listeners

### FR-AUTH-002: Incident Management
- Authorities shall view all incidents in a sortable/filterable list
- Default sort: AI Severity Score (highest first)
- Filter options: district, incident type, status, date range, severity level
- Authority shall be able to accept, reject, reassign, or escalate incidents
- Authority shall be able to add internal notes to any incident
- Authority shall be able to close/resolve incidents with resolution notes

### FR-AUTH-003: AI Recommendations Review
- Authority shall see AI-generated recommendations for each incident
- Recommendations include: severity score, priority rank, suggested resources, situation summary
- Authority shall see the AI reasoning/explanation alongside each recommendation
- Authority shall be able to override AI recommendation with manual decision (with reason)

### FR-AUTH-004: Resource Deployment
- Authority shall view all available resources on a live map
- Authority shall assign specific resources to specific incidents
- System shall warn if selected resource is already deployed or out of range
- Authority shall receive confirmation when field unit accepts/declines assignment

### FR-AUTH-005: Inter-Agency Coordination
- Authority shall be able to escalate incidents to state level
- Authority shall be able to request mutual aid from neighboring districts
- System shall send automated notifications to relevant agencies on escalation
- Authority shall access a shared incident comment thread for coordination

### FR-AUTH-006: Situation Reports
- Authority shall generate AI-assisted situation reports for any time period
- Reports shall include: incident statistics, response metrics, resource utilization, casualties, pending actions
- Reports shall be exportable as PDF and CSV

---

## 2.3 Admin Module

### FR-ADM-001: User Management
- Admin shall create, edit, deactivate, and delete user accounts
- Admin shall assign and modify roles for any user
- Admin shall view full user activity logs
- Admin shall manage organization/agency registrations

### FR-ADM-002: Resource Registry Management
- Admin shall maintain master registry of all rescue resources
- Resource types: ambulance, fire truck, rescue boat, helicopter, rescue team, NGO unit, shelter, hospital
- Each resource has: name, type, capacity, location, contact, status, assigned district

### FR-ADM-003: System Configuration
- Admin shall configure AI severity thresholds and escalation rules
- Admin shall configure notification templates
- Admin shall configure district-to-agency routing rules
- Admin shall manage system settings (maintenance mode, feature flags)

### FR-ADM-004: Platform Analytics
- Admin shall view platform-wide analytics: total incidents, response times, user activity
- Admin shall generate compliance and audit reports
- Admin shall view Gemini AI usage and cost metrics

### FR-ADM-005: Audit Trail
- System shall log every action performed by every user
- Audit log includes: user ID, action, timestamp, IP address, affected record
- Admin shall search and export audit logs

---

## 2.4 AI Engine Module

### FR-AI-001: Incident Classification
- AI engine shall classify every submitted incident into a disaster type category
- Categories: Flood, Cyclone, Earthquake, Landslide, Fire, Medical Emergency, Industrial Accident, Drought, Civil Unrest, Other
- Classification confidence score (0–1) shall be stored with each result

### FR-AI-002: Severity Assessment
- AI shall assign a severity score from 1 (minor) to 10 (catastrophic) to each incident
- Score shall be based on: incident type, description text, number of people affected, location vulnerability, time of day, weather data
- Severity bands: 1–3 (Low), 4–6 (Medium), 7–8 (High), 9–10 (Critical)

### FR-AI-003: Priority Ranking
- AI shall maintain a continuously updated priority queue across all active incidents
- Priority algorithm considers: severity score, time since report, population density, resource proximity, incident escalation history
- Priority rank updates automatically as new incidents arrive or status changes

### FR-AI-004: Resource Recommendation
- AI shall recommend specific resource types and quantities for each incident
- Recommendation considers: incident type, severity, affected population, available resources, distance/travel time
- Recommendations shall include primary and fallback resource options

### FR-AI-005: Situation Summary Generation
- AI shall generate a natural language situation summary for each incident
- Summary includes: what happened, where, how many affected, current status, recommended actions
- Summaries shall be regenerated when incident is updated

### FR-AI-006: Explainable AI Output
- Every AI decision shall include a human-readable explanation
- Explanation format: "This incident is rated CRITICAL (9/10) because: [3–5 bullet point reasons]"
- Authorities shall be able to provide feedback on AI accuracy (thumbs up/down)

### FR-AI-007: Duplicate Detection
- AI shall identify potentially duplicate reports (same location, same time, similar description)
- Duplicates shall be flagged and linked, not deleted
- Authority shall confirm or reject duplicate flagging

### FR-AI-008: Trend Analysis
- AI shall identify emerging incident clusters (e.g., 5+ flood reports in one district in 2 hours)
- Cluster detection shall trigger automatic alerts to state authorities
- AI shall correlate incident patterns with weather API data

---

## 2.5 Analytics Module

### FR-ANA-001: Real-Time Dashboard Analytics
- System shall display live KPIs: active incidents, response rate, average resolution time, resources deployed
- Charts: incident trend over time, type distribution, severity heatmap, district-wise breakdown

### FR-ANA-002: Historical Analytics
- System shall store and serve historical data for trend analysis
- Date range filters: today, last 7 days, last 30 days, custom range, by disaster event
- Comparative analytics: current period vs. previous period

### FR-ANA-003: Geospatial Analytics
- System shall generate incident density heatmaps by district/state
- Resource coverage gap analysis on map
- Evacuation route analysis overlay

### FR-ANA-004: Performance Analytics
- Response time analytics by agency, district, incident type
- AI recommendation acceptance rate vs. override rate
- Resource utilization efficiency metrics

### FR-ANA-005: Export & Reporting
- All analytics exportable as PDF, Excel, CSV
- Scheduled report delivery via email (daily/weekly/on-event)

---

## 2.6 Notifications Module

### FR-NOT-001: Multi-Channel Notifications
- System shall deliver notifications via: in-app (real-time), push notification (FCM), SMS (Twilio/MSG91), email (SendGrid)
- Notification preference management per user

### FR-NOT-002: Automated Triggers
- New critical incident in jurisdiction → notify all authority users
- Incident assigned to unit → notify the assigned unit
- Status change → notify the reporting citizen
- SOS broadcast → notify all available nearby responders
- Cluster detected → notify state authority
- Resource capacity threshold crossed → notify admin

### FR-NOT-003: Notification Center
- In-app notification center with read/unread state
- Notification history (last 90 days)
- Bulk actions: mark all as read, clear all

### FR-NOT-004: Emergency Broadcast
- Admin/State authority shall be able to send broadcast alerts to all citizens in a district/state
- Broadcast delivered via push, SMS, and in-app simultaneously

---

## 2.7 Maps Module

### FR-MAP-001: Live Incident Map
- Map shall display all active incidents as markers color-coded by severity
- Click on marker → show incident summary panel
- Map shall auto-center on highest-severity cluster

### FR-MAP-002: Resource Map
- Map shall display all available resources with type icons
- Filter resources by type, status, district
- Click resource → show details and assignment options

### FR-MAP-003: Heatmap View
- Toggle heatmap overlay showing incident density
- Heatmap color scale from green (low) to red (critical)

### FR-MAP-004: Route Planning
- Show optimal route from resource location to incident location
- Estimated travel time considering road conditions
- Alternative route suggestions

### FR-MAP-005: Infrastructure Layer
- Toggleable overlays: hospitals, shelters, police stations, fire stations
- Real-time availability status on each facility marker

---

## 2.8 Authentication Module

### FR-ATH-001: Multi-Provider Authentication
- Support: email/password, Google OAuth, phone OTP
- Two-Factor Authentication (2FA) mandatory for Authority and Admin roles

### FR-ATH-002: Session Management
- JWT access tokens (15-minute expiry) + refresh tokens (7-day expiry)
- Automatic token refresh with silent re-authentication
- Force logout on role change or security event

### FR-ATH-003: Password & Account Security
- Password policy: min 8 chars, 1 uppercase, 1 number, 1 special char
- Account lockout after 5 failed attempts (30-minute lockout)
- Password reset via email OTP

---

## 2.9 Resource Management Module

### FR-RES-001: Resource Inventory
- Complete registry of: rescue teams, vehicles, medical units, shelters, helicopters, boats
- Real-time availability status: Available, Deployed, Maintenance, Unavailable
- Resource capacity tracking (e.g., shelter: 200/500 capacity)

### FR-RES-002: Resource Assignment
- Authority shall assign resources to incidents from inventory
- System shall validate resource availability before assignment
- Assignment history per resource and per incident

### FR-RES-003: Resource Tracking
- Field units shall update their GPS location every 60 seconds (mobile app)
- Live tracking visible on authority map view

### FR-RES-004: Resource Request
- District authority shall request additional resources from state pool
- State authority shall approve/reject/fulfill resource requests

---

## 2.10 Incident Management Module

### FR-INC-001: Incident Lifecycle
- States: Draft → Submitted → AI Processing → Triaged → Assigned → In Progress → Resolved → Closed → Archived
- Automated state transitions where AI processing is complete
- Manual transitions require authority action with timestamp

### FR-INC-002: Incident Linking
- Authority shall link related incidents (same event, different reports)
- System shall suggest potential links based on AI proximity analysis
- Linked incidents share updates and resource assignments

### FR-INC-003: Incident Escalation
- Incidents exceeding severity threshold (≥7) shall auto-escalate after 15 minutes without assignment
- Escalation path: District Officer → State Officer → NDMA Liaison
- Each escalation triggers notification to the next authority level

### FR-INC-004: Mass Casualty Protocol
- When ≥5 CRITICAL incidents detected in one district within 1 hour, system activates Mass Casualty Mode
- Mass Casualty Mode: auto-alerts all state resources, activates emergency broadcast, notifies NDMA

---

*Next: [Non-Functional Requirements →](./03-non-functional-requirements.md)*
