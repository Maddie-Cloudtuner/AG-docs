# Fire & Fight Detection Datasets for YOLOv8

> Comprehensive dataset collection for fine-tuning YOLOv8 on Jetson Orin Nano

---

## 🔥 Fire & Smoke Detection Datasets

### Primary Datasets (YOLO-Ready)

| Dataset | Size | Classes | Format | Link |
|---------|------|---------|--------|------|
| **D-Fire** | 21,000+ images | Fire, Smoke | YOLO | [GitHub](https://github.com/gaiasd/DFireDataset) |
| **FIRESENSE** | 49 videos | Fire, Smoke | Video/Frames | [Zenodo](https://zenodo.org/record/836749) |
| **FireNet** | 2,700+ images | Fire, Normal | Image Classification | [Kaggle](https://www.kaggle.com/datasets/phylake1337/fire-dataset) |
| **Wildfire Smoke** | 737 images | Smoke | YOLO | [Kaggle](https://www.kaggle.com/datasets/dataclusterlabs/wildfire-smoke-detection) |

### Roboflow Universe (Pre-formatted YOLO)

| Dataset | Images | Classes | Link |
|---------|--------|---------|------|
| **Fire Detection v2** | 7,000+ | Fire, Smoke | [Roboflow](https://universe.roboflow.com/fire-detection-kbsxn/fire-detection-qagzv) |
| **Fire & Smoke Dataset** | 4,500+ | Fire, Smoke, Neutral | [Roboflow](https://universe.roboflow.com/fire-smoke-detection/fire-and-smoke-xspvt) |
| **Indoor Fire Detection** | 2,100+ | Fire | [Roboflow](https://universe.roboflow.com/fire-detection-v4rka/fire-detection-b3yfq) |
| **Smoke Detection** | 3,200+ | Smoke | [Roboflow](https://universe.roboflow.com/smoke-detection-cdyif/smoke-detection-iyy4l) |
| **Fire Extinguisher + Fire** | 1,800+ | Fire, Extinguisher | [Roboflow](https://universe.roboflow.com/object-detection-bdcfa/fire-detection-pjbqs) |

### Academic/Research Datasets

| Dataset | Description | Source |
|---------|-------------|--------|
| **BoWFire** | Benchmark for fire detection | [GitHub](https://github.com/pedbrgs/Fire-Detection-CNN) |
| **FD-Dataset** | Forest fire dataset | [IEEE DataPort](https://ieee-dataport.org/open-access/forest-fire-dataset) |
| **Corsican Fire** | Mediterranean wildfire images | [Kaggle](https://www.kaggle.com/datasets/brsdincer/corsican-fire-database) |

---

## 👊 Fight/Violence Detection Datasets

### Video-Based Violence Datasets

| Dataset | Size | Type | Link |
|---------|------|------|------|
| **RWF-2000** | 2,000 clips | Real-world fights | [GitHub](https://github.com/mcheng89/real-world-fight-dataset) |
| **Hockey Fight** | 1,000 clips | Sports violence | [Kaggle](https://www.kaggle.com/datasets/yassershrief/hockey-fight-videos) |
| **Movies Fight** | 200 clips | Movie scenes | [Kaggle](https://www.kaggle.com/datasets/naveenk903/movies-fight-detection-dataset) |
| **Surveillance Fight** | 300 clips | CCTV footage | [GitHub](https://github.com/seymanurakti/fight-detection-surveillance) |
| **XD-Violence** | 4,754 videos | Multi-scene violence | [GitHub](https://roc-ng.github.io/XD-Violence/) |

### Frame-Based Violence/Aggression

| Dataset | Images | Classes | Link |
|---------|--------|---------|------|
| **Violence Detection Frames** | 4,000+ | Violence, Non-violence | [Kaggle](https://www.kaggle.com/datasets/mohamedmustafa/real-life-violence-situations-dataset) |
| **Crowd Violence** | 2,000+ | Fighting, Normal | [Roboflow](https://universe.roboflow.com/violence-detection) |
| **Aggression Detection** | 1,500+ | Aggressive poses | [GitHub](https://github.com/Ademord/violence-detection) |

### Pose-Based Fight Detection (Recommended for Jetson)

| Dataset | Type | Use Case | Link |
|---------|------|----------|------|
| **NTU RGB+D** | Skeleton data | Action recognition | [GitHub](https://rose1.ntu.edu.sg/dataset/actionRecognition/) |
| **Kinetics-Violence** | Subset of Kinetics | Fighting actions | [DeepMind](https://deepmind.com/research/open-source/kinetics) |
| **Penn Action** | Pose annotations | Action classification | [Penn](https://dreamdragon.github.io/PennAction/) |

---

## 🎯 Combined/Multi-Class Datasets

| Dataset | Classes | Best For | Link |
|---------|---------|----------|------|
| **Anomaly Detection** | Fire, Fight, Accident | Surveillance | [UCF-Crime](https://www.kaggle.com/datasets/odins0n/ucf-crime-dataset) |
| **COCO + Fire** | 80+ objects + Fire | Multi-task | Custom merge required |
| **OpenImages V7** | 600+ classes | Diverse detection | [Google](https://storage.googleapis.com/openimages/web/index.html) |

---

## 📥 Download Instructions

### Roboflow (Recommended - YOLO Format Ready)

```python
from roboflow import Roboflow

# Fire Detection
rf = Roboflow(api_key="YOUR_API_KEY")
project = rf.workspace("fire-detection-kbsxn").project("fire-detection-qagzv")
dataset = project.version(2).download("yolov8")

# Smoke Detection
project = rf.workspace("smoke-detection-cdyif").project("smoke-detection-iyy4l")
dataset = project.version(1).download("yolov8")
```

### Kaggle Datasets

```bash
# Install Kaggle CLI
pip install kaggle

# Download fire dataset
kaggle datasets download -d phylake1337/fire-dataset

# Download violence dataset
kaggle datasets download -d mohamedmustafa/real-life-violence-situations-dataset
```

### GitHub Datasets

```bash
# D-Fire Dataset
git clone https://github.com/gaiasd/DFireDataset.git

# RWF-2000 (Fight Detection)
git clone https://github.com/mcheng89/real-world-fight-dataset.git
```

---

## 🔧 Dataset Preparation for YOLOv8

### Merge Multiple Datasets

```yaml
# combined_dataset.yaml
path: ./datasets/combined
train: train/images
val: valid/images
test: test/images

names:
  0: person
  1: fire
  2: smoke
  3: fighting
  # Add your existing classes here
```

### Directory Structure

```
datasets/
└── combined/
    ├── train/
    │   ├── images/
    │   └── labels/
    ├── valid/
    │   ├── images/
    │   └── labels/
    └── test/
        ├── images/
        └── labels/
```

### Label Format (YOLO)

```
# Each .txt file per image
# class_id x_center y_center width height (normalized 0-1)
1 0.45 0.32 0.15 0.20  # fire
2 0.60 0.50 0.30 0.40  # smoke
3 0.25 0.45 0.20 0.35  # fighting
```

---

## 🚀 Training on Jetson Orin Nano

### Optimized Training Command

```python
from ultralytics import YOLO

model = YOLO('yolov8n.pt')  # Start with nano for Jetson

model.train(
    data='combined_dataset.yaml',
    epochs=100,
    imgsz=640,
    batch=8,        # Adjust based on memory
    device=0,
    half=True,      # FP16 for speed
    workers=4,
    patience=20,
    save=True,
    project='fire_fight_detection'
)

# Export to TensorRT for Jetson deployment
model.export(format='engine', half=True, device=0)
```

---

## 📊 Recommended Dataset Combinations

### For InvEye Product

| Use Case | Datasets to Combine |
|----------|---------------------|
| **Industrial Safety** | D-Fire + Smoke Detection + Your objects |
| **Retail Security** | Violence Frames + Fire Detection + Person |
| **General Surveillance** | UCF-Crime + Fire + COCO subset |

### Minimum Recommended Sizes

| Class | Min Images | Recommended |
|-------|------------|-------------|
| Fire | 2,000 | 5,000+ |
| Smoke | 1,500 | 3,000+ |
| Fighting | 2,000 | 4,000+ |

---

## 📝 Notes

1. **Augmentation**: Use Albumentations for fire color variations
2. **Class Balance**: Ensure equal representation across classes
3. **Negative Samples**: Include normal scenes to reduce false positives
4. **Video Frames**: Extract diverse frames, not consecutive ones
5. **Jetson Optimization**: Use YOLOv8n or YOLOv8s for best performance

---

*Last Updated: December 2024*
