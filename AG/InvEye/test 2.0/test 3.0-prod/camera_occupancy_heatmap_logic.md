# Camera Occupancy Heatmap - Backend Logic

> **For InvEye CCTV Analytics powered by YOLO Detections**

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CAMERA OCCUPANCY HEATMAP PIPELINE                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌───────────┐ │
│  │   LAYER 1    │    │   LAYER 2    │    │   LAYER 3    │    │  LAYER 4  │ │
│  │  Jetson +    │───▶│  Ingestion   │───▶│  ClickHouse  │───▶│ Query API │ │
│  │    YOLO      │    │     API      │    │   Storage    │    │           │ │
│  └──────────────┘    └──────────────┘    └──────────────┘    └─────┬─────┘ │
│        │                                                           │       │
│        │ Detection Events                                          │       │
│        │ {camera_id, zone_id,                                      ▼       │
│        │  person_count, bbox,                              ┌───────────┐   │
│        │  timestamp}                                       │  LAYER 5  │   │
│                                                            │  Frontend │   │
│                                                            │ Dashboard │   │
│                                                            └───────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Layer 1: Edge Device (Jetson + YOLO)

### Detection Event Payload

The Jetson runs YOLO inference and sends detection summaries to the backend:

```python
# jetson/detection_sender.py
import requests
import json
from datetime import datetime

class DetectionEventSender:
    def __init__(self, api_endpoint, api_key, site_id):
        self.endpoint = api_endpoint  # https://api.inveye.io/v1/detections
        self.api_key = api_key
        self.site_id = site_id
        self.buffer = []
        self.buffer_size = 10  # Send every 10 detections or 5 seconds
    
    def send_detection(self, camera_id: str, zone_id: str, detections: list):
        """
        Called after each YOLO inference frame.
        
        Args:
            camera_id: e.g., "CAM_001"
            zone_id: e.g., "EMPLOYEE_AREA", "CAFETERIA"
            detections: List of detected objects with bboxes
        """
        # Count persons in frame
        persons = [d for d in detections if d['class'] == 'person']
        
        event = {
            "camera_id": camera_id,
            "zone_id": zone_id,
            "timestamp": datetime.utcnow().isoformat(),
            "person_count": len(persons),
            "detections": [
                {
                    "class": d['class'],
                    "confidence": d['confidence'],
                    "bbox": d['bbox']  # [x1, y1, x2, y2] normalized 0-1
                }
                for d in persons[:20]  # Cap at 20 per frame
            ]
        }
        
        self.buffer.append(event)
        
        if len(self.buffer) >= self.buffer_size:
            self.flush()
    
    def flush(self):
        if not self.buffer:
            return
        
        payload = {
            "site_id": self.site_id,
            "events": self.buffer
        }
        
        try:
            requests.post(
                self.endpoint,
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": self.api_key
                },
                json=payload,
                timeout=5
            )
        except Exception as e:
            print(f"Failed to send: {e}")
        
        self.buffer = []
```

### Event Payload Structure

```json
{
  "site_id": "HEAD_OFFICE",
  "events": [
    {
      "camera_id": "CAM_001",
      "zone_id": "EMPLOYEE_AREA",
      "timestamp": "2026-01-05T11:30:45.123Z",
      "person_count": 8,
      "detections": [
        {"class": "person", "confidence": 0.92, "bbox": [0.1, 0.2, 0.3, 0.8]},
        {"class": "person", "confidence": 0.87, "bbox": [0.4, 0.3, 0.6, 0.9]}
      ]
    },
    {
      "camera_id": "CAM_002",
      "zone_id": "RECEPTION_AREA",
      "timestamp": "2026-01-05T11:30:45.456Z",
      "person_count": 6,
      "detections": [...]
    }
  ]
}
```

---

## Layer 2: Ingestion API

```python
# app/api/detections.py
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import List, Optional
from clickhouse_driver import Client
from datetime import datetime

app = FastAPI(title="InvEye Detection Ingestion")
ch = Client(host='clickhouse', database='inveye')

class Detection(BaseModel):
    class_name: str = "person"
    confidence: float
    bbox: List[float]  # [x1, y1, x2, y2]

class DetectionEvent(BaseModel):
    camera_id: str
    zone_id: str
    timestamp: str
    person_count: int
    detections: Optional[List[Detection]] = []

class DetectionBatch(BaseModel):
    site_id: str
    events: List[DetectionEvent]

@app.post("/api/v1/detections", status_code=202)
async def ingest_detections(
    batch: DetectionBatch,
    x_api_key: str = Header(...)
):
    """
    Ingest detection events from edge devices.
    """
    # Validate API key
    if not validate_api_key(x_api_key, batch.site_id):
        raise HTTPException(401, "Invalid API key")
    
    # Transform to ClickHouse rows
    rows = []
    for event in batch.events:
        event_time = datetime.fromisoformat(event.timestamp.replace('Z', '+00:00'))
        
        rows.append({
            'site_id': batch.site_id,
            'camera_id': event.camera_id,
            'zone_id': event.zone_id,
            'person_count': event.person_count,
            'detection_count': len(event.detections),
            'avg_confidence': sum(d.confidence for d in event.detections) / len(event.detections) if event.detections else 0,
            'event_time': event_time,
            'event_date': event_time.date()
        })
    
    # Batch insert to ClickHouse
    ch.execute(
        '''INSERT INTO detection_events 
           (site_id, camera_id, zone_id, person_count, detection_count, 
            avg_confidence, event_time, event_date) VALUES''',
        rows
    )
    
    return {"status": "accepted", "count": len(rows)}
```

---

## Layer 3: ClickHouse Storage & Aggregation

### Schema

```sql
-- Raw detection events (1 row per YOLO inference frame)
CREATE TABLE detection_events (
    site_id LowCardinality(String),
    camera_id LowCardinality(String),
    zone_id LowCardinality(String),
    person_count UInt8,
    detection_count UInt8,
    avg_confidence Float32,
    event_time DateTime64(3),
    event_date Date DEFAULT toDate(event_time)
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_date)
ORDER BY (site_id, zone_id, event_time)
TTL event_date + INTERVAL 90 DAY DELETE;


-- Materialized View: Hourly zone stats (for "Hourly Activity" grid)
CREATE MATERIALIZED VIEW hourly_zone_stats_mv
ENGINE = SummingMergeTree()
ORDER BY (site_id, zone_id, hour)
AS SELECT
    site_id,
    zone_id,
    toStartOfHour(event_time) AS hour,
    count() AS event_count,
    max(person_count) AS peak_count,
    avg(person_count) AS avg_count
FROM detection_events
GROUP BY site_id, zone_id, hour;


-- Materialized View: Daily zone peaks (for "Peak Occupancy" cards)
CREATE MATERIALIZED VIEW daily_zone_peaks_mv
ENGINE = ReplacingMergeTree(updated_at)
ORDER BY (site_id, zone_id, date)
AS SELECT
    site_id,
    zone_id,
    toDate(event_time) AS date,
    max(person_count) AS peak_occupancy,
    count() AS total_events,
    avg(person_count) AS avg_occupancy,
    now() AS updated_at
FROM detection_events
GROUP BY site_id, zone_id, date;
```

### Aggregation Logic Explained

```
YOLO Detection Frame:
  camera_id: CAM_001
  zone_id: EMPLOYEE_AREA
  person_count: 8
  timestamp: 2026-01-05 11:30:45

ClickHouse Processing:
  1. INSERT into detection_events
  2. Materialized Views AUTO-UPDATE:
     
     hourly_zone_stats_mv:
       hour: 2026-01-05 11:00:00
       zone_id: EMPLOYEE_AREA
       peak_count: max(8, existing_peak) = 8
       
     daily_zone_peaks_mv:
       date: 2026-01-05
       zone_id: EMPLOYEE_AREA
       peak_occupancy: 8
       total_events: +1
```

---

## Layer 4: Query API

```python
# app/api/heatmap.py
from fastapi import FastAPI, Query
from clickhouse_driver import Client
from datetime import datetime, date

app = FastAPI()
ch = Client(host='clickhouse', database='inveye')

@app.get("/api/v1/zones/{site_id}/stats")
async def get_zone_stats(
    site_id: str,
    target_date: str = Query(None, description="YYYY-MM-DD, default: today")
):
    """
    Get zone occupancy stats for dashboard.
    Returns data matching your heatmap.html structure:
    
    {
      EMPLOYEE_AREA: { peak: 8, events: 17 },
      RECEPTION_AREA: { peak: 6, events: 312 },
      ...
    }
    """
    if not target_date:
        target_date = date.today().isoformat()
    
    query = """
        SELECT
            zone_id,
            max(peak_occupancy) AS peak,
            sum(total_events) AS events
        FROM daily_zone_peaks_mv FINAL
        WHERE site_id = %(site_id)s
          AND date = %(date)s
        GROUP BY zone_id
    """
    
    rows = ch.execute(query, {'site_id': site_id, 'date': target_date})
    
    # Transform to match frontend expected format
    zones = {}
    for zone_id, peak, events in rows:
        zones[zone_id] = {
            "peak": peak,
            "events": events,
            "intensity": classify_intensity(peak)
        }
    
    return {
        "site_id": site_id,
        "date": target_date,
        "zones": zones
    }

@app.get("/api/v1/hourly/{site_id}")
async def get_hourly_activity(
    site_id: str,
    target_date: str = Query(None)
):
    """
    Get hourly breakdown for "Hourly Activity" grid.
    
    Returns:
      hours: [
        {hour: 5, count: 1, intensity: "low"},
        {hour: 10, count: 8, intensity: "high"},
        ...
      ]
    """
    if not target_date:
        target_date = date.today().isoformat()
    
    query = """
        SELECT
            toHour(hour) AS h,
            sum(peak_count) AS peak_sum,
            sum(event_count) AS events
        FROM hourly_zone_stats_mv
        WHERE site_id = %(site_id)s
          AND toDate(hour) = %(date)s
        GROUP BY h
        ORDER BY h
    """
    
    rows = ch.execute(query, {'site_id': site_id, 'date': target_date})
    
    hours = []
    for h, peak_sum, events in rows:
        # Use average peak across zones for intensity
        avg_peak = peak_sum // max(len(rows), 1)
        hours.append({
            "hour": h,
            "count": avg_peak,
            "events": events,
            "intensity": classify_intensity(avg_peak)
        })
    
    return {
        "site_id": site_id,
        "date": target_date,
        "hours": hours
    }

def classify_intensity(peak: int) -> str:
    """
    Match your frontend classification:
    - Low: 1-3 people
    - Medium: 4-6 people  
    - High: 7+ people
    """
    if peak >= 7:
        return "high"
    elif peak >= 4:
        return "medium"
    else:
        return "low"
```

---

## Layer 5: Frontend Integration

### Update Your heatmap.html

Replace the hardcoded `liveData` with API calls:

```javascript
// Replace lines 284-306 in heatmap.html with:

async function loadDashboardData() {
    const siteId = 'HEAD_OFFICE';
    const today = new Date().toISOString().split('T')[0];
    
    // Fetch zone stats from API
    const zoneResponse = await fetch(`/api/v1/zones/${siteId}/stats?target_date=${today}`);
    const zoneData = await zoneResponse.json();
    
    // Update zone cards
    const zoneMapping = {
        'EMPLOYEE_AREA': 'emp-heat',
        'RECEPTION_AREA': 'rec-heat',
        'CAFETERIA': 'caf-heat',
        'BOSS_CABIN': 'boss-heat'
    };
    
    for (const [zoneId, elementId] of Object.entries(zoneMapping)) {
        const stats = zoneData.zones[zoneId];
        if (stats) {
            const el = document.getElementById(elementId);
            el.textContent = stats.peak;
            el.className = 'heatmap-visual ' + stats.intensity;
            
            // Update peak info text
            const peakInfo = el.parentElement.querySelector('.peak-info');
            if (peakInfo) {
                peakInfo.textContent = `Peak: ${stats.peak} people • ${stats.events} events`;
            }
        }
    }
    
    // Fetch hourly activity
    const hourlyResponse = await fetch(`/api/v1/hourly/${siteId}?target_date=${today}`);
    const hourlyData = await hourlyResponse.json();
    
    // Update time slots (you'll need to update HTML structure)
    updateHourlyGrid(hourlyData.hours);
}

function updateHourlyGrid(hours) {
    const timeSlots = document.querySelectorAll('.time-slot');
    hours.forEach((hourData, index) => {
        if (timeSlots[index]) {
            const slot = timeSlots[index];
            slot.className = 'time-slot ' + hourData.intensity;
            slot.innerHTML = `${formatHour(hourData.hour)}<br><strong>${hourData.count}</strong>`;
        }
    });
}

function formatHour(hour) {
    if (hour === 0) return '12 AM';
    if (hour < 12) return `${hour} AM`;
    if (hour === 12) return '12 PM';
    return `${hour - 12} PM`;
}

// Load on page ready
document.addEventListener('DOMContentLoaded', loadDashboardData);
```

---

## Global Date Filter

### HTML - Add Date Filter UI

Add this to your [heatmap.html](file:///c:/Users/LENOVO/Desktop/my_docs/AG/InvEye/test%202.0/test%203.0-prod/heatmap.html) header section:

```html
<!-- Add after the back button in .header -->
<div class="global-filter">
    <label for="date-filter">Date:</label>
    <input type="date" id="date-filter" />
    
    <!-- Optional: Date range -->
    <label for="date-from" style="margin-left: 1rem;">From:</label>
    <input type="date" id="date-from" />
    <label for="date-to">To:</label>
    <input type="date" id="date-to" />
    
    <button id="apply-filter" class="filter-btn">Apply</button>
</div>

<style>
.global-filter {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-left: auto;
    font-size: 0.85rem;
}
.global-filter input[type="date"] {
    padding: 0.4rem 0.6rem;
    border: 1px solid #E2E8F0;
    border-radius: 6px;
    font-size: 0.85rem;
}
.filter-btn {
    padding: 0.5rem 1rem;
    background: #3B82F6;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
}
.filter-btn:hover {
    background: #2563EB;
}
</style>
```

### JavaScript - Dynamic Data Loading

```javascript
// Global state for date filter
const state = {
    siteId: 'HEAD_OFFICE',
    selectedDate: new Date().toISOString().split('T')[0],
    dateFrom: null,
    dateTo: null
};

// Initialize date filter
function initDateFilter() {
    const dateInput = document.getElementById('date-filter');
    const dateFrom = document.getElementById('date-from');
    const dateTo = document.getElementById('date-to');
    const applyBtn = document.getElementById('apply-filter');
    
    // Set default to today
    dateInput.value = state.selectedDate;
    
    // Single date change
    dateInput.addEventListener('change', (e) => {
        state.selectedDate = e.target.value;
        loadDashboardData();
    });
    
    // Date range apply
    applyBtn.addEventListener('click', () => {
        if (dateFrom.value && dateTo.value) {
            state.dateFrom = dateFrom.value;
            state.dateTo = dateTo.value;
            loadDashboardDataRange();
        } else if (dateInput.value) {
            state.selectedDate = dateInput.value;
            loadDashboardData();
        }
    });
}

// Load data for single date
async function loadDashboardData() {
    const { siteId, selectedDate } = state;
    
    // Show loading state
    showLoading(true);
    
    try {
        // Parallel fetch for performance
        const [zoneData, hourlyData] = await Promise.all([
            fetch(`/api/v1/zones/${siteId}/stats?target_date=${selectedDate}`).then(r => r.json()),
            fetch(`/api/v1/hourly/${siteId}?target_date=${selectedDate}`).then(r => r.json())
        ]);
        
        updateZoneCards(zoneData.zones);
        updateHourlyGrid(hourlyData.hours);
        updateDateDisplay(selectedDate);
        
    } catch (error) {
        console.error('Failed to load data:', error);
        showError('Failed to load heatmap data');
    } finally {
        showLoading(false);
    }
}

// Load data for date range
async function loadDashboardDataRange() {
    const { siteId, dateFrom, dateTo } = state;
    
    showLoading(true);
    
    try {
        const [zoneData, hourlyData] = await Promise.all([
            fetch(`/api/v1/zones/${siteId}/stats?from_date=${dateFrom}&to_date=${dateTo}`).then(r => r.json()),
            fetch(`/api/v1/hourly/${siteId}?from_date=${dateFrom}&to_date=${dateTo}`).then(r => r.json())
        ]);
        
        updateZoneCards(zoneData.zones);
        updateHourlyGrid(hourlyData.hours);
        updateDateDisplay(`${dateFrom} to ${dateTo}`);
        
    } catch (error) {
        console.error('Failed to load data:', error);
    } finally {
        showLoading(false);
    }
}

// Update zone occupancy cards
function updateZoneCards(zones) {
    const mapping = {
        'EMPLOYEE_AREA': 'emp-heat',
        'RECEPTION_AREA': 'rec-heat',
        'CAFETERIA': 'caf-heat',
        'BOSS_CABIN': 'boss-heat'
    };
    
    for (const [zoneId, elementId] of Object.entries(mapping)) {
        const stats = zones[zoneId] || { peak: 0, events: 0, intensity: 'low' };
        const el = document.getElementById(elementId);
        
        if (el) {
            el.textContent = stats.peak;
            el.className = 'heatmap-visual ' + stats.intensity;
            
            const peakInfo = el.parentElement.querySelector('.peak-info');
            if (peakInfo) {
                peakInfo.textContent = `Peak: ${stats.peak} people • ${stats.events} events`;
            }
        }
    }
}

// Update hourly activity grid
function updateHourlyGrid(hours) {
    const container = document.querySelector('.time-grid');
    if (!container) return;
    
    // Clear existing slots
    container.innerHTML = '';
    
    // Generate all 24 hours or just provided data
    for (const hourData of hours) {
        const slot = document.createElement('div');
        slot.className = `time-slot ${hourData.intensity}`;
        slot.innerHTML = `${formatHour(hourData.hour)}<br><strong>${hourData.count}</strong>`;
        container.appendChild(slot);
    }
}

// Update header date display
function updateDateDisplay(dateStr) {
    const subtitle = document.querySelector('.section-header p');
    if (subtitle) {
        subtitle.textContent = `Data from ${dateStr} • ${state.siteId}`;
    }
}

// UI helpers
function showLoading(show) {
    document.body.classList.toggle('loading', show);
}

function formatHour(hour) {
    if (hour === 0) return '12 AM';
    if (hour < 12) return `${hour} AM`;
    if (hour === 12) return '12 PM';
    return `${hour - 12} PM`;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initDateFilter();
    loadDashboardData();
});
```

### Updated API Endpoints (with date range support)

```python
@app.get("/api/v1/zones/{site_id}/stats")
async def get_zone_stats(
    site_id: str,
    target_date: str = Query(None, description="Single date: YYYY-MM-DD"),
    from_date: str = Query(None, description="Range start: YYYY-MM-DD"),
    to_date: str = Query(None, description="Range end: YYYY-MM-DD")
):
    """
    Get zone stats for a date or date range.
    """
    # Determine date filter
    if from_date and to_date:
        date_filter = f"date BETWEEN '{from_date}' AND '{to_date}'"
    elif target_date:
        date_filter = f"date = '{target_date}'"
    else:
        date_filter = f"date = '{date.today().isoformat()}'"
    
    query = f"""
        SELECT
            zone_id,
            max(peak_occupancy) AS peak,
            sum(total_events) AS events
        FROM daily_zone_peaks_mv FINAL
        WHERE site_id = %(site_id)s AND {date_filter}
        GROUP BY zone_id
    """
    
    rows = ch.execute(query, {'site_id': site_id})
    
    zones = {}
    for zone_id, peak, events in rows:
        zones[zone_id] = {
            "peak": peak,
            "events": events,
            "intensity": classify_intensity(peak)
        }
    
    return {"site_id": site_id, "date_filter": date_filter, "zones": zones}


@app.get("/api/v1/hourly/{site_id}")
async def get_hourly_activity(
    site_id: str,
    target_date: str = Query(None),
    from_date: str = Query(None),
    to_date: str = Query(None)
):
    """
    Get hourly breakdown with date range support.
    For ranges, returns averaged/aggregated hourly data.
    """
    if from_date and to_date:
        date_filter = f"toDate(hour) BETWEEN '{from_date}' AND '{to_date}'"
    elif target_date:
        date_filter = f"toDate(hour) = '{target_date}'"
    else:
        date_filter = f"toDate(hour) = '{date.today().isoformat()}'"
    
    query = f"""
        SELECT
            toHour(hour) AS h,
            max(peak_count) AS peak,
            sum(event_count) AS events
        FROM hourly_zone_stats_mv
        WHERE site_id = %(site_id)s AND {date_filter}
        GROUP BY h
        ORDER BY h
    """
    
    rows = ch.execute(query, {'site_id': site_id})
    
    hours = []
    for h, peak, events in rows:
        hours.append({
            "hour": h,
            "count": peak,
            "events": events,
            "intensity": classify_intensity(peak)
        })
    
    return {"site_id": site_id, "hours": hours}

---

## Complete Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         COMPLETE DATA FLOW                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  YOLO DETECTION (every frame, ~10-30 FPS)                                   │
│      │                                                                       │
│      │ {camera: "CAM_001", zone: "EMPLOYEE_AREA", persons: 8}               │
│      ▼                                                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ LAYER 1: Jetson Edge Device                                         │    │
│  │  • Run YOLO11 inference on camera frame                             │    │
│  │  • Count persons detected                                           │    │
│  │  • Map camera_id → zone_id (via config)                             │    │
│  │  • Buffer 10 events, then flush to API                              │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│      │                                                                       │
│      │ POST /api/v1/detections                                              │
│      ▼                                                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ LAYER 2: Ingestion API                                               │    │
│  │  • Validate API key                                                  │    │
│  │  • Transform events to ClickHouse rows                               │    │
│  │  • Batch INSERT to detection_events table                            │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│      │                                                                       │
│      │ INSERT INTO detection_events                                         │
│      ▼                                                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ LAYER 3: ClickHouse                                                  │    │
│  │                                                                      │    │
│  │  detection_events:                                                   │    │
│  │    (site=HEAD_OFFICE, zone=EMPLOYEE_AREA, person_count=8, 11:30:45) │    │
│  │                                                                      │    │
│  │  ─── Materialized Views AUTO-UPDATE ───                              │    │
│  │                                                                      │    │
│  │  hourly_zone_stats_mv:                                               │    │
│  │    (zone=EMPLOYEE_AREA, hour=11:00, peak=8, events=17)              │    │
│  │                                                                      │    │
│  │  daily_zone_peaks_mv:                                                │    │
│  │    (zone=EMPLOYEE_AREA, date=2026-01-05, peak=8, events=17)         │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│      │                                                                       │
│      │ Query                                                                 │
│      ▼                                                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ LAYER 4: Query API                                                   │    │
│  │                                                                      │    │
│  │  GET /api/v1/zones/HEAD_OFFICE/stats                                │    │
│  │                                                                      │    │
│  │  Response:                                                           │    │
│  │  {                                                                   │    │
│  │    "zones": {                                                        │    │
│  │      "EMPLOYEE_AREA": {"peak": 8, "events": 17, "intensity": "high"}│    │
│  │      "RECEPTION_AREA": {"peak": 6, "events": 312, "intensity": "medium"}│ │
│  │    }                                                                 │    │
│  │  }                                                                   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│      │                                                                       │
│      │ JSON                                                                  │
│      ▼                                                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ LAYER 5: Frontend Dashboard (heatmap.html)                           │    │
│  │                                                                      │    │
│  │  EMPLOYEE AREA                                                       │    │
│  │  ┌─────────────────────┐                                             │    │
│  │  │         8           │  ← peak from API                            │    │
│  │  │        HIGH         │  ← intensity from API                       │    │
│  │  │  Peak: 8 • 17 evts  │                                             │    │
│  │  └─────────────────────┘                                             │    │
│  │                                                                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Key Formulas

| Metric | Formula | Example |
|--------|---------|---------|
| **Peak Occupancy** | `MAX(person_count)` per zone per day | 8 people |
| **Event Count** | `COUNT(*)` detection frames | 17 frames |
| **Intensity** | `peak >= 7 → high, >= 4 → medium, else low` | "high" |
| **Hourly Peak** | `MAX(person_count)` per hour | Used for time grid |

---

## Mapping to Your Current heatmap.html

| Your Frontend | Backend Source |
|---------------|----------------|
| `liveData.EMPLOYEE_AREA.peak` | `daily_zone_peaks_mv.peak_occupancy` |
| `liveData.EMPLOYEE_AREA.events` | `daily_zone_peaks_mv.total_events` |
| Time slot count (e.g., "10 AM: 8") | `hourly_zone_stats_mv.peak_count` |
| Intensity class (low/medium/high) | Calculated from peak using thresholds |
