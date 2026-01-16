#!/usr/bin/env python3
"""
Export YOLO11 to TensorRT Engine for DeepStream
Run this on Jetson Orin Nano after training

Usage:
    python3 export_to_deepstream.py --model yolo11s_fire_fight.pt
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path


def check_environment():
    """Verify we're on a Jetson with required tools"""
    
    print("🔍 Checking environment...")
    
    # Check CUDA
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✅ CUDA available: {torch.cuda.get_device_name(0)}")
        else:
            print("⚠️  CUDA not available")
    except ImportError:
        print("❌ PyTorch not installed")
        return False
    
    # Check TensorRT
    try:
        import tensorrt as trt
        print(f"✅ TensorRT version: {trt.__version__}")
    except ImportError:
        print("⚠️  TensorRT not found (will use ONNX first)")
    
    # Check DeepStream-YOLO export script
    export_script = Path.home() / "ultralytics" / "export_yolo11.py"
    if export_script.exists():
        print(f"✅ DeepStream export script found")
    else:
        print("❌ Export script not found. Run setup_jetson.sh first")
        return False
    
    return True


def export_model(model_path: str, output_dir: str, dynamic: bool = True):
    """Export YOLO11 model to TensorRT engine"""
    
    model_path = Path(model_path)
    if not model_path.exists():
        print(f"❌ Model not found: {model_path}")
        return None
    
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Use DeepStream-YOLO export script
    export_script = Path.home() / "ultralytics" / "export_yolo11.py"
    
    cmd = [
        "python3", str(export_script),
        "-w", str(model_path),
        "-o", str(output_dir),
    ]
    
    if dynamic:
        cmd.append("--dynamic")
    
    print(f"\n🔄 Exporting model...")
    print(f"   Command: {' '.join(cmd)}\n")
    
    result = subprocess.run(cmd, cwd=str(Path.home() / "ultralytics"))
    
    if result.returncode != 0:
        print("❌ Export failed")
        return None
    
    # Find generated files
    engine_file = output_dir / f"{model_path.stem}.engine"
    cfg_file = output_dir / f"{model_path.stem}.cfg"
    
    print(f"\n✅ Export complete!")
    print(f"   Engine: {engine_file}")
    print(f"   Config: {cfg_file}")
    
    return engine_file


def create_nvinfer_config(engine_path: str, labels_path: str, output_path: str):
    """Generate DeepStream nvinfer configuration"""
    
    config = f"""# Auto-generated InvEye nvinfer config
[property]
gpu-id=0
net-scale-factor=0.0039215697906911373
model-color-format=0

# TensorRT Engine
model-engine-file={engine_path}

# Labels
labelfile-path={labels_path}

# YOLO parser
parse-bbox-func-name=NvDsInferParseYolo
custom-lib-path=/opt/nvidia/deepstream/deepstream/lib/libnvds_infercustomparser.so

# Network config
infer-dims=3;640;640
batch-size=4
network-mode=2
num-detected-classes=83
interval=0

gie-unique-id=1
process-mode=1
network-type=0
cluster-mode=2

# Detection thresholds
nms-iou-threshold=0.45
pre-cluster-threshold=0.25

[class-attrs-all]
pre-cluster-threshold=0.25
topk=100
"""
    
    with open(output_path, 'w') as f:
        f.write(config)
    
    print(f"✅ nvinfer config: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Export YOLO11 to TensorRT for DeepStream"
    )
    parser.add_argument(
        "--model", "-m",
        required=True,
        help="Path to trained YOLO11 model (.pt)"
    )
    parser.add_argument(
        "--output", "-o",
        default="./",
        help="Output directory for engine file"
    )
    parser.add_argument(
        "--labels",
        default="labels.txt",
        help="Path to labels file"
    )
    parser.add_argument(
        "--dynamic",
        action="store_true",
        default=True,
        help="Enable dynamic batch size"
    )
    
    args = parser.parse_args()
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║  YOLO11 → TensorRT Export for DeepStream                     ║
║  InvEye Fire & Fight Detection                               ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    if not check_environment():
        print("\n❌ Environment check failed. Please run setup_jetson.sh first.")
        sys.exit(1)
    
    # Export model
    engine_path = export_model(args.model, args.output, args.dynamic)
    
    if engine_path:
        # Create nvinfer config
        config_path = Path(args.output) / "config_infer_yolo11.txt"
        create_nvinfer_config(
            str(engine_path),
            args.labels,
            str(config_path)
        )
        
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║  ✅ EXPORT COMPLETE                                          ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Engine: {str(engine_path):<50} ║
║                                                              ║
║  Next: Run InvEye with:                                      ║
║    python3 inveye_multi_camera.py --config cameras.yaml      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """)


if __name__ == "__main__":
    main()
