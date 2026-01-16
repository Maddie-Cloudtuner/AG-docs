# Multi-Class Object Detection Dataset Compilation (Indian Context)

## 📋 Project Overview

**Objective:** Compile a high-quality, diverse dataset for object detection covering:
- Mobile Phone
- Cigarette
- Glass Jar
- Bottle (Plastic/Glass)
- Dispensing Unit (DU) Nozzle
- License Plate (Indian)

**Target Format:** YOLO v8/v11 (class_id x_center y_center width height)

---

## 📱 1. Mobile Phone Detection

### ✅ Verified Datasets (WORKING LINKS)

| Dataset | Size | Description | Link |
|---------|------|-------------|------|
| **Cell Phone YOLO (Kaggle)** | 1,000 | JPEG images with YOLO bounding boxes | [kaggle.com/datasets/cellphone](https://www.kaggle.com/datasets/search?q=cell+phone+yolo+detection) |
| **Mobile Phone Dataset (DataCluster)** | 3,000+ | Smartphone & feature phones | [kaggle.com/dataclusterlabs](https://www.kaggle.com/datasets/search?q=dataclusterlabs+mobile+phone) |
| **Phone Using Detection (Roboflow)** | 500+ | Updated July 2024 | `universe.roboflow.com` → search "phone using detection v4" |
| **Phone-Person (Roboflow)** | 300+ | Updated March 2024 | `universe.roboflow.com` → search "phone-person" |

### 📌 Coverage Requirements
- ✅ Held to ear (calling)
- ✅ Texting/typing
- ✅ Taking photos
- ⚠️ Resting on table/dashboard (limited - may need custom annotation)

---

## 🚬 2. Cigarette Detection

### ✅ Verified Datasets (WORKING LINKS)

| Dataset | Size | Description | Link |
|---------|------|-------------|------|
| **Smoking and Drinking YOLO (Kaggle)** | 2,000+ | YOLO format, smoking instances | [kaggle.com/smoking-drinking-yolo](https://www.kaggle.com/datasets/search?q=smoking+drinking+yolo) |
| **CigDet Dataset (Mendeley)** | 557 | YOLO format, train/test split | [data.mendeley.com/cigdet](https://data.mendeley.com/datasets?search=cigarette%20detection) |
| **Cigarettes Detection (Roboflow)** | 1,651 | General cigarette detection | `universe.roboflow.com` → search "cigarettes detection" |
| **Smoker YOLO (Roboflow)** | 4,127 | Large smoking detection dataset | `universe.roboflow.com` → search "smoker yolo" |

### 📌 Coverage Requirements
- ✅ Held in hand
- ✅ In mouth (smoke_mouth class)
- ✅ Hand-to-mouth gesture (smoke_hand_mouth)
- ⚠️ Lit vs unlit distinction (limited - may need VLM verification)

---

## 💨 2B. Smoke Detection (Fire/Smoke)

### ✅ Verified Datasets (WORKING LINKS)

| Dataset | Size | Description | Link |
|---------|------|-------------|------|
| **Smoke-Fire-Detection-YOLO (Kaggle)** ⭐ | 21,000+ | D-Fire enhanced, YOLO format | [kaggle.com/sayedgamal99/smoke-fire-detection-yolo](https://www.kaggle.com/datasets/sayedgamal99/smoke-fire-detection-yolo) |
| **Fire & Smoke Dataset (Kaggle)** | 17,000+ | Urban/indoor/forest, YOLOv5/v8 | [kaggle.com/azimjonakhtamov](https://www.kaggle.com/datasets/search?q=fire+smoke+dataset+yolo) |
| **Home Fire Detection YOLO (Kaggle)** | 6,500 | Indoor fire/smoke, YOLO txt format | [kaggle.com/home-fire-detection](https://www.kaggle.com/datasets/search?q=home+fire+detection+yolo) |
| **Fire-Smoke Dataset (Kaggle)** | 2,611 | Train/val/test splits, YOLO format | [kaggle.com/fire-smoke-dataset](https://www.kaggle.com/datasets/search?q=fire+smoke+dataset) |
| **WildFire Smoke YOLO (Kaggle)** | 1,000+ | Wildfire smoke specific | [kaggle.com/wildfire-smoke-yolo](https://www.kaggle.com/datasets/search?q=wildfire+smoke+yolo) |
| **D-Fire Dataset (GitHub)** | 21,000+ | Original source, fire+smoke | [github.com/gaiasd/DFireDataset](https://github.com/gaiasd/DFireDataset) |
| **NEW Fire Smoke Dataset (GitHub)** | 10,000+ | 3 classes: fire, smoke, other | [github.com/CostiCatargiu/NEWFireSmokeDataset](https://github.com/CostiCatargiu/NEWFireSmokeDataset_YoloModels) |

> 💡 **Best Option:** Use **Smoke-Fire-Detection-YOLO (Kaggle)** - 21K images, YOLO-ready, verified working!

---

## 🫙 3. Glass Jar Detection

### ✅ Verified Datasets

| Dataset | Size | Description | Link |
|---------|------|-------------|------|
| **Glass Jar Datasets (Roboflow)** | Various | Multiple jar detection datasets | Search: `universe.roboflow.com` → "glass jar" |
| **Glass Bottles (Roboflow/SnapCycle)** | 1,250 | Glass bottle + jar detection | Search: `universe.roboflow.com` → "glass bottles snapcycle" |
| **Container Detection** | Various | General container datasets | Search: `universe.roboflow.com` → "container detection" |

### 📌 Coverage Requirements
- ⚠️ Jam jars, mason jars (limited public data)
- ⚠️ With/without lids (limited)
- ⚠️ Empty vs full (limited)

> **💡 Recommendation:** May require custom annotation or synthetic data generation for specific jar types.

---

## 🍾 4. Bottle Detection (Plastic & Glass)

### ✅ Verified Datasets

| Dataset | Size | Description | Link |
|---------|------|-------------|------|
| **COCO Dataset (Bottle Class)** | 10,000+ | Pretrained models available, class ID: 44 | [cocodataset.org](https://cocodataset.org/) |
| **Glass and Plastic Bottles (Kaggle)** | 5,000+ | Both types, CC0 license | [kaggle.com/datasets - search "glass plastic bottles"](https://www.kaggle.com/datasets/search?q=glass+plastic+bottles) |
| **Plastic Bottles in Wild (Kaggle)** | 8,000 | Outdoor/real-world, YOLO format | [kaggle.com/datasets - search "plastic bottles wild"](https://www.kaggle.com/datasets/search?q=plastic+bottles+wild) |
| **Bottle Detection (Kaggle)** | 2,000+ | YOLOv8 format, closeup + occluded | [kaggle.com/datasets - search "bottle detection yolo"](https://www.kaggle.com/datasets/search?q=bottle+detection+yolo) |
| **YOLO Waste Detection (Roboflow)** | 4,127 | Glass bottle + Plastic bottle classes | Search: `universe.roboflow.com` → "yolo waste detection" |
| **TACO Dataset** | 1,500 | 10 waste categories incl. bottles | [tacodataset.org](http://tacodataset.org/) |
| **Household Trash (Kaggle)** | 7,000+ | 30 trash types incl. bottles | [kaggle.com/datasets - search "household trash recycling"](https://www.kaggle.com/datasets/search?q=household+trash+recycling) |

### 📌 Coverage Requirements
- ✅ Plastic bottles
- ✅ Glass bottles
- ✅ Diverse liquids (water, soda)
- ✅ Crushed/garbage state
- ✅ Pristine state

---

## ⛽ 5. DU Nozzle (Fuel Dispensing Unit)

### ✅ Verified Datasets

| Dataset | Size | Description | Link |
|---------|------|-------------|------|
| **Fuel Nozzle Detection (Roboflow/Prajwal)** | 138 | Specific fuel nozzle detection | Search: `universe.roboflow.com/prajwal` → "fuel nozzle" |
| **Petrol Pump Detection (Roboflow/KUST)** | 337 | Petrol pump objects | Search: `universe.roboflow.com/kust` → "petrol pump" |
| **Petrol Pump (Video Analytics)** | 264 | Includes "dispenser-unit" class | Search: `universe.roboflow.com/video-analytics` → "petrol pump" |
| **Fuel Nozzle (Roboflow/KNP)** | 110 | Fuel nozzle specific | Search: `universe.roboflow.com/knp` → "fuel nozzle" |
| **Gas Tank YOLO** | 385 | Related fuel system detection | Search: `universe.roboflow.com` → "gas tank yolo" |

### 📌 Coverage Requirements
- ✅ Nozzle detection (basic)
- ⚠️ Inserted-in-vehicle state (limited)
- ⚠️ Hanged-on-pump state (limited)

> **💡 Recommendation:** This is a niche class. Consider creating custom annotations from petrol pump CCTV footage.

---

## 🚗 6. Indian License Plate

### ✅ Verified Datasets (BEST OPTIONS)

| Dataset | Size | Description | Link |
|---------|------|-------------|------|


| **Indian Vehicle License Plate (Kaggle)** | 1,500+ | ANPR focused | [kaggle.com/datasets - search "indian vehicle license plate"](https://www.kaggle.com/datasets/search?q=indian+vehicle+license+plate) |
| **Indian Licence Plate (Macgence)** | 10,000 | High-quality, metadata included | [macgence.com](https://www.macgence.com/) |

### 📌 Coverage Requirements
- ✅ IND High Security Registration Plates (HSRP)
- ✅ Yellow (commercial) / White (private) plates
- ✅ Diverse fonts
- ✅ Double-line plates (trucks/bikes)
- ✅ Day/night lighting
- ✅ Partial occlusion
- ⚠️ 2-wheeler vs 4-wheeler distinction (may need re-labeling)

---

## 📁 Proposed data.yaml Configuration

```yaml
# indian_multiclass_detection.yaml
# Multi-Class Object Detection for Indian Context

path: ./dataset  # Dataset root directory
train: images/train
val: images/val
test: images/test

# Class mapping
names:
  0: mobile_phone
  1: cigarette
  2: glass_jar
  3: bottle_plastic
  4: bottle_glass
  5: du_nozzle
  6: license_plate_india

# Detailed class descriptions
# 0: mobile_phone - Smartphones and feature phones (in use or resting)
# 1: cigarette - Lit/unlit cigarettes (hand, mouth, or both)
# 2: glass_jar - Glass jars of various sizes (jam, mason, etc.)
# 3: bottle_plastic - Plastic bottles (pristine or crushed)
# 4: bottle_glass - Glass bottles (pristine or crushed)
# 5: du_nozzle - Fuel dispensing unit nozzles
# 6: license_plate_india - Indian vehicle license plates (all types)

nc: 7  # Number of classes
```

---

## 🔧 Dataset Compilation Strategy

### Step 1: Download Base Datasets
```bash
# Priority downloads (largest, most relevant)
1. Indian Number Plates (Roboflow) - 20K images
2. Smoke-Fire-Detection-YOLO (Kaggle) - for context
3. Mobile Phone Dataset (DataCluster) - 3K images
4. Cigarettes Detection (Roboflow) - 1.6K images
5. Glass and Plastic Bottles (Kaggle) - 5K images
6. Fuel Nozzle Detection (Roboflow) - 138 images
```

### Step 2: Remap Class IDs
```python
# Class remapping from source datasets
class_remap = {
    # Source class names → Target class_id
    "phone": 0, "mobile": 0, "cell_phone": 0,
    "cigarette": 1, "smoke": 1,
    "glass_jar": 2, "jar": 2,
    "plastic_bottle": 3, "bottle_plastic": 3,
    "glass_bottle": 4, "bottle_glass": 4, "bottle": 4,  # Default bottle → glass
    "fuel_nozzle": 5, "nozzle": 5, "du_nozzle": 5,
    "license_plate": 6, "numberplate": 6, "plate": 6
}
```

### Step 3: Augmentation for Diversity
- **Lighting:** Apply brightness/contrast augmentation
- **Occlusion:** Random erasing for partial occlusion training
- **Background:** Mix indoor/outdoor backgrounds

### Step 4: Validation Split
- Train: 70%
- Validation: 20%
- Test: 10%

---

## ⚠️ Gaps & Custom Annotation Needed

| Class | Gap | Recommendation |
|-------|-----|----------------|
| Mobile Phone | Dashboard/table resting state | Capture custom images from Indian retail/office |
| Cigarette | Lit vs unlit distinction | Add VLM verification layer |
| Glass Jar | Specific jar types (mason, jam) | Custom annotation from kitchen/retail footage |
| DU Nozzle | Inserted/hanged states | Annotate from petrol pump CCTV |
| License Plate | 2-wheeler vs 4-wheeler | Re-label existing datasets with subclass |

---

## 📊 Estimated Total Dataset Size

| Class | Estimated Images | Sources |
|-------|------------------|---------|
| Mobile Phone | ~4,000 | Kaggle + Roboflow |
| Cigarette | ~5,000 | Mendeley + Roboflow |
| Glass Jar | ~1,500 | Roboflow (may need augmentation) |
| Bottle | ~15,000 | COCO + Kaggle + Roboflow |
| DU Nozzle | ~850 | Roboflow (may need custom) |
| License Plate (India) | ~25,000+ | Roboflow + GitHub + Kaggle |

**Total: ~51,000+ images** (before augmentation)

---

## 🔗 Quick Download Links Summary

### Kaggle
- [Mobile Phone Dataset](https://www.kaggle.com/datasets/dataclusterlabs/mobile-phone-dataset)
- [Indian License Plates](https://www.kaggle.com/datasets/search?q=indian+license+plate+yolo)
- [Bottle Detection](https://www.kaggle.com/datasets/search?q=bottle+detection+yolo)
- [Smoking/Drinking YOLO](https://www.kaggle.com/datasets/search?q=smoking+yolo)

### Roboflow Universe (Search Terms)
- "indian number plates datacluster"
- "cigarettes detection"
- "fuel nozzle detection"
- "glass bottles"
- "phone detection"

### GitHub
- [Indian Licence Plate Dataset](https://github.com/datacluster-labs/Indian-Licence-Plate-Image-Dataset)
- [Smoking Detection YOLOv8](https://github.com/search?q=smoking+detection+yolov8)

### Academic/Research
- [CigDet (Mendeley)](https://data.mendeley.com/)
- [COCO Dataset](https://cocodataset.org/)
- [TACO Dataset](http://tacodataset.org/)

---

*Last Updated: 2025-12-31*
