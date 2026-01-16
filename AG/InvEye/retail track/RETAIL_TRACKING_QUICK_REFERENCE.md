# Retail KPI Tracking Dashboard - Quick Reference Guide

## 📌 Document Overview

This is your **quick reference sheet** for understanding and designing the InvEye Retail KPI Tracking Dashboard. Bookmark this page!

---

## 🎯 KPIs Being Tracked

### 15 Core Metrics

| # | KPI | What It Measures | How CCTV Detects It |
|:---|:---|:---|:---|
| **1** | Footfall & Traffic Analytics | Total visitors, peak times, demographics | People counting at entrance/exit gates |
| **2** | Zone Heatmap & Engagement | High/low traffic areas in store | Zone-based tracking + dwell time |
| **3** | Queue & Checkout Analytics | Wait times, lane efficiency | Queue length detection + timer |
| **4** | Customer Journey Paths | Shopping patterns, path optimization | Multi-camera person tracking |
| **5** | Product Interaction Tracker | Items picked up, examined | Shelf cameras + object detection |
| **6** | Conversion Funnel | Entry → Engagement → Purchase | Customer tracking + POS integration |
| **7** | Shopping Basket Analysis | Average items, bundles, cross-sell | Cart content recognition |
| **8** | Theft & Shrinkage Monitor | Suspicious behavior, concealment | Behavior analysis + action recognition |
| **9** | Inventory Presence Verification | Out-of-stock alerts, shelf fullness | Shelf monitoring + product detection |
| **10** | Access Control | Staff-only zone monitoring | Person classification + zone detection |
| **11** | Employee Floor Coverage | Staff  deployment optimization | Staff location tracking |
| **12** | Customer Service Engagement | Staff-customer interactions | Interaction detection + duration |
| **13** | Cleaning & Maintenance | Spills, debris, maintenance needs | Object detection + condition monitoring |
| **14** | Promotional Display Effectiveness | Ad views, engagement, conversion | Attention tracking + gaze analysis |
| **15** | Fitting Room Analytics | Occupancy, try-on conversion | Entry/exit tracking + timer |

---

## 🏗️ System Architecture (Simplified)

```
[Store CCTV Cameras]
    → Capture video footage (30 FPS)
    ↓
[NVIDIA Jetson Edge Devices (maigic.ai)]
    → Run AI models (people counting, behavior analysis, product detection)
    → Process in real-time at the edge
    ↓
[Event Processor]
    → Generate events (entry, exit, interaction, theft, etc.)
    ↓
[Database]
    → Store all events and metrics
    ↓
[cloudtuner.ai Dashboard]
    → Display KPIs, alerts, charts
    → Real-time updates via WebSocket
```

---

## 🎨 Dashboard Screen Structure

### Screen 1: Overview Dashboard

**Purpose:** High-level summary of entire store

**Components:**
- Header with date selector and live status
- 4 KPI summary cards (Footfall, Conversion, Alerts, Revenue)
- Live CCTV grid (4-16 camera feeds)
- Real-time alert feed (right sidebar)
- Footfall trend chart
- Zone heatmap visualization

**User Actions:**
- Click KPI card → View detailed breakdown
- Click alert → View incident details
- Click camera → Fullscreen view
- Change date range → Update all metrics

---

### Screen 2: Customer Analytics

**Purpose:** Deep dive into customer behavior

**Components:**
- Footfall by hour/day chart
- Demographic breakdown (age, gender)
- Customer journey paths visualization
- Zone engagement heatmap
- Dwell time analysis

**User Actions:**
- Filter by date range
- Select specific zones
- Export customer reports
- View journey replay

---

### Screen 3: Product Intelligence

**Purpose:** Understand product performance

**Components:**
- Top interacted products list
- Shelf engagement metrics
- Conversion funnel visualization
- Basket analysis insights

**User Actions:**
- Search by product
- Filter by category
- Compare time periods
- Generate product reports

---

### Screen 4: Loss Prevention

**Purpose:** Security and theft monitoring

**Components:**
- Active incident feed
- Suspicious behavior alerts
- Inventory discrepancy log
- Access control violations

**User Actions:**
- View CCTV footage
- Dispatch security
- Acknowledge incidents
- Export security reports

---

### Screen 5: Staff Dashboard

**Purpose:** Staff performance and deployment

**Components:**
- Floor coverage heatmap
- Staff-customer interaction stats
- Service time metrics
- Deployment optimization recommendations

**User Actions:**
- View staff locations
- Analyze engagement patterns
- Adjust deployment
- Export performance reports

---

## 🎨 Design System Quick Reference

### Colors

| Color | Hex Code | Use Case |
|:---|:---|:---|
| Primary Blue | `#3B82F6` | Main actions, headers, links |
| Success Green | `#10B981` | Positive metrics, goals achieved |
| Warning Amber | `#F59E0B` | Warnings, attention needed |
| Danger Red | `#EF4444` | Alerts, critical issues, theft |
| Background | `#F9FAFB` | Page background |
| Surface | `#FFFFFF` | Card backgrounds |
| Text Dark | `#111827` | Primary text |
| Text Gray | `#6B7280` | Secondary text, labels |

### Typography

| Style | Font | Size | Weight | Use |
|:---|:---|:---:|:---:|:---:|
| Headline | Inter | 32px | Bold | Section headers |
| Title | Inter | 24px | Semibold | Card titles |
| Body Large | Inter | 16px | Regular | Important content |
| Body | Inter | 14px | Regular | Standard text |
| Caption | Inter | 12px | Regular | Labels, timestamps |

### Spacing

Use **8px grid system:**
- 8px - Tight spacing
- 16px - Default padding
- 24px - Section gaps
- 32px - Major spacing
- 48px - Page margins

---

## 🧩 Key Components

### KPI Card
```
┌─────────────────────┐
│  👥  Icon           │
│  2,847  Value       │
│  ↑ +12% Change      │
│  Visitors Today     │
└─────────────────────┘
```
- Size: 280×160px
- Background: White
- Shadow: Subtle
- Border radius: 12px

---

### Alert Banner
```
┌────────────────────────────────────┐
│ 🔴  Theft Suspected                │
│     Location: Aisle 7 Electronics  │
│     Camera: CAM-12 - 1 min ago     │
│     [View CCTV] [Dispatch]         │
└────────────────────────────────────┘
```
- Height: 64px
- Padding: 16px
- Border: 2px solid (severity color)

---

### CCTV Camera Feed
```
┌─────────────────┐
│ [Video Feed]    │
│                 │
│ 🔴 LIVE         │
│ CAM 1 - Entrance│
└─────────────────┘
```
- Size: 320×240px (16:9 aspect ratio)
- Live indicator: Pulsing red dot
- Camera name overlay

---

## 🔔 Alert Severity Levels

| Level | Color | Icon | Response Time | Example |
|:---|:---:|:---:|:---|:---|
| **Critical** | 🔴 Red | ⚠️ | Immediate | Theft in progress, emergency |
| **High** | 🟠 Orange | ⚡ | < 3 min | Suspicious behavior, long queue |
| **Medium** | 🟡 Yellow | ℹ️ | < 15 min | Low stock, spill detected |
| **Low** | 🔵 Blue | 📋 | < 1 hour | Cleaning needed, minor issue |

---

## 🔄 Data Flow

### Real-Time Updates

```
CCTV Camera
  → AI Detection (every frame, 30 FPS)
  → Event Generated (when something detected)
  → Database Updated (event logged)
  → WebSocket Push (to cloudtuner.ai dashboard)
  → Dashboard Updates (under 1 second)
```

### KPI Calculation Frequency

| KPI | Update Frequency | How |
|:---|:---|:---|
| Footfall Count | Real-time | On every entry/exit event |
| Queue Length | Every 30 seconds | Aggregate camera data |
| Active Alerts | Real-time | On every new violation |
| Conversion Rate | Every 5 minutes | Calculate from POS integration |

---

## 📊 Chart Types Used

### 1. Line Chart - Footfall Trend
- X-axis: Time (hourly or daily)
- Y-axis: Number of customers
- Shows: Patterns over time

### 2. Bar Chart - Zone Performance
- X-axis: Store zones
- Y-axis: Engagement percentage
- Shows: Comparison across zones

### 3. Pie/Donut Chart - Demographics
- Slices: Age ranges or gender
- Shows: Distribution/proportion

### 4. Heatmap - Store Layout
- Visual representation of store floor
- Color intensity: Customer density
- Shows: Hot/cold zones

### 5. Funnel Chart - Conversion
- Stages: Entry → Browse → Cart → Purchase
- Shows: Drop-off points

---

## 🎬 User Interactions

### Common Flows

**Flow 1: Manager checks daily summary**
1. Login → Lands on Overview Dashboard
2. Sees 2,847 visitors (KPI card)
3. Notices 2 active theft alerts
4. Clicks alert → Views CCTV footage
5. Dispatches security → Alert resolved

**Flow 2: Manager investigates zone performance**
1. Goes to Customer Analytics screen
2. Views zone heatmap
3. Sees clearance zone has low traffic
4. Clicks zone for details
5. Makes note to relocate clearance items

**Flow 3: Manager optimizes checkout**
1. Sees "Queue Long" alert
2. Views queue analytics
3. Sees Lane 13 has 9 min wait
4. Opens additional checkout lane
5. Queue resolves within 3 minutes

---

## 🖼️ Employee Dashboard Inspiration

**What to replicate from employee tracking dashboard:**

1. **Clean, professional look**
   - Lots of white space
   - Light gray background
   - Card-based layout

2. **Live indicators**
   - 🔴 LIVE badge on active feeds
   - Pulsing animation
   - Last updated timestamp

3. **Color-coded status**
   - Green: Good/normal
   - Red: Alert/critical
   - Yellow: Warning
   - Blue: Info

4. **Multi-level navigation**
   - Overview → Zone View → Product Detail

5. **CCTV grid layout**
   - 4 cameras in 2×2 grid
   - Scale to 9 or 16 based on needs

6. **Alert sidebar**
   - Right-side panel
   - Scrollable list
   - Most recent at top

7. **Summary metrics at top**
   - 4 KPI cards in a row
   - Large numbers
   - Trend indicators (↑ ↓)

---

## ✅ Implementation Checklist

Before starting, make sure you have:
- [ ] Camera placement plan finalized
- [ ] NVIDIA Jetson devices procured
- [ ] POS system integration API access
- [ ] cloudtuner.ai account set up

**Week 1-2 (Hardware Setup):**
- [ ] Install CCTV cameras
- [ ] Deploy edge devices
- [ ] Configure network
- [ ] Test camera feeds

**Week 3-4 (AI Training):**
- [ ] Collect training data
- [ ] Train people counting model
- [ ] Train product detection model
- [ ] Validate accuracy

**Week 5-6 (Dashboard Build):**
- [ ] Design Figma prototypes
- [ ] Build frontend
- [ ] Integrate WebSocket
- [ ] Implement alerts

**Week 7-8 (Testing & Launch):**
- [ ] End-to-end testing
- [ ] Manager training
- [ ] Soft launch
- [ ] Go live

---

## 🚀 InvEye Product Integration

### Three-Component System

```
┌────────────────────┐
│  Edge Kit          │ → NVIDIA Jetson devices at store
│  (Hardware)        │    Process video locally
└────────────────────┘
         ↓
┌────────────────────┐
│  maigic.ai         │ → AI processing engine
│  (Analysis)        │    Computer vision models
└────────────────────┘
         ↓
┌────────────────────┐
│  cloudtuner.ai     │ → Cloud dashboard
│  (Dashboard)       │    Visualization & reporting
└────────────────────┘
```

**Integration Benefits:**
- Edge processing = Low latency, privacy
- AI analysis = Accurate, scalable
- Cloud dashboard = Accessible anywhere, real-time

---

## 💡 Tips for Success

1. **Start with pilot zone** - Test in one section before full deployment
2. **Use real store data** - Train models on your actual store footage
3. **Involve store staff** - Get manager feedback early
4. **Privacy first** - Anonymize customer data, comply with regulations
5. **Iterate quickly** - Deploy MVP, gather feedback, improve
6. **Monitor accuracy** - Regularly validate AI model performance

---

## 📚 Related Documents

| Document | Purpose | When to Use |
|:---|:---|:---|
| **Retail KPI Workflow** | System architecture, technical flow | Understand how the system works |
| **Retail KPI Cards** | Complete KPI definitions | Deep dive into all 15 metrics |
| **Integration Guide** | End-to-end setup instructions | Implementation planning |
| **Employee Tracking Workflow** | Similar system for employees | Compare implementations |

---

## 🎯 Next Steps

**For Store Managers:**
1. Review KPIs being tracked
2. Define alert thresholds
3. Plan staff training
4. Set performance goals

**For IT Teams:**
1. Review technical flow
2. Plan network infrastructure
3. Set up cloudtuner.ai
4. Prepare POS integration

**For Implementation Partners:**
1. Conduct site survey
2. Design camera placement
3. Order hardware
4. Create project timeline

---

**Need help?** Refer to the detailed documents:
- Technical questions → `RETAIL_KPI_WORKFLOW.md`
- KPI definitions → `RETAIL_KPI_CARDS.md`
- Integration setup → `RETAIL_INVEYE_INTEGRATION_GUIDE.md`

---

**Document Version:** 1.0  
**Last Updated:** December 2, 2024  
**Quick Reference Guide**
