# Roboi Production Dashboard Demo

A standalone frontend demo matching your production Next.js dashboard, with API integration to the roboi-backend.

## 📁 Files

| File | Description |
|------|-------------|
| `index.html` | Main dashboard with all 6 tabs |
| `styles.css` | Light theme matching production |
| `script.js` | Tab logic, charts, data loading |
| `api.js` | API service with mock fallback |

## 🚀 Quick Start

1. **Open**: Double-click `index.html`
2. **Configure**: Click ⚙️ button (bottom-right) to set your API URL
3. **Test**: Navigate tabs, click alerts, view AI insights

## ⚙️ API Configuration

Click the floating ⚙️ button to configure:
- **Backend URL**: `http://localhost:8000` (default)
- **API Key**: Your backend API key
- **Site ID**: `ro001` (default)

## 📊 Features

### Dashboard Tabs
| Tab | Content |
|-----|---------|
| OVERVIEW | Stats, compliance cards, heatmap, alerts, charts |
| SAFETY | Fire, Smoke, Smoking, Violence metrics |
| OPERATIONS | 5L Testing, Equipment, Vehicle Conversion |
| STAFF | Uniform compliance, FSM presence, greeting |
| CUSTOMERS | Footfall, peak hours, dwell time |
| CAMERAS | Camera grid with status indicators |

### AI Insights Modal
- Evidence carousel
- KPI Score (1-10)
- Uniform/Cleanliness/Safety bars (1-5)
- Quick facts (People, Vehicles, Staff)
- Issues detected badges
- AI Analysis (Overview, Deep Dive, Insights)
- TL;DR summary

## 🔌 Backend Endpoints Used

```
GET /api/v1/sites/{siteId}/summary
GET /api/v1/sites/{siteId}/events
GET /api/v1/sites/{siteId}/analytics?viewType=distribution
GET /api/v1/sites/{siteId}/analytics/object-counts
GET /api/v1/sites/{siteId}/detections
```

## 📝 Notes

- Works offline with mock data (no backend required)
- Date range filter updates all data
- Keyboard shortcuts: `Escape` to close, `←/→` for carousel
