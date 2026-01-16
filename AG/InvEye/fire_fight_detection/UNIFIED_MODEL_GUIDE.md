# 🔥👊💨👤 Unified YOLO11n Model Guide

> **Goal**: Train ONE model for complete petrol pump monitoring  
> **Base**: YOLO11n (edge-optimized for Jetson Orin Nano)

---

## Detection Classes

| ID | Class | Priority | Use Case |
|----|-------|----------|----------|
| 0 | `person` | 🔴 High | Customer/employee tracking |
| 1 | `fire` | 🔴 Critical | Fuel fire detection |
| 2 | `smoke` | 🔴 Critical | Early fire warning |
| 3 | `violence` | 🟡 Important | Security incidents |
| 4 | `cigarette` | 🔴 Critical | Ignition hazard at pump |

---

## Data Sources (Aligned with Reference Models)

| Class | Dataset | Reference Model |
|-------|---------|-----------------|
| person | Roboflow people-detection + COCO | Standard |
| fire/smoke | Roboflow fire-detection | [ProFSAM-Fire-Detector](https://huggingface.co/UEmmanuel5/ProFSAM-Fire-Detector) (FASDD) |
| violence | Roboflow violence-detection | [fight_detection_yolov8](https://huggingface.co/Musawer14/fight_detection_yolov8) |
| cigarette | Roboflow smoker-detection | Custom |

---

## Why Single Model?

| Metric | 5 Separate Models | 1 Unified Model |
|--------|-------------------|-----------------|
| **Size** | ~30 MB | **~6 MB** |
| **FPS on Jetson** | 8-12 FPS | **40-50 FPS** |
| **Memory** | ~800 MB | **~180 MB** |
| **Inference** | 5 passes | **1 pass** |

---

## Quick Start

### Google Colab (Free GPU)
1. Open `Unified_YOLO_Training.ipynb`
2. Runtime → Change runtime → **T4 GPU**
3. Add Roboflow API key (free at roboflow.com)
4. Run all cells (~1-2 hours)

### Kaggle (30 hrs/week free GPU)
1. Upload notebook to kaggle.com/code
2. Enable **GPU T4 x2**
3. Run all cells

---

## Deployment on Jetson

### Using Ultralytics
```python
from ultralytics import YOLO

model = YOLO('petrol_pump_yolo11n.pt')

# RTSP camera stream
results = model.predict('rtsp://camera_ip/stream', stream=True)

for result in results:
    for box in result.boxes:
        cls = int(box.cls[0])
        name = ['person', 'fire', 'smoke', 'violence', 'cigarette'][cls]
        conf = float(box.conf[0])
        
        # Alert on critical detections
        if name in ['fire', 'smoke', 'cigarette']:
            print(f"🚨 ALERT: {name} ({conf:.0%})")
```

### Convert to TensorRT (faster)
```bash
# On Jetson device
yolo export model=petrol_pump_yolo11n.pt format=engine half=True
```

---

## Expected Performance

| Metric | Value |
|--------|-------|
| mAP50 | 0.75-0.85 |
| FPS (Jetson Orin Nano) | 40-50 |
| Model Size | ~6 MB |
| ONNX Size | ~12 MB |

---

## Files in This Folder

| File | Description |
|------|-------------|
| `Unified_YOLO_Training.ipynb` | Training notebook |
| `labels.txt` | Class labels (5 classes) |
| `UNIFIED_MODEL_GUIDE.md` | This guide |

---

*Last Updated: December 2024*
