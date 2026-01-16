# Heatmap Backend - Developer Handoff

> **For: Fullstack Developer**  
> **Date:** January 5, 2026

---

## Quick Summary

| What | Details |
|------|---------|
| **Frontend** | `heatmap_v2.html` - ready to use |
| **APIs Needed** | **Only 2 endpoints** |
| **Database** | ClickHouse (existing `camera_events` table) |
| **Data Source** | Existing YOLO detections - already being ingested |

---

## Files to Share

```
📁 Handoff Package
├── heatmap_v2.html              ← Frontend (production-ready)
├── DEVELOPER_HANDOFF.md         ← This document
├── schema_doc.md                ← Existing ClickHouse schema
```

---

## Your Existing Schema (camera_events)

The heatmap queries your **existing** `camera_events` table. Key columns used:

| Column | Type | Usage for Heatmap |
|--------|------|-------------------|
| `cam_name` | `LowCardinality(String)` | Zone identifier (EMPLOYEE_AREA, etc.) |
| `site_name` | `LowCardinality(String)` | Site filter |
| `people_count` | `UInt16` | Peak occupancy count |
| `event_timestamp` | `UInt16` | Date/time filter |
| `event_triggers` | `Array(String)` | Critical event type counts |

---

## API Design (2 Endpoints Only)

### API 1: Ingest Events (Already Exists)

Your existing ingestion to `camera_events` - no changes needed.

---

### API 2: Dashboard Data (NEW - Single Endpoint)

```
GET /api/v1/dashboard/{site_name}?date=2026-01-05
```

**Response:**
```json
{
  "site_name": "HEAD_OFFICE",
  "date": "2026-01-05",
  "zones": {
    "EMPLOYEE_AREA": {"peak": 8, "events": 17, "intensity": "high"},
    "RECEPTION_AREA": {"peak": 6, "events": 312, "intensity": "medium"},
    "CAFETERIA": {"peak": 2, "events": 16, "intensity": "low"},
    "BOSS_CABIN": {"peak": 2, "events": 382, "intensity": "low"}
  },
  "hourly": [
    {"hour": 5, "count": 1, "intensity": "low"},
    {"hour": 10, "count": 8, "intensity": "high"}
  ],
  "critical_events": {
    "UNAUTHORIZED_STRANGER": 23,
    "RESTRICTED_ACCESS": 18,
    "CROWD_VIOLATION": 3,
    "total_events": 2844
  }
}
```

---

## Backend Implementation (FastAPI)

```python
from fastapi import FastAPI, Query
from clickhouse_driver import Client
from datetime import datetime

app = FastAPI()
ch = Client(host='clickhouse', database='your_database')

@app.get("/api/v1/dashboard/{site_name}")
async def get_dashboard(
    site_name: str,
    date: str = Query(None, description="YYYY-MM-DD")
):
    # Convert date to timestamp range
    if date:
        target_date = datetime.strptime(date, '%Y-%m-%d')
        start_ts = int(target_date.timestamp())
        end_ts = start_ts + 86400
    else:
        start_ts = int(datetime.now().replace(hour=0, minute=0, second=0).timestamp())
        end_ts = start_ts + 86400
    
    # ZONES: Peak people_count per camera (zone)
    zones_query = """
        SELECT 
            cam_name AS zone_id,
            max(people_count) AS peak,
            count() AS events
        FROM camera_events
        WHERE site_name = %(site_name)s
          AND event_timestamp >= %(start_ts)s
          AND event_timestamp < %(end_ts)s
        GROUP BY cam_name
    """
    zones_raw = ch.execute(zones_query, {
        'site_name': site_name, 'start_ts': start_ts, 'end_ts': end_ts
    })
    
    zones = {}
    for zone_id, peak, events in zones_raw:
        zones[zone_id] = {
            "peak": peak,
            "events": events,
            "intensity": "high" if peak >= 7 else "medium" if peak >= 4 else "low"
        }
    
    # HOURLY: Max people_count per hour
    hourly_query = """
        SELECT 
            toHour(toDateTime(event_timestamp)) AS hour,
            max(people_count) AS peak
        FROM camera_events
        WHERE site_name = %(site_name)s
          AND event_timestamp >= %(start_ts)s
          AND event_timestamp < %(end_ts)s
        GROUP BY hour
        ORDER BY hour
    """
    hourly_raw = ch.execute(hourly_query, {
        'site_name': site_name, 'start_ts': start_ts, 'end_ts': end_ts
    })
    
    hourly = [{"hour": h, "count": p, "intensity": "high" if p >= 7 else "medium" if p >= 4 else "low"} 
              for h, p in hourly_raw]
    
    # CRITICAL EVENTS: Count by trigger type
    events_query = """
        SELECT trigger, count() AS cnt
        FROM camera_events
        ARRAY JOIN event_triggers AS trigger
        WHERE site_name = %(site_name)s
          AND event_timestamp >= %(start_ts)s
          AND event_timestamp < %(end_ts)s
        GROUP BY trigger
    """
    events_raw = ch.execute(events_query, {
        'site_name': site_name, 'start_ts': start_ts, 'end_ts': end_ts
    })
    critical_events = {row[0]: row[1] for row in events_raw}
    
    # Total events
    total = ch.execute("""
        SELECT count() FROM camera_events
        WHERE site_name = %(site_name)s
          AND event_timestamp >= %(start_ts)s AND event_timestamp < %(end_ts)s
    """, {'site_name': site_name, 'start_ts': start_ts, 'end_ts': end_ts})[0][0]
    
    critical_events['total_events'] = total
    
    return {
        "site_name": site_name,
        "date": date or datetime.now().strftime('%Y-%m-%d'),
        "zones": zones,
        "hourly": hourly,
        "critical_events": critical_events
    }
```

---

## ClickHouse Queries Reference

### Peak Occupancy Per Zone
```sql
SELECT cam_name AS zone, max(people_count) AS peak, count() AS events
FROM camera_events
WHERE site_name = 'HEAD_OFFICE'
  AND toDate(toDateTime(event_timestamp)) = '2026-01-05'
GROUP BY cam_name
```

### Hourly Activity
```sql
SELECT toHour(toDateTime(event_timestamp)) AS hour, max(people_count) AS peak
FROM camera_events
WHERE site_name = 'HEAD_OFFICE'
  AND toDate(toDateTime(event_timestamp)) = '2026-01-05'
GROUP BY hour ORDER BY hour
```

### Critical Events by Trigger
```sql
SELECT trigger, count() AS count
FROM camera_events
ARRAY JOIN event_triggers AS trigger
WHERE site_name = 'HEAD_OFFICE'
  AND toDate(toDateTime(event_timestamp)) = '2026-01-05'
GROUP BY trigger
```

---

## Frontend Configuration

Update `heatmap_v2.html` CONFIG section:

```javascript
const CONFIG = {
    API_BASE_URL: 'https://your-api.inveye.io/api/v1',
    SITE_ID: 'HEAD_OFFICE',  // Must match site_name in DB
    
    ZONES: {
        'EMPLOYEE_AREA': 'Employee Area',
        'RECEPTION_AREA': 'Reception Area',
        'CAFETERIA': 'Cafeteria',
        'BOSS_CABIN': 'Boss Cabin'
    }
};
```

---

## Data Flow

```
Existing:                              NEW:
┌─────────────┐     ┌─────────────┐
│   Jetson    │────▶│camera_events│
│   + YOLO    │     │   (exists)  │
└─────────────┘     └──────┬──────┘
                           │
                           ▼
┌─────────────┐     ┌─────────────┐
│  Frontend   │◀────│GET /dashboard│ ← Implement this
│ heatmap_v2  │     │  /{site}    │
└─────────────┘     └─────────────┘
```

---

## Developer Checklist

- [ ] Implement `GET /api/v1/dashboard/{site_name}` endpoint
- [ ] Test queries against existing camera_events data
- [ ] Update `CONFIG.SITE_ID` in heatmap_v2.html
- [ ] Map `cam_name` values to `CONFIG.ZONES` display names
- [ ] Deploy and test

---

## Note on Timestamps

Your schema uses `UInt16` for `event_timestamp`. Check if this is:
- Unix timestamp (will overflow UInt16 - max 65535)
- Seconds since midnight
- Some other format

Adjust queries accordingly.
