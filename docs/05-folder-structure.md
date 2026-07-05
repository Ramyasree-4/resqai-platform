# Section 05 – Complete Project Folder Structure

---

## 5.1 Root Workspace

```
resqai/
├── frontend/                    # React + TypeScript web application
├── backend/                     # Node.js + Express API server
├── shared/                      # Shared types, schemas, constants
├── docs/                        # Architecture and design documentation
├── scripts/                     # Deployment, seeding, utility scripts
├── assets/                      # Brand assets, logos, design files
├── .github/                     # GitHub Actions CI/CD workflows
│   └── workflows/
│       ├── frontend-deploy.yml
│       ├── backend-deploy.yml
│       └── tests.yml
├── .gitignore
├── README.md
└── docker-compose.yml           # Local development environment
```

---

## 5.2 Frontend Structure

```
frontend/
├── public/
│   ├── favicon.ico
│   ├── manifest.json            # PWA manifest
│   ├── robots.txt
│   └── icons/                   # PWA icons (192x192, 512x512)
│
├── src/
│   ├── main.tsx                 # App entry point
│   ├── App.tsx                  # Root component, router setup
│   ├── vite-env.d.ts
│   │
│   ├── assets/                  # Static assets used in components
│   │   ├── images/
│   │   ├── icons/
│   │   └── illustrations/
│   │
│   ├── components/              # Reusable UI components
│   │   ├── ui/                  # Shadcn/UI base components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── input.tsx
│   │   │   ├── select.tsx
│   │   │   ├── badge.tsx
│   │   │   ├── table.tsx
│   │   │   ├── tabs.tsx
│   │   │   └── ...
│   │   │
│   │   ├── layout/              # Layout components
│   │   │   ├── AppShell.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── TopNavbar.tsx
│   │   │   ├── Footer.tsx
│   │   │   ├── PageHeader.tsx
│   │   │   └── BreadcrumbNav.tsx
│   │   │
│   │   ├── common/              # Shared functional components
│   │   │   ├── LoadingSpinner.tsx
│   │   │   ├── ErrorBoundary.tsx
│   │   │   ├── EmptyState.tsx
│   │   │   ├── ConfirmDialog.tsx
│   │   │   ├── StatusBadge.tsx
│   │   │   ├── SeverityIndicator.tsx
│   │   │   ├── NotificationBell.tsx
│   │   │   ├── Avatar.tsx
│   │   │   ├── FileUpload.tsx
│   │   │   └── DataTable.tsx
│   │   │
│   │   ├── map/                 # Map components
│   │   │   ├── ResQAIMap.tsx
│   │   │   ├── IncidentMarker.tsx
│   │   │   ├── ResourceMarker.tsx
│   │   │   ├── HeatmapLayer.tsx
│   │   │   ├── MapControls.tsx
│   │   │   ├── MapLegend.tsx
│   │   │   ├── RouteOverlay.tsx
│   │   │   └── InfrastructureLayer.tsx
│   │   │
│   │   ├── charts/              # Chart components
│   │   │   ├── IncidentTrendChart.tsx
│   │   │   ├── SeverityDistributionChart.tsx
│   │   │   ├── IncidentTypePieChart.tsx
│   │   │   ├── ResponseTimeChart.tsx
│   │   │   ├── ResourceUtilizationChart.tsx
│   │   │   └── DistrictComparisonChart.tsx
│   │   │
│   │   ├── incident/            # Incident-specific components
│   │   │   ├── IncidentCard.tsx
│   │   │   ├── IncidentList.tsx
│   │   │   ├── IncidentForm.tsx
│   │   │   ├── IncidentDetails.tsx
│   │   │   ├── IncidentTimeline.tsx
│   │   │   ├── AIAnalysisPanel.tsx
│   │   │   ├── ResourceAssignment.tsx
│   │   │   └── EscalationPanel.tsx
│   │   │
│   │   ├── resource/            # Resource components
│   │   │   ├── ResourceCard.tsx
│   │   │   ├── ResourceList.tsx
│   │   │   ├── ResourceForm.tsx
│   │   │   └── ResourceStatusToggle.tsx
│   │   │
│   │   └── notification/        # Notification components
│   │       ├── NotificationPanel.tsx
│   │       ├── NotificationItem.tsx
│   │       └── BroadcastForm.tsx
│   │
│   ├── pages/                   # Route-level page components
│   │   ├── public/              # Unauthenticated pages
│   │   │   ├── LandingPage.tsx
│   │   │   ├── LoginPage.tsx
│   │   │   ├── RegisterPage.tsx
│   │   │   └── ForgotPasswordPage.tsx
│   │   │
│   │   ├── citizen/             # Citizen portal pages
│   │   │   ├── CitizenDashboard.tsx
│   │   │   ├── ReportIncident.tsx
│   │   │   ├── MyReports.tsx
│   │   │   ├── IncidentTracker.tsx
│   │   │   ├── NearbyResources.tsx
│   │   │   └── SOSPage.tsx
│   │   │
│   │   ├── authority/           # Authority portal pages
│   │   │   ├── AuthorityDashboard.tsx
│   │   │   ├── IncidentQueue.tsx
│   │   │   ├── IncidentDetailsPage.tsx
│   │   │   ├── AIAnalysisPage.tsx
│   │   │   ├── ResourceAllocation.tsx
│   │   │   ├── MapOperationsView.tsx
│   │   │   ├── AnalyticsDashboard.tsx
│   │   │   ├── SituationReports.tsx
│   │   │   └── NotificationsPage.tsx
│   │   │
│   │   ├── admin/               # Admin portal pages
│   │   │   ├── AdminDashboard.tsx
│   │   │   ├── UserManagement.tsx
│   │   │   ├── ResourceRegistry.tsx
│   │   │   ├── SystemSettings.tsx
│   │   │   ├── AuditLogs.tsx
│   │   │   └── PlatformAnalytics.tsx
│   │   │
│   │   └── shared/              # Shared authenticated pages
│   │       ├── ProfilePage.tsx
│   │       ├── SettingsPage.tsx
│   │       └── NotFoundPage.tsx
│   │
│   ├── hooks/                   # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── useIncidents.ts
│   │   ├── useResources.ts
│   │   ├── useNotifications.ts
│   │   ├── useRealtime.ts
│   │   ├── useGeolocation.ts
│   │   ├── useMap.ts
│   │   ├── useAIAnalysis.ts
│   │   └── usePermissions.ts
│   │
│   ├── stores/                  # Zustand state stores
│   │   ├── authStore.ts
│   │   ├── incidentStore.ts
│   │   ├── resourceStore.ts
│   │   ├── notificationStore.ts
│   │   ├── mapStore.ts
│   │   └── uiStore.ts
│   │
│   ├── services/                # API service layer
│   │   ├── api.ts               # Axios instance, interceptors
│   │   ├── authService.ts
│   │   ├── incidentService.ts
│   │   ├── resourceService.ts
│   │   ├── aiService.ts
│   │   ├── notificationService.ts
│   │   ├── analyticsService.ts
│   │   ├── storageService.ts
│   │   └── mapsService.ts
│   │
│   ├── firebase/                # Firebase configuration
│   │   ├── config.ts
│   │   ├── auth.ts
│   │   ├── firestore.ts
│   │   ├── storage.ts
│   │   ├── messaging.ts
│   │   └── remoteConfig.ts
│   │
│   ├── lib/                     # Utility functions
│   │   ├── utils.ts
│   │   ├── formatters.ts
│   │   ├── validators.ts
│   │   ├── constants.ts
│   │   ├── severityColors.ts
│   │   └── exportHelpers.ts
│   │
│   ├── types/                   # TypeScript type definitions
│   │   ├── index.ts
│   │   ├── incident.types.ts
│   │   ├── resource.types.ts
│   │   ├── user.types.ts
│   │   ├── ai.types.ts
│   │   └── api.types.ts
│   │
│   ├── routes/                  # Route definitions
│   │   ├── index.tsx
│   │   ├── ProtectedRoute.tsx
│   │   ├── RoleRoute.tsx
│   │   └── routeConfig.ts
│   │
│   └── styles/                  # Global styles
│       ├── globals.css
│       ├── tailwind.css
│       └── animations.css
│
├── .env.example
├── .eslintrc.json
├── .prettierrc
├── index.html
├── package.json
├── tailwind.config.ts
├── tsconfig.json
├── tsconfig.app.json
├── vite.config.ts
└── vitest.config.ts
```

---

## 5.3 Backend Structure

```
backend/
├── src/
│   ├── server.ts                # HTTP server entry point
│   ├── app.ts                   # Express app configuration
│   │
│   ├── config/                  # Configuration modules
│   │   ├── firebase.ts          # Firebase Admin SDK init
│   │   ├── gemini.ts            # Gemini AI client init
│   │   ├── storage.ts           # Google Cloud Storage init
│   │   ├── cloudTasks.ts        # Cloud Tasks client init
│   │   └── environment.ts       # Environment variable validation
│   │
│   ├── routes/                  # Express route definitions
│   │   ├── index.ts             # Route aggregator
│   │   ├── auth.routes.ts
│   │   ├── incident.routes.ts
│   │   ├── ai.routes.ts
│   │   ├── resource.routes.ts
│   │   ├── dashboard.routes.ts
│   │   ├── analytics.routes.ts
│   │   ├── notification.routes.ts
│   │   └── admin.routes.ts
│   │
│   ├── controllers/             # Request handlers
│   │   ├── auth.controller.ts
│   │   ├── incident.controller.ts
│   │   ├── ai.controller.ts
│   │   ├── resource.controller.ts
│   │   ├── dashboard.controller.ts
│   │   ├── analytics.controller.ts
│   │   ├── notification.controller.ts
│   │   └── admin.controller.ts
│   │
│   ├── services/                # Business logic layer
│   │   ├── auth.service.ts
│   │   ├── incident.service.ts
│   │   ├── ai/
│   │   │   ├── gemini.service.ts          # Gemini API integration
│   │   │   ├── classification.service.ts  # Incident type classification
│   │   │   ├── severity.service.ts        # Severity scoring
│   │   │   ├── prioritization.service.ts  # Priority queue management
│   │   │   ├── recommendation.service.ts  # Resource recommendation
│   │   │   ├── summary.service.ts         # Situation summary generation
│   │   │   ├── duplicate.service.ts       # Duplicate detection
│   │   │   └── fallback.service.ts        # Rule-based AI fallback
│   │   ├── resource.service.ts
│   │   ├── notification.service.ts
│   │   ├── analytics.service.ts
│   │   ├── storage.service.ts
│   │   ├── maps.service.ts
│   │   └── audit.service.ts
│   │
│   ├── middleware/              # Express middleware
│   │   ├── authenticate.ts      # JWT verification
│   │   ├── authorize.ts         # Role-based authorization
│   │   ├── rateLimiter.ts       # Rate limiting
│   │   ├── validate.ts          # Request body validation (Zod)
│   │   ├── errorHandler.ts      # Global error handler
│   │   ├── requestLogger.ts     # Request/response logging
│   │   └── uploadHandler.ts     # Multer file upload
│   │
│   ├── repositories/            # Firestore data access layer
│   │   ├── base.repository.ts   # Generic CRUD base class
│   │   ├── user.repository.ts
│   │   ├── incident.repository.ts
│   │   ├── resource.repository.ts
│   │   ├── notification.repository.ts
│   │   ├── analytics.repository.ts
│   │   ├── audit.repository.ts
│   │   └── feedback.repository.ts
│   │
│   ├── models/                  # Data models and Zod schemas
│   │   ├── user.model.ts
│   │   ├── incident.model.ts
│   │   ├── resource.model.ts
│   │   ├── notification.model.ts
│   │   ├── aiAnalysis.model.ts
│   │   └── audit.model.ts
│   │
│   ├── tasks/                   # Cloud Tasks handlers
│   │   ├── processIncident.task.ts
│   │   ├── sendNotification.task.ts
│   │   ├── generateReport.task.ts
│   │   └── archiveIncidents.task.ts
│   │
│   ├── utils/                   # Utility functions
│   │   ├── logger.ts
│   │   ├── errorTypes.ts
│   │   ├── httpResponse.ts
│   │   ├── pagination.ts
│   │   ├── geospatial.ts
│   │   └── prompts.ts           # Gemini prompt templates
│   │
│   └── types/                   # Backend TypeScript types
│       ├── express.d.ts         # Express request extensions
│       ├── index.ts
│       └── shared.ts
│
├── tests/
│   ├── unit/
│   │   ├── services/
│   │   └── utils/
│   └── integration/
│       ├── auth.test.ts
│       ├── incident.test.ts
│       └── ai.test.ts
│
├── Dockerfile
├── .dockerignore
├── .env.example
├── .eslintrc.json
├── jest.config.ts
├── package.json
└── tsconfig.json
```

---

## 5.4 Shared Structure

```
shared/
├── types/
│   ├── incident.ts          # Shared incident types (frontend + backend)
│   ├── resource.ts          # Shared resource types
│   ├── user.ts              # Shared user types
│   ├── ai.ts                # Shared AI response types
│   ├── api.ts               # API request/response contracts
│   └── enums.ts             # Shared enumerations
│
├── schemas/
│   ├── incidentSchema.ts    # Zod schemas shared between FE and BE
│   ├── resourceSchema.ts
│   ├── userSchema.ts
│   └── aiSchema.ts
│
└── constants/
    ├── roles.ts             # User role constants
    ├── incidentTypes.ts     # Disaster type enum
    ├── severityLevels.ts    # Severity band definitions
    ├── resourceTypes.ts     # Resource type enum
    └── statusCodes.ts       # HTTP and business status codes
```

---

## 5.5 Docs Structure

```
docs/
├── README.md                     # Document index (this file)
├── 01-project-vision.md
├── 02-functional-requirements.md
├── 03-non-functional-requirements.md
├── 04-technology-stack.md
├── 05-folder-structure.md
├── 06-system-architecture.md
├── 07-database-design.md
├── 08-er-diagram.md
├── 09-api-design.md
├── 10-user-roles.md
├── 11-application-flow.md
├── 12-ui-wireframes.md
├── 13-dashboard-design.md
├── 14-gemini-integration.md
├── 15-maps-integration.md
├── 16-security-architecture.md
├── 17-deployment-architecture.md
├── 18-project-timeline.md
├── 19-presentation-flow.md
├── 20-future-enhancements.md
└── diagrams/
    ├── system-architecture.png
    ├── er-diagram.png
    ├── deployment-diagram.png
    └── user-flow.png
```

---

## 5.6 Scripts Structure

```
scripts/
├── deploy/
│   ├── deploy-frontend.sh       # Firebase Hosting deployment
│   ├── deploy-backend.sh        # Cloud Run deployment
│   └── deploy-all.sh            # Full stack deployment
│
├── seed/
│   ├── seed-resources.ts        # Seed resource registry
│   ├── seed-users.ts            # Seed test users
│   └── seed-incidents.ts        # Seed demo incidents
│
├── setup/
│   ├── create-firestore-indexes.sh
│   ├── setup-cloud-tasks.sh
│   └── setup-cloud-storage.sh
│
└── utils/
    ├── export-analytics.ts
    ├── archive-incidents.ts
    └── health-check.sh
```

---

## 5.7 Assets Structure

```
assets/
├── brand/
│   ├── logo.svg
│   ├── logo-dark.svg
│   ├── logo-mark.svg
│   └── brand-guidelines.pdf
│
├── design/
│   ├── figma-exports/
│   ├── wireframes/
│   └── color-palette.md
│
└── presentation/
    ├── pitch-deck.pptx
    ├── demo-screenshots/
    └── architecture-diagrams/
```

---

*Next: [System Architecture →](./06-system-architecture.md)*
