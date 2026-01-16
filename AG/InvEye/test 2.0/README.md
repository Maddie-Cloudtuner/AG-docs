# InvEye Detection Analytics Dashboard v2.0

Real-time CCTV detection monitoring dashboard powered by InvEye and CloudTuner.ai.

## Features

- **Live Camera Feeds**: 4-camera grid showing CAFETERIA, EMPLOYEE_AREA, RECEPTION_AREA, BOSS_CABIN
- **Critical Event Alerts**: Real-time notifications for restricted access violations
- **KPI Cards**: 
  - Restricted Access violations (BOSS_CABIN)
  - Peak Occupancy tracking
  - Total Detection counts
  - System Health monitoring
- **Interactive Charts**:
  - People count timeline by camera
  - Camera distribution doughnut chart
  - Events frequency bar chart
- **Object Detection Summary**: Horizontal bar chart showing detected objects
- **Detection Log Table**: Searchable log of all detections

## Deploy to Vercel

1. Install Vercel CLI (if not already installed):
   ```bash
   npm i -g vercel
   ```

2. Navigate to this folder:
   ```bash
   cd "test 2.0"
   ```

3. Deploy:
   ```bash
   vercel
   ```

4. Follow the prompts to deploy.

## Local Development

```bash
# Using npx serve
npx serve .

# Or with Python
python -m http.server 8000
```

Then open http://localhost:3000 (or http://localhost:8000)

## File Structure

```
test 2.0/
├── index.html          # Main dashboard HTML
├── styles.css          # CloudTuner.ai design system
├── app.js              # Detection data processing & charts
├── detection_log (1).json  # Sample detection data
├── package.json        # Project metadata
├── vercel.json         # Vercel deployment config
└── README.md           # This file
```

## Data Format

The dashboard reads from `detection_log (1).json` which contains:

- **METRIC** entries: Regular camera data with people count and object detections
- **EVENT** entries: Critical alerts (e.g., RESTRICTED_ACCESS_BOSS_CABIN)

Each entry includes:
- `meta`: timestamp, camera ID, site, status
- `data/event`: people count, detection array with labels and confidence scores

## Technologies

- HTML5 + CSS3 (CloudTuner.ai design system)
- Vanilla JavaScript (ES6+)
- Chart.js for visualizations
- Inter font from Google Fonts

---

© 2024 InvEye by Invincible Ocean • Powered by CloudTuner.ai
