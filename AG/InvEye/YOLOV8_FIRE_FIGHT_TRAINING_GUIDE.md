# YOLOv8 Fire & Fight Detection - Complete Training Guide

> End-to-end guide for training and deploying a unified YOLOv8 model on Jetson Orin Nano

---

## 📁 Project Structure

```
fire_fight_detection/
├── datasets/
│   ├── fire/                 # Fire dataset
│   ├── smoke/                # Smoke dataset
│   ├── violence/             # Fight/violence dataset
│   └── combined/             # Merged dataset
│       ├── train/
│       │   ├── images/
│       │   └── labels/
│       ├── valid/
│       │   ├── images/
│       │   └── labels/
│       └── test/
├── scripts/
│   ├── download_datasets.py
│   ├── merge_datasets.py
│   ├── train.py
│   └── export_tensorrt.py
├── models/
│   └── best.pt               # Trained model
├── deploy/
│   └── model.engine          # TensorRT engine
└── combined_dataset.yaml
```

---

## 1️⃣ Dataset Download Script

```python
# scripts/download_datasets.py

import os
import subprocess
import zipfile
import shutil
from pathlib import Path

# Configuration
BASE_DIR = Path("./datasets")
BASE_DIR.mkdir(exist_ok=True)

def download_roboflow_datasets():
    """Download datasets from Roboflow (requires API key)"""
    try:
        from roboflow import Roboflow
        
        # Get API key from environment or input
        api_key = os.environ.get("ROBOFLOW_API_KEY") or input("Enter Roboflow API Key: ")
        rf = Roboflow(api_key=api_key)
        
        # Fire Detection Dataset
        print("📥 Downloading Fire Detection dataset...")
        project = rf.workspace("roboflow-universe-projects").project("fire-detection-pjbqs")
        fire_dataset = project.version(1).download("yolov8", location=str(BASE_DIR / "fire"))
        
        # Smoke Detection Dataset  
        print("📥 Downloading Smoke Detection dataset...")
        project = rf.workspace("smoke-detection-cdyif").project("smoke-detection-iyy4l")
        smoke_dataset = project.version(1).download("yolov8", location=str(BASE_DIR / "smoke"))
        
        print("✅ Roboflow datasets downloaded!")
        return True
        
    except ImportError:
        print("⚠️ Roboflow not installed. Run: pip install roboflow")
        return False

def download_kaggle_datasets():
    """Download datasets from Kaggle"""
    try:
        # Fire Dataset
        print("📥 Downloading Kaggle Fire dataset...")
        subprocess.run([
            "kaggle", "datasets", "download", "-d", 
            "phylake1337/fire-dataset",
            "-p", str(BASE_DIR / "kaggle_fire")
        ], check=True)
        
        # Violence Dataset
        print("📥 Downloading Kaggle Violence dataset...")
        subprocess.run([
            "kaggle", "datasets", "download", "-d",
            "mohamedmustafa/real-life-violence-situations-dataset",
            "-p", str(BASE_DIR / "kaggle_violence")
        ], check=True)
        
        # Unzip files
        for zip_file in BASE_DIR.glob("**/*.zip"):
            print(f"📦 Extracting {zip_file.name}...")
            with zipfile.ZipFile(zip_file, 'r') as z:
                z.extractall(zip_file.parent)
            zip_file.unlink()
            
        print("✅ Kaggle datasets downloaded!")
        return True
        
    except Exception as e:
        print(f"⚠️ Kaggle download failed: {e}")
        return False

def download_github_datasets():
    """Clone datasets from GitHub"""
    repos = [
        ("https://github.com/gaiasd/DFireDataset.git", "dfire"),
    ]
    
    for url, name in repos:
        dest = BASE_DIR / name
        if not dest.exists():
            print(f"📥 Cloning {name}...")
            subprocess.run(["git", "clone", url, str(dest)], check=True)
        else:
            print(f"✓ {name} already exists")
    
    print("✅ GitHub datasets cloned!")

def main():
    print("=" * 50)
    print("🔥 Fire & Fight Detection Dataset Downloader")
    print("=" * 50)
    
    # Try each source
    download_roboflow_datasets()
    download_kaggle_datasets()
    download_github_datasets()
    
    print("\n✅ All available datasets downloaded!")
    print(f"📂 Location: {BASE_DIR.absolute()}")

if __name__ == "__main__":
    main()
```

---

## 2️⃣ Dataset Merger Script

```python
# scripts/merge_datasets.py

import os
import shutil
import random
from pathlib import Path
from collections import defaultdict
import yaml

# Configuration
DATASETS_DIR = Path("./datasets")
OUTPUT_DIR = Path("./datasets/combined")
TRAIN_RATIO = 0.8
VAL_RATIO = 0.15
TEST_RATIO = 0.05

# Class mapping - adjust based on your existing classes
CLASS_MAPPING = {
    # Original classes from your model (adjust IDs)
    "person": 0,
    "car": 1,
    "truck": 2,
    # Add your existing classes here...
    
    # New classes to add
    "fire": 10,
    "smoke": 11,
    "flame": 10,       # Map to fire
    "fighting": 12,
    "violence": 12,    # Map to fighting
    "aggression": 12,  # Map to fighting
}

def create_output_structure():
    """Create output directory structure"""
    for split in ["train", "valid", "test"]:
        (OUTPUT_DIR / split / "images").mkdir(parents=True, exist_ok=True)
        (OUTPUT_DIR / split / "labels").mkdir(parents=True, exist_ok=True)
    print("✅ Output structure created")

def find_dataset_files(dataset_path):
    """Find all image-label pairs in a dataset"""
    pairs = []
    
    # Common dataset structures
    image_dirs = list(dataset_path.glob("**/images")) + \
                 list(dataset_path.glob("**/train")) + \
                 list(dataset_path.glob("**/valid"))
    
    for img_dir in image_dirs:
        # Find corresponding labels directory
        label_dir = img_dir.parent / "labels"
        if not label_dir.exists():
            label_dir = img_dir.parent.parent / "labels" / img_dir.name
        
        if not label_dir.exists():
            continue
            
        for img_file in img_dir.glob("*.*"):
            if img_file.suffix.lower() in [".jpg", ".jpeg", ".png", ".bmp"]:
                label_file = label_dir / f"{img_file.stem}.txt"
                if label_file.exists():
                    pairs.append((img_file, label_file))
    
    return pairs

def remap_labels(label_file, class_name_to_new_id):
    """Remap class IDs in a label file"""
    lines = []
    with open(label_file, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 5:
                old_class_id = int(parts[0])
                # Keep the same ID or remap if needed
                new_class_id = old_class_id  # Modify this based on your mapping
                lines.append(f"{new_class_id} {' '.join(parts[1:])}")
    return lines

def merge_datasets():
    """Merge all datasets into combined directory"""
    all_pairs = []
    
    # Collect files from each dataset
    for dataset_dir in DATASETS_DIR.iterdir():
        if dataset_dir.is_dir() and dataset_dir.name != "combined":
            print(f"📂 Processing {dataset_dir.name}...")
            pairs = find_dataset_files(dataset_dir)
            print(f"   Found {len(pairs)} image-label pairs")
            all_pairs.extend(pairs)
    
    print(f"\n📊 Total pairs found: {len(all_pairs)}")
    
    # Shuffle and split
    random.shuffle(all_pairs)
    
    n_total = len(all_pairs)
    n_train = int(n_total * TRAIN_RATIO)
    n_val = int(n_total * VAL_RATIO)
    
    splits = {
        "train": all_pairs[:n_train],
        "valid": all_pairs[n_train:n_train + n_val],
        "test": all_pairs[n_train + n_val:]
    }
    
    # Copy files to output
    for split_name, pairs in splits.items():
        print(f"\n📁 Creating {split_name} split ({len(pairs)} samples)...")
        
        for i, (img_file, label_file) in enumerate(pairs):
            # Create unique filename
            new_name = f"{split_name}_{i:06d}"
            
            # Copy image
            dst_img = OUTPUT_DIR / split_name / "images" / f"{new_name}{img_file.suffix}"
            shutil.copy2(img_file, dst_img)
            
            # Copy label (with remapping if needed)
            dst_label = OUTPUT_DIR / split_name / "labels" / f"{new_name}.txt"
            shutil.copy2(label_file, dst_label)
        
        print(f"   ✅ {split_name}: {len(pairs)} samples")
    
    return splits

def create_yaml_config(splits):
    """Create dataset YAML configuration"""
    config = {
        "path": str(OUTPUT_DIR.absolute()),
        "train": "train/images",
        "val": "valid/images", 
        "test": "test/images",
        "names": {
            0: "person",
            1: "car",
            2: "truck",
            # Add your existing classes...
            10: "fire",
            11: "smoke",
            12: "fighting"
        }
    }
    
    yaml_path = Path("./combined_dataset.yaml")
    with open(yaml_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    print(f"\n✅ Created {yaml_path}")
    return yaml_path

def print_statistics(splits):
    """Print dataset statistics"""
    print("\n" + "=" * 50)
    print("📊 Dataset Statistics")
    print("=" * 50)
    
    for split_name, pairs in splits.items():
        print(f"\n{split_name.upper()}:")
        print(f"  Images: {len(pairs)}")
        
        # Count classes
        class_counts = defaultdict(int)
        for _, label_file in pairs:
            with open(label_file, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if parts:
                        class_id = int(parts[0])
                        class_counts[class_id] += 1
        
        for class_id, count in sorted(class_counts.items()):
            print(f"  Class {class_id}: {count} instances")

def main():
    print("=" * 50)
    print("🔀 Dataset Merger for Fire & Fight Detection")
    print("=" * 50)
    
    create_output_structure()
    splits = merge_datasets()
    create_yaml_config(splits)
    print_statistics(splits)
    
    print("\n✅ Dataset merging complete!")
    print(f"📂 Output: {OUTPUT_DIR.absolute()}")

if __name__ == "__main__":
    main()
```

---

## 3️⃣ Training Script

```python
# scripts/train.py

import torch
from ultralytics import YOLO
from pathlib import Path
import argparse

def get_device():
    """Detect best available device"""
    if torch.cuda.is_available():
        device = 0
        print(f"🎮 Using GPU: {torch.cuda.get_device_name(0)}")
    else:
        device = "cpu"
        print("💻 Using CPU")
    return device

def train_model(
    base_model: str = "yolov8n.pt",
    data_yaml: str = "combined_dataset.yaml",
    epochs: int = 100,
    imgsz: int = 640,
    batch: int = 16,
    project: str = "fire_fight_detection",
    name: str = "train"
):
    """Train YOLOv8 model on combined dataset"""
    
    print("=" * 50)
    print("🚀 YOLOv8 Fire & Fight Detection Training")
    print("=" * 50)
    
    device = get_device()
    
    # Adjust batch size for Jetson
    if "jetson" in str(torch.cuda.get_device_name(0)).lower() if torch.cuda.is_available() else "":
        batch = 8  # Reduce for Jetson memory
        print(f"⚡ Jetson detected, reducing batch size to {batch}")
    
    # Load model
    print(f"\n📦 Loading base model: {base_model}")
    model = YOLO(base_model)
    
    # Training configuration
    train_args = {
        "data": data_yaml,
        "epochs": epochs,
        "imgsz": imgsz,
        "batch": batch,
        "device": device,
        "project": project,
        "name": name,
        
        # Optimization settings
        "half": True,              # FP16 training
        "cache": True,             # Cache images in RAM
        "workers": 4,              # Data loading workers
        
        # Training hyperparameters
        "optimizer": "AdamW",
        "lr0": 0.001,              # Initial learning rate
        "lrf": 0.01,               # Final learning rate factor
        "momentum": 0.937,
        "weight_decay": 0.0005,
        
        # Augmentation
        "hsv_h": 0.015,            # HSV-Hue augmentation
        "hsv_s": 0.7,              # HSV-Saturation
        "hsv_v": 0.4,              # HSV-Value
        "degrees": 10,             # Rotation
        "translate": 0.1,
        "scale": 0.5,
        "flipud": 0.5,             # Vertical flip (important for fire)
        "fliplr": 0.5,             # Horizontal flip
        "mosaic": 1.0,             # Mosaic augmentation
        "mixup": 0.1,              # Mixup augmentation
        
        # Callbacks
        "patience": 30,            # Early stopping patience
        "save": True,              # Save checkpoints
        "save_period": 10,         # Save every N epochs
        "val": True,               # Run validation
        "plots": True,             # Generate plots
        "verbose": True,
    }
    
    print(f"\n⚙️ Training Configuration:")
    print(f"   Epochs: {epochs}")
    print(f"   Image Size: {imgsz}")
    print(f"   Batch Size: {batch}")
    print(f"   Dataset: {data_yaml}")
    
    # Start training
    print("\n🏋️ Starting training...\n")
    results = model.train(**train_args)
    
    # Print results
    print("\n" + "=" * 50)
    print("📊 Training Complete!")
    print("=" * 50)
    print(f"Best model saved to: {results.save_dir}/weights/best.pt")
    
    # Validate
    print("\n🔍 Running validation...")
    metrics = model.val()
    print(f"   mAP50: {metrics.box.map50:.4f}")
    print(f"   mAP50-95: {metrics.box.map:.4f}")
    
    return model, results

def main():
    parser = argparse.ArgumentParser(description="Train YOLOv8 for Fire & Fight Detection")
    parser.add_argument("--model", default="yolov8n.pt", help="Base model")
    parser.add_argument("--data", default="combined_dataset.yaml", help="Dataset YAML")
    parser.add_argument("--epochs", type=int, default=100, help="Training epochs")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size")
    parser.add_argument("--batch", type=int, default=16, help="Batch size")
    parser.add_argument("--project", default="fire_fight_detection", help="Project name")
    parser.add_argument("--name", default="train", help="Run name")
    
    args = parser.parse_args()
    
    train_model(
        base_model=args.model,
        data_yaml=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        project=args.project,
        name=args.name
    )

if __name__ == "__main__":
    main()
```

---

## 4️⃣ TensorRT Export Script

```python
# scripts/export_tensorrt.py

import torch
from ultralytics import YOLO
from pathlib import Path
import argparse
import subprocess
import sys

def check_tensorrt():
    """Check if TensorRT is available"""
    try:
        import tensorrt
        print(f"✅ TensorRT version: {tensorrt.__version__}")
        return True
    except ImportError:
        print("⚠️ TensorRT not found")
        return False

def export_to_tensorrt(
    model_path: str,
    imgsz: int = 640,
    half: bool = True,
    batch: int = 1,
    workspace: int = 4,  # GB
    output_dir: str = "./deploy"
):
    """Export YOLOv8 model to TensorRT engine"""
    
    print("=" * 50)
    print("🚀 YOLOv8 TensorRT Export for Jetson")
    print("=" * 50)
    
    # Check TensorRT
    has_tensorrt = check_tensorrt()
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Load model
    print(f"\n📦 Loading model: {model_path}")
    model = YOLO(model_path)
    
    # Export configuration
    export_args = {
        "format": "engine",        # TensorRT engine
        "imgsz": imgsz,
        "half": half,              # FP16 for Jetson
        "device": 0,               # GPU
        "batch": batch,
        "workspace": workspace,    # GB workspace
        "simplify": True,          # Simplify ONNX
        "dynamic": False,          # Fixed batch size for speed
        "verbose": True,
    }
    
    print(f"\n⚙️ Export Configuration:")
    print(f"   Image Size: {imgsz}")
    print(f"   Half Precision (FP16): {half}")
    print(f"   Batch Size: {batch}")
    print(f"   Workspace: {workspace} GB")
    
    if not has_tensorrt:
        print("\n⚠️ TensorRT not available. Exporting to ONNX first...")
        export_args["format"] = "onnx"
    
    # Export
    print("\n🔄 Exporting model...")
    exported_path = model.export(**export_args)
    
    print(f"\n✅ Model exported to: {exported_path}")
    
    return exported_path

def create_inference_script():
    """Create Jetson inference script"""
    
    script = '''# jetson_inference.py - Run on Jetson Orin Nano

import cv2
import numpy as np
from ultralytics import YOLO
import time

class FireFightDetector:
    def __init__(self, model_path="model.engine", conf_threshold=0.5):
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold
        
        # Class names
        self.class_names = {
            0: "person",
            10: "fire",
            11: "smoke", 
            12: "fighting"
        }
        
        # Alert colors (BGR)
        self.colors = {
            "fire": (0, 0, 255),      # Red
            "smoke": (128, 128, 128), # Gray
            "fighting": (0, 165, 255), # Orange
            "person": (0, 255, 0)     # Green
        }
    
    def detect(self, frame):
        """Run detection on a frame"""
        results = self.model(frame, conf=self.conf_threshold, verbose=False)
        return results[0]
    
    def draw_results(self, frame, results):
        """Draw bounding boxes and labels"""
        boxes = results.boxes
        
        alerts = []
        
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            
            class_name = self.class_names.get(cls_id, f"class_{cls_id}")
            color = self.colors.get(class_name, (255, 255, 255))
            
            # Draw box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            label = f"{class_name}: {conf:.2f}"
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
            cv2.rectangle(frame, (x1, y1 - 20), (x1 + w, y1), color, -1)
            cv2.putText(frame, label, (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            # Track alerts
            if class_name in ["fire", "smoke", "fighting"]:
                alerts.append({"class": class_name, "confidence": conf})
        
        return frame, alerts
    
    def run_camera(self, source=0):
        """Run detection on camera stream"""
        cap = cv2.VideoCapture(source)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        fps_counter = 0
        fps_start = time.time()
        current_fps = 0
        
        print("🎥 Starting camera detection... Press 'q' to quit")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect
            results = self.detect(frame)
            frame, alerts = self.draw_results(frame, results)
            
            # Calculate FPS
            fps_counter += 1
            if time.time() - fps_start >= 1.0:
                current_fps = fps_counter
                fps_counter = 0
                fps_start = time.time()
            
            # Draw FPS
            cv2.putText(frame, f"FPS: {current_fps}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Show alerts
            if alerts:
                alert_text = " | ".join([f"⚠️ {a['class'].upper()}" for a in alerts])
                cv2.putText(frame, alert_text, (10, 70),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            
            cv2.imshow("Fire & Fight Detection", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="model.engine", help="Model path")
    parser.add_argument("--source", default=0, help="Video source (0 for camera)")
    parser.add_argument("--conf", type=float, default=0.5, help="Confidence threshold")
    
    args = parser.parse_args()
    
    detector = FireFightDetector(
        model_path=args.model,
        conf_threshold=args.conf
    )
    
    # Run camera detection
    detector.run_camera(source=args.source)
'''
    
    script_path = Path("./deploy/jetson_inference.py")
    script_path.parent.mkdir(exist_ok=True)
    
    with open(script_path, 'w') as f:
        f.write(script)
    
    print(f"✅ Created inference script: {script_path}")
    return script_path

def main():
    parser = argparse.ArgumentParser(description="Export YOLOv8 to TensorRT")
    parser.add_argument("--model", default="fire_fight_detection/train/weights/best.pt", 
                       help="Model path")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size")
    parser.add_argument("--batch", type=int, default=1, help="Batch size")
    parser.add_argument("--workspace", type=int, default=4, help="TensorRT workspace (GB)")
    parser.add_argument("--output", default="./deploy", help="Output directory")
    
    args = parser.parse_args()
    
    # Export model
    export_to_tensorrt(
        model_path=args.model,
        imgsz=args.imgsz,
        batch=args.batch,
        workspace=args.workspace,
        output_dir=args.output
    )
    
    # Create inference script
    create_inference_script()
    
    print("\n" + "=" * 50)
    print("📋 Deployment Instructions")
    print("=" * 50)
    print("""
1. Copy files to Jetson Orin Nano:
   scp -r deploy/ jetson@<IP>:~/fire_fight_detection/

2. On Jetson, install dependencies:
   pip install ultralytics opencv-python

3. Run inference:
   python jetson_inference.py --model model.engine --source 0

4. For RTSP stream:
   python jetson_inference.py --model model.engine --source "rtsp://..."
""")

if __name__ == "__main__":
    main()
```

---

## 5️⃣ Complete Workflow

```bash
# Step 1: Setup environment
pip install ultralytics roboflow kaggle pyyaml

# Step 2: Download datasets
python scripts/download_datasets.py

# Step 3: Merge datasets
python scripts/merge_datasets.py

# Step 4: Train model
python scripts/train.py --model yolov8n.pt --epochs 100 --batch 16

# Step 5: Export to TensorRT (on Jetson or with TensorRT installed)
python scripts/export_tensorrt.py --model fire_fight_detection/train/weights/best.pt

# Step 6: Deploy to Jetson
scp -r deploy/ jetson@<JETSON_IP>:~/fire_fight_detection/

# Step 7: Run on Jetson
ssh jetson@<JETSON_IP>
cd ~/fire_fight_detection
python jetson_inference.py --model model.engine --source 0
```

---

## 📊 Expected Performance on Jetson Orin Nano

| Model | FPS (FP16) | mAP50 | Size |
|-------|-----------|-------|------|
| YOLOv8n | 45-60 | ~70% | 6 MB |
| YOLOv8s | 30-40 | ~75% | 22 MB |
| YOLOv8m | 15-25 | ~80% | 52 MB |

### Optimization Tips

1. **Use FP16** - Always enable `half=True` for 2x speedup
2. **Optimize image size** - Try 480 or 416 instead of 640
3. **Batch size 1** - Best latency for real-time
4. **DeepStream** - For multi-stream, use NVIDIA DeepStream SDK
5. **Async processing** - Use separate threads for capture and inference

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Out of memory during training | Reduce batch size to 4-8 |
| TensorRT export fails | Ensure CUDA and TensorRT versions match |
| Low FPS on Jetson | Use smaller model (YOLOv8n) or reduce imgsz |
| Poor detection accuracy | Increase training epochs, add more data |
| False positives | Add negative samples, increase conf threshold |

---

*Last Updated: December 2024*
