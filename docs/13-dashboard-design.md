# Section 13 – Dashboard Design

---

## 13.1 Authority Operations Dashboard

### KPI Cards (Top Row)

| Card | Metric | Description | Color Logic |
|------|--------|-------------|-------------|
| Active Incidents | Count | All non-closed incidents in jurisdiction | Red if >50 |
| Critical Incidents | Count | Severity ≥ 7 (CRITICAL band) | Always red |
| Resources Deployed | Count / Total | e.g., 15/49 | Orange if >80% |
| Avg Response Time | Minutes | Rolling 24-hour average | Red if >SLA threshold |
| Resolved Today | Count | Incidents closed today | Green |
| Pending Assignment | Count | TRIAGED but not yet assigned | Red if >0 |
| AI Processing Queue | Count | Jobs pending AI analysis | Yellow if >10 |
| SOS Today | Count | SOS button activations today | Red |

### Charts

**1. Incident Trend Chart (Area Chart)**
- X-axis: Last 7 days (daily labels)
- Y-axis: Incident count
- Series: Total, Critical, Resolved
- Color: Blue (total), Red (critical), Green (resolved)
- Library: Recharts AreaChart

**2. Severity Distribution (Donut Chart)**
- Segments: CRITICAL (red), HIGH (orange), MEDIUM (yellow), LOW (green)
- Center label: Total active incidents
- Library: Recharts PieChart

**3. Incident Type Breakdown (Horizontal Bar)**
- Types: Flood, Fire, Cyclone, Medical, Earthquake, Other
- Bars colored by type
- Library: Recharts BarChart (horizontal)

**4. Response Time Trend (Line Chart)**
- X-axis: Last 30 days
- Y-axis: Average response time (minutes)
- Target line: SLA threshold
- Library: Recharts LineChart

**5. District Comparison (Grouped Bar)**
- X-axis: Districts in state
- Y-axis: Incident count
- Groups: Critical, High, Medium
- Available to STATE_OFFICER and ADMIN only

**6. Resource Utilization (Stacked Bar)**
- X-axis: Resource types
- Y-axis: Count
- Segments: Available, Deployed, Maintenance

### Filters

| Filter | Options | Persistence |
|--------|---------|-------------|
| District | All + district list | User preference |
| Time Period | Today, 7 days, 30 days, Custom | Session |
| Incident Type | All types | Session |
| Severity | All, Critical, High, Medium, Low | Session |
| Status | All, Active, Assigned, Resolved | Session |

### Map Section (Operations Map)

- Full-width interactive Google Map (below KPI cards)
- Incident markers: color = severity band
- Resource markers: type-specific icons
- Heatmap toggle overlay
- Click marker → slide-out panel with summary + quick actions
- Auto-centers on jurisdiction bounds

### Tables

**Incident Queue Table**

Columns: Rank | Incident ID | Type | Severity | District | Affected | Status | Time Since | Actions

- Default sort: AI severity score descending
- Row click: opens incident details page
- Inline actions: Quick Assign, Escalate
- Pagination: 20 per page
- Search/filter bar above table

**Resource Status Table**

Columns: Name | Type | Status | Location | Current Assignment | Last Updated | Actions

---

## 13.2 Citizen Dashboard

### KPI Cards

| Card | Metric |
|------|--------|
| My Active Reports | Count of open incidents |
| Last Submitted | Time ago of most recent report |
| Nearest Help | Distance to nearest available resource |
| District Alert Level | Current district emergency level |

### Widgets

**My Reports Summary**
- List of recent 5 reports with status pills
- Status color: SUBMITTED (gray), PROCESSING (blue), TRIAGED (yellow), ASSIGNED (orange), RESOLVED (green)
- Quick link to full tracking page

**Nearby Resources Map**
- Small map centered on user location
- Shows: hospitals (H), shelters (S), police (P), fire stations (F)
- Tap to see details and directions

**Emergency Alert Banner**
- Conditional: shows when district has active broadcast
- Red background, bold text
- Dismissible

---

## 13.3 Admin Dashboard

### Platform KPI Cards

| Card | Metric |
|------|--------|
| Total Users | Registered users across platform |
| Active Today | DAU (Daily Active Users) |
| Total Incidents (All Time) | Platform lifetime count |
| AI Processing (24h) | Gemini API calls today |
| System Health | ALL GREEN / WARNING / CRITICAL |
| Pending Approvals | Users awaiting role verification |
| Error Rate (1h) | API error rate percentage |
| Gemini Cost Today | USD cost of AI API calls |

### Admin Charts

**User Growth Chart** — Line chart of new registrations by week

**Incident Volume by State** — Choropleth-style bar chart

**AI Accuracy Over Time** — Line chart tracking recommendation acceptance rate

**System Performance** — Response time P50/P95/P99 over 24 hours

---

## 13.4 Design System

### Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `--critical` | `#DC2626` | Critical severity, SOS, urgent alerts |
| `--high` | `#EA580C` | High severity incidents |
| `--medium` | `#D97706` | Medium severity |
| `--low` | `--22C55E` | Low severity, resolved, available |
| `--info` | `#3B82F6` | AI analysis, informational |
| `--neutral` | `#6B7280` | Secondary text, borders |
| `--bg-primary` | `#0F172A` | Dark dashboard background |
| `--bg-card` | `#1E293B` | Card backgrounds |
| `--text-primary` | `#F8FAFC` | Primary text on dark |

### Typography

| Element | Font | Size | Weight |
|---------|------|------|--------|
| Page Title | Inter | 24px | 700 |
| Section Heading | Inter | 18px | 600 |
| Card Value (KPI) | Inter | 32px | 700 |
| Card Label | Inter | 12px | 400 |
| Table Data | Inter | 14px | 400 |
| Badge/Pill | Inter | 11px | 600 |

### Component States

All interactive components support: default, hover, focus, active, disabled, loading

---

*Next: [Gemini AI Integration →](./14-gemini-integration.md)*
