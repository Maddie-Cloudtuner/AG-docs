# Roboi Codebase Analysis & Recommendations

> **Created:** 2026-01-09  
> **Purpose:** Frontend UI improvements, false trigger locations, and AI Insights recommendations

---

## 📁 Codebase Structure Overview

```
roboi-main/
├── roboi-backend/           # FastAPI Backend
│   ├── app/
│   │   ├── api/endpoints/   # API routes
│   │   │   ├── events.py    # Event ingestion (ClickHouse, WebSocket, Telegram)
│   │   │   ├── sites.py     # Analytics endpoints (peak-occupancy, heatmap, detections)
│   │   │   ├── telegram.py  # Alert formatting & sending
│   │   │   └── validation.py
│   │   ├── prompt/          # AI Prompt configurations
│   │   │   ├── prompt.py           # EVENT VALIDATION (valid vs false positive)
│   │   │   └── prompt_ai_info.py   # KPI ANALYSIS (scores & insights)
│   │   └── services/
│   │       ├── validation_service.py  # Gemini AI integration
│   │       └── telegram.py            # Telegram service
│   └── config.py
└── roboi-frontend/          # Next.js Frontend
    └── src/
        ├── components/
        │   ├── widgets/     # Dashboard widgets (alerts, charts, tables)
        │   └── charts/
        └── app/             # Page routes
```

---

## 🖼️ Current Frontend Screenshots

### Dashboard Overview
![Dashboard Overview](file:///C:/Users/LENOVO/.gemini/antigravity/brain/590734cf-623e-49e4-aa68-ae553deca998/uploaded_image_0_1767944980590.png)

### Analytics Charts
![Analytics Charts](file:///C:/Users/LENOVO/.gemini/antigravity/brain/590734cf-623e-49e4-aa68-ae553deca998/uploaded_image_1_1767944980590.png)

### Detection Log Table
![Detection Log](file:///C:/Users/LENOVO/.gemini/antigravity/brain/590734cf-623e-49e4-aa68-ae553deca998/uploaded_image_2_1767944980590.png)

### Alert Detail Modal
![Alert Detail Modal](file:///C:/Users/LENOVO/.gemini/antigravity/brain/590734cf-623e-49e4-aa68-ae553deca998/uploaded_image_3_1767944980590.png)

---

## 🎨 Frontend Improvement Suggestions

### 1. Dashboard Overview (Screenshot 1)

| Current Issue | Recommended Change |
|---------------|-------------------|
| **Stats cards are plain** | Add gradient backgrounds, mini sparkline trends, and comparison arrows (↑↓) |
| **Peak Occupancy shows "8"** | Show as "8/50" (current/threshold) with a micro progress ring |
| **Heatmap lacks context** | Add camera selector dropdown and time range inside the widget |
| **Recent Alerts list is dense** | Add subtle row hover effects and severity color coding on left border |
| **Employee Area label is static** | Make camera zones clickable to switch heatmap data |

### 2. Analytics Charts (Screenshot 2)

| Current Issue | Recommended Change |
|---------------|-------------------|
| **Objects Detected bar chart** | Convert to horizontal stacked bar or add icons per object type |
| **SOP Compliance radar** | Add baseline comparison (dotted line for "ideal" scores) |
| **Cleanliness Score line** | Add threshold line (e.g., red dashed at 60) + anomaly highlights |
| **Object Count Over Time** | Add legend toggle, zoom capability, and brush selection for date range |
| **No summary insight** | Add a one-liner AI insight card above charts: *"Car detections up 23% today"* |

### 3. Detection Log Table (Screenshot 3)

| Current Issue | Recommended Change |
|---------------|-------------------|
| **All rows look the same** | Add severity-colored left border (red=critical, yellow=warning, green=safe) |
| **Key Detections column** | Use colored chips/tags instead of plain text pills |
| **Confidence bars are small** | Make them thicker, add percentage label on hover |
| **No quick actions** | Add inline action buttons: 👁️ View | ✓ Triage | 🚫 Dismiss |
| **Type column shows only "METRIC"** | Use icons: 📊 Metric, 🚨 Event, 📍 Detection |

### 4. Alert Detail Modal (Screenshot 4)

| Current Issue | Recommended Change |
|---------------|-------------------|
| **AI Insights shows Lorem ipsum** | **Critical Fix!** Populate from `ai_insights` field (see section below) |
| **Evidence carousel lacks timeline** | Add timestamp overlay on each image |
| **No visual severity indicator** | Add pulsing red badge for CRITICAL alerts |
| **Actions at bottom** | Add "Escalate to Manager" and "Share to Telegram" buttons |
| **No context summary** | Add quick facts: Camera, Duration, Objects Detected count |

---

## 🔍 False Trigger Detection Locations

### Where to Check for **Peak Crowd Occupancy** False Triggers

| File | Location | What to Modify |
|------|----------|----------------|
| [sites.py](file:///c:/Users/LENOVO/Desktop/my_docs/AG/ROBOI/roboi-main/roboi-backend/app/api/endpoints/sites.py#L153-L183) | `get_peak_occupancy()` function | Add occupancy threshold comparison logic |
| [events.py](file:///c:/Users/LENOVO/Desktop/my_docs/AG/ROBOI/roboi-main/roboi-backend/app/api/endpoints/events.py#L131-L140) | Telegram alert trigger | Add crowd validation before sending alert |
| [prompt.py](file:///c:/Users/LENOVO/Desktop/my_docs/AG/ROBOI/roboi-main/roboi-backend/app/prompt/prompt.py#L17-L19) | `MOB_GATHERING` validation | Tune detection parameters |

#### Recommended Changes for Crowd False Triggers:

```python
# In sites.py - Add threshold validation
CROWD_THRESHOLD = 15  # Define per site

def is_genuine_crowd_alert(people_count, threshold=CROWD_THRESHOLD):
    """Filter out transient spikes (e.g., shift change)."""
    if people_count < threshold:
        return False
    # Add time-based validation (sustained for 5+ mins)
    return True
```

---

### Where to Check for **Fire Detection** False Triggers

| File | Location | What to Modify |
|------|----------|----------------|
| [prompt.py](file:///c:/Users/LENOVO/Desktop/my_docs/AG/ROBOI/roboi-main/roboi-backend/app/prompt/prompt.py#L67-L77) | **False Positive Example** | See existing fire detection error handling |
| [prompt.py](file:///c:/Users/LENOVO/Desktop/my_docs/AG/ROBOI/roboi-main/roboi-backend/app/prompt/prompt.py#L21-L26) | `FALSE POSITIVE CAUSES` | Documents known false trigger reasons |
| [validation_service.py](file:///c:/Users/LENOVO/Desktop/my_docs/AG/ROBOI/roboi-main/roboi-backend/app/services/validation_service.py#L243-L258) | `analyze_all_media()` | AI validation call to Gemini |

#### Current False Positive Logic (from `prompt.py`):

```python
FALSE POSITIVE CAUSES:
- Low confidence detection (<50%)
- Small bounding box (visual artifact)
- Vehicle exhaust mistaken for smoke
- Authorized maintenance work
```

#### Example False Positive Response Pattern:

```json
{
    "alert_valid": false,
    "verdict": "False Positive - Visual artifact misidentified as fire",
    "why_it_happened": "DETECTION ERROR: fire_detected at 40% confidence with 12x12px bounding box. Small detection indicates visual artifact (glare/reflection).",
    "recommendation": "TUNE DETECTION: Increase fire threshold to 60%. Ignore detections under 50x50px."
}
```

> [!IMPORTANT]
> **Backend Engineer Action:** Add pre-validation in `events.py` before Gemini call:
> ```python
> # Pre-filter obvious false triggers
> if trigger == "fire_detected" and confidence < 0.5 and bbox_area < 2500:
>     mark_as_false_positive(event)
>     return  # Skip expensive Gemini validation
> ```

---

## 🤖 AI Insights Recommendation for Snapshot View

### Current Problem

The **AI Insights** section in the Alert Detail Modal currently shows `null` or Lorem ipsum placeholder text. The actual rich data is being generated for Telegram but **not persisted to the frontend**.

### Telegram Response (What You Currently Get via Postman)

```
📊 AI KPI ANALYSIS
📸 Camera: d5
⏰ Time: 2026-01-08 12:07:59
━━━━━━━━━━━━━━━━━━━━━━━━
📈 Verdict: KPI Analysis - 7/10 compliance. 1 issue found.
📋 KPI SCORES:
  👔 Uniform:    █░░░░ 1/5
  🧹 Cleanliness: █████ 5/5
  🛡️ Safety:     █████ 5/5
📈 Utilization: 🔴 LOW
👥 Metrics:
  • People Detected: 1
  • Media Analyzed: 10
🚨 Alerts:
  ⚠️ No Uniformed Staff Visible
━━━━━━━━━━━━━━━━━━━━━━━━
🔬 AI OVERVIEW:
* Petrol pump premises during daylight hours. • Safety: CLEAR • Vehicles: 3 • Staff: 0
━━━━━━━━━━━━━━━━━━━━━━━━
🔬 AI DEEPDIVE:
* One white car (GJ-11MS4553) is parked in the foreground...
━━━━━━━━━━━━━━━━━━━━━━━━
💡 INSIGHTS:
No uniformed staff is visible at the pump. The premises appear clean with no safety concerns.
━━━━━━━━━━━━━━━━━━━━━━━━
🎯 Summary:
KPI: 7/10 | Uniform: 1/5 | Clean: 5/5 | Safety: 5/5 | No uniformed staff visible.
```

---

### Recommended JSON Structure for Backend to Populate `ai_insights`

Tell your backend engineer to populate the `ai_insights` field with a **structured JSON object** (not plain text):

```json
{
  "verdict": "KPI Analysis - 7/10 compliance. 1 issue found.",
  "kpi_scores": {
    "uniform": { "score": 1, "max": 5, "label": "Poor" },
    "cleanliness": { "score": 5, "max": 5, "label": "Excellent" },
    "safety": { "score": 5, "max": 5, "label": "Excellent" }
  },
  "utilization": "low",
  "metrics": {
    "people_detected": 1,
    "media_analyzed": 10,
    "vehicles": 3,
    "staff_visible": 0
  },
  "alerts": ["No Uniformed Staff Visible"],
  "overview": "Petrol pump premises during daylight hours. Safety: CLEAR. Vehicles: 3. Staff: 0 uniformed staff visible.",
  "deepdive": "One white car (GJ-11MS4553) is parked in the foreground. A white SUV is near the fuel pumps. A truck is visible in the background. One person, identified as a 'Stranger', is standing near the building.",
  "insights_summary": "No uniformed staff is visible at the pump. The premises appear clean with no safety concerns.",
  "tldr": "KPI: 7/10 | Uniform: 1/5 | Clean: 5/5 | Safety: 5/5 | No uniformed staff visible."
}
```

---

### Frontend Display Mockup for AI Insights

The frontend should render this as a **clean, scannable card**:

```
┌────────────────────────────────────────────────────┐
│ ✨ AI Insights                           7/10 KPI  │
├────────────────────────────────────────────────────┤
│ 📊 Scores:                                         │
│   👔 Uniform:    ████░░░░░░ 1/5                    │
│   🧹 Cleanliness: ██████████ 5/5                   │
│   🛡️ Safety:     ██████████ 5/5                   │
├────────────────────────────────────────────────────┤
│ 📋 Quick Facts:                                    │
│   • People: 1  • Vehicles: 3  • Staff: 0           │
│   • Utilization: LOW 🔴                            │
├────────────────────────────────────────────────────┤
│ ⚠️ Alerts:                                         │
│   • No Uniformed Staff Visible                     │
├────────────────────────────────────────────────────┤
│ 💬 Summary:                                        │
│ No uniformed staff visible. Premises clean with    │
│ no safety concerns.                                │
└────────────────────────────────────────────────────┘
```

---

### Backend Code Changes Required

#### 1. Modify `events.py` to store AI insights when processing events

```python
# In app/api/endpoints/events.py - After AI validation

ai_insights_json = json.dumps({
    "verdict": ai_result.get("verdict"),
    "kpi_scores": {
        "uniform": {"score": ai_result.get("uniform_score", 0), "max": 5},
        "cleanliness": {"score": ai_result.get("cleanliness_score", 0), "max": 5},
        "safety": {"score": ai_result.get("safety_score", 0), "max": 5}
    },
    "utilization": ai_result.get("utilization", "unknown"),
    "metrics": {
        "people_detected": ai_result.get("actual_people_count", 0),
        "media_analyzed": ai_result.get("media_analyzed", 0)
    },
    "alerts": ai_result.get("triggers", []),
    "insights_summary": ai_result.get("insights", ""),
    "tldr": ai_result.get("validation_summary", "")
})

# Store in ClickHouse
payload.ai_insights = ai_insights_json
```

#### 2. Modify `prompt_ai_info.py` to ensure all fields are returned

The current prompt already generates these fields. Ensure the AI returns:
- `uniform_score`, `cleanliness_score`, `safety_score` (1-5)
- `utilization` ("low"/"medium"/"high")
- `insights` (1-2 sentence summary)
- `triggers` (array of issues)
- `validation_summary` (TL;DR line)

---

## ✅ Action Items Summary

| Priority | Task | Owner | File(s) |
|----------|------|-------|---------|
| 🔴 High | Fix AI Insights null value | Backend | `events.py`, `sites.py` |
| 🔴 High | Add fire false positive pre-filter | Backend | `events.py` |
| 🟡 Medium | Add crowd threshold validation | Backend | `sites.py` |
| 🟡 Medium | Parse & display AI Insights JSON | Frontend | Alert Modal component |
| 🟢 Low | Apply UI improvements from table above | Frontend | Various widgets |

---

## 📚 Key Files Reference

| Purpose | File Path |
|---------|-----------|
| Event Validation Prompt | [prompt.py](file:///c:/Users/LENOVO/Desktop/my_docs/AG/ROBOI/roboi-main/roboi-backend/app/prompt/prompt.py) |
| KPI Analysis Prompt | [prompt_ai_info.py](file:///c:/Users/LENOVO/Desktop/my_docs/AG/ROBOI/roboi-main/roboi-backend/app/prompt/prompt_ai_info.py) |
| AI Validation Service | [validation_service.py](file:///c:/Users/LENOVO/Desktop/my_docs/AG/ROBOI/roboi-main/roboi-backend/app/services/validation_service.py) |
| Peak Occupancy API | [sites.py](file:///c:/Users/LENOVO/Desktop/my_docs/AG/ROBOI/roboi-main/roboi-backend/app/api/endpoints/sites.py) |
| Event Ingestion | [events.py](file:///c:/Users/LENOVO/Desktop/my_docs/AG/ROBOI/roboi-main/roboi-backend/app/api/endpoints/events.py) |
| Telegram Formatting | [telegram.py](file:///c:/Users/LENOVO/Desktop/my_docs/AG/ROBOI/roboi-main/roboi-backend/app/api/endpoints/telegram.py) |
