# InvEye Employee Tracking Dashboard

## 🚀 How to Run

### Option 1: Quick Start (Easiest)
Simply **double-click** on `index.html` and it will open in your default browser.

### Option 2: Using Python HTTP Server (Recommended)

If you have Python installed, run this command in the dashboard folder:

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
dashboard/
├── index.html          # Main HTML file
├── styles.css          # All styling (CloudTuner.ai inspired)
├── data.js            # Sample data (employees, alerts, CCTV)
├── chart.js           # Lightweight chart library
├── app.js             # Main application logic
└── README.md          # This file
```

---

## ✨ Features

- **Real-time KPI Cards** - Present count, compliance rate, alerts, avg time
- **Live CCTV Grid** - 4 camera feeds (expandable to 16)
- **Real-time Alerts** - Critical, high, and medium severity alerts
- **Employee List** - Searchable list with status indicators
- **Attendance Chart** - 7-day trend visualization
- **PPE Compliance** - Live compliance tracking with progress bars
- **Responsive Design** - Works on desktop, tablet, and mobile

---

## 🎨 Design Highlights

- **CloudTuner.ai-inspired premium design**
- Gradient color schemes
- Smooth animations and transitions
- Professional blue/purple theme
- Clean, spacious layout
- Accessible color contrast

---

## 🔄 Real-time Updates

The dashboard simulates real-time updates:
- Employee count updates every 5 seconds
- Compliance rate fluctuates realistically
- All data refreshes automatically

---

## 🎯 Interactive Elements

**Try clicking on:**
- Employee items → Opens profile modal (simulated)
- CCTV feeds → Expands to fullscreen (simulated)
- Alert "View CCTV" → Shows camera footage (simulated)
- Alert "Dismiss" → Removes alert from list
- Search box → Filter employees by name/ID/department
- Location/Date selectors → Change context (logged to console)

---

## 🛠️ Customization

### Change Colors

Edit `styles.css` and modify the CSS variables:

```css
:root {
    --primary-500: #3B82F6;  /* Main blue */
    --purple-500: #8B5CF6;   /* Accent purple */
    --success-500: #10B981;  /* Green */
    --warning-500: #F59E0B;  /* Amber */
    --danger-500: #EF4444;   /* Red */
}
```

### Add More Employees

Edit `data.js` and add to the `employees` array:

```javascript
{
    id: "EMP-XXXX",
    name: "Your Name",
    initials: "YN",
    status: "on-site",
    department: "Your Department",
    clockIn: "9:00 AM"
}
```

### Add More Alerts

Edit `data.js` and add to the `alerts` array.

### Add More CCTV Feeds

Edit `data.js` and add to the `cctvFeeds` array.

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
async function fetchEmployees() {
    const response = await fetch('https://your-api.com/api/employees');
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

## 🎓 Next Steps

1. **Customize the design** - Edit colors, fonts, layout
2. **Add more features** - Employee detail page, analytics charts
3. **Connect to backend** - Replace sample data with real API calls
4. **Deploy** - Host on Netlify, Vercel, or your server

---

## 💡 Tips

- **Open browser console** (F12) to see logged actions
- **Search employees** by typing in the search box
- **Dismiss alerts** to see count decrease
- **Refresh page** to reset sample data

---

## 🐛 Troubleshooting

**Dashboard not showing?**
- Make sure all 4 files are in the same folder
- Clear browser cache (Ctrl + Shift + R)
- Check browser console for errors

**Charts not rendering?**
- The chart uses HTML5 Canvas - ensure JavaScript is enabled
- Try a different browser

**Styles look broken?**
- Ensure `styles.css` is in the same folder as `index.html`
- Check that the Google Fonts link is loading

---

## 📄 License

This is a demo dashboard for InvEye employee tracking system.

---

**Version:** 1.0  
**Created:** December 2, 2024  
**Inspired by:** CloudTuner.ai design aesthetic
