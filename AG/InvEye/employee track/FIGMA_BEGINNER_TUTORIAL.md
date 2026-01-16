# Figma Design Tutorial for Employee Tracking Dashboard (Complete Beginner's Guide)

## 📌 What is Figma?

Figma is a **web-based design tool** (like Photoshop, but for UI/UX design). You can:
- Design website and app interfaces
- Create interactive prototypes
- Collaborate with team members in real-time
- No installation needed (works in browser)

**Access Figma:** Go to [figma.com](https://figma.com) and sign up for a free account.

---

## 🎯 Your Goal

You will design the **InvEye Employee Tracking Dashboard** - an admin interface to monitor employees in real-time using CCTV analytics. Think of it like the petrol pump dashboard you created, but for employee monitoring.

### What You'll Design

1. **Overview Dashboard** - Summary cards, live CCTV feeds, alerts
2. **Employee List** - Table view with all employees
3. **Individual Employee Detail** - Detailed timeline and metrics
4. **Analytics Screen** - Charts and trends
5. **Alert Management** - Real-time alerts and incidents

---

## 📐 Part 1: Setting Up Your Figma Project

### Step 1: Create New File

1. Log into Figma
2. Click **"New design file"** button (top right)
3. Name it: `InvEye Employee Tracking Dashboard`

### Step 2: Set Up Your Canvas

1. **Create your first frame** (frames = screens)
   - Press **`F`** on keyboard (Frame tool)
   - Look at right sidebar → Click **"Desktop"** → Select **"Desktop (1920 × 1080)"**
   - A large rectangle appears on canvas
   - Rename it: Double-click "Desktop" in left sidebar → Type `"Employee Overview Dashboard"`

2. **Set up the grid** (helps with alignment)
   - Select your frame (click on it)
   - Right sidebar → Look for "Layout Grid" section
   - Click **`+`** button
   - Change settings:
     - Grid type: **Columns**
     - Count: **12**
     - Gutter: **24**
     - Margin: **48**
   - This creates invisible columns that help you align elements

### Step 3: Install a Font (Important!)

1. Go to [Google Fonts](https://fonts.google.com/specimen/Inter)
2. Download **Inter** font
3. Install it on your computer
4. Restart Figma (refresh the browser tab)
5. Now you can use "Inter" font in your designs

---

## 🎨 Part 2: Creating Your Design System

**What is a Design System?** Think of it as your "ingredient list" - colors, fonts, spacing rules that you'll use throughout your design to keep everything consistent.

### Step 2A: Create Color Styles

1. **Draw a rectangle** (press **`R`** key)
   - Size: 200 × 200 pixels
   - Fill color: `#3B82F6` (blue)

2. **Save as color style:**
   - Select rectangle
   - Right sidebar → Find "Fill" section
   - Click **4-dot icon** next to the color
   - Click **`+`** (Create style)
   - Name: `Primary Blue`
   - Click **Create style**

3. **Repeat for all colors:**

| Color Name | Hex Code | When to Use |
|:---|:---|:---|
| Primary Blue | `#3B82F6` | Main actions, headers |
| Success Green | `#10B981` | Positive metrics, success states |
| Warning Amber | `#F59E0B` | Warnings, attention needed |
| Danger Red | `#EF4444` | Alerts, critical issues |
| Background Gray | `#F9FAFB` | Page background |
| Surface White | `#FFFFFF` | Card backgrounds |
| Text Dark | `#111827` | Main text |
| Text Gray | `#6B7280` | Secondary text, labels |

**Pro Tip:** After creating all colors, delete the rectangles. The color styles are saved in your file!

### Step 2B: Create Text Styles

1. **Create a text element** (press **`T`** key)
   - Type: "Dashboard Title"
   - Select the text
   - Right sidebar → Set:
     - Font: **Inter**
     - Weight: **Bold**
     - Size: **32**
     - Color: Text Dark (`#111827`)

2. **Save as text style:**
   - With text selected → Right sidebar → Find "Text" section
   - Click **4-dot icon** next to "Inter"
   - Click **`+`** (Create style)
   - Name: `Headline/Bold 32`

3. **Create all text styles:**

| Style Name | Font | Weight | Size | Use For |
|:---|:---|:---|:---:|:---|
| Headline/Bold 32 | Inter | Bold | 32px | Section headers |
| Title/Semibold 24 | Inter | Semibold | 24px | Card titles |
| Body/Regular 16 | Inter | Regular | 16px | Main content |
| Body/Regular 14 | Inter | Regular | 14px | Standard text |
| Caption/Regular 12 | Inter | Regular | 12px | Labels, timestamps |

---

## 🧩 Part 3: Building Your First Component (KPI Card)

**What is a Component?** A reusable design element. Create it once, use it many times. If you update the main component, all copies update automatically!

### Step 3A: Create the KPI Card

1. **Create a frame for the component:**
   - Press **`F`** key
   - Draw a rectangle, then change size in right sidebar:
     - Width: **280px**
     - Height: **160px**
   - Name it: `kpi-card`

2. **Add background and styling:**
   - Select frame
   - Right sidebar → Fill: **Surface White** (use your color style)
   - Corner radius: **12**
   - Effects → **`+`** → Drop shadow
     - X: 0, Y: 2, Blur: 8
     - Color: Black at 8% opacity

3. **Set up Auto Layout** (makes things automatically align)
   - Select frame
   - Press **Shift + A** (turns on Auto Layout)
   - Right sidebar → Auto Layout settings:
     - Direction: Vertical (↓)
     - Padding: **20** (all sides)
     - Gap: **12**

### Step 3B: Add Elements Inside

**Add Icon:**
1. Use **Iconify plugin** (free icons):
   - Menu → Plugins → Browse plugins → Search "Iconify"
   - Install it
   - Run plugin: Menu → Plugins → Iconify
   - Search "user" → Pick a simple user icon
   - Resize: 32 × 32 px
   - Color: Primary Blue

**Add Value Text:**
1. Press **`T`** → Type "145"
2. Apply style: `Headline/Bold 32`
3. Color: Text Dark

**Add Label Text:**
1. Press **`T`** → Type "Present Today"
2. Apply style: `Body/Regular 14`
3. Color: Text Gray

**Add Trend Badge:**
1. Create small frame (Auto Layout)
2. Add "↑ +5%" text
3. Background: Light green
4. Padding: 4px 8px

### Step 3C: Convert to Component

1. Select the entire `kpi-card` frame
2. Press **Ctrl + Alt + K** (or Cmd + Option + K on Mac)
3. Notice purple outline → It's now a component!
4. It appears in "Assets" panel (left sidebar)

### Step 3D: Create Variants (Different States)

1. Select component
2. Right sidebar → Click **"Add Variant"**
3. Now you have 2 versions side-by-side
4. Customize the second one:
   - Change icon color to Warning Amber
   - Change border to match
5. In right sidebar → Properties section:
   - Change property name to: `State`
   - Values: `Default` and `Warning`

Now you can switch between states when using this component!

---

## 📱 Part 4: Designing the Main Dashboard Screen

### Step 4A: Header Section

1. **Create header frame:**
   - Press **`F`** → Draw at top of your main frame
   - Auto Layout: Horizontal
   - Width: **1920px** (full width)
   - Height: **80px**
   - Padding: 24px
   - Background: Surface White

2. **Add elements:**
   - Logo/Title text: "🏠 InvEye Dashboard"
   - Date picker button
   - Live status indicator (🔴 LIVE)
   - User profile

**Pro Tip:** Use **Shift + A** frequently to turn elements into Auto Layout containers!

### Step 4B: KPI Summary Section

1. **Create container frame:**
   - Auto Layout: Horizontal
   - Gap: 24px
   - Padding: 24px

2. **Add 4 KPI cards:**
   - Drag your `kpi-card` component from Assets (left sidebar)
   - Duplicate 3 times (Ctrl + D)
   - Edit text for each:
     - Card 1: 145 / Present Today
     - Card 2: 92% / Compliance Rate
     - Card 3: 3 / Active Alerts
     - Card 4: 7.2hr / Avg Time

### Step 4C: Live CCTV Section

1. **Create grid:**
   - Frame with Auto Layout (wrap enabled)
   - 2×2 grid layout

2. **CCTV placeholder:**
   - For each camera, create frame (320×240px)
   - Background: Dark gray
   - Add text: "CAM 1 - Main Gate"
   - Add "🔴 LIVE" badge

3. **Insert placeholder image** (optional):
   - Menu → Plugins → Unsplash
   - Search "security camera"
   - Insert into frame

### Step 4D: Alerts Feed

1. **Create alert card component:**
   - Frame with Auto Layout
   - Horizontal layout
   - Elements:
     - Severity icon (🔴 / 🟡 / 🔵)
     - Text content (title + timestamp)
     - Action button

2. **Stack multiple alerts:**
   - Container with vertical Auto Layout
   - Gap: 12px
   - Add 3-5 alert cards

### Step 4E: Charts Section

**Option 1: Use Chart Plugin**
1. Menu → Plugins → Browse → Search "Charts"
2. Install "Charts" plugin
3. Run plugin → Select "Line Chart"
4. Input your data
5. Customize colors

**Option 2: Draw Manually (Beginner Friendly)**
1. Use **Line tool** (L key) for trend line
2. Use **Circle tool** (O key) for data points
3. Add grid lines with rectangles
4. Add axis labels with text

---

## 🎭 Part 5: Creating Interactive Prototype

### Step 5A: Link Screens

1. **Switch to Prototype mode:**
   - Top right → Click **"Prototype"** tab

2. **Create interaction:**
   - Click on a button/card
   - Blue circle appears → Drag to destination frame
   - In right sidebar:
     - Trigger: **On click**
     - Action: **Navigate to**
     - Destination: [Select target frame]
     - Animation: **Smart animate**
     - Duration: 300ms

3. **Common interactions to add:**
   - KPI card → Employee detail screen
   - Alert item → Alert detail
   - Employee row → Employee profile
   - Back buttons → Previous screen

### Step 5B: Preview Your Prototype

1. **Click Play button** (▶️) in top right
2. Full-screen preview opens
3. Click around to test interactions!
4. Press **Esc** to exit

### Step 5C: Share with Team

1. **Click "Share"** button (top right)
2. **Copy link**
3. Set permissions: "Anyone with link can view"
4. Send link to stakeholders for feedback!

---

## 📊 Part 6: Advanced Tips for Your Dashboard

### Tip 1: Using Plugins to Speed Up

**Recommended Plugins:**
1. **Iconify** - 100,000+ free icons
2. **Unsplash** - Free stock photos (for CCTV placeholders)
3. **Charts** - Generate data visualizations
4. **Content Reel** - Fill with realistic data (names, numbers)
5. **Lorem Ipsum** - Generate placeholder text

**How to install:**
- Menu → Plugins → Browse plugins in Community
- Search plugin name → Click "Install"

### Tip 2: Creating a Heatmap

1. **Grid of small squares:**
   - Create 20×20px square
   - Duplicate many times (Ctrl + D)
   - Arrange in grid pattern

2. **Color code by intensity:**
   - Cold (low activity): Light blue `#DBEAFE`
   - Warm: Yellow `#FCD34D`
   - Hot: Orange `#FB923C`
   - Very hot (high activity): Red `#EF4444`

3. **Add labels:**
   - Hours: 9am, 10am, 11am...
   - Days: Mon, Tue, Wed...

### Tip 3: Live Status Animation

1. **Create 2 frames:**
   - Frame 1: Dot at 100% opacity
   - Frame 2: Dot at 40% opacity

2. **Add animation:**
   - Prototype tab
   - Connect Frame 1 → Frame 2
   - Trigger: **After delay** (1000ms)
   - Animation: **Dissolve**
   - Then Frame 2 → Frame 1 (loop)

### Tip 4: Responsive Design

**Create multiple frame sizes:**
1. Desktop: 1920×1080px (done!)
2. Tablet: 768×1024px
3. Mobile: 375×812px

**Adapt layout:**
- Desktop: 4 KPI cards in a row
- Tablet: 2×2 grid
- Mobile: Vertical stack (scroll)

---

## ✅ Part 7: Design Checklist Before Handoff

Before sharing with developers, verify:

- [ ] All text uses defined text styles (no random font sizes)
- [ ] All colors use color styles (no random hex codes)
- [ ] Components are organized in clear structure
- [ ] Screens are properly named
- [ ] Interactive prototype works smoothly
- [ ] Responsive versions created (desktop, tablet, mobile)
- [ ] All icons are same style (consistent icon set)
- [ ] Spacing is consistent (use 8px grid: 8, 16, 24, 32, 48)
- [ ] Accessibility: Text has good contrast, readable sizes
- [ ] Developer notes added (comments on complex interactions)

---

## 📋 Part 8: Screen-by-Screen Design Breakdown

### Screen 1: Employee Overview Dashboard

**Elements to include:**
```
Header
├─ Logo + Title
├─ Location selector
├─ Date range picker
└─ Live status + User menu

Summary Section (4 KPI Cards)
├─ Present Today (145)
├─ Compliance Rate (92%)
├─ Active Alerts (3)
└─ Avg Time (7.2hr)

Main Content (2 column layout)
├─ Left Column (65%)
│  ├─ Live CCTV Grid (4 cameras)
│  ├─ Attendance Trend Chart
│  └─ PPE Compliance Chart
└─ Right Column (35%)
   ├─ Real-time Alerts Feed
   └─ Productivity Score Ring
```

**Figma Steps:**
1. Create header frame (Horizontal Auto Layout)
2. Create KPI container (Horizontal, gap: 24px)
3. Add 4 KPI card instances
4. Create 2-column layout (Horizontal Auto Layout)
5. Add CCTV grid (2×2 layout)
6. Add chart components
7. Add alerts sidebar

### Screen 2: Employee List

**Elements:**
```
Header (same as Screen 1)

Filter Bar
├─ Search box
├─ Department filter
├─ Shift filter
└─ Export button

Table
├─ Columns: Photo | Name | Status | Time In | Time on Site | Compliance
├─ 50 rows (use Content Reel plugin for dummy data)
└─ Pagination (10, 25, 50 per page)
```

**Figma Steps:**
1. Create table header row (Horizontal Auto Layout)
2. Create table cell component
3. Create full row component (8-10 cells)
4. Duplicate row 10-15 times
5. Add hover state (highlight row on hover)

### Screen 3: Individual Employee Detail

**Elements:**
```
Breadcrumb
└─ Employees > John Doe

Employee Header Card
├─ Photo
├─ Name + ID
├─ Department
├─ Current Status
└─ Shift timing

Timeline (Full width)
└─ Visual timeline of day (9am - 6pm)
    ├─ Clock in marker
    ├─ Break periods (shaded)
    ├─ Idle times (red)
    └─ Clock out marker

Metrics Grid (3 columns)
├─ Time on Premises (6h 45m)
├─ Active Time (5h 30m)
├─ Break Time (45m)
├─ Idle Time (30m)
├─ Overtime (0m)
└─ Compliance Score (92%)

Incident Log Table
└─ List of violations/alerts for this employee
```

### Screen 4: Analytics Dashboard

**Elements:**
```
Filters
├─ Date range
├─ Department
└─ Shift

Charts (2×2 grid)
├─ Attendance Trend (Line chart)
├─ Compliance by Department (Bar chart)
├─ Break Area Usage (Pie chart)
└─ Hourly Activity Heatmap
```

---

## 🎨 Part 9: Design Inspiration from Petrol Pump Dashboard

**What to replicate:**
1. **Clean, spacious layout** - Lots of white space, not cluttered
2. **Card-based design** - Each section in a rounded card
3. **Live status indicators** - 🔴 LIVE badges with pulsing animation
4. **Color-coded alerts** - Red (critical), Orange (high), Yellow (medium)
5. **Geographic view** - Map showing locations (adapt to floor plan for your case)
6. **Multi-level navigation** - HQ Overview → State → Individual RO
   - Your case: Overview → Department → Individual Employee
7. **Real-time CCTV grid** - 4-16 camera feeds in grid layout
8. **Alert sidebar** - Right panel with scrollable alert feed
9. **Trend charts** - Line charts showing hourly/daily trends
10. **Summary tables** - Clean tables with progress bars

**Color scheme similarity:**
- Primary: Blue (professional, trust)
- Background: Light gray (#F9FAFB)
- Cards: White with subtle shadow
- Status: Green (good), Red (bad), Yellow (warning)

---

## 🚀 Part 10: Export for Development

### Step 10A: Export Assets

**For developers:**
1. **Select element** (icon, image, logo)
2. Right sidebar → Find "Export" section
3. Click **`+`**
4. Settings:
   - Format: **PNG** (for images) or **SVG** (for icons)
   - Scale: **@1x, @2x, @3x** (for different screen densities)
5. Click **Export**

### Step 10B: Inspect Mode (Developer Handoff)

**How developers will use your design:**
1. They click on element in View mode
2. Right sidebar shows:
   - **Code** panel (Ctrl/Cmd + C)
   - CSS properties (width, height, color, etc.)
   - Automatically generated CSS code
3. They copy values directly!

**Your job:** Make sure everything is properly named and organized!

### Step 10C: Add Developer Notes

1. **Select a frame/component**
2. Right sidebar → Find **"Comments"** section
3. Click anywhere on canvas → Add comment
4. Type notes like:
   - "This should refresh every 30 seconds"
   - "Click to open camera in fullscreen"
   - "Load data from /api/employees endpoint"

---

## 🎓 Part 11: Common Beginner Mistakes to Avoid

### ❌ Mistake 1: Not Using Components
**Wrong:** Creating each KPI card from scratch
**Right:** Create one component, reuse it everywhere

### ❌ Mistake 2: Random Spacing
**Wrong:** 15px gap here, 18px there, 22px somewhere else
**Right:** Stick to 8px grid (8, 16, 24, 32, 48, 64)

### ❌ Mistake 3: Inconsistent Colors
**Wrong:** Using #3B82F6 in one place, #3A81F8 in another
**Right:** Create color styles once, use everywhere

### ❌ Mistake 4: Forgetting Mobile Design
**Wrong:** Only designing desktop version
**Right:** Create desktop, tablet, and mobile versions

### ❌ Mistake 5: Not Organizing Layers
**Wrong:** Layers named "Rectangle 127", "Frame 45"
**Right:** "header", "kpi-card", "alert-banner"

### ❌ Mistake 6: Unreadable Text
**Wrong:** Gray text (#CCC) on white background (poor contrast)
**Right:** Dark text (#111827) on white - 16:1 contrast ratio

---

## 📚 Learning Resources

### Video Tutorials
1. **Figma Official YouTube Channel**
   - "Figma for Beginners" (4-part series)
   - "Design Systems in Figma"

2. **DesignCourse YouTube**
   - "Figma Crash Course 2024"

3. **Chunbuns YouTube**
   - "Dashboard Design Tutorial"

### Practice Files
- Download Figma community files of dashboards
- Duplicate and study how they're built
- Search: "Admin Dashboard Template"

### Keyboard Shortcuts (Essential)
```
R - Rectangle
O - Circle
T - Text
F - Frame
V - Move tool
A - Auto Layout (Shift + A)
K - Scale tool
Ctrl + D - Duplicate
Ctrl + G - Group
Z - Zoom tool
Ctrl + Alt + K - Create component
```

---

## 🎯 Your Action Plan (Week-by-Week)

### Week 1: Fundamentals
- [ ] Day 1-2: Watch "Figma for Beginners" tutorial
- [ ] Day 3-4: Practice creating shapes, text, colors
- [ ] Day 5: Build your first component (button)
- [ ] Day 6-7: Create color palette and text styles

### Week 2: Components
- [ ] Day 1-2: Build KPI card component (with variants)
- [ ] Day 3: Build alert banner component
- [ ] Day 4: Build CCTV camera feed component
- [ ] Day 5-7: Build chart components

### Week 3: Screens
- [ ] Day 1-2: Design Overview Dashboard
- [ ] Day 3: Design Employee List
- [ ] Day 4: Design Employee Detail
- [ ] Day 5: Design Analytics screen
- [ ] Day 6-7: Design Alerts screen

### Week 4: Polish & Prototype
- [ ] Day 1-2: Add interactions (prototype mode)
- [ ] Day 3-4: Create mobile responsive versions
- [ ] Day 5: Add animations (pulsing live indicator)
- [ ] Day 6: Final polish, consistency check
- [ ] Day 7: Share prototype, gather feedback

---

## 💡 Pro Tips for Success

### Tip 1: Start Simple
Don't try to create everything perfectly on day 1. Build iteratively:
1. First: Wireframes (boxes and text, no colors)
2. Then: Add colors and icons
3. Finally: Add polish (shadows, animations)

### Tip 2: Use Real Data Examples
Instead of "Lorem ipsum", use realistic data:
- Employee names: "John Doe", "Sarah Lee"
- Metrics: "145 present", "92% compliance"
- Timestamps: "2 min ago", "5 min ago"

This makes it easier to visualize the real product!

### Tip 3: Study Similar Dashboards
Search on [dribbble.com](https://dribbble.com) or [behance.net](https://behance.net):
- "Admin dashboard"
- "Analytics dashboard"
- "Monitoring dashboard"
- "Security dashboard"

Take inspiration, but don't copy directly!

### Tip 4: Get Feedback Early
Share your design after each screen:
- Show to developers: "Is this buildable?"
- Show to users: "Is this understandable?"
- Show to managers: "Does this show the right KPIs?"

### Tip 5: Version Control
- Save versions: File → Save to version history
- Name them: "v1 - Initial draft", "v2 - After feedback"
- You can always go back if needed!

---

## 🎬 Final Checklist - Are You Ready?

Before calling your design "done", check:

**Design Quality:**
- [ ] Consistent spacing throughout (8px grid)
- [ ] All colors from defined palette
- [ ] All text uses text styles
- [ ] Icons all from same icon set
- [ ] Proper visual hierarchy (clear importance)
- [ ] Aligned elements (use alignment tools)

**Functionality:**
- [ ] All screens designed
- [ ] Prototype links work
- [ ] Hover states defined
- [ ] Error states designed
- [ ] Loading states designed
- [ ] Empty states designed ("No alerts yet")

**Documentation:**
- [ ] Screens properly named
- [ ] Components organized
- [ ] Developer comments added
- [ ] Handoff notes prepared

**Responsiveness:**
- [ ] Desktop version (1920×1080)
- [ ] Tablet version (768×1024) - optional
- [ ] Mobile version (375×812) - optional

---

## 🌟 Conclusion

You now have everything you need to design your Employee Tracking Dashboard in Figma! 

**Remember:**
1. Start small (one component at a time)
2. Practice daily (Figma is a skill, gets easier!)
3. Don't aim for perfection - aim for progress
4. Use existing templates and community files to learn
5. Ask for feedback often

**Need help?** Figma has an excellent community:
- [Figma Community](https://figma.com/community) - Free templates
- [Figma Forum](https://forum.figma.com) - Ask questions
- [Figma YouTube](https://youtube.com/figma) - Official tutorials

Good luck! 🚀

---

**Document Version:** 1.0  
**Last Updated:** December 2, 2024  
**Related Documents:**
- [Employee Tracking Workflow](file:///c:/Users/LENOVO/Desktop/my_docs/AG/InvEye/EMPLOYEE_TRACKING_WORKFLOW.md)
- [Employee & Retail KPIs](file:///c:/Users/LENOVO/Desktop/my_docs/AG/InvEye/EMPLOYEE_RETAIL_KPIS.md)
- [Advanced Figma Design Guide](file:///c:/Users/LENOVO/Desktop/my_docs/AG/InvEye/FIGMA_DASHBOARD_DESIGN_GUIDE.md)
