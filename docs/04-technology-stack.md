# Section 04 – Complete Technology Stack

---

## 4.1 Frontend

| Category | Technology | Version | Justification |
|----------|-----------|---------|---------------|
| **Framework** | React | 18.3 | Component model, concurrent features, wide ecosystem |
| **Language** | TypeScript | 5.4 | Type safety, better IDE support, fewer runtime errors |
| **Build Tool** | Vite | 5.x | Fast HMR, optimized production builds |
| **Styling** | Tailwind CSS | 3.4 | Utility-first, rapid prototyping, consistent design system |
| **UI Components** | Shadcn/UI | Latest | Accessible, headless, Tailwind-compatible component library |
| **Icons** | Lucide React | Latest | Consistent icon set, tree-shakeable |
| **State Management** | Zustand | 4.x | Lightweight, minimal boilerplate, React hooks-based |
| **Server State** | TanStack Query | 5.x | Data fetching, caching, background sync, optimistic updates |
| **Forms** | React Hook Form | 7.x | Performant, uncontrolled components, minimal re-renders |
| **Validation** | Zod | 3.x | Schema-first validation, TypeScript inference |
| **Routing** | React Router | 6.x | SPA routing, nested routes, data loaders |
| **Maps** | @vis.gl/react-google-maps | Latest | Google Maps React wrapper, declarative API |
| **Charts** | Recharts | 2.x | React-native charts, customizable, responsive |
| **Date/Time** | date-fns | 3.x | Lightweight, tree-shakeable date utilities |
| **HTTP Client** | Axios | 1.x | Interceptors, request/response transformation |
| **Real-time** | Firebase SDK | 10.x | Firestore real-time listeners built-in |
| **Animations** | Framer Motion | 11.x | Smooth UI transitions, gesture support |
| **PDF Export** | jsPDF + html2canvas | Latest | Client-side report generation |
| **PWA** | Vite PWA Plugin | Latest | Service worker, offline caching, installable app |
| **Testing** | Vitest + Testing Library | Latest | Fast unit tests, React component testing |

---

## 4.2 Backend

| Category | Technology | Version | Justification |
|----------|-----------|---------|---------------|
| **Runtime** | Node.js | 20 LTS | Async I/O, large ecosystem, Google Cloud native support |
| **Framework** | Express.js | 4.x | Minimal, flexible, proven for REST APIs |
| **Language** | TypeScript | 5.4 | Type safety across full stack |
| **AI SDK** | @google/generative-ai | Latest | Official Gemini SDK |
| **Firebase Admin** | firebase-admin | 12.x | Server-side Firestore, Auth, FCM access |
| **Validation** | Zod | 3.x | Shared schemas between frontend and backend |
| **Authentication** | Firebase Admin Auth | — | JWT verification, custom claims |
| **Task Queue** | Google Cloud Tasks | — | Async AI processing, reliable job queuing |
| **File Upload** | Multer | 1.x | Multipart form data handling |
| **Cloud Storage** | @google-cloud/storage | Latest | File uploads to GCS |
| **Logging** | Winston | 3.x | Structured JSON logging, multiple transports |
| **HTTP Security** | Helmet.js | 7.x | Security headers middleware |
| **Rate Limiting** | express-rate-limit | 7.x | IP-based rate limiting |
| **CORS** | cors | 2.x | Cross-origin resource sharing |
| **Environment** | dotenv | 16.x | Environment variable management |
| **Process Manager** | — | — | Cloud Run manages process lifecycle |
| **Testing** | Jest + Supertest | Latest | API integration testing |
| **API Docs** | Swagger/OpenAPI 3.0 | — | Auto-generated API documentation |

---

## 4.3 Database

| Category | Technology | Justification |
|----------|-----------|---------------|
| **Primary Database** | Firebase Firestore | NoSQL, real-time, auto-scaling, offline support, no server management |
| **Caching** | Firestore client cache | Built-in offline persistence in Firebase SDK |
| **Search** | Firestore composite indexes | Sufficient for structured queries at MVP scale |
| **File Storage** | Google Cloud Storage | Scalable media storage, CDN-integrated, lifecycle policies |
| **Analytics Storage** | BigQuery | Long-term analytics data warehouse, SQL queries, AI/ML integrations |

### Firestore Mode
- **Native Mode** (not Datastore mode) — required for real-time listeners
- **Multi-region location**: `nam5` (US) or `asia-south1` (Mumbai) for India deployment
- **Backup**: Daily automated Firestore exports to Cloud Storage

---

## 4.4 Authentication

| Category | Technology | Purpose |
|----------|-----------|---------|
| **Primary Auth** | Firebase Authentication | User identity management |
| **OAuth Provider** | Google OAuth 2.0 | Social login |
| **Phone Auth** | Firebase Phone Auth | OTP verification |
| **Token Standard** | JWT (Firebase ID Tokens) | Stateless API authentication |
| **2FA** | Firebase MFA (TOTP) | Admin and authority accounts |
| **Custom Claims** | Firebase Custom Claims | Role-based access embedded in token |
| **Session** | Firebase Refresh Tokens | 7-day sliding sessions |

---

## 4.5 Hosting

| Service | Technology | Purpose |
|---------|-----------|---------|
| **Frontend** | Firebase Hosting | Static files, CDN, SSL, custom domain |
| **Backend API** | Google Cloud Run | Containerized Node.js, auto-scaling, pay-per-request |
| **API Gateway** | Google Cloud Endpoints / API Gateway | Rate limiting, authentication, routing |
| **Container Registry** | Google Artifact Registry | Docker image storage |
| **CI/CD** | GitHub Actions | Automated build, test, deploy pipeline |

---

## 4.6 Cloud (Google Cloud Platform)

| Service | Purpose |
|---------|---------|
| **Google Cloud Run** | Serverless containers for backend API |
| **Firebase Firestore** | Primary real-time database |
| **Firebase Authentication** | User identity management |
| **Firebase Hosting** | Frontend CDN hosting |
| **Firebase Cloud Messaging** | Push notifications |
| **Google Cloud Storage** | Media and document file storage |
| **Google Cloud Tasks** | Async AI processing job queue |
| **Google Cloud Pub/Sub** | Event streaming between services |
| **Google Cloud Logging** | Centralized log aggregation |
| **Google Cloud Monitoring** | Metrics, dashboards, alerting |
| **Google Cloud Armor** | DDoS protection, WAF |
| **Google Cloud Secret Manager** | API keys and credentials management |
| **BigQuery** | Analytics data warehouse |
| **Google Cloud Scheduler** | Cron jobs (daily reports, cleanup) |

---

## 4.7 AI

| Service | Purpose |
|---------|---------|
| **Google Gemini 1.5 Pro** | Primary AI model for incident analysis, classification, prioritization, summarization |
| **Gemini 1.5 Flash** | High-volume, faster classification tasks (cost optimization) |
| **Vertex AI** | Model hosting if custom fine-tuned models are added in future |
| **Natural Language API** | Fallback sentiment/entity extraction if Gemini is unavailable |

---

## 4.8 Maps

| Service | Purpose |
|---------|---------|
| **Google Maps JavaScript API** | Interactive map rendering in web app |
| **Google Maps Geocoding API** | Address to coordinates conversion |
| **Google Maps Directions API** | Route optimization for resource dispatch |
| **Google Maps Places API** | Location autocomplete in report form |
| **Google Maps Distance Matrix API** | Calculate distance/time from resources to incidents |
| **Maps Static API** | Static map thumbnails in notifications/PDFs |

---

## 4.9 Charts & Data Visualization

| Library | Purpose |
|---------|---------|
| **Recharts** | Line charts, bar charts, pie charts, area charts in dashboards |
| **Google Charts** | Optional: integration with BigQuery data |
| **Tailwind + custom SVG** | Severity gauges, progress bars, custom KPI cards |

---

## 4.10 Notifications

| Service | Purpose |
|---------|---------|
| **Firebase Cloud Messaging (FCM)** | Web push and mobile push notifications |
| **Twilio / MSG91** | SMS notifications (OTP + emergency alerts) |
| **SendGrid** | Transactional email (registration, status updates, reports) |
| **Firebase In-App Messaging** | In-app notification banners |

---

## 4.11 Storage

| Service | Purpose |
|---------|---------|
| **Google Cloud Storage** | Incident media uploads (images, videos, audio) |
| **Firebase Storage** | User profile photos |
| **Cloud Storage Buckets** | Separated by: `resqai-media`, `resqai-exports`, `resqai-backups` |
| **Storage Lifecycle Rules** | Auto-archive media >90 days to Coldline; delete >1 year |
| **CDN** | Cloud CDN fronts GCS for fast media delivery |

---

## 4.12 Monitoring & Observability

| Service | Purpose |
|---------|---------|
| **Google Cloud Monitoring** | Infrastructure metrics, dashboards, uptime checks |
| **Google Cloud Logging** | Centralized log aggregation from all services |
| **Firebase Crashlytics** | Frontend error tracking and crash reporting |
| **Firebase Performance Monitoring** | Frontend web performance metrics |
| **Google Cloud Trace** | Distributed tracing for API performance |
| **Uptime Checks** | Cloud Monitoring uptime checks on all endpoints |
| **Alerting Policies** | PagerDuty/email alerts for P0/P1 SLA breaches |
| **Error Reporting** | Automated error grouping and notification |

---

## 4.13 Development Tools

| Tool | Purpose |
|------|---------|
| **VS Code** | Primary IDE |
| **ESLint + Prettier** | Code quality and formatting |
| **Husky + lint-staged** | Pre-commit hooks |
| **Commitizen** | Conventional commits |
| **Docker** | Local development and Cloud Run builds |
| **Postman / Insomnia** | API testing |
| **Figma** | UI/UX design |
| **draw.io / Lucidchart** | Architecture diagrams |

---

*Next: [Project Folder Structure →](./05-folder-structure.md)*
