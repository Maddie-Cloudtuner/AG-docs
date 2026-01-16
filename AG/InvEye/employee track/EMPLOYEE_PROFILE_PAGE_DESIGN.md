# Employee Profile Page Design - Adapted from Vehicle Profile

## 📊 Comparison: Vehicle Profile → Employee Profile

This document shows how to adapt the **Vehicle Profile page** (Pump Dashboard) to create an **Employee Profile page** for the InvEye system.

---

## Image Analysis

### Current Vehicle Profile Structure (Pump5 Image)
![Vehicle Profile Reference](C:/Users/LENOVO/.gemini/antigravity/brain/893742ee-c07d-49c4-92f3-0e90fd0c6e2d/uploaded_image_1_1764657512363.png)

### Employee Overview Reference (Emp 1 Image)
![Employee Overview Reference](C:/Users/LENOVO/.gemini/antigravity/brain/893742ee-c07d-49c4-92f3-0e90fd0c6e2d/uploaded_image_0_1764657512363.png)

---

## 🔄 Element-by-Element Mapping

### Header Section

| Vehicle Profile | → | Employee Profile |
|:---|:---:|:---|
| **Vehicle Profile – GJ30 AB 1000** | → | **Employee Profile – #EMP-1234** |
| Vehicle registration number | → | Employee ID / Employee Code |
| Pump location | → | Department / Team |
| Last visit timestamp | → | Current status (On Site / On Leave / Absent) |

**New Header Design:**
```
┌─────────────────────────────────────────────────────┐
│ ← Back to Employee List                             │
│                                                      │
│ Employee Profile – BR15V77Y3Y3 (John Doe)          │
│ Department: GJ Team | Shift: Morning (9am-6pm)     │
│ Status: 🟢 On Premises | Last Seen: 2 min ago      │
└─────────────────────────────────────────────────────┘
```

---

### Section 1: Summary Cards (Top)

#### Vehicle Profile Has:
- **Day Ticket(s)**: 1835
- **Captures**: 1
- **Flags**: 1

#### Employee Profile Should Have:
- **Today's Hours**: 6h 45m
- **Compliance Score**: 92%
- **Violations Today**: 2

**Mockup:**
```
┌──────────────┬──────────────┬──────────────┬──────────────┐
│   🕐        │    ✓         │    ⚠️        │    📊       │
│   6h 45m    │    92%       │     2        │   85/100    │
│ Today's Hrs │  Compliance  │  Violations  │ Productivity│
│  ↑ +15m     │   ↓ -3%      │   → same     │   ↑ +5     │
└──────────────┴──────────────┴──────────────┴──────────────┘
```

---

### Section 2: Timeline/Activity View

#### Vehicle Profile Has:
**Visit History**
- List of dates and locations visited
- Simple chronological list

#### Employee Profile Should Have:
**Today's Timeline** (Horizontal timeline showing the day)

```
┌──────────────────────────────────────────────────────────┐
│ Today's Activity Timeline - December 2, 2024             │
├──────────────────────────────────────────────────────────┤
│                                                           │
│ 9am   10am   11am   12pm   1pm   2pm   3pm   4pm   5pm  │
│  │─────│─────│─────│─────│─────│─────│─────│─────│     │
│  ✓     ▓▓▓▓▓▓▓▓▓▓░░░▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░▓▓▓▓▓▓▓          │
│  │                                                        │
│  ↓                                                        │
│ Clock-In                                                  │
│ 9:02 AM                                                   │
│ Gate A                                                    │
│                                                           │
│ Events:                                                   │
│ • 9:02 AM - Clocked in (Gate A)                         │
│ • 11:30 AM - Break started (Cafeteria)                  │
│ • 11:50 AM - Break ended (20 min)                       │
│ • 2:15 PM - Phone use detected (Warning)                │
│ • 4:30 PM - Currently at workstation                    │
│                                                           │
│ Legend: ▓ Active | ░ Break | ░ Idle | 🔴 Violation     │
└──────────────────────────────────────────────────────────┘
```

---

### Section 3: Detailed Information Cards

#### Vehicle Profile Has:
Multiple expandable sections:
- **1. CAMERA/E AVAILABILITY**
- **2. PAYMENT INFORMATION**
- **3. THEFT ANALYSIS**
- **4. FIRE ANALYSIS**
- **5. SOP VIOLATION**
- **6. RATE/STATE/RULES**

#### Employee Profile Should Have:
Employee-specific analysis sections:

```
┌─────────────────────────────────────────────────────────┐
│ 📍 1. LOCATION & MOVEMENT TRACKING                      │
├─────────────────────────────────────────────────────────┤
│ Current Location:  Workstation B-15                     │
│ Time at Station:   3h 45m                               │
│ Total Movements:   12 zones visited today               │
│                                                          │
│ Zone Breakdown:                                          │
│ • Workstation B-15:    3h 45m (56%)                     │
│ • Break Room A:        45m (11%)                        │
│ • Cafeteria:           30m (7%)                         │
│ • Meeting Room 2:      1h 15m (19%)                     │
│ • Restroom:            10m (2%)                         │
│ • Other:               20m (5%)                         │
│                                                          │
│ [View Floor Plan Heatmap →]                             │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ ⏱️ 2. ATTENDANCE & TIME TRACKING                        │
├─────────────────────────────────────────────────────────┤
│ Clock In:         9:02 AM (Scheduled: 9:00 AM)          │
│ Status:           ✅ On Time (2 min late)                │
│ Expected Out:     6:00 PM                               │
│ Time on Site:     6h 45m (Current)                      │
│                                                          │
│ This Week Summary:                                       │
│ • Mon: 9:05 AM - 6:15 PM (9h 10m) ✅                    │
│ • Tue: 9:10 AM - 7:30 PM (10h 20m) ⚠️ Overtime         │
│ • Wed: 8:58 AM - 6:05 PM (9h 7m) ✅                     │
│ • Thu: Absent (Sick Leave) 🏥                           │
│ • Fri: 9:02 AM - Present (Current) 🟢                   │
│                                                          │
│ Weekly Stats:                                            │
│ • Total Hours: 35h 22m (Target: 40h)                    │
│ • Overtime: 1h 20m                                      │
│ • Punctuality: 75% (3/4 on-time)                        │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 🔒 3. SAFETY & COMPLIANCE                               │
├─────────────────────────────────────────────────────────┤
│ PPE Compliance Score:      92%                          │
│ Status: ✅ Within threshold (Target: 95%)               │
│                                                          │
│ Today's Detections:                                      │
│ ✅ Hard Hat:     Detected 145/150 frames (97%)          │
│ ✅ Safety Vest:  Detected 148/150 frames (99%)          │
│ ⚠️ Gloves:       Detected 130/150 frames (87%)          │
│ ✅ Safety Shoes: Detected 142/150 frames (95%)          │
│                                                          │
│ Recent Violations:                                       │
│ • 10:45 AM - No gloves in production zone (5 min)       │
│ • 2:30 PM - Improper posture at workstation             │
│                                                          │
│ Safety Score Trend (7 days):                            │
│ Mon  Tue  Wed  Thu  Fri  Sat  Sun                       │
│ 94%  89%  92%  95%  92%   -    -                        │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 📱 4. BEHAVIORAL COMPLIANCE                             │
├─────────────────────────────────────────────────────────┤
│ Phone Use Today:       12 min (Threshold: 10 min/hr)    │
│ Status: ⚠️ Above threshold                               │
│                                                          │
│ Phone Use Incidents:                                     │
│ • 10:15 AM - 3 min (Workstation)                        │
│ • 2:15 PM - 7 min (Workstation) ⚠️ Warning sent         │
│ • 3:45 PM - 2 min (Break area) ✅ Allowed               │
│                                                          │
│ Idle Time:             45 min (7% of total)             │
│ Longest Idle Period:   20 min (11:30 AM - 11:50 AM)     │
│ Status: ✅ Within acceptable range                      │
│                                                          │
│ Other Behaviors:                                         │
│ • Smoking detected: 0 times ✅                          │
│ • Unauthorized areas: 0 violations ✅                   │
│ • Extended conversations: 2 times (15 min total)        │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 📊 5. PRODUCTIVITY ANALYSIS                             │
├─────────────────────────────────────────────────────────┤
│ Productivity Score:    85/100                           │
│ Trend: ↑ +5 from last week                              │
│                                                          │
│ Time Breakdown:                                          │
│ ■■■■■■■■■░░ Active Time      5h 30m (82%)              │
│ ░░░        Break Time         45m (11%)                 │
│ ░          Idle Time          30m (4%)                  │
│ ░          Unaccounted        10m (2%)                  │
│                                                          │
│ Workstation Activity:                                    │
│ • Time at desk: 5h 55m                                  │
│ • Movement detected: 87% of time                        │
│ • Focus sessions: 3 (avg 1h 50m each)                   │
│                                                          │
│ Weekly Comparison:                                       │
│     Mon  Tue  Wed  Thu  Fri                             │
│ Score 82   88   85   -   85                             │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 🚨 6. INCIDENT LOG & VIOLATIONS                         │
├─────────────────────────────────────────────────────────┤
│ Total Incidents Today: 2                                │
│ Total This Week: 6                                      │
│ Total This Month: 18                                    │
│                                                          │
│ Recent Incidents:                                        │
│                                                          │
│ 🟡 MEDIUM - Today, 2:15 PM                              │
│ Unauthorized Phone Use                                  │
│ Duration: 7 minutes (Threshold: 5 min)                  │
│ Location: Workstation B-15                              │
│ Status: Warning sent                                    │
│ [View CCTV] [View Details]                              │
│                                                          │
│ 🟡 MEDIUM - Today, 10:45 AM                             │
│ No PPE - Gloves Missing                                 │
│ Duration: 5 minutes                                     │
│ Location: Production Floor Zone B                       │
│ Status: Acknowledged by supervisor                      │
│ [View CCTV] [View Details]                              │
│                                                          │
│ 🔵 LOW - Yesterday, 4:50 PM                             │
│ Overtime (not pre-approved)                             │
│ Duration: 1h 20m                                        │
│ Status: Pending approval                                │
│ [View Details]                                          │
│                                                          │
│ [View All Incidents (18) →]                             │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 📈 7. HISTORICAL PERFORMANCE                            │
├─────────────────────────────────────────────────────────┤
│ Performance Trends (Last 30 Days)                       │
│                                                          │
│ Attendance Rate:        95% (19/20 days present)        │
│ Average Hours/Day:      8.5 hours                       │
│ Overtime Hours:         12 hours total                  │
│ Compliance Score:       91% average                     │
│ Productivity Score:     83/100 average                  │
│                                                          │
│ [Line Chart: Daily Productivity]                        │
│ 100│                     ╱╲                             │
│  90│        ╱╲    ╱╲    ╱  ╲  ╱╲                        │
│  80│   ╱╲  ╱  ╲  ╱  ╲  ╱    ╲╱  ╲                       │
│  70│  ╱  ╲╱    ╲╱    ╲╱          ╲                      │
│  60│ ╱                             ╲                     │
│    └────────────────────────────────                    │
│     Week 1  Week 2  Week 3  Week 4                      │
│                                                          │
│ Top Performing Days:                                     │
│ • Tuesday: Avg 92/100                                   │
│ • Wednesday: Avg 89/100                                 │
│                                                          │
│ Improvement Areas:                                       │
│ • Reduce phone usage (12% above threshold)              │
│ • Improve PPE compliance (+3% needed)                   │
│ • Arrive on time more consistently                      │
└─────────────────────────────────────────────────────────┘
```

---

## 🆕 Additional Sections for Employee Profile

These sections don't exist in the vehicle profile but should be added:

### 8. Zone Access & Permissions
```
┌─────────────────────────────────────────────────────────┐
│ 🔐 8. ZONE ACCESS & PERMISSIONS                         │
├─────────────────────────────────────────────────────────┤
│ Authorized Zones: 8 of 15                               │
│                                                          │
│ ✅ Allowed Zones:                                        │
│ • Workstation Zone B (Floor 2)                          │
│ • Break Room A, B                                       │
│ • Cafeteria                                             │
│ • Meeting Rooms 1-3                                     │
│ • Production Floor Zone B                               │
│ • Storage Area 2                                        │
│                                                          │
│ ⛔ Restricted Zones:                                     │
│ • Server Room                                           │
│ • Executive Floor                                       │
│ • Production Floor Zone A                               │
│ • Chemical Storage                                      │
│ • Warehouse Section 1, 3                                │
│                                                          │
│ Unauthorized Access Attempts:                            │
│ • None this week ✅                                     │
└─────────────────────────────────────────────────────────┘
```

### 9. Health & Wellness
```
┌─────────────────────────────────────────────────────────┐
│ 🏥 9. HEALTH & WELLNESS MONITORING                      │
├─────────────────────────────────────────────────────────┤
│ Temperature Check:     36.5°C (Normal) ✅               │
│ Last Checked:          9:00 AM today                    │
│                                                          │
│ Fatigue Indicators:                                      │
│ • Eye closure events: 0 today ✅                        │
│ • Head nodding: Not detected ✅                         │
│ • Posture deterioration: Minimal                        │
│                                                          │
│ Break Compliance:                                        │
│ • Breaks taken: 2 (Recommended: 2-3)                    │
│ • Total break time: 45 min (Target: 30-60 min)          │
│ • Longest work stretch: 2h 30m ✅                       │
│                                                          │
│ Stress Indicators:                                       │
│ • Rapid movements: Normal range                         │
│ • Agitation detected: None                              │
└─────────────────────────────────────────────────────────┘
```

### 10. Manager Notes & Actions
```
┌─────────────────────────────────────────────────────────┐
│ 📝 10. MANAGER NOTES & ACTIONS                          │
├─────────────────────────────────────────────────────────┤
│ Recent Notes:                                            │
│                                                          │
│ Dec 1, 2024 - Supervisor: Jane Smith                    │
│ "Good performance this week. Discussed phone usage      │
│  during team meeting. Employee acknowledged."           │
│                                                          │
│ Nov 28, 2024 - HR: Mike Johnson                         │
│ "Completed safety training refresher."                  │
│                                                          │
│ Scheduled Actions:                                       │
│ • Performance review: Dec 15, 2024                      │
│ • Safety training renewal: Jan 10, 2025                 │
│                                                          │
│ [Add New Note] [Schedule Action] [View All Notes]       │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 Complete Comparison Table

| # | Vehicle Profile Element | Employee Profile Element | Change Type |
|:---|:---|:---|:---|
| **Header** |
| 1 | Vehicle Number | Employee ID | **Swap** |
| 2 | Pump Location | Department/Team | **Swap** |
| 3 | Last Visit | Current Status | **Swap** |
| **Summary Cards** |
| 4 | Day Tickets | Today's Hours | **Swap** |
| 5 | Captures | Compliance Score | **Swap** |
| 6 | Flags | Violations Today | **Swap** |
| 7 | - | Productivity Score | **Add New** |
| **Main Content** |
| 8 | Visit History | Today's Timeline | **Swap + Enhance** |
| 9 | Camera Availability | Location & Movement | **Swap** |
| 10 | Payment Information | Attendance & Time | **Swap** |
| 11 | Theft Analysis | Safety & Compliance | **Swap** |
| 12 | Fire Analysis | Behavioral Compliance | **Swap** |
| 13 | SOP Violation | Productivity Analysis | **Swap** |
| 14 | Rate/State/Rules | Incident Log | **Swap** |
| 15 | - | Historical Performance | **Add New** |
| 16 | - | Zone Access | **Add New** |
| 17 | - | Health & Wellness | **Add New** |
| 18 | - | Manager Notes | **Add New** |

---

## 🎨 Design Changes Needed

### Color Scheme
**Keep from Vehicle Profile:**
- Blue primary color ✅
- Green for positive metrics ✅
- Red for violations/alerts ✅
- Light gray background ✅

**Adjust:**
- Use warmer tones for employee wellness sections
- Add orange/amber for warnings
- Use purple for productivity metrics

### Icons
**Swap These:**
| Old (Vehicle) | New (Employee) |
|:---|:---|
| 🚗 Vehicle | 👤 Person |
| ⛽ Pump | 🏢 Building/Department |
| 💰 Payment | ⏰ Time Clock |
| 🔥 Fire | 🦺 Safety Equipment |
| 🚨 Theft | 📱 Phone/Behavior |

### Layout
**Keep:**
- Expandable sections ✅
- Card-based design ✅
- Blue headers for sections ✅
- White content areas ✅

**Change:**
- Add horizontal timeline at top
- Make timeline more prominent
- Add circular progress rings for scores
- Include small avatar/photo of employee

---

## 📸 CCTV Integration Differences

### Vehicle Profile:
- Shows snapshots of incidents
- Focus on vehicle/pump area

### Employee Profile:
- Shows employee at workstation
- Blur face for privacy (show in restricted view only)
- Include zone context
- Show timestamp overlay

**Example:**
```
┌─────────────────────────────────┐
│ CCTV Snapshot                   │
│ 2:15 PM - Workstation B-15      │
│                                  │
│ [Blurred employee image]         │
│                                  │
│ Violation: Phone use detected   │
│ Camera: CAM-12                  │
│                                  │
│ [👁️ View Full (Authorized)] │
└─────────────────────────────────┘
```

---

## 🔄 Data Fields Mapping

### Remove from Vehicle Profile:
- ❌ Pump ID / RO Code
- ❌ Fuel types
- ❌ Transaction amounts
- ❌ Payment methods
- ❌ Diesel/Petrol quantities
- ❌ Nozzle information

### Add to Employee Profile:
- ✅ Employee photo/avatar
- ✅ Department/Team
- ✅ Shift timing
- ✅ Job role/designation
- ✅ Reporting manager
- ✅ Emergency contact (if authorized)
- ✅ Clock in/out times
- ✅ Break duration
- ✅ Overtime hours
- ✅ PPE requirements
- ✅ Zone access permissions
- ✅ Productivity metrics
- ✅ Compliance scores
- ✅ Health indicators
- ✅ Training status

---

## 🎯 Priority Changes (MVP)

### Phase 1 - Essential Changes:
1. ✅ Swap header (vehicle → employee info)
2. ✅ Change summary cards (hours, compliance, violations)
3. ✅ Add timeline view
4. ✅ Adapt sections 1-6 (location, attendance, safety, behavior, productivity, incidents)

### Phase 2 - Enhanced Features:
5. ⏳ Add historical performance
6. ⏳ Add zone access tracking
7. ⏳ Add manager notes

### Phase 3 - Advanced:
8. ⏳ Health & wellness monitoring
9. ⏳ Predictive analytics
10. ⏳ Comparative benchmarks

---

## 💡 Quick Action Items for Figma

**To adapt the vehicle profile design:**

1. **Duplicate the vehicle profile frame**
   - Rename to "Employee Profile"

2. **Update header section**
   - Change "Vehicle Profile" text to "Employee Profile"
   - Replace vehicle number with employee ID
   - Update metadata fields

3. **Redesign summary cards**
   - Keep the 4-card layout
   - Change icons and labels
   - Update values to employee metrics

4. **Rebuild sections 1-6**
   - Keep the blue header style
   - Keep expandable functionality
   - Swap content as per mapping table above

5. **Add new sections 7-10**
   - Copy existing section component
   - Update content for new sections

6. **Update all icons**
   - Use Iconify plugin
   - Search for employee/productivity/safety icons
   - Replace vehicle-related icons

7. **Add timeline component**
   - Create new horizontal timeline
   - Place after summary cards
   - Use auto-layout for markers

---

## ✅ Checklist for Conversion

Before finalizing, verify:

- [ ] All vehicle references removed
- [ ] Employee ID displayed correctly
- [ ] Timeline shows today's activity
- [ ] All 7 KPIs represented
- [ ] Safety/compliance sections show PPE
- [ ] Behavioral tracking included
- [ ] Privacy considerations (blur faces)
- [ ] Manager actions section added
- [ ] CCTV snapshots have employee context
- [ ] Color scheme is consistent
- [ ] Icons are employee-focused
- [ ] All text updated (no "pump", "vehicle", etc.)
- [ ] Data privacy disclaimers added

---

**Document Version:** 1.0  
**Created:** December 2, 2024  
**Purpose:** Guide for adapting vehicle profile to employee profile design
