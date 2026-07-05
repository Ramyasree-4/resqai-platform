# Section 03 – Non-Functional Requirements

---

## 3.1 Security

| ID | Requirement | Standard / Target |
|----|-------------|-------------------|
| NFR-SEC-001 | All data in transit encrypted | TLS 1.3 mandatory |
| NFR-SEC-002 | All data at rest encrypted | AES-256 (Firestore default) |
| NFR-SEC-003 | Authentication token expiry | Access: 15 min, Refresh: 7 days |
| NFR-SEC-004 | Role-Based Access Control | Firestore Security Rules + middleware |
| NFR-SEC-005 | API rate limiting | 100 req/min per IP for public, 1000 for authenticated |
| NFR-SEC-006 | Input validation & sanitization | All endpoints, prevent SQL/NoSQL injection, XSS |
| NFR-SEC-007 | OWASP Top 10 compliance | Full compliance required |
| NFR-SEC-008 | 2FA for admin and authority users | TOTP or SMS OTP |
| NFR-SEC-009 | Audit logging | All state-changing operations logged immutably |
| NFR-SEC-010 | PII data handling | PDPB 2023 (India) compliant, data minimization |
| NFR-SEC-011 | Gemini API key security | Never exposed to client; server-side proxy only |
| NFR-SEC-012 | DDoS protection | Cloud Armor WAF on API Gateway |
| NFR-SEC-013 | CSRF protection | SameSite cookies + CSRF tokens |
| NFR-SEC-014 | Security headers | HSTS, CSP, X-Frame-Options, X-Content-Type-Options |
| NFR-SEC-015 | Vulnerability scanning | Automated SAST/DAST in CI/CD pipeline |

---

## 3.2 Performance

| ID | Requirement | Target Metric |
|----|-------------|---------------|
| NFR-PER-001 | Page load time (initial) | < 2.5 seconds (LCP) on 4G |
| NFR-PER-002 | Page load time (subsequent) | < 1 second (cached assets) |
| NFR-PER-003 | API response time (P95) | < 500ms for non-AI endpoints |
| NFR-PER-004 | AI triage response time | < 5 seconds per incident |
| NFR-PER-005 | Map render time | < 1 second for up to 500 markers |
| NFR-PER-006 | Real-time update latency | < 2 seconds (Firestore live listener) |
| NFR-PER-007 | Database query time (P95) | < 200ms per Firestore query |
| NFR-PER-008 | Report submission response | < 1 second acknowledgement |
| NFR-PER-009 | Dashboard load time | < 3 seconds (all KPIs loaded) |
| NFR-PER-010 | Notification delivery time | Push: < 3s, SMS: < 30s, Email: < 60s |
| NFR-PER-011 | Search/filter response | < 300ms for any filtered list |
| NFR-PER-012 | File upload (5 media files) | < 10 seconds on 4G |

---

## 3.3 Availability

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-AVL-001 | Overall system uptime | 99.9% (< 8.7 hours/year downtime) |
| NFR-AVL-002 | Disaster-period uptime | 99.99% (< 52 minutes/year) |
| NFR-AVL-003 | Planned maintenance windows | Off-peak hours only (2 AM – 4 AM IST) |
| NFR-AVL-004 | RTO (Recovery Time Objective) | < 15 minutes |
| NFR-AVL-005 | RPO (Recovery Point Objective) | < 5 minutes (Firestore continuous backup) |
| NFR-AVL-006 | Health check endpoints | All services expose /health endpoint |
| NFR-AVL-007 | Auto-failover | Cloud Run automatic instance restart |
| NFR-AVL-008 | Multi-region backup | Firestore multi-region (nam5 primary) |
| NFR-AVL-009 | CDN availability | Firebase Hosting CDN (global edge) |
| NFR-AVL-010 | Offline capability | PWA service worker caches critical UI |

---

## 3.4 Scalability

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-SCA-001 | Concurrent users | 100,000+ simultaneous users |
| NFR-SCA-002 | Incident ingestion rate | 10,000 incidents/hour sustained |
| NFR-SCA-003 | Horizontal auto-scaling | Cloud Run scales 1 → 1000 instances automatically |
| NFR-SCA-004 | Database throughput | Firestore: unlimited reads, 1M writes/day per collection |
| NFR-SCA-005 | AI processing throughput | Gemini API: queue-based, scalable via Cloud Tasks |
| NFR-SCA-006 | Media storage scaling | Cloud Storage: auto-scales to petabytes |
| NFR-SCA-007 | Notification throughput | FCM: 500 messages/second per project |
| NFR-SCA-008 | API Gateway scaling | Cloud Endpoints auto-scales with Cloud Run |
| NFR-SCA-009 | Search at scale | Firestore composite indexes for all query patterns |
| NFR-SCA-010 | Cost scaling | Pay-per-use model; no idle server costs |

---

## 3.5 Reliability

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-REL-001 | Data durability | 99.999999999% (Firestore SLA) |
| NFR-REL-002 | Idempotent API design | All POST/PUT operations safe to retry |
| NFR-REL-003 | Circuit breaker pattern | Implemented for Gemini AI and Maps API calls |
| NFR-REL-004 | AI fallback | If Gemini unavailable, rule-based classifier activates |
| NFR-REL-005 | Message queue reliability | Cloud Tasks: at-least-once delivery for AI jobs |
| NFR-REL-006 | Error handling | Global error boundaries; no unhandled promise rejections |
| NFR-REL-007 | Graceful degradation | Map falls back to static tiles if Maps API unavailable |
| NFR-REL-008 | Data consistency | Firestore transactions for multi-document updates |
| NFR-REL-009 | Retry logic | Exponential backoff on all external API calls |
| NFR-REL-010 | Monitoring & alerting | PagerDuty-equivalent alerting for P0/P1 incidents |

---

## 3.6 Usability

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-USA-001 | Time to first report submission | < 3 minutes for a first-time citizen user |
| NFR-USA-002 | Mobile-first responsive design | Fully functional on 320px–2560px screens |
| NFR-USA-003 | Intuitive navigation | Max 3 clicks to reach any primary function |
| NFR-USA-004 | Error messages | Clear, actionable, human-readable error text |
| NFR-USA-005 | Loading states | Skeleton screens and progress indicators on all async operations |
| NFR-USA-006 | Onboarding | Role-specific guided tour on first login |
| NFR-USA-007 | Color coding | Consistent severity colors: Green/Yellow/Orange/Red |
| NFR-USA-008 | SOS accessibility | SOS button visible and tappable without login |
| NFR-USA-009 | Keyboard navigation | Full keyboard navigability for authority dashboard |
| NFR-USA-010 | Language | English primary; Hindi secondary (Phase 1) |

---

## 3.7 Maintainability

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-MNT-001 | Code documentation | JSDoc for all functions; OpenAPI 3.0 for all endpoints |
| NFR-MNT-002 | Test coverage | > 80% unit test coverage for business logic |
| NFR-MNT-003 | Code style enforcement | ESLint + Prettier; enforced in CI |
| NFR-MNT-004 | Dependency management | Pinned versions; Dependabot automated updates |
| NFR-MNT-005 | Logging | Structured JSON logs; severity levels (DEBUG/INFO/WARN/ERROR) |
| NFR-MNT-006 | Configuration management | Environment-based config; no secrets in code |
| NFR-MNT-007 | Deployment pipeline | GitHub Actions CI/CD; one-command deployment |
| NFR-MNT-008 | Feature flags | Firebase Remote Config for gradual feature rollouts |
| NFR-MNT-009 | Database migrations | Firestore schema versioning strategy documented |
| NFR-MNT-010 | Modular architecture | Feature-based folder structure; loose coupling |

---

## 3.8 Accessibility

| ID | Requirement | Standard |
|----|-------------|---------|
| NFR-ACC-001 | WCAG compliance level | WCAG 2.1 Level AA |
| NFR-ACC-002 | Screen reader support | Full ARIA labeling on all interactive elements |
| NFR-ACC-003 | Color contrast ratio | Minimum 4.5:1 for normal text, 3:1 for large text |
| NFR-ACC-004 | Focus management | Visible focus indicators on all focusable elements |
| NFR-ACC-005 | Alt text | All images and icons have descriptive alt text |
| NFR-ACC-006 | Form labels | All form inputs have explicit labels |
| NFR-ACC-007 | Error identification | Errors identified in text (not color alone) |
| NFR-ACC-008 | Keyboard traps | No keyboard traps; modals closable via Escape |
| NFR-ACC-009 | Skip navigation | Skip-to-main-content link on all pages |
| NFR-ACC-010 | Touch targets | Minimum 44x44px touch targets on mobile |
| NFR-ACC-011 | Text scaling | UI functional at 200% browser text size |
| NFR-ACC-012 | Motion sensitivity | Animations respect prefers-reduced-motion media query |

---

*Next: [Technology Stack →](./04-technology-stack.md)*
