# Section 18 – Project Timeline (3-Day Hackathon)

---

## Strategy Overview

**Priority Rule:** Build the demo path first. Every hour of coding should produce something demoable.

**Demo Path (Minimum Viable Demo):**
1. Citizen submits an incident → AI analysis runs → Severity shown
2. Authority sees incident on dashboard → Assigns resource
3. Maps shows live incident markers
4. AI shows reasoning panel

**Team Assumption:** 3–4 developers + 1 designer

---

## Day 1 — Foundation & Core Features (Hours 0–24)

### Morning Block (Hours 0–6): Project Setup

| Time | Task | Owner |
|------|------|-------|
| 0:00–1:00 | Initialize repos, Firebase project, GCP project setup | DevOps/Lead |
| 0:00–1:00 | Figma design setup, color system, component planning | Designer |
| 1:00–2:00 | Backend: Express skeleton, Firebase Admin init, env config | Backend Dev |
| 1:00–2:00 | Frontend: Vite + React + TS + Tailwind + Shadcn setup | Frontend Dev |
| 2:00–3:00 | Firebase Auth: email + Google login, custom claims | Backend Dev |
| 2:00–3:00 | Frontend: Router setup, ProtectedRoute, Login/Register pages | Frontend Dev |
| 3:00–4:00 | Firestore collections: users, incidents, resources — seed data | Backend Dev |
| 3:00–4:00 | Frontend: AppShell, Sidebar, Navbar, theme tokens | Designer + FE |
| 4:00–6:00 | Authentication flow E2E: register → login → JWT → dashboard | Full Stack |

### Afternoon Block (Hours 6–14): Core Incident System

| Time | Task | Owner |
|------|------|-------|
| 6:00–8:00 | Backend: Incident CRUD API (POST, GET, GET/:id) | Backend Dev |
| 6:00–8:00 | Frontend: Citizen Dashboard + Report Incident multi-step form | Frontend Dev |
| 8:00–9:00 | Backend: File upload to Cloud Storage (media files) | Backend Dev |
| 8:00–9:00 | Frontend: GPS capture + Google Maps location picker | Frontend Dev |
| 9:00–11:00 | **Gemini AI Integration** — Core prompt engineering | Backend Dev |
|  | - Classification, severity, recommendations, summary, reasoning | |
|  | - Cloud Tasks queue for async processing | |
| 9:00–11:00 | Frontend: Incident list with status badges, real-time Firestore listener | Frontend Dev |
| 11:00–12:00 | Integration test: Submit incident → AI analysis → Firestore update | Full Stack |
| 12:00–14:00 | Frontend: Incident Details page with full AI Analysis panel | Frontend Dev |

### Evening Block (Hours 14–24): Authority Dashboard

| Time | Task | Owner |
|------|------|-------|
| 14:00–17:00 | Frontend: Authority Dashboard — KPI cards, incident queue, Firestore listeners | Frontend Dev |
| 14:00–17:00 | Backend: Dashboard stats API, resource assignment API | Backend Dev |
| 17:00–19:00 | Frontend: Google Maps integration — incident markers, severity colors | Frontend Dev |
| 17:00–19:00 | Backend: Resource model, seed 20 resources, GET /resources/nearby | Backend Dev |
| 19:00–21:00 | Frontend: Resource Assignment panel in Incident Details | Frontend Dev |
| 19:00–21:00 | Backend: Status update API + notification trigger (FCM push) | Backend Dev |
| 21:00–22:00 | E2E demo path test: Submit → AI → Dashboard → Assign → Notify | Full Stack |
| 22:00–24:00 | Bug fixes, polish, commit | All |

**Day 1 Deliverable:** Working E2E demo path. Citizen can submit incident, AI analyzes it, authority dashboard shows it sorted by severity, authority can assign resources.

---

## Day 2 — Features, Maps & Analytics (Hours 24–48)

### Morning Block (Hours 24–32): Maps, Analytics & Notifications

| Time | Task | Owner |
|------|------|-------|
| 24:00–26:00 | Frontend: Full operations map — heatmap, resource markers, route overlay | Frontend Dev |
| 24:00–26:00 | Backend: Analytics aggregation API, dashboard chart data endpoints | Backend Dev |
| 26:00–28:00 | Frontend: Analytics Dashboard — all charts (Recharts) | Frontend Dev |
| 26:00–28:00 | Backend: Multi-channel notifications (FCM + email via SendGrid) | Backend Dev |
| 28:00–30:00 | Frontend: Notification center + real-time bell counter | Frontend Dev |
| 28:00–30:00 | Backend: SOS endpoint (fast path, no AI wait) | Backend Dev |
| 30:00–32:00 | Frontend: Infrastructure layers (hospitals, shelters) on map | Frontend Dev |

### Afternoon Block (Hours 32–40): AI Polish & Security

| Time | Task | Owner |
|------|------|-------|
| 32:00–34:00 | AI: Duplicate detection algorithm + cluster detection | Backend Dev |
| 32:00–34:00 | Frontend: AI feedback panel (thumbs up/down, override flow) | Frontend Dev |
| 34:00–36:00 | Security: Firestore rules, rate limiting, Helmet.js | Backend Dev |
| 34:00–36:00 | Frontend: Role-based rendering, ProtectedRoute by role | Frontend Dev |
| 36:00–38:00 | Backend: Situation report generation (Gemini PDF narrative) | Backend Dev |
| 36:00–38:00 | Frontend: Reports page + PDF export | Frontend Dev |
| 38:00–40:00 | Frontend: Citizen tracking page with status timeline | Frontend Dev |

### Evening Block (Hours 40–48): Admin & Polish

| Time | Task | Owner |
|------|------|-------|
| 40:00–42:00 | Admin Portal: User management, resource registry | Frontend Dev |
| 40:00–42:00 | Backend: Admin APIs (user management, audit logs, settings) | Backend Dev |
| 42:00–44:00 | Frontend: Profile page, Settings page, landing page polish | Designer + FE |
| 44:00–46:00 | Deploy: Firebase Hosting + Cloud Run staging environment | DevOps |
| 46:00–48:00 | Full E2E testing on staging, bug fixes | All |

**Day 2 Deliverable:** Complete platform with all major features working on staging. Full demo flow polished.

---

## Day 3 — Production, Polish & Presentation (Hours 48–72)

### Morning Block (Hours 48–56): Production Deployment

| Time | Task | Owner |
|------|------|-------|
| 48:00–50:00 | Production Firebase + GCP deployment | DevOps |
| 48:00–50:00 | Seed realistic demo data (incidents, resources, users) | Backend Dev |
| 50:00–52:00 | Final UI polish — animations, loading states, error boundaries | Designer + FE |
| 50:00–52:00 | Performance optimization: lazy loading, bundle size audit | Frontend Dev |
| 52:00–54:00 | Accessibility pass: ARIA labels, keyboard nav, contrast | Designer |
| 52:00–54:00 | PWA setup: service worker, manifest, offline draft saving | Frontend Dev |
| 54:00–56:00 | Final production testing + smoke tests | All |

### Afternoon Block (Hours 56–66): Presentation Prep

| Time | Task | Owner |
|------|------|-------|
| 56:00–60:00 | Build pitch deck (Problem → Solution → Architecture → Demo → Impact) | Lead + Designer |
| 60:00–64:00 | Record demo video (2 minutes) as backup | Lead |
| 64:00–66:00 | Prepare live demo script — practice 3 times | All |

### Final Block (Hours 66–72): Final Rehearsal

| Time | Task | Owner |
|------|------|-------|
| 66:00–69:00 | Full presentation rehearsal — timing, transitions, demo | All |
| 69:00–71:00 | Last-minute fixes from rehearsal | Dev |
| 71:00–72:00 | Final commit, tag release, submit | Lead |

**Day 3 Deliverable:** Production-deployed application + polished presentation + 2-minute demo video.

---

## Feature Priority Matrix

| Feature | Priority | Day |
|---------|----------|-----|
| Incident Submission (Citizen) | P0 | Day 1 |
| Gemini AI Analysis | P0 | Day 1 |
| Authority Dashboard | P0 | Day 1 |
| Resource Assignment | P0 | Day 1 |
| Google Maps (Incidents) | P0 | Day 1 |
| AI Analysis Panel (Reasoning) | P0 | Day 1 |
| Real-time Firestore Updates | P0 | Day 1 |
| Analytics Charts | P1 | Day 2 |
| Heatmap | P1 | Day 2 |
| Notifications | P1 | Day 2 |
| SOS Button | P1 | Day 2 |
| Duplicate Detection | P1 | Day 2 |
| Situation Reports | P1 | Day 2 |
| Admin Portal | P2 | Day 2 |
| PWA Offline Mode | P2 | Day 3 |
| SMS Notifications | P3 | Day 3 (if time) |

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Gemini API rate limits | Use Flash model for bulk, Pro for demo incidents only |
| Maps API quota | Use one Maps API key for demo, cache all responses |
| Firebase Auth issues | Pre-create demo accounts in Firestore |
| Demo network failure | Pre-record complete 2-minute demo video backup |
| Cloud Run cold start | Set minimum instances to 2 |

---

*Next: [Hackathon Presentation Flow →](./19-presentation-flow.md)*
