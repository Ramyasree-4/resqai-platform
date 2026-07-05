# ResQAI – AI-Powered Disaster Response & Resource Allocation Platform

> Complete Software Architecture & Design Documentation  
> National-Level Hackathon – Production-Ready Architecture

---

## Document Index

| # | Document | Description |
|---|----------|-------------|
| 01 | [Project Vision](./01-project-vision.md) | Vision, Mission, Objectives, Impact |
| 02 | [Functional Requirements](./02-functional-requirements.md) | Complete FR by module |
| 03 | [Non-Functional Requirements](./03-non-functional-requirements.md) | NFR: Security, Performance, Scalability |
| 04 | [Technology Stack](./04-technology-stack.md) | Full stack recommendation |
| 05 | [Project Folder Structure](./05-folder-structure.md) | Frontend, Backend, Shared, Docs |
| 06 | [System Architecture](./06-system-architecture.md) | Layered architecture design |
| 07 | [Database Design](./07-database-design.md) | Firestore collections & schema |
| 08 | [ER Diagram](./08-er-diagram.md) | Entity Relationship Diagram (text) |
| 09 | [REST API Design](./09-api-design.md) | All endpoints with request/response |
| 10 | [User Roles & Permissions](./10-user-roles.md) | RBAC design |
| 11 | [Application Flow](./11-application-flow.md) | User journeys & process flows |
| 12 | [UI Wireframes](./12-ui-wireframes.md) | Detailed page layouts |
| 13 | [Dashboard Design](./13-dashboard-design.md) | KPIs, charts, filters |
| 14 | [Gemini AI Integration](./14-gemini-integration.md) | Prompt design, AI flows |
| 15 | [Google Maps Integration](./15-maps-integration.md) | Markers, heatmaps, tracking |
| 16 | [Security Architecture](./16-security-architecture.md) | Auth, RBAC, Firestore rules |
| 17 | [Deployment Architecture](./17-deployment-architecture.md) | Cloud Run, Firebase, CI/CD |
| 18 | [Project Timeline](./18-project-timeline.md) | 3-day hackathon plan |
| 19 | [Hackathon Presentation](./19-presentation-flow.md) | Pitch structure |
| 20 | [Future Enhancements](./20-future-enhancements.md) | Roadmap & innovations |

---

## Platform Overview

**ResQAI** is a national-level AI-powered disaster response and resource allocation platform built entirely on Google Cloud.  
It ingests emergency reports from citizens across multiple channels, applies Google Gemini AI for intelligent triage and decision support,  
and provides disaster management authorities with a real-time decision intelligence dashboard.

### Core Technology
- **Frontend:** React 18 + TypeScript + Tailwind CSS + Shadcn UI
- **Backend:** Node.js + Express on Google Cloud Run
- **Database:** Firebase Firestore (NoSQL, real-time)
- **Auth:** Firebase Authentication + Custom JWT
- **AI Engine:** Google Gemini 1.5 Pro
- **Maps:** Google Maps Platform
- **Hosting:** Firebase Hosting + Cloud Run
- **Monitoring:** Google Cloud Monitoring + Firebase Analytics

---

*Architecture Version 1.0 | Generated for National-Level Hackathon Submission*
