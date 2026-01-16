# 🎯 Pre-trained Face Detection & Recognition Models

## Ready-to-Use Models for YOLO11/Jetson Deployment

---

## 🔍 Face Detection Models

### YOLO Face Detection (Recommended)

| Model | Source | Size | mAP (WIDER) | Download |
|-------|--------|------|-------------|----------|
| **yolov11n-face.pt** | YapaLab | ~6MB | ~93% | [GitHub](https://github.com/YapaLab/yolo-face) |
| **yolov11s-face.pt** | YapaLab | ~20MB | ~94% | [GitHub](https://github.com/YapaLab/yolo-face) |
| **yolov8n-face.pt** | lindevs | ~6MB | 90.3% | [GitHub](https://github.com/lindevs/yolov8-face) |
| **yolov8s-face.pt** | lindevs | ~22MB | 93.4% | [GitHub](https://github.com/lindevs/yolov8-face) |
| **yolov8m-face.pt** | lindevs | ~52MB | 95.1% | [GitHub](https://github.com/lindevs/yolov8-face) |

### Quick Download Commands

```python
# YOLOv11n Face (Recommended for Jetson)
!wget https://github.com/YapaLab/yolo-face/releases/download/v1.0/yolov11n-face.pt

# YOLOv8n Face (Alternative)
!wget https://github.com/lindevs/yolov8-face/releases/download/v2.0/yolov8n-face.pt

# Direct usage
from ultralytics import YOLO
model = YOLO('yolov11n-face.pt')
results = model.predict(source=0, show=True)
```

---

## 👤 Face Recognition Models (Embeddings)

### InsightFace / ArcFace (Recommended)

| Model | Backbone | Size | Accuracy (LFW) | Best For |
|-------|----------|------|----------------|----------|
| **buffalo_l** | ResNet | 150MB | 99.8% | High accuracy |
| **buffalo_s** | MobileNet | 30MB | 99.5% | Balanced |
| **buffalo_sc** | MobileNet | 17MB | 99.2% | Edge devices |

```python
# Install InsightFace
!pip install insightface onnxruntime-gpu

# Usage
from insightface.app import FaceAnalysis

app = FaceAnalysis(name='buffalo_sc', providers=['CUDAExecutionProvider'])
app.prepare(ctx_id=0, det_size=(640, 640))

# Detect + Extract embeddings
faces = app.get(image)
for face in faces:
    embedding = face.embedding  # 512-dim vector
```

### FaceNet

| Model | Framework | Size | Accuracy (LFW) | Download |
|-------|-----------|------|----------------|----------|
| **facenet-512** | TensorFlow | 95MB | 99.6% | [GitHub](https://github.com/davidsandberg/facenet) |
| **facenet-keras** | Keras | 92MB | 99.4% | [Keras-FaceNet](https://github.com/nyoki-mtl/keras-facenet) |

```python
# Using deepface library (easiest)
!pip install deepface

from deepface import DeepFace

# Get embedding
embedding = DeepFace.represent(img_path, model_name="Facenet512")
```

### EdgeFace (Optimized for Edge)

| Model | Params | Size | Accuracy | Platform |
|-------|--------|------|----------|----------|
| **EdgeFace-base** | 1.1M | 4.5MB | 98.7% | CPU/GPU |
| **EdgeFace-small** | 0.6M | 2.4MB | 97.9% | Edge/Mobile |

```python
# EdgeFace - ultra-lightweight
!pip install edgeface

from edgeface import EdgeFace
model = EdgeFace(variant='base')
embedding = model.get_embedding(face_image)
```

---

## 🚀 Complete Pipeline for Petrol Pump

### Option 1: YOLO + InsightFace (Production)

```python
from ultralytics import YOLO
from insightface.app import FaceAnalysis
import cv2

# Face Detection
detector = YOLO('yolov11n-face.pt')

# Face Recognition
recognizer = FaceAnalysis(name='buffalo_sc')
recognizer.prepare(ctx_id=0)

# Process frame
results = detector.predict(frame)
for box in results[0].boxes:
    x1, y1, x2, y2 = map(int, box.xyxy[0])
    face_crop = frame[y1:y2, x1:x2]
    
    # Get embedding
    faces = recognizer.get(face_crop)
    if faces:
        embedding = faces[0].embedding
        # Compare with database...
```

### Option 2: DeepFace (Easy Setup)

```python
from deepface import DeepFace

# All-in-one detection + recognition
result = DeepFace.verify(img1_path, img2_path, model_name="Facenet512")
print(f"Same person: {result['verified']}")

# Find similar face in database
dfs = DeepFace.find(img_path, db_path="employee_faces/", model_name="Facenet512")
```

---

## 📦 Pre-trained Model Downloads

### Direct Links

| Model | URL | Size | Notes |
|-------|-----|------|-------|
| YOLOv11n-face | [Download](https://github.com/YapaLab/yolo-face/releases) | 6MB | Best for Jetson |
| YOLOv8n-face v2 | [Download](https://github.com/lindevs/yolov8-face/releases/download/v2.0/yolov8n-face.pt) | 6MB | Stable |
| InsightFace buffalo_sc | Auto-download | 17MB | Best embed for edge |
| SCRFD-10GF | [InsightFace](https://github.com/deepinsight/insightface/tree/master/detection/scrfd) | 4MB | Fast detection |

### HuggingFace Models

```python
# YOLO Face from HuggingFace
from huggingface_hub import hf_hub_download

# Download YOLOv8 face model
model_path = hf_hub_download(repo_id="arnabdhar/YOLOv8-Face-Detection", filename="yolov8n-face.pt")
```

---

## ⚡ Jetson Deployment

### Convert to TensorRT

```bash
# On Jetson device
yolo export model=yolov11n-face.pt format=engine half=True device=0

# For InsightFace ONNX → TensorRT
trtexec --onnx=buffalo_sc.onnx --saveEngine=buffalo_sc.engine --fp16
```

### Performance on Jetson Orin Nano

| Model | Format | FPS | Latency |
|-------|--------|-----|---------|
| YOLOv11n-face | TensorRT FP16 | 60+ | ~15ms |
| YOLOv8n-face | TensorRT FP16 | 55+ | ~18ms |
| buffalo_sc | ONNX | 25+ | ~40ms |
| EdgeFace | ONNX | 50+ | ~20ms |

---

## 🔗 Resources

| Resource | Link |
|----------|------|
| YapaLab YOLO-Face | https://github.com/YapaLab/yolo-face |
| lindevs YOLOv8-Face | https://github.com/lindevs/yolov8-face |
| InsightFace | https://github.com/deepinsight/insightface |
| DeepFace | https://github.com/serengil/deepface |
| EdgeFace | https://github.com/otroshi/edgeface |
| FaceNet PyTorch | https://github.com/timesler/facenet-pytorch |

---

## 📋 Recommendation for Petrol Pump

| Use Case | Detection | Recognition | Notes |
|----------|-----------|-------------|-------|
| **Employee Attendance** | YOLOv11n-face | InsightFace buffalo_sc | Best accuracy |
| **Customer Counting** | YOLOv11n-face | None (just count) | Fastest |
| **VIP Detection** | YOLOv11n-face | EdgeFace | Low memory |
| **Unknown Person Alert** | YOLOv11n-face | InsightFace | Compare vs database |

**My Recommendation**: Use **YOLOv11n-face.pt** for detection + **InsightFace buffalo_sc** for recognition. This gives the best balance of speed and accuracy for Jetson deployment.
