# Section 08 – Entity Relationship Diagram

---

## 8.1 ER Diagram (Text Format)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ResQAI – Entity Relationship Diagram                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────┐
│        USER         │
├─────────────────────┤
│ PK  uid             │
│     email           │
│     phoneNumber     │
│     displayName     │
│     role            │
│     district        │
│     state           │
│     isVerified      │
│     isActive        │
│     fcmTokens[]     │
│     createdAt       │
│     updatedAt       │
└──────────┬──────────┘
           │
     ┌─────┴──────────────────────────────────────────────────┐
     │                           │                            │
  REPORTS                   ASSIGNS                      RECEIVES
  (1 : N)                   (1 : N)                      (1 : N)
     │                           │                            │
     ▼                           ▼                            ▼
┌─────────────────────┐   ┌─────────────────────┐   ┌──────────────────────┐
│      INCIDENT       │   │      INCIDENT       │   │    NOTIFICATION      │
│  (as reporter)      │   │  (as authority)     │   ├──────────────────────┤
└─────────────────────┘   └─────────────────────┘   │ PK  notificationId   │
                                                     │     recipientId (FK) │
                                                     │     title            │
                                                     │     body             │
                                                     │     type             │
                                                     │     isRead           │
                                                     │     channels         │
                                                     │     createdAt        │
                                                     └──────────────────────┘


┌──────────────────────────────────────────────────────────────────────────┐
│                            INCIDENT                                       │
├──────────────────────────────────────────────────────────────────────────┤
│ PK  incidentId                                                            │
│ FK  reportedBy         → USER.uid                                         │
│ FK  assignedTo.authorityId → USER.uid                                     │
│ FK  eventId            → DISASTER_EVENT.eventId                           │
│     title                                                                 │
│     description                                                           │
│     incidentType       (FLOOD|CYCLONE|EARTHQUAKE|LANDSLIDE|FIRE|...)      │
│     status             (SUBMITTED|TRIAGED|ASSIGNED|IN_PROGRESS|RESOLVED)  │
│     urgencyLevel       (LOW|MEDIUM|HIGH|CRITICAL)                         │
│     affectedPeople                                                        │
│     fatalities                                                            │
│     injuries                                                              │
│     location.address                                                      │
│     location.district                                                     │
│     location.state                                                        │
│     location.coordinates.latitude                                         │
│     location.coordinates.longitude                                        │
│     location.geohash                                                      │
│     mediaFiles[]                                                          │
│     linkedIncidents[]  → INCIDENT.incidentId (self-referencing, M:M)      │
│     source             (WEB|MOBILE|SMS|API)                               │
│     createdAt                                                             │
│     updatedAt                                                             │
├──────────────────────────────────────────────────────────────────────────┤
│  Embedded Sub-entity: AI_ANALYSIS                                         │
│  ├── analysisId                                                           │
│  ├── classifiedType                                                       │
│  ├── classificationConfidence                                             │
│  ├── severityScore       (1-10)                                           │
│  ├── severityBand        (LOW|MEDIUM|HIGH|CRITICAL)                       │
│  ├── priorityRank                                                         │
│  ├── resourceRecommendations[]                                            │
│  ├── situationSummary                                                     │
│  ├── reasoning[]                                                          │
│  ├── isDuplicate                                                          │
│  ├── duplicateOf        → INCIDENT.incidentId                             │
│  └── authorityFeedback                                                    │
│                                                                           │
│  Embedded Sub-entity: ASSIGNMENT                                          │
│  ├── authorityId        → USER.uid                                        │
│  ├── assignedAt                                                           │
│  └── resources[]        → RESOURCE.resourceId (M:M via embed)            │
│                                                                           │
│  Embedded Sub-entity: ESCALATION                                          │
│  ├── isEscalated                                                          │
│  ├── escalatedAt                                                          │
│  ├── escalatedBy        → USER.uid                                        │
│  └── escalatedTo                                                          │
└──────────────────────────────────────────────────────────────────────────┘
           │                             │                          │
     HAS MANY                       TRIGGERS                  LINKED TO
    (1 : N)                          (1 : N)                  (M : M)
           │                             │                          │
           ▼                             ▼                          ▼
┌────────────────────┐     ┌──────────────────────┐     ┌─────────────────┐
│  INCIDENT_COMMENT  │     │    NOTIFICATION       │     │   INCIDENT      │
├────────────────────┤     └──────────────────────┘     │  (self-ref)     │
│ PK  commentId      │                                   └─────────────────┘
│ FK  incidentId     │
│ FK  authorId       │
│     content        │
│     isInternal     │
│     createdAt      │
└────────────────────┘

┌────────────────────┐
│  STATUS_HISTORY    │
├────────────────────┤
│ PK  historyId      │
│ FK  incidentId     │
│     fromStatus     │
│     toStatus       │
│ FK  changedBy      │
│     changedAt      │
│     note           │
└────────────────────┘


┌──────────────────────────────────────────────────────────┐
│                        RESOURCE                           │
├──────────────────────────────────────────────────────────┤
│ PK  resourceId                                            │
│ FK  organizationId       → ORGANIZATION.orgId             │
│     name                                                  │
│     type   (RESCUE_TEAM|AMBULANCE|FIRE_TRUCK|HELICOPTER..)│
│     district                                              │
│     state                                                 │
│     contactName                                           │
│     contactPhone                                          │
│     status  (AVAILABLE|DEPLOYED|MAINTENANCE|UNAVAILABLE)  │
│     capacity.total                                        │
│     capacity.current                                      │
│     baseLocation.coordinates                             │
│     currentLocation.coordinates                          │
│     capabilities[]                                        │
│     isActive                                              │
│     registeredAt                                          │
├──────────────────────────────────────────────────────────┤
│  Embedded: currentAssignment                              │
│  ├── incidentId          → INCIDENT.incidentId            │
│  └── assignedAt                                          │
└──────────────────────────────────────────────────────────┘
           │
     HAS MANY
    (1 : N)
           │
           ▼
┌──────────────────────┐
│  DEPLOYMENT_HISTORY  │
├──────────────────────┤
│ PK  deploymentId     │
│ FK  resourceId       │
│ FK  incidentId       │
│ FK  deployedBy       │
│     deployedAt       │
│     returnedAt       │
│     notes            │
└──────────────────────┘


┌──────────────────────────────────────────┐
│               ORGANIZATION               │
├──────────────────────────────────────────┤
│ PK  orgId                                │
│     name                                 │
│     type   (NDRF|SDRF|NGO|POLICE|FIRE..) │
│     district                             │
│     state                                │
│     contactEmail                         │
│     contactPhone                         │
│     isVerified                           │
│     createdAt                            │
└──────────────┬───────────────────────────┘
               │
         HAS MANY (1:N)
               │
        ┌──────┴──────┐
        ▼             ▼
    RESOURCE        USER


┌──────────────────────────────────────────┐
│             DISASTER_EVENT               │
├──────────────────────────────────────────┤
│ PK  eventId                              │
│     name                                 │
│     type                                 │
│     state                                │
│     districts[]                          │
│     startDate                            │
│     endDate                              │
│     severity                             │
│     isActive                             │
│     totalIncidents                       │
│     createdAt                            │
└──────────────┬───────────────────────────┘
               │
         HAS MANY (1:N)
               │
               ▼
           INCIDENT


┌──────────────────────────────────────────┐
│               ANALYTICS                  │
├──────────────────────────────────────────┤
│ PK  analyticsId                          │
│     period   (HOURLY|DAILY|WEEKLY)       │
│     date                                 │
│     scope    (NATIONAL|STATE|DISTRICT)   │
│     district                             │
│     state                                │
│     incidents.total                      │
│     incidents.byType                     │
│     incidents.bySeverity                 │
│     response.avgResponseTimeMinutes      │
│     resources.utilizationRate            │
│     ai.recommendationsAccepted           │
│     computedAt                           │
└──────────────────────────────────────────┘


┌──────────────────────────────────────────┐
│                 REPORT                   │
├──────────────────────────────────────────┤
│ PK  reportId                             │
│ FK  generatedBy         → USER.uid       │
│     title                                │
│     type                                 │
│     summary                              │
│     pdfUrl                               │
│     fromDate                             │
│     toDate                               │
│     status                               │
│     createdAt                            │
└──────────────────────────────────────────┘


┌──────────────────────────────────────────┐
│                FEEDBACK                  │
├──────────────────────────────────────────┤
│ PK  feedbackId                           │
│ FK  submittedBy         → USER.uid       │
│ FK  targetId            → INCIDENT.incidentId │
│     targetType                           │
│     rating              (1-5)            │
│     sentiment                            │
│     aiAccuracyRating                     │
│     comment                              │
│     createdAt                            │
└──────────────────────────────────────────┘


┌──────────────────────────────────────────┐
│               AUDIT_LOG                  │
├──────────────────────────────────────────┤
│ PK  auditId                              │
│ FK  userId              → USER.uid       │
│     action                               │
│     resource                             │
│     resourceId                           │
│     previousValue                        │
│     newValue                             │
│     ipAddress                            │
│     success                              │
│     timestamp                            │
└──────────────────────────────────────────┘
```

---

## 8.2 Relationship Summary Table

| Entity A | Relationship | Entity B | Cardinality | Key |
|----------|-------------|----------|-------------|-----|
| USER | reports | INCIDENT | 1 : N | incidents.reportedBy → users.uid |
| USER | manages | INCIDENT | 1 : N | incidents.assignedTo.authorityId → users.uid |
| USER | belongs to | ORGANIZATION | N : 1 | users.organizationId → organizations.orgId |
| USER | receives | NOTIFICATION | 1 : N | notifications.recipientId → users.uid |
| USER | writes | AUDIT_LOG | 1 : N | auditLogs.userId → users.uid |
| USER | submits | FEEDBACK | 1 : N | feedback.submittedBy → users.uid |
| USER | generates | REPORT | 1 : N | reports.generatedBy → users.uid |
| INCIDENT | has | AI_ANALYSIS | 1 : 1 | embedded in incident document |
| INCIDENT | has | COMMENTS | 1 : N | subcollection |
| INCIDENT | has | STATUS_HISTORY | 1 : N | subcollection |
| INCIDENT | assigned | RESOURCE | M : N | embedded array in incident + ref in resource |
| INCIDENT | linked to | INCIDENT | M : N | incidents.linkedIncidents[] self-reference |
| INCIDENT | belongs to | DISASTER_EVENT | N : 1 | incidents.eventId → disasterEvents.eventId |
| INCIDENT | triggers | NOTIFICATION | 1 : N | notifications.relatedIncidentId |
| INCIDENT | has | FEEDBACK | 1 : N | feedback.targetId → incidents.incidentId |
| RESOURCE | belongs to | ORGANIZATION | N : 1 | resources.organizationId |
| RESOURCE | has | DEPLOYMENT_HISTORY | 1 : N | subcollection |
| ORGANIZATION | owns | RESOURCE | 1 : N | resources.organizationId |
| ORGANIZATION | employs | USER | 1 : N | users.organizationId |
| DISASTER_EVENT | contains | INCIDENT | 1 : N | incidents.eventId |

---

## 8.3 Embedded vs. Referenced Design Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| AI analysis in incident | **Embedded** | Always read together; no separate queries needed |
| Assignment in incident | **Embedded** | Frequently needed with incident data |
| Comments on incident | **Subcollection** | Variable length; not always needed |
| Status history | **Subcollection** | Audit trail; not needed in list view |
| Resource deployment history | **Subcollection** | Historical; not needed in real-time ops |
| Organization data in user | **Partial embed** (name only) | Avoid join for display; full org via reference |
| Notification channels | **Embedded** | Always needed; small size |

---

*Next: [REST API Design →](./09-api-design.md)*
