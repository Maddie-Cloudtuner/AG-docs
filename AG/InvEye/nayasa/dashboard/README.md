# InvEye Nayara - Fuel Station Compliance Dashboard

**Professional AI-powered fuel station monitoring and compliance tracking dashboard**

---

## 🎯 Overview

This is a production-ready web dashboard for Nayara fuel station operations, featuring:

- **73 KPIs** organized by severity (VERY CRITICAL, CRITICAL, MODERATE)
- Real-time CCTV monitoring (24 cameras)
- AI-powered compliance tracking
- Fuel quality monitoring (ATG integration)
- Regulatory certificate management
- CloudTuner.ai design system

---

## 🚀 Quick Start

### Option 1: Direct Open
Simply open `index.html` in any modern browser (Chrome, Firefox, Edge, Safari).

### Option 2: Local Server (Recommended)
```bash
# Using Python (if installed)
python -m http.server 8000

# Using Node.js http-server (if installed)
npx -y http-server -p 8000

# Then open: http://localhost:8000
```

---

## 📁 File Structure

```
dashboard/
├── index.html      # Main dashboard page
├── styles.css      # CloudTuner.ai design system
├── data.js         # Mock data (alerts, CCTV, fuel metrics)
├── chart.js        # Chart.js configuration
├── app.js          # Main application logic
└── README.md       # This file
```

---

## 🎨 Design System

### Color Scheme (CloudTuner.ai Brand)
- **Primary**: Purple/Pink Gradient (`#8B5CF6` → `#EC4899`)
- **Severity Colors**:
  - 🔥 **RED** (`#EF4444`): VERY CRITICAL alerts
  - ⚠️ **ORANGE** (`#F59E0B`): CRITICAL alerts
  - 🟡 **YELLOW** (`#EAB308`): MODERATE alerts
  - ✅ **GREEN** (`#10B981`): Compliant/Normal

### Typography
- **Font**: Inter (Google Fonts)
- **Weights**: 300, 400, 500, 600, 700, 800

---

## 📊 Features

### 1. Compliance Score Banner
- Overall compliance percentage
- Breakdown by severity (RED/ORANGE/YELLOW/GREEN)
- Trend indicator

### 2. 73 KPIs Organized by Severity
- **VERY CRITICAL (RED)**: 32 KPIs
  - Fire Safety, Fuel Quality, Equipment Integrity
- **CRITICAL (ORANGE)**: 27 KPIs
  - Operations, Customer Service, Documentation
- **MODERATE (YELLOW)**: 14 KPIs
  - Housekeeping, HR, Environmental

### 3. Live CCTV Grid
- 6 camera feeds displayed (out of 24 total)
- Zone-based monitoring:
  - Forecourt Entry
  - DU Islands
  - Tanker Bay
  - Cash Counter
  - Perimeter

### 4. Real-Time Alert Feed
- Color-coded by severity
- Includes location, camera ID, timestamp
- Click to view details

### 5. Fuel Tank Monitoring (ATG Integration)
- Real-time fuel levels (MS & HSD)
- Density tracking with tolerance
- Water contamination alerts
- Visual level indicators

### 6. Regulatory Certificates
- PESO License
- Fire NOC
- Weights & Measures
- Pollution Control
- Expiry tracking with warnings

### 7. Fuel Dispensing Chart
- Hourly MS (Petrol) and HSD (Diesel) data
- Animated line chart
- Interactive tooltips

---

## 🔧 Customization

### Changing Station
Edit in `index.html`:
```html
<select id="locationSelect">
    <option>Your Station Name</option>
</select>
```

### Updating Data
Edit `data.js`:
```javascript
const mockData = {
    alerts: [...],
    cctvFeeds: [...],
    fuelData: {...},
    // ... etc
};
```

### Modifying Colors
Edit `styles.css`:
```css
:root {
    --primary-500: #8B5CF6;  /* Change primary color */
    --pink-500: #EC4899;     /* Change accent color */
    /* ... etc */
}
```

---

## 🌐 Browser Support

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Edge 90+
- ✅ Safari 14+

---

## 📦 Dependencies

### External Libraries (CDN)
- **Chart.js 4.4.0**: Fuel dispensing chart
  - Loaded from: `https://cdn.jsdelivr.net/npm/chart.js@4.4.0`
- **Google Fonts - Inter**: Typography
  - Loaded from: `https://fonts.googleapis.com`

### No npm install required!
This is a **zero-build**, pure HTML/CSS/JS dashboard.

---

## 🔐 Security & Production Notes

### Current State (Demo)
- Mock data (no real API calls)
- No authentication
- Client-side only

### For Production Deployment
1. **Backend Integration**:
   - Replace `mockData` with REST API calls
   - Add WebSocket for real-time updates
   - Integrate with ATG, POS, DU systems

2. **Authentication**:
   - Add login page
   - Role-based access (Station Manager, Regional Manager)
   - Session management

3. **Security Headers**:
   - CSP (Content Security Policy)
   - CORS configuration
   - HTTPS enforcement

4. **Performance**:
   - Lazy load CCTV feeds
   - Implement pagination for alerts
   - Cache static assets

---

## 📱 Responsive Design

The dashboard is fully responsive:
- **Desktop** (≥ 1400px): Full layout with 3-column CCTV grid
- **Tablet** (768px - 1399px): 2-column CCTV grid
- **Mobile** (< 768px): Single column, stacked layout

---

## 🎯 Next Steps

### Recommended Enhancements
1. **Video Integration**:
   - RTSP stream integration
   - Fullscreen camera modal
   - Video playback controls

2. **Advanced Analytics**:
   - Historical data comparison
   - Predictive alerts (ML-based)
   - Custom report generation

3. **Mobile App**:
   - React Native version
   - Push notifications
   - Offline support

4. **Multi-Station View**:
   - Regional Manager dashboard
   - Compare multiple stations
   - Aggregate metrics

---

## 📞 Support

For technical support or feature requests:
- **Product**: InvEye (Nayara Edition)
- **Platform**: cloudtuner.ai
- **Edge Processing**: maigic.ai

---

## 📄 License

Internal use only - Nayara Petroleum Retail Operations

---

**Version**: 1.0  
**Last Updated**: December 8, 2024  
**Status**: Production-Ready Demo

---

## 🎨 Screenshots

> **Note**: Open `index.html` in browser to see the live dashboard

### Key Features
- Compliance Score: 91%
- Active Alerts: 23 (2 RED, 7 ORANGE, 14 YELLOW)
- CCTV Uptime: 95%
- Fuel Quality: 100% Compliant
