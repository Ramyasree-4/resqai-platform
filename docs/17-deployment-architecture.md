# Section 17 – Deployment Architecture

---

## 17.1 Deployment Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                     GitHub Repository                                │
│                         resqai/resqai                               │
└────────────────────────────┬────────────────────────────────────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
    Push to main         Push to main   Pull Request
              │              │
              ▼              ▼
    ┌─────────────┐  ┌─────────────────────────┐
    │  Frontend   │  │       Backend            │
    │  CI/CD      │  │       CI/CD              │
    │  Workflow   │  │       Workflow            │
    └──────┬──────┘  └────────────┬────────────┘
           │                      │
           ▼                      ▼
  ┌────────────────┐    ┌──────────────────────┐
  │ npm run build  │    │ docker build         │
  │ (Vite)         │    │ docker push          │
  │                │    │ (Artifact Registry)  │
  └────────┬───────┘    └──────────┬───────────┘
           │                       │
           ▼                       ▼
  ┌────────────────┐    ┌──────────────────────┐
  │ Firebase       │    │ Cloud Run Deploy      │
  │ Hosting Deploy │    │ gcloud run deploy     │
  │                │    │ --image gcr://...     │
  └────────────────┘    └──────────────────────┘
```

---

## 17.2 Frontend Deployment (Firebase Hosting)

### Configuration

```json
// firebase.json
{
  "hosting": {
    "public": "frontend/dist",
    "ignore": ["firebase.json", "**/.*", "**/node_modules/**"],
    "rewrites": [
      { "source": "**", "destination": "/index.html" }
    ],
    "headers": [
      {
        "source": "**/*.@(js|css)",
        "headers": [
          { "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }
        ]
      },
      {
        "source": "/service-worker.js",
        "headers": [
          { "key": "Cache-Control", "value": "no-cache" }
        ]
      },
      {
        "source": "**",
        "headers": [
          { "key": "X-Frame-Options", "value": "DENY" },
          { "key": "X-Content-Type-Options", "value": "nosniff" },
          { "key": "Strict-Transport-Security", 
            "value": "max-age=31536000; includeSubDomains; preload" }
        ]
      }
    ]
  }
}
```

### CI/CD Workflow

```yaml
# .github/workflows/frontend-deploy.yml
name: Frontend Deploy
on:
  push:
    branches: [main]
    paths: ['frontend/**']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install dependencies
        run: npm ci
        working-directory: frontend
      
      - name: Run tests
        run: npm run test:run
        working-directory: frontend
      
      - name: Build
        run: npm run build
        working-directory: frontend
        env:
          VITE_FIREBASE_API_KEY: ${{ secrets.VITE_FIREBASE_API_KEY }}
          VITE_API_BASE_URL: ${{ secrets.VITE_API_BASE_URL }}
          VITE_MAPS_API_KEY: ${{ secrets.VITE_MAPS_API_KEY }}
      
      - name: Deploy to Firebase Hosting
        uses: FirebaseExtended/action-hosting-deploy@v0
        with:
          repoToken: ${{ secrets.GITHUB_TOKEN }}
          firebaseServiceAccount: ${{ secrets.FIREBASE_SERVICE_ACCOUNT }}
          projectId: resqai-prod
          channelId: live
```

### Environment Variables (Frontend)

```
VITE_FIREBASE_API_KEY=...
VITE_FIREBASE_AUTH_DOMAIN=resqai-prod.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=resqai-prod
VITE_FIREBASE_STORAGE_BUCKET=resqai-prod.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=...
VITE_FIREBASE_APP_ID=...
VITE_FIREBASE_VAPID_KEY=...  (FCM Web Push)
VITE_API_BASE_URL=https://api.resqai.in/v1
VITE_MAPS_API_KEY=...  (restricted to resqai domains)
VITE_ENVIRONMENT=production
```

---

## 17.3 Backend Deployment (Google Cloud Run)

### Dockerfile

```dockerfile
# backend/Dockerfile
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

# Production stage
FROM node:20-alpine AS runner

WORKDIR /app

# Security: run as non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S resqai -u 1001

COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./

USER resqai

EXPOSE 8080
ENV PORT=8080
ENV NODE_ENV=production

CMD ["node", "dist/server.js"]
```

### Cloud Run Service Configuration

```yaml
# cloud-run-service.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: resqai-api
  annotations:
    run.googleapis.com/ingress: all
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "2"
        autoscaling.knative.dev/maxScale: "1000"
        run.googleapis.com/cpu-throttling: "false"
    spec:
      containerConcurrency: 100
      timeoutSeconds: 60
      serviceAccountName: resqai-api-sa@resqai-prod.iam.gserviceaccount.com
      containers:
        - image: asia-south1-docker.pkg.dev/resqai-prod/resqai/api:latest
          ports:
            - containerPort: 8080
          resources:
            limits:
              cpu: "2"
              memory: "1Gi"
          env:
            - name: NODE_ENV
              value: production
            - name: FIREBASE_PROJECT_ID
              value: resqai-prod
            - name: GEMINI_API_KEY
              valueFrom:
                secretKeyRef:
                  name: resqai-gemini-api-key
                  key: latest
            - name: SENDGRID_API_KEY
              valueFrom:
                secretKeyRef:
                  name: resqai-sendgrid-key
                  key: latest
```

### Backend CI/CD Workflow

```yaml
# .github/workflows/backend-deploy.yml
name: Backend Deploy
on:
  push:
    branches: [main]
    paths: ['backend/**']

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: npm ci && npm test
        working-directory: backend

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Authenticate to GCP
        uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}
      
      - name: Configure Docker
        run: gcloud auth configure-docker asia-south1-docker.pkg.dev
      
      - name: Build and push image
        run: |
          docker build -t asia-south1-docker.pkg.dev/resqai-prod/resqai/api:${{ github.sha }} backend/
          docker push asia-south1-docker.pkg.dev/resqai-prod/resqai/api:${{ github.sha }}
          docker tag asia-south1-docker.pkg.dev/resqai-prod/resqai/api:${{ github.sha }} \
                     asia-south1-docker.pkg.dev/resqai-prod/resqai/api:latest
          docker push asia-south1-docker.pkg.dev/resqai-prod/resqai/api:latest
      
      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy resqai-api \
            --image asia-south1-docker.pkg.dev/resqai-prod/resqai/api:${{ github.sha }} \
            --region asia-south1 \
            --platform managed \
            --no-traffic  # Deploy to 10% traffic first (canary)
      
      - name: Canary health check
        run: ./scripts/deploy/health-check.sh
      
      - name: Promote to 100% traffic
        run: |
          gcloud run services update-traffic resqai-api \
            --to-latest \
            --region asia-south1
```

---

## 17.4 Database (Firebase Firestore)

### Configuration

```
Project: resqai-prod
Firestore Mode: Native
Location: asia-south1 (Mumbai)
Backup: Daily exports to gs://resqai-backups/firestore/
Multi-region: Enabled (data replicated across Asia South zones)
```

### Firestore Indexes

```json
// firestore.indexes.json
{
  "indexes": [
    {
      "collectionGroup": "incidents",
      "queryScope": "COLLECTION",
      "fields": [
        { "fieldPath": "location.district", "order": "ASCENDING" },
        { "fieldPath": "status", "order": "ASCENDING" },
        { "fieldPath": "aiAnalysis.severityScore", "order": "DESCENDING" }
      ]
    },
    {
      "collectionGroup": "incidents",
      "queryScope": "COLLECTION",
      "fields": [
        { "fieldPath": "reportedBy", "order": "ASCENDING" },
        { "fieldPath": "createdAt", "order": "DESCENDING" }
      ]
    },
    {
      "collectionGroup": "resources",
      "queryScope": "COLLECTION",
      "fields": [
        { "fieldPath": "district", "order": "ASCENDING" },
        { "fieldPath": "type", "order": "ASCENDING" },
        { "fieldPath": "status", "order": "ASCENDING" }
      ]
    },
    {
      "collectionGroup": "notifications",
      "queryScope": "COLLECTION",
      "fields": [
        { "fieldPath": "recipientId", "order": "ASCENDING" },
        { "fieldPath": "isRead", "order": "ASCENDING" },
        { "fieldPath": "createdAt", "order": "DESCENDING" }
      ]
    }
  ]
}
```

---

## 17.5 GCP Project Structure

```
GCP Project: resqai-prod
Region: asia-south1 (Mumbai)

Services:
├── Cloud Run:           resqai-api (backend)
├── Firebase Hosting:    resqai-prod.web.app / resqai.in
├── Firestore:           resqai-prod (native, asia-south1)
├── Firebase Auth:       resqai-prod
├── Cloud Storage:       resqai-media, resqai-exports, resqai-backups
├── Cloud Tasks:         resqai-ai-queue
├── Cloud Scheduler:     resqai-daily-rollup, resqai-archive-job
├── Cloud Pub/Sub:       resqai-incident-events, resqai-alerts
├── Artifact Registry:   asia-south1-docker.pkg.dev/resqai-prod/resqai
├── Secret Manager:      6 secrets (API keys)
├── Cloud Armor:         resqai-security-policy
├── Cloud Monitoring:    resqai-monitoring-workspace
└── BigQuery:            resqai-analytics dataset
```

---

## 17.6 IAM & Service Accounts

| Service Account | Roles | Purpose |
|----------------|-------|---------|
| `resqai-api-sa` | Firestore User, Storage Object Admin, Cloud Tasks Enqueuer, Secret Accessor | Cloud Run backend |
| `resqai-scheduler-sa` | Cloud Tasks Enqueuer, Firestore User | Cloud Scheduler jobs |
| `resqai-deploy-sa` | Cloud Run Admin, Artifact Registry Writer | GitHub Actions deployment |
| `resqai-backup-sa` | Firestore Import/Export Admin, Storage Object Creator | Automated backups |

---

## 17.7 Monitoring & Alerting

### Uptime Checks

```
Check: resqai-api-health
URL: https://api.resqai.in/v1/health
Interval: 1 minute
Regions: asia-southeast1, us-central1 (multi-region check)
Alert: If 2 consecutive failures → PagerDuty + email
```

### Alert Policies

| Alert | Condition | Notification |
|-------|-----------|-------------|
| API Error Rate High | Error rate > 5% for 5 min | Email + Slack |
| API P95 Latency High | P95 > 2s for 10 min | Email |
| Cloud Run Instance Limit | Instances > 800 | Email + Slack |
| Firestore Read Quota | > 80% of daily quota | Email |
| Gemini API Errors | Error rate > 10% | Email + Slack |
| AI Queue Depth | > 100 pending jobs | Email |
| Frontend Error Rate | Crashlytics > 1% | Email |

---

## 17.8 Environments

| Environment | Frontend URL | Backend URL | Firebase Project |
|------------|-------------|-------------|----------------|
| Development | localhost:5173 | localhost:8080 | resqai-dev |
| Staging | staging.resqai.in | api-staging.resqai.in | resqai-staging |
| Production | resqai.in | api.resqai.in | resqai-prod |

### Environment Promotion
```
Feature Branch → PR Review → Merge to main → Auto-deploy to Staging
Staging QA → Manual approval → Promote to Production
```

---

*Next: [Project Timeline →](./18-project-timeline.md)*
