"""
🚀 Jetson Orin Nano Deployment Script
======================================
Deploys trained YOLO models on Jetson Orin Nano for real-time inference.
Supports Fire, Fight, and Face Detection with TensorRT optimization.

Author: InvEye Team
Hardware: NVIDIA Jetson Orin Nano Developer Kit (8GB)

Usage:
    python jetson_deploy.py --model best.pt --export           # Export to TensorRT
    python jetson_deploy.py --model best.engine --camera 0     # Run inference on camera
    python jetson_deploy.py --model best.engine --rtsp rtsp://ip/stream
    python jetson_deploy.py --benchmark                        # Run performance benchmark
"""

import os
import sys
import time
import argparse
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Check if we're on Jetson
IS_JETSON = os.path.exists('/etc/nv_tegra_release')

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False
    print("⚠️ OpenCV not found. Install with: pip install opencv-python")

try:
    from ultralytics import YOLO
    HAS_YOLO = True
except ImportError:
    HAS_YOLO = False
    print("⚠️ Ultralytics not found. Install with: pip install ultralytics")

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


# ============================================================================
# CONFIGURATION
# ============================================================================

# Detection classes
CLASS_NAMES = {
    0: "fire",
    1: "smoke",
    2: "fighting",
    3: "face",
    4: "weapon",
    5: "knife",
    6: "person",
}

# Alert thresholds
ALERT_CLASSES = {
    "fire": {"threshold": 0.5, "priority": "CRITICAL", "color": (0, 0, 255)},
    "smoke": {"threshold": 0.4, "priority": "HIGH", "color": (128, 128, 128)},
    "fighting": {"threshold": 0.6, "priority": "CRITICAL", "color": (0, 0, 255)},
    "face": {"threshold": 0.5, "priority": "INFO", "color": (0, 255, 0)},
    "weapon": {"threshold": 0.5, "priority": "CRITICAL", "color": (0, 0, 255)},
    "knife": {"threshold": 0.5, "priority": "CRITICAL", "color": (0, 0, 255)},
    "person": {"threshold": 0.5, "priority": "INFO", "color": (255, 0, 0)},
}

# Jetson Orin Nano optimal settings
JETSON_SETTINGS = {
    "imgsz": 640,           # Input size (640 recommended for balance)
    "half": True,           # FP16 inference
    "device": 0,            # GPU device
    "max_det": 100,         # Max detections per frame
    "conf": 0.4,            # Confidence threshold
    "iou": 0.5,             # NMS IoU threshold
    "vid_stride": 1,        # Video frame stride
}


# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

def export_to_tensorrt(model_path, output_path=None, imgsz=640, half=True):
    """Export PyTorch model to TensorRT engine for Jetson."""
    print("\n" + "="*60)
    print("🔧 EXPORTING MODEL TO TENSORRT")
    print("="*60)
    
    if not HAS_YOLO:
        print("❌ Ultralytics not installed!")
        return None
    
    model_path = Path(model_path)
    
    if not model_path.exists():
        print(f"❌ Model not found: {model_path}")
        return None
    
    print(f"   Input model: {model_path}")
    print(f"   Image size: {imgsz}")
    print(f"   FP16: {half}")
    print(f"   Platform: {'Jetson' if IS_JETSON else 'Desktop'}")
    
    # Load model
    model = YOLO(str(model_path))
    
    # Export to TensorRT
    print("\n   Exporting to TensorRT (this may take several minutes)...")
    
    try:
        engine_path = model.export(
            format="engine",
            imgsz=imgsz,
            half=half,
            device=0,
            simplify=True,
            workspace=4,  # 4GB workspace (suitable for Orin Nano 8GB)
        )
        
        print(f"\n✅ Export successful!")
        print(f"   Engine saved to: {engine_path}")
        
        return engine_path
        
    except Exception as e:
        print(f"\n❌ Export failed: {e}")
        
        # Fallback to ONNX if TensorRT fails
        print("\n   Attempting ONNX export as fallback...")
        try:
            onnx_path = model.export(format="onnx", imgsz=imgsz, simplify=True)
            print(f"   ONNX saved to: {onnx_path}")
            return onnx_path
        except Exception as e2:
            print(f"   ONNX export also failed: {e2}")
            return None


def export_to_onnx(model_path, imgsz=640):
    """Export PyTorch model to ONNX format."""
    print("\n🔧 Exporting to ONNX...")
    
    model = YOLO(str(model_path))
    onnx_path = model.export(format="onnx", imgsz=imgsz, simplify=True, dynamic=False)
    
    print(f"✅ ONNX saved to: {onnx_path}")
    return onnx_path


# ============================================================================
# INFERENCE ENGINE
# ============================================================================

class JetsonInference:
    """High-performance inference engine optimized for Jetson Orin Nano."""
    
    def __init__(self, model_path, **kwargs):
        self.model_path = Path(model_path)
        self.settings = {**JETSON_SETTINGS, **kwargs}
        
        # Statistics
        self.frame_count = 0
        self.total_time = 0
        self.detections = defaultdict(int)
        self.alerts = []
        
        # Load model
        print(f"\n📦 Loading model: {self.model_path}")
        self.model = YOLO(str(self.model_path))
        print(f"   Model loaded successfully!")
        
        # Warmup
        self._warmup()
    
    def _warmup(self, n_warmup=3):
        """Warmup the model for consistent timing."""
        print(f"   Warming up ({n_warmup} iterations)...")
        dummy = np.zeros((self.settings['imgsz'], self.settings['imgsz'], 3), dtype=np.uint8)
        for _ in range(n_warmup):
            self.model.predict(dummy, verbose=False)
        print("   Warmup complete!")
    
    def predict(self, frame, track=False):
        """Run inference on a single frame."""
        start_time = time.time()
        
        # Run inference
        if track:
            results = self.model.track(
                frame,
                persist=True,
                conf=self.settings['conf'],
                iou=self.settings['iou'],
                imgsz=self.settings['imgsz'],
                half=self.settings['half'],
                max_det=self.settings['max_det'],
                verbose=False
            )
        else:
            results = self.model.predict(
                frame,
                conf=self.settings['conf'],
                iou=self.settings['iou'],
                imgsz=self.settings['imgsz'],
                half=self.settings['half'],
                max_det=self.settings['max_det'],
                verbose=False
            )
        
        # Update statistics
        inference_time = time.time() - start_time
        self.frame_count += 1
        self.total_time += inference_time
        
        # Process detections
        detections = self._process_results(results[0])
        
        return {
            'detections': detections,
            'inference_time': inference_time,
            'fps': 1.0 / inference_time if inference_time > 0 else 0
        }
    
    def _process_results(self, result):
        """Process YOLO results into structured detections."""
        detections = []
        
        if result.boxes is None:
            return detections
        
        boxes = result.boxes
        
        for i in range(len(boxes)):
            class_id = int(boxes.cls[i].item())
            confidence = float(boxes.conf[i].item())
            bbox = boxes.xyxy[i].cpu().numpy().tolist()
            
            class_name = CLASS_NAMES.get(class_id, f"class_{class_id}")
            alert_config = ALERT_CLASSES.get(class_name, {})
            
            detection = {
                'class_id': class_id,
                'class_name': class_name,
                'confidence': confidence,
                'bbox': bbox,
                'priority': alert_config.get('priority', 'INFO'),
                'color': alert_config.get('color', (0, 255, 0))
            }
            
            # Track object ID if available
            if hasattr(boxes, 'id') and boxes.id is not None:
                detection['track_id'] = int(boxes.id[i].item())
            
            detections.append(detection)
            self.detections[class_name] += 1
            
            # Generate alert for critical detections
            threshold = alert_config.get('threshold', 0.5)
            if confidence >= threshold and alert_config.get('priority') == 'CRITICAL':
                self._generate_alert(detection)
        
        return detections
    
    def _generate_alert(self, detection):
        """Generate an alert for critical detections."""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'class': detection['class_name'],
            'confidence': detection['confidence'],
            'priority': detection['priority'],
            'bbox': detection['bbox']
        }
        self.alerts.append(alert)
        
        # Print alert to console
        print(f"\n🚨 ALERT [{detection['priority']}]: {detection['class_name']} detected (conf: {detection['confidence']:.2f})")
    
    def draw_detections(self, frame, detections):
        """Draw detection boxes on frame."""
        for det in detections:
            x1, y1, x2, y2 = [int(v) for v in det['bbox']]
            color = det['color']
            
            # Draw box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            label = f"{det['class_name']} {det['confidence']:.2f}"
            if 'track_id' in det:
                label += f" ID:{det['track_id']}"
            
            # Label background
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(frame, (x1, y1 - 20), (x1 + w, y1), color, -1)
            cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Draw FPS
        fps = self.frame_count / self.total_time if self.total_time > 0 else 0
        cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        return frame
    
    def get_stats(self):
        """Get inference statistics."""
        avg_fps = self.frame_count / self.total_time if self.total_time > 0 else 0
        
        return {
            'total_frames': self.frame_count,
            'total_time': self.total_time,
            'average_fps': avg_fps,
            'detections_by_class': dict(self.detections),
            'total_alerts': len(self.alerts)
        }


# ============================================================================
# VIDEO PROCESSING
# ============================================================================

def run_camera_inference(model_path, camera_source=0, track=True, output=None, headless=False):
    """Run real-time inference on camera or video stream."""
    print("\n" + "="*60)
    print("📹 STARTING REAL-TIME INFERENCE")
    print("="*60)
    
    # Initialize inference engine
    engine = JetsonInference(model_path)
    
    # Open video source
    if isinstance(camera_source, str) and camera_source.startswith('rtsp'):
        print(f"   Opening RTSP stream: {camera_source}")
        # Use GStreamer for RTSP on Jetson
        if IS_JETSON:
            gst_str = f'rtspsrc location={camera_source} latency=0 ! rtph264depay ! h264parse ! nvv4l2decoder ! nvvidconv ! video/x-raw,format=BGRx ! videoconvert ! video/x-raw,format=BGR ! appsink'
            cap = cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)
        else:
            cap = cv2.VideoCapture(camera_source)
    else:
        print(f"   Opening camera: {camera_source}")
        if IS_JETSON:
            # Use GStreamer for CSI camera on Jetson
            if camera_source == 0:
                gst_str = "nvarguscamerasrc ! video/x-raw(memory:NVMM),width=1280,height=720,framerate=30/1 ! nvvidconv ! video/x-raw,format=BGRx ! videoconvert ! video/x-raw,format=BGR ! appsink"
                cap = cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)
            else:
                cap = cv2.VideoCapture(camera_source)
        else:
            cap = cv2.VideoCapture(camera_source)
    
    if not cap.isOpened():
        print("❌ Failed to open video source!")
        return
    
    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    print(f"   Resolution: {width}x{height}")
    print(f"   FPS: {fps}")
    print(f"   Tracking: {'Enabled' if track else 'Disabled'}")
    print(f"   Press 'q' to quit, 's' to save screenshot")
    
    # Video writer for output
    writer = None
    if output:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(output, fourcc, fps, (width, height))
        print(f"   Recording to: {output}")
    
    print("\n   Starting inference loop...")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("   End of stream")
                break
            
            # Run inference
            result = engine.predict(frame, track=track)
            
            # Draw detections
            frame = engine.draw_detections(frame, result['detections'])
            
            # Write output
            if writer:
                writer.write(frame)
            
            # Display (if not headless)
            if not headless:
                cv2.imshow('InvEye - Fire/Fight/Face Detection', frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    screenshot_path = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                    cv2.imwrite(screenshot_path, frame)
                    print(f"   📷 Screenshot saved: {screenshot_path}")
    
    except KeyboardInterrupt:
        print("\n   Interrupted by user")
    
    finally:
        cap.release()
        if writer:
            writer.release()
        cv2.destroyAllWindows()
        
        # Print statistics
        stats = engine.get_stats()
        print("\n" + "="*60)
        print("📊 SESSION STATISTICS")
        print("="*60)
        print(f"   Total frames: {stats['total_frames']}")
        print(f"   Average FPS: {stats['average_fps']:.1f}")
        print(f"   Total alerts: {stats['total_alerts']}")
        print("\n   Detections by class:")
        for cls, count in stats['detections_by_class'].items():
            print(f"      {cls}: {count}")
        
        # Save alerts to file
        if engine.alerts:
            alerts_path = f"alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(alerts_path, 'w') as f:
                json.dump(engine.alerts, f, indent=2)
            print(f"\n   Alerts saved to: {alerts_path}")


def run_benchmark(model_path, n_iterations=100):
    """Run performance benchmark."""
    print("\n" + "="*60)
    print("⚡ PERFORMANCE BENCHMARK")
    print("="*60)
    
    engine = JetsonInference(model_path)
    
    # Create test image
    test_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
    
    print(f"\n   Running {n_iterations} iterations...")
    
    times = []
    for i in range(n_iterations):
        start = time.time()
        engine.predict(test_image, track=False)
        times.append(time.time() - start)
        
        if (i + 1) % 20 == 0:
            print(f"   Progress: {i + 1}/{n_iterations}")
    
    # Calculate statistics
    times = times[10:]  # Remove warmup
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    avg_fps = 1.0 / avg_time
    
    print("\n   Results:")
    print(f"      Average inference time: {avg_time * 1000:.2f} ms")
    print(f"      Min inference time: {min_time * 1000:.2f} ms")
    print(f"      Max inference time: {max_time * 1000:.2f} ms")
    print(f"      Average FPS: {avg_fps:.1f}")
    print(f"      Theoretical max FPS: {1.0 / min_time:.1f}")
    
    # Jetson-specific info
    if IS_JETSON:
        print("\n   Jetson Power Mode:")
        try:
            import subprocess
            result = subprocess.run(['nvpmodel', '-q'], capture_output=True, text=True)
            print(f"      {result.stdout.strip()}")
        except:
            pass


# ============================================================================
# MULTI-CAMERA SUPPORT
# ============================================================================

def run_multi_camera(model_path, camera_sources, output_dir=None, headless=False):
    """Run inference on multiple cameras simultaneously."""
    print("\n" + "="*60)
    print("📹 MULTI-CAMERA INFERENCE")
    print("="*60)
    
    import threading
    from queue import Queue
    
    # Shared model (thread-safe in inference mode)
    engine = JetsonInference(model_path)
    
    # Create threads for each camera
    threads = []
    results_queue = Queue()
    
    def camera_worker(camera_id, source):
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            print(f"❌ Failed to open camera {camera_id}")
            return
        
        print(f"   Camera {camera_id} started")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            result = engine.predict(frame)
            results_queue.put((camera_id, frame, result))
        
        cap.release()
    
    # Start threads
    for i, source in enumerate(camera_sources):
        t = threading.Thread(target=camera_worker, args=(i, source))
        t.daemon = True
        t.start()
        threads.append(t)
    
    print(f"   Started {len(threads)} camera threads")
    
    # Display loop
    try:
        while True:
            if not results_queue.empty():
                camera_id, frame, result = results_queue.get()
                frame = engine.draw_detections(frame, result['detections'])
                
                if not headless:
                    cv2.imshow(f'Camera {camera_id}', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    except KeyboardInterrupt:
        pass
    
    finally:
        cv2.destroyAllWindows()
        print("\n   Multi-camera session ended")


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Jetson Orin Nano Deployment for Fire/Fight/Face Detection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Export model to TensorRT
  python jetson_deploy.py --model best.pt --export
  
  # Run on camera
  python jetson_deploy.py --model best.engine --camera 0
  
  # Run on RTSP stream
  python jetson_deploy.py --model best.engine --rtsp rtsp://192.168.1.100/stream
  
  # Run benchmark
  python jetson_deploy.py --model best.engine --benchmark
  
  # Multi-camera
  python jetson_deploy.py --model best.engine --multi-camera 0,1,2,3
        """
    )
    
    parser.add_argument("--model", type=str, required=True,
                        help="Path to model file (.pt, .onnx, or .engine)")
    parser.add_argument("--export", action="store_true",
                        help="Export model to TensorRT engine")
    parser.add_argument("--camera", type=int, default=None,
                        help="Camera device index (e.g., 0)")
    parser.add_argument("--rtsp", type=str, default=None,
                        help="RTSP stream URL")
    parser.add_argument("--video", type=str, default=None,
                        help="Path to video file")
    parser.add_argument("--output", type=str, default=None,
                        help="Output video file path")
    parser.add_argument("--benchmark", action="store_true",
                        help="Run performance benchmark")
    parser.add_argument("--headless", action="store_true",
                        help="Run without display (for servers)")
    parser.add_argument("--no-track", action="store_true",
                        help="Disable object tracking")
    parser.add_argument("--imgsz", type=int, default=640,
                        help="Inference image size")
    parser.add_argument("--conf", type=float, default=0.4,
                        help="Confidence threshold")
    parser.add_argument("--multi-camera", type=str, default=None,
                        help="Comma-separated camera indices for multi-camera mode")
    
    args = parser.parse_args()
    
    # Print banner
    print("""
╔════════════════════════════════════════════════════════════════════╗
║     🚀 JETSON ORIN NANO DEPLOYMENT - InvEye Detection System 🚀   ║
║                                                                    ║
║  Detects: 🔥 Fire | 💨 Smoke | 👊 Fighting | 👤 Face | 🔪 Weapon  ║
╚════════════════════════════════════════════════════════════════════╝
    """)
    
    print(f"Platform: {'NVIDIA Jetson' if IS_JETSON else 'Desktop/Server'}")
    
    # Update settings
    JETSON_SETTINGS['imgsz'] = args.imgsz
    JETSON_SETTINGS['conf'] = args.conf
    
    # Export mode
    if args.export:
        export_to_tensorrt(args.model, imgsz=args.imgsz)
        return
    
    # Benchmark mode
    if args.benchmark:
        run_benchmark(args.model)
        return
    
    # Multi-camera mode
    if args.multi_camera:
        cameras = [int(c.strip()) for c in args.multi_camera.split(',')]
        run_multi_camera(args.model, cameras, headless=args.headless)
        return
    
    # Determine video source
    source = None
    if args.camera is not None:
        source = args.camera
    elif args.rtsp:
        source = args.rtsp
    elif args.video:
        source = args.video
    else:
        print("⚠️ No video source specified. Using camera 0")
        source = 0
    
    # Run inference
    run_camera_inference(
        args.model,
        camera_source=source,
        track=not args.no_track,
        output=args.output,
        headless=args.headless
    )


if __name__ == "__main__":
    main()
