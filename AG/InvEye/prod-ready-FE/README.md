# Nayara Energy - Petrol Pump Analytics Dashboard

Production-ready frontend for InvEye petrol pump video analytics.

## 🚀 Quick Start

### Local Development
```bash
# Using Python
python -m http.server 8080

# Using Node.js
npx serve .
```

Open http://localhost:8080

### Deploy to Vercel
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

Or just drag & drop the folder on [vercel.com](https://vercel.com)

## 📁 Files

| File | Description |
|------|-------------|
| `index.html` | Main dashboard |
| `styles.css` | All styling |
| `app.js` | Charts & real-time logic |
| `vercel.json` | Vercel config |
| `package.json` | NPM config |

## 🔗 Connect to Backend

Edit `app.js`:
```javascript
const CONFIG = {
    analyticsPath: 'YOUR_API_ENDPOINT',
    demoMode: false, // Set to false for live data
};
```

## 📱 Features

- Live CCTV grid
- Real-time alerts
- KPI stat cards
- Incident charts
- Footfall analytics
- Responsive design

---
**Powered by InvEye × CloudTuner.ai**
