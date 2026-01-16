# Public Datasets for AI Model Training

## 🔥 Fire Detection (Indoor - NOT Forest Fire)

### ✅ Verified Indoor Fire Datasets

| Dataset | Size | Description | Link |
|---------|------|-------------|------|
| **Smoke-Fire-Detection-YOLO (D-Fire Kaggle)** | 21,000+ | Indoor + outdoor, YOLO format, fire & smoke classes | [kaggle.com/sayedgamal99/smoke-fire-detection-yolo](https://www.kaggle.com/datasets/sayedgamal99/smoke-fire-detection-yolo) |
| **Fire & Smoke Dataset (Kaggle)** | 17,000+ | Diverse environments incl. indoor, YOLO optimized | [kaggle.com/azimjonakhtamov/fire-smoke](https://www.kaggle.com/datasets/search?q=fire+smoke+yolo+dataset) |
| **Fire Detection YOLO v8 (Roboflow)** | 7,896 | Indoor fire focus, 416x416 format | Search: `universe.roboflow.com` → "fire detection yolo" |
| **Fire Smoke Indoor (Roboflow)** | 2,500 | Indoor fire + smoke specific | Search: `universe.roboflow.com` → "fire smoke indoor" |

> 💡 **Best Choice:** Use **Smoke-Fire-Detection-YOLO (Kaggle)** - 21K images, YOLO-ready, verified working link!

### ⚠️ Outdoor/Forest Fire Datasets (For Reference Only)

| Dataset | Size | Description | Link |
|---------|------|-------------|------|
| **D-Fire Dataset (GitHub)** | 21,000+ | Mixed fire/smoke, original source | [github.com/gaiasd/DFireDataset](https://github.com/gaiasd/DFireDataset) |
| **Wildfire Smoke (AI for Mankind)** | 2,192 | Wildfire smoke only | [github.com/aiformankind/wildfire-smoke-dataset](https://github.com/aiformankind/wildfire-smoke-dataset) |

---

## 💨 Smoke Detection (Separate Datasets)

### ✅ Verified Smoke-Only & Smoke-Focused Datasets

| Dataset | Size | Description | Link |
|---------|------|-------------|------|
| **Smoke Object Detection (HuggingFace)** | 21,578 | Smoke-only, COCO format, 640x640 | [huggingface.co/datasets/keremberke/smoke-object-detection](https://huggingface.co/datasets/keremberke/smoke-object-detection) |
| **Smoke Only (Roboflow)** | 5,210 | Smoke-only annotations | Search: `universe.roboflow.com/thesis-dataset/smoke-only` |
| **Smoke-Fire-Detection-YOLO (Kaggle)** | 5,867 smoke-only images | Has separate "smoke only" subset | [kaggle.com/sayedgamal99/smoke-fire-detection-yolo](https://www.kaggle.com/datasets/sayedgamal99/smoke-fire-detection-yolo) |
| **Wildfire Smoke Dataset (GitHub)** | 2,192 | Bounding box annotated smoke | [github.com/aiformankind/wildfire-smoke-dataset](https://github.com/aiformankind/wildfire-smoke-dataset) |
| **D-Fire Smoke Class** | 11,865 boxes | Smoke annotations from D-Fire | [github.com/gaiasd/DFireDataset](https://github.com/gaiasd/DFireDataset) |

> 💡 **Best for Smoke-Only:** Use **Smoke Object Detection (HuggingFace)** - 21K smoke images, verified working!


## 👊 Fight/Violence Detection

### ✅ Verified Working Links

| Dataset | Size | Description | Link |
|---------|------|-------------|------|
| **Real Life Violence Situations** | 2,000 videos | Real street fights + non-violence | [kaggle.com/real-life-violence-situations-dataset](https://www.kaggle.com/datasets/mohamedmustafa/real-life-violence-situations-dataset) |
| **UCF Crime Dataset** | 1,900 videos | Anomaly detection (violence included) | [kaggle.com/ucf-crime-dataset](https://www.kaggle.com/datasets/odins0n/ucf-crime-dataset) |
| **XD-Violence** | 4,754 videos | Multi-scene violence benchmark (ECCV 2020) | [roc-ng.github.io/XD-Violence](https://roc-ng.github.io/XD-Violence/) |



## 👤 Face Detection & Recognition

### ✅ Verified Working Links (Datasets)

| Dataset | Size | Description | Link |
|---------|------|-------------|------|
| **Face Detection Dataset (Kaggle)** | 16,700 | YOLO format bounding boxes | [kaggle.com/face-detection-dataset](https://www.kaggle.com/datasets/fareselmenshawii/face-detection-dataset) |
| **WIDER FACE** | 32,000+ | Face detection benchmark | [shuoyang1213.me/WIDERFACE](http://shuoyang1213.me/WIDERFACE/) |
| **CelebA** | 202,599 | Celebrity faces with 40 attributes | [mmlab.ie.cuhk.edu.hk/projects/CelebA](http://mmlab.ie.cuhk.edu.hk/projects/CelebA.html) |
| **FFHQ (NVIDIA)** | 70,000 | High-quality 1024×1024 faces | [github.com/NVlabs/ffhq-dataset](https://github.com/NVlabs/ffhq-dataset) |

### 🏆 Best Face Recognition Models for Jetson Orin Nano

| Model | Purpose | Why It's Best | Link |
|-------|---------|---------------|------|
| **RetinaFace** | Face Detection | High accuracy, works in crowds, TensorRT optimized | [InsightFace](https://github.com/deepinsight/insightface) |
| **ArcFace** | Face Recognition | Best accuracy-to-speed ratio on edge devices | [InsightFace](https://github.com/deepinsight/insightface) |
| **EdgeFace** | Recognition (Alt) | Won IJCB 2023 Efficient Face Recognition Competition, edge-optimized | [github.com/otroshi/EdgeFace](https://github.com/otroshi/edgeface) |

### Recommended Pipeline for Jetson

```
Detection: RetinaFace (TensorRT optimized)
     ↓
Embedding: ArcFace or EdgeFace (512-dim vectors)
     ↓
Database: FAISS for fast similarity search
```

### Key Libraries
- **InsightFace** - Open-source, includes ArcFace + RetinaFace
- **TensorRT** - Convert models to engine files for 2-3x speedup
- **DeepStream SDK** - For video stream processing on Jetson



## 🌙 Low-Light & Night Vision Datasets

### Recommended Public Datasets

| Dataset | Description | Best For | Link |
|---------|-------------|----------|------|
| **ExDark Dataset** | 7,363 images in 12 classes captured in low-light | Night object detection | [github.com/cs-chan/Exclusively-Dark-Image-Dataset](https://github.com/cs-chan/Exclusively-Dark-Image-Dataset) |
| **LOL Dataset** | 500 low/normal light pairs | Low-light enhancement | [daooshee.github.io/BMVC2018website](https://daooshee.github.io/BMVC2018website/) |
| **DARK FACE** | 6,000 low-light face images | Night face detection | [flyywh.github.io/CVPRW2019_Face_Deblurring](https://flyywh.github.io/CVPRW2019_Face_Deblurring/) |
| **NightOwls Dataset** | 40+ videos, 280K pedestrian frames | Night pedestrian detection | [cs.ox.ac.uk/datasets/nightowls](https://www.nightowls-dataset.org/) |
| **LLVIP** | 34K visible-infrared pairs | Infrared detection | [bupt-ai-cz.github.io/LLVIP](https://bupt-ai-cz.github.io/LLVIP/) |
|


## 🇮🇳 Indian Condition Datasets

### Datasets with Indian/Diverse Conditions

| Dataset | Description | Relevant For | Link |
|---------|-------------|--------------|------|
| **India Driving Dataset (IDD)** | 10K+ images from Indian cities | Traffic, vehicles, pedestrians | [idd.insaan.iiit.ac.in](https://idd.insaan.iiit.ac.in/) |
| **CrowdHuman** | Dense crowd scenarios | Indian crowd conditions | [www.crowdhuman.org](https://www.crowdhuman.org/) |



## ⛽ Petrol Pump Objects List

### Objects Present at Petrol Pumps (For Detection)

| Category | Objects | Priority | Detection Method |
|----------|---------|----------|------------------|
| **Vehicles** | Car, Motorcycle, Truck, Auto-rickshaw, Bus | High | YOLO |
| **Infrastructure** | Fuel Dispenser (DU), Pump Island, Canopy, Air Machine, Tank Cover | High | YOLO + Custom |
| **Safety** | Fire Extinguisher, Safety Cone, Spill Kit | High | YOLO + Custom |
| **Persons** | Customer, Staff/FSM, Manager | High | YOLO + Face |
| **Equipment** | Fuel Nozzle, Testing Jar (5L), Hose, Receipt Printer | Medium | Custom YOLO |
| **Hazards** | Fire, Smoke, Oil Spill, Open Manhole | Critical | Custom YOLO |
| **Containers** | Plastic Bottle, Jerry Can, Bucket | Medium | YOLO |
| **Actions** | Smoking (Cigarette), Phone Usage, Fighting | Critical | Pose + VLM |
| **Vehicle Parts** | License Plate, Open Fuel Tank | Medium | YOLO + OCR |
| **Hygiene** | Trash, Debris, Stickers on DU | Low | VLM |

### Custom Classes Needed for Training

```yaml
# petrol_pump_classes.yaml
names:
  0: person
  1: car
  2: motorcycle
  3: truck
  4: auto_rickshaw
  5: bus
  6: fuel_dispenser
  7: fuel_nozzle
  8: testing_jar
  9: fire_extinguisher
  10: safety_cone
  11: fire
  12: smoke
  13: cigarette
  14: mobile_phone
  15: license_plate
  16: plastic_bottle
  17: open_manhole
  18: open_du_cover
```


---

## 🚬 Smoking/Pose Detection Datasets

### Cigarette/Smoking Detection

| Dataset | Description | Link |
|---------|-------------|------|
| **Smoking Detection Dataset (Kaggle)** | Search "smoking detection" | [kaggle.com/datasets?search=smoking+detection]https://www.kaggle.com/datasets/sujaykapadnis/smoking
| **Hand Gesture Detection** | For hand-to-mouth poses | https://universe.roboflow.com/none-5ituz/smoking-mvsja

### Pose Estimation Datasets

| Dataset | Size | Use Case | Link |
|---------|------|----------|------|
| **COCO Keypoints** | 200K+ | 17-keypoint pose | [cocodataset.org](https://cocodataset.org/#keypoints-2020) |
| **MPII Human Pose** | 25K images | Full body pose | [human-pose.mpi-inf.mpg.de](http://human-pose.mpi-inf.mpg.de/) |
| **NTU RGB+D** | 60K+ clips | Action + skeleton | [rose1.ntu.edu.sg/dataset/actionRecognition](https://rose1.ntu.edu.sg/dataset/actionRecognition/) |
| **PoseTrack** | 23K frames | Multi-person tracking | [posetrack.net](https://posetrack.net/) |

### Smoking Detection Strategy

```
Pipeline: Pose Estimation → Hand-to-Mouth → VLM Verification

1. YOLO Pose: Detect person + skeleton keypoints
2. Logic: Check if wrist near face (hand-to-mouth gesture)
3. Trigger: Crop ROI around person
4. VLM Query: "Is this person holding a cigarette or smoking?"
5. Result: Confirmed smoking alert
```



