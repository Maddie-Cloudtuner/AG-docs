#!/usr/bin/env python3
"""
Jetson Deployment Script
========================

Optimizes and converts models for TensorRT acceleration on Jetson.

Usage:
    python jetson_deploy.py --convert-all
    python jetson_deploy.py --convert-face
    python jetson_deploy.py --benchmark
"""

import os
import sys
import argparse
import time
from pathlib import Path


def check_jetson():
    """Check if running on Jetson."""
    try:
        with open('/etc/nv_tegra_release', 'r') as f:
            content = f.read()
            print(f"✅ Running on Jetson: {content.strip()}")
            return True
    except:
        print("⚠️ Not running on Jetson (TensorRT conversion may not work)")
        return False


def convert_to_tensorrt(model_path: str, output_path: str = None, half: bool = True):
    """Convert YOLO model to TensorRT engine."""
    from ultralytics import YOLO
    
    print(f"\n🔧 Converting: {model_path}")
    print(f"   FP16: {half}")
    
    model = YOLO(model_path)
    
    engine_path = model.export(
        format='engine',
        half=half,
        device=0,
        simplify=True,
        workspace=4  # GB
    )
    
    print(f"✅ Created: {engine_path}")
    return engine_path


def convert_onnx(model_path: str, output_path: str = None):
    """Convert YOLO model to ONNX."""
    from ultralytics import YOLO
    
    print(f"\n🔧 Converting to ONNX: {model_path}")
    
    model = YOLO(model_path)
    
    onnx_path = model.export(
        format='onnx',
        simplify=True,
        dynamic=False
    )
    
    print(f"✅ Created: {onnx_path}")
    return onnx_path


def benchmark_model(model_path: str, iterations: int = 100):
    """Benchmark model inference speed."""
    import numpy as np
    from ultralytics import YOLO
    
    print(f"\n📊 Benchmarking: {model_path}")
    
    model = YOLO(model_path)
    
    # Warmup
    dummy_input = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
    for _ in range(10):
        model.predict(dummy_input, verbose=False)
    
    # Benchmark
    times = []
    for i in range(iterations):
        start = time.time()
        model.predict(dummy_input, verbose=False)
        times.append((time.time() - start) * 1000)
    
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    fps = 1000 / avg_time
    
    print(f"   Iterations: {iterations}")
    print(f"   Avg Time:   {avg_time:.2f} ms")
    print(f"   Min Time:   {min_time:.2f} ms")
    print(f"   Max Time:   {max_time:.2f} ms")
    print(f"   FPS:        {fps:.1f}")
    
    return {
        'model': model_path,
        'avg_ms': avg_time,
        'min_ms': min_time,
        'max_ms': max_time,
        'fps': fps
    }


def setup_models_directory():
    """Create models directory and show download instructions."""
    models_dir = Path('models')
    models_dir.mkdir(exist_ok=True)
    
    print("\n📁 Models Directory Setup")
    print("="*50)
    
    required_models = [
        ('yolov11n-face.pt', 'https://github.com/YapaLab/yolo-face/releases/download/v0.0.0/yolov11n-face.pt'),
        ('yolov11n.pt', 'https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n.pt'),
    ]
    
    for model_name, url in required_models:
        model_path = models_dir / model_name
        if model_path.exists():
            print(f"  ✅ {model_name} - Found")
        else:
            print(f"  ❌ {model_name} - Missing")
            print(f"     Download: {url}")
            print(f"     wget {url} -O {model_path}")
    
    print()


def main():
    parser = argparse.ArgumentParser(description='Jetson Deployment Tool')
    
    parser.add_argument('--convert-all', action='store_true', 
                       help='Convert all models to TensorRT')
    parser.add_argument('--convert-face', action='store_true',
                       help='Convert face detection model only')
    parser.add_argument('--convert-object', action='store_true',
                       help='Convert object detection model only')
    parser.add_argument('--to-onnx', action='store_true',
                       help='Convert to ONNX instead of TensorRT')
    parser.add_argument('--benchmark', action='store_true',
                       help='Benchmark all models')
    parser.add_argument('--setup', action='store_true',
                       help='Setup models directory')
    parser.add_argument('--model', type=str,
                       help='Specific model path to convert')
    parser.add_argument('--fp32', action='store_true',
                       help='Use FP32 instead of FP16')
    
    args = parser.parse_args()
    
    # Check Jetson
    is_jetson = check_jetson()
    
    if args.setup:
        setup_models_directory()
        return
    
    models_dir = Path('models')
    
    # Convert specific model
    if args.model:
        if args.to_onnx:
            convert_onnx(args.model)
        else:
            convert_to_tensorrt(args.model, half=not args.fp32)
        return
    
    # Convert face model
    if args.convert_face or args.convert_all:
        face_model = models_dir / 'yolov11n-face.pt'
        if face_model.exists():
            if args.to_onnx:
                convert_onnx(str(face_model))
            else:
                convert_to_tensorrt(str(face_model), half=not args.fp32)
        else:
            print(f"❌ Face model not found: {face_model}")
    
    # Convert object model
    if args.convert_object or args.convert_all:
        object_model = models_dir / 'yolov11n.pt'
        if object_model.exists():
            if args.to_onnx:
                convert_onnx(str(object_model))
            else:
                convert_to_tensorrt(str(object_model), half=not args.fp32)
        else:
            print(f"❌ Object model not found: {object_model}")
    
    # Benchmark
    if args.benchmark:
        print("\n" + "="*60)
        print("MODEL BENCHMARKS")
        print("="*60)
        
        results = []
        
        for model_file in models_dir.glob('*.pt'):
            try:
                result = benchmark_model(str(model_file))
                results.append(result)
            except Exception as e:
                print(f"❌ Failed to benchmark {model_file}: {e}")
        
        for model_file in models_dir.glob('*.engine'):
            try:
                result = benchmark_model(str(model_file))
                results.append(result)
            except Exception as e:
                print(f"❌ Failed to benchmark {model_file}: {e}")
        
        # Summary table
        if results:
            print("\n" + "="*60)
            print("BENCHMARK SUMMARY")
            print("="*60)
            print(f"{'Model':<40} {'Avg (ms)':<12} {'FPS':<10}")
            print("-"*60)
            for r in sorted(results, key=lambda x: x['avg_ms']):
                print(f"{r['model']:<40} {r['avg_ms']:<12.2f} {r['fps']:<10.1f}")
    
    if not any([args.convert_all, args.convert_face, args.convert_object, 
                args.benchmark, args.model, args.setup]):
        parser.print_help()


if __name__ == '__main__':
    main()
