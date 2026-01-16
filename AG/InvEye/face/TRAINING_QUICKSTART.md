# 👤 Face Detection Training - Quick Start Guide

## Petrol Pump Deployment | InvEye Analytics

---

## 🚀 Quick Start

### 1. Open in Google Colab
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/your-repo/blob/main/YOLO11_Face_Detection_Training.ipynb)

Upload `YOLO11_Face_Detection_Training.ipynb` to Google Colab and select **GPU runtime**.

### 2. Get Roboflow API Key
1. Go to [Roboflow](https://app.roboflow.com/)
2. Navigate to **Settings → API**
3. Copy your Private API Key
4. Paste in the notebook

### 3. Run All Cells
The notebook will:
- Download 4+ face detection datasets
- Merge into unified format
- Train YOLO11n model
- Export to `.pt` and `.onnx`

---

## 📊 Datasets Used

| Dataset | Source | Images | Description |
|---------|--------|--------|-------------|
| WIDER Face | Roboflow | 32k+ | Large-scale face benchmark |
| Face Detection | Roboflow | 5k+ | High-quality annotations |
| Multi-Face | Roboflow | 3k+ | Crowded scene detection |
| Human Faces | Roboflow | 2k+ | Diverse lighting/angles |

**Total: 10,000+ images** (after merging)

---

## ⚙️ Training Configuration

```python
MODEL = 'yolo11n.pt'    # Nano - optimized for Jetson
EPOCHS = 100            # Increase for production (150-200)
BATCH_SIZE = 16         # Adjust for GPU memory
IMG_SIZE = 640          # Standard YOLO input
```

---

## 📦 Output Files

After training, you'll get:

| File | Format | Use Case |
|------|--------|----------|
| `best.pt` | PyTorch | General inference |
| `best.onnx` | ONNX | TensorRT conversion |
| `face_detection_deployment.zip` | Package | Ready-to-deploy bundle |

---

## 🔌 Jetson Deployment

### Convert to TensorRT (on Jetson)

```bash
# Install ultralytics
pip install ultralytics

# Convert model
yolo export model=face_detector.pt format=engine half=True device=0

# Test inference
yolo predict model=face_detector.engine source=0 show=True
```

### RTSP Camera Stream

```bash
python run_inference.py --model face_detector.engine \
    --source "rtsp://192.168.1.100:554/stream1" \
    --conf 0.5
```

---

## 📈 Expected Performance

| Metric | Target | Notes |
|--------|--------|-------|
| mAP50 | >0.85 | Detection accuracy |
| mAP50-95 | >0.55 | Strict accuracy |
| Inference | <20ms | On Jetson Orin Nano |
| Model Size | ~6 MB | YOLO11n .pt |

---

## 🎯 Petrol Pump Use Cases

### 1. Employee Attendance
- Auto clock-in/out via face recognition
- Track employee working hours
- Detect unauthorized personnel

### 2. Customer Analytics
- Count unique customers
- Track repeat visitors
- Peak hour analysis

### 3. Security
- Unknown person alerts
- Restricted area monitoring
- Theft prevention (known offenders)

### 4. VIP Detection
- Alert when regular customers arrive
- Personalized service triggers
- Loyalty program integration

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Low mAP | Increase epochs to 150+ |
| OOM Error | Reduce batch size to 8 |
| Slow training | Use T4/A100 GPU |
| Missing faces | Lower confidence threshold |

---

## 📁 File Structure

```
InvEye/face/
├── YOLO11_Face_Detection_Training.ipynb  # Training notebook
├── TRAINING_QUICKSTART.md                 # This guide
├── FACE_DETECTION_USE_CASES.md           # Detailed use cases
└── (after training)
    ├── face_detector.pt                   # Trained model
    ├── face_detector.onnx                 # ONNX export
    └── run_inference.py                   # Inference script
```

---

## 🔗 Related Resources

- [YOLO11 Documentation](https://docs.ultralytics.com/)
- [Roboflow Universe](https://universe.roboflow.com/)
- [Jetson AI Lab](https://www.jetson-ai-lab.com/)
- [DeepStream SDK](https://developer.nvidia.com/deepstream-sdk)
