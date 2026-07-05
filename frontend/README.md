# ResQAI Frontend

> AI-Powered Disaster Response & Resource Allocation Platform — React Frontend

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | React 19 + TypeScript 5 |
| Build | Vite 6 |
| Styling | Tailwind CSS 3 + custom design tokens |
| UI Primitives | Radix UI (Dialog, Select, Tabs, Switch, Dropdown) |
| Icons | Lucide React |
| Routing | React Router v6 |
| Server State | TanStack Query v5 |
| Forms | React Hook Form + Zod |
| Charts | Recharts 2 |
| Maps | Google Maps JavaScript API |
| Auth | Firebase Authentication |
| HTTP | Axios with JWT interceptors |
| Toast | Sonner |
| Animations | Framer Motion |

---

## Project Structure

```
src/
├── App.tsx                    # Root with AuthProvider + ThemeProvider
├── main.tsx                   # ReactDOM entry, QueryClient, BrowserRouter
├── vite-env.d.ts              # Vite env type declarations
│
├── types/                     # TypeScript interfaces matching backend models
│   ├── auth.types.ts          # User, UserRole, LoginRequest, RegisterRequest
│   ├── incident.types.ts      # Incident, AIAnalysis, all incident enums
│   ├── resource.types.ts      # ResourceResponse, ResourceStatus
│   ├── analytics.types.ts     # DashboardStats, MapData, TrendData
│   ├── notification.types.ts  # Notification, NotificationType
│   └── index.ts               # Barrel export
│
├── utils/
│   ├── cn.ts                  # clsx + tailwind-merge helper
│   ├── constants.ts           # SEVERITY_COLORS, API_ENDPOINTS, labels
│   └── formatters.ts          # Date, distance, severity formatters
│
├── firebase/
│   ├── config.ts              # Firebase app init
│   └── auth.ts                # signInWithGoogle, onAuthStateChanged
│
├── services/                  # Axios API layer
│   ├── api.ts                 # Axios instance, JWT interceptors
│   ├── auth.service.ts        # login, register, getMe, updateProfile
│   ├── incident.service.ts    # CRUD + SOS + assign + AI feedback
│   ├── resource.service.ts    # CRUD + nearby search
│   ├── analytics.service.ts   # Dashboard stats, map data, trends
│   └── notification.service.ts # Get, mark read, broadcast
│
├── contexts/
│   ├── AuthContext.tsx        # user, login, register, logout, refreshUser
│   └── ThemeContext.tsx       # light/dark/system theme + localStorage
│
├── hooks/                     # TanStack Query hooks
│   ├── useAuth.ts             # Consumes AuthContext
│   ├── useIncidents.ts        # useIncidents, useIncident, useCreateIncident…
│   ├── useResources.ts        # useResources, useNearbyResources…
│   ├── useDashboard.ts        # useDashboardStats, useMapData, useIncidentTrend
│   ├── useNotifications.ts    # useNotifications (list + unread count + mark read)
│   └── useGeolocation.ts      # navigator.geolocation wrapper
│
├── router/
│   ├── index.tsx              # All routes with lazy loading
│   └── ProtectedRoute.tsx     # Auth + role guard
│
├── components/
│   ├── ui/                    # Atomic UI components
│   │   ├── Button, Card, Input, Select, Modal
│   │   ├── Badge, SeverityBadge, StatusBadge, Avatar
│   │   ├── LoadingSpinner (+ SkeletonCard), EmptyState, StatsCard
│   ├── layout/
│   │   ├── AppShell.tsx       # Sidebar + TopNavbar + Outlet
│   │   ├── Sidebar.tsx        # Role-based nav links, collapsible
│   │   ├── TopNavbar.tsx      # Search, notifications, theme, user menu
│   │   └── Footer.tsx
│   ├── common/
│   │   ├── NotificationBell.tsx  # Bell icon + dropdown panel
│   │   ├── PageHeader.tsx        # Title + breadcrumbs + action slot
│   │   └── ErrorBoundary.tsx
│   ├── charts/
│   │   ├── IncidentTrendChart.tsx   # Area chart (total/critical/resolved)
│   │   ├── SeverityDonutChart.tsx   # Donut chart
│   │   ├── IncidentTypeBarChart.tsx # Horizontal bar chart
│   │   └── ResponseTimeChart.tsx    # Line chart + SLA reference line
│   ├── map/
│   │   └── ResQAIMap.tsx      # Google Maps with incident/resource markers
│   └── incident/
│       ├── IncidentCard.tsx          # Summary card with severity bar
│       ├── AIAnalysisPanel.tsx       # Full AI analysis with reasoning
│       ├── IncidentTimeline.tsx      # Status history timeline
│       └── ResourceAssignmentPanel.tsx
│
├── pages/
│   ├── public/  LandingPage, LoginPage, RegisterPage, ForgotPasswordPage
│   ├── citizen/ CitizenDashboard, ReportIncidentPage (5-step), MyReportsPage,
│   │            IncidentTrackerPage
│   ├── authority/ AuthorityDashboard, IncidentQueuePage, IncidentDetailsPage,
│   │              ResourceManagementPage, AnalyticsPage, MapViewPage
│   ├── admin/   AdminDashboard
│   └── shared/  NotificationsPage, ProfilePage, SettingsPage, NotFoundPage
│
└── styles/
    └── globals.css            # Tailwind directives, CSS vars, animations
```

---

## Quick Start

### 1. Install dependencies
```bash
npm install
```

### 2. Configure environment
```bash
cp .env.example .env
# Fill in Firebase, Gemini, Maps API keys
```

### 3. Start backend (in separate terminal)
```bash
# Backend must be running at http://localhost:8000
cd ../backend
uvicorn main:app --reload --port 8000
```

### 4. Start frontend
```bash
npm run dev
# → http://localhost:3000
```

---

## Environment Variables

```env
VITE_API_BASE_URL=http://localhost:8000/v1
VITE_FIREBASE_API_KEY=...
VITE_FIREBASE_AUTH_DOMAIN=resqai-dev.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=resqai-dev
VITE_FIREBASE_STORAGE_BUCKET=resqai-dev.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=...
VITE_FIREBASE_APP_ID=...
VITE_MAPS_API_KEY=...       # Optional — map shows placeholder without it
VITE_ENVIRONMENT=development
```

---

## Role-Based Navigation

| Role | Landing Page | Access |
|------|-------------|--------|
| `CITIZEN` | `/dashboard` | Report, track, SOS |
| `AUTHORITY` / `DISTRICT_OFFICER` / `STATE_OFFICER` | `/authority` | Full ops dashboard |
| `NGO` / `VOLUNTEER` | `/authority` | Read-only incident view |
| `ADMIN` | `/admin` | User management, system stats |

---

## Build for Production

```bash
npm run build
# Output: dist/  (deploy to Firebase Hosting)
```

```bash
# Firebase Hosting deploy
firebase deploy --only hosting
```

---

## Key Design Decisions

- **TanStack Query** for all server state — auto-refetch, stale-while-revalidate, background sync
- **Firestore IDs as URL params** — backend returns `_firestoreId` on list results; pages use this for navigation
- **Async AI** — incident is created instantly, AI analysis arrives via 60s refetch or real-time
- **Role guards** at both route level (`ProtectedRoute`) and sidebar nav level
- **Circuit-breaker awareness** — AI panels show "Fallback Mode" badge when `fallbackUsed: true`
- **Zero polling for auth** — Firebase `onAuthStateChanged` keeps token fresh automatically

---

*ResQAI Frontend v1.0.0 — Built for National-Level Hackathon*
