#!/usr/bin/env python3
"""
Simple Demo Script
==================

Quick demo to test the pipeline with webcam or video file.

Usage:
    python demo.py                    # Use webcam
    python demo.py --video test.mp4   # Use video file
    python demo.py --rtsp rtsp://...  # Use RTSP camera
"""

import sys
import argparse
import cv2
import time
from pathlib import Path

# Check dependencies
def check_dependencies():
    missing = []
    
    try:
        from ultralytics import YOLO
    except ImportError:
        missing.append('ultralytics')
    
    try:
        import numpy as np
    except ImportError:
        missing.append('numpy')
    
    if missing:
        print("❌ Missing dependencies:")
        for m in missing:
            print(f"   pip install {m}")
        sys.exit(1)
    
    print("✅ All core dependencies installed")

check_dependencies()

from ultralytics import YOLO
import numpy as np


def download_models():
    """Download required models if not present."""
    models_dir = Path('models')
    models_dir.mkdir(exist_ok=True)
    
    face_model = models_dir / 'yolov11n-face.pt'
    
    if not face_model.exists():
        print("📥 Downloading face detection model...")
        import urllib.request
        url = "https://github.com/YapaLab/yolo-face/releases/download/v0.0.0/yolov11n-face.pt"
        urllib.request.urlretrieve(url, face_model)
        print(f"✅ Downloaded: {face_model}")
    
    return str(face_model)


def run_demo(source, model_path: str):
    """Run simple face detection demo."""
    
    # Load model
    print(f"📦 Loading model: {model_path}")
    model = YOLO(model_path)
    print("✅ Model loaded")
    
    # Open video source
    if isinstance(source, str) and source.isdigit():
        source = int(source)
    
    cap = cv2.VideoCapture(source)
    
    if not cap.isOpened():
        print(f"❌ Failed to open: {source}")
        return
    
    print(f"📹 Source opened: {source}")
    print("Press 'q' to quit, 's' for stats")
    
    frame_count = 0
    total_time = 0
    fps_display = 0
    last_fps_update = time.time()
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect faces
            start = time.time()
            results = model.predict(frame, conf=0.5, verbose=False)
            inference_time = (time.time() - start) * 1000
            
            total_time += inference_time
            frame_count += 1
            
            # Draw results
            for r in results:
                for box in r.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                    conf = float(box.conf[0])
                    
                    # Draw box
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    
                    # Draw label
                    label = f"Face {conf:.2f}"
                    cv2.putText(frame, label, (x1, y1 - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # FPS counter
            now = time.time()
            if now - last_fps_update >= 0.5:
                fps_display = frame_count / (now - last_fps_update + 0.001)
                if fps_display > 100:
                    fps_display = 0
                frame_count = 0
                last_fps_update = now
            
            # Info overlay
            info = [
                f"FPS: {fps_display:.1f}",
                f"Inference: {inference_time:.1f}ms",
                f"Faces: {len(results[0].boxes) if results else 0}"
            ]
            
            y = 30
            for text in info:
                cv2.putText(frame, text, (10, y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                y += 30
            
            # Show
            cv2.imshow("InvEye Demo - Face Detection", frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                print(f"\n📊 Stats: {frame_count} frames, avg {total_time/max(1,frame_count):.1f}ms")
    
    except KeyboardInterrupt:
        print("\nInterrupted")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        
        print(f"\n📊 Final Stats:")
        print(f"   Total Frames: {frame_count}")
        if frame_count > 0:
            print(f"   Avg Inference: {total_time/frame_count:.1f}ms")


def main():
    parser = argparse.ArgumentParser(description='InvEye Demo')
    parser.add_argument('--video', type=str, help='Video file path')
    parser.add_argument('--rtsp', type=str, help='RTSP URL')
    parser.add_argument('--webcam', type=int, default=0, help='Webcam index')
    parser.add_argument('--model', type=str, help='Model path')
    
    args = parser.parse_args()
    
    # Determine source
    if args.video:
        source = args.video
    elif args.rtsp:
        source = args.rtsp
    else:
        source = args.webcam
    
    # Get model
    if args.model:
        model_path = args.model
    else:
        model_path = download_models()
    
    # Run demo
    run_demo(source, model_path)


if __name__ == '__main__':
    main()
