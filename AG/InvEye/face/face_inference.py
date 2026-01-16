#!/usr/bin/env python3
"""
Face Detection Inference Script for Petrol Pump Deployment
InvEye Analytics | YOLO11n Edge Inference

Usage:
    # Webcam
    python face_inference.py --source 0
    
    # RTSP stream
    python face_inference.py --source "rtsp://192.168.1.100:554/stream"
    
    # Video file
    python face_inference.py --source video.mp4 --save
    
    # Image
    python face_inference.py --source image.jpg --save
"""

import argparse
import cv2
import time
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional

try:
    from ultralytics import YOLO
except ImportError:
    print("Error: ultralytics not installed. Run: pip install ultralytics")
    exit(1)


class FaceDetector:
    """Face detection wrapper for YOLO11n model."""
    
    def __init__(
        self,
        model_path: str = "face_detector.pt",
        conf_threshold: float = 0.5,
        iou_threshold: float = 0.45,
        device: str = "0"
    ):
        """Initialize the face detector.
        
        Args:
            model_path: Path to YOLO model (.pt, .onnx, or .engine)
            conf_threshold: Confidence threshold for detections
            iou_threshold: IoU threshold for NMS
            device: Device to run inference on ("0" for GPU, "cpu" for CPU)
        """
        self.model_path = model_path
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.device = device
        
        print(f"Loading model: {model_path}")
        self.model = YOLO(model_path)
        print(f"✅ Model loaded successfully")
        
        # Stats
        self.total_detections = 0
        self.frame_count = 0
        self.start_time = None
    
    def detect(self, frame) -> List[Dict]:
        """Detect faces in a frame.
        
        Args:
            frame: OpenCV image (BGR format)
            
        Returns:
            List of detection dictionaries with keys:
            - bbox: [x1, y1, x2, y2]
            - confidence: float
            - class_name: str
        """
        results = self.model.predict(
            source=frame,
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            device=self.device,
            verbose=False
        )
        
        detections = []
        
        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0].cpu().numpy())
                cls = int(box.cls[0].cpu().numpy())
                
                detections.append({
                    "bbox": [int(x1), int(y1), int(x2), int(y2)],
                    "confidence": round(conf, 3),
                    "class_name": "face"
                })
        
        self.total_detections += len(detections)
        self.frame_count += 1
        
        return detections
    
    def draw_detections(
        self,
        frame,
        detections: List[Dict],
        show_conf: bool = True,
        color: Tuple[int, int, int] = (0, 255, 0)
    ):
        """Draw bounding boxes on frame.
        
        Args:
            frame: OpenCV image to draw on
            detections: List of detection dictionaries
            show_conf: Whether to show confidence scores
            color: BGR color for boxes
            
        Returns:
            Frame with drawn detections
        """
        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            conf = det["confidence"]
            
            # Draw box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            if show_conf:
                label = f"Face {conf:.2f}"
            else:
                label = "Face"
            
            # Background for text
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(frame, (x1, y1 - 20), (x1 + w + 10, y1), color, -1)
            cv2.putText(
                frame, label, (x1 + 5, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1
            )
        
        return frame
    
    def draw_stats(self, frame):
        """Draw statistics overlay on frame."""
        if self.start_time is None:
            self.start_time = time.time()
        
        elapsed = time.time() - self.start_time
        fps = self.frame_count / elapsed if elapsed > 0 else 0
        
        stats = [
            f"FPS: {fps:.1f}",
            f"Frames: {self.frame_count}",
            f"Total Faces: {self.total_detections}"
        ]
        
        y = 30
        for stat in stats:
            cv2.putText(
                frame, stat, (10, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2
            )
            y += 25
        
        return frame


def run_inference(
    model_path: str,
    source,
    conf: float = 0.5,
    show: bool = True,
    save: bool = False,
    output_dir: str = "output"
):
    """Run face detection inference.
    
    Args:
        model_path: Path to YOLO model
        source: Video source (0 for webcam, path, or RTSP URL)
        conf: Confidence threshold
        show: Whether to display output window
        save: Whether to save output
        output_dir: Directory to save outputs
    """
    detector = FaceDetector(model_path=model_path, conf_threshold=conf)
    
    # Open video source
    if isinstance(source, str) and source.isdigit():
        source = int(source)
    
    cap = cv2.VideoCapture(source)
    
    if not cap.isOpened():
        print(f"Error: Could not open source: {source}")
        return
    
    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps_video = cap.get(cv2.CAP_PROP_FPS) or 30
    
    print(f"Source: {source}")
    print(f"Resolution: {width}x{height}")
    print(f"FPS: {fps_video}")
    
    # Setup video writer if saving
    writer = None
    if save:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"{output_dir}/face_detection_{timestamp}.mp4"
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(output_path, fourcc, fps_video, (width, height))
        print(f"Saving to: {output_path}")
    
    print("\n" + "="*50)
    print("Starting face detection... Press 'q' to quit")
    print("="*50 + "\n")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect faces
            detections = detector.detect(frame)
            
            # Draw results
            frame = detector.draw_detections(frame, detections)
            frame = detector.draw_stats(frame)
            
            # Log detections
            if detections:
                print(f"Frame {detector.frame_count}: {len(detections)} face(s) detected")
            
            # Save frame
            if writer:
                writer.write(frame)
            
            # Show frame
            if show:
                cv2.imshow("Face Detection - InvEye", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    
    finally:
        cap.release()
        if writer:
            writer.release()
        cv2.destroyAllWindows()
        
        # Print summary
        elapsed = time.time() - detector.start_time if detector.start_time else 0
        print("\n" + "="*50)
        print("INFERENCE SUMMARY")
        print("="*50)
        print(f"Total Frames:     {detector.frame_count}")
        print(f"Total Detections: {detector.total_detections}")
        print(f"Elapsed Time:     {elapsed:.2f}s")
        print(f"Average FPS:      {detector.frame_count/elapsed:.1f}")
        if save:
            print(f"Saved to:         {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Face Detection Inference for Petrol Pump Deployment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python face_inference.py --source 0                    # Webcam
  python face_inference.py --source video.mp4 --save     # Video file
  python face_inference.py --source rtsp://ip:554/stream # RTSP camera
  python face_inference.py --source image.jpg --save     # Single image
        """
    )
    
    parser.add_argument(
        "--model", 
        default="face_detector.pt",
        help="Path to YOLO model (.pt, .onnx, or .engine)"
    )
    parser.add_argument(
        "--source",
        default="0",
        help="Video source: 0 for webcam, path to file, or RTSP URL"
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.5,
        help="Confidence threshold (default: 0.5)"
    )
    parser.add_argument(
        "--show",
        action="store_true",
        default=True,
        help="Display output window"
    )
    parser.add_argument(
        "--no-show",
        action="store_true",
        help="Disable output window (for headless mode)"
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save output video"
    )
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Output directory for saved files"
    )
    
    args = parser.parse_args()
    
    # Handle show flag
    show = not args.no_show
    
    run_inference(
        model_path=args.model,
        source=args.source,
        conf=args.conf,
        show=show,
        save=args.save,
        output_dir=args.output_dir
    )


if __name__ == "__main__":
    main()
