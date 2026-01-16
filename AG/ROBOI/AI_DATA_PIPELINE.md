# Petrol Pump AI Data Pipeline

> **Purpose:** How AI-generated KPI data is captured, processed, stored, and served to the dashboard  
> **Created:** 2026-01-12

---

## 🔄 Data Flow Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           DATA PIPELINE ARCHITECTURE                             │
└─────────────────────────────────────────────────────────────────────────────────┘

    EDGE (Jetson)              CLOUD PROCESSING              STORAGE           FRONTEND
    ─────────────              ────────────────              ───────           ────────
                                                                                
   ┌─────────┐     RTSP       ┌─────────────┐              ┌──────────┐      ┌─────────┐
   │ Camera  │ ──────────────>│   YOLO      │              │ClickHouse│<─────│Dashboard│
   │ (IP/NVR)│                │ Detection   │              │(Analytics)│      │  API    │
   └─────────┘                └──────┬──────┘              └──────────┘      └─────────┘
                                     │                           ▲                 ▲
                              Detections                         │                 │
                                     │                           │                 │
                                     ▼                           │                 │
                              ┌─────────────┐    JSON       ┌────┴─────┐          │
                              │   VLM/LLM   │ ─────────────>│ MongoDB  │──────────┘
                              │ (AI_INFO)   │   AI Output   │  (KPIs)  │
                              └─────────────┘               └──────────┘
                                     │
                              Triggers/Alerts
                                     │
                                     ▼
                              ┌─────────────┐
                              │  Alerting   │ ──> WhatsApp, Email, Push
                              │   Service   │
                              └─────────────┘
```

---

## 📦 Step-by-Step Data Flow

### **Step 1: Camera Capture → YOLO Detection**

```python
# On Jetson Edge Device
# File: roboi-main/roboi-backend/app/services/detection_service.py

# 1. Frame captured from RTSP stream
frame = capture_frame(camera_url)

# 2. YOLO inference
detections = yolo_model.predict(frame)
# Returns: [{class_id: 0, label: "person", bbox: [x,y,w,h], confidence: 0.92}, ...]

# 3. Build YOLO context for VLM
yolo_context = format_detections(detections)
# Output: "Detected: 2 persons, 1 car, 1 motorcycle, 1 du_nozzle"
```

**Output:** Detection data + captured frame(s)

---

### **Step 2: VLM/LLM Analysis (AI_INFO)**

```python
# File: roboi-main/roboi-backend/app/prompt/prompt2.py
# Called by: app/services/ai_service.py

# 1. Send frame + YOLO context to Gemini/GPT
ai_response = call_vlm(
    prompt=AI_INFO_INSTRUCTIONS.format(yolo_context=yolo_context),
    images=[frame_base64]
)

# 2. Parse JSON response
ai_result = json.loads(ai_response)
```

**Output JSON structure:**
```json
{
  "alert_valid": true,
  "status": "safe",
  "ai_verified_people_count": 4,
  "triggers": [],
  
  "ai_overview": {
    "scene_summary": "Active fueling at pump 2",
    "safety_status": "CLEAR",
    "compliance_score": "8/10",
    "issues_found": 1
  },
  
  "ai_deepdive": {
    "vehicles": {
      "count": 2,
      "details": [
        {"type": "car", "color": "white", "number_plate": "GJ05AB7890", "location": "pump 1"}
      ]
    },
    "people": {
      "staff": {"count": 2, "uniform_status": "1 compliant, 1 missing cap"},
      "customers": {"count": 2}
    },
    "safety_checks": {
      "smoking": {"detected": false},
      "fire": {"detected": false},
      "plastic_fill": {"detected": false},
      "du_open": {"detected": false},
      "manhole": {"detected": false}
    },
    "environment": {
      "cleanliness": {"score": 4, "issues": ["minor oil stain"]},
      "garbage": {"found": true, "items": ["plastic bottle"]}
    },
    "compliance_checks": {
      "greeting": {"observed": true},
      "zero_display": {"observed": false}
    }
  },
  
  "kpi_scores": {
    "uniform_score": 4,
    "cleanliness_score": 4,
    "safety_score": 5
  },
  
  "validation_summary": "KPI: 8/10 | Uniform: 4/5 | Clean: 4/5 | Safety: 5/5"
}
```

---

### **Step 3: Storage - Where Data Goes**

#### **A. ClickHouse (Time-Series Analytics)**

```sql
-- Table: video_analytics_logs
-- Purpose: Raw event logging, time-series queries

INSERT INTO video_analytics_logs (
    site_id,
    cam_id,
    cam_name,
    event_timestamp,
    event_type,
    
    -- Counts
    ai_verified_people_count,
    detected_objects,
    
    -- Scores (flattened)
    uniform_score,
    cleanliness_score,
    safety_score,
    compliance_score,
    
    -- Vehicles (arrays)
    vehicle_types,
    vehicle_plates,
    
    -- Safety flags
    smoking_detected,
    fire_detected,
    plastic_fill_detected,
    
    -- Raw AI output
    ai_response_json,
    
    -- Media
    capture_path
) VALUES (
    'RO001',
    1,
    'D1',
    now(),
    'AI_INFO',
    4,
    ['person', 'person', 'car', 'motorcycle'],
    4, 4, 5, 8.0,
    ['car', 'motorcycle'],
    ['GJ05AB7890', 'GJ01XX1234'],
    false, false, false,
    '{"ai_overview": {...}, "ai_deepdive": {...}}',
    'gs://bucket/captures/RO001/D1/2026-01-12/capture_001.webp'
);
```

**Use Case:** Dashboard analytics, hourly aggregations, trends

---

#### **B. MongoDB (Document Store for KPIs)**

```javascript
// Collection: ai_analysis
// Purpose: Full AI analysis documents for detailed querying

db.ai_analysis.insertOne({
  "_id": ObjectId("..."),
  "event_id": "insight_RO001_D1_1705054200",
  "site_id": "RO001",
  "cam_name": "D1",
  "analyzed_at": ISODate("2026-01-12T09:30:00Z"),
  
  "status": "safe",
  "people_count": 4,
  "vehicle_count": 2,
  
  "kpi_scores": {
    "uniform": 4,
    "cleanliness": 4,
    "safety": 5,
    "greeting": 1,
    "zero_display": 0
  },
  
  "compliance_score": 8.0,
  
  "vehicles": [
    {"type": "car", "plate": "GJ05AB7890", "pump": 1, "color": "white"},
    {"type": "motorcycle", "plate": "GJ01XX1234", "pump": 2, "color": "red"}
  ],
  
  "staff": {
    "count": 2,
    "compliant": 1,
    "issues": ["missing cap"]
  },
  
  "safety_checks": {
    "smoking": false,
    "fire": false,
    "plastic_fill": false,
    "du_open": false,
    "manhole": false
  },
  
  "environment": {
    "garbage_items": ["plastic bottle"],
    "clutter_items": [],
    "spill_detected": false
  },
  
  "triggers": [],
  "ai_summary": "Operations normal. 1 uniform issue. Minor garbage.",
  
  "media_path": "gs://bucket/captures/RO001/D1/2026-01-12/capture_001.webp",
  "created_at": ISODate("2026-01-12T09:30:05Z")
});
```

**Use Case:** Detailed KPI drill-downs, event history, issue tracking

---

#### **C. Redis (Real-Time Cache)**

```python
# Cache structure for live dashboard updates

# Latest site status
redis.set("site:RO001:status", json.dumps({
    "online": True,
    "last_analysis": "2026-01-12T09:30:00Z",
    "compliance_score": 8.0,
    "active_cameras": 5,
    "open_alerts": 2
}), ex=60)  # TTL: 60 seconds

# Live pump status
redis.hset("site:RO001:pumps", "pump_1", json.dumps({
    "status": "active",
    "vehicle": "GJ05AB7890",
    "staff": "Ramesh Kumar",
    "timer_start": 1705054200
}))

# Recent vehicles queue
redis.lpush("site:RO001:recent_vehicles", json.dumps({
    "plate": "GJ05AB7890",
    "type": "car",
    "pump": 1,
    "timestamp": 1705054200
}))
redis.ltrim("site:RO001:recent_vehicles", 0, 49)  # Keep last 50
```

**Use Case:** Real-time dashboard updates, live operations view

---

### **Step 4: Processing & Aggregation**

```python
# File: app/services/kpi_aggregator.py
# Runs every 5 minutes or on each AI analysis

def aggregate_hourly_kpis(site_id: str, hour: datetime):
    """Aggregate KPI scores for the hour."""
    
    # Query all analyses for this hour
    analyses = db.ai_analysis.find({
        "site_id": site_id,
        "analyzed_at": {
            "$gte": hour,
            "$lt": hour + timedelta(hours=1)
        }
    })
    
    # Calculate averages
    kpi_sums = {"uniform": 0, "cleanliness": 0, "safety": 0}
    count = 0
    total_vehicles = 0
    total_alerts = 0
    
    for analysis in analyses:
        for key in kpi_sums:
            kpi_sums[key] += analysis["kpi_scores"].get(key, 0)
        total_vehicles += analysis.get("vehicle_count", 0)
        total_alerts += len(analysis.get("triggers", []))
        count += 1
    
    # Store hourly summary
    db.kpi_hourly_summary.updateOne(
        {"site_id": site_id, "hour_start": hour},
        {"$set": {
            "kpi_averages": {k: v/count for k, v in kpi_sums.items()},
            "total_vehicles": total_vehicles,
            "total_alerts": total_alerts,
            "analysis_count": count
        }},
        upsert=True
    )
```

---

### **Step 5: API Endpoints for Dashboard**

```python
# File: app/api/endpoints/kpi.py

@router.get("/api/v1/sites/{site_id}/dashboard")
async def get_dashboard_data(site_id: str):
    """Main dashboard API - aggregates all KPI data."""
    
    # 1. Get latest analysis
    latest = await mongodb.ai_analysis.find_one(
        {"site_id": site_id},
        sort=[("analyzed_at", -1)]
    )
    
    # 2. Get today's summary from ClickHouse
    today_stats = await clickhouse.execute("""
        SELECT 
            count() as total_analyses,
            sum(vehicle_count) as total_vehicles,
            avg(compliance_score) as avg_compliance,
            countIf(smoking_detected) as smoking_incidents,
            countIf(fire_detected) as fire_incidents
        FROM video_analytics_logs
        WHERE site_id = {site_id}
        AND event_timestamp >= today()
    """, {"site_id": site_id})
    
    # 3. Get live status from Redis
    live_status = await redis.get(f"site:{site_id}:status")
    pump_status = await redis.hgetall(f"site:{site_id}:pumps")
    
    return {
        "site_id": site_id,
        "status": "online" if live_status else "offline",
        "last_update": latest["analyzed_at"],
        
        "metrics": {
            "revenue_today": calculate_revenue(today_stats["total_vehicles"]),
            "vehicles_served": today_stats["total_vehicles"],
            "compliance_score": today_stats["avg_compliance"],
            "open_alerts": count_open_alerts(site_id)
        },
        
        "live_operations": {
            "pumps": parse_pump_status(pump_status),
            "staff_on_duty": get_staff_on_duty(site_id)
        },
        
        "safety": {
            "smoking": {"incidents_today": today_stats["smoking_incidents"]},
            "fire": {"detected": False},
            "du_covers": "all_closed",
            "manholes": "all_covered"
        },
        
        "recent_vehicles": latest.get("vehicles", []),
        "action_items": get_open_issues(site_id)
    }


@router.get("/api/v1/sites/{site_id}/kpi/compliance")
async def get_compliance_details(site_id: str, date: str = None):
    """Compliance page - detailed breakdown."""
    
    analyses = await mongodb.ai_analysis.find({
        "site_id": site_id,
        "analyzed_at": {"$gte": parse_date(date)}
    }).to_list(100)
    
    return {
        "uniform_compliance": calculate_uniform_stats(analyses),
        "greeting_rate": calculate_greeting_rate(analyses),
        "zero_display_rate": calculate_zero_display_rate(analyses),
        "staff_details": get_staff_compliance(analyses)
    }


@router.get("/api/v1/sites/{site_id}/kpi/vehicles")
async def get_vehicle_data(site_id: str, limit: int = 50):
    """Vehicles page - license plates and transactions."""
    
    return await mongodb.ai_analysis.aggregate([
        {"$match": {"site_id": site_id}},
        {"$unwind": "$vehicles"},
        {"$sort": {"analyzed_at": -1}},
        {"$limit": limit},
        {"$project": {
            "plate": "$vehicles.plate",
            "type": "$vehicles.type",
            "color": "$vehicles.color",
            "pump": "$vehicles.pump",
            "timestamp": "$analyzed_at"
        }}
    ]).to_list(limit)
```

---

## 📊 Storage Summary

| Data Type | Storage | Retention | Use Case |
|-----------|---------|-----------|----------|
| Raw detections | ClickHouse | 90 days | Time-series analytics |
| AI analysis | MongoDB | 1 year | KPI drill-downs |
| Live status | Redis | 60 sec TTL | Real-time dashboard |
| Media captures | GCS/S3 | 30 days | Evidence review |
| Alerts | MongoDB | Indefinite | Audit trail |

---

## 🔌 Dashboard Integration

```javascript
// Frontend: dashboard.js

// 1. Initial load - fetch all data
async function loadDashboard() {
    const data = await fetch('/api/v1/sites/RO001/dashboard');
    renderDashboard(data);
}

// 2. Real-time updates via WebSocket
const ws = new WebSocket('wss://api.roboi.com/ws/RO001');

ws.onmessage = (event) => {
    const update = JSON.parse(event.data);
    
    if (update.type === 'pump_update') {
        updatePumpStatus(update.data);
    } else if (update.type === 'new_vehicle') {
        addRecentVehicle(update.data);
    } else if (update.type === 'alert') {
        showAlert(update.data);
    }
};

// 3. Poll for KPI updates (fallback)
setInterval(async () => {
    const kpis = await fetch('/api/v1/sites/RO001/kpi/live');
    updateKPICards(kpis);
}, 30000); // Every 30 seconds
```

---

## 📁 Files to Implement

| Component | File | Status |
|-----------|------|--------|
| AI Prompt | `app/prompt/prompt2.py` | ✅ Exists |
| AI Service | `app/services/ai_service.py` | 🔄 Implement |
| KPI Endpoints | `app/api/endpoints/kpi.py` | 🔄 Implement |
| Aggregator | `app/services/kpi_aggregator.py` | 🔄 Implement |
| MongoDB Models | `app/models/kpi_schemas.py` | 🔄 Implement |
| ClickHouse Queries | `app/db/clickhouse_queries.py` | ✅ Partial |
| Dashboard JS | `ROBOI_FRONTEND_DEMO/dashboard.js` | ✅ Mock data |

---

> [!TIP]
> **Quick Start:** The `dashboard.js` currently uses mock data. Replace the `mockData` object with API calls to `/api/v1/sites/{site_id}/dashboard` once the backend endpoints are implemented.

> [!IMPORTANT]
> **Critical Path:** Implement `kpi.py` endpoints → Connect to MongoDB → Test with real AI output → Update dashboard.js to fetch from API.
