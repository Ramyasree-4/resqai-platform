# Section 07 – Database Design (Firebase Firestore)

---

## 7.1 Design Principles

- **Document-oriented**: Each entity stored as a JSON document
- **Denormalization**: Frequently read data duplicated for query performance
- **Subcollections**: Used for 1-to-many relationships (e.g., incident comments, audit log per incident)
- **Composite Indexes**: Defined for every multi-field query
- **Security Rules**: Collection-level access control enforced at Firestore layer

---

## 7.2 Collection: `users`

**Document ID:** Firebase Auth UID (auto-generated)

```
users/{userId}
{
  // Identity
  uid:               string       // Firebase Auth UID (Primary Key)
  email:             string       // Unique email address
  phoneNumber:       string       // E.164 format (+91XXXXXXXXXX)
  displayName:       string       // Full name
  photoURL:          string?      // Profile photo GCS URL
  
  // Role & Organization
  role:              string       // Enum: CITIZEN | AUTHORITY | DISTRICT_OFFICER | 
                                  //       STATE_OFFICER | NGO | VOLUNTEER | ADMIN
  organizationId:    string?      // Ref: organizations/{orgId}
  organizationName:  string?      // Denormalized for display
  designation:       string?      // Job title
  badgeNumber:       string?      // For official authority users
  
  // Location
  district:          string       // Assigned/home district
  state:             string       // Assigned/home state
  pincode:           string
  address:           string?
  
  // Emergency Contacts
  emergencyContacts: [
    {
      name:          string
      phone:         string
      relationship:  string
    }
  ]
  
  // Profile Flags
  isVerified:        boolean      // Identity verification status
  isActive:          boolean      // Account active status
  hasDisability:     boolean      // Priority rescue tag
  disabilityDetails: string?
  
  // Authentication
  authProviders:     string[]     // ["password", "google.com", "phone"]
  mfaEnabled:        boolean      // 2FA enabled for authority/admin
  lastPasswordChange: timestamp
  
  // Preferences
  notificationPreferences: {
    pushEnabled:     boolean
    smsEnabled:      boolean
    emailEnabled:    boolean
    language:        string       // "en" | "hi" | "or" | "bn"
  }
  
  // Device
  fcmTokens:         string[]     // FCM push tokens (multi-device)
  
  // Metadata
  createdAt:         timestamp
  updatedAt:         timestamp
  lastLoginAt:       timestamp
  lastLoginIP:       string
  loginCount:        number
  createdBy:         string?      // Admin UID if created by admin
}
```

**Subcollections:**
```
users/{userId}/sessions/{sessionId}
{
  token:         string
  deviceInfo:    string
  ipAddress:     string
  createdAt:     timestamp
  expiresAt:     timestamp
  isRevoked:     boolean
}
```

---

## 7.3 Collection: `incidents`

**Document ID:** Auto-generated Firestore ID (prefixed `INC-` in display)

```
incidents/{incidentId}
{
  // Identity
  incidentId:        string       // Display ID: INC-2024-XXXXXXXX
  
  // Reporter
  reportedBy:        string       // Ref: users/{userId}
  reporterName:      string       // Denormalized
  reporterPhone:     string       // Denormalized
  isAnonymous:       boolean
  
  // Incident Details
  title:             string       // Short title (user-provided or AI-generated)
  description:       string       // Full description from citizen
  incidentType:      string       // Enum: FLOOD | CYCLONE | EARTHQUAKE | LANDSLIDE |
                                  //       FIRE | MEDICAL | INDUSTRIAL | DROUGHT |
                                  //       CIVIL_UNREST | OTHER
  
  // Location
  location: {
    address:         string       // Human-readable address
    district:        string
    state:           string
    pincode:         string
    coordinates: {
      latitude:      number
      longitude:     number
    }
    geohash:         string       // For geospatial proximity queries
    accuracy:        number       // GPS accuracy in meters
    locationMethod:  string       // "GPS" | "MANUAL" | "IP"
  }
  
  // Scale
  affectedPeople:    number       // Estimated count
  fatalities:        number?      // Confirmed deaths
  injuries:          number?      // Confirmed injuries
  
  // Media
  mediaFiles: [
    {
      fileId:        string
      url:           string       // GCS signed URL
      type:          string       // "image" | "video" | "audio" | "document"
      filename:      string
      size:          number       // bytes
      uploadedAt:    timestamp
    }
  ]
  
  // Status
  status:            string       // Enum: DRAFT | SUBMITTED | AI_PROCESSING |
                                  //       TRIAGED | ASSIGNED | IN_PROGRESS |
                                  //       RESOLVED | CLOSED | ARCHIVED
  urgencyLevel:      string       // User-stated: LOW | MEDIUM | HIGH | CRITICAL
  
  // AI Analysis
  aiAnalysis: {
    analysisId:      string
    processedAt:     timestamp
    modelVersion:    string       // "gemini-1.5-pro"
    
    // Classification
    classifiedType:  string       // AI-determined incident type
    classificationConfidence: number // 0.0 - 1.0
    
    // Severity
    severityScore:   number       // 1 - 10
    severityBand:    string       // LOW | MEDIUM | HIGH | CRITICAL
    
    // Priority
    priorityRank:    number       // Dynamic rank in queue
    priorityScore:   number       // Composite priority score
    
    // Recommendations
    resourceRecommendations: [
      {
        resourceType:   string
        quantity:       number
        urgency:        string
        reason:         string
      }
    ]
    
    // Summary
    situationSummary: string      // Natural language summary
    
    // Explainability
    reasoning: [string]           // Array of reason bullets
    
    // Duplicate detection
    isDuplicate:     boolean
    duplicateOf:     string?      // Ref to original incident if duplicate
    duplicateScore:  number?      // Similarity score 0.0-1.0
    
    // Authority feedback
    authorityFeedback: string?    // "ACCEPTED" | "OVERRIDDEN" | null
    feedbackNote:    string?
  }
  
  // Assignment
  assignedTo: {
    authorityId:     string?      // Ref: users/{userId}
    authorityName:   string?
    assignedAt:      timestamp?
    resources: [
      {
        resourceId:  string       // Ref: resources/{resourceId}
        resourceName: string
        resourceType: string
        assignedAt:  timestamp
        status:      string       // DISPATCHED | EN_ROUTE | ON_SCENE | RETURNING
      }
    ]
  }
  
  // Escalation
  escalation: {
    isEscalated:     boolean
    escalatedAt:     timestamp?
    escalatedBy:     string?
    escalatedTo:     string?      // Role level
    escalationReason: string?
    escalationCount: number
  }
  
  // Links
  linkedIncidents:   string[]     // Refs to related incidents
  eventId:           string?      // Ref: disasterEvents/{eventId}
  
  // Resolution
  resolution: {
    resolvedAt:      timestamp?
    resolvedBy:      string?
    resolutionNote:  string?
    outcome:         string?      // "RESCUED" | "FALSE_ALARM" | "REFERRED" | "DECEASED"
  }
  
  // Metadata
  source:            string       // "WEB" | "MOBILE" | "SMS" | "API"
  version:           number       // Optimistic locking
  createdAt:         timestamp
  updatedAt:         timestamp
  
  // Computed (updated by Cloud Functions)
  responseTimeMinutes: number?    // Time from submission to first assignment
}
```

**Subcollections:**
```
incidents/{incidentId}/comments/{commentId}
{
  authorId:    string
  authorName:  string
  authorRole:  string
  content:     string
  isInternal:  boolean    // Internal authority note vs. visible to citizen
  createdAt:   timestamp
  updatedAt:   timestamp
}

incidents/{incidentId}/statusHistory/{historyId}
{
  fromStatus:  string
  toStatus:    string
  changedBy:   string
  changedAt:   timestamp
  note:        string?
}
```

---

## 7.4 Collection: `resources`

**Document ID:** Auto-generated

```
resources/{resourceId}
{
  // Identity
  resourceId:        string       // Display ID: RES-XXXXXXXX
  name:              string       // e.g., "NDRF Boat Unit 7"
  type:              string       // Enum: RESCUE_TEAM | AMBULANCE | FIRE_TRUCK |
                                  //       RESCUE_BOAT | HELICOPTER | POLICE_UNIT |
                                  //       MEDICAL_UNIT | NGO_UNIT | SHELTER |
                                  //       HOSPITAL | RELIEF_CAMP
  subType:           string?      // More specific type
  
  // Organization
  organizationId:    string       // Owning organization
  organizationName:  string
  district:          string
  state:             string
  
  // Contact
  contactName:       string
  contactPhone:      string
  contactEmail:      string?
  
  // Capacity (for shelters, hospitals)
  capacity: {
    total:           number?
    current:         number?      // Current occupancy
    available:       number?      // Computed: total - current
  }
  
  // Status
  status:            string       // AVAILABLE | DEPLOYED | MAINTENANCE | UNAVAILABLE
  statusUpdatedAt:   timestamp
  statusUpdatedBy:   string
  
  // Current Assignment
  currentAssignment: {
    incidentId:      string?
    incidentTitle:   string?
    assignedAt:      timestamp?
    estimatedReturn: timestamp?
  }
  
  // Location
  baseLocation: {
    address:         string
    district:        string
    coordinates: {
      latitude:      number
      longitude:     number
    }
  }
  currentLocation: {
    coordinates: {
      latitude:      number
      longitude:     number
    }
    updatedAt:       timestamp
    updatedBy:       string       // "MANUAL" | "GPS" | "FIELD_APP"
  }
  
  // Capabilities
  capabilities:      string[]     // e.g., ["WATER_RESCUE", "MEDICAL_FIRST_AID"]
  
  // Metadata
  isActive:          boolean
  registeredAt:      timestamp
  createdBy:         string
  updatedAt:         timestamp
  notes:             string?
}
```

**Subcollections:**
```
resources/{resourceId}/deploymentHistory/{deploymentId}
{
  incidentId:   string
  incidentTitle: string
  deployedAt:   timestamp
  returnedAt:   timestamp?
  deployedBy:   string
  notes:        string?
}
```

---

## 7.5 Collection: `notifications`

**Document ID:** Auto-generated

```
notifications/{notificationId}
{
  // Target
  recipientId:       string       // Ref: users/{userId} (null for broadcast)
  recipientRole:     string?      // For role-based broadcasts
  district:          string?      // For district-wide broadcasts
  
  // Content
  title:             string
  body:              string
  type:              string       // Enum: INCIDENT_STATUS | NEW_INCIDENT | 
                                  //       ASSIGNMENT | ESCALATION | BROADCAST |
                                  //       RESOURCE_UPDATE | SYSTEM | CLUSTER_ALERT
  
  // Reference
  relatedIncidentId: string?
  relatedResourceId: string?
  actionUrl:         string?      // Deep link for notification tap
  
  // Delivery Status
  channels: {
    push: {
      sent:          boolean
      sentAt:        timestamp?
      deliveredAt:   timestamp?
      error:         string?
    }
    sms: {
      sent:          boolean
      sentAt:        timestamp?
      messageId:     string?
      error:         string?
    }
    email: {
      sent:          boolean
      sentAt:        timestamp?
      messageId:     string?
      error:         string?
    }
  }
  
  // Read Status
  isRead:            boolean
  readAt:            timestamp?
  
  // Priority
  priority:          string       // LOW | NORMAL | HIGH | URGENT
  
  // Metadata
  createdAt:         timestamp
  expiresAt:         timestamp?   // Auto-delete old notifications
  createdBy:         string       // System or user UID
}
```

---

## 7.6 Collection: `analytics`

**Document ID:** Date-based (e.g., `daily-2024-01-15` or `hourly-2024-01-15-14`)

```
analytics/{analyticsId}
{
  // Time Dimension
  period:            string       // "HOURLY" | "DAILY" | "WEEKLY" | "MONTHLY"
  date:              string       // ISO date string
  hour:              number?      // 0-23 for hourly
  
  // Scope
  scope:             string       // "NATIONAL" | "STATE" | "DISTRICT"
  district:          string?
  state:             string?
  
  // Incident Metrics
  incidents: {
    total:           number
    new:             number
    resolved:        number
    active:          number
    byType: {
      FLOOD:         number
      CYCLONE:       number
      EARTHQUAKE:    number
      LANDSLIDE:     number
      FIRE:          number
      MEDICAL:       number
      INDUSTRIAL:    number
      OTHER:         number
    }
    bySeverity: {
      LOW:           number
      MEDIUM:        number
      HIGH:          number
      CRITICAL:      number
    }
    byStatus: {
      SUBMITTED:     number
      TRIAGED:       number
      ASSIGNED:      number
      IN_PROGRESS:   number
      RESOLVED:      number
    }
  }
  
  // Response Metrics
  response: {
    avgResponseTimeMinutes:   number
    medianResponseTimeMinutes: number
    p95ResponseTimeMinutes:   number
    avgResolutionTimeHours:   number
    slaBreachCount:           number    // Incidents exceeding SLA
    escalationCount:          number
  }
  
  // Resource Metrics
  resources: {
    totalAvailable:   number
    totalDeployed:    number
    utilizationRate:  number      // 0.0 - 1.0
    deploymentCount:  number
  }
  
  // AI Metrics
  ai: {
    incidentsProcessed:    number
    avgProcessingTimeMs:   number
    recommendationsAccepted: number
    recommendationsOverridden: number
    duplicatesDetected:    number
    fallbackActivations:   number
  }
  
  // User Metrics
  users: {
    activeUsers:     number
    newRegistrations: number
    reportingUsers:  number
  }
  
  // Computed
  computedAt:        timestamp
  isComplete:        boolean      // false during the current period
}
```

---

## 7.7 Collection: `reports`

**Document ID:** Auto-generated

```
reports/{reportId}
{
  reportId:          string
  title:             string
  type:              string       // "SITUATION" | "DAILY_SUMMARY" | "ANALYTICS" | "AUDIT"
  
  // Scope
  generatedBy:       string       // User UID
  district:          string?
  state:             string?
  
  // Time Range
  fromDate:          timestamp
  toDate:            timestamp
  
  // Content
  summary:           string       // AI-generated narrative
  sections: [
    {
      heading:       string
      content:       string
      data:          object?
    }
  ]
  
  // Files
  pdfUrl:            string?      // GCS URL to generated PDF
  csvUrl:            string?      // GCS URL to CSV export
  
  // Metadata
  status:            string       // "GENERATING" | "READY" | "FAILED"
  generatedAt:       timestamp?
  createdAt:         timestamp
  expiresAt:         timestamp    // Auto-delete after 90 days
}
```

---

## 7.8 Collection: `feedback`

**Document ID:** Auto-generated

```
feedback/{feedbackId}
{
  feedbackId:        string
  
  // Source
  submittedBy:       string       // User UID
  submitterRole:     string
  
  // Target
  targetType:        string       // "AI_ANALYSIS" | "PLATFORM" | "INCIDENT"
  targetId:          string       // ID of the AI analysis or incident
  
  // Content
  rating:            number       // 1-5 stars
  sentiment:         string       // "POSITIVE" | "NEGATIVE" | "NEUTRAL"
  category:          string       // "ACCURACY" | "SPEED" | "UI" | "FEATURE_REQUEST"
  comment:           string?
  
  // For AI feedback specifically
  aiAccuracyRating: {
    classificationCorrect: boolean?
    severityAccurate:      boolean?
    recommendationsUseful: boolean?
    summaryAccurate:       boolean?
  }
  
  // Metadata
  createdAt:         timestamp
  resolvedAt:        timestamp?
  resolvedBy:        string?
  resolution:        string?
}
```

---

## 7.9 Collection: `settings`

**Document ID:** Predefined keys

```
settings/system
{
  // Feature Flags
  features: {
    aiEnabled:              boolean
    smsNotificationsEnabled: boolean
    emailNotificationsEnabled: boolean
    mapsEnabled:            boolean
    registrationOpen:       boolean
    maintenanceMode:        boolean
  }
  
  // AI Thresholds
  ai: {
    criticalSeverityThreshold:  number  // Default: 7
    escalationDelayMinutes:     number  // Default: 15
    clusterDetectionCount:      number  // Default: 5
    clusterDetectionWindowHours: number // Default: 1
    massCasualtyThreshold:      number  // Default: 5 critical in 1 hour
    duplicateScoreThreshold:    number  // Default: 0.85
  }
  
  // SLA Configuration
  sla: {
    criticalResponseMinutes:  number   // Default: 30
    highResponseMinutes:      number   // Default: 60
    mediumResponseMinutes:    number   // Default: 120
    lowResponseMinutes:       number   // Default: 240
  }
  
  // Notification Templates
  notificationTemplates: {
    reportReceived:    string
    reportAssigned:    string
    reportResolved:    string
    sosReceived:       string
  }
  
  // Metadata
  version:            string
  updatedAt:          timestamp
  updatedBy:          string
}

settings/districts
{
  districts: [
    {
      code:           string       // e.g., "OR-KH"
      name:           string       // e.g., "Khurda"
      state:          string
      population:     number
      riskLevel:      string       // LOW | MEDIUM | HIGH | VERY_HIGH
      coordinates: {
        latitude:     number
        longitude:    number
      }
      defaultAuthority: string    // User UID of default district officer
    }
  ]
  updatedAt:          timestamp
}
```

---

## 7.10 Collection: `auditLogs`

**Document ID:** Auto-generated

```
auditLogs/{auditId}
{
  auditId:           string
  
  // Actor
  userId:            string
  userName:          string
  userRole:          string
  
  // Action
  action:            string       // e.g., "INCIDENT_STATUS_CHANGED", "USER_ROLE_UPDATED"
  resource:          string       // e.g., "incidents", "users"
  resourceId:        string
  
  // Change
  previousValue:     object?      // Snapshot before change
  newValue:          object?      // Snapshot after change
  
  // Context
  ipAddress:         string
  userAgent:         string
  requestId:         string
  
  // Outcome
  success:           boolean
  errorMessage:      string?
  
  // Timestamp
  timestamp:         timestamp    // Indexed for time-range queries
}
```

---

## 7.11 Collection Relationships

```
users (1) ──────────── (many) incidents [reportedBy]
users (1) ──────────── (many) incidents [assignedTo.authorityId]
users (1) ──────────── (many) notifications [recipientId]
users (1) ──────────── (many) feedback [submittedBy]
users (1) ──────────── (many) reports [generatedBy]
users (1) ──────────── (many) auditLogs [userId]

incidents (1) ──────── (many) notifications [relatedIncidentId]
incidents (1) ──────── (many) resources [currentAssignment.incidentId]
incidents (1) ──────── (many) feedback [targetId]
incidents (many) ───── (many) incidents [linkedIncidents]

resources (1) ──────── (many) notifications [relatedResourceId]
```

---

## 7.12 Firestore Index Strategy

```
// Composite indexes required

// Incidents by district + status + severity
incidents: district (ASC), status (ASC), aiAnalysis.severityScore (DESC)

// Incidents by type + date
incidents: incidentType (ASC), createdAt (DESC)

// Incidents by location + status
incidents: location.district (ASC), status (ASC), createdAt (DESC)

// Resources by district + type + status
resources: district (ASC), type (ASC), status (ASC)

// Notifications by recipient + read status
notifications: recipientId (ASC), isRead (ASC), createdAt (DESC)

// Analytics by scope + period + date
analytics: scope (ASC), period (ASC), date (DESC)

// Audit logs by user + timestamp
auditLogs: userId (ASC), timestamp (DESC)

// Audit logs by resource type + timestamp
auditLogs: resource (ASC), timestamp (DESC)
```

---

*Next: [ER Diagram →](./08-er-diagram.md)*
