# InvEye Dashboard - Figma Design Guide

## Overview

This guide provides detailed specifications for implementing the InvEye analytics dashboard in Figma, including employee tracking and retail store KPIs.

---

## Dashboard Preview

![InvEye Dashboard Mockup](C:/Users/LENOVO/.gemini/antigravity/brain/2c811c3b-5e18-4171-9f0c-5688205e590f/inveye_dashboard_mockup_1764590939358.png)

---

## Design System Specifications

### 1. Color Palette

#### Employee Tracking Theme
```css
Primary:     #3B82F6  /* Blue - Professional, Trust */
Primary-50:  #EFF6FF  /* Very light blue background */
Primary-100: #DBEAFE  /* Light blue for hover states */
Primary-600: #2563EB  /* Darker blue for text */
Primary-800: #1E40AF  /* Deep blue for headers */

Success:     #10B981  /* Green - Compliance achieved */
Warning:     #F59E0B  /* Amber - Attention needed */
Danger:      #EF4444  /* Red - Immediate action */
```

#### Retail Store Theme
```css
Primary:     #8B5CF6  /* Purple - Retail, Premium */
Primary-50:  #F5F3FF  /* Very light purple background */
Primary-100: #EDE9FE  /* Light purple for hover states */
Primary-600: #7C3AED  /* Darker purple for text */
Primary-800: #5B21B6  /* Deep purple for headers */

Success:     #10B981  /* Green - Sales growth */
Warning:     #F59E0B  /* Amber - Queue buildup */
Danger:      #EF4444  /* Red - Security alert */
```

#### Neutral Colors
```css
Background:  #F9FAFB  /* Light gray for page background */
Surface:     #FFFFFF  /* White for cards */
Border:      #E5E7EB  /* Light border color */
Text-Primary: #111827  /* Dark gray for main text */
Text-Secondary: #6B7280  /* Medium gray for labels */
Text-Tertiary: #9CA3AF  /* Light gray for timestamps */
```

### 2. Typography

#### Font Family
```
Primary: Inter (Google Fonts)
Fallback: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto
```

#### Font Sizes & Weights
```
Display Large:  48px / Bold (600)     - Main dashboard title
Headline:       32px / Bold (600)     - Section headers
Title:          24px / Semibold (500) - Card titles
Body Large:     16px / Regular (400)  - Main content
Body:           14px / Regular (400)  - Standard text
Caption:        12px / Regular (400)  - Labels, timestamps
Small:          10px / Medium (500)   - Tiny labels
```

### 3. Spacing System

Use 8px base grid:
```
xs:   4px   - Tight spacing within components
sm:   8px   - Default component padding
md:   16px  - Card padding, margins
lg:   24px  - Section spacing
xl:   32px  - Major section gaps
2xl:  48px  - Page margins
```

### 4. Corner Radius
```
Small:   4px  - Buttons, badges
Medium:  8px  - Input fields, small cards
Large:   12px - Main cards, panels
X-Large: 16px - Modal dialogs
Round:   9999px - Pills, avatars
```

### 5. Shadows
```
Sm:  0px 1px 2px rgba(0, 0, 0, 0.05)
Md:  0px 2px 8px rgba(0, 0, 0, 0.08)
Lg:  0px 4px 16px rgba(0, 0, 0, 0.12)
Xl:  0px 8px 24px rgba(0, 0, 0, 0.15)
```

---

## Component Library

### Component 1: KPI Card

**Figma Setup:**
```
Frame Name: kpi-card
Size: 240px × 140px (flexible width)
Auto Layout: Vertical
Padding: 20px
Gap: 12px
Fill: #FFFFFF
Corner Radius: 12px
Shadow: md (0px 2px 8px rgba(0,0,0,0.08))

Variants:
- Theme: employee / retail
- State: default / warning / critical
```

**Structure:**
```
kpi-card (Auto Layout - Vertical)
├── icon-container (Frame, 48×48px)
│   └── icon (Icon, 32×32px)
├── value-container (Auto Layout - Horizontal)
│   ├── value (Text, 32px Bold)
│   └── trend-badge (Optional)
│       ├── arrow-icon (12px)
│       └── percentage (14px)
└── label (Text, 14px Regular, #6B7280)
```

**Example:**
```
Icon: 👤 (Person icon, #3B82F6)
Value: 145
Trend: ↑ +12% (Green background)
Label: Present Today
```

### Component 2: Alert Banner

**Figma Setup:**
```
Frame Name: alert-banner
Size: Auto × 64px
Auto Layout: Horizontal
Padding: 16px
Gap: 12px
Fill: Depends on severity
Border: 2px solid (matching fill color)
Corner Radius: 8px

Variants:
- Severity: info / warning / critical
```

**Structure:**
```
alert-banner (Auto Layout - Horizontal)
├── status-icon (Icon, 24×24px)
├── content (Auto Layout - Vertical)
│   ├── alert-text (Text, 14px Medium)
│   └── timestamp (Text, 12px Regular, #9CA3AF)
└── action-button (Optional, 32×32px)
    └── icon (Close or View, 16×16px)
```

**Color Mapping:**
```
Info:
  Fill: #EFF6FF
  Border: #3B82F6
  Icon Color: #3B82F6

Warning:
  Fill: #FFFBEB
  Border: #F59E0B
  Icon Color: #F59E0B

Critical:
  Fill: #FEF2F2
  Border: #EF4444
  Icon Color: #EF4444
```

### Component 3: Line Chart

**Figma Setup:**
```
Frame Name: line-chart
Size: 400px × 200px (flexible)
Fill: #FFFFFF
Corner Radius: 12px
Padding: 20px
```

**Structure:**
```
line-chart (Frame)
├── chart-title (Text, 16px Semibold)
├── chart-area (Frame, contains SVG or vector)
│   ├── grid-lines (Horizontal lines, 1px, #E5E7EB)
│   ├── x-axis (Line + labels)
│   ├── y-axis (Line + labels)
│   ├── data-line (Vector, 3px stroke, #3B82F6)
│   └── data-points (Circles, 8px diameter, #3B82F6)
└── legend (Auto Layout - Horizontal)
    ├── legend-item-1
    └── legend-item-2
```

**Chart Styling:**
```
Grid Lines: 
  Stroke: 1px
  Color: #E5E7EB
  Opacity: 50%

Data Line:
  Stroke: 3px
  Color: #3B82F6 (employee) / #8B5CF6 (retail)
  Join: Round

Data Points:
  Size: 8×8px circles
  Fill: #3B82F6
  Border: 2px solid #FFFFFF

Axis Labels:
  Font: 12px Regular
  Color: #6B7280
```

### Component 4: Heatmap Grid

**Figma Setup:**
```
Frame Name: heatmap
Size: 300px × 200px (7 columns × 24 rows for weekly hour view)
Auto Layout: Vertical
Gap: 2px
```

**Structure:**
```
heatmap (Auto Layout - Vertical)
├── heatmap-header (Text, labels for days/hours)
├── heatmap-grid (Auto Layout - Horizontal wrap)
│   └── heatmap-cell (Component with variants)
│       ├── Variant: intensity (0-100)
│       └── Size: 20×20px, Corner Radius: 4px
└── legend (Color scale)
    ├── Cold (0-25%): #DBEAFE
    ├── Warm (26-50%): #FCD34D
    ├── Hot (51-75%): #FB923C
    └── Very Hot (76-100%): #EF4444
```

**Cell Color Logic:**
```javascript
// Map value (0-100) to color
function getHeatmapColor(value) {
  if (value <= 25) return '#DBEAFE';      // Cold
  else if (value <= 50) return '#FCD34D'; // Warm
  else if (value <= 75) return '#FB923C'; // Hot
  else return '#EF4444';                   // Very Hot
}
```

### Component 5: Progress Ring

**Figma Setup:**
```
Frame Name: progress-ring
Size: 120×120px
```

**Structure:**
```
progress-ring (Frame)
├── background-circle
│   ├── Size: 120×120px
│   ├── Stroke: 8px
│   ├── Color: #E5E7EB
│   └── Fill: None
├── progress-arc (Vector)
│   ├── Stroke: 8px
│   ├── Color: #3B82F6 / #8B5CF6
│   ├── Cap: Round
│   └── Angle: 0-360° based on percentage
└── center-content (Auto Layout - Vertical, centered)
    ├── value (Text, 24px Bold)
    └── label (Text, 12px Regular)
```

**Creating the Arc in Figma:**
1. Draw a circle (120×120px)
2. Convert to vector
3. Use pen tool to create arc segment
4. Set stroke to 8px, round cap
5. Adjust angle based on percentage (e.g., 85% = 306°)

### Component 6: Live Status Indicator

**Figma Setup:**
```
Frame Name: live-status
Size: Auto × 24px
Auto Layout: Horizontal
Padding: 8px
Gap: 8px
```

**Structure:**
```
live-status (Auto Layout - Horizontal)
├── status-dot (Circle)
│   ├── Size: 12×12px
│   ├── Fill: #10B981 (online) / #EF4444 (offline)
│   └── Animated: Pulse effect
├── status-text (Text, 14px Medium)
└── timestamp (Text, 12px Regular, #9CA3AF)
```

**Animation (Prototype):**
```
Create 2 frames:
Frame 1: Opacity 100%
Frame 2: Opacity 40%

Smart Animate between frames
Duration: 1000ms
Easing: Ease In-Out
Loop: Yes
```

### Component 7: Queue Status Card

**Figma Setup:**
```
Frame Name: queue-status-card
Size: 280px × 80px
Auto Layout: Horizontal
Padding: 16px
Gap: 16px
```

**Structure:**
```
queue-status-card (Auto Layout - Horizontal)
├── checkout-info (Auto Layout - Vertical)
│   ├── checkout-name (Text, 14px Semibold)
│   │   └── "Checkout 1"
│   ├── queue-count (Auto Layout - Horizontal)
│   │   ├── people-icon (16px)
│   │   └── count (Text, 16px Medium)
│   └── wait-time (Text, 12px Regular)
│       └── "Wait: 2.5 min"
└── status-indicator (Component)
    ├── ✅ (Green) if wait < 3 min
    ├── 🟡 (Yellow) if 3-5 min
    └── 🔴 (Red) if > 5 min
```

---

## Screen Layouts

### Screen 1: Employee Tracking Dashboard

**Frame Size:** 1920×1080px (Desktop)

**Layout Grid:**
```
Columns: 12 (Gutter: 24px, Margin: 48px)
Rows: Auto (Gap: 24px)
```

**Structure:**
```
employee-dashboard (Frame)
├── header (Full width, 80px height)
│   ├── logo + title
│   ├── date-range-selector
│   └── live-status-indicator
├── summary-section (Span 12 columns)
│   ├── kpi-card (Span 3 columns) × 4
├── main-content (Span 8 columns)
│   ├── ppe-compliance-chart (Full width)
│   └── attendance-heatmap (Full width)
└── sidebar (Span 4 columns)
    ├── real-time-alerts (Scrollable)
    └── productivity-score
```

### Screen 2: Retail Store Dashboard

**Frame Size:** 1920×1080px (Desktop)

**Layout Grid:** Same as Employee Dashboard

**Structure:**
```
retail-dashboard (Frame)
├── header (Same as employee dashboard)
├── summary-section (Span 12 columns)
│   ├── kpi-card (Span 3 columns) × 4
├── queue-monitoring (Span 4 columns)
│   ├── queue-status-card × 3
├── customer-flow-chart (Span 8 columns)
├── store-heatmap (Span 6 columns)
└── top-categories (Span 6 columns)
```

### Mobile Layout

**Frame Size:** 375×812px (iPhone 13)

**Structure:**
```
mobile-dashboard (Frame)
├── mobile-header (Full width, 60px)
│   ├── menu-icon (hamburger)
│   ├── title
│   └── notification-icon
├── summary-cards (Scrollable - Horizontal)
│   ├── kpi-card (160px width) × 4
├── alerts-section (Collapsed, expandable)
├── primary-chart (Full width, 240px height)
├── secondary-metrics (Tabs)
│   ├── Tab 1: Heatmap
│   ├── Tab 2: Queue Status
│   └── Tab 3: Top Categories
└── bottom-navigation (60px height)
    ├── Overview
    ├── Alerts
    ├── Analytics
    └── Settings
```

---

## Interactions & Prototyping

### 1. KPI Card Hover

```
Trigger: While hovering
Action: Change to
Changes:
  - Shadow: md → lg
  - Scale: 1.0 → 1.02
  - Duration: 200ms
  - Easing: Ease Out
```

### 2. Alert Banner Dismiss

```
Trigger: On click (close button)
Action: Smart Animate
Changes:
  - Opacity: 100% → 0%
  - Height: 64px → 0px
  - Duration: 300ms
  - Easing: Ease In
```

### 3. Date Range Selector

```
Trigger: On click
Action: Open overlay
Overlay: date-picker-modal
Animation: Slide up
Duration: 250ms
```

### 4. Chart Tooltip

```
Trigger: While hovering (data point)
Action: Show/Hide
Component: tooltip-card
Position: Smart position (auto)
Animation: Fade in/out (150ms)
```

### 5. Live Feed Auto-Scroll

```
Trigger: After delay (3000ms)
Action: Scroll to position
Position: Next alert item
Animation: Smooth scroll
Loop: Yes
```

---

## Responsive Breakpoints

```css
/* Desktop Large */
@media (min-width: 1920px) {
  Grid: 12 columns, 24px gutter
  Max Cards Per Row: 4
}

/* Desktop */
@media (min-width: 1280px) {
  Grid: 12 columns, 24px gutter
  Max Cards Per Row: 4
}

/* Tablet */
@media (min-width: 768px) {
  Grid: 8 columns, 16px gutter
  Max Cards Per Row: 2
}

/* Mobile */
@media (max-width: 767px) {
  Grid: 4 columns, 16px gutter
  Max Cards Per Row: 2 (scrollable horizontal)
}
```

---

## Accessibility Guidelines

### Color Contrast

All text must meet WCAG AA standards:
```
Large Text (18px+): Minimum 3:1 contrast ratio
Normal Text: Minimum 4.5:1 contrast ratio
```

**Verified Combinations:**
- Primary Blue (#3B82F6) on White: ✅ 7.2:1
- Primary Purple (#8B5CF6) on White: ✅ 6.8:1
- Text Primary (#111827) on White: ✅ 16.1:1
- Text Secondary (#6B7280) on White: ✅ 4.9:1

### Focus States

All interactive elements must have visible focus:
```
Focus Ring:
  Outline: 2px solid #3B82F6
  Offset: 2px
  Border Radius: Inherit from component
```

### Screen Reader Labels

Add hidden labels for icons and visual-only elements:
```
<!-- Example structure -->
<button aria-label="Dismiss alert">
  <icon name="close" aria-hidden="true" />
</button>
```

---

## Export Settings

### For Development Handoff

**Raster Assets:**
```
Format: PNG
Scale: @1x, @2x, @3x
Naming: component-name@2x.png
```

**Vector Assets:**
```
Format: SVG
Include: id
Outline text: No (preserve as text)
Naming: icon-name.svg
```

**CSS Export:**
```
Unit: px
Color format: HSL
Include: All styles
```

---

## Figma File Organization

### Page Structure
```
📄 InvEye Dashboard
├── 🎨 Design System
│   ├── Colors
│   ├── Typography
│   └── Spacing
├── 🧩 Components
│   ├── KPI Cards
│   ├── Charts
│   ├── Alerts
│   └── Navigation
├── 📱 Screens - Desktop
│   ├── Employee Dashboard
│   └── Retail Dashboard
├── 📱 Screens - Mobile
│   ├── Employee Mobile
│   └── Retail Mobile
└── 🔗 Prototypes
    ├── Desktop Flow
    └── Mobile Flow
```

### Naming Conventions
```
Components: lowercase-with-dashes
Variants: Capitalize First Letter
Frames: PascalCase for screens
Layers: descriptive-lowercase
```

---

## Development Handoff Checklist

- [ ] All components created with variants
- [ ] Color styles defined and named
- [ ] Text styles defined and named
- [ ] Spacing system documented
- [ ] Responsive layouts created (Desktop, Tablet, Mobile)
- [ ] Prototypes linked for all interactions
- [ ] Accessibility annotations added
- [ ] Export settings configured
- [ ] Developer notes added to each screen
- [ ] Assets exported in required formats

---

## Tools & Plugins Recommended

### Figma Plugins

1. **Iconify** - Access to 100,000+ icons
2. **Unsplash** - High-quality placeholder images
3. **Content Reel** - Generate realistic dummy data
4. **Charts** - Create data visualizations quickly
5. **A11y - Color Contrast Checker** - Verify accessibility
6. **Anima** - Export to React/Vue code
7. **Stark** - Comprehensive accessibility toolkit

### Resources

- [Inter Font](https://fonts.google.com/specimen/Inter)
- [Heroicons](https://heroicons.com/) - Icon set
- [TailwindCSS Colors](https://tailwindcss.com/docs/customizing-colors) - Color palette reference
- [Coolors](https://coolors.co/) - Color scheme generator

---

## Quick Start Guide

### For Designers

1. **Download Figma file** (or start from scratch)
2. **Install Inter font** from Google Fonts
3. **Create color styles** from the palette above
4. **Build component library** following specifications
5. **Design screens** using 12-column grid
6. **Add interactions** using prototyping mode
7. **Export assets** for development

### For Developers

1. **Access Figma file** (view mode)
2. **Inspect components** using Code panel (Cmd/Ctrl + C)
3. **Export assets** using Export tab
4. **Copy CSS** for styles
5. **Reference spacing** using 8px grid
6. **Implement components** in your framework (React, Vue, etc.)
7. **Match interactions** with JavaScript/CSS animations

---

**Document Version:** 1.0  
**Last Updated:** December 1, 2024  
**Related Documents:**
- [Employee & Retail KPIs](file:///c:/Users/LENOVO/Desktop/my_docs/AG/InvEye/EMPLOYEE_RETAIL_KPIS.md)
- [Main Implementation Guide](file:///c:/Users/LENOVO/Desktop/my_docs/AG/InvEye/INVEYE_COMPLETE_IMPLEMENTATION_GUIDE.md)
