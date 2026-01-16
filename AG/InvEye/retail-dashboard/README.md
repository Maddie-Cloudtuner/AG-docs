# InvEye Retail Analytics Dashboard

## 🚀 How to Run

### Option 1: Quick Start (Easiest)
Simply **double-click** on `index.html` and it will open in your default browser.

### Option 2: Using Python HTTP Server (Recommended)

If you have Python installed, run this command in the retail-dashboard folder:

```bash
# Python 3
python -m http.server 8000

# Then open: http://localhost:8000
```

### Option 3: Using Node.js HTTP Server

If you have Node.js installed:

```bash
# Install http-server globally (one-time)
npm install -g http-server

# Run the server
http-server -p 8000

# Then open: http://localhost:8000
```

### Option 4: Using VS Code Live Server

1. Install "Live Server" extension in VS Code
2. Right-click on `index.html`
3. Select "Open with Live Server"

---

## 📁 File Structure

```
retail-dashboard/
├── index.html          # Main HTML file
├── styles.css          # Retail-specific styling (purple/pink theme)
├── data.js            # Sample retail data (visitors, queues, alerts)
├── chart.js           # Lightweight chart library
├── app.js             # Main application logic
├── run.bat            # Windows batch file to run server
└── README.md          # This file
```

---

## ✨ Features

- **Real-time KPI Cards** - Footfall, conversion rate, dwell time, security events
- **Live Store Cameras** - 4 camera feeds (expandable to 12)
- **Security Alerts** - Shoplifting, suspicious behavior, unauthorized access
- **Queue Monitoring** - Real-time checkout status with wait times
- **Customer Flow Chart** - Hourly visitor and purchase trends
- **Zone Performance** - Heat map showing engagement by department
- **Responsive Design** - Works on desktop, tablet, and mobile

---

## 🎨 Design Highlights

- **Retail-optimized purple/pink gradient theme**
- Premium CloudTuner.ai-inspired design
- Smooth animations and micro-interactions
- Clean, spacious layout for store managers
- High-contrast accessibility colors

---

## 🔄 Real-time Updates

The dashboard simulates real-time updates:
- Visitor count updates every 6 seconds
- Queue wait times fluctuate dynamically
- Conversion rate adjusts realistically
- All data refreshes automatically

---

## 🎯 Interactive Elements

**Try clicking on:**
- Queue items → View detailed queue analytics
- CCTV feeds → Expand to fullscreen view
- Alert "View CCTV" → Shows camera footage location
- Alert "Dismiss" → Removes alert from list
- Location/Date selectors → Change context (logged to console)
- Expand cameras → Show all 12 store cameras

---

## 🛠️ Customization

### Change Colors

Edit `styles.css` and modify the CSS variables:

```css
:root {
    --primary-500: #8B5CF6;  /* Purple */
    --pink-500: #EC4899;     /* Pink accent */
    --success-500: #10B981;  /* Green */
    --warning-500: #F59E0B;  /* Amber */
    --danger-500: #EF4444;   /* Red */
}
```

### Add More Cameras

Edit `data.js` and add to the `cctvFeeds` array:

```javascript
{
    id: 5,
    name: "CAM 5",
    location: "Your Location",
    status: "live",
    thumbnail: "data:image/svg+xml,..."
}
```

### Add More Alerts

Edit `data.js` and add to the `alerts` array.

### Add More Checkout Lanes

Edit `data.js` and add to the `queues` array.

---

## 📊 Data Flow

```
data.js (Sample Data)
    ↓
app.js (Renders to DOM)
    ↓
index.html (Structure)
    ↓
styles.css (Styling)
    ↓
Browser Display
```

---

## 🔌 Connecting to Real Data

To connect to real backend APIs:

1. **Update `data.js`** with API endpoints
2. **Modify `app.js`** to fetch from your backend:

```javascript
async function fetchVisitors() {
    const response = await fetch('https://your-api.com/api/visitors');
    const data = await response.json();
    return data;
}
```

3. **Add WebSocket** for real-time updates:

```javascript
const ws = new WebSocket('wss://your-api.com/ws');
ws.onmessage = (event) => {
    const update = JSON.parse(event.data);
    updateDashboard(update);
};
```

---

## 🌐 Browser Support

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

---

## 📱 Mobile Responsive

The dashboard automatically adapts to:
- **Desktop**: Full 2-column layout
- **Tablet**: Stacked layout with grid adjustments
- **Mobile**: Single column, scrollable

---

## 📈 Retail KPI Categories

### Customer Behavior
- Footfall tracking
- Zone heatmaps
- Customer journey paths
- Queue management

### Sales & Conversion
- Product engagement
- Conversion funnel
- Basket analysis
- Dwell time analytics

### Security & Loss Prevention
- Theft detection
- Suspicious behavior alerts
- Access control monitoring
- Incident logging

### Operations
- Queue optimization
- Staff deployment
- Cleaning schedules
- Display effectiveness

---

## 🎓 Next Steps

1. **Customize the design** - Edit colors, fonts, layout
2. **Add more features** - Customer demographics, heatmaps
3. **Connect to backend** - Replace sample data with real API calls
4. **Integrate with POS** - Sync with point-of-sale system
5. **Deploy** - Host on Netlify, Vercel, or your server

---

## 💡 Tips

- **Open browser console** (F12) to see logged actions
- **Dismiss alerts** to see count decrease
- **Click queue items** to view detailed analytics
- **Refresh page** to reset sample data

---

## 🐛 Troubleshooting

**Dashboard not showing?**
- Make sure all 5 files are in the same folder
- Clear browser cache (Ctrl + Shift + R)
- Check browser console for errors

**Charts not rendering?**
- The chart uses HTML5 Canvas - ensure JavaScript is enabled
- Try a different browser

**Styles look broken?**
- Ensure `styles.css` is in the same folder as `index.html`
- Check that the Google Fonts link is loading

---

## 🔗 Related Dashboards

- **Employee Dashboard**: Located in `../dashboard/` folder
- Uses similar structure but blue theme for employee tracking

---

## 📄 License

This is a demo dashboard for InvEye retail analytics system.

---

**Version:** 1.0  
**Created:** December 3, 2024  
**Theme:** Purple/Pink Retail Premium  
**Inspired by:** CloudTuner.ai design aesthetic
