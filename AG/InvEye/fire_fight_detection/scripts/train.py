"""
YOLO11 Training Script for Fire & Fight Detection
Compatible with DeepStream-YOLO export workflow

Train on PC with GPU, then export to Jetson Orin Nano
"""

import torch
from ultralytics import YOLO
from pathlib import Path
import argparse
import os

# Project paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
DEFAULT_DATA = PROJECT_DIR / "combined_dataset.yaml"
DEFAULT_PROJECT = PROJECT_DIR / "runs"


def get_device_info():
    """Get device information and recommended settings"""
    
    if torch.cuda.is_available():
        device = 0
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
        
        print(f"🎮 GPU: {gpu_name}")
        print(f"   Memory: {gpu_memory:.1f} GB")
        
        # Recommend batch size based on GPU memory
        if "jetson" in gpu_name.lower() or gpu_memory < 8:
            recommended_batch = 4
        elif gpu_memory < 12:
            recommended_batch = 8
        elif gpu_memory < 24:
            recommended_batch = 16
        else:
            recommended_batch = 32
            
        return device, recommended_batch
    else:
        print("💻 Using CPU (training will be slow)")
        return "cpu", 4


def download_base_model(model_name: str) -> str:
    """Download YOLO11 base model if not exists"""
    
    model_path = Path(model_name)
    
    if model_path.exists():
        return str(model_path)
    
    # YOLO11 model URLs
    model_urls = {
        "yolo11n.pt": "https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n.pt",
        "yolo11s.pt": "https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11s.pt",
        "yolo11m.pt": "https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11m.pt",
        "yolo11l.pt": "https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11l.pt",
        "yolo11x.pt": "https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11x.pt",
    }
    
    if model_name in model_urls:
        print(f"📥 Downloading {model_name}...")
        import urllib.request
        urllib.request.urlretrieve(model_urls[model_name], model_name)
        print(f"✅ Downloaded {model_name}")
        return model_name
    
    # Let ultralytics handle it
    return model_name


def train_model(args):
    """Train YOLO11 model on fire/fight dataset"""
    
    print("=" * 60)
    print("🔥 YOLO11 Fire & Fight Detection Training")
    print("=" * 60)
    
    # Get device info
    device, recommended_batch = get_device_info()
    
    # Use recommended batch if not specified
    batch = args.batch if args.batch else recommended_batch
    print(f"📦 Batch size: {batch}")
    
    # Verify dataset exists
    data_path = Path(args.data)
    if not data_path.exists():
        print(f"\n❌ Dataset config not found: {data_path}")
        print("   Please run merge_datasets.py first!")
        return None
    
    print(f"\n📄 Dataset: {data_path}")
    
    # Download/load base model
    model_path = download_base_model(args.model)
    print(f"📦 Loading base model: {model_path}")
    model = YOLO(model_path)
    
    # Training configuration optimized for fire/fight detection
    train_config = {
        "data": str(data_path),
        "epochs": args.epochs,
        "imgsz": args.imgsz,
        "batch": batch,
        "device": device,
        "project": str(args.project),
        "name": args.name,
        
        # Precision
        "half": True,              # FP16 for faster training
        "amp": True,               # Automatic mixed precision
        
        # Data loading
        "cache": args.cache,
        "workers": args.workers,
        
        # Optimizer (YOLO11 defaults)
        "optimizer": "AdamW",
        "lr0": 0.001,
        "lrf": 0.01,
        "momentum": 0.937,
        "weight_decay": 0.0005,
        "warmup_epochs": 3.0,
        
        # Augmentation optimized for fire detection
        "hsv_h": 0.015,            # Hue variation
        "hsv_s": 0.7,              # Saturation (fire colors)
        "hsv_v": 0.4,              # Brightness
        "degrees": 10.0,           # Rotation
        "translate": 0.1,
        "scale": 0.5,
        "flipud": 0.5,             # Vertical flip
        "fliplr": 0.5,             # Horizontal flip
        "mosaic": 1.0,             # Mosaic augmentation
        "mixup": 0.1,              # Mixup
        
        # Training behavior
        "patience": args.patience,
        "save": True,
        "save_period": 10,
        "val": True,
        "plots": True,
        "verbose": True,
        "resume": args.resume,
    }
    
    # Print config
    print(f"\n⚙️ Training Configuration:")
    print(f"   Model: YOLO11 ({args.model})")
    print(f"   Epochs: {args.epochs}")
    print(f"   Image Size: {args.imgsz}")
    print(f"   Batch Size: {batch}")
    print(f"   Patience: {args.patience}")
    
    # Start training
    print("\n" + "=" * 60)
    print("🏋️ Starting Training...")
    print("=" * 60 + "\n")
    
    try:
        results = model.train(**train_config)
        
        # Get best model path
        best_model = Path(results.save_dir) / "weights" / "best.pt"
        
        print("\n" + "=" * 60)
        print("✅ Training Complete!")
        print("=" * 60)
        print(f"\n📁 Results: {results.save_dir}")
        print(f"📦 Best model: {best_model}")
        
        # Validation metrics
        print("\n🔍 Running final validation...")
        metrics = model.val()
        
        print(f"\n📊 Validation Results:")
        print(f"   mAP50: {metrics.box.map50:.4f}")
        print(f"   mAP50-95: {metrics.box.map:.4f}")
        print(f"   Precision: {metrics.box.mp:.4f}")
        print(f"   Recall: {metrics.box.mr:.4f}")
        
        return best_model
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Training interrupted")
        print("   Resume with --resume flag")
        return None
    
    except Exception as e:
        print(f"\n❌ Training failed: {e}")
        raise


def main():
    parser = argparse.ArgumentParser(
        description="Train YOLO11 for Fire & Fight Detection",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Model settings
    parser.add_argument("--model", default="yolo11s.pt",
                       help="Base model (yolo11n/s/m/l/x.pt)")
    parser.add_argument("--data", default=str(DEFAULT_DATA),
                       help="Dataset YAML path")
    
    # Training settings
    parser.add_argument("--epochs", type=int, default=100,
                       help="Number of training epochs")
    parser.add_argument("--imgsz", type=int, default=640,
                       help="Image size for training")
    parser.add_argument("--batch", type=int, default=None,
                       help="Batch size (auto-detected if not set)")
    parser.add_argument("--patience", type=int, default=30,
                       help="Early stopping patience")
    
    # Data loading
    parser.add_argument("--workers", type=int, default=4,
                       help="Number of data loading workers")
    parser.add_argument("--cache", action="store_true",
                       help="Cache images in RAM")
    
    # Output settings
    parser.add_argument("--project", default=str(DEFAULT_PROJECT),
                       help="Project directory")
    parser.add_argument("--name", default="fire_fight",
                       help="Run name")
    
    # Resume
    parser.add_argument("--resume", action="store_true",
                       help="Resume training from last checkpoint")
    
    args = parser.parse_args()
    
    # Train
    best_model = train_model(args)
    
    if best_model:
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║  🎯 NEXT STEPS                                               ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  1. Copy model to Jetson:                                    ║
║     scp {str(best_model):<44} ║
║         nvidia@<JETSON_IP>:~/inveye/                         ║
║                                                              ║
║  2. Export to TensorRT (on Jetson):                          ║
║     python3 export_to_deepstream.py --model best.pt          ║
║                                                              ║
║  3. Run multi-camera detection:                              ║
║     python3 inveye_multi_camera.py --config cameras.yaml     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """)


if __name__ == "__main__":
    main()
