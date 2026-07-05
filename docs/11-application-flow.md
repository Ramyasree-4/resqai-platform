# Section 11 – Application Flow

---

## 11.1 Citizen User Journey

### 11.1.1 First-Time Citizen Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                     CITIZEN FIRST-TIME JOURNEY                       │
└─────────────────────────────────────────────────────────────────────┘

[Landing Page]
    │
    ├─── Click "Report Emergency" (no login) ──► [Quick SOS Form]
    │                                                    │
    │                                           GPS auto-captured
    │                                                    │
    │                                        [SOS Submitted] ──► END
    │
    └─── Click "Sign Up" ──► [Registration Form]
              │
    Fill: Name, Phone, Email, Password, District, State
              │
    [OTP Verification]
              │
    [Guided Tour] (role-specific onboarding)
              │
    [Citizen Dashboard]
```

### 11.1.2 Citizen Incident Report Flow

```
[Citizen Dashboard]
        │
        │ Click "Report Emergency"
        ▼
[Step 1: Incident Type Selection]
  ○ Flood  ○ Fire  ○ Earthquake  ○ Landslide  ○ Medical  ○ Other
        │
        ▼
[Step 2: Location]
  GPS auto-detected ──► Show on map preview
  Manual override available (type address → Maps autocomplete)
        │
        ▼
[Step 3: Description]
  - Text description (mandatory)
  - People affected (number input)
  - Urgency (Low/Medium/High/Critical — user's assessment)
        │
        ▼
[Step 4: Media Upload]
  - Up to 5 photos/videos
  - Optional (skip allowed)
        │
        ▼
[Step 5: Review & Submit]
  - Preview all entered data
  - Confirm location on map
  - Submit button
        │
        ▼
[Submission Processing]
  - Instant acknowledgement screen
  - Incident ID shown: INC-2024-00000001
  - "Your report is being analyzed by AI..."
        │
        ▼
[Citizen Dashboard – My Reports]
  - New report appears in list
  - Status: SUBMITTED → AI PROCESSING → TRIAGED
  - Push notification sent
```

### 11.1.3 Citizen Tracking Flow

```
[My Reports List]
        │
        │ Click on a report
        ▼
[Incident Tracker Page]
  ┌─────────────────────────────────┐
  │ Status Timeline                  │
  │ ✅ Submitted       10:30 AM      │
  │ ✅ AI Analysis     10:32 AM      │
  │ ✅ Acknowledged    10:45 AM      │
  │ 🔵 Assigned        11:00 AM      │
  │ ○  In Progress                   │
  │ ○  Resolved                      │
  └─────────────────────────────────┘
  
  Assigned Team: ODRAF Boat Unit 3
  Contact: +91-XXXXXXXXXX
  ETA: ~25 minutes
  
  [Comment Section — public thread]
```

---

## 11.2 Authority User Journey

### 11.2.1 Authority Login and Dashboard Load Flow

```
[Login Page]
      │
      │ Enter credentials + 2FA OTP
      ▼
[Firebase Auth] → JWT issued with role: AUTHORITY
      │
      ▼
[Authority Dashboard Loads]
  │
  ├── Firestore onSnapshot listener: incidents (district, status ≠ CLOSED)
  ├── Firestore onSnapshot listener: resources (district)
  ├── API call: GET /dashboard/stats
  ├── API call: GET /dashboard/map-data
  └── FCM background notification subscription
  
  All load within ~2 seconds
```

### 11.2.2 Authority Incident Triage Flow

```
[Authority Dashboard]
        │
        │ New incident arrives (Firestore real-time push)
        ▼
[Incident Queue – Top of Priority List]
  INC-2024-00000001
  🔴 CRITICAL | Flood | Khurda | 800 people | Severity: 9/10
        │
        │ Click "View Details"
        ▼
[Incident Details Page]
  ┌──────────────────┐  ┌──────────────────────────────────────────┐
  │  Incident Info   │  │         AI Analysis Panel                 │
  ├──────────────────┤  ├──────────────────────────────────────────┤
  │ Type: FLOOD      │  │ 🤖 Severity: 9/10 — CRITICAL             │
  │ District: Khurda │  │                                          │
  │ Affected: 800    │  │ Situation Summary:                       │
  │ Status: TRIAGED  │  │ "A critical flood emergency is active    │
  │                  │  │ in the Khandagiri area affecting ~800    │
  │ Location Map ↓   │  │ residents. Electricity is cut. Children  │
  │ [Mini Map]       │  │ and elderly require priority rescue."    │
  │                  │  │                                          │
  │ Media Files:     │  │ AI Reasoning:                            │
  │ [Photo 1][Vid 1] │  │ • High affected population (800)         │
  │                  │  │ • Vulnerable groups identified           │
  │                  │  │ • Rapidly rising water level             │
  │                  │  │ • Loss of critical infrastructure        │
  │                  │  │                                          │
  │                  │  │ Recommended Resources:                   │
  │                  │  │ • 5× Rescue Boats (IMMEDIATE)            │
  │                  │  │ • 2× Medical Units (HIGH)                │
  │                  │  │ • 1× Helicopter (MEDIUM)                 │
  └──────────────────┘  └──────────────────────────────────────────┘
        │
        │ Authority reviews and decides
        ▼
  [Accept AI Recommendation] ──► Opens Resource Assignment Panel
  [Override with custom plan] ──► Opens Resource Assignment Panel (pre-cleared)
        │
        ▼
[Resource Assignment Panel]
  Available in district:
  ✅ ODRAF Boat Unit 2 — 2.3 km away
  ✅ ODRAF Boat Unit 3 — 4.1 km away
  ✅ NDRF Medical Team A — 5.0 km away
  
  [Select Units] → [Assign & Dispatch]
        │
        ▼
[Confirmation]
  - Incident status → ASSIGNED
  - Resources status → DEPLOYED
  - Citizen notified via push + SMS
  - Assigned teams notified
  - Map updates in real-time
```

### 11.2.3 Authority Situation Report Flow

```
[Authority Dashboard]
        │
        │ Click "Generate Report"
        ▼
[Report Configuration]
  - Period: Today / Last 7 Days / Custom
  - Scope: District / State
  - Include: Charts, Resource Utilization, AI Metrics
        │
        ▼
[AI Generates Report Summary]
  Gemini creates narrative:
  "As of 15 January 2024, Khurda district has recorded 47 active 
   incidents with 8 classified as critical..."
        │
        ▼
[Report Preview]
  - Structured PDF layout
  - Charts embedded
  - KPI tables
        │
        ▼
[Download PDF] or [Share via Email]
```

---

## 11.3 AI Processing Flow

```
INCIDENT SUBMITTED (status: SUBMITTED)
        │
        │ IncidentService.create()
        │  → Save to Firestore
        │  → Upload media to GCS
        │  → Enqueue Cloud Task
        ▼
CLOUD TASKS QUEUE
        │
        │ Task delivered to /internal/ai/process
        ▼
AI PROCESSING SERVICE (status: AI_PROCESSING)
        │
        ├─ Step 1: Build Gemini Prompt
        │    Input:
        │    - incidentType (user-provided)
        │    - description (free text)
        │    - affectedPeople
        │    - location.district + state
        │    - geohash (for population density lookup)
        │    - mediaAnalysis (optional: image description via Gemini Vision)
        │    - weatherContext (optional: weather API data)
        │
        ├─ Step 2: Call Gemini 1.5 Pro
        │    Prompt template: [See Section 14]
        │
        ├─ Step 3: Parse Structured Response
        │    {
        │      classification, confidence,
        │      severityScore, severityBand,
        │      priorityScore,
        │      recommendations[],
        │      situationSummary,
        │      reasoning[],
        │      isDuplicate, duplicateOf
        │    }
        │
        ├─ Step 4: Duplicate Check
        │    Query nearby incidents (same geohash prefix, last 2 hours)
        │    Calculate similarity score
        │    Flag if > 0.85 threshold
        │
        ├─ Step 5: Update Firestore
        │    incident.aiAnalysis = { ...parsed response }
        │    incident.status = TRIAGED
        │    incident.updatedAt = now()
        │
        ├─ Step 6: Trigger Notifications
        │    - All authority users in district → "New Critical Incident"
        │    - Citizen → "Your report has been analyzed"
        │
        └─ Step 7: Cluster Check
             Query: How many CRITICAL incidents in this district in last 1 hour?
             If ≥ 5 → Trigger Mass Casualty Protocol
                     → Alert State Officer
                     → Send broadcast notification

FIRESTORE LISTENER FIRES → All authority clients update in < 2 seconds
```

### 11.3.1 AI Fallback Flow

```
Gemini API Call
        │
        │ Circuit Breaker: Is Gemini available?
        │
        ├─ YES ──► Normal AI flow (above)
        │
        └─ NO (circuit open) ──► FALLBACK SERVICE
              │
              Rule-based classifier:
              - Keyword match: "flood", "water", "drowning" → FLOOD
              - Keyword match: "fire", "burning", "smoke" → FIRE
              - Affected people > 1000 → severity HIGH
              - Affected people > 5000 → severity CRITICAL
              - Default: severity MEDIUM
              │
              Generate basic rule-based recommendation
              Flag: aiAnalysis.fallbackUsed = true
              │
              Update Firestore + notify (with fallback flag visible)
```

---

## 11.4 Admin Flow

### 11.4.1 Admin Daily Operations

```
[Admin Dashboard – Morning Check]
        │
        ├── Check platform health: all services GREEN?
        ├── Review overnight incident summary
        ├── Check AI processing queue depth
        ├── Review user registration requests (authority/NGO)
        └── Check any pending resource requests
        
[Admin – User Approval Flow]
        │
        │ New authority account requests in queue
        ▼
[User Management → Pending Approval]
  - Review submitted credentials
  - Verify government ID / NGO certificate
  - Approve → Assign district + role
  - OR Reject with reason (email sent)
        
[Admin – System Configuration Flow]
        │
        │ Configure AI thresholds
        ▼
[Settings Page]
  Critical Severity Threshold: [7] ←adjustable
  Escalation Delay: [15] minutes
  Cluster Detection: [5] incidents in [1] hour
  Mass Casualty Mode: [5] CRITICAL in [1] hour
        │
        │ Save → audit logged
        ▼
[Changes effective immediately via Firestore settings listener]
```

---

## 11.5 SOS Emergency Flow (Priority Path)

```
CITIZEN TAPS SOS BUTTON
        │
        │ No form — just tap
        ▼
[Permission Check]
        │
        ├─ GPS available ──► Auto-capture coordinates
        └─ GPS unavailable ──► "Please enable GPS for SOS"
                                 Fallback: IP-based location
        │
        ▼
[Optional: Voice/text quick note]
"Describe emergency in 1 sentence" (10-second timeout then auto-submit)
        │
        ▼
POST /incidents/sos
        │
        │ Server:
        │ 1. Create incident with CRITICAL severity (no AI processing wait)
        │ 2. Immediately alert all AUTHORITY users in district
        │ 3. Find nearest AVAILABLE resource
        │ 4. Auto-assign nearest resource (or flag for immediate human review)
        │ 5. Trigger AI analysis async (updates later)
        ▼
[Citizen sees]
  "🆘 SOS Received!
  Nearest unit: ODRAF Boat Unit 2 — 2.3 km away
  Reference: INC-2024-00000003"
  
  [Stay on screen — live tracking of assigned unit]
```

---

## 11.6 Escalation Flow

```
INCIDENT STATUS: TRIAGED
        │
        │ Timer starts: 15 minutes (configurable)
        │
        │ No assignment within 15 minutes?
        ▼
[AUTO-ESCALATION TRIGGER]
  
  Level 1: District Officer notified
  Incident.escalation.escalatedTo = "DISTRICT_OFFICER"
        │
        │ Still no assignment after 30 minutes?
        ▼
  Level 2: State Officer notified
  Incident.escalation.escalatedTo = "STATE_OFFICER"
        │
        │ Still no assignment after 60 minutes?
        ▼
  Level 3: NDMA Liaison alerted
  Emergency broadcast option activated
```

---

*Next: [UI Wireframes →](./12-ui-wireframes.md)*
