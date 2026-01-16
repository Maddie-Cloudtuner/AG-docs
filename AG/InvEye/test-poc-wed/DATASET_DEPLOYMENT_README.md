# 🚀 InvEye Dataset & Deployment Toolkit

> **Complete solution for Fire, Fight, and Face Detection on Jetson Orin Nano**

---

## 📦 Contents

| File | Purpose |
|------|---------|
| `PUBLIC_DATASETS_COMPREHENSIVE.md` | Full dataset reference document |
| `download_datasets.py` | Automated dataset downloader |
| `DOWNLOAD_DATASETS.bat` | Windows one-click download |
| `download_datasets.sh` | Linux/Mac download script |
| `merge_datasets.py` | Dataset merger for unified YOLO format |
| `jetson_deploy.py` | Jetson inference & TensorRT export |
| `jetson_setup.sh` | Jetson one-click environment setup |

---

## 🚀 Quick Start

### Step 1: Download Datasets (on PC)

```bash
# Option A: Windows - Double-click
DOWNLOAD_DATASETS.bat

# Option B: Command line
pip install roboflow kaggle requests tqdm gdown
python download_datasets.py --all --roboflow-key YOUR_KEY
```

### Step 2: Merge Datasets

```bash
python merge_datasets.py --input ./datasets --output ./datasets/combined
```

### Step 3: Train Model (Google Colab/Cloud)

```python
from ultralytics import YOLO

model = YOLO('yolov8n.pt')
model.train(data='datasets/combined/data.yaml', epochs=100)
model.export(format='onnx')  # For transfer
```

### Step 4: Deploy on Jetson Orin Nano

```bash
# Copy to Jetson
scp best.pt jetson@192.168.1.100:~/inveye/models/

# On Jetson: Setup (one-time)
sudo ./jetson_setup.sh

# Export to TensorRT
python jetson_deploy.py --model models/best.pt --export

# Run detection
python jetson_deploy.py --model models/best.engine --camera 0
```

---

## 📋 Commands Reference

### Download Datasets

```bash
python download_datasets.py --all              # All categories
python download_datasets.py --fire             # Fire/smoke only
python download_datasets.py --fight            # Fight/violence only
python download_datasets.py --face             # Face detection only
python download_datasets.py --list             # List available datasets
```

### Merge Datasets

```bash
python merge_datasets.py --input ./datasets --output ./datasets/combined
python merge_datasets.py --fire-only           # Fire datasets only
python merge_datasets.py --verify              # Verify merged dataset
```

### Jetson Deployment

```bash
# Export to TensorRT
python jetson_deploy.py --model best.pt --export

# Camera inference
python jetson_deploy.py --model best.engine --camera 0

# RTSP stream
python jetson_deploy.py --model best.engine --rtsp rtsp://ip/stream

# Multi-camera
python jetson_deploy.py --model best.engine --multi-camera 0,1,2,3

# Performance benchmark
python jetson_deploy.py --model best.engine --benchmark

# Headless mode (no display)
python jetson_deploy.py --model best.engine --camera 0 --headless
```

---

## 🔧 Configuration

### Class Mapping

| ID | Class | Alert Priority |
|----|-------|----------------|
| 0 | fire | 🔴 CRITICAL |
| 1 | smoke | 🟠 HIGH |
| 2 | fighting | 🔴 CRITICAL |
| 3 | face | 🟢 INFO |
| 4 | weapon | 🔴 CRITICAL |
| 5 | knife | 🔴 CRITICAL |
| 6 | person | 🟢 INFO |

### Jetson Performance Settings

```python
JETSON_SETTINGS = {
    "imgsz": 640,      # Input size
    "half": True,      # FP16 inference
    "conf": 0.4,       # Confidence threshold
    "iou": 0.5,        # NMS IoU threshold
}
```

---

## 📊 Expected Performance

| Model | Resolution | FPS (Orin Nano) | Notes |
|-------|------------|-----------------|-------|
| YOLOv8n | 640x640 | 45-55 FPS | Best for real-time |
| YOLOv8s | 640x640 | 30-40 FPS | Better accuracy |
| YOLOv8m | 640x640 | 15-25 FPS | High accuracy |

---

## 🔗 API Keys

| Platform | Get Key | Cost |
|----------|---------|------|
| Roboflow | [roboflow.com/account](https://app.roboflow.com/account/api) | Free |
| Kaggle | [kaggle.com/account](https://www.kaggle.com/account) | Free |

---

## 📁 Directory Structure (After Setup)

```
inveye/
├── datasets/
│   ├── fire_smoke/
│   ├── fight_violence/
│   ├── face_detection/
│   └── combined/
│       ├── train/
│       ├── valid/
│       ├── test/
│       └── data.yaml
├── models/
│   ├── best.pt          # PyTorch model
│   └── best.engine      # TensorRT engine
├── outputs/
│   └── alerts_*.json    # Detection alerts
└── scripts/
    ├── download_datasets.py
    ├── merge_datasets.py
    └── jetson_deploy.py
```

---

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| TensorRT export fails | Use `--export` flag, ensure JetPack 5.x |
| Low FPS | Use YOLOv8n, run `jetson_clocks`, set MAXN mode |
| Camera not found | Run `v4l2-ctl --list-devices` |
| RTSP lag | Add `?tcp` to URL, reduce resolution |
| Out of memory | Reduce batch size, use smaller model |

---

## 📞 Support

For issues/questions, refer to:
- [Ultralytics Docs](https://docs.ultralytics.com)
- [NVIDIA Jetson Forums](https://forums.developer.nvidia.com/c/agx-autonomous-machines/jetson-embedded-systems/)
- [Roboflow Universe](https://universe.roboflow.com)

---

*InvEye Team | December 2024*
