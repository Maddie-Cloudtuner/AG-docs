# InvEye KPIs: Employee Tracking & Retail Store Analytics

## Table of Contents
1. [Employee Tracking KPIs](#employee-tracking-kpis)
2. [Retail Store KPIs](#retail-store-kpis)
3. [Dashboard Design Guidelines](#dashboard-design-guidelines)
4. [AI Detection Models Required](#ai-detection-models-required)

---

## Employee Tracking KPIs

### 1. Attendance & Time Tracking

| KPI | Description | Measurement | Alert Threshold |
|:---|:---|:---|:---|
| **Clock In/Out Time** | Employee entry/exit detection | Facial recognition + time stamp | Late >15 min |
| **Total Working Hours** | Actual time on premises | Entry time - Exit time | <8 hours/day |
| **Break Duration** | Time spent in break areas | Time in designated zones | >60 min/day |
| **Overtime Hours** | Hours beyond shift | Total - scheduled shift | >2 hours/day |
| **Absenteeism Rate** | % of scheduled days missed | (Absent days / Total days) × 100 | >5% per month |
| **Punctuality Score** | On-time arrival rate | (On-time / Total days) × 100 | <90% |

**AI Models Required:**
- Face recognition for ID verification
- Zone detection for break areas
- Timestamp correlation

### 2. Productivity Metrics

| KPI | Description | Measurement | Alert Threshold |
|:---|:---|:---|:---|
| **Workstation Occupancy** | Time at designated workstation | Presence detection at desk | <70% of shift |
| **Idle Time** | Inactive periods at workstation | No movement detected >15 min | >20% of shift |
| **Movement Patterns** | Efficiency of movement | Path analysis, frequency | Erratic patterns |
| **Task Completion Rate** | Tasks done per hour | Count of completed actions | <80% target |
| **Multi-tasking Index** | Concurrent activities | overlapping activities detected | >3 tasks |
| **Focus Time** | Uninterrupted work periods | Segments without interruptions | <2 hours/day |

**AI Models Required:**
- Pose estimation for activity detection
- Object detection for task identification
- Movement tracking

### 3. Safety & Compliance

| KPI | Description | Measurement | Alert Threshold |
|:---|:---|:---|:---|
| **PPE Compliance Rate** | % time wearing required PPE | (PPE detected / Total time) × 100 | <95% |
| **Restricted Area Violations** | Unauthorized zone entry | Count of zone breaches | >0 per shift |
| **Safety Incident Count** | Near-miss or accidents | Fall detection, collision detection | >0 per week |
| **Posture Score** | Ergonomic compliance | Slouching, awkward positions | <70% good posture |
| **Fatigue Detection** | Signs of tiredness | Eye closure, head nodding | Detected during shift |
| **Social Distancing** | Maintaining safe distance | <6 feet for >30 sec | >5 violations/day |

**AI Models Required:**
- PPE classifier (helmet, gloves, mask, vest)
- Pose estimation for posture analysis
- Face mesh for fatigue detection
- Distance calculation between people

### 4. Behavior & Engagement

| KPI | Description | Measurement | Alert Threshold |
|:---|:---|:---|:---|
| **Collaboration Score** | Time in team interactions | Group detection, duration | <20% of shift |
| **Phone Usage** | Unauthorized phone use | Object detection: phone in hand | >10 min/hour |
| **Smoking Detection** | Smoking in prohibited areas | Smoking gesture + smoke detection | >0 occurrences |
| **Distraction Events** | Off-task behaviors | Sleeping, extended conversations | >3 per shift |
| **Training Compliance** | Attendance at safety briefings | Count of attendees vs roster | <100% |
| **Uniform Compliance** | Proper attire adherence | Uniform color/logo detection | <95% |

**AI Models Required:**
- Object detection (phone, cigarette)
- Gesture recognition
- Color/pattern recognition for uniforms

### 5. Health & Wellness

| KPI | Description | Measurement | Alert Threshold |
|:---|:---|:---|:---|
| **Temperature Screening** | Elevated body temp | Thermal camera integration | >99.5°F (37.5°C) |
| **Mask Compliance** | Face mask wearing | Face mask classifier | <95% in required areas |
| **Hand Hygiene** | Handwashing/sanitizing | Action detection at sinks | <5 times/shift |
| **Stress Indicators** | Signs of distress | Rapid movement, agitation | Detected patterns |
| **Medical Emergency** | Fall or unconsciousness | Fall detection algorithm | Immediate alert |

**AI Models Required:**
- Thermal imaging integration
- Face mask classifier
- Fall detection
- Action recognition (handwashing)

---

## Retail Store KPIs

### 1. Customer Footfall Analytics

| KPI | Description | Measurement | Alert Threshold |
|:---|:---|:---|:---|
| **Total Footfall** | Unique visitors per day | Person counting at entrance | <baseline -20% |
| **Hourly Traffic** | Visitors per hour | Time-binned people count | Peak hour identification |
| **Dwell Time** | Average time in store | Exit time - Entry time | <10 min (low engagement) |
| **Return Visitor Rate** | % of repeat customers | Face recognition (opt-in) | <30% |
| **Conversion Rate** | % visitors who purchase | (Transactions / Footfall) × 100 | <15% |
| **Entry vs Exit Count** | Tracking discrepancies | Entry count - Exit count | >5% mismatch |

**AI Models Required:**
- Person detection and counting
- Person re-identification
- Entry/exit line crossing detection

### 2. Queue & Checkout Analytics

| KPI | Description | Measurement | Alert Threshold |
|:---|:---|:---|:---|
| **Average Queue Length** | People waiting at checkout | Count in queue zone | >5 people |
| **Wait Time** | Time from queue join to service | Duration in queue zone | >5 minutes |
| **Checkout Abandonment** | Customers leaving queue | Exiting queue before service | >10% |
| **Cashier Efficiency** | Transactions per hour | Count of completed transactions | <20/hour |
| **Self-Checkout Usage** | % using self-service | Self-checkout / Total checkouts | <40% |
| **Queue Join Rate** | Customers joining vs leaving | Join count - Leave count | Negative trend |

**AI Models Required:**
- Queue zone detection
- Person tracking in queue
- Timestamp analysis

### 3. Product & Shelf Analytics

| KPI | Description | Measurement | Alert Threshold |
|:---|:---|:---|:---|
| **Out-of-Stock Events** | Empty shelf detection | Image comparison with baseline | >3 per day |
| **Shelf Attention Time** | Time spent at product category | Dwell in shelf zone | Category ranking |
| **Product Interaction** | Touch/pickup rate | Hand reaching detection | Low interaction items |
| **Planogram Compliance** | Shelf arrangement accuracy | Image match vs planogram | <90% |
| **Hot Zones** | High-traffic areas | Heatmap of movement | Zone optimization |
| **Cold Zones** | Low-traffic areas | Areas with <5% footfall | Rearrange products |

**AI Models Required:**
- Object detection for shelf monitoring
- Image comparison
- Hand detection and tracking
- Movement heatmap generation

### 4. Staff Performance

| KPI | Description | Measurement | Alert Threshold |
|:---|:---|:---|:---|
| **Staff Availability** | Employees on floor | Count of staff in customer areas | <2 during peak hours |
| **Customer Interaction** | Staff-customer engagements | Proximity detection >2 min | <10 per shift |
| **Service Response Time** | Time to assist customer | From customer signal to staff arrival | >2 minutes |
| **Uniform Compliance** | Staff in proper attire | Uniform detection (color, logo) | <100% |
| **Station Abandonment** | Unattended counters | No staff detected >5 min | Counter/demo areas |
| **Staff Efficiency** | Tasks completed per hour | Activity detection + counting | <10 tasks/hour |

**AI Models Required:**
- Person classification (staff vs customer)
- Proximity detection
- Activity recognition
- Uniform detection

### 5. Security & Loss Prevention

| KPI | Description | Measurement | Alert Threshold |
|:---|:---|:---|:---|
| **Suspicious Behavior** | Loitering, concealment | Dwell >10 min, hiding gestures | Immediate alert |
| **Shoplifting Events** | Theft detection | Product taken without checkout | Real-time alert |
| **Cart Abandonment** | Full carts left in store | Cart detection in aisles >15 min | Investigate |
| **Perimeter Breach** | After-hours intrusion | Motion detection when closed | Immediate alert |
| **Restricted Area Access** | Unauthorized entry | Person in staff-only zones | Real-time alert |
| **Vandalism Detection** | Property damage | Unusual actions near fixtures | Immediate alert |

**AI Models Required:**
- Behavior analysis (loitering, concealment)
- Object tracking (cart, products)
- Motion detection
- Zone violation detection

### 6. Store Operations

| KPI | Description | Measurement | Alert Threshold |
|:---|:---|:---|:---|
| **Cleaning Frequency** | Restroom/floor cleaning | Staff activity detection | <Every 2 hours |
| **Display Maintenance** | Displinary upkeep | Change detection on displays | Disarray detected |
| **Entrance Congestion** | Crowding at entry/exit | Density in entrance zone | >20 people |
| **Temperature Compliance** | Store climate control | Thermal monitoring | Outside 68-72°F |
| **Lighting Issues** | Inadequate lighting | Brightness analysis | <300 lux in aisles |
| **Spill Detection** | Floor hazards | Anomaly on floor surface | Immediate alert |

**AI Models Required:**
- Activity recognition
- Image change detection
- Density estimation
- Anomaly detection

### 7. Marketing & Merchandising

| KPI | Description | Measurement | Alert Threshold |
|:---|:---|:---|:---|
| **Promotion Engagement** | Time at promotional displays | Dwell in promo zones | <30 sec average |
| **Digital Signage Views** | Attention to screens | Gaze direction detection | <50% pass-by notice |
| **Gender Demographics** | Male/Female ratio | Gender classifier | Market insights |
| **Age Demographics** | Age group distribution | Age estimation | Target audience match |
| **Cart Fill Rate** | Products in cart | Object counting in cart | <5 items average |
| **Window Shopping** | Time at storefront | Dwell outside entrance | Conversion opportunity |

**AI Models Required:**
- Gaze tracking
- Gender and age classifier
- Object detection and counting
- Zone-based dwell time

---

## Dashboard Design Guidelines

### Layout Structure

```
┌─────────────────────────────────────────────────────┐
│  Header: InvEye Dashboard - [Location Name]        │
│  Date Range: [Selector] | Live Status: ●          │
└─────────────────────────────────────────────────────┘

┌───────────────┬───────────────┬───────────────────┐
│ EMPLOYEE TRACKING SECTION                          │
├───────────────────────────────────────────────────┤
│                                                    │
│  ┌─────────────────────────────────────────────┐ │
│  │  TODAY'S SUMMARY                            │ │
│  │  ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐  │ │
│  │  │  👤   │ │  ✓    │ │  ⚠️   │ │  🕐   │  │ │
│  │  │  145  │ │  92%  │ │   3   │ │ 7.2hr │  │ │
│  │  │Present│ │ComplianCe Alerts│  │Avg   │  │ │
│  │  └───────┘ └───────┘ └───────┘ └───────┘  │ │
│  └─────────────────────────────────────────────┘ │
│                                                    │
│  Real-time Alerts          PPE Compliance Trend   │
│  ┌──────────────────┐     ┌──────────────────┐   │
│  │ 🔴 Zone B        │     │     ___/\___     │   │
│  │ No PPE detected  │     │    /        \    │   │
│  │ 2 min ago        │     │___/          \___|   │
│  ├──────────────────┤     │ Mon Tue Wed Thu │   │
│  │ 🟡 Fatigue       │     │ 89% 92% 95% 92% │   │
│  │ Employee #234    │     └──────────────────┘   │
│  │ 5 min ago        │                             │
│  └──────────────────┘                             │
│                                                    │
│  Attendance Heatmap        Productivity Score     │
│  ┌──────────────────┐     ┌──────────────────┐   │
│  │ 6am [▓▓░░░░░░]   │     │      85/100      │   │
│  │ 9am [▓▓▓▓▓▓▓▓]   │     │   ████████░░     │   │
│  │12pm [▓▓▓▓▓▓░░]   │     │                  │   │
│  │ 3pm [▓▓▓▓▓▓▓░]   │     │ ↑ 3% vs last week│   │
│  │ 6pm [▓▓░░░░░░]   │     └──────────────────┘   │
│  └──────────────────┘                             │
└───────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────┐
│ RETAIL STORE SECTION                              │
├───────────────────────────────────────────────────┤
│                                                    │
│  ┌─────────────────────────────────────────────┐ │
│  │  STORE PERFORMANCE TODAY                    │ │
│  │  ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐  │ │
│  │  │  👥   │ │  🛒   │ │  ⏱️   │ │  💹   │  │ │
│  │  │ 1,247 │ │  18%  │ │ 23min │ │ +12% │  │ │
│  │  │Visitors Conversion Dwell  │  │Sales │  │ │
│  │  └───────┘ └───────┘ └───────┘ └───────┘  │ │
│  └─────────────────────────────────────────────┘ │
│                                                    │
│  Live Queue Status         Customer Flow Today   │
│  ┌──────────────────┐     ┌──────────────────┐   │
│  │ Checkout 1: 3👤  │     │     ╱╲           │   │
│  │ Wait: 2.5 min ✅ │     │    ╱  ╲          │   │
│  ├──────────────────┤     │   ╱    ╲    ╱╲   │   │
│  │ Checkout 2: 7👤  │     │  ╱      ╲  ╱  ╲  │   │
│  │ Wait: 6.2 min 🔴 │     │ ╱        ╲╱    ╲ │   │
│  ├──────────────────┤     │9am 11am 1pm 3pm 5pm  │
│  │ Self-serve: 2👤  │     └──────────────────┘   │
│  │ Wait: 0.8 min ✅ │                             │
│  └──────────────────┘                             │
│                                                    │
│  Store Heatmap             Top Categories         │
│  ┌──────────────────┐     ┌──────────────────┐   │
│  │ Entry  🔥🔥       │     │ 1. Electronics   │   │
│  │      🔥          │     │    ■■■■■■■ 28%   │   │
│  │ Aisles 🔥🔥      │     │ 2. Clothing      │   │
│  │      ❄️         │     │    ■■■■■ 22%     │   │
│  │ Checkout 🔥🔥🔥   │     │ 3. Groceries     │   │
│  │ Exit   🔥🔥       │     │    ■■■■ 18%      │   │
│  └──────────────────┘     └──────────────────┘   │
└───────────────────────────────────────────────────┘
```

### Color Scheme Recommendations

**Employee Tracking:**
- Primary: `#3B82F6` (Blue) - Professional, trust
- Success: `#10B981` (Green) - Compliance achieved
- Warning: `#F59E0B` (Amber) - Attention needed
- Danger: `#EF4444` (Red) - Immediate action
- Background: `#F9FAFB` (Light gray)

**Retail Store:**
- Primary: `#8B5CF6` (Purple) - Retail, premium
- Success: `#10B981` (Green) - Sales growth
- Warning: `#F59E0B` (Amber) - Queue buildup
- Danger: `#EF4444` (Red) - Security alert
- Background: `#F9FAFB` (Light gray)

### Component Types for Figma

#### 1. KPI Card
```
Component: kpi-card
Variants: employee, retail
States: normal, warning, critical

Auto Layout: Vertical
Padding: 20px
Corner Radius: 12px
Shadow: 0px 2px 8px rgba(0,0,0,0.08)

Elements:
- Icon (48×48px)
- Value (32px, Bold)
- Label (14px, Regular)
- Trend indicator (+/- %)
```

#### 2. Alert Banner
```
Component: alert-banner
Variants: info, warning, critical

Auto Layout: Horizontal
Padding: 16px
Corner Radius: 8px
Border: 2px solid (variant color)

Elements:
- Status icon (24×24px)
- Alert text (14px)
- Timestamp (12px, gray)
- Action button (optional)
```

#### 3. Line Chart
```
Component: trend-chart
Size: 300×180px

Elements:
- Grid lines (1px, #E5E7EB)
- Data line (3px, primary color)
- Data points (8px circles)
- X-axis labels (12px)
- Y-axis labels (12px)
- Legend
```

#### 4. Heatmap
```
Component: heatmap
Variants: time-based, spatial

Grid: 7×24 (weekly) or custom
Cell size: 20×20px
Color scale:
  - Cold: #DBEAFE (0-25%)
  - Warm: #FBBF24 (26-75%)
  - Hot: #EF4444 (76-100%)
```

#### 5. Progress Ring
```
Component: progress-ring
Size: 120×120px

Elements:
- Background circle (stroke: 8px, #E5E7EB)
- Progress arc (stroke: 8px, primary color)
- Center value (24px, Bold)
- Center label (12px)
```

#### 6. Live Status Indicator
```
Component: live-status
Variants: online, offline, warning

Elements:
- Animated dot (12px circle)
- Status text (14px)
- Last updated timestamp (12px, gray)

Animation: Pulse (2s infinite)
```

### Dashboard Screens Breakdown

#### Screen 1: Employee Overview
- Header with date range selector
- 4 summary KPI cards (attendance, compliance, alerts, hours)
- Real-time alert feed (right sidebar)
- PPE compliance trend chart
- Attendance heatmap (hourly)
- Productivity score gauge

#### Screen 2: Employee Details
- Individual employee cards with photo
- Detailed timeline (clock in/out, breaks)
- Safety violations list
- Productivity metrics (focus time, idle time)
- Historical performance chart

#### Screen 3: Retail Overview
- Header with live status indicator
- 4 summary KPI cards (footfall, conversion, dwell, sales)
- Live queue monitoring (all checkouts)
- Customer flow timeline chart
- Store heatmap (spatial)
- Top performing categories

#### Screen 4: Retail Analytics
- Demographics breakdown (age, gender)
- Promotion engagement metrics
- Shelf attention heatmap
- Security alerts feed
- Staff performance metrics
- Hour-by-hour breakdown

### Interactive Elements

**Filters:**
- Date range picker (Today, Yesterday, Last 7 days, Last 30 days, Custom)
- Location selector (multi-store support)
- Department/Zone filter
- Shift selector (Morning, Afternoon, Night, All)

**Actions:**
- Export report (PDF, CSV, Excel)
- Configure alerts
- Camera feed viewer (click to view live)
- Historical playback
- Manual incident logging

### Mobile Responsive Design

For mobile dashboard (Figma frames: 375×812px):
```
Stack layout (vertical scroll):
1. Summary cards (2×2 grid)
2. Critical alerts (collapsed list)
3. Primary chart (full width)
4. Secondary metrics (tabs)

Bottom navigation:
- Overview
- Alerts
- Analytics
- Settings
```

---

## AI Detection Models Required

### Summary of Required Models

| Use Case | Model Type | Priority | Estimated Accuracy |
|:---|:---|:---|:---|
| Person detection | YOLOv8 | High | 95%+ |
| Face recognition | ArcFace, DeepFace | High | 97%+ |
| PPE detection | Custom YOLO | High | 92%+ |
| Pose estimation | MediaPipe, OpenPose | Medium | 88%+ |
| Gender/Age classifier | ResNet-50 | Medium | 85%+ |
| Object detection (products) | YOLOv8 | Medium | 90%+ |
| Action recognition | SlowFast R-CNN | Low | 82%+ |
| Anomaly detection | Isolation Forest | Low | 75%+ |
| Gaze tracking | OpenFace | Low | 78%+ |

### Model Deployment Strategy

**Edge (NVIDIA Jetson):**
- Person detection (YOLOv8n - 3MB, 30 FPS)
- PPE detection (Custom YOLO - 15MB, 20 FPS)
- Face recognition (lightweight model - 10MB, 25 FPS)

**Cloud (for complex analysis):**
- Behavior analysis
- Demographics classification
- Predictive analytics

---

## Implementation Priority

### Phase 1: Core KPIs (Month 1-2)
- Employee attendance tracking
- Retail footfall counting
- Basic PPE compliance
- Queue length monitoring

### Phase 2: Safety & Security (Month 3-4)
- Restricted area violations
- Fatigue detection
- Shoplifting detection
- Suspicious behavior alerts

### Phase 3: Advanced Analytics (Month 5-6)
- Productivity metrics
- Customer demographics
- Heatmap generation
- Behavior patterns

### Phase 4: Predictive Intelligence (Month 7+)
- Demand forecasting
- Staff optimization
- Preventive maintenance
- Anomaly prediction

---

**Document Version:** 1.0  
**Last Updated:** December 1, 2024  
**Related:** [Main Implementation Guide](file:///c:/Users/LENOVO/Desktop/my_docs/AG/InvEye/INVEYE_COMPLETE_IMPLEMENTATION_GUIDE.md)
