# Section 12 – Complete UI Wireframes

---

## 12.1 Landing Page

```
┌──────────────────────────────────────────────────────────────────────┐
│  NAVBAR                                                               │
│  [🔴 ResQAI Logo]          [About] [Features] [Login] [Sign Up]      │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│  HERO SECTION                        [Background: aerial disaster img]│
│                                                                       │
│  AI-Powered Disaster Response                                         │
│  When Every Second Counts                                             │
│                                                                       │
│  ResQAI transforms emergency chaos into coordinated action            │
│  using Google Gemini AI — connecting citizens, responders,            │
│  and authorities in real-time.                                        │
│                                                                       │
│  [🆘 Report Emergency Now]    [👁 View Live Map]                      │
│                                                                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐               │
│  │ 1.4B     │ │ 83%      │ │ 5 sec    │ │ 99.9%    │               │
│  │ Citizens │ │ Faster   │ │ AI Triage│ │ Uptime   │               │
│  │ Protected│ │ Response │ │ Time     │ │ SLA      │               │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘               │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│  HOW IT WORKS (3 columns)                                            │
│                                                                       │
│  [📍 Report]        [🤖 AI Analyzes]     [🚁 Rescue Dispatched]      │
│  Citizen submits    Gemini AI classifies  Nearest resource            │
│  incident with GPS  severity & recommends dispatched in minutes      │
│  location           resources             with live tracking          │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│  LIVE STATISTICS TICKER                                              │
│  🔴 Active Incidents: 47  |  ✅ Resolved Today: 23  |  🚁 Units Deployed: 15│
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│  FEATURES GRID (2x3)                                                 │
│  [Gemini AI] [Real-time Map] [Multi-agency] [Explainable AI]         │
│  [Offline PWA] [Multi-language]                                      │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│  FOOTER                                                              │
│  ResQAI © 2024 | Privacy | Terms | Contact | GitHub                 │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 12.2 Login Page

```
┌──────────────────────────────────────────────────────────────────────┐
│  LEFT PANEL (40%)                    RIGHT PANEL (60%)               │
│                                                                       │
│  [ResQAI Logo]                       ┌──────────────────────────┐   │
│  AI-Powered Disaster Response        │  Welcome Back             │   │
│                                      │                           │   │
│  [Map background showing             │  [Email input]            │   │
│   active incidents]                  │  [Password input]  [👁]   │   │
│                                      │                           │   │
│  "47 emergencies being               │  [□ Remember me]          │   │
│   actively managed right now"        │  [Forgot Password?]       │   │
│                                      │                           │   │
│                                      │  [Sign In ──────────────] │   │
│                                      │                           │   │
│                                      │  ────── or continue ────  │   │
│                                      │  [G  Sign in with Google] │   │
│                                      │  [📱 Sign in with Phone]  │   │
│                                      │                           │   │
│                                      │  Don't have account?      │   │
│                                      │  [Sign Up]                │   │
│                                      └──────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 12.3 Register Page

```
┌──────────────────────────────────────────────────────────────────────┐
│  Create Your Account                                                  │
│                                                                       │
│  Step 1 ●──────○──────○  Basic Info                                  │
│                                                                       │
│  [First Name ──────────]  [Last Name ─────────]                      │
│  [Email Address ────────────────────────────]                        │
│  [Phone Number (+91) ──────────────────────]                         │
│  [Password ─────────────────────────] [👁]                           │
│  [Confirm Password ─────────────────] [👁]                           │
│                                                                       │
│  I am registering as:                                                │
│  ○ Citizen    ○ Authority/Responder    ○ NGO Worker    ○ Volunteer   │
│                                                                       │
│  [State ────────────▼]  [District ──────────▼]                       │
│                                                                       │
│  [✓ Accept Terms & Conditions]                                       │
│                                                                       │
│  [Continue ─────────────────────────────────]                        │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 12.4 Citizen Dashboard

```
┌──────────────────────────────────────────────────────────────────────┐
│ TOPBAR: [ResQAI] [Rajesh Kumar ▼] [🔔 3] [Khurda, Odisha]           │
└──────────────────────────────────────────────────────────────────────┘
┌──────────┐ ┌──────────────────────────────────────────────────────┐
│ SIDEBAR  │ │  MAIN CONTENT                                         │
│          │ │                                                       │
│ 🏠 Home  │ │  ┌─────────────────────────────────────────────────┐ │
│ 📋 My    │ │  │  🆘 EMERGENCY SOS                               │ │
│    Reports│ │  │  Tap to broadcast your location immediately     │ │
│ ➕ Report │ │  │  [    🆘 SOS EMERGENCY BUTTON    ]              │ │
│ 🗺 Map   │ │  └─────────────────────────────────────────────────┘ │
│ 🔔 Alerts│ │                                                       │
│ 👤 Profile│ │  My Recent Reports                  [+ New Report]  │
│ ⚙ Settings│ │  ┌──────────────────────────────────────────────┐  │
│          │ │  │ INC-001 | 🔵 Assigned | Flood | Khandagiri   │  │
│          │ │  │ "200 families trapped..." | Jan 15, 10:30 AM  │  │
│          │ │  ├──────────────────────────────────────────────┤  │
│          │ │  │ INC-002 | ✅ Resolved | Medical | Patia      │  │
│          │ │  │ "Elderly person collapsed..." | Jan 14         │  │
│          │ │  └──────────────────────────────────────────────┘  │
│          │ │                                                       │
│          │ │  Nearby Resources                                     │
│          │ │  ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│          │ │  │🏥 Hospital│ │🏠 Shelter│ │🚒 Fire   │            │
│          │ │  │ 1.2 km   │ │ 2.1 km  │ │ 3.0 km   │            │
│          │ │  │ OPEN     │ │ 342/500 │ │ AVAILABLE│            │
│          │ │  └──────────┘ └──────────┘ └──────────┘            │
└──────────┘ └──────────────────────────────────────────────────────┘
```

---

## 12.5 Authority Dashboard

```
┌──────────────────────────────────────────────────────────────────────┐
│ TOPBAR: [ResQAI OPS] [Dist. Collector ▼] [🔔 12] [Khurda] [LIVE ●] │
└──────────────────────────────────────────────────────────────────────┘
┌──────────┐ ┌──────────────────────────────────────────────────────┐
│ SIDEBAR  │ │  KPI CARDS ROW                                        │
│          │ │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐        │
│ 📊 Dash  │ │  │🔴 47   │ │🟡 8    │ │🟢 15   │ │⏱ 38m  │        │
│ 🚨 Queue │ │  │Active  │ │Critical│ │Deployd │ │Avg Resp│        │
│ 🗺 Map   │ │  └────────┘ └────────┘ └────────┘ └────────┘        │
│ 🚁 Resources│ │                                                    │
│ 📈 Analytics│ │  ┌─────────────────────┐ ┌──────────────────────┐ │
│ 📄 Reports  │ │  │  INCIDENT QUEUE      │ │  OPERATIONS MAP      │ │
│ 🔔 Notifs   │ │  │  (Priority Sorted)   │ │                      │ │
│ ⚙ Settings  │ │  │  🔴 INC-001 Flood    │ │   [Google Map]       │ │
│           │ │  │  Score: 9/10 CRITICAL│ │   🔴 incidents       │ │
│           │ │  │  [View][Assign]      │ │   🟢 resources       │ │
│           │ │  ├─────────────────────┤ │   🔥 heatmap         │ │
│           │ │  │  🔴 INC-007 Fire     │ │                      │ │
│           │ │  │  Score: 8/10 HIGH    │ │                      │ │
│           │ │  │  [View][Assign]      │ │                      │ │
│           │ │  ├─────────────────────┤ │                      │ │
│           │ │  │  🟡 INC-012 Medical  │ │                      │ │
│           │ │  │  Score: 6/10 MEDIUM  │ │                      │ │
│           │ │  └─────────────────────┘ └──────────────────────┘ │
│           │ │                                                       │
│           │ │  INCIDENT TREND (7 days)  SEVERITY DISTRIBUTION      │
│           │ │  [Area Chart ──────────]  [Pie Chart]                │
└──────────┘ └──────────────────────────────────────────────────────┘
```

---

## 12.6 Create Incident Page (Multi-step)

```
┌──────────────────────────────────────────────────────────────────────┐
│  Report Emergency Incident                                            │
│                                                                       │
│  Step: [1. Type] ──●── [2. Location] ──○── [3. Details] ──○── [4. Media] ──○── [5. Review]│
│                                                                       │
│  STEP 1: Select Incident Type                                        │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐│
│  │🌊      │ │🌪       │ │🔥      │ │🏔       │ │⚡      │ │➕      ││
│  │FLOOD   │ │CYCLONE │ │FIRE    │ │LANDSLIDE│ │QUAKE   │ │OTHER   ││
│  │(select)│ │        │ │        │ │         │ │        │ │        ││
│  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘ └────────┘│
│                                                                       │
│  Your urgency level:                                                 │
│  ○ Low   ○ Medium   ● High   ○ Critical                              │
│                                                                       │
│  [Next: Location →]                                                  │
└──────────────────────────────────────────────────────────────────────┘

STEP 2: Location
┌──────────────────────────────────────────────────────────────────────┐
│  📍 Location                          [Use My GPS Location ⟳]       │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │              [Google Maps Component]                           │  │
│  │   Interactive map — tap to pin location                        │  │
│  │   [draggable marker]                                           │  │
│  └───────────────────────────────────────────────────────────────┘  │
│  Address: [Maps autocomplete search bar]                             │
│  District: [auto-filled]    State: [auto-filled]                     │
│                                                                       │
│  [← Back]   [Next: Details →]                                        │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 12.7 Incident Details Page (Authority View)

```
┌──────────────────────────────────────────────────────────────────────┐
│  ← Back to Queue    INC-2024-00000001    🔴 CRITICAL    [Escalate ↑] │
└──────────────────────────────────────────────────────────────────────┘
┌─────────────────────────────┐  ┌──────────────────────────────────┐
│  INCIDENT INFORMATION       │  │  🤖 AI ANALYSIS                  │
├─────────────────────────────┤  ├──────────────────────────────────┤
│  Type:    🌊 FLOOD          │  │  Severity Score                  │
│  Status:  🔵 ASSIGNED       │  │  ┌──────────────────────────┐   │
│  District: Khurda, Odisha   │  │  │  9 / 10   ████████████░  │   │
│  Reported: Jan 15, 10:30 AM │  │  │  CRITICAL                │   │
│  Reporter: Anonymous        │  │  └──────────────────────────┘   │
│  Affected: 800 people       │  │                                  │
│                             │  │  Priority Rank: #1 in District  │
│  LOCATION MAP               │  │                                  │
│  ┌───────────────────────┐  │  │  Situation Summary:             │
│  │   [Mini Google Map]   │  │  │  "Critical flood emergency in   │
│  │   📍 Khandagiri area  │  │  │  Khandagiri area affecting ~800 │
│  └───────────────────────┘  │  │  residents. Immediate rescue    │
│                             │  │  required for trapped families."│
│  DESCRIPTION                │  │                                  │
│  "Water level rising        │  │  AI Reasoning:                  │
│  rapidly, approximately     │  │  • 800 people affected          │
│  200 families trapped on    │  │  • Vulnerable populations       │
│  rooftops. Electricity cut  │  │  • Rapidly rising water level   │
│  off. Children and elderly  │  │  • Infrastructure loss          │
│  need immediate help."      │  │                                  │
│                             │  │  Recommended Resources:         │
│  MEDIA                      │  │  • 5× Rescue Boats [IMMEDIATE] │
│  [IMG1] [IMG2] [VID1]       │  │  • 2× Medical Units [HIGH]     │
│                             │  │  • 1× Helicopter [MEDIUM]      │
│                             │  │                                  │
│                             │  │  [✅ Accept] [✏ Override]       │
└─────────────────────────────┘  └──────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│  RESOURCE ASSIGNMENT                                                  │
│  Available in District:                                              │
│  [☑] ODRAF Boat Unit 2  — 2.3 km  — Available                      │
│  [☑] ODRAF Boat Unit 3  — 4.1 km  — Available                      │
│  [☑] NDRF Medical A     — 5.0 km  — Available                      │
│  [☐] ODRAF Boat Unit 7  — 8.2 km  — Available                      │
│                                                                       │
│  [Assign Selected Resources & Dispatch ────────────────────────────]│
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│  COMMENTS & COORDINATION                                             │
│  [Add internal note...]                        [Post Internal Note]  │
│                                                                       │
│  10:45 AM  Dist. Collector: ODRAF units being contacted              │
│  10:48 AM  ODRAF Team Lead: Boat units 2 and 3 dispatched            │
│  11:02 AM  Dist. Collector: ETA 20 minutes confirmed                 │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 12.8 Map View (Operations)

```
┌──────────────────────────────────────────────────────────────────────┐
│  TOPBAR CONTROLS                                                     │
│  Layers: [☑ Incidents] [☑ Resources] [☑ Heatmap] [○ Shelters]      │
│          [○ Hospitals]  [○ Routes]                                   │
│  Filter: [All Types ▼] [All Status ▼] [District: All ▼]            │
└──────────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────┐ ┌────────────────┐
│                                                  │ │ LEGEND         │
│           [FULL SCREEN GOOGLE MAP]               │ │ 🔴 Critical    │
│                                                  │ │ 🟠 High        │
│   🔴  🔴         🟠                              │ │ 🟡 Medium      │
│         🔴  🟡          [heat zone]              │ │ 🟢 Low         │
│   🟢─────►🔴    🟢                               │ │ ──► Route      │
│  (resource en route to incident)                 │ │ 🟢 Available   │
│                                                  │ │ 🚁 Helicopter  │
│                           🟠                     │ │ 🚤 Boat        │
│                                                  │ └────────────────┘
└─────────────────────────────────────────────────┘
[Click incident marker → Side panel with incident summary + assign CTA]
```

---

## 12.9 Analytics Dashboard

```
┌──────────────────────────────────────────────────────────────────────┐
│  Analytics – Khurda District         Period: [Last 7 Days ▼]        │
│  [Export PDF] [Export CSV] [Schedule Report]                         │
└──────────────────────────────────────────────────────────────────────┘

KPI ROW:
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ 142      │ │ 38 min   │ │ 94%      │ │ 85%      │ │ 8        │
│ Total    │ │ Avg Resp │ │ AI Accy  │ │ Resolve  │ │ Escaltd  │
│ Incidents│ │ Time     │ │ Rate     │ │ Rate     │ │          │
└──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘

CHARTS ROW 1:
┌─────────────────────────┐  ┌──────────────────────┐
│ Incident Trend (7 days) │  │ Incident Type Mix     │
│ [Area/Line Chart]       │  │ [Pie Chart]           │
│ Total | Critical | Resolved│  │ Flood 45% | Fire 22% │
└─────────────────────────┘  └──────────────────────┘

CHARTS ROW 2:
┌─────────────────────────┐  ┌──────────────────────┐
│ Response Time by Type   │  │ Resource Utilization  │
│ [Horizontal Bar Chart]  │  │ [Stacked Bar Chart]   │
└─────────────────────────┘  └──────────────────────┘

INCIDENTS TABLE:
[Searchable, sortable, paginated table with export]
```

---

## 12.10 Resource Allocation Page

```
┌──────────────────────────────────────────────────────────────────────┐
│  Resource Management – Khurda District          [+ Add Resource]     │
│  Filter: [All Types ▼] [Status: Available ▼] [Search resource name]  │
└──────────────────────────────────────────────────────────────────────┘

SUMMARY CARDS:
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ 49 Total │ │ 34 Avail │ │ 15 Depld │ │ 3 Maint  │
└──────────┘ └──────────┘ └──────────┘ └──────────┘

RESOURCE TABLE:
┌────┬───────────────────┬────────────┬───────────┬──────────┬──────────────┐
│ #  │ Name              │ Type       │ Status    │ Location │ Actions      │
├────┼───────────────────┼────────────┼───────────┼──────────┼──────────────┤
│  1 │ ODRAF Boat Unit 2 │ Rescue Boat│ 🟢 Avail  │ 2.3 km   │ [View][Assign]│
│  2 │ NDRF Medical A    │ Medical    │ 🔵 Deployed│ INC-001  │ [Track][Recall]│
│  3 │ Fire Engine 5     │ Fire Truck │ 🟡 Maint  │ HQ       │ [View]       │
└────┴───────────────────┴────────────┴───────────┴──────────┴──────────────┘
```

---

## 12.11 Notifications Page

```
┌──────────────────────────────────────────────────────────────────────┐
│  Notifications                [Mark All Read] [Filter ▼]             │
└──────────────────────────────────────────────────────────────────────┘
│ 🔴 UNREAD │ 2 minutes ago                                            │
│  🆘 New CRITICAL Incident in Khurda                                 │
│  INC-2024-00000001 — Flood — 800 people affected                    │
│  [View Incident →]                                                   │
├──────────────────────────────────────────────────────────────────────┤
│  🔴 UNREAD │ 15 minutes ago                                          │
│  ⚠️ Cluster Alert: 5 FLOOD incidents detected in Khurda in 1 hour   │
│  [View Map →]                                                        │
├──────────────────────────────────────────────────────────────────────┤
│  ✅ READ │ 1 hour ago                                                │
│  INC-2024-00000003 resolved by NDRF Team Alpha                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 12.12 Settings Page

```
┌──────────────────────────────────────────────────────────────────────┐
│  Settings                                                            │
│  [Account] [Notifications] [Privacy] [Appearance] [Security]        │
└──────────────────────────────────────────────────────────────────────┘

NOTIFICATIONS TAB:
  Push Notifications          [Toggle ON]
  SMS Alerts                  [Toggle ON]
  Email Updates               [Toggle OFF]
  Emergency Broadcasts        [Toggle ON — cannot disable]
  Language Preference:        [English ▼]

SECURITY TAB:
  Two-Factor Authentication   [Toggle ON]
  Active Sessions: 2          [Manage Sessions]
  [Change Password]
  [Download My Data]
  [Delete Account]
```

---

## 12.13 Profile Page

```
┌──────────────────────────────────────────────────────────────────────┐
│                                                                       │
│  [  Avatar / Upload Photo  ]                                         │
│                                                                       │
│  Rajesh Kumar                                                        │
│  CITIZEN | Khurda, Odisha                                            │
│  Member since January 2024                                           │
│                                                                       │
│  📊 My Activity                                                      │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐                         │
│  │ 7         │ │ 5         │ │ 2         │                         │
│  │ Reports   │ │ Resolved  │ │ Active    │                         │
│  └───────────┘ └───────────┘ └───────────┘                         │
│                                                                       │
│  Personal Information          [Edit]                                │
│  Full Name:   Rajesh Kumar                                           │
│  Email:       rajesh@example.com                                     │
│  Phone:       +91-9876543210                                         │
│  District:    Khurda                                                 │
│  State:       Odisha                                                 │
│                                                                       │
│  Emergency Contacts           [+ Add Contact]                        │
│  1. Priya Kumar (Spouse) — +91-9876543211                           │
│  2. Dr. Ramesh (Doctor) — +91-9876543212                            │
│                                                                       │
│  Special Needs: None                                                 │
└──────────────────────────────────────────────────────────────────────┘
```

---

*Next: [Dashboard Design →](./13-dashboard-design.md)*
