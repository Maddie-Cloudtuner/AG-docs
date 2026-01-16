"""
TensorRT Export Script for Jetson Orin Nano
Exports YOLOv8 model to TensorRT engine for optimized inference
"""

import torch
from ultralytics import YOLO
from pathlib import Path
import argparse
import shutil

# Project paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
DEPLOY_DIR = PROJECT_DIR / "deploy"


def check_tensorrt():
    """Check if TensorRT is available"""
    try:
        import tensorrt as trt
        print(f"✅ TensorRT version: {trt.__version__}")
        return True
    except ImportError:
        print("⚠️ TensorRT not installed")
        print("   On Jetson, TensorRT comes pre-installed")
        print("   On PC, install: pip install tensorrt")
        return False


def check_cuda():
    """Check CUDA availability"""
    if torch.cuda.is_available():
        print(f"✅ CUDA available: {torch.cuda.get_device_name(0)}")
        return True
    else:
        print("❌ CUDA not available - TensorRT export requires GPU")
        return False


def export_model(args):
    """Export YOLOv8 model to various formats"""
    
    print("=" * 60)
    print("🚀 YOLOv8 TensorRT Export for Jetson")
    print("=" * 60)
    
    # Check requirements
    has_cuda = check_cuda()
    has_tensorrt = check_tensorrt()
    
    if not has_cuda:
        print("\n❌ Cannot export without CUDA GPU")
        return None
    
    # Create deploy directory
    DEPLOY_DIR.mkdir(exist_ok=True)
    
    # Load model
    model_path = Path(args.model)
    if not model_path.exists():
        print(f"\n❌ Model not found: {model_path}")
        return None
    
    print(f"\n📦 Loading model: {model_path}")
    model = YOLO(str(model_path))
    
    # Export configuration
    export_format = "engine" if has_tensorrt else "onnx"
    
    print(f"\n⚙️ Export Configuration:")
    print(f"   Format: {export_format.upper()}")
    print(f"   Image Size: {args.imgsz}")
    print(f"   Half Precision (FP16): {args.half}")
    print(f"   Batch Size: {args.batch}")
    
    if has_tensorrt:
        print(f"   Workspace: {args.workspace} GB")
    
    # Export
    print(f"\n🔄 Exporting to {export_format.upper()}...")
    
    try:
        if has_tensorrt:
            # TensorRT export
            exported_path = model.export(
                format="engine",
                imgsz=args.imgsz,
                half=args.half,
                device=0,
                batch=args.batch,
                workspace=args.workspace,
                simplify=True,
                dynamic=False,  # Fixed batch for best performance
                verbose=True,
            )
        else:
            # ONNX export (can convert to TensorRT on Jetson)
            exported_path = model.export(
                format="onnx",
                imgsz=args.imgsz,
                half=args.half,
                device=0,
                batch=args.batch,
                simplify=True,
                dynamic=False,
                verbose=True,
            )
        
        print(f"\n✅ Model exported: {exported_path}")
        
        # Copy to deploy directory
        exported_file = Path(exported_path)
        deploy_path = DEPLOY_DIR / exported_file.name
        shutil.copy2(exported_file, deploy_path)
        print(f"📁 Copied to: {deploy_path}")
        
        return deploy_path
        
    except Exception as e:
        print(f"\n❌ Export failed: {e}")
        raise


def create_inference_script():
    """Create ready-to-run inference script for Jetson"""
    
    script_content = '''#!/usr/bin/env python3
"""
Fire & Fight Detection Inference for Jetson Orin Nano
Run: python jetson_inference.py --model model.engine --source 0
"""

import cv2
import numpy as np
from ultralytics import YOLO
import time
import argparse
from collections import deque


class FireFightDetector:
    """Real-time Fire & Fight Detection using YOLOv8"""
    
    def __init__(self, model_path, conf_threshold=0.5, iou_threshold=0.45):
        print(f"Loading model: {model_path}")
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        
        # Class configuration
        self.class_names = {
            0: "person",
            1: "fire",
            2: "smoke",
            3: "fighting"
        }
        
        # Alert colors (BGR format)
        self.colors = {
            "person": (0, 255, 0),      # Green
            "fire": (0, 0, 255),        # Red
            "smoke": (128, 128, 128),   # Gray
            "fighting": (0, 165, 255),  # Orange
        }
        
        # FPS tracking
        self.fps_history = deque(maxlen=30)
        self.last_time = time.time()
        
        print("✅ Model loaded successfully!")
    
    def detect(self, frame):
        """Run detection on a single frame"""
        results = self.model(
            frame, 
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            verbose=False
        )
        return results[0]
    
    def draw_results(self, frame, results):
        """Draw bounding boxes and labels on frame"""
        boxes = results.boxes
        alerts = []
        
        for box in boxes:
            # Get box coordinates
            x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            
            # Get class name and color
            class_name = self.class_names.get(cls_id, f"class_{cls_id}")
            color = self.colors.get(class_name, (255, 255, 255))
            
            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw label background
            label = f"{class_name}: {conf:.2f}"
            (label_w, label_h), _ = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1
            )
            cv2.rectangle(
                frame, 
                (x1, y1 - label_h - 10), 
                (x1 + label_w + 5, y1), 
                color, -1
            )
            
            # Draw label text
            cv2.putText(
                frame, label, (x1 + 2, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1
            )
            
            # Track alerts for dangerous detections
            if class_name in ["fire", "smoke", "fighting"]:
                alerts.append({
                    "class": class_name,
                    "confidence": conf,
                    "bbox": (x1, y1, x2, y2)
                })
        
        return frame, alerts
    
    def draw_fps(self, frame):
        """Draw FPS counter on frame"""
        current_time = time.time()
        fps = 1.0 / (current_time - self.last_time)
        self.last_time = current_time
        self.fps_history.append(fps)
        
        avg_fps = sum(self.fps_history) / len(self.fps_history)
        
        cv2.putText(
            frame, f"FPS: {avg_fps:.1f}", (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
        )
        
        return frame, avg_fps
    
    def draw_alerts(self, frame, alerts):
        """Draw alert banner if dangerous events detected"""
        if not alerts:
            return frame
        
        # Create alert message
        alert_classes = list(set([a['class'].upper() for a in alerts]))
        alert_text = " | ".join([f"⚠️ {c} DETECTED" for c in alert_classes])
        
        # Draw alert banner
        h, w = frame.shape[:2]
        cv2.rectangle(frame, (0, h - 50), (w, h), (0, 0, 200), -1)
        cv2.putText(
            frame, alert_text, (10, h - 15),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2
        )
        
        return frame
    
    def run_camera(self, source=0, display=True, save_video=None):
        """Run detection on camera or video stream"""
        
        # Open video source
        if isinstance(source, str) and source.isdigit():
            source = int(source)
        
        print(f"Opening video source: {source}")
        cap = cv2.VideoCapture(source)
        
        if not cap.isOpened():
            print(f"❌ Failed to open video source: {source}")
            return
        
        # Get video properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        
        print(f"📹 Video: {width}x{height} @ {fps:.1f} FPS")
        
        # Video writer for saving
        writer = None
        if save_video:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(save_video, fourcc, fps, (width, height))
            print(f"📼 Saving to: {save_video}")
        
        print("\\n🎥 Starting detection... Press 'q' to quit\\n")
        
        frame_count = 0
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    if isinstance(source, int):
                        continue  # Camera might have temporary read failure
                    break  # End of video file
                
                frame_count += 1
                
                # Run detection
                results = self.detect(frame)
                
                # Draw results
                frame, alerts = self.draw_results(frame, results)
                frame, current_fps = self.draw_fps(frame)
                frame = self.draw_alerts(frame, alerts)
                
                # Log alerts
                if alerts and frame_count % 30 == 0:  # Log every ~1 second
                    for alert in alerts:
                        print(f"🚨 {alert['class'].upper()}: {alert['confidence']:.2f}")
                
                # Save frame
                if writer:
                    writer.write(frame)
                
                # Display
                if display:
                    cv2.imshow("Fire & Fight Detection", frame)
                    
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        break
                    elif key == ord('s'):
                        # Save screenshot
                        screenshot_path = f"screenshot_{frame_count}.jpg"
                        cv2.imwrite(screenshot_path, frame)
                        print(f"📸 Screenshot saved: {screenshot_path}")
        
        finally:
            cap.release()
            if writer:
                writer.release()
            if display:
                cv2.destroyAllWindows()
            
            print(f"\\n✅ Processed {frame_count} frames")


def main():
    parser = argparse.ArgumentParser(
        description="Fire & Fight Detection for Jetson Orin Nano"
    )
    
    parser.add_argument("--model", default="model.engine",
                       help="Model path (.engine or .pt)")
    parser.add_argument("--source", default="0",
                       help="Video source (0 for camera, path for video, rtsp:// for stream)")
    parser.add_argument("--conf", type=float, default=0.5,
                       help="Confidence threshold")
    parser.add_argument("--iou", type=float, default=0.45,
                       help="IoU threshold for NMS")
    parser.add_argument("--save", type=str, default=None,
                       help="Save output video to path")
    parser.add_argument("--no-display", action="store_true",
                       help="Disable display window")
    
    args = parser.parse_args()
    
    # Create detector
    detector = FireFightDetector(
        model_path=args.model,
        conf_threshold=args.conf,
        iou_threshold=args.iou
    )
    
    # Run detection
    detector.run_camera(
        source=args.source,
        display=not args.no_display,
        save_video=args.save
    )


if __name__ == "__main__":
    main()
'''
    
    # Save script
    script_path = DEPLOY_DIR / "jetson_inference.py"
    DEPLOY_DIR.mkdir(exist_ok=True)
    
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    print(f"✅ Created inference script: {script_path}")
    return script_path


def create_readme():
    """Create deployment README"""
    
    readme_content = """# Fire & Fight Detection - Jetson Deployment

## Quick Start

```bash
# Run with camera
python jetson_inference.py --model model.engine --source 0

# Run with video file
python jetson_inference.py --model model.engine --source video.mp4

# Run with RTSP stream
python jetson_inference.py --model model.engine --source "rtsp://user:pass@ip:port/stream"

# Save output
python jetson_inference.py --model model.engine --source 0 --save output.mp4
```

## Requirements

```bash
pip install ultralytics opencv-python numpy
```

## Keyboard Controls

- `q` - Quit
- `s` - Save screenshot

## Performance Tips

1. Use YOLOv8n for best FPS
2. Lower image size (--imgsz 480) for faster inference
3. Increase confidence threshold (--conf 0.6) to reduce processing
4. Use TensorRT engine (.engine) instead of PyTorch (.pt)

## Troubleshooting

**Low FPS**: 
- Check if TensorRT engine is being used
- Reduce image size
- Close other GPU applications

**No detections**:
- Lower confidence threshold
- Ensure lighting conditions are adequate
- Verify model was trained on similar data

**Camera not opening**:
- Check camera permissions
- Try different source IDs (0, 1, 2)
- For USB cameras, ensure proper connection
"""
    
    readme_path = DEPLOY_DIR / "README.md"
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    
    print(f"✅ Created README: {readme_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Export YOLOv8 to TensorRT for Jetson",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument("--model", required=True,
                       help="Path to trained model (.pt)")
    parser.add_argument("--imgsz", type=int, default=640,
                       help="Image size for export")
    parser.add_argument("--batch", type=int, default=1,
                       help="Batch size (1 for real-time)")
    parser.add_argument("--half", action="store_true", default=True,
                       help="Use FP16 half precision")
    parser.add_argument("--workspace", type=int, default=4,
                       help="TensorRT workspace size in GB")
    
    args = parser.parse_args()
    
    # Export model
    exported_path = export_model(args)
    
    # Create inference script
    create_inference_script()
    
    # Create README
    create_readme()
    
    # Print deployment instructions
    print("\n" + "=" * 60)
    print("📋 Deployment Instructions")
    print("=" * 60)
    print(f"""
1. Copy deploy folder to Jetson Orin Nano:
   scp -r {DEPLOY_DIR} jetson@<JETSON_IP>:~/

2. On Jetson, install dependencies:
   pip install ultralytics opencv-python

3. Run inference:
   cd ~/deploy
   python jetson_inference.py --model model.engine --source 0

4. For RTSP streams (CCTV):
   python jetson_inference.py --model model.engine --source "rtsp://..."
""")


if __name__ == "__main__":
    main()
