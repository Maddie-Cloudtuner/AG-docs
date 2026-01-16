# Petrol Pump KPI Cards - Additional Dashboard Cards

> **Created:** 2026-01-12  
> **Based on:** `prompt_ai_info.py`, `prompt.py`, `prompt2.py`  
> **Purpose:** Define all possible KPI cards from AI analysis data

---

## 📊 Current Dashboard Cards (Already Implemented)

| Card | Data Source | Status |
|------|-------------|--------|
| Active Cameras | System | ✅ |
| Active Events | Event count | ✅ |
| Critical Alerts | Trigger count | ✅ |
| Total People | `ai_verified_people_count` | ✅ |
| Peak Occupancy | Max people per hour | ✅ |
| SOP Violations (24h) | Trigger history | ✅ |
| Safety Incidents | Fire/Smoke/Violence count | ✅ |
| 5L Testing | `equipment.testing` status | ✅ |
| Equipment Secure | DU/Manhole status | ✅ |
| Vehicle Conversion | Vehicles served % | ✅ |
| SOP Compliance Radar | Scores visualization | ✅ |
| Cleanliness Score | `environment.cleanliness.score` | ✅ |
| Objects Detected | Detection counts | ✅ |
| Object Count Over Time | Time series | ✅ |

---

## 🆕 NEW KPI Cards - From `prompt2.py` AI Deepdive

### 1. **Staff Uniform Compliance**
```
┌─────────────────────────────────────────┐
│ 👔 Uniform Compliance                   │
│                                         │
│ Score: 4/5                              │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ ████████░░                              │
│                                         │
│ 👥 Staff Visible:    3                  │
│ ✅ Compliant:        2                  │
│ ⚠️ Violations:       1                  │
│                                         │
│ Issues:                                 │
│ • 1 staff missing cap                   │
└─────────────────────────────────────────┘
```
**Data Source:**
```json
"people": {
  "staff": {
    "count": 2,
    "uniform_status": "1 compliant, 1 missing cap"
  }
}
```

---

### 2. **Vehicle License Plate Tracker**
```
┌─────────────────────────────────────────┐
│ 🚗 License Plates Captured              │
│                                         │
│ Today: 127 plates                       │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                         │
│ Recent Detections:                      │
│ • GJ05AB7890 (Car-White) @ Pump 1       │
│ • GJ01XX1234 (Motorcycle) @ Pump 2      │
│ • MH12CD5678 (Truck) @ Pump 3           │
│                                         │
│ 📈 Readable: 89%  |  Partial: 8%        │
│ ❌ Not Visible: 3%                      │
└─────────────────────────────────────────┘
```
**Data Source:**
```json
"vehicles": {
  "details": [
    {"type": "car", "color": "white", "number_plate": "GJ05AB7890", "location": "pump 1"}
  ]
}
```

---

### 3. **Greeting & Zero Display Tracker**
```
┌─────────────────────────────────────────┐
│ 🙏 Customer Service                     │
│                                         │
│ Greetings Observed:     ████████░░ 78%  │
│ Zero Display Shown:     ██████░░░░ 62%  │
│                                         │
│ Last Hour Performance:                  │
│ • Greeting instances: 15/20             │
│ • Zero shown: 12/19                     │
│                                         │
│ 💡 Tip: Remind staff on zero display    │
└─────────────────────────────────────────┘
```
**Data Source:**
```json
"compliance_checks": {
  "greeting": {"observed": true, "details": "staff greeting customer at pump 2"},
  "zero_display": {"observed": false, "details": "not visible in frame"}
}
```

---

### 4. **Garbage & Clutter Monitor**
```
┌─────────────────────────────────────────┐
│ 🗑️ Cleanliness Issues                   │
│                                         │
│ Garbage Items:          4               │
│ Clutter Items:          2               │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                         │
│ 🗑️ Garbage Found:                       │
│ • Plastic bottle near bin               │
│ • Paper cups x3                         │
│                                         │
│ 🪑 Clutter Found:                       │
│ • Plastic chair blocking path           │
│ • Empty bucket                          │
│                                         │
│ 📍 Locations: Pump 2, Island 1          │
└─────────────────────────────────────────┘
```
**Data Source:**
```json
"environment": {
  "garbage": {"found": true, "items": ["plastic bottle near bin", "paper cups x3"]},
  "clutter": {"found": true, "items": ["plastic chair blocking path"]}
}
```

---

### 5. **Air Station Status**
```
┌─────────────────────────────────────────┐
│ 🌬️ Air Station                          │
│                                         │
│ Status:           🟢 MANNED             │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                         │
│ Current: 1 vehicle                      │
│ Today: 34 vehicles served               │
│                                         │
│ 📊 Manned Hours (24h):                  │
│ ███████████░░░░░░░░░ 78%               │
│                                         │
│ ⚠️ Last unmanned: 11:30 AM              │
└─────────────────────────────────────────┘
```
**Data Source:**
```json
"equipment": {
  "air_station": {"status": "manned", "vehicle_present": true}
}
```

---

### 6. **FSM Presence Tracker**
```
┌─────────────────────────────────────────┐
│ 👨‍💼 FSM (Fuel Station Manager)          │
│                                         │
│ Status: 🟢 PRESENT                      │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                         │
│ Current Location: Office               │
│ Last Seen on Floor: 5 min ago           │
│                                         │
│ Today's Activity:                       │
│ • Floor Rounds: 8                       │
│ • Customer Assistance: 3                │
│ • Staff Training: 1                     │
│                                         │
│ Shift: 06:00 - 14:00                    │
└─────────────────────────────────────────┘
```
**Data Source:**
- Face recognition + role assignment
- `recognitions` array from event data

---

### 7. **Dispenser Unit (DU) Status**
```
┌─────────────────────────────────────────┐
│ ⛽ Dispenser Units                       │
│                                         │
│ Total DUs: 6    Active: 4               │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                         │
│ DU Status:                              │
│ • DU 1: ✅ CLOSED (Idle)                │
│ • DU 2: ⛽ IN USE (Refueling)           │
│ • DU 3: ⛽ IN USE (Refueling)           │
│ • DU 4: ✅ CLOSED (Idle)                │
│ • DU 5: ⚠️ COVER OPEN                   │
│ • DU 6: 🔧 MAINTENANCE                  │
│                                         │
│ 📊 Covers Open Alerts (24h): 3          │
└─────────────────────────────────────────┘
```
**Data Source:**
```json
"equipment": {
  "dispensers": {"count": 2, "status": "all closed and operational"}
},
"safety_checks": {
  "du_open": {"detected": true}
}
```

---

### 8. **Vehicle Queue & Wait Time**
```
┌─────────────────────────────────────────┐
│ 🚦 Queue Status                         │
│                                         │
│ Vehicles Waiting: 3                     │
│ Avg Wait Time: 4.2 min                  │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                         │
│ By Pump:                                │
│ • Pump 1: 🚗 1 waiting                  │
│ • Pump 2: ∅ Clear                       │
│ • Pump 3: 🚗🚗 2 waiting                │
│                                         │
│ 📈 Peak Today: 6 vehicles (12:30 PM)    │
│ 💡 Suggest: Open Pump 4                 │
└─────────────────────────────────────────┘
```
**Data Source:**
- Vehicle detection + trajectory tracking
- Pump proximity analysis

---

### 9. **Oil Spill Detection**
```
┌─────────────────────────────────────────┐
│ 🛢️ Spill Detection                      │
│                                         │
│ Status: ⚠️ 1 SPILL DETECTED             │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                         │
│ Current Issues:                         │
│ • Minor oil stain near Pump 1           │
│                                         │
│ Resolution Time:                        │
│ ⏱️ Detected: 10 min ago                 │
│ ⏱️ Avg Cleanup: 15 min                  │
│                                         │
│ 📊 Spills Today: 2                      │
│ 📊 Spills (Week): 8                     │
└─────────────────────────────────────────┘
```
**Data Source:**
```json
"environment": {
  "cleanliness": {"score": 4, "issues": ["minor oil stain near pump 1"]}
}
```

---

### 10. **Plastic Fill Detection**
```
┌─────────────────────────────────────────┐
│ 🚨 Plastic Fill Alert                   │
│                                         │
│ Status: 🔴 VIOLATION DETECTED           │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                         │
│ Location: Pump 2                        │
│ Time: 14:32 PM                          │
│                                         │
│ Details:                                │
│ • Plastic container detected            │
│ • Nozzle in use                         │
│ • No vehicle present                    │
│                                         │
│ 📊 Violations Today: 1                  │
│ 📊 Violations (Month): 7                │
└─────────────────────────────────────────┘
```
**Data Source:**
```json
"safety_checks": {
  "plastic_fill": {"detected": true}
}
```

---

### 11. **Cell Phone Usage Near Pump**
```
┌─────────────────────────────────────────┐
│ 📱 Cell Phone Detection                 │
│                                         │
│ Today: 12 incidents                     │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                         │
│ By Zone:                                │
│ • Pump Area: 8 (⚠️ High Risk)           │
│ • Shop Area: 3 (OK)                     │
│ • Parking: 1 (OK)                       │
│                                         │
│ Most Recent:                            │
│ 📍 Pump 3 - 5:42 PM                     │
│ 👤 Customer on phone while refueling    │
│                                         │
│ 📊 Trend: ↗️ +15% vs last week          │
└─────────────────────────────────────────┘
```
**Data Source:**
- YOLO class: `cell_phone(17)`
- Proximity to nozzle/pump detection

---

### 12. **Manhole Status**
```
┌─────────────────────────────────────────┐
│ 🕳️ Manhole Status                       │
│                                         │
│ Status: 🟢 ALL COVERED                  │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                         │
│ Manholes Monitored: 4                   │
│ • Tank Access 1: ✅ Closed              │
│ • Tank Access 2: ✅ Closed              │
│ • Drainage 1: ✅ Covered                │
│ • Drainage 2: ✅ Covered                │
│                                         │
│ 📊 Open Events (Week): 2                │
│ ⏱️ Avg Open Duration: 45 min            │
└─────────────────────────────────────────┘
```
**Data Source:**
```json
"safety_checks": {
  "manhole": {"detected": false, "status": "cover closed"}
}
```

---

### 13. **Violence/Fight Detection**
```
┌─────────────────────────────────────────┐
│ ⚠️ Altercation Monitor                  │
│                                         │
│ Status: 🟢 CLEAR                        │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                         │
│ Incidents (30 days): 2                  │
│                                         │
│ Recent Events:                          │
│ • Jan 5 - Verbal altercation @ Pump 2   │
│   (Resolved, no escalation)             │
│ • Dec 28 - Customer dispute @ Shop      │
│   (Staff intervened)                    │
│                                         │
│ 👮 Security Response Time: 2.3 min      │
└─────────────────────────────────────────┘
```
**Data Source:**
- YOLO class: `violence(7)`
- Pose estimation for aggressive behavior

---

### 14. **AI Confidence Score**
```
┌─────────────────────────────────────────┐
│ 🤖 AI Analysis Quality                  │
│                                         │
│ Avg Confidence: 87.3%                   │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ █████████░                              │
│                                         │
│ By Category:                            │
│ • People Detection: 92%                 │
│ • Vehicle Detection: 89%                │
│ • Safety Events: 84%                    │
│ • Compliance: 81%                       │
│                                         │
│ 📊 False Positives (24h): 3             │
│ 📊 False Negative Rate: 2.1%            │
└─────────────────────────────────────────┘
```
**Data Source:**
- Detection confidence from YOLO
- AI validation results

---

### 15. **Compliance Score Summary**
```
┌──────────────────────────────────────────┐
│ 📋 Today's Compliance Summary            │
│                                          │
│ Overall: 8.2/10                          │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ ████████░░                               │
│                                          │
│ Breakdown:                               │
│ • Uniform:     █████░░░░░ 4/5            │
│ • Cleanliness: █████████░ 5/5            │
│ • Safety:      █████████░ 5/5            │
│ • Greeting:    █████████░ ✓              │
│ • Zero Display:██████░░░░ 60%            │
│                                          │
│ 📈 vs Yesterday: ↗️ +0.5                 │
│ 🎯 Target: 9.0/10                        │
└──────────────────────────────────────────┘
```
**Data Source:**
```json
"ai_overview": {
  "compliance_score": "8/10"
},
"kpi_scores": {
  "uniform_score": 4,
  "cleanliness_score": 5,
  "safety_score": 5
}
```

---

## 📊 KPI Cards by Category

### Safety Cards (Red/Critical)
| Card | Priority | Data Field |
|------|----------|------------|
| Smoking Detection | 🔴 Critical | `safety_checks.smoking` |
| Fire Detection | 🔴 Critical | `safety_checks.fire` |
| Plastic Fill | 🔴 Critical | `safety_checks.plastic_fill` |
| Violence/Fight | 🔴 Critical | `triggers` |
| Cell Phone at Pump | 🟡 Warning | YOLO `cell_phone` |

### Equipment Cards (Yellow/Warning)
| Card | Priority | Data Field |
|------|----------|------------|
| DU Cover Status | 🟡 Warning | `safety_checks.du_open` |
| Manhole Status | 🟡 Warning | `safety_checks.manhole` |
| Air Station Status | 🟡 Warning | `equipment.air_station` |
| Dispenser Status | 🟢 Info | `equipment.dispensers` |

### Compliance Cards (Green/Operational)
| Card | Priority | Data Field |
|------|----------|------------|
| Uniform Score | 🟢 Info | `people.staff.uniform_status` |
| Greeting Tracker | 🟢 Info | `compliance_checks.greeting` |
| Zero Display | 🟢 Info | `compliance_checks.zero_display` |
| Cleanliness Score | 🟢 Info | `environment.cleanliness` |
| Garbage/Clutter | 🟢 Info | `environment.garbage/clutter` |

### Operational Cards (Blue/Info)
| Card | Priority | Data Field |
|------|----------|------------|
| Vehicle Count | 🔵 Info | `vehicles.count` |
| License Plates | 🔵 Info | `vehicles.details[].number_plate` |
| FSM Presence | 🔵 Info | Face recognition |
| Queue Status | 🔵 Info | Vehicle tracking |
| Staff Count | 🔵 Info | `people.staff.count` |

---

## 🔗 JSON Field → Card Mapping

```javascript
// From prompt2.py AI_INFO response

{
  "ai_overview": {
    "scene_summary"     → Header text for all cards
    "safety_status"     → Safety status badge (CLEAR/WARNING/CRITICAL)
    "compliance_score"  → Compliance Score Card
    "issues_found"      → Issues counter badge
  },
  
  "ai_deepdive": {
    "vehicles.count"                → Vehicle Count Card
    "vehicles.details[].number_plate" → License Plate Tracker Card
    "people.staff.count"            → Staff Count Card
    "people.staff.uniform_status"   → Uniform Compliance Card
    "equipment.dispensers"          → DU Status Card
    "equipment.air_station"         → Air Station Card
    "environment.cleanliness"       → Cleanliness Score Card
    "environment.garbage"           → Garbage Monitor Card
    "environment.clutter"           → Clutter Monitor Card
    "safety_checks.smoking"         → Smoking Alert Card
    "safety_checks.fire"            → Fire Alert Card
    "safety_checks.plastic_fill"    → Plastic Fill Card
    "safety_checks.du_open"         → DU Cover Status Card
    "safety_checks.manhole"         → Manhole Status Card
    "compliance_checks.greeting"    → Greeting Tracker Card
    "compliance_checks.zero_display" → Zero Display Card
  }
}
```

---

## 🚀 Implementation Priority

### Phase 1 - Quick Wins (Use Existing Data)
1. ✅ Uniform Compliance Score Card
2. ✅ Garbage/Clutter Monitor Card
3. ✅ Greeting Tracker Card
4. ✅ Zero Display Card
5. ✅ DU Status Card

### Phase 2 - Enhanced Cards (Needs Backend Changes)
1. 🔄 License Plate Tracker (needs OCR extraction)
2. 🔄 Air Station Status (needs persistent tracking)
3. 🔄 FSM Presence (needs face recognition integration)
4. 🔄 Queue Wait Time (needs vehicle trajectory)

### Phase 3 - Advanced Analytics
1. 📊 Compliance Trends (historical)
2. 📊 Peak Hour Analysis
3. 📊 Staff Performance Leaderboard
4. 📊 Camera Health Monitor

---

## 📝 Backend Changes Required

### 1. Add to `events.py` for persistence:
```python
ai_insights = {
    "uniform_score": ai_result.get("uniform_score"),
    "cleanliness_score": ai_result.get("cleanliness_score"),
    "safety_score": ai_result.get("safety_score"),
    "greeting_observed": ai_result.get("ai_deepdive", {}).get("compliance_checks", {}).get("greeting", {}).get("observed"),
    "zero_display_observed": ai_result.get("ai_deepdive", {}).get("compliance_checks", {}).get("zero_display", {}).get("observed"),
    "garbage_items": ai_result.get("ai_deepdive", {}).get("environment", {}).get("garbage", {}).get("items", []),
    "clutter_items": ai_result.get("ai_deepdive", {}).get("environment", {}).get("clutter", {}).get("items", []),
    "vehicles": ai_result.get("ai_deepdive", {}).get("vehicles", {}),
}
```

### 2. New API Endpoints Needed:
```
GET /api/v1/kpi/uniform-score?site_id=...&date=...
GET /api/v1/kpi/cleanliness-score?site_id=...&date=...
GET /api/v1/kpi/greeting-stats?site_id=...&date=...
GET /api/v1/kpi/zero-display-stats?site_id=...&date=...
GET /api/v1/kpi/license-plates?site_id=...&date=...
GET /api/v1/kpi/garbage-items?site_id=...&date=...
```

---

> [!TIP]
> **Quick Win:** Start with the **Compliance Score Summary** card - it aggregates multiple existing scores into one visual!

> [!IMPORTANT]
> **Most Valuable Cards:** License Plate Tracker and Queue Status provide highest business value for fuel station management.

---

## 🎨 Recommended Visualizations for Customer Appeal

### Visual Design Principles

1. **Don't overwhelm** - Show 4-6 KPIs max on first view
2. **Use visual hierarchy** - Most critical KPIs at top/left
3. **Color-code by status** - Green/Yellow/Red for quick scanning
4. **Animate key values** - Subtle count-up animations draw attention
5. **Show context** - Always include trend (vs yesterday) or target

---

### 📊 Chart Types by KPI Category

#### 1. **Safety Monitoring** — Use Status Badges & Alert Cards

| KPI | Recommended Visualization | Why It Works |
|-----|---------------------------|--------------|
| Fire/Smoke | **Large Status Badge** (🟢 CLEAR / 🔴 ALERT) | Instant recognition, no interpretation needed |
| Smoking Detection | **Status Badge + Incident Counter** | Shows current + historical context |
| Plastic Fill | **Alert Card with Location Map** | Shows WHERE the issue is |
| Cell Phone Usage | **Heatmap by Zone** | Visual hotspots drive action |

**Example Design:**
```
┌──────────────────────────────────────────────────────┐
│  🔥 FIRE/SMOKE       🚬 SMOKING        📱 CELL PHONE │
│                                                      │
│   🟢 CLEAR           🟢 CLEAR          ⚠️ 3 TODAY    │
│   ━━━━━━━━           ━━━━━━━━          ━━━━━━━━━━━━  │
│   0 incidents        0 incidents       Pump Area: 8  │
│   0 false alarms     Last: 3 days ago  Shop: 3       │
└──────────────────────────────────────────────────────┘
```

---

#### 2. **Compliance Scores** — Use Radial Gauges & Progress Bars

| KPI | Recommended Visualization | Why It Works |
|-----|---------------------------|--------------|
| Overall Compliance | **Radial Gauge (0-10)** | Executive summary at a glance |
| Uniform Compliance | **Horizontal Progress Bar (x/5)** | Simple ratio visualization |
| Greeting Rate | **Animated % Counter + Progress Ring** | Shows improvement opportunity |
| Zero Display | **Progress Bar with Target Line** | Shows gap to goal |

**Example Design:**
```
┌────────────────────────────────────────────────────────────┐
│                    COMPLIANCE OVERVIEW                      │
│                                                            │
│        ╭───────────╮                                       │
│       ╱   8.2/10    ╲    Uniform    ████████░░ 4/5         │
│      │   ████████   │    Clean      ██████████ 5/5         │
│      │   ████████   │    Safety     ██████████ 5/5         │
│       ╲   GOOD      ╱    Greeting   ████████░░ 78%         │
│        ╰───────────╯     Zero Disp  ██████░░░░ 62% ⚠️      │
│                                     ────────── Target: 80%  │
│         +0.5 vs yesterday                                   │
└────────────────────────────────────────────────────────────┘
```

---

#### 3. **Real-Time Operations** — Use Live Cards with Timers

| KPI | Recommended Visualization | Why It Works |
|-----|---------------------------|--------------|
| Pump Status | **Live Status Cards with Timers** | Shows activity in real-time |
| Queue Status | **Pump Grid with Wait Indicators** | Spatial awareness |
| Air Station | **Status Badge + Activity Counter** | Simple boolean + context |
| FSM Presence | **Profile Card with Location** | Humanizes the data |

**Example Design:**
```
┌─────────────────────────────────────────────────────────────┐
│                    LIVE OPERATIONS                          │
│                                                             │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │ PUMP 1  │  │ PUMP 2  │  │ PUMP 3  │  │ PUMP 4  │        │
│  │ ⛽ BUSY │  │ ⛽ BUSY │  │ ○ IDLE  │  │ ⏳ 1 Q  │        │
│  │ 02:34   │  │ 01:12   │  │         │  │ ~3 min  │        │
│  │ GJ05AB  │  │ GJ01XX  │  │ 4m ago  │  │ Waiting │        │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘        │
│                                                             │
│  Avg service: 3.2 min                Peak hour: 12-1 PM    │
└─────────────────────────────────────────────────────────────┘
```

---

#### 4. **Staff Performance** — Use Leaderboards & Profile Cards

| KPI | Recommended Visualization | Why It Works |
|-----|---------------------------|--------------|
| Staff List | **Profile Cards with Avatar** | Personal, not just numbers |
| Vehicles Served | **Leaderboard with Bar Chart** | Gamification drives performance |
| Uniform Status | **Badge on Profile (✓/⚠️)** | Quick compliance scan |
| Greeting Rate | **Inline Progress Bar per Staff** | Compare performance |

**Example Design:**
```
┌────────────────────────────────────────────────────────────┐
│                    STAFF PERFORMANCE                        │
│                                                            │
│  ┌──────┐  Ramesh Kumar         32 served  ████████████████│
│  │  RK  │  Pump Operator        Uniform ✓  Greeting 85%    │
│  └──────┘                                                  │
│                                                            │
│  ┌──────┐  Suresh Patel         28 served  █████████████░░░│
│  │  SP  │  Pump Operator        ⚠️ No cap  Greeting 70%    │
│  └──────┘                                                  │
│                                                            │
│  ┌──────┐  Amit Joshi           @Office    FSM on duty     │
│  │  AJ  │  Station Manager      Uniform ✓  8 floor rounds  │
│  └──────┘                                                  │
└────────────────────────────────────────────────────────────┘
```

---

#### 5. **Vehicle & Transaction Data** — Use Tables & Lists

| KPI | Recommended Visualization | Why It Works |
|-----|---------------------------|--------------|
| License Plates | **Scrolling List with Monospace Plates** | Professional, easy to scan |
| Fuel Transactions | **Data Table with Filters** | Detailed analysis possible |
| Vehicle Type Mix | **Donut Chart** | Quick category breakdown |
| Hourly Traffic | **Area/Line Chart** | Shows patterns over time |

**Example Design:**
```
┌─────────────────────────────────────────────────────────────┐
│  VEHICLE OVERVIEW                                           │
│                                                             │
│  ┌─────────────┐                                            │
│  │  ╭───╮      │   156 Vehicles Today (+8%)                │
│  │  │Car│ 57%  │   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━        │
│  │  ╰───╯      │                                            │
│  │  🏍️ 27%     │   Recent Plates:                          │
│  │  🚛 11%     │   GJ05AB7890  White Swift    Pump 1  2m   │
│  │  🛺 5%      │   GJ01XX1234  Red Activa     Pump 2  8m   │
│  └─────────────┘   MH12CD5678  Blue Truck     Pump 3  15m  │
│                                                             │
│  Plate Recognition: 94% accurate                            │
└─────────────────────────────────────────────────────────────┘
```

---

#### 6. **Trend Analysis** — Use Sparklines & Mini Charts

| KPI | Recommended Visualization | Why It Works |
|-----|---------------------------|--------------|
| Hourly Traffic | **Area Chart with Gradient** | Shows flow pattern |
| Compliance Trend | **Sparkline** (compact line chart) | Fits in small spaces |
| Daily Revenue | **Bar Chart by Day** | Easy comparison |
| Peak Occupancy | **Heatmap by Hour** | Pattern recognition |

**Example Sparkline Usage:**
```
┌────────────────────────────────────────────────────────────┐
│  KPI              TODAY      TREND (7 days)                 │
│  ───────────────────────────────────────────────────────── │
│  Vehicles         156        ▁▃▅▆▇█ ↗️ +8%                 │
│  Compliance       8.2        ▃▄▅▆▆█ ↗️ +0.5                │
│  Safety Score     5/5        █████████ ━ Stable            │
│  Greeting Rate    78%        ▅▆▆▇▇█ ↗️ +12%                │
│  Revenue          ₹2.3L      ▃▄▅▆▇█ ↗️ +12%                │
└────────────────────────────────────────────────────────────┘
```

---

### 🎯 High-Impact Visualization Combos

#### Executive Summary View (9 Cards)
```
┌─────────────────────────────────────────────────────────────────┐
│  TODAY'S REVENUE     VEHICLES SERVED    COMPLIANCE     ALERTS  │
│  ₹2,34,500 ↗️+12%    156 ↗️+8%          8.2/10 ↗️       3 ⚠️   │
└─────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────┐
│  LIVE OPERATIONS                   │  SAFETY & COMPLIANCE       │
│  ┌────┐┌────┐┌────┐┌────┐         │  🔥 Clear  🚬 Clear        │
│  │P1 ⛽││P2 ⛽││P3 ○ ││P4 ⏳│         │  📱 3 today ⛽ All closed │
│  └────┘└────┘└────┘└────┘         │  🕳️ Covered 🧹 5/5         │
└─────────────────────────────────────────────────────────────────┘
┌────────────────────────────────┐  ┌──────────────────────────────┐
│  ACTION ITEMS (3)              │  │  RECENT VEHICLES              │
│  ⚠️ Uniform violation - SP     │  │  GJ05AB7890  Swift   2m ago  │
│  ⚠️ Mobile phone at Pump 1     │  │  GJ01XX1234  Activa  8m ago  │
│  ○ Zero display below target   │  │  MH12CD5678  Truck   15m ago │
└────────────────────────────────┘  └──────────────────────────────┘
```

---

### 🌟 Premium Visualization Components

#### 1. Radial Compliance Gauge (Hero Card)
```
         ╭─────────────╮
        ╱               ╲
       │    8.2 / 10     │
       │   ▓▓▓▓▓▓▓▓░░    │
       │     GOOD        │
        ╲               ╱
         ╰─────────────╯
         +0.5 vs yesterday
```
**Use for:** Overall compliance score - the ONE number executives care about

---

#### 2. Real-Time Pump Status Grid
```
  ⛽       ⛽       ○        ⏳
 PUMP 1   PUMP 2   PUMP 3   PUMP 4
 02:34    01:12    idle     1 queue
 GJ05AB   GJ01XX            ~3 min
```
**Use for:** Operations overview - shows activity density

---

#### 3. Issue Priority Queue (Kanban Style)
```
 🔴 CRITICAL (1)        🟡 WARNING (2)         🟢 INFO (1)
 ─────────────          ──────────────         ────────────
 Mobile at pump         Uniform violation      Zero display
 └─ Pump 1, 2m ago      └─ Suresh P.           below target
                        Cell phone x3
```
**Use for:** Actionable insights - staff knows what to fix

---

#### 4. License Plate Ticker (Live Feed)
```
 🚗 GJ05AB7890 → Pump 1 → 2m ago → Ramesh K.
 🏍️ GJ01XX1234 → Pump 2 → 8m ago → Suresh P.
 🚛 MH12CD5678 → Pump 3 → 15m ago → Ramesh K.
```
**Use for:** Activity feed - shows the station is "alive"

---

#### 5. Hourly Traffic Heatmap
```
      6AM  7   8   9   10  11  12  1PM  2   3   4   5   6
     ─────────────────────────────────────────────────────
 Mon  ░░  ░▒  ▒▓  ▓█  ▒▓  ▓█  ██  ██  ▓█  ▒▓  ▓█  ██  ▓█
 Tue  ░░  ░▒  ▒▓  ▓█  ▓█  ▓█  ██  ██  ▓█  ▓█  ▓█  ██  ▓█
 Wed  ░░  ░▒  ▒▓  ▓█  ▒▓  ▓█  ██  ██  ▓█  ▒▓  ▓█  ██  ▓█
```
**Use for:** Pattern analysis - identify rush hours

---

### 🎨 Color Recommendations

| Status | Color | Hex | Usage |
|--------|-------|-----|-------|
| Critical | Red | `#dc2626` | Fire, smoke, violence alerts |
| Warning | Amber | `#d97706` | Compliance issues, mobile phone |
| Good | Green | `#22c55e` | All clear, targets met |
| Info | Teal | `#14b8a6` | Neutral data, counters |
| Muted | Gray | `#737373` | Disabled, historical |

---

### 📱 Responsive Layout Priorities

| Screen Size | Show First | Secondary | Hide |
|-------------|------------|-----------|------|
| **Mobile** | Compliance score, Safety status, Alerts | Recent vehicles, Staff list | Charts, heatmaps |
| **Tablet** | + Live operations, Charts | + Full vehicle list | Detailed analytics |
| **Desktop** | Full dashboard | All cards | Nothing |

---

> [!TIP]
> **Customer Impact:** Start with the **Radial Compliance Gauge** + **Live Operations Grid** + **Issue Queue** combo. This gives executives the "at a glance" view while staff gets actionable items.

> [!IMPORTANT]
> **Animation:** Add subtle count-up animations (0 → 156) on page load. This makes data feel "live" and increases perceived value of the real-time monitoring.

