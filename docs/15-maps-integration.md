# Section 15 – Google Maps Integration

---

## 15.1 Maps Architecture

```
Frontend (React)                     Google Maps Platform
     │                                       │
     │  @vis.gl/react-google-maps            │
     ├── <APIProvider> (API key)             │
     │        │                              │
     │   ┌────▼──────────────────────┐       │
     │   │  <Map> component          │──────►│ Maps JavaScript API
     │   │    ├── <IncidentMarkers>  │       │
     │   │    ├── <ResourceMarkers>  │       │
     │   │    ├── <HeatmapLayer>     │       │
     │   │    ├── <InfraLayer>       │       │
     │   │    └── <RouteOverlay>     │       │
     │   └───────────────────────────┘       │
     │                                       │
Backend (Node.js)                            │
     ├── Geocoding API ────────────────────► │ Geocoding API
     ├── Distance Matrix ──────────────────► │ Distance Matrix API
     ├── Directions API ────────────────────►│ Directions API
     └── Places API ────────────────────────►│ Places API
```

---

## 15.2 Maps APIs Used

| API | Purpose | Where Used |
|-----|---------|-----------|
| **Maps JavaScript API** | Interactive web map rendering | All map views in frontend |
| **Geocoding API** | Convert address → coordinates | Incident form, resource registry |
| **Reverse Geocoding** | Convert coordinates → address | Auto-fill location after GPS capture |
| **Places API** | Address autocomplete | Incident form location field |
| **Distance Matrix API** | Calculate distance/time between resource and incident | Resource recommendation sorting |
| **Directions API** | Route from resource to incident | Route overlay on map |
| **Maps Static API** | Static map thumbnail | Notifications, PDF reports |

---

## 15.3 Incident Markers

### Marker Design

```
SEVERITY BANDS → Marker Colors:

🔴 CRITICAL (score 9-10)  →  Large pulsing red pin
🟠 HIGH     (score 7-8)   →  Medium orange pin
🟡 MEDIUM   (score 4-6)   →  Medium yellow pin
🟢 LOW      (score 1-3)   →  Small green pin

Marker Structure:
  - Custom SVG pin with incident type icon inside
  - Severity color determines fill
  - Pulsing animation for CRITICAL incidents
  - Cluster at zoom-out (MarkerClusterer)
```

### Marker Data Binding

```typescript
// Each marker binds to incident data
interface IncidentMarker {
  incidentId: string
  position: { lat: number; lng: number }
  severityBand: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW'
  incidentType: IncidentType
  status: IncidentStatus
  title: string
  affectedPeople: number
}

// Click handler opens InfoWindow then side panel
onMarkerClick(incidentId) → fetchIncidentSummary() → showSidePanel()
```

### Incident Marker Clustering

- At zoom level < 10: cluster nearby markers
- Cluster bubble shows count + dominant severity color
- Click cluster → zoom to cluster bounds
- At zoom level ≥ 10: individual markers visible

---

## 15.4 Resource Markers

### Resource Marker Types

```
🚤  RESCUE_BOAT      — Blue anchor icon
🚑  AMBULANCE        — Green cross icon  
🚒  FIRE_TRUCK       — Red flame icon
🚁  HELICOPTER       — Blue helicopter icon
👥  RESCUE_TEAM      — Orange people icon
🏥  HOSPITAL         — Red H icon
🏠  SHELTER          — Blue house icon
👮  POLICE_UNIT      — Blue badge icon
🤝  NGO_UNIT         — Green hands icon
```

### Resource Status Colors

```
🟢 AVAILABLE     — Solid color, full opacity
🔵 DEPLOYED      — Moving animation (en route) or solid (on scene)
🟡 MAINTENANCE   — Gray tint, reduced opacity
⚫ UNAVAILABLE   — Gray, not interactive
```

### Resource Live Tracking

- Field units update GPS every 60 seconds via `PUT /resources/:id/location`
- Frontend polls resource locations every 30 seconds (or uses Firestore listener)
- Moving resources show animated route line from last to current position
- "En Route" resources show direction arrow

---

## 15.5 Heatmap Layer

### Heatmap Configuration

```typescript
const heatmapConfig = {
  data: incidents.map(i => ({
    location: new google.maps.LatLng(i.location.coordinates.lat, i.location.coordinates.lng),
    weight: i.aiAnalysis.severityScore / 10  // 0.0 to 1.0
  })),
  options: {
    radius: 30,           // pixels
    opacity: 0.6,
    gradient: [
      'rgba(0, 255, 0, 0)',    // transparent (low density)
      'rgba(0, 255, 0, 1)',    // green
      'rgba(255, 255, 0, 1)',  // yellow
      'rgba(255, 165, 0, 1)',  // orange
      'rgba(255, 0, 0, 1)'    // red (high density)
    ]
  }
}
```

### Heatmap Toggles
- Default: OFF (performance optimization)
- Toggle via map controls bar
- Recalculated when district filter changes
- Heatmap based on severity-weighted incident density

---

## 15.6 Infrastructure Layers

### Toggleable Overlays

**Hospitals Layer**
- Data source: Google Places API (type: hospital) + curated DB
- Marker: Red cross icon
- Click → show: name, address, phone, beds available, emergency: YES/NO
- Color: Green (emergency available) / Yellow (partial) / Red (full)

**Shelters / Relief Camps Layer**
- Data source: Firestore `resources` collection (type: SHELTER)
- Marker: Blue house icon
- Click → show: name, capacity (current/total), contact, distance
- Capacity color: Green <50%, Yellow 50-80%, Red >80%

**Police Stations Layer**
- Data source: Google Places API (type: police) + official data
- Marker: Blue badge icon
- Click → show: station name, phone number, jurisdiction

**Fire Stations Layer**
- Data source: Google Places API + official data
- Marker: Red flame icon
- Click → show: station name, active units, phone

### Layer Toggle Controls

```
Map Layer Controls (top-right panel):
[ ☑ Incidents ]   [ ☑ Resources ]
[ ☐ Heatmap   ]   [ ☐ Hospitals ]
[ ☐ Shelters  ]   [ ☐ Police    ]
[ ☐ Fire Stn  ]   [ ☐ Routes    ]
```

---

## 15.7 Route Overlay

### Route Display (Resource to Incident)

```typescript
// When a resource is assigned or "en route"
const routeRequest = {
  origin: resource.currentLocation.coordinates,
  destination: incident.location.coordinates,
  travelMode: google.maps.TravelMode.DRIVING,
  drivingOptions: {
    departureTime: new Date(),
    trafficModel: google.maps.TrafficModel.BEST_GUESS
  }
}

// Display on map
directionsRenderer.setDirections(routeResult)
// Show: route polyline, ETA, distance in side panel
```

### Route Information Display

- Dashed polyline from resource to incident
- Color: Matches resource type color
- Side panel shows: Distance, ETA, Turn-by-turn (collapsible)
- Updates when resource location updates

---

## 15.8 Map Controls and UX

### Map Controls Layout

```
┌──────────────────────────────────────────────────────────────┐
│  [Search location...              🔍]  [Layers ▼] [Filter ▼] │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│                    MAP AREA                          [+]     │
│                                                      [-]     │
│                                               [⊙ My Location]│
│                                               [□ Fullscreen] │
│                                               [↻ Reset View] │
└──────────────────────────────────────────────────────────────┘
```

### Auto-Center Logic

1. On dashboard load → center on jurisdiction (district/state bounds)
2. New CRITICAL incident → animate pan to incident location
3. Filter by district → fit bounds to filtered markers
4. Manual search → geocode and center

### Incident Click → Side Panel

```
[Map Marker clicked]
        │
        ▼
[Map Side Panel slides in from right]
┌────────────────────────────────┐
│  🔴 INC-2024-00000001          │
│  Flood — Khandagiri, Khurda    │
│                                │
│  Severity: 9/10  CRITICAL      │
│  Affected: 800 people          │
│  Status: Assigned              │
│                                │
│  AI Summary:                   │
│  "Critical flood in Khandagiri │
│  area. ODRAF en route."        │
│                                │
│  [View Full Details →]         │
│  [Assign Resource]             │
└────────────────────────────────┘
```

---

## 15.9 Incident Form Location Picker

### Location Capture Workflow

```
[Incident Report Form — Step 2: Location]
        │
        ├─ Auto-GPS Option:
        │   navigator.geolocation.getCurrentPosition()
        │   → coordinates captured
        │   → reverse geocode via Geocoding API
        │   → auto-fill: address, district, state, pincode
        │
        ├─ Manual Search:
        │   [Search address...] — Google Places Autocomplete
        │   → user selects from dropdown
        │   → geocode to coordinates
        │   → show on map
        │
        └─ Map Click:
            User taps directly on map
            → reverse geocode to get address
            → confirm location
```

---

## 15.10 Performance Optimization

| Technique | Implementation |
|-----------|----------------|
| **Marker Clustering** | MarkerClusterer library at zoom < 10 |
| **Viewport-based Loading** | Only load markers visible in current map bounds |
| **Debounced Updates** | Map center changes debounced 500ms before re-query |
| **Lazy Heatmap** | Heatmap computed only when toggled on |
| **Cached Infrastructure** | Hospital/police/fire data cached for 1 hour |
| **Reduced API Calls** | Distance Matrix batched (max 25 origins × 25 destinations) |
| **Maps API Loading** | Loaded with `loading="async"` to not block page render |
| **Resource Tracking** | Throttled to 1 update/60s per resource (battery/cost) |

---

*Next: [Security Architecture →](./16-security-architecture.md)*
