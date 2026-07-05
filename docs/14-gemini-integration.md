# Section 14 – Google Gemini AI Integration

---

## 14.1 Integration Architecture

```
                    ┌────────────────────────────────┐
                    │     ResQAI Backend (Cloud Run)  │
                    │                                 │
                    │  ┌───────────────────────────┐  │
                    │  │    AI Processing Service  │  │
                    │  │                           │  │
  Cloud Tasks ─────►│  │  1. Build prompt          │  │
  (incident job)    │  │  2. Call Gemini API        │  │
                    │  │  3. Parse response         │  │
                    │  │  4. Validate schema        │  │
                    │  │  5. Write to Firestore     │  │
                    │  └──────────────┬────────────┘  │
                    └─────────────────┼───────────────┘
                                      │ HTTPS
                                      ▼
                    ┌─────────────────────────────────┐
                    │   Google Gemini 1.5 Pro API      │
                    │   generativelanguage.googleapis  │
                    └─────────────────────────────────┘
```

**Model Selection:**

| Task | Model | Reason |
|------|-------|--------|
| Full incident analysis (new reports) | `gemini-1.5-pro` | Best accuracy, multi-step reasoning |
| Quick re-classification (updates) | `gemini-1.5-flash` | Faster + cheaper for incremental updates |
| Image analysis (media files) | `gemini-1.5-pro` (multimodal) | Vision capability |
| Situation report generation | `gemini-1.5-pro` | Long-form output quality |

---

## 14.2 Primary Incident Analysis Prompt

### Prompt Template

```
SYSTEM INSTRUCTION:
You are ResQAI, an AI-powered disaster response analysis system.
Your role is to analyze emergency incident reports submitted by citizens
during natural disasters and provide structured, actionable intelligence
to disaster management authorities.

Always respond in valid JSON matching the exact schema provided.
Be conservative with severity ratings — when uncertain, rate higher.
Prioritize human life above all other factors.

---

USER PROMPT (dynamically constructed):

Analyze the following emergency incident report and provide a complete 
structured assessment.

=== INCIDENT DATA ===
Incident ID: {incidentId}
Report Type: {incidentType}
Description: {description}
People Affected: {affectedPeople}
Location: {district}, {state}, India
GPS Coordinates: {latitude}, {longitude}
Reported At: {reportedAt}
User Urgency: {urgencyLevel}

=== CONTEXT DATA ===
Population Density (district): {populationDensity} per sq km
Current Weather: {weatherCondition}, {temperature}°C, {rainfall}mm
Active Disasters in District: {activeDisasterCount}
Historical Vulnerability Score: {vulnerabilityScore}/10

=== TASK ===
Provide your assessment in the following JSON format:

{
  "classification": {
    "incidentType": "<one of: FLOOD|CYCLONE|EARTHQUAKE|LANDSLIDE|FIRE|MEDICAL|INDUSTRIAL|DROUGHT|CIVIL_UNREST|OTHER>",
    "subType": "<more specific classification>",
    "confidence": <0.0 to 1.0>
  },
  "severity": {
    "score": <1 to 10>,
    "band": "<LOW|MEDIUM|HIGH|CRITICAL>",
    "justification": "<one sentence>"
  },
  "priority": {
    "score": <0.0 to 1.0>,
    "reasoning": "<one sentence about why this priority was assigned>"
  },
  "resourceRecommendations": [
    {
      "resourceType": "<RESCUE_BOAT|AMBULANCE|FIRE_TRUCK|HELICOPTER|RESCUE_TEAM|MEDICAL_UNIT|POLICE_UNIT>",
      "quantity": <number>,
      "urgency": "<IMMEDIATE|HIGH|MEDIUM|LOW>",
      "reason": "<why this resource>"
    }
  ],
  "situationSummary": "<2-3 sentence natural language summary of the emergency>",
  "reasoning": [
    "<reason 1 for severity rating>",
    "<reason 2>",
    "<reason 3>",
    "<reason 4 (if applicable)>",
    "<reason 5 (if applicable)>"
  ],
  "immediateActions": [
    "<action 1 that authorities should take immediately>",
    "<action 2>",
    "<action 3>"
  ],
  "risks": [
    "<identified risk 1>",
    "<identified risk 2>"
  ],
  "duplicateLikelihood": <0.0 to 1.0>,
  "dataQuality": "<HIGH|MEDIUM|LOW>",
  "dataQualityNote": "<any concerns about data completeness or reliability>"
}
```

---

## 14.3 Prompt Flow Diagram

```
INCIDENT SUBMITTED
        │
        ▼
STEP 1: DATA ENRICHMENT
  ├── Fetch weather data (OpenWeatherMap / IMD API)
  ├── Lookup district vulnerability index (Firestore settings)
  ├── Count active incidents in district (Firestore query)
  ├── Get population density (static district data)
  └── If media attached: prepare image URLs for vision model
        │
        ▼
STEP 2: PROMPT CONSTRUCTION
  ├── Inject all enriched data into prompt template
  ├── Select model: gemini-1.5-pro (full) or flash (quick)
  └── Set parameters:
        temperature: 0.1 (low — deterministic for safety applications)
        maxOutputTokens: 2048
        topP: 0.9
        candidateCount: 1
        responseMimeType: "application/json"
        │
        ▼
STEP 3: API CALL
  ├── POST to Gemini API with prompt
  ├── Timeout: 30 seconds
  ├── Retry: 3 attempts with exponential backoff
  └── Circuit breaker: opens after 5 consecutive failures
        │
        ▼
STEP 4: RESPONSE PARSING
  ├── Parse JSON response
  ├── Validate against Zod schema
  ├── Range-check: severityScore in [1,10], confidence in [0,1]
  ├── If invalid: retry with schema-correction prompt
  └── If still invalid: activate rule-based fallback
        │
        ▼
STEP 5: POST-PROCESSING
  ├── Apply business rules override (e.g., force CRITICAL if fatalities > 0)
  ├── Calculate combined priority score
  │    priorityScore = (severityScore * 0.5) + (timeFactor * 0.2) 
  │                  + (populationFactor * 0.2) + (resourceProximity * 0.1)
  ├── Run duplicate detection query
  └── Write complete AI analysis to Firestore
```

---

## 14.4 Severity Analysis Design

### Severity Score Components

| Factor | Weight | Source |
|--------|--------|--------|
| Incident type severity baseline | 20% | Static lookup table |
| Affected population | 25% | User input |
| Description sentiment & keywords | 25% | Gemini NLU |
| Location vulnerability | 15% | Historical data |
| Weather conditions | 10% | Weather API |
| Time-of-day factor | 5% | System clock |

### Severity Bands

| Score | Band | Color | SLA Response Time |
|-------|------|-------|-------------------|
| 1–3 | LOW | 🟢 Green | 240 minutes |
| 4–6 | MEDIUM | 🟡 Yellow | 120 minutes |
| 7–8 | HIGH | 🟠 Orange | 60 minutes |
| 9–10 | CRITICAL | 🔴 Red | 30 minutes |

### Severity Escalation Rules (Post-AI Business Logic)

```
IF fatalities > 0 THEN severityScore = MAX(severityScore, 8)
IF affectedPeople > 10000 THEN severityScore = MAX(severityScore, 8)
IF incidentType == EARTHQUAKE AND affectedPeople > 0 THEN severityScore = MAX(severityScore, 7)
IF description.contains("children") AND description.contains("trapped") THEN severityScore += 1
IF weatherCondition == "CYCLONE_WARNING" THEN severityScore += 1
severityScore = MIN(severityScore, 10)  // Cap at 10
```

---

## 14.5 Priority Detection System

### Priority Queue Algorithm

```
PRIORITY SCORE = 
  (normalizedSeverity    × 0.40) +   // 0-1, from severity score/10
  (timeDecayFactor       × 0.25) +   // Increases as time without response grows
  (populationFactor      × 0.20) +   // log(affectedPeople) / log(10000)
  (resourceProximity     × 0.10) +   // 1 - (nearestResource_km / 100)
  (vulnerabilityFactor   × 0.05)     // District vulnerability index / 10

TIME DECAY FACTOR:
  minutesWaiting = now - reportedAt (in minutes)
  timeDecayFactor = MIN(1.0, minutesWaiting / 120)
  // Incident at 120+ minutes without response gets max time priority
```

### Priority Queue Rules
- Queue is re-ranked every 60 seconds (Cloud Scheduler)
- New CRITICAL incidents inserted at top immediately (bypass queue rank)
- SOS incidents always rank #1 regardless of score
- Resolved/Closed incidents removed from queue

---

## 14.6 Resource Recommendation Engine

### Recommendation Logic

The AI model recommends resources based on:

1. **Incident Type → Resource Type Mapping** (AI-inferred)
   - FLOOD → Rescue Boats, Medical Units, Helicopters
   - FIRE → Fire Trucks, Medical Units, Police
   - EARTHQUAKE → Rescue Teams, Medical Units, Helicopters, Cranes
   - MEDICAL → Ambulances, Medical Units
   - CYCLONE → Shelter Staff, Rescue Teams, Medical Units

2. **Quantity Calculation**
   - AI uses affected population to recommend quantity
   - Rule: 1 rescue boat per 100 people in flood
   - Rule: 1 ambulance per 50 injured persons estimated
   - AI adjusts based on incident severity band

3. **Urgency Assignment**
   - IMMEDIATE: Resource needed within 15 minutes
   - HIGH: Needed within 30 minutes
   - MEDIUM: Within 1 hour
   - LOW: Within 2 hours

### Resource Matching (Backend Business Logic)

After AI recommendation, backend queries Firestore for actual available resources:

```
FOR EACH recommended resource type:
  1. Query: resources WHERE type = :type AND status = AVAILABLE AND district = :district
  2. Sort by: distance to incident (using Distance Matrix API)
  3. Return top N matches (N = AI recommended quantity)
  4. If insufficient in district: query neighboring districts
```

---

## 14.7 Situation Summary Generation

### Summary Prompt

```
Based on this incident analysis:
- Type: {classifiedType}
- Severity: {severityScore}/10
- Affected: {affectedPeople} people
- Location: {district}
- Status: {status}
- Assigned Resources: {assignedResources}

Generate a 2-3 sentence situation summary suitable for a government 
situation report. Use professional language. Include: what happened, 
scale of impact, and current response status.
```

### Summary Refresh Triggers
- New incident submitted: Initial summary generated
- Status changes to IN_PROGRESS: Summary updated with response status
- Resources assigned: Summary updated with deployment info
- Incident resolved: Final summary generated for report

---

## 14.8 Situation Report Generation

### Report Prompt

```
SYSTEM: You are a professional disaster management report writer.

Generate a formal situation report for the following data:

Period: {fromDate} to {toDate}
Jurisdiction: {district}, {state}

Incident Statistics:
{incidentStats JSON}

Response Metrics:
{responseMetrics JSON}

Resource Utilization:
{resourceMetrics JSON}

Top 5 Critical Incidents:
{topIncidents JSON}

Write a professional situation report with:
1. Executive Summary (2 paragraphs)
2. Incident Overview (statistics narrative)
3. Response Operations (what was done)
4. Resource Utilization (efficiency narrative)
5. Key Challenges
6. Recommendations for Next 24 Hours
7. Conclusion

Format: Professional government report style.
Tone: Factual, measured, authoritative.
```

---

## 14.9 Explainable AI Design

ResQAI's explainability is central to authority trust. Every AI output includes:

### Authority View of AI Explanation

```
┌──────────────────────────────────────────────────────────┐
│  🤖 AI Assessment – Gemini 1.5 Pro                       │
│  Analyzed at: 10:32:15 AM  |  Confidence: 97%            │
├──────────────────────────────────────────────────────────┤
│  Severity Score:  9/10  ████████████░  CRITICAL          │
│                                                          │
│  Why this rating:                                        │
│  • 800 people affected — significantly above average     │
│  • Flood type with rapidly rising water level            │
│  • Vulnerable groups identified (children, elderly)      │
│  • Critical infrastructure loss (electricity)            │
│  • Location at high flood-risk zone (historical data)    │
│                                                          │
│  Confidence in classification: 97% (FLOOD)              │
│  Data quality: HIGH                                      │
│                                                          │
│  Immediate Actions Recommended:                          │
│  1. Deploy rescue boats to Khandagiri area immediately   │
│  2. Establish medical triage at DRM ground               │
│  3. Issue district-wide flood alert broadcast            │
│                                                          │
│  [✅ Accept Recommendation]  [✏️ Override with Reason]   │
│                                                          │
│  Was this assessment accurate?  [👍 Yes]  [👎 No]       │
└──────────────────────────────────────────────────────────┘
```

### Feedback Loop

Authority feedback (accept/override) is:
1. Stored in Firestore (feedback collection)
2. Aggregated into AI accuracy metrics (analytics)
3. Used to tune prompt parameters over time
4. Reviewed by admin to identify systematic AI errors

---

## 14.10 Duplicate Detection Algorithm

```
NEW INCIDENT SUBMITTED at (lat, lng)

STEP 1: Geohash Query
  Compute geohash prefix (precision 6 = ~1.2 km radius)
  Query Firestore: incidents WHERE geohash STARTS WITH {prefix}
                               AND createdAt > (now - 2 hours)
                               AND status NOT IN [CLOSED, ARCHIVED]

STEP 2: Gemini Similarity Check
  For each candidate:
  Prompt: "Are these two incident descriptions describing the same event?
  Report 1: {description1}
  Report 2: {description2}
  Answer: YES/NO with confidence score 0.0-1.0"

STEP 3: Scoring
  duplicateScore = (geohashProximity × 0.4) + (descriptionSimilarity × 0.6)

STEP 4: Decision
  IF duplicateScore > 0.85 → Flag as duplicate, link to original
  IF duplicateScore > 0.65 → Flag as possible duplicate, needs human review
  IF duplicateScore < 0.65 → Not a duplicate
```

---

*Next: [Google Maps Integration →](./15-maps-integration.md)*
