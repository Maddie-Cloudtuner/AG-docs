# 🔥 InvEye Fire & Fight Detection
## DeepStream + YOLO11 for Jetson Orin Nano

> Multi-camera detection system for fire, smoke, fighting, and standard object detection

---

## 📁 Project Files

```
fire_fight_detection/
├── inveye_multi_camera.py    # Main DeepStream pipeline (RUN THIS)
├── cameras.yaml              # Camera configuration (EDIT THIS)
├── config_infer_yolo11.txt   # DeepStream nvinfer config
├── labels.txt                # Detection class labels
├── setup_jetson.sh           # Jetson setup script
├── export_to_deepstream.py   # Model export utility
├── scripts/
│   ├── download_datasets.py  # Download training data
│   ├── merge_datasets.py     # Combine datasets
│   └── train.py              # Train YOLO11
└── README.md
```

---

## 🚀 Quick Start (Jetson Orin Nano)

### Step 1: Initial Setup

```bash
# SSH into Jetson
ssh nvidia@<JETSON_IP>

# Copy files to Jetson
scp -r fire_fight_detection/ nvidia@<JETSON_IP>:~/inveye/

# Run setup script
cd ~/inveye
chmod +x setup_jetson.sh
./setup_jetson.sh
```

### Step 2: Configure Cameras

Edit `cameras.yaml` with your RTSP URLs:

```yaml
cameras:
  - id: cam_entrance
    name: Entrance Camera
    rtsp_url: rtsp://admin:password@192.168.1.101:554/stream1
    
  - id: cam_office1
    name: Office Area 1
    rtsp_url: rtsp://admin:password@192.168.1.102:554/stream1
    
  # Add more cameras...
```

### Step 3: Export Model to TensorRT

```bash
# If you have a trained model:
python3 export_to_deepstream.py --model yolo11s_fire_fight.pt

# Or use base YOLO11 (without fire/fight):
cd ~/ultralytics
python3 export_yolo11.py -w yolo11s.pt --dynamic
cp yolo11s.engine ~/inveye/
```

### Step 4: Run Detection

```bash
cd ~/inveye
python3 inveye_multi_camera.py --config cameras.yaml
```

---

## 🔧 Training Custom Model (On PC with GPU)

### 1. Download Datasets

```bash
python scripts/download_datasets.py
```

### 2. Merge Datasets

```bash
python scripts/merge_datasets.py
```

### 3. Train YOLO11

```bash
python scripts/train.py --model yolo11s.pt --epochs 100
```

### 4. Copy to Jetson & Export

```bash
scp runs/fire_fight/weights/best.pt nvidia@<JETSON_IP>:~/inveye/

# On Jetson:
python3 export_to_deepstream.py --model best.pt
```

---

## 📊 Detection Classes

| ID | Class | Alert |
|----|-------|-------|
| 0 | person | ❌ |
| 2 | car | ❌ |
| 7 | truck | ❌ |
| 80 | **fire** | ✅ 🚨 |
| 81 | **smoke** | ✅ 🚨 |
| 82 | **fighting** | ✅ 🚨 |

---

## ⚡ Performance (4 Cameras)

| Model | FPS per Camera | Total FPS | Memory |
|-------|---------------|-----------|--------|
| YOLO11n | 30+ | 120+ | 2 GB |
| YOLO11s | 25+ | 100+ | 3 GB |
| YOLO11m | 15+ | 60+ | 4 GB |

---

## 🔗 Cloud Integration

Edit `cameras.yaml`:

```yaml
cloud_api:
  url: https://api.cloudtuner.ai/v1/inveye/detections
  key: your-api-key
```

Detection metadata (NOT video) is sent every 90 frames.

---

## 🚨 Alert Notifications

Configure in `cameras.yaml`:

```yaml
alerts:
  alert_cooldown: 30  # seconds
  webhook_url: https://hooks.slack.com/your-webhook
```

---

## 📝 Troubleshooting

| Issue | Solution |
|-------|----------|
| No video display | Check DISPLAY env var, use SSH -X |
| Camera not connecting | Verify RTSP URL with VLC first |
| Low FPS | Use YOLO11n, reduce cameras |
| Engine error | Re-export model on same Jetson |

---

*InvEye - AI Eyes That Never Blink*
