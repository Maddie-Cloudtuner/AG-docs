# Petrol Pump AI KPI Documentation

## 1. KPI Summary

### Safety KPIs (Critical Alert Triggers)
| KPI | YOLO Labels Used | Quantification | Alert Threshold |
|-----|------------------|----------------|-----------------|
| **Smoking Detection** | `cigarette(21)`, `smoke(20)`, `face(25)` | Binary: YES/NO | Immediate alert |
| **Fire Detection** | `fire(19)`, `smoke(20)` | Confidence % + bbox size | > 60% confidence |
| **Plastic Fill** | `container(24)`, `du_nozzle(22)`, `person(0)` | Logic: Nozzle + Container + No Vehicle | Immediate alert |
| **DU Cover Open** | Custom class | Confidence % | > 80% |
| **Manhole Open** | Custom class | Binary | Immediate alert |
| **Mob Gathering** | `person(0)` count | Count > 10 in zone | Alert when exceeded |

### Compliance KPIs (Scored 1-5)
| KPI | YOLO Labels Used | Quantification Method |
|-----|------------------|----------------------|
| **Uniform Score** | `person(0)`, `face(25)` | VLM rates: hat, tucked shirt, safety shoes |
| **Cleanliness Score** | `bottle(11)`, `chair(13)`, scene analysis | Count garbage items + spill detection |
| **Clutter Score** | `chair(13)`, `bottle(11)`, `backpack(8)` | Count items blocking driveway |

### Operational KPIs
| KPI | YOLO Labels Used | Quantification Method |
|-----|------------------|----------------------|
| **Vehicle Count** | `car(2)`, `motorcycle(3)`, `bus(4)`, `truck(5)`, `bicycle(1)` | Direct count |
| **License Plate** | `license_plate(23)` | OCR extraction |
| **People Count** | `person(0)` | Direct count |
| **FSM Attendance** | `face(25)` + recognition | Match against employee DB |
| **Greeting (Namaste)** | Pose estimation | Wrists/elbows close (prayer pose) |
| **Showing Zero** | `du_nozzle(22)` + `person(0)` | Pointing gesture near DU |

---

## 2. LLM JSON Output Format

```json
{
  "alert_valid": true,
  "status": "safe",
  "actual_people_count": 4,
  "media_analyzed": 11,
  
  "kpi_scores": {
    "uniform_score": 5,
    "cleanliness_score": 4,
    "safety_score": 5,
    "greeting_score": 1,
    "zero_display_score": 0
  },
  
  "utilization": "medium",
  
  "detections": {
    "vehicles": {
      "total": 2,
      "details": [
        {"type": "car", "color": "white", "plate": "GJ05AB7890", "pump": 1},
        {"type": "motorcycle", "color": "black", "plate": "not_visible", "pump": 2}
      ]
    },
    "people": {
      "total": 4,
      "staff": {"count": 2, "uniform_compliant": 2},
      "customers": {"count": 2}
    },
    "garbage_items": [],
    "clutter_items": []
  },
  
  "safety_checks": {
    "smoking": {"detected": false, "confidence": 0},
    "fire": {"detected": false, "confidence": 0},
    "plastic_fill": {"detected": false},
    "du_open": {"detected": false},
    "manhole_open": {"detected": false}
  },
  
  "triggers": [],
  "insights": "Operations running smoothly. All staff in proper uniform.",
  
  "verdict": "KPI Analysis - 10/10 compliance. 0 issues found.",
  "what_happened": "AI OVERVIEW: • Active pump • 2 vehicles (GJ05AB7890) • 2 staff compliant. DEEPDIVE: Clean premises, no issues.",
  "why_it_happened": "",
  "recommendation": "NO ACTION REQUIRED - All KPIs compliant.",
  "validation_summary": "KPI: 10/10 | Uniform: 5/5 | Clean: 4/5 | Safety: 5/5"
}
```

---

## 3. Quantified Metrics Using YOLO Labels

### Cleanliness Score Calculation

| Score | Criteria | YOLO Labels Detected |
|-------|----------|---------------------|
| **5** | Spotless - No garbage, no spills | No `bottle(11)`, no debris |
| **4** | Minor - 1-2 small items | 1-2 `bottle(11)` near bins |
| **3** | Moderate - Visible garbage | 3-5 `bottle(11)`, papers visible |
| **2** | Poor - Multiple issues | > 5 garbage items, `chair(13)` blocking |
| **1** | Very Poor - Major issues | Excessive garbage, visible spills |

**Formula:**
```
cleanliness_score = max(1, 5 - floor(garbage_count / 2) - spill_penalty)

Where:
- garbage_count = count(bottle) + count(loose_items)
- spill_penalty = 1 if oil_spill_detected else 0
```

### Uniform Score Calculation

| Score | Criteria | VLM Assessment |
|-------|----------|----------------|
| **5** | Full uniform | Hat ✓, Tucked shirt ✓, Safety shoes ✓ |
| **4** | Minor issue | 1 item missing (e.g., no hat) |
| **3** | Moderate | 2 items missing |
| **2** | Poor | Only shirt visible |
| **1** | No uniform | Cannot assess / no staff |

**Formula:**
```
uniform_score = sum(hat_visible, shirt_tucked, proper_shoes) + 2
# Bonus +2 if all items present
```

### Safety Score Calculation

| Score | Criteria | Detection Status |
|-------|----------|------------------|
| **5** | All clear | No smoking, fire, DU open, manhole |
| **4** | Minor concern | Unrelated smoke (exhaust) |
| **3** | Moderate | Cell phone near pump |
| **2** | Safety issue | DU open, manhole visible |
| **1** | Critical | Smoking or fire detected |

**Formula:**
```
safety_score = 5
if smoking_detected: safety_score = 1
if fire_detected: safety_score = 1
if du_open: safety_score = min(safety_score, 2)
if cell_phone_near_pump: safety_score = min(safety_score, 3)
```

### Utilization Calculation

| Level | People Count | Vehicle Count |
|-------|--------------|---------------|
| **Low** | 0-2 | 0-1 |
| **Medium** | 3-5 | 2-3 |
| **High** | 6+ | 4+ |

---

## 4. YOLO Label Mapping for KPIs

```
YOLO Class → KPI Mapping:

person(0)        → People count, Mob detection, Staff presence
bicycle(1)       → Vehicle count
car(2)           → Vehicle count, Conversion tracking
motorcycle(3)    → Vehicle count  
bus(4)           → Vehicle count
truck(5)         → Vehicle count
fire hydrant(6)  → Safety landmark
dog(7)           → Anomaly detection
backpack(8)      → Clutter detection
handbag(9)       → Customer identification
suitcase(10)     → Clutter detection
bottle(11)       → Garbage/Cleanliness score
knife(12)        → Safety alert
chair(13)        → Clutter detection
toilet(14)       → N/A
tv(15)           → N/A
cell phone(16)   → Safety concern near pump
clock(17)        → N/A
scissors(18)     → Safety alert
fire(19)         → CRITICAL - Fire detection
smoke(20)        → Safety - Fire/Smoking detection
cigarette(21)    → CRITICAL - Smoking detection
du_nozzle(22)    → Fuel operations tracking
license_plate(23)→ Vehicle identification (OCR)
container(24)    → Plastic fill detection
face(25)         → Face recognition, Staff ID
```

---

## 5. MongoDB Schema for AI Insights

### Collection: `ai_analysis`

```javascript
// Main AI Analysis Document
{
  "_id": ObjectId("..."),
  "event_id": "insight_india_gujarat_ahmedabad_ro001_d5_1767862506",
  "site_id": "ro001",
  "cam_name": "d5",
  "analyzed_at": ISODate("2026-01-12T12:30:00.000Z"),
  
  // Status
  "alert_valid": true,
  "status": "safe", // safe | warning | critical
  
  // Counts
  "people_count": 4,
  "vehicle_count": 2,
  "media_analyzed": 11,
  
  // KPI Scores (1-5)
  "kpi_scores": {
    "uniform": 5,
    "cleanliness": 4,
    "safety": 5,
    "greeting": 1,      // 0 or 1
    "zero_display": 0   // 0 or 1
  },
  
  // Utilization
  "utilization": "medium", // low | medium | high
  
  // Compliance
  "compliance_score": 9.5,  // X/10
  "issues_found": 0,
  
  // Vehicles (Embedded)
  "vehicles": [
    {
      "type": "car",
      "color": "white",
      "license_plate": "GJ05AB7890",
      "pump": 1,
      "confidence": 0.92
    },
    {
      "type": "motorcycle",
      "color": "black",
      "license_plate": "not_visible",
      "pump": 2,
      "confidence": 0.88
    }
  ],
  
  // People (Embedded)
  "people": {
    "staff": {
      "count": 2,
      "uniform_compliant": 2,
      "details": ["Hat:Yes, Shirt:Yes, Shoes:Yes"]
    },
    "customers": {
      "count": 2
    }
  },
  
  // Environment (Embedded)
  "environment": {
    "garbage_items": [],
    "clutter_items": [],
    "spills_detected": false
  },
  
  // Safety Checks (Embedded)
  "safety_checks": {
    "smoking": { "detected": false, "confidence": 0 },
    "fire": { "detected": false, "confidence": 0 },
    "plastic_fill": { "detected": false },
    "du_open": { "detected": false },
    "manhole_open": { "detected": false },
    "cell_phone": { "detected": false }
  },
  
  // Triggers Array
  "triggers": [],
  
  // AI Output Text
  "ai_output": {
    "verdict": "KPI Analysis - 10/10 compliance. 0 issues found.",
    "what_happened": "AI OVERVIEW: • Active pump • 2 vehicles (GJ05AB7890) • 2 staff compliant.",
    "why_it_happened": "",
    "recommendation": "NO ACTION REQUIRED - All KPIs compliant.",
    "validation_summary": "KPI: 10/10 | Uniform: 5/5 | Clean: 4/5 | Safety: 5/5",
    "insights": "Operations running smoothly. All staff in proper uniform."
  },
  
  // Media Reference
  "media_files": [
    "gs://roboi-event-captures/events/.../1.webp",
    "gs://roboi-event-captures/events/.../2.webp"
  ],
  
  // Timestamps
  "created_at": ISODate("2026-01-12T12:30:00.000Z"),
  "updated_at": ISODate("2026-01-12T12:30:00.000Z")
}
```

### Collection: `kpi_hourly_summary`

```javascript
// Aggregated Hourly Summary for Dashboards
{
  "_id": ObjectId("..."),
  "site_id": "ro001",
  "cam_name": "d5",
  "hour_start": ISODate("2026-01-12T12:00:00.000Z"),
  
  "kpi_averages": {
    "uniform": 4.5,
    "cleanliness": 4.2,
    "safety": 4.8,
    "compliance": 8.7
  },
  
  "totals": {
    "vehicles": 45,
    "people": 120,
    "alerts": 2,
    "analyses": 15
  },
  
  "issues_breakdown": {
    "uniform_violations": 3,
    "cleanliness_issues": 2,
    "safety_alerts": 0
  }
}
```

### Collection: `safety_alerts`

```javascript
// Critical Safety Alerts (for fast retrieval)
{
  "_id": ObjectId("..."),
  "analysis_id": ObjectId("..."),
  "site_id": "ro001",
  "cam_name": "d5",
  "alert_type": "smoking_detected", // smoking | fire | plastic_fill | du_open | manhole
  "severity": "critical",
  "detected_at": ISODate("2026-01-12T12:30:00.000Z"),
  "confidence": 0.87,
  "location": "pump_2",
  "resolved": false,
  "resolved_at": null,
  "details": {
    "person_count": 1,
    "description": "Customer smoking near active fuel pump"
  }
}
```

### Indexes

```javascript
// ai_analysis indexes
db.ai_analysis.createIndex({ "site_id": 1, "cam_name": 1, "analyzed_at": -1 })
db.ai_analysis.createIndex({ "status": 1, "analyzed_at": -1 })
db.ai_analysis.createIndex({ "event_id": 1 }, { unique: true })
db.ai_analysis.createIndex({ "analyzed_at": -1 })
db.ai_analysis.createIndex({ "triggers": 1 })

// kpi_hourly_summary indexes
db.kpi_hourly_summary.createIndex({ "site_id": 1, "cam_name": 1, "hour_start": -1 })

// safety_alerts indexes
db.safety_alerts.createIndex({ "site_id": 1, "alert_type": 1, "detected_at": -1 })
db.safety_alerts.createIndex({ "resolved": 1, "severity": 1 })
```

---

## 6. MongoDB Query Examples

### Get Latest Analysis
```javascript
db.ai_analysis.findOne(
  { site_id: "ro001" },
  { sort: { analyzed_at: -1 } }
)
```

### Get KPI Trends (Last 24 Hours)
```javascript
db.ai_analysis.aggregate([
  {
    $match: {
      analyzed_at: { $gte: new Date(Date.now() - 24*60*60*1000) }
    }
  },
  {
    $group: {
      _id: {
        $dateToString: { format: "%Y-%m-%d %H:00", date: "$analyzed_at" }
      },
      avg_uniform: { $avg: "$kpi_scores.uniform" },
      avg_cleanliness: { $avg: "$kpi_scores.cleanliness" },
      avg_safety: { $avg: "$kpi_scores.safety" },
      count: { $sum: 1 }
    }
  },
  { $sort: { "_id": 1 } }
])
```

### Get Safety Alerts (Last 7 Days)
```javascript
db.ai_analysis.find({
  status: "critical",
  analyzed_at: { $gte: new Date(Date.now() - 7*24*60*60*1000) }
}).sort({ analyzed_at: -1 })
```

### Vehicle Statistics
```javascript
db.ai_analysis.aggregate([
  {
    $match: {
      analyzed_at: { $gte: new Date(Date.now() - 24*60*60*1000) }
    }
  },
  { $unwind: "$vehicles" },
  {
    $group: {
      _id: "$vehicles.type",
      total: { $sum: 1 },
      unique_plates: { $addToSet: "$vehicles.license_plate" }
    }
  },
  {
    $project: {
      vehicle_type: "$_id",
      total: 1,
      unique_plates_count: { $size: "$unique_plates" }
    }
  }
])
```

### Get Site Dashboard Summary
```javascript
db.ai_analysis.aggregate([
  {
    $match: {
      site_id: "ro001",
      analyzed_at: { $gte: new Date(Date.now() - 24*60*60*1000) }
    }
  },
  {
    $group: {
      _id: "$site_id",
      avg_compliance: { $avg: "$compliance_score" },
      total_vehicles: { $sum: "$vehicle_count" },
      total_people: { $sum: "$people_count" },
      total_alerts: { $sum: { $cond: [{ $eq: ["$status", "critical"] }, 1, 0] } },
      total_analyses: { $sum: 1 }
    }
  }
])
```
