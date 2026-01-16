#!/usr/bin/env python3
"""
InvEye Production Pipeline - Multi-Camera Video Analytics
==========================================================

Combines:
- YOLOv11n Face Detection
- InsightFace buffalo_sc Recognition  
- YOLO Object Detection (Fire, Fight, Smoke, Person)

Optimized for Jetson Orin Nano with 4 cameras.

Usage:
    python main_pipeline.py --config config.yaml
    python main_pipeline.py --cameras rtsp://cam1 rtsp://cam2 --show
"""

import os
import sys
import time
import json
import logging
import argparse
import threading
import queue
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from collections import defaultdict

import cv2
import numpy as np
import yaml

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('InvEye')


@dataclass
class Detection:
    """Single detection result."""
    class_name: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2
    class_id: int = 0
    track_id: Optional[int] = None
    embedding: Optional[np.ndarray] = None
    identity: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


@dataclass
class FrameResult:
    """Results for a single frame."""
    camera_id: str
    timestamp: datetime
    frame: np.ndarray
    faces: List[Detection] = field(default_factory=list)
    objects: List[Detection] = field(default_factory=list)
    alerts: List[Dict] = field(default_factory=list)
    processing_time_ms: float = 0.0


class ModelManager:
    """Manages all AI models with lazy loading and optimization."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.device = config.get('device', 'cuda:0')
        
        # Models (lazy loaded)
        self._face_detector = None
        self._object_detector = None
        self._face_recognizer = None
        
        # Model paths
        self.face_model_path = config.get('face_detection_model', 'yolov11n-face.pt')
        self.object_model_path = config.get('object_detection_model', 'yolov11n.pt')
        self.recognition_model = config.get('recognition_model', 'buffalo_sc')
        
        logger.info(f"ModelManager initialized with device: {self.device}")
    
    @property
    def face_detector(self):
        """Lazy load face detection model."""
        if self._face_detector is None:
            from ultralytics import YOLO
            logger.info(f"Loading face detector: {self.face_model_path}")
            self._face_detector = YOLO(self.face_model_path)
            logger.info("Face detector loaded successfully")
        return self._face_detector
    
    @property
    def object_detector(self):
        """Lazy load object detection model."""
        if self._object_detector is None:
            from ultralytics import YOLO
            logger.info(f"Loading object detector: {self.object_model_path}")
            self._object_detector = YOLO(self.object_model_path)
            logger.info("Object detector loaded successfully")
        return self._object_detector
    
    @property
    def face_recognizer(self):
        """Lazy load face recognition model."""
        if self._face_recognizer is None:
            try:
                from insightface.app import FaceAnalysis
                logger.info(f"Loading face recognizer: {self.recognition_model}")
                self._face_recognizer = FaceAnalysis(
                    name=self.recognition_model,
                    providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
                )
                self._face_recognizer.prepare(ctx_id=0, det_size=(160, 160))
                logger.info("Face recognizer loaded successfully")
            except ImportError:
                logger.warning("InsightFace not installed. Face recognition disabled.")
                self._face_recognizer = None
            except Exception as e:
                logger.error(f"Failed to load face recognizer: {e}")
                self._face_recognizer = None
        return self._face_recognizer
    
    def detect_faces(self, frame: np.ndarray, conf: float = 0.5) -> List[Detection]:
        """Detect faces in frame."""
        detections = []
        
        results = self.face_detector.predict(
            source=frame,
            conf=conf,
            device=self.device,
            verbose=False
        )
        
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                conf = float(box.conf[0].cpu().numpy())
                
                detections.append(Detection(
                    class_name='face',
                    confidence=conf,
                    bbox=(x1, y1, x2, y2),
                    class_id=0
                ))
        
        return detections
    
    def detect_objects(self, frame: np.ndarray, conf: float = 0.5) -> List[Detection]:
        """Detect objects (fire, fight, smoke, person) in frame."""
        detections = []
        
        results = self.object_detector.predict(
            source=frame,
            conf=conf,
            device=self.device,
            verbose=False
        )
        
        for r in results:
            names = r.names
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                conf = float(box.conf[0].cpu().numpy())
                cls_id = int(box.cls[0].cpu().numpy())
                cls_name = names.get(cls_id, f'class_{cls_id}')
                
                detections.append(Detection(
                    class_name=cls_name,
                    confidence=conf,
                    bbox=(x1, y1, x2, y2),
                    class_id=cls_id
                ))
        
        return detections
    
    def recognize_face(self, frame: np.ndarray, bbox: Tuple[int, int, int, int]) -> Optional[np.ndarray]:
        """Get face embedding for recognition."""
        if self.face_recognizer is None:
            return None
        
        x1, y1, x2, y2 = bbox
        
        # Expand bbox slightly for better recognition
        h, w = frame.shape[:2]
        pad = int((x2 - x1) * 0.1)
        x1 = max(0, x1 - pad)
        y1 = max(0, y1 - pad)
        x2 = min(w, x2 + pad)
        y2 = min(h, y2 + pad)
        
        face_crop = frame[y1:y2, x1:x2]
        
        if face_crop.size == 0:
            return None
        
        try:
            faces = self.face_recognizer.get(face_crop)
            if faces and len(faces) > 0:
                return faces[0].embedding
        except Exception as e:
            logger.debug(f"Recognition failed: {e}")
        
        return None


class FaceDatabase:
    """Manages known face embeddings for recognition."""
    
    def __init__(self, db_path: str = "face_database"):
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        self.embeddings: Dict[str, np.ndarray] = {}
        self.metadata: Dict[str, Dict] = {}
        
        self._load_database()
    
    def _load_database(self):
        """Load existing face database."""
        db_file = self.db_path / "embeddings.npz"
        meta_file = self.db_path / "metadata.json"
        
        if db_file.exists():
            data = np.load(db_file, allow_pickle=True)
            for name in data.files:
                self.embeddings[name] = data[name]
            logger.info(f"Loaded {len(self.embeddings)} face embeddings")
        
        if meta_file.exists():
            with open(meta_file, 'r') as f:
                self.metadata = json.load(f)
    
    def save_database(self):
        """Save face database to disk."""
        if self.embeddings:
            np.savez(self.db_path / "embeddings.npz", **self.embeddings)
        
        with open(self.db_path / "metadata.json", 'w') as f:
            json.dump(self.metadata, f, indent=2)
        
        logger.info(f"Saved {len(self.embeddings)} face embeddings")
    
    def add_face(self, person_id: str, embedding: np.ndarray, metadata: Dict = None):
        """Add or update a face in the database."""
        self.embeddings[person_id] = embedding
        self.metadata[person_id] = metadata or {}
        self.save_database()
        logger.info(f"Added face for: {person_id}")
    
    def find_match(self, embedding: np.ndarray, threshold: float = 0.5) -> Tuple[Optional[str], float]:
        """Find matching face in database."""
        if not self.embeddings or embedding is None:
            return None, 0.0
        
        best_match = None
        best_score = 0.0
        
        for person_id, stored_embedding in self.embeddings.items():
            # Cosine similarity
            similarity = np.dot(embedding, stored_embedding) / (
                np.linalg.norm(embedding) * np.linalg.norm(stored_embedding)
            )
            
            if similarity > best_score:
                best_score = similarity
                best_match = person_id
        
        if best_score >= threshold:
            return best_match, best_score
        
        return None, best_score
    
    def get_all_persons(self) -> List[str]:
        """Get list of all registered persons."""
        return list(self.embeddings.keys())


class AlertManager:
    """Manages alerts and notifications."""
    
    # Alert severity levels
    SEVERITY_LOW = 'low'
    SEVERITY_MEDIUM = 'medium'
    SEVERITY_HIGH = 'high'
    SEVERITY_CRITICAL = 'critical'
    
    # Alert types with severity mapping
    ALERT_CONFIG = {
        'fire': {'severity': 'critical', 'cooldown': 30},
        'smoke': {'severity': 'high', 'cooldown': 30},
        'fight': {'severity': 'critical', 'cooldown': 30},
        'violence': {'severity': 'critical', 'cooldown': 30},
        'unknown_person': {'severity': 'medium', 'cooldown': 60},
        'no_employee': {'severity': 'low', 'cooldown': 300},
    }
    
    def __init__(self, callback=None):
        self.callback = callback
        self.alert_history: List[Dict] = []
        self.last_alert_time: Dict[str, float] = defaultdict(float)
        self._lock = threading.Lock()
    
    def create_alert(
        self,
        alert_type: str,
        camera_id: str,
        detection: Detection = None,
        message: str = None,
        frame: np.ndarray = None
    ) -> Optional[Dict]:
        """Create an alert if cooldown allows."""
        
        config = self.ALERT_CONFIG.get(alert_type, {'severity': 'medium', 'cooldown': 60})
        
        with self._lock:
            key = f"{alert_type}_{camera_id}"
            now = time.time()
            
            if now - self.last_alert_time[key] < config['cooldown']:
                return None  # Still in cooldown
            
            self.last_alert_time[key] = now
        
        alert = {
            'id': f"{alert_type}_{camera_id}_{int(now)}",
            'type': alert_type,
            'severity': config['severity'],
            'camera_id': camera_id,
            'timestamp': datetime.now().isoformat(),
            'message': message or f"{alert_type.upper()} detected on {camera_id}",
            'detection': {
                'class': detection.class_name if detection else None,
                'confidence': detection.confidence if detection else None,
                'bbox': detection.bbox if detection else None,
            } if detection else None
        }
        
        self.alert_history.append(alert)
        
        # Keep only last 1000 alerts
        if len(self.alert_history) > 1000:
            self.alert_history = self.alert_history[-500:]
        
        # Trigger callback
        if self.callback:
            try:
                self.callback(alert, frame)
            except Exception as e:
                logger.error(f"Alert callback failed: {e}")
        
        logger.warning(f"ALERT [{alert['severity'].upper()}]: {alert['message']}")
        
        return alert


class CameraStream:
    """Handles video stream from a single camera."""
    
    def __init__(self, camera_id: str, source, fps_limit: int = 15):
        self.camera_id = camera_id
        self.source = source
        self.fps_limit = fps_limit
        
        self.cap = None
        self.running = False
        self.frame_queue = queue.Queue(maxsize=2)
        self.thread = None
        
        self.frame_count = 0
        self.fps = 0.0
        self.last_fps_time = time.time()
    
    def start(self):
        """Start the camera stream."""
        self.cap = cv2.VideoCapture(self.source)
        
        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open camera: {self.source}")
        
        # Set buffer size to minimize latency
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        self.running = True
        self.thread = threading.Thread(target=self._read_frames, daemon=True)
        self.thread.start()
        
        logger.info(f"Camera {self.camera_id} started: {self.source}")
    
    def stop(self):
        """Stop the camera stream."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        if self.cap:
            self.cap.release()
        logger.info(f"Camera {self.camera_id} stopped")
    
    def _read_frames(self):
        """Background thread to read frames."""
        frame_interval = 1.0 / self.fps_limit
        last_frame_time = 0
        
        while self.running:
            ret, frame = self.cap.read()
            
            if not ret:
                logger.warning(f"Camera {self.camera_id}: Failed to read frame, reconnecting...")
                time.sleep(1.0)
                self.cap.release()
                self.cap = cv2.VideoCapture(self.source)
                continue
            
            # FPS limiting
            now = time.time()
            if now - last_frame_time < frame_interval:
                continue
            last_frame_time = now
            
            # Update FPS counter
            self.frame_count += 1
            if now - self.last_fps_time >= 1.0:
                self.fps = self.frame_count / (now - self.last_fps_time)
                self.frame_count = 0
                self.last_fps_time = now
            
            # Put frame in queue (drop old frames if full)
            try:
                if self.frame_queue.full():
                    self.frame_queue.get_nowait()
                self.frame_queue.put_nowait((frame, datetime.now()))
            except queue.Empty:
                pass
    
    def get_frame(self, timeout: float = 0.1) -> Optional[Tuple[np.ndarray, datetime]]:
        """Get latest frame from camera."""
        try:
            return self.frame_queue.get(timeout=timeout)
        except queue.Empty:
            return None


class InvEyePipeline:
    """Main production pipeline for InvEye video analytics."""
    
    def __init__(self, config_path: str = None, config: Dict = None):
        """Initialize the pipeline.
        
        Args:
            config_path: Path to YAML config file
            config: Config dictionary (overrides config_path)
        """
        self.config = self._load_config(config_path, config)
        
        # Initialize components
        self.model_manager = ModelManager(self.config.get('models', {}))
        self.face_database = FaceDatabase(self.config.get('face_database_path', 'face_database'))
        self.alert_manager = AlertManager(callback=self._on_alert)
        
        # Cameras
        self.cameras: Dict[str, CameraStream] = {}
        
        # Processing settings
        self.face_detection_interval = self.config.get('face_detection_interval', 1)
        self.object_detection_interval = self.config.get('object_detection_interval', 1)
        self.recognition_interval = self.config.get('recognition_interval', 3)
        
        # Stats
        self.stats = defaultdict(lambda: defaultdict(int))
        self.running = False
        
        # Alert classes
        self.alert_classes = set(self.config.get('alert_classes', ['fire', 'smoke', 'fight', 'violence']))
        
        logger.info("InvEye Pipeline initialized")
    
    def _load_config(self, config_path: str, config: Dict) -> Dict:
        """Load configuration."""
        if config:
            return config
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        
        # Default config
        return {
            'models': {
                'device': 'cuda:0',
                'face_detection_model': 'yolov11n-face.pt',
                'object_detection_model': 'yolov11n.pt',
                'recognition_model': 'buffalo_sc',
            },
            'face_database_path': 'face_database',
            'face_detection_interval': 1,
            'object_detection_interval': 1,
            'recognition_interval': 3,
            'face_confidence': 0.5,
            'object_confidence': 0.5,
            'recognition_threshold': 0.5,
            'alert_classes': ['fire', 'smoke', 'fight', 'violence'],
        }
    
    def _on_alert(self, alert: Dict, frame: np.ndarray = None):
        """Handle alert callback."""
        # Save alert frame
        if frame is not None and self.config.get('save_alert_frames', True):
            alerts_dir = Path(self.config.get('alerts_dir', 'alerts'))
            alerts_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"{alert['id']}.jpg"
            cv2.imwrite(str(alerts_dir / filename), frame)
    
    def add_camera(self, camera_id: str, source, fps_limit: int = 15):
        """Add a camera to the pipeline."""
        if camera_id in self.cameras:
            logger.warning(f"Camera {camera_id} already exists, replacing...")
            self.cameras[camera_id].stop()
        
        self.cameras[camera_id] = CameraStream(camera_id, source, fps_limit)
        logger.info(f"Added camera: {camera_id} -> {source}")
    
    def remove_camera(self, camera_id: str):
        """Remove a camera from the pipeline."""
        if camera_id in self.cameras:
            self.cameras[camera_id].stop()
            del self.cameras[camera_id]
            logger.info(f"Removed camera: {camera_id}")
    
    def register_face(self, person_id: str, image_path: str = None, frame: np.ndarray = None):
        """Register a new face in the database."""
        if image_path:
            frame = cv2.imread(image_path)
        
        if frame is None:
            raise ValueError("Must provide image_path or frame")
        
        # Detect face
        faces = self.model_manager.detect_faces(frame)
        if not faces:
            raise ValueError("No face detected in image")
        
        # Get embedding for largest face
        largest_face = max(faces, key=lambda f: (f.bbox[2]-f.bbox[0]) * (f.bbox[3]-f.bbox[1]))
        embedding = self.model_manager.recognize_face(frame, largest_face.bbox)
        
        if embedding is None:
            raise ValueError("Failed to extract face embedding")
        
        self.face_database.add_face(person_id, embedding, {'registered_at': datetime.now().isoformat()})
        return True
    
    def process_frame(self, camera_id: str, frame: np.ndarray, frame_num: int) -> FrameResult:
        """Process a single frame through all detection pipelines."""
        start_time = time.time()
        
        result = FrameResult(
            camera_id=camera_id,
            timestamp=datetime.now(),
            frame=frame
        )
        
        # Face detection (every N frames)
        if frame_num % self.face_detection_interval == 0:
            faces = self.model_manager.detect_faces(
                frame, 
                conf=self.config.get('face_confidence', 0.5)
            )
            result.faces = faces
            
            # Face recognition (less frequent)
            if frame_num % self.recognition_interval == 0:
                for face in faces:
                    embedding = self.model_manager.recognize_face(frame, face.bbox)
                    if embedding is not None:
                        face.embedding = embedding
                        identity, score = self.face_database.find_match(
                            embedding,
                            threshold=self.config.get('recognition_threshold', 0.5)
                        )
                        face.identity = identity
                        face.metadata['match_score'] = score
                        
                        # Alert for unknown person
                        if identity is None and self.config.get('alert_unknown_faces', False):
                            self.alert_manager.create_alert(
                                'unknown_person',
                                camera_id,
                                face,
                                f"Unknown person detected on {camera_id}"
                            )
        
        # Object detection (every N frames)
        if frame_num % self.object_detection_interval == 0:
            objects = self.model_manager.detect_objects(
                frame,
                conf=self.config.get('object_confidence', 0.5)
            )
            result.objects = objects
            
            # Check for alert conditions
            for obj in objects:
                if obj.class_name.lower() in self.alert_classes:
                    alert = self.alert_manager.create_alert(
                        obj.class_name.lower(),
                        camera_id,
                        obj,
                        frame=frame
                    )
                    if alert:
                        result.alerts.append(alert)
        
        result.processing_time_ms = (time.time() - start_time) * 1000
        
        # Update stats
        self.stats[camera_id]['frames_processed'] += 1
        self.stats[camera_id]['faces_detected'] += len(result.faces)
        self.stats[camera_id]['objects_detected'] += len(result.objects)
        
        return result
    
    def draw_results(self, frame: np.ndarray, result: FrameResult) -> np.ndarray:
        """Draw detection results on frame."""
        frame = frame.copy()
        
        # Draw faces
        for face in result.faces:
            x1, y1, x2, y2 = face.bbox
            color = (0, 255, 0) if face.identity else (0, 165, 255)  # Green if known, orange if unknown
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            label = face.identity or 'Unknown'
            if face.metadata.get('match_score'):
                label += f" ({face.metadata['match_score']:.2f})"
            
            cv2.putText(frame, label, (x1, y1 - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Draw objects
        for obj in result.objects:
            x1, y1, x2, y2 = obj.bbox
            
            # Color based on alert class
            if obj.class_name.lower() in self.alert_classes:
                color = (0, 0, 255)  # Red for alerts
            else:
                color = (255, 0, 0)  # Blue for normal
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            label = f"{obj.class_name} {obj.confidence:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Draw info overlay
        info_text = [
            f"Camera: {result.camera_id}",
            f"Faces: {len(result.faces)}",
            f"Objects: {len(result.objects)}",
            f"Time: {result.processing_time_ms:.1f}ms"
        ]
        
        y = 30
        for text in info_text:
            cv2.putText(frame, text, (10, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            y += 25
        
        return frame
    
    def run(self, show: bool = False, output_dir: str = None):
        """Run the pipeline on all cameras."""
        if not self.cameras:
            raise RuntimeError("No cameras configured")
        
        # Start all cameras
        for cam in self.cameras.values():
            cam.start()
        
        self.running = True
        frame_counts = defaultdict(int)
        
        # Output video writers
        writers = {}
        if output_dir:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Pipeline running with {len(self.cameras)} cameras")
        
        try:
            while self.running:
                for camera_id, camera in self.cameras.items():
                    frame_data = camera.get_frame(timeout=0.01)
                    
                    if frame_data is None:
                        continue
                    
                    frame, timestamp = frame_data
                    frame_counts[camera_id] += 1
                    
                    # Process frame
                    result = self.process_frame(camera_id, frame, frame_counts[camera_id])
                    
                    # Draw results
                    if show or output_dir:
                        display_frame = self.draw_results(frame, result)
                        
                        if show:
                            cv2.imshow(f"InvEye - {camera_id}", display_frame)
                        
                        if output_dir:
                            if camera_id not in writers:
                                h, w = frame.shape[:2]
                                output_path = Path(output_dir) / f"{camera_id}.mp4"
                                writers[camera_id] = cv2.VideoWriter(
                                    str(output_path),
                                    cv2.VideoWriter_fourcc(*'mp4v'),
                                    15, (w, h)
                                )
                            writers[camera_id].write(display_frame)
                
                # Check for quit
                if show:
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        break
                    elif key == ord('s'):
                        self._print_stats()
        
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        
        finally:
            self.running = False
            
            # Cleanup
            for cam in self.cameras.values():
                cam.stop()
            
            for writer in writers.values():
                writer.release()
            
            cv2.destroyAllWindows()
            
            self._print_stats()
    
    def _print_stats(self):
        """Print pipeline statistics."""
        print("\n" + "="*60)
        print("PIPELINE STATISTICS")
        print("="*60)
        
        for camera_id, stats in self.stats.items():
            print(f"\n{camera_id}:")
            for key, value in stats.items():
                print(f"  {key}: {value}")
        
        print("\nAlerts:")
        for alert in self.alert_manager.alert_history[-10:]:
            print(f"  [{alert['severity']}] {alert['message']}")
        
        print("="*60)


def main():
    parser = argparse.ArgumentParser(description='InvEye Production Pipeline')
    
    parser.add_argument('--config', type=str, help='Path to config.yaml')
    parser.add_argument('--cameras', nargs='+', help='Camera sources (file paths or RTSP URLs)')
    parser.add_argument('--show', action='store_true', help='Display output windows')
    parser.add_argument('--output', type=str, help='Output directory for recorded videos')
    parser.add_argument('--fps', type=int, default=15, help='FPS limit per camera')
    
    args = parser.parse_args()
    
    # Initialize pipeline
    pipeline = InvEyePipeline(config_path=args.config)
    
    # Add cameras from command line
    if args.cameras:
        for i, source in enumerate(args.cameras):
            # Convert numeric strings to int (webcam index)
            if source.isdigit():
                source = int(source)
            pipeline.add_camera(f"camera_{i+1}", source, fps_limit=args.fps)
    
    # Run pipeline
    pipeline.run(show=args.show, output_dir=args.output)


if __name__ == '__main__':
    main()
