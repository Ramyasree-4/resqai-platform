# Section 06 – System Architecture

---

## 6.1 Architecture Overview

ResQAI follows a **layered, cloud-native, event-driven architecture** built entirely on Google Cloud Platform. The system is designed for high availability, real-time responsiveness, and AI-augmented decision-making.

**Architecture Style:** Microservices-inspired monolith (modular monolith backend on Cloud Run) with event-driven async AI processing

---

## 6.2 Architecture Diagram (Text Representation)

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                           CLIENT LAYER                                       ║
║                                                                              ║
║  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐  ║
║  │  Citizen PWA    │  │ Authority Web   │  │      Admin Portal           │  ║
║  │  (React + TS)   │  │ (React + TS)    │  │      (React + TS)           │  ║
║  │  Firebase CDN   │  │ Firebase CDN    │  │      Firebase CDN           │  ║
║  └────────┬────────┘  └───────┬─────────┘  └──────────────┬──────────────┘  ║
║           │                  │                            │                  ║
║           │    ┌─────────────▼────────────────────────────▼──────────┐       ║
║           │    │        Firebase Realtime Listeners (Firestore)       │       ║
║           │    └─────────────────────────────────────────────────────┘       ║
╚═══════════╪═════════════════════════════════════════════════════════════════╝
            │ HTTPS / REST
╔═══════════▼═════════════════════════════════════════════════════════════════╗
║                           API LAYER                                          ║
║                                                                              ║
║  ┌─────────────────────────────────────────────────────────────────────┐    ║
║  │              Google Cloud Armor (WAF + DDoS Protection)             │    ║
║  └─────────────────────────────┬───────────────────────────────────────┘    ║
║                                │                                             ║
║  ┌─────────────────────────────▼───────────────────────────────────────┐    ║
║  │              Google Cloud API Gateway                                │    ║
║  │        (Rate Limiting · Authentication · Routing · Logging)          │    ║
║  └──────────────────────────────┬──────────────────────────────────────┘    ║
║                                 │                                            ║
║  ┌──────────────────────────────▼──────────────────────────────────────┐    ║
║  │              Cloud Run – ResQAI API Server                           │    ║
║  │              (Node.js / Express / TypeScript)                        │    ║
║  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │    ║
║  │  │  /auth   │ │/incidents│ │   /ai    │ │/resources│ │ /admin   │  │    ║
║  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘  │    ║
║  └──────────────────────────────────────────────────────────────────────┘    ║
╚══════════════════════════════════════════════════════════════════════════════╝
            │                         │                          │
╔═══════════▼═════════════╗  ╔════════▼═════════╗  ╔════════════▼═══════════╗
║   BUSINESS LOGIC LAYER  ║  ║    AI LAYER      ║  ║   NOTIFICATION LAYER   ║
║                         ║  ║                  ║  ║                        ║
║ ┌─────────────────────┐ ║  ║ ┌──────────────┐ ║  ║ ┌────────────────────┐ ║
║ │  IncidentService    │ ║  ║ │ Cloud Tasks  │ ║  ║ │ FCM (Push)         │ ║
║ │  ResourceService    │ ║  ║ │   Queue      │ ║  ║ │ SMS (Twilio)       │ ║
║ │  AuthService        │ ║  ║ └──────┬───────┘ ║  ║ │ Email (SendGrid)   │ ║
║ │  AnalyticsService   │ ║  ║        │         ║  ║ └────────────────────┘ ║
║ │  AuditService       │ ║  ║ ┌──────▼───────┐ ║  ╚════════════════════════╝
║ └─────────────────────┘ ║  ║ │ Gemini 1.5  │ ║
╚══════════╪══════════════╝  ║ │    Pro      │ ║
           │                ║ │  Classify   │ ║
╔══════════▼══════════════╗  ║ │  Severity   │ ║
║    DATABASE LAYER       ║  ║ │  Summarize  │ ║
║                         ║  ║ │  Recommend  │ ║
║ ┌─────────────────────┐ ║  ║ └─────────────┘ ║
║ │  Firebase Firestore  │ ║  ╚══════════════════╝
║ │  (Real-time NoSQL)  │ ║
║ │  ┌───────────────┐  │ ║
║ │  │ Users         │  │ ║
║ │  │ Incidents     │  │ ║
║ │  │ Resources     │  │ ║
║ │  │ Notifications │  │ ║
║ │  │ Analytics     │  │ ║
║ │  │ AuditLogs     │  │ ║
║ │  └───────────────┘  │ ║
║ └─────────────────────┘ ║
║                         ║
║ ┌─────────────────────┐ ║
║ │  Cloud Storage      │ ║
║ │  (Media Files)      │ ║
║ └─────────────────────┘ ║
║                         ║
║ ┌─────────────────────┐ ║
║ │  BigQuery           │ ║
║ │  (Analytics DW)     │ ║
║ └─────────────────────┘ ║
╚═════════════════════════╝

╔═══════════════════════════════════════════════════════════╗
║                   EXTERNAL APIs                           ║
║  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    ║
║  │ Google Maps  │  │ MSG91 (SMS)  │  │ SendGrid     │    ║
║  │ Platform     │  │              │  │ (Email)      │    ║
║  └──────────────┘  └──────────────┘  └──────────────┘    ║
╚═══════════════════════════════════════════════════════════╝
```

---

## 6.3 Layer-by-Layer Explanation

### Layer 1: Client Layer

**Components:** Citizen PWA, Authority Web App, Admin Portal

All three frontend applications are single-page React applications served from **Firebase Hosting** via global CDN edge nodes. They share the same codebase with role-based rendering.

- **Citizen PWA**: Installable Progressive Web App optimized for mobile, low bandwidth, offline report drafting. Uses service workers to cache UI shell.
- **Authority Web App**: Full-featured dashboard with real-time Firestore listeners. Designed for desktop-first with responsive mobile support.
- **Admin Portal**: System management interface. Accessible only from whitelisted IPs in production.

**Real-time Communication:** All clients maintain persistent Firestore WebSocket connections for live data updates. No polling required.

---

### Layer 2: API Layer

**Components:** Cloud Armor → API Gateway → Cloud Run API Server

**Cloud Armor** (Web Application Firewall):
- DDoS protection at the network edge
- OWASP rule set enforcement
- Geographic IP filtering capability
- Rate limiting at infrastructure level

**API Gateway:**
- Single entry point for all API calls
- Handles authentication token validation (Firebase JWT verification)
- Routes requests to Cloud Run backend
- Enforces per-user and per-IP rate limits
- Centralized request logging

**Cloud Run API Server:**
- Containerized Node.js/Express application
- Stateless design — any instance handles any request
- Auto-scales from 0 to 1000 instances based on traffic
- Modular route structure (auth, incidents, ai, resources, admin)
- Minimum instances: 2 (warm instances for zero cold-start in production)

---

### Layer 3: Business Logic Layer

**Location:** Inside Cloud Run API Server (src/services/)

This layer contains all domain logic, separated from HTTP concerns:

| Service | Responsibility |
|---------|----------------|
| `IncidentService` | CRUD, state transitions, escalation logic, duplicate detection |
| `ResourceService` | Inventory management, assignment optimization, availability tracking |
| `AuthService` | Token management, permission checking, role resolution |
| `AnalyticsService` | Metric aggregation, BigQuery export, report generation |
| `AuditService` | Immutable action logging, audit trail queries |
| `NotificationService` | Orchestration of multi-channel notification delivery |

---

### Layer 4: AI Layer

**Components:** Cloud Tasks Queue → Gemini 1.5 Pro

**Asynchronous AI Processing Design:**

When a new incident is submitted:
1. API Server immediately acknowledges the submission (< 200ms)
2. API Server enqueues an AI processing job to **Cloud Tasks**
3. Cloud Tasks delivers the job to the AI processing endpoint
4. AI endpoint calls **Gemini 1.5 Pro** with a structured prompt
5. Gemini returns: classification, severity, priority, recommendations, summary, explanation
6. Results are written back to Firestore
7. Firestore listener pushes update to all connected authority clients in real-time

**Why Async?** Gemini API calls can take 2–5 seconds. Blocking the HTTP request would degrade user experience. The async queue also provides retry logic and backpressure management.

**Fallback:** If Gemini is unavailable (circuit breaker open), a rule-based classifier kicks in using keyword matching and pattern rules to provide basic triage.

---

### Layer 5: Database Layer

**Primary Store: Firebase Firestore**
- NoSQL document database with real-time capabilities
- All incident, user, resource, notification data stored here
- Firestore security rules enforce access control at the data layer
- Composite indexes maintained for all query patterns

**File Storage: Google Cloud Storage**
- Incident media uploads (photos, videos, documents)
- Exported PDF reports
- System backups and Firestore exports
- Buckets: `resqai-media`, `resqai-exports`, `resqai-backups`

**Analytics Warehouse: BigQuery**
- Daily Firestore export to BigQuery via scheduled Cloud Function
- Historical trend analysis, complex SQL analytics
- ML-ready dataset for future predictive analytics

---

### Layer 6: Cloud Layer

**Google Cloud Services:**
- **Cloud Run**: Backend hosting with auto-scaling
- **Cloud Tasks**: Async job processing for AI workloads
- **Cloud Pub/Sub**: Event streaming between services (cluster detection, mass casualty alerts)
- **Cloud Scheduler**: Cron jobs (daily analytics rollup, archive job, report delivery)
- **Cloud Logging**: Centralized log storage
- **Cloud Monitoring**: Metrics, dashboards, alerting
- **Secret Manager**: Secure storage of all API keys and credentials
- **Artifact Registry**: Docker image storage for Cloud Run deployments

---

### Layer 7: External APIs

| API | Integration Point |
|-----|-----------------|
| **Google Gemini** | Backend AI layer (never exposed to client) |
| **Google Maps Platform** | Frontend map rendering + backend geocoding |
| **MSG91/Twilio** | Backend notification service → SMS delivery |
| **SendGrid** | Backend notification service → email delivery |

---

## 6.4 Data Flow: Incident Submission to Authority Action

```
CITIZEN
  │ 1. Submit incident report (form + GPS + media)
  ▼
FIREBASE HOSTING (CDN)
  │ 2. POST /api/v1/incidents
  ▼
CLOUD ARMOR → API GATEWAY
  │ 3. Authenticate + rate check
  ▼
CLOUD RUN API
  │ 4. Validate input (Zod)
  │ 5. Save incident to Firestore (status: SUBMITTED)
  │ 6. Upload media to Cloud Storage
  │ 7. Enqueue AI job to Cloud Tasks
  │ 8. Return 201 + incident ID to citizen (< 500ms)
  ▼
CLOUD TASKS
  │ 9. Deliver AI job to processing endpoint
  ▼
CLOUD RUN (AI endpoint)
  │ 10. Build Gemini prompt with incident data
  │ 11. Call Gemini 1.5 Pro API
  │ 12. Parse AI response
  │ 13. Update Firestore: status TRIAGED + AI analysis attached
  ▼
FIRESTORE
  │ 14. Real-time listener fires on all authority clients
  ▼
AUTHORITY DASHBOARD
  │ 15. New incident appears in priority queue
  │ 16. Authority reviews AI recommendation
  │ 17. Authority assigns resources + accepts incident
  ▼
CLOUD RUN API
  │ 18. Update incident status: ASSIGNED
  │ 19. Trigger notification to citizen + assigned team
  ▼
CITIZEN (push notification)
  "Your report #INC-2024-001 has been assigned to NDRF Team Alpha"
```

---

## 6.5 Real-Time Architecture

ResQAI uses Firestore's real-time listener model for instant data synchronization:

```
Authority Client                 Firestore                    API Server
     │                              │                              │
     │── onSnapshot(incidents) ────►│                              │
     │    (persistent listener)      │                              │
     │                              │                              │
     │                              │◄── New incident write ───────│
     │                              │                              │
     │◄── Real-time push ──────────│                              │
     │  (incident list updated)      │                              │
     │                              │                              │
```

**No polling. No websocket management. Firebase handles all connection lifecycle.**

---

*Next: [Database Design →](./07-database-design.md)*
