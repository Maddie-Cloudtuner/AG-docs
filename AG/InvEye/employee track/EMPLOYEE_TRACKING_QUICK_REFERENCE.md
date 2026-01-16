# Employee Tracking Dashboard - Quick Reference Guide

## 📌 Document Overview

This is your **quick reference sheet** for understanding and designing the InvEye Employee Tracking Dashboard. Bookmark this page!

---

## 🎯 KPIs Being Tracked

### 7 Core Metrics

| # | KPI | What It Measures | How CCTV Detects It |
|:---|:---|:---|:---|
| **1** | Employee Entry/Exit Detection | Who's on premises, when they arrived/left | Facial recognition at gates |
| **2** | Actual Time on Premises | Total hours employee is on site | First entry to last exit |
| **3** | Time Spent in Break Areas | Duration in break rooms, cafeteria | Zone detection + person tracking |
| **4** | Hours Beyond Shift | Overtime hours worked | Comparing exit time vs scheduled shift end |
| **5** | % of Scheduled Days Missed | Absenteeism rate | Comparing scheduled shifts vs actual entries |
| **6** | Inactive Periods at Workstation | Time desk is empty or no movement | Pose detection at workstation |
| **7** | Unauthorized Phone Use | Time spent on phone during work hours | Object detection (phone in hand) |

---

## 🏗️ System Architecture (Simplified)

```
[CCTV Cameras] 
    → Capture video footage (30 FPS)
    ↓
[NVIDIA Jetson Edge Devices]
    → Run AI models (face recognition, PPE detection, pose estimation)
    → Process in real-time
    ↓
[Event Processor]
    → Generate events (entry, exit, violation, etc.)
    ↓
[Database]
    → Store all events and metrics
    ↓
[Admin Dashboard]
    → Display KPIs, alerts, charts
    → Real-time updates via WebSocket
```

---

## 🎨 Dashboard Screen Structure

### Screen 1: Overview Dashboard

**Purpose:** High-level summary of entire facility

**Components:**
- Header with date selector and live status
- 4 KPI summary cards
- Live CCTV grid (4-16 camera feeds)
- Real-time alert feed (right sidebar)
- Attendance trend chart
- PPE compliance chart

**User Actions:**
- Click KPI card → View detailed breakdown
- Click alert → View incident details
- Click camera → Fullscreen view
- Change date range → Update all metrics

---

### Screen 2: Employee List

**Purpose:** See all employees and their current status

**Components:**
- Search and filter bar
- Table with columns:
  - Photo
  - Name & ID
  - Department
  - Status (Present/Absent/On Break)
  - Time In
  - Time on Site
  - Compliance Score
- Pagination controls

**User Actions:**
- Click employee row → View individual details
- Search by name/ID
- Filter by department, shift, status
- Export to CSV

---

### Screen 3: Individual Employee Detail

**Purpose:** Deep dive into one employee's day

**Components:**
- Employee header (photo, name, department)
- Current status badge
- Timeline visualization (9am-6pm with markers)
- 6 metric cards (time on premises, active time, break time, idle time, overtime, compliance)
- Incident log table
- Historical performance chart

**User Actions:**
- View timeline → See exact activities
- Click incident → View CCTV snapshot
- View historical data → Compare with past weeks

---

### Screen 4: Analytics Dashboard

**Purpose:** Trends and patterns analysis

**Components:**
- Date range and filter controls
- 4 large charts:
  - Attendance trend (line chart)
  - Compliance by department (bar chart)
  - Break area usage (pie chart)
  - Hourly activity heatmap
- Top performers list
- Bottom performers list

**User Actions:**
- Change filters → Update charts
- Hover chart → See exact values
- Export report → PDF/Excel

---

### Screen 5: Alerts & Incidents

**Purpose:** Manage all alerts and violations

**Components:**
- Filter by severity, type, status
- Alert cards with:
  - Severity indicator (🔴 🟠 🟡 🔵)
  - Alert type
  - Employee name
  - Location
  - Timestamp
  - CCTV snapshot
  - Action buttons (Acknowledge, Dismiss, View Details)

**User Actions:**
- Filter alerts by type/severity
- Acknowledge alert → Mark as reviewed
- Dismiss alert → Remove from active list
- View CCTV → See what happened

---

## 🎨 Design System Quick Reference

### Colors

| Color | Hex Code | Use Case |
|:---|:---|:---|
| Primary Blue | `#3B82F6` | Main actions, headers, links |
| Success Green | `#10B981` | Positive metrics, compliance achieved |
| Warning Amber | `#F59E0B` | Warnings, attention needed |
| Danger Red | `#EF4444` | Alerts, critical issues, violations |
| Background | `#F9FAFB` | Page background |
| Surface | `#FFFFFF` | Card backgrounds |
| Text Dark | `#111827` | Primary text |
| Text Gray | `#6B7280` | Secondary text, labels |

### Typography

| Style | Font | Size | Weight | Use |
|:---|:---|:---:|:---:|:---|
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
│  👤  Icon           │
│  145  Value         │
│  ↑ +5% Change       │
│  Present Today      │
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
│ 🔴  No PPE Detected                │
│     Employee: John Doe (#1234)     │
│     Location: Floor B - 5 min ago  │
│     [View CCTV] [Dismiss]          │
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
│ CAM 1 - Gate A  │
└─────────────────┘
```
- Size: 320×240px (16:9 aspect ratio)
- Live indicator: Pulsing red dot
- Camera name overlay

---

## 🔔 Alert Severity Levels

| Level | Color | Icon | Response Time | Example |
|:---|:---:|:---:|:---|:---|
| **Critical** | 🔴 Red | ⚠️ | Immediate | Restricted area breach |
| **High** | 🟠 Orange | ⚡ | < 5 min | No PPE in hazard zone |
| **Medium** | 🟡 Yellow | ℹ️ | < 30 min | Excessive phone use |
| **Low** | 🔵 Blue | 📋 | < 1 hour | Late arrival |

---

## 🔄 Data Flow

### Real-Time Updates

```
CCTV Camera 
  → AI Detection (every frame, 30 FPS)
  → Event Generated (when something detected)
  → Database Updated (event logged)
  → WebSocket Push (to all connected dashboards)
  → Dashboard Updates (under 1 second)
```

### KPI Calculation Frequency

| KPI | Update Frequency | How |
|:---|:---|:---|
| Present Count | Real-time | On every entry/exit event |
| Compliance Rate | Every 5 minutes | Aggregate recent detections |
| Active Alerts | Real-time | On every new violation |
| Average Time | Every 5 minutes | Calculate from all employees |

---

## 📊 Chart Types Used

### 1. Line Chart - Attendance Trend
- X-axis: Time (hourly or daily)
- Y-axis: Number of employees
- Shows: Patterns over time

### 2. Bar Chart - Compliance by Department
- X-axis: Department names
- Y-axis: Compliance percentage
- Shows: Comparison across departments

### 3. Pie/Donut Chart - Break Area Usage
- Slices: Different break areas
- Shows: Distribution/proportion

### 4. Heatmap - Hourly Activity
- Rows: Days of week
- Columns: Hours of day
- Color intensity: Activity level
- Shows: When activity is highest/lowest

### 5. Progress Ring - Compliance Score
- Full circle: 100%
- Arc length: Current percentage
- Shows: Single metric as percentage

---

## 🎬 User Interactions

### Common Flows

**Flow 1: Admin checks daily summary**
1. Login → Lands on Overview Dashboard
2. Sees 145 employees present (KPI card)
3. Notices 3 active alerts
4. Clicks alert → Views details
5. Acknowledges alert → Removed from active list

**Flow 2: Admin investigates employee**
1. Goes to Employee List screen
2. Searches "John Doe"
3. Clicks on employee row
4. Views detailed timeline
5. Sees phone use violation at 2:30 PM
6. Clicks CCTV snapshot → Confirms violation
7. Adds note → Saves for HR

**Flow 3: Admin generates report**
1. Goes to Analytics Dashboard
2. Selects date range: Last 30 days
3. Views trends
4. Clicks "Export Report"
5. Downloads PDF with all charts

---

## 🖼️ Petrol Pump Dashboard Inspiration

**What to replicate from your reference:**

1. **Clean, professional look**
   - Lots of white space
   - Light gray background
   - Card-based layout

2. **Live indicators**
   - 🔴 LIVE badge on active feeds
   - Pulsing animation
   - Last updated timestamp

3. **Color-coded status**
   - Green: Good/operational
   - Red: Alert/critical
   - Yellow: Warning
   - Blue: Info

4. **Multi-level navigation**
   - HQ Overview → State View → Individual RO
   - **Your case:** Overview → Department → Individual Employee

5. **CCTV grid layout**
   - 4 cameras in 2×2 grid
   - Scale to 9 or 16 based on needs
   - Fullscreen option

6. **Alert sidebar**
   - Right-side panel
   - Scrollable list
   - Most recent at top
   - Severity indicators

7. **Summary metrics at top**
   - 4 KPI cards in a row
   - Large numbers
   - Trend indicators (↑ ↓)
   - Icons for quick recognition

8. **Charts for trends**
   - Line charts for time-based data
   - Bar charts for comparisons
   - Clean, minimal styling

9. **Geographic visualization**
   - Map in petrol pump dashboard
   - **Your case:** Floor plan or zone map

10. **Data tables**
    - Clean, organized
    - Progress bars for percentages
    - Sortable columns

---

## ✅ Figma Checklist

Before starting, make sure you have:
- [ ] Figma account created (free at figma.com)
- [ ] Inter font installed on your computer
- [ ] Reviewed petrol pump dashboard images for inspiration
- [ ] Read the Beginner's Tutorial document

**First session (1-2 hours):**
- [ ] Create color palette (8 colors)
- [ ] Create text styles (5 styles)
- [ ] Build your first KPI card component

**Second session (2-3 hours):**
- [ ] Build alert banner component
- [ ] Build CCTV feed component
- [ ] Build header component

**Third session (3-4 hours):**
- [ ] Design Overview Dashboard screen
- [ ] Add all components to layout
- [ ] Test on 12-column grid

**Fourth session (2-3 hours):**
- [ ] Create prototype links
- [ ] Add hover states
- [ ] Test interactions in preview mode

---

## 🚀 Implementation Phases

### Phase 1: MVP (Weeks 1-4)
**Goal:** Basic dashboard with core KPIs

**Features:**
- Entry/exit detection
- Present employee count
- Basic PPE compliance
- Simple alert system

**Dashboard:**
- Overview screen only
- 4 KPI cards
- Alert list
- No charts yet

---

### Phase 2: Enhanced (Weeks 5-8)
**Goal:** Add analytics and individual tracking

**Features:**
- Individual employee timelines
- Break time tracking
- Idle time detection
- Historical trends

**Dashboard:**
- Employee List screen
- Employee Detail screen
- Add charts to Overview

---

### Phase 3: Advanced (Weeks 9-12)
**Goal:** Full analytics and predictions

**Features:**
- Predictive analytics
- Heatmap visualizations
- Comparative reports
- Export functionality

**Dashboard:**
- Analytics screen
- Alert Management screen
- Mobile responsive version

---

## 📱 Mobile Considerations

If creating mobile version:
- Stack KPI cards vertically (not 4 in a row)
- CCTV grid becomes 1 per row (swipeable)
- Charts become full-width
- Use tabs for different sections
- Bottom navigation bar

---

## 🔐 Security & Privacy

**Important considerations:**
- Employee facial data is sensitive
- Comply with privacy laws (GDPR, etc.)
- Show only authorized data to each admin
- Blur faces in shared reports
- Log all access to employee data
- Allow employees to request their data

---

## 💡 Tips for Success

1. **Start with wireframes** - Boxes and text, no colors
2. **Use real data examples** - Not "Lorem ipsum"
3. **Test with stakeholders** - Get feedback early
4. **Think mobile-first** - Even if desktop is primary
5. **Keep it simple** - Don't overcomplicate
6. **Iterate quickly** - Don't aim for perfection on v1

---

## 📚 Related Documents

| Document | Purpose | When to Use |
|:---|:---|:---|
| **Employee Tracking Workflow** | System architecture, technical flow | Understand how the system works |
| **Figma Beginner Tutorial** | Step-by-step Figma guide | Learning Figma from scratch |
| **Employee & Retail KPIs** | Complete KPI definitions | Deep dive into all metrics |
| **Figma Dashboard Design Guide** | Advanced design specs | Detailed component specifications |

---

## 🎯 Next Steps

**For Project Managers:**
1. Review system architecture in Workflow document
2. Define MVP scope
3. Assign resources
4. Set timeline

**For Designers:**
1. Read Figma Beginner Tutorial
2. Set up Figma file
3. Create design system
4. Design Overview Dashboard

**For Developers:**
1. Review technical flow in Workflow document
2. Set up CCTV integration
3. Build backend API
4. Prepare frontend framework

**For Stakeholders:**
1. Review KPIs being tracked
2. Provide feedback on dashboard wireframes
3. Define alert thresholds
4. Plan deployment

---

**Need help?** Refer to the detailed documents:
- Technical questions → `EMPLOYEE_TRACKING_WORKFLOW.md`
- Design questions → `FIGMA_BEGINNER_TUTORIAL.md`
- KPI definitions → `EMPLOYEE_RETAIL_KPIS.md`

---

**Document Version:** 1.0  
**Last Updated:** December 2, 2024  
**Quick Reference Guide**
