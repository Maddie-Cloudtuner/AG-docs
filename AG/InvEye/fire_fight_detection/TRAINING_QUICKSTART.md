# 🔥 Fire Detection Training - Quick Start Guide

## Overview

This notebook trains YOLO11 to detect **fire**, **smoke**, and optionally **fighting/violence** for the InvEye product on NVIDIA Jetson Orin Nano.

---

## 🚀 Quick Start (5 Steps)

### Step 1: Open in Colab
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/)

Upload `YOLO11_Fire_Detection_Training.ipynb` to Google Colab or open directly.

### Step 2: Enable GPU
- Go to **Runtime** → **Change runtime type** → Select **T4 GPU**

### Step 3: Get Roboflow API Key
1. Create free account at [roboflow.com](https://roboflow.com)
2. Go to Settings → API Keys
3. Copy your API key

### Step 4: Run the Notebook
1. Replace `YOUR_API_KEY_HERE` with your Roboflow API key
2. Run all cells sequentially (Shift + Enter)
3. Training takes ~1-2 hours for 100 epochs on T4 GPU

### Step 5: Download Your Model
- After training, download `best.pt` (your trained model)
- Also get `best.onnx` for DeepStream deployment

---

## 📁 Output Files

| File | Description | Size (approx) |
|------|-------------|---------------|
| `best.pt` | Best performing PyTorch model | ~6 MB |
| `last.pt` | Last epoch checkpoint | ~6 MB |
| `best.onnx` | ONNX format for cross-platform | ~12 MB |
| `results.png` | Training curves | ~200 KB |

---

## 🎛️ Key Configuration Options

```python
# In Section 4.1 of the notebook:

MODEL_SIZE = 'yolo11n.pt'  # Options: n, s, m, l, x
EPOCHS = 100               # More = better accuracy
BATCH_SIZE = 16            # Reduce if OOM error
IMAGE_SIZE = 640           # Standard size
```

### Model Size Comparison

| Model | Size | Speed | Accuracy | Best For |
|-------|------|-------|----------|----------|
| yolo11n | 3.2M | ⚡⚡⚡ | ★★☆ | Edge devices |
| yolo11s | 11.2M | ⚡⚡ | ★★★ | Balanced |
| yolo11m | 25.9M | ⚡ | ★★★★ | Higher accuracy |

---

## 🔄 Using Your Own Images

If you have your own fire images instead of using Roboflow:

1. Set `USE_CUSTOM_IMAGES = True` in Section 2.3
2. Upload images to the created folder structure
3. **Important**: Each image needs a `.txt` label file

### Label Format
```
class_id x_center y_center width height
```
Example:
```
0 0.5 0.5 0.3 0.4
```
Where:
- `0` = fire class
- `1` = smoke class
- All values normalized to 0-1

---

## 🚀 Deploying to Jetson

After training, transfer files to Jetson:

```bash
# On Jetson, convert to TensorRT
yolo export model=best.pt format=engine device=0 half=True imgsz=640
```

This creates `best.engine` optimized for Jetson.

---

## ❓ Troubleshooting

| Issue | Solution |
|-------|----------|
| CUDA out of memory | Reduce `BATCH_SIZE` to 8 or 4 |
| Training too slow | Use T4 GPU, reduce `EPOCHS` |
| Low accuracy | Train longer, use larger model |
| Dataset not found | Check Roboflow API key and project name |

---

## 📊 Expected Results

After 100 epochs of training:
- **mAP50**: 0.85-0.95 (fire detection)
- **mAP50-95**: 0.60-0.80
- **Inference Speed**: ~15-30ms per frame on T4

---

## 📚 References

- [Ultralytics YOLO11 Docs](https://docs.ultralytics.com/)
- [Roboflow Fire Datasets](https://universe.roboflow.com/search?q=fire)
- [DeepStream-YOLO](https://github.com/marcoslucianops/DeepStream-Yolo)
