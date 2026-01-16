# Fighting/Violence Detection Datasets

## Research Summary

Total available images across sources: **30,000+**

---

## Roboflow Datasets (Object Detection with Bounding Boxes)

### 1. Violence Detection (Primary)
- **Workspace**: securityviolence
- **Project**: violence-detection-bxcxf
- **Images**: ~6,160
- **Classes**: `violence`, `non_violence`
- **Format**: YOLOv8

### 2. Violence_maksad
- **Workspace**: jaishreeram-uqqfn
- **Project**: violence_maksad
- **Images**: ~8,290
- **Classes**: `violence`
- **Format**: YOLOv8

### 3. Fight Detection
- **Workspace**: fight-bx8oy
- **Project**: fight-detection-6hkff
- **Images**: ~5,000
- **Classes**: `fight`, `no_fight`
- **Format**: YOLOv8

### 4. Crime Detection
- **Workspace**: berdav
- **Project**: crime_detection-g30fi
- **Images**: ~8,686
- **Classes**: `knife`, `Violence`, `guns`, `NonViolence`
- **Format**: YOLOv8

### 5. Weapon Detection (Bonus)
- **Workspace**: yolov7test
- **Project**: weapon-detection
- **Images**: ~9,670
- **Classes**: `handgun`, `person`, `pistol`, `rifle`, `weapon`, `aggressor`, `knife`
- **Format**: YOLOv8

---

## Kaggle Datasets (Classification/Video)

### 1. Real Life Violence & Non-Violence
- **Images**: 11,063 (extracted from videos)
- **Categories**: Violence (5,832), Non-Violence (5,231)
- **Source**: YouTube real street fights
- **Link**: kaggle.com/datasets/mohamedmustafa/real-life-violence-situations-dataset

### 2. Violence vs Non-Violence: 11K Images
- **Images**: 11,073
- **Resolution**: 416x416
- **Categories**: Violence, Non-Violence

### 3. Human Action Recognition (HAR)
- **Images**: 12,000+
- **Activities**: 15 classes including "fighting"
- **Format**: Classification

### 4. Smart-City CCTV Violence Detection (SCVD)
- **Type**: CCTV footage (preprocessed)
- **Categories**: Violence, Weaponized Violence
- **Best for**: Surveillance applications

### 5. NTU CCTV-Fights Dataset
- **Type**: Video with frame-level annotations
- **Categories**: Fight, Non-Fight
- **Splits**: Train/Valid/Test

---

## Class Mapping Strategy

All datasets merged with unified classes:

| Original Class | Maps To | ID |
|---------------|---------|-----|
| violence, Violence | fighting | 0 |
| fight, Fight, fighting | fighting | 0 |
| aggression, Aggression | fighting | 0 |
| non_violence, NonViolence | normal | 1 |
| no_fight, normal | normal | 1 |

---

## Recommended Dataset Combination

For optimal results with 10k+ images:

1. **Primary**: Violence Detection (Roboflow) - 6k images
2. **Secondary**: Violence_maksad - 8k images  
3. **Tertiary**: Fight Detection - 5k images
4. **Bonus**: Crime Detection - 8k images

**Total: ~27,000 images** with bounding box annotations.

---

## Dataset Quality Notes

### Strengths:
- Multiple angles and lighting conditions
- Real-world scenarios
- Bounding box annotations (not just classification)
- CCTV-specific datasets available

### Potential Issues:
- Some overlap between datasets
- Class imbalance (more violence than non-violence in some)
- Varying annotation quality

### Mitigations Applied:
- Unified class mapping
- Dataset prefix for file naming
- Label file validation during merge
