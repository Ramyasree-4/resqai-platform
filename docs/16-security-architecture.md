# Section 16 – Security Architecture

---

## 16.1 Security Layers Overview

```
Internet Request
       │
       ▼
[1. Cloud Armor — WAF + DDoS]
       │
       ▼
[2. API Gateway — Rate Limiting + Auth Check]
       │
       ▼
[3. Firebase Auth — JWT Verification]
       │
       ▼
[4. Express Middleware — Role Authorization]
       │
       ▼
[5. Business Logic — Data Scope Enforcement]
       │
       ▼
[6. Firestore Security Rules — Final Gate]
       │
       ▼
[Data Access Granted / Denied]
```

---

## 16.2 Firebase Authentication

### Auth Providers Configured

```
Firebase Authentication Providers:
  ✅ Email/Password
  ✅ Google OAuth 2.0
  ✅ Phone (OTP via SMS)
  ✅ Multi-Factor Authentication (TOTP)
```

### Custom Claims (Role in JWT Token)

Firebase custom claims are set by the backend when a user's role is assigned:

```typescript
// Server-side: Set custom claims on role assignment
await admin.auth().setCustomUserClaims(uid, {
  role: 'DISTRICT_OFFICER',
  district: 'Khurda',
  state: 'Odisha',
  organizationId: 'org-001'
})
```

**JWT Payload (decoded):**

```json
{
  "uid": "firebase-uid-abc123",
  "email": "officer@khurda.gov.in",
  "role": "DISTRICT_OFFICER",
  "district": "Khurda",
  "state": "Odisha",
  "organizationId": "org-001",
  "iat": 1705315200,
  "exp": 1705318800,
  "iss": "https://securetoken.google.com/resqai-prod"
}
```

### Token Lifecycle

| Token Type | Expiry | Storage | Refresh |
|-----------|--------|---------|---------|
| ID Token (access) | 1 hour | Memory only (never localStorage) | Auto via Firebase SDK |
| Refresh Token | 7 days | httpOnly cookie | Silent background refresh |
| Custom Token | 1 hour | Server-side only | N/A |

---

## 16.3 JWT Middleware (Backend)

```typescript
// middleware/authenticate.ts

export const authenticate = async (req: Request, res: Response, next: NextFunction) => {
  const authHeader = req.headers.authorization

  if (!authHeader?.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Missing authorization token' })
  }

  const token = authHeader.split('Bearer ')[1]

  try {
    // Verify token with Firebase Admin SDK (checks signature + expiry)
    const decoded = await admin.auth().verifyIdToken(token, true) // checkRevoked=true
    
    req.user = {
      uid: decoded.uid,
      email: decoded.email,
      role: decoded.role as UserRole,
      district: decoded.district,
      state: decoded.state
    }
    next()
  } catch (error) {
    return res.status(401).json({ error: 'Invalid or expired token' })
  }
}
```

---

## 16.4 Role-Based Access Control (RBAC)

```typescript
// middleware/authorize.ts

export const authorize = (...allowedRoles: UserRole[]) => {
  return (req: Request, res: Response, next: NextFunction) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Unauthorized' })
    }
    
    if (!allowedRoles.includes(req.user.role)) {
      return res.status(403).json({ 
        error: 'Forbidden: insufficient permissions',
        required: allowedRoles,
        current: req.user.role
      })
    }
    
    next()
  }
}

// Usage in routes:
router.get('/incidents', 
  authenticate, 
  authorize('AUTHORITY', 'DISTRICT_OFFICER', 'STATE_OFFICER', 'ADMIN'),
  incidentController.list
)

router.put('/incidents/:id/status',
  authenticate,
  authorize('AUTHORITY', 'DISTRICT_OFFICER', 'STATE_OFFICER', 'ADMIN'),
  validate(updateStatusSchema),
  incidentController.updateStatus
)
```

### District Scope Enforcement

```typescript
// In incident service: enforce district scope
const getIncidents = async (filters: IncidentFilters, user: AuthUser) => {
  let query = db.collection('incidents')

  // CITIZEN: can only see their own incidents
  if (user.role === 'CITIZEN') {
    query = query.where('reportedBy', '==', user.uid)
  }
  // AUTHORITY/DISTRICT_OFFICER: limited to their district
  else if (['AUTHORITY', 'DISTRICT_OFFICER', 'NGO'].includes(user.role)) {
    query = query.where('location.district', '==', user.district)
  }
  // STATE_OFFICER: limited to their state
  else if (user.role === 'STATE_OFFICER') {
    query = query.where('location.state', '==', user.state)
  }
  // ADMIN: no restriction

  return query
}
```

---

## 16.5 Firestore Security Rules

```javascript
// firestore.rules

rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
  
    // Helper functions
    function isAuthenticated() {
      return request.auth != null;
    }
    
    function getUserRole() {
      return request.auth.token.role;
    }
    
    function isAdmin() {
      return getUserRole() == 'ADMIN';
    }
    
    function isAuthority() {
      return getUserRole() in ['AUTHORITY', 'DISTRICT_OFFICER', 'STATE_OFFICER', 'ADMIN'];
    }
    
    function isStateOfficer() {
      return getUserRole() in ['STATE_OFFICER', 'ADMIN'];
    }
    
    function isSameDistrict(resource) {
      return request.auth.token.district == resource.data.location.district;
    }
    
    function isSameState(resource) {
      return request.auth.token.state == resource.data.location.state;
    }
    
    function isOwner(resource) {
      return request.auth.uid == resource.data.reportedBy;
    }

    // ─── USERS ───────────────────────────────────────────────────────────
    match /users/{userId} {
      // Users can read and write their own document
      allow read: if isAuthenticated() && 
                     (request.auth.uid == userId || isAdmin());
      allow update: if isAuthenticated() && 
                       request.auth.uid == userId &&
                       !('role' in request.resource.data);  // Cannot change own role
      allow create: if isAuthenticated() && request.auth.uid == userId;
      allow delete: if isAdmin();
    }

    // ─── INCIDENTS ───────────────────────────────────────────────────────
    match /incidents/{incidentId} {
      // Read: own incidents (citizen) | district (authority) | state | all (admin)
      allow read: if isAuthenticated() && (
        isOwner(resource) ||
        (isAuthority() && isSameDistrict(resource)) ||
        (isStateOfficer() && isSameState(resource)) ||
        isAdmin()
      );
      
      // Create: any authenticated user
      allow create: if isAuthenticated() &&
                       request.resource.data.reportedBy == request.auth.uid;
      
      // Update: owner (limited fields) | authority in district | admin
      allow update: if isAuthenticated() && (
        (isOwner(resource) && onlyUpdatingAllowedCitizenFields()) ||
        (isAuthority() && isSameDistrict(resource)) ||
        isAdmin()
      );
      
      allow delete: if isAdmin();

      // ─── COMMENTS (subcollection) ───────────────────────────────────
      match /comments/{commentId} {
        allow read: if isAuthenticated() && (
          isOwner(get(/databases/$(database)/documents/incidents/$(incidentId))) ||
          isAuthority()
        );
        allow create: if isAuthenticated();
        allow update, delete: if isAuthenticated() && 
                                  request.auth.uid == resource.data.authorId;
      }

      // ─── STATUS HISTORY (subcollection) ───────────────────────────────
      match /statusHistory/{historyId} {
        allow read: if isAuthenticated();
        allow write: if false;  // Written only by backend service account
      }
    }

    // ─── RESOURCES ───────────────────────────────────────────────────────
    match /resources/{resourceId} {
      allow read: if isAuthenticated();
      allow create, update: if isAuthenticated() && isAuthority();
      allow delete: if isAdmin();
    }

    // ─── NOTIFICATIONS ───────────────────────────────────────────────────
    match /notifications/{notificationId} {
      allow read: if isAuthenticated() && (
        request.auth.uid == resource.data.recipientId ||
        isAdmin()
      );
      allow update: if isAuthenticated() && 
                       request.auth.uid == resource.data.recipientId &&
                       request.resource.data.diff(resource.data).affectedKeys()
                         .hasOnly(['isRead', 'readAt']);
      allow create, delete: if false;  // Backend only
    }

    // ─── ANALYTICS ───────────────────────────────────────────────────────
    match /analytics/{analyticsId} {
      allow read: if isAuthenticated() && isAuthority();
      allow write: if false;  // Backend service account only
    }

    // ─── SETTINGS ────────────────────────────────────────────────────────
    match /settings/{settingId} {
      allow read: if isAuthenticated();
      allow write: if isAdmin();
    }

    // ─── AUDIT LOGS ──────────────────────────────────────────────────────
    match /auditLogs/{auditId} {
      allow read: if isAdmin();
      allow write: if false;  // Backend service account only
    }

    // ─── FEEDBACK ────────────────────────────────────────────────────────
    match /feedback/{feedbackId} {
      allow read: if isAuthenticated() && (
        request.auth.uid == resource.data.submittedBy || isAdmin()
      );
      allow create: if isAuthenticated() &&
                       request.resource.data.submittedBy == request.auth.uid;
      allow update, delete: if isAdmin();
    }
  }
}
```

---

## 16.6 API Security

### Rate Limiting Configuration

```typescript
// Rate limits per endpoint category
const rateLimits = {
  // Public endpoints
  'POST /auth/register':     { window: '1h', max: 5  },
  'POST /auth/login':        { window: '15m', max: 10 },
  'POST /incidents/sos':     { window: '1m', max: 5  },  // More lenient for SOS

  // Authenticated endpoints
  'POST /incidents':         { window: '1h', max: 20  },
  'GET /*':                  { window: '1m', max: 100 },
  'PUT /*':                  { window: '1m', max: 50  },

  // AI endpoints
  'POST /ai/*':              { window: '1m', max: 10  },
  
  // Admin endpoints
  '/admin/*':                { window: '1m', max: 200 },
}
```

### Input Validation (Zod)

```typescript
// All request bodies validated with Zod schemas
const createIncidentSchema = z.object({
  title: z.string().min(5).max(200).trim(),
  description: z.string().min(20).max(2000).trim(),
  incidentType: z.enum(['FLOOD','CYCLONE','EARTHQUAKE','LANDSLIDE','FIRE',
                        'MEDICAL','INDUSTRIAL','DROUGHT','CIVIL_UNREST','OTHER']),
  urgencyLevel: z.enum(['LOW','MEDIUM','HIGH','CRITICAL']),
  affectedPeople: z.number().int().min(1).max(1000000),
  location: z.object({
    address: z.string().max(500),
    district: z.string().max(100),
    state: z.string().max(100),
    coordinates: z.object({
      latitude: z.number().min(-90).max(90),
      longitude: z.number().min(-180).max(180)
    })
  })
})
```

### Security Headers (Helmet.js)

```typescript
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "https://maps.googleapis.com", "https://apis.google.com"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      imgSrc: ["'self'", "https://maps.gstatic.com", "data:", "blob:"],
      connectSrc: ["'self'", "https://*.googleapis.com", "wss://*.firebaseio.com"]
    }
  },
  hsts: { maxAge: 31536000, includeSubDomains: true, preload: true },
  frameguard: { action: 'deny' },
  noSniff: true,
  xssFilter: true
}))
```

---

## 16.7 Secrets Management

All secrets stored in **Google Cloud Secret Manager**. Zero secrets in code or environment files in production.

| Secret | Name in Secret Manager |
|--------|----------------------|
| Gemini API Key | `resqai-gemini-api-key` |
| Firebase Service Account | `resqai-firebase-sa-key` |
| Maps API Key (server) | `resqai-maps-server-key` |
| SendGrid API Key | `resqai-sendgrid-key` |
| Twilio/MSG91 Key | `resqai-sms-key` |
| JWT Secret (custom tokens) | `resqai-jwt-secret` |

**Access:** Cloud Run service account has `Secret Manager Accessor` role only.

---

## 16.8 Cloud Armor Configuration

```yaml
# Cloud Armor Security Policy
security_policy:
  name: resqai-security-policy
  rules:
    # Block known malicious IPs
    - priority: 1000
      action: deny(403)
      match:
        expr: "origin.ip in ['malicious-ip-list']"
    
    # Rate limit aggressive IPs
    - priority: 2000
      action: throttle
      rate_limit_options:
        rate_limit_threshold:
          count: 1000
          interval_sec: 60
    
    # OWASP CRS rules
    - priority: 3000
      action: deny(403)
      match:
        expr: "evaluatePreconfiguredExpr('sqli-v33-stable')"
    
    - priority: 3001
      action: deny(403)
      match:
        expr: "evaluatePreconfiguredExpr('xss-v33-stable')"
    
    # Allow all other traffic
    - priority: 2147483647
      action: allow
      match:
        versioned_expr: SRC_IPS_V1
        config:
          src_ip_ranges: ['*']
```

---

## 16.9 Data Privacy & Compliance

### PII Data Handling

| Data Type | Storage | Retention | Access |
|-----------|---------|-----------|--------|
| Email address | Firestore (encrypted) | Account lifetime | User + Admin |
| Phone number | Firestore (encrypted) | Account lifetime | User + Admin |
| GPS coordinates | Firestore | 90 days post-resolution | Authority + Admin |
| Incident description | Firestore | 1 year, then anonymized | Authority scope |
| Profile photo | Cloud Storage | Account lifetime | User only |
| Audit logs | Firestore | 3 years | Admin only |

### Data Anonymization (Post-Incident)
- After 1 year: incident descriptions stripped of PII (name, phone, address)
- Reporter field replaced with anonymized token
- Coordinates aggregated to district level

---

*Next: [Deployment Architecture →](./17-deployment-architecture.md)*
