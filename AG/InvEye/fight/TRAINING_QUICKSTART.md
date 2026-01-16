# 👊 Fighting Detection Training - Quick Start Guide

## Overview

This notebook trains YOLO11s to detect **fighting/violence** for the InvEye product on NVIDIA Jetson Orin Nano.

---

## 📊 Datasets Used (30,000+ Images)

| Dataset | Source | Images | Classes |
|---------|--------|--------|---------|
| Violence Detection | Roboflow | ~6,000 | violence, non_violence |
| Violence_maksad | Roboflow | ~8,000 | violence |
| Fight Detection | Roboflow | ~5,000 | fight, no_fight |
| Crime Detection | Roboflow | ~8,000 | Violence, NonViolence, knife, guns |
| **TOTAL** | **Combined** | **~27,000+** | Merged → `fighting`, `normal` |

---

## 🚀 Quick Start (5 Steps)

### Step 1: Open in Colab
Upload `YOLO11_Fighting_Detection_Training.ipynb` to Google Colab.

### Step 2: Enable GPU
- Go to **Runtime** → **Change runtime type** → Select **T4 GPU**

### Step 3: Get Roboflow API Key
1. Create free account at [roboflow.com](https://roboflow.com)
2. Go to Settings → API Keys
3. Copy your API key

### Step 4: Run the Notebook
1. Replace `YOUR_API_KEY_HERE` with your Roboflow API key
2. Run all cells sequentially (Shift + Enter)
3. Training takes ~2-3 hours for 150 epochs on T4 GPU

### Step 5: Download Your Model
- After training, download `best.pt` (your trained model)
- Also get `best.onnx` for DeepStream deployment

---

## 📁 Output Files

| File | Description | Size (approx) |
|------|-------------|---------------|
| `best.pt` | Best performing model | ~22 MB |
| `last.pt` | Last epoch checkpoint | ~22 MB |
| `best.onnx` | ONNX for cross-platform | ~45 MB |

---

## 🎛️ Key Configuration

```python
# In Section 5.1:
MODEL_SIZE = 'yolo11s.pt'  # Using 's' for better accuracy
EPOCHS = 150               # More epochs for action detection
BATCH_SIZE = 16            # Reduce to 8 if OOM error
IMAGE_SIZE = 640
```

---

## 📊 Unified Classes

| ID | Class | Description |
|----|-------|-------------|
| 0 | `fighting` | Violence, physical altercation, aggression |
| 1 | `normal` | Non-violent, normal behavior |

---

## 🚀 Deploying to Jetson

After training, transfer files to Jetson:

```bash
# On Jetson Orin Nano
yolo export model=best.pt format=engine device=0 half=True imgsz=640
```

This creates `best.engine` optimized for Jetson.

---

## 💡 Tips for Better Accuracy

1. **Set appropriate confidence threshold**
   - Start with `conf=0.3` for fighting detection
   - Increase to `conf=0.5` if too many false positives

2. **Use temporal filtering**
   - Require 3+ consecutive frames with fighting detection
   - Reduces false alarms from sudden movements

3. **Fine-tune on your environment**
   - Collect 50-100 frames from your actual CCTV
   - Add as additional training data

---

## ❓ Troubleshooting

| Issue | Solution |
|-------|----------|
| CUDA out of memory | Reduce `BATCH_SIZE` to 8 or 4 |
| Dataset download fails | Check API key, try alternative datasets |
| Low accuracy | Train longer (200+ epochs), add more data |
| Too many false positives | Increase confidence threshold to 0.4-0.5 |

---

## 📚 References

- [Ultralytics YOLO11 Docs](https://docs.ultralytics.com/)
- [Roboflow Violence Datasets](https://universe.roboflow.com/search?q=violence)
- [DeepStream-YOLO](https://github.com/marcoslucianops/DeepStream-Yolo)
