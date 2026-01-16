# 🚀 InvEye Petrol Pump Analytics - Plug & Play

## Complete Video Analytics for Petrol Pump Deployment on Jetson Orin Nano

---

## ⚡ One-Click Setup

### Windows
```batch
setup_windows.bat
```

### Jetson / Linux
```bash
chmod +x setup_jetson.sh && ./setup_jetson.sh
```

This automatically:
- ✅ Creates all required directories
- ✅ Installs dependencies
- ✅ Downloads AI models
- ✅ Sets up face database

---

## 🎮 Quick Test (Webcam)

```bash
python petrol_pump_analytics.py --test
```

Press **Q** to quit, **S** for stats, **J** to output JSON.

---

## 🏭 Production Deployment

### Step 1: Configure Cameras

Edit `petrol_pump_config.yaml`:

```yaml
cameras:
  - id: "pump_entrance"
    source: "rtsp://admin:password@192.168.1.101:554/stream1"
    fps_limit: 15
    
  - id: "pump_area_1"
    source: "rtsp://admin:password@192.168.1.102:554/stream1"
    fps_limit: 15
    
  - id: "pump_area_2"
    source: "rtsp://admin:password@192.168.1.103:554/stream1"
    fps_limit: 15
    
  - id: "cash_counter"
    source: "rtsp://admin:password@192.168.1.104:554/stream1"
    fps_limit: 15
```

### Step 2: Register Employees

```bash
# From image
python petrol_pump_analytics.py --register "Rajesh Kumar" photos/rajesh.jpg

# From webcam
python register_faces.py --person "Amit Singh" --webcam

# Bulk from folder
python register_faces.py --folder employee_photos/
```

### Step 3: Run

```bash
python petrol_pump_analytics.py --config petrol_pump_config.yaml
```

---

## 📊 JSON Analytics Output

The system outputs real-time analytics to `analytics_output.json`:

```json
{
  "face_stats": {
    "total_unique_faces": 45,
    "returning_faces_today": 12,
    "employees_present": 3,
    "unknown_faces_today": 30
  },
  "kpi_summary": {
    "today": {
      "total": 8,
      "smoking": 1,
      "mobile_phone": 3
    }
  },
  "incidents": [...],
  "camera_stats": {...}
}
```

See `sample_output.json` for complete example.

---

## 🎯 Detected KPIs (From Your Spreadsheet)

### 🚨 CRITICAL
| KPI | Description | Detection |
|-----|-------------|-----------|
| Smoking | Smoking in fuel area | Cigarette detection |
| Fire | Fire detected | Flame/fire detection |
| Engine Running | Engine on during fueling | Vehicle state |
| Fuel Spill | Fuel spillage | Spill detection |
| Customer Altercation | Physical conflict | Fight detection |

### ⚠️ HIGH
| KPI | Description | Detection |
|-----|-------------|-----------|
| Mobile Phone | Phone use during fueling | Phone detection |
| Child at Pump | Unsupervised child | Child detection |
| Smoke | Smoke detected | Smoke detection |
| Fight | Violence detected | Violence detection |
| Drive-Off | Vehicle leaving unpaid | Vehicle tracking |

### 📋 MEDIUM
| KPI | Description | Detection |
|-----|-------------|-----------|
| Unknown Person | Unregistered person | Face recognition |
| Attendant Presence | Staff in forecourt | Employee tracking |
| Static Touch | Vehicle grounding | Action detection |

### ℹ️ LOW
| KPI | Description | Detection |
|-----|-------------|-----------|
| Queue Length | Vehicles waiting | Vehicle counting |
| Person Count | People in forecourt | Person detection |

---

## 👤 Face Recognition Features

| Feature | Description |
|---------|-------------|
| **Employee Detection** | Identifies registered employees |
| **Returning Visitors** | Tracks repeat customers |
| **Unknown Alerts** | Flags unregistered persons |
| **Visit Counting** | Counts visits per person |
| **Real-time Tracking** | Continuous face tracking |

---

## 📁 File Structure

```
prod ready/
├── petrol_pump_analytics.py    # 🎯 Main plug-and-play script
├── petrol_pump_config.yaml     # Camera configuration
├── setup_windows.bat           # Windows one-click setup
├── setup_jetson.sh             # Jetson one-click setup
├── sample_output.json          # Example JSON output
├── register_faces.py           # Face enrollment tool
├── jetson_deploy.py            # TensorRT conversion
├── main_pipeline.py            # Alternative modular pipeline
├── demo.py                     # Quick demo script
├── requirements.txt            # Dependencies
├── config.yaml                 # Alternative config
├── README.md                   # This file
│
├── models/                     # AI models (auto-downloaded)
│   ├── yolov11n-face.pt        # Face detection
│   └── yolov11n.pt             # Object detection
│
├── face_database/              # Registered faces (auto-created)
│   ├── embeddings.npz
│   └── metadata.json
│
├── incidents/                  # Alert frame captures
│   └── *.jpg
│
└── logs/                       # Log files
```

---

## 🔧 Jetson Optimization

### Convert to TensorRT (2-3x speedup)

```bash
python jetson_deploy.py --convert-all
python jetson_deploy.py --benchmark
```

### Enable Max Performance

```bash
sudo jetson_clocks
sudo nvpmodel -m 0
```

### Expected Performance

| Configuration | FPS per Camera | 4 Cameras Total |
|---------------|----------------|-----------------|
| PyTorch | 8-12 | 32-48 FPS |
| TensorRT FP16 | 15-20 | 60-80 FPS |

---

## 🔌 API Integration

The JSON output can be consumed by any backend:

```python
import json
import time

while True:
    with open('analytics_output.json', 'r') as f:
        data = json.load(f)
    
    # Process data
    incidents = data['incidents']
    face_stats = data['face_stats']
    
    # Send to cloud, trigger alerts, update dashboard...
    
    time.sleep(5)
```

---

## 🛠️ Troubleshooting

### "Models not found"
```bash
# Re-run setup
setup_windows.bat   # or ./setup_jetson.sh
```

### "No GPU detected"
```bash
# Check CUDA
python -c "import torch; print(torch.cuda.is_available())"

# Use CPU (slower)
# Edit config: device: "cpu"
```

### "Camera not opening"
```bash
# Test RTSP
ffplay "rtsp://admin:pass@192.168.1.101:554/stream"

# Check network connectivity
ping 192.168.1.101
```

### "Low FPS"
```bash
# On Jetson
sudo jetson_clocks
python jetson_deploy.py --convert-all
```

---

## 📞 Files Reference

| Need To... | Use This |
|------------|----------|
| Quick test | `python petrol_pump_analytics.py --test` |
| Production run | `python petrol_pump_analytics.py --config petrol_pump_config.yaml` |
| Register faces | `python register_faces.py --person "Name" --webcam` |
| Convert for Jetson | `python jetson_deploy.py --convert-all` |
| Simple demo | `python demo.py` |

---

## ✅ Checklist for Deployment

- [ ] Run setup script
- [ ] Test with webcam
- [ ] Edit `petrol_pump_config.yaml` with camera IPs
- [ ] Register employee faces
- [ ] Run production script
- [ ] Verify JSON output
- [ ] (Jetson) Convert models to TensorRT
- [ ] Set up auto-start on boot

---

**Made for InvEye - Petrol Pump Video Analytics**
