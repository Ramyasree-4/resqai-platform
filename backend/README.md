# ResQAI Backend

> AI-Powered Disaster Response & Resource Allocation Platform — Python/FastAPI Backend

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Runtime | Python 3.12 |
| Framework | FastAPI 0.115 |
| Database | Firebase Firestore |
| Auth | Firebase Authentication + JWT |
| AI | Google Gemini 1.5 Pro/Flash |
| Deployment | Google Cloud Run |
| Logging | structlog (JSON in production) |

---

## Project Structure

```
backend/
├── main.py                     # FastAPI app + lifespan + health checks
├── requirements.txt
├── .env.example
│
└── app/
    ├── api/                    # Route handlers (thin controllers)
    │   ├── auth.py             # POST /auth/register, /login, /refresh ...
    │   ├── incidents.py        # POST/GET /incidents, /sos, /assign ...
    │   ├── resources.py        # CRUD /resources + /nearby
    │   ├── notifications.py    # GET/PUT /notifications, /broadcast
    │   ├── analytics.py        # /dashboard/stats, /analytics/summary ...
    │   ├── ai.py               # /ai/analyze, /ai/analysis, /ai/cluster ...
    │   └── admin.py            # /admin/users, /admin/audit-logs ...
    │
    ├── services/               # Business logic layer
    │   ├── auth_service.py
    │   ├── incident_service.py # AI trigger, lifecycle, duplicate detection
    │   ├── resource_service.py
    │   ├── notification_service.py
    │   └── analytics_service.py
    │
    ├── gemini/
    │   ├── service.py          # GeminiService, CircuitBreaker, fallback
    │   └── prompts.py          # All Gemini prompt templates
    │
    ├── firebase/
    │   └── client.py           # Firebase Admin SDK init + Collections
    │
    ├── middleware/
    │   ├── auth.py             # JWT verification, role dependencies
    │   ├── error_handler.py    # Global exception → standard error envelope
    │   └── request_logger.py   # Request ID + timing logs
    │
    ├── models/                 # Pydantic models (request/response/DB)
    │   ├── enums.py
    │   ├── user.py
    │   ├── incident.py
    │   ├── resource.py
    │   ├── notification.py
    │   └── analytics.py
    │
    ├── config/
    │   └── settings.py         # Pydantic Settings (env vars)
    │
    ├── core/
    │   ├── exceptions.py       # Custom exception hierarchy
    │   ├── responses.py        # Standard response envelopes
    │   ├── logging.py          # structlog setup
    │   └── context.py          # Request ID context var
    │
    └── utils/
        ├── geo.py              # Haversine, geohash, coordinate validation
        ├── ids.py              # Incident/resource ID generation
        └── priority.py         # Priority score algorithm
```

---

## Quick Start

### 1. Prerequisites

```bash
# Python 3.12
python --version

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Setup

```bash
cp .env.example .env
# Edit .env and fill in:
# - FIREBASE_PROJECT_ID
# - FIREBASE_WEB_API_KEY
# - FIREBASE_SERVICE_ACCOUNT_PATH (or FIREBASE_SERVICE_ACCOUNT_JSON)
# - FIREBASE_STORAGE_BUCKET
# - GEMINI_API_KEY
# - JWT_SECRET_KEY
```

### 3. Firebase Setup

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Create project `resqai-dev`
3. Enable Firestore (Native mode, region: `asia-south1`)
4. Enable Authentication (Email/Password + Google)
5. Download service account JSON → save as `firebase-service-account.json`
6. Copy Web API Key from Project Settings

### 4. Run Development Server

```bash
cd backend
python main.py
# OR
uvicorn main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

---

## API Reference

### Base URL
```
http://localhost:8000/v1        (development)
https://api.resqai.in/v1       (production)
```

### Authentication
All protected endpoints require:
```
Authorization: Bearer <Firebase_ID_Token>
```

### Key Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/register` | No | Register citizen/authority |
| POST | `/auth/login` | No | Login and get tokens |
| GET | `/auth/me` | Yes | Get current user profile |
| POST | `/incidents` | Yes | Submit emergency report |
| POST | `/incidents/sos` | Optional | SOS one-tap emergency |
| GET | `/incidents` | Authority+ | List incidents (role-scoped) |
| GET | `/incidents/priority` | Authority+ | Severity-sorted queue |
| GET | `/incidents/{id}` | Yes | Full incident details + AI analysis |
| PUT | `/incidents/{id}/status` | Authority+ | Update status |
| PUT | `/incidents/{id}/assign` | Authority+ | Assign resources |
| POST | `/incidents/{id}/escalate` | Authority+ | Escalate to higher authority |
| GET | `/resources` | Authority+ | List resources |
| POST | `/resources` | District+ | Create resource |
| GET | `/resources/nearby` | Yes | Find resources by distance |
| GET | `/notifications` | Yes | User notifications |
| PUT | `/notifications/read-all` | Yes | Mark all read |
| POST | `/notifications/broadcast` | State+ | Send district/state broadcast |
| GET | `/dashboard/stats` | Authority+ | KPI statistics |
| GET | `/dashboard/map-data` | Authority+ | Map markers + heatmap |
| GET | `/analytics/summary` | Authority+ | Analytics summary |
| POST | `/ai/analyze` | Admin | Trigger/re-run AI analysis |
| GET | `/ai/analysis/{id}` | Yes | Get AI results |
| POST | `/ai/cluster-analysis` | Authority+ | Detect incident clusters |
| GET | `/admin/users` | Admin | User management |
| GET | `/admin/audit-logs` | Admin | Platform audit trail |
| GET | `/admin/system-stats` | Admin | Platform health |

---

## AI Integration

### Gemini Analysis Flow
```
Incident submitted
  → Saved to Firestore (status: SUBMITTED)
  → AI job queued (background thread)
  → Gemini 1.5 Pro called with structured prompt
  → Response parsed + business rules applied
  → Firestore updated (status: TRIAGED + aiAnalysis)
  → Authority dashboard updates in real-time (Firestore listener)
```

### AI Fallback
If Gemini is unavailable (circuit breaker open after 5 failures):
- Rule-based keyword classifier activates
- Severity estimated from population count + keywords
- `aiAnalysis.fallbackUsed = true` flagged in response

### Circuit Breaker
- Opens after 5 consecutive Gemini failures
- Auto-resets after 60 seconds (half-open probe)
- Status visible at `/health/ready`

---

## Role-Based Access

| Role | Access Level |
|------|-------------|
| `CITIZEN` | Own incidents only |
| `AUTHORITY` | District incidents + resources |
| `NGO` | District read-only |
| `VOLUNTEER` | Nearby incidents |
| `DISTRICT_OFFICER` | Full district operations |
| `STATE_OFFICER` | Full state operations + broadcast |
| `ADMIN` | All data + user management |

---

## Running Tests

```bash
cd backend
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=app --cov-report=term-missing
```

---

## Deployment (Google Cloud Run)

```bash
# Build Docker image
docker build -t asia-south1-docker.pkg.dev/resqai-prod/resqai/api:latest .

# Push to Artifact Registry
docker push asia-south1-docker.pkg.dev/resqai-prod/resqai/api:latest

# Deploy to Cloud Run
gcloud run deploy resqai-api \
  --image asia-south1-docker.pkg.dev/resqai-prod/resqai/api:latest \
  --region asia-south1 \
  --platform managed \
  --min-instances 2 \
  --max-instances 1000 \
  --memory 1Gi \
  --cpu 2
```

---

## Health Checks

| Endpoint | Purpose |
|----------|---------|
| `GET /health` | Liveness probe — app running? |
| `GET /health/ready` | Readiness probe — Firebase + Gemini OK? |

---

## Environment Variables

See `.env.example` for the complete list with descriptions.

Required for production:
- `FIREBASE_PROJECT_ID`
- `FIREBASE_WEB_API_KEY`
- `FIREBASE_SERVICE_ACCOUNT_JSON` (Cloud Run uses this)
- `FIREBASE_STORAGE_BUCKET`
- `GEMINI_API_KEY`
- `JWT_SECRET_KEY`
- `ENVIRONMENT=production`

---

*ResQAI Backend v1.0.0 — Built for National-Level Hackathon*
