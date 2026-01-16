# 📊 Test 3.0 - Extended Object Detection Dashboard

## METRIC vs EVENT: Understanding the Difference

### **METRIC** (Regular Telemetry)
```json
{
  "type": "METRIC",
  "meta": {
    "ts": "2025-12-16T13:37:10.971002Z",
    "cam_id": "CAFETERIA",
    "site": "HEAD_OFFICE",
    "status": "SAFE"           // SAFE = normal operation
  },
  "data": {
    "people_count": 8,
    "detections": [...]        // Array of all detected objects
  }
}
```

**Purpose**: Continuous monitoring data sent at regular intervals (e.g., every second)
- **When sent**: Constantly, on every frame processed
- **Status**: Usually `SAFE` (normal) or `WARNING` (elevated)
- **Contains**: `data.people_count` + `data.detections[]`
- **Use case**: Populate dashboards, charts, object counts

---

### **EVENT** (Triggered Alert)
```json
{
  "type": "EVENT",
  "meta": {
    "ts": "2025-12-16T13:43:49.138755Z",
    "cam_id": "BOSS_CABIN",
    "site": "HEAD_OFFICE",
    "status": "CRITICAL"       // CRITICAL = action required
  },
  "event": {
    "triggers": ["RESTRICTED_ACCESS_BOSS_CABIN"],  // Why it triggered
    "people_count": 1,
    "detections": [...],
    "capture_triggered": true  // Screenshot/video captured
  }
}
```

**Purpose**: Alert when something unusual/important happens
- **When sent**: Only when a rule is triggered
- **Status**: Usually `CRITICAL` or `WARNING`
- **Contains**: `event.triggers[]` + `event.people_count` + `event.detections[]`
- **Use case**: Alerts, notifications, security events

---

## Key Differences Table

| Aspect | METRIC | EVENT |
|--------|--------|-------|
| **Frequency** | Continuous (every frame) | On-demand (rule triggered) |
| **Status** | Usually `SAFE` | Usually `CRITICAL` |
| **Data Location** | `data.people_count`, `data.detections` | `event.people_count`, `event.detections` |
| **Has Triggers** | ❌ No | ✅ Yes (`event.triggers[]`) |
| **Capture** | ❌ No | ✅ Optional (`capture_triggered`) |
| **Use** | Analytics, dashboards | Alerts, security |

---

## Detected Object Classes (COCO)

| Class ID | Label | Icon |
|----------|-------|------|
| 0 | person | 👤 |
| 24 | backpack | 🎒 |
| 39 | bottle | 🍼 |
| 56 | chair | 🪑 |
| 60 | dining table | 🍽️ |
| 62 | tv | 📺 |
| 63 | laptop | 💻 |
| 68 | microwave | 📦 |
| 74 | clock | ⏰ |

---

## What's New in Test 3.0

- ✅ Extended object detection support (clock, laptop, backpack, bottle, microwave, dining table)
- ✅ Object icons in detection summary
- ✅ Improved object categorization bars
- ✅ Better METRIC/EVENT differentiation in UI
- ✅ Object-specific styling and colors
