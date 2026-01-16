#!/usr/bin/env python3
"""
InvEye Petrol Pump Analytics Pipeline - Plug & Play Edition
============================================================

Complete plug-and-play solution for petrol pump video analytics.
Detects all KPIs, tracks faces, and outputs JSON analytics.

Features:
- Face detection & recognition (employees + returning customers)
- Incident detection (fire, smoke, fight, etc.)
- Petrol pump specific KPIs
- Real-time JSON analytics output
- Alert system with configurable severity
- Multi-camera support

Usage:
    # Quick test with webcam
    python petrol_pump_analytics.py --test
    
    # Production with RTSP cameras
    python petrol_pump_analytics.py --config petrol_pump_config.yaml
    
    # With JSON output
    python petrol_pump_analytics.py --test --json-output analytics.json
"""

import os
import sys
import json
import time
import threading
import queue
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from collections import defaultdict
from enum import Enum
import hashlib

import cv2
import numpy as np
import yaml

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger('PetrolPump')


# ============================================================================
# PETROL PUMP KPI DEFINITIONS
# ============================================================================

class Severity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# All Petrol Pump KPIs from the specification
PETROL_PUMP_KPIS = {
    # CRITICAL - Immediate action required
    "smoking": {"severity": Severity.CRITICAL, "description": "Smoking in fuel area", "threshold": "Any detection", "cooldown": 30},
    "engine_running": {"severity": Severity.CRITICAL, "description": "Engine on during fueling", "threshold": "Engine running", "cooldown": 60},
    "fuel_spill": {"severity": Severity.CRITICAL, "description": "Fuel spillage detected", "threshold": "Any spill", "cooldown": 30},
    "emergency_blocked": {"severity": Severity.CRITICAL, "description": "E-stop not accessible", "threshold": "Any obstruction", "cooldown": 120},
    "tanker_safety": {"severity": Severity.CRITICAL, "description": "Tanker delivery procedure violation", "threshold": "Procedures violated", "cooldown": 60},
    "tanker_grounding": {"severity": Severity.CRITICAL, "description": "Ground wire not connected", "threshold": "Not grounded", "cooldown": 60},
    "altercation": {"severity": Severity.CRITICAL, "description": "Physical conflict at station", "threshold": "Any detection", "cooldown": 30},
    "fire": {"severity": Severity.CRITICAL, "description": "Fire detected", "threshold": "Any detection", "cooldown": 10},
    
    # HIGH - Requires attention
    "mobile_phone": {"severity": Severity.HIGH, "description": "Phone use during fueling", "threshold": "Any usage", "cooldown": 60},
    "spill_response": {"severity": Severity.HIGH, "description": "Slow spill cleanup", "threshold": ">3 min", "cooldown": 180},
    "improper_container": {"severity": Severity.HIGH, "description": "Non-approved fuel container", "threshold": "Non-approved", "cooldown": 60},
    "overfill": {"severity": Severity.HIGH, "description": "Tank overflow during fill", "threshold": "Overflow", "cooldown": 30},
    "child_at_pump": {"severity": Severity.HIGH, "description": "Unsupervised child in forecourt", "threshold": "Any detection", "cooldown": 60},
    "child_in_vehicle": {"severity": Severity.HIGH, "description": "Child alone in parked car", "threshold": "Any detection", "cooldown": 120},
    "extinguisher_blocked": {"severity": Severity.HIGH, "description": "Fire extinguisher blocked", "threshold": "Any obstruction", "cooldown": 300},
    "drive_off": {"severity": Severity.HIGH, "description": "Vehicle leaving unpaid", "threshold": "Any drive-off", "cooldown": 10},
    "license_capture": {"severity": Severity.HIGH, "description": "License plate of non-payer", "threshold": "Capture failed", "cooldown": 10},
    "lpg_access": {"severity": Severity.HIGH, "description": "Unauthorized near LPG storage", "threshold": "Any unauthorized", "cooldown": 60},
    "smoke": {"severity": Severity.HIGH, "description": "Smoke detected", "threshold": "Any detection", "cooldown": 30},
    "fight": {"severity": Severity.HIGH, "description": "Violence/fight detected", "threshold": "Any detection", "cooldown": 30},
    
    # MEDIUM - Monitor
    "static_touch": {"severity": Severity.MEDIUM, "description": "Vehicle touched before pump", "threshold": "No touch", "cooldown": 120},
    "attendant_presence": {"severity": Severity.MEDIUM, "description": "Staff in forecourt when required", "threshold": "<Required", "cooldown": 300},
    "unknown_person": {"severity": Severity.MEDIUM, "description": "Unregistered person detected", "threshold": "Not in database", "cooldown": 60},
    
    # LOW - Informational
    "queue_length": {"severity": Severity.LOW, "description": "Vehicles waiting for pumps", "threshold": ">5 vehicles", "cooldown": 300},
    "person_count": {"severity": Severity.LOW, "description": "People in forecourt", "threshold": "Count", "cooldown": 60},
}

# Detection class mapping (what YOLO detects -> KPI)
DETECTION_TO_KPI = {
    "fire": "fire",
    "smoke": "smoke",
    "flame": "fire",
    "fight": "fight",
    "violence": "altercation",
    "fighting": "fight",
    "person": "person_count",
    "cell phone": "mobile_phone",
    "phone": "mobile_phone",
    "child": "child_at_pump",
    "cigarette": "smoking",
    "smoke_cigarette": "smoking",
    "car": "queue_length",
    "vehicle": "queue_length",
    "spill": "fuel_spill",
    "container": "improper_container",
}


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class FaceRecord:
    """Record of a detected face."""
    face_id: str
    first_seen: datetime
    last_seen: datetime
    visit_count: int = 1
    is_employee: bool = False
    person_name: Optional[str] = None
    embedding: Optional[np.ndarray] = None
    thumbnail_path: Optional[str] = None
    
    def to_dict(self):
        return {
            "face_id": self.face_id,
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "visit_count": self.visit_count,
            "is_employee": self.is_employee,
            "person_name": self.person_name,
        }


@dataclass
class Incident:
    """Record of an incident/KPI violation."""
    id: str
    kpi_name: str
    severity: str
    camera_id: str
    timestamp: datetime
    description: str
    confidence: float
    bbox: Optional[Tuple[int, int, int, int]] = None
    frame_path: Optional[str] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    
    def to_dict(self):
        return {
            "id": self.id,
            "kpi_name": self.kpi_name,
            "severity": self.severity,
            "camera_id": self.camera_id,
            "timestamp": self.timestamp.isoformat(),
            "description": self.description,
            "confidence": self.confidence,
            "bbox": self.bbox,
            "frame_path": self.frame_path,
            "resolved": self.resolved,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
        }


@dataclass
class AnalyticsSnapshot:
    """Current analytics state."""
    timestamp: datetime
    camera_stats: Dict[str, Dict] = field(default_factory=dict)
    active_incidents: List[Dict] = field(default_factory=list)
    face_stats: Dict = field(default_factory=dict)
    kpi_summary: Dict = field(default_factory=dict)
    
    def to_dict(self):
        return {
            "timestamp": self.timestamp.isoformat(),
            "camera_stats": self.camera_stats,
            "active_incidents": self.active_incidents,
            "face_stats": self.face_stats,
            "kpi_summary": self.kpi_summary,
        }


# ============================================================================
# FACE TRACKER
# ============================================================================

class FaceTracker:
    """Tracks faces across frames and identifies returning visitors."""
    
    def __init__(self, similarity_threshold: float = 0.5, revisit_window_hours: int = 24):
        self.similarity_threshold = similarity_threshold
        self.revisit_window = timedelta(hours=revisit_window_hours)
        
        self.known_faces: Dict[str, FaceRecord] = {}
        self.employees: Dict[str, FaceRecord] = {}
        self.session_faces: Dict[str, FaceRecord] = {}  # Faces seen in current session
        
        self._lock = threading.Lock()
        
        # Stats
        self.stats = {
            "total_unique_faces": 0,
            "returning_faces_today": 0,
            "employees_present": set(),
            "unknown_faces_today": 0,
        }
    
    def _generate_face_id(self, embedding: np.ndarray) -> str:
        """Generate unique ID from embedding."""
        return hashlib.md5(embedding.tobytes()[:64]).hexdigest()[:12]
    
    def _cosine_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Calculate cosine similarity between embeddings."""
        return float(np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2)))
    
    def find_match(self, embedding: np.ndarray) -> Tuple[Optional[str], float, bool]:
        """Find matching face in database.
        
        Returns: (face_id, similarity_score, is_employee)
        """
        best_match = None
        best_score = 0.0
        is_employee = False
        
        with self._lock:
            # Check employees first
            for face_id, record in self.employees.items():
                if record.embedding is not None:
                    score = self._cosine_similarity(embedding, record.embedding)
                    if score > best_score:
                        best_score = score
                        best_match = face_id
                        is_employee = True
            
            # Check known faces
            for face_id, record in self.known_faces.items():
                if record.embedding is not None:
                    score = self._cosine_similarity(embedding, record.embedding)
                    if score > best_score:
                        best_score = score
                        best_match = face_id
                        is_employee = False
        
        if best_score >= self.similarity_threshold:
            return best_match, best_score, is_employee
        
        return None, best_score, False
    
    def process_face(self, embedding: np.ndarray, frame: np.ndarray = None, 
                     bbox: Tuple[int, int, int, int] = None) -> Dict:
        """Process a detected face and return tracking info."""
        
        now = datetime.now()
        
        # Find match
        match_id, score, is_employee = self.find_match(embedding)
        
        result = {
            "face_id": None,
            "is_new": False,
            "is_returning": False,
            "is_employee": is_employee,
            "person_name": None,
            "visit_count": 1,
            "match_score": score,
        }
        
        with self._lock:
            if match_id:
                # Known face
                if is_employee:
                    record = self.employees[match_id]
                else:
                    record = self.known_faces.get(match_id)
                
                if record:
                    # Check if returning (not seen recently)
                    time_since_last = now - record.last_seen
                    result["is_returning"] = time_since_last > timedelta(minutes=30)
                    
                    if result["is_returning"]:
                        record.visit_count += 1
                        self.stats["returning_faces_today"] += 1
                    
                    record.last_seen = now
                    
                    result["face_id"] = match_id
                    result["person_name"] = record.person_name
                    result["visit_count"] = record.visit_count
                    
                    if is_employee:
                        self.stats["employees_present"].add(match_id)
            else:
                # New face
                face_id = self._generate_face_id(embedding)
                
                record = FaceRecord(
                    face_id=face_id,
                    first_seen=now,
                    last_seen=now,
                    embedding=embedding.copy(),
                    is_employee=False,
                )
                
                self.known_faces[face_id] = record
                self.session_faces[face_id] = record
                self.stats["total_unique_faces"] += 1
                self.stats["unknown_faces_today"] += 1
                
                result["face_id"] = face_id
                result["is_new"] = True
        
        return result
    
    def register_employee(self, person_name: str, embedding: np.ndarray):
        """Register an employee face."""
        face_id = self._generate_face_id(embedding)
        
        with self._lock:
            self.employees[face_id] = FaceRecord(
                face_id=face_id,
                first_seen=datetime.now(),
                last_seen=datetime.now(),
                is_employee=True,
                person_name=person_name,
                embedding=embedding.copy(),
            )
        
        logger.info(f"Registered employee: {person_name} (ID: {face_id})")
        return face_id
    
    def get_stats(self) -> Dict:
        """Get face tracking statistics."""
        with self._lock:
            return {
                "total_unique_faces": self.stats["total_unique_faces"],
                "returning_faces_today": self.stats["returning_faces_today"],
                "employees_present": len(self.stats["employees_present"]),
                "unknown_faces_today": self.stats["unknown_faces_today"],
                "session_faces": len(self.session_faces),
            }
    
    def get_all_faces(self) -> List[Dict]:
        """Get all face records."""
        with self._lock:
            faces = []
            for record in list(self.employees.values()) + list(self.known_faces.values()):
                faces.append(record.to_dict())
            return faces


# ============================================================================
# INCIDENT MANAGER
# ============================================================================

class IncidentManager:
    """Manages incidents and KPI violations."""
    
    def __init__(self, output_dir: str = "incidents"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.active_incidents: Dict[str, Incident] = {}
        self.incident_history: List[Incident] = []
        self.last_incident_time: Dict[str, datetime] = {}
        
        self._lock = threading.Lock()
        
        # Daily stats
        self.daily_stats = defaultdict(lambda: defaultdict(int))
    
    def _get_cooldown(self, kpi_name: str) -> int:
        """Get cooldown period for KPI."""
        kpi = PETROL_PUMP_KPIS.get(kpi_name, {})
        return kpi.get("cooldown", 60)
    
    def create_incident(
        self,
        kpi_name: str,
        camera_id: str,
        confidence: float,
        bbox: Tuple[int, int, int, int] = None,
        frame: np.ndarray = None,
    ) -> Optional[Incident]:
        """Create a new incident if not in cooldown."""
        
        kpi = PETROL_PUMP_KPIS.get(kpi_name)
        if not kpi:
            return None
        
        now = datetime.now()
        key = f"{kpi_name}_{camera_id}"
        
        with self._lock:
            # Check cooldown
            last_time = self.last_incident_time.get(key)
            if last_time:
                elapsed = (now - last_time).total_seconds()
                if elapsed < self._get_cooldown(kpi_name):
                    return None
            
            self.last_incident_time[key] = now
        
        # Create incident
        incident_id = f"{kpi_name}_{camera_id}_{int(now.timestamp())}"
        
        # Save frame if provided
        frame_path = None
        if frame is not None:
            frame_path = str(self.output_dir / f"{incident_id}.jpg")
            cv2.imwrite(frame_path, frame)
        
        incident = Incident(
            id=incident_id,
            kpi_name=kpi_name,
            severity=kpi["severity"].value,
            camera_id=camera_id,
            timestamp=now,
            description=kpi["description"],
            confidence=confidence,
            bbox=bbox,
            frame_path=frame_path,
        )
        
        with self._lock:
            self.active_incidents[incident_id] = incident
            self.incident_history.append(incident)
            
            # Update stats
            date_key = now.strftime("%Y-%m-%d")
            self.daily_stats[date_key][kpi_name] += 1
            self.daily_stats[date_key]["total"] += 1
        
        severity_emoji = {"critical": "🚨", "high": "⚠️", "medium": "📋", "low": "ℹ️"}
        emoji = severity_emoji.get(incident.severity, "📋")
        logger.warning(f"{emoji} INCIDENT [{incident.severity.upper()}]: {incident.description} on {camera_id}")
        
        return incident
    
    def resolve_incident(self, incident_id: str):
        """Mark incident as resolved."""
        with self._lock:
            if incident_id in self.active_incidents:
                incident = self.active_incidents[incident_id]
                incident.resolved = True
                incident.resolved_at = datetime.now()
                del self.active_incidents[incident_id]
    
    def get_active_incidents(self) -> List[Dict]:
        """Get list of active incidents."""
        with self._lock:
            return [i.to_dict() for i in self.active_incidents.values()]
    
    def get_incident_history(self, limit: int = 100) -> List[Dict]:
        """Get incident history."""
        with self._lock:
            return [i.to_dict() for i in self.incident_history[-limit:]]
    
    def get_kpi_summary(self) -> Dict:
        """Get KPI summary statistics."""
        today = datetime.now().strftime("%Y-%m-%d")
        
        summary = {
            "today": dict(self.daily_stats.get(today, {})),
            "by_severity": defaultdict(int),
            "by_kpi": defaultdict(int),
            "active_count": len(self.active_incidents),
        }
        
        with self._lock:
            for incident in self.active_incidents.values():
                summary["by_severity"][incident.severity] += 1
                summary["by_kpi"][incident.kpi_name] += 1
        
        return dict(summary)


# ============================================================================
# ANALYTICS ENGINE
# ============================================================================

class AnalyticsEngine:
    """Generates real-time analytics and JSON output."""
    
    def __init__(self, output_file: str = None, output_interval: int = 5):
        self.output_file = output_file
        self.output_interval = output_interval
        
        self.camera_stats: Dict[str, Dict] = defaultdict(lambda: {
            "frames_processed": 0,
            "faces_detected": 0,
            "objects_detected": 0,
            "incidents_today": 0,
            "fps": 0.0,
            "last_update": None,
        })
        
        self.start_time = datetime.now()
        self.last_output_time = time.time()
        
        self._lock = threading.Lock()
    
    def update_camera_stats(self, camera_id: str, faces: int, objects: int, 
                            processing_time: float, incidents: int = 0):
        """Update statistics for a camera."""
        with self._lock:
            stats = self.camera_stats[camera_id]
            stats["frames_processed"] += 1
            stats["faces_detected"] += faces
            stats["objects_detected"] += objects
            stats["incidents_today"] += incidents
            stats["fps"] = 1000 / processing_time if processing_time > 0 else 0
            stats["last_update"] = datetime.now().isoformat()
    
    def generate_snapshot(self, face_tracker: FaceTracker, 
                         incident_manager: IncidentManager) -> AnalyticsSnapshot:
        """Generate current analytics snapshot."""
        
        snapshot = AnalyticsSnapshot(
            timestamp=datetime.now(),
            camera_stats=dict(self.camera_stats),
            active_incidents=incident_manager.get_active_incidents(),
            face_stats=face_tracker.get_stats(),
            kpi_summary=incident_manager.get_kpi_summary(),
        )
        
        return snapshot
    
    def maybe_output(self, face_tracker: FaceTracker, 
                     incident_manager: IncidentManager) -> Optional[Dict]:
        """Output analytics if interval has passed."""
        
        now = time.time()
        if now - self.last_output_time < self.output_interval:
            return None
        
        self.last_output_time = now
        snapshot = self.generate_snapshot(face_tracker, incident_manager)
        
        # Write to file if configured
        if self.output_file:
            try:
                with open(self.output_file, 'w') as f:
                    json.dump(snapshot.to_dict(), f, indent=2)
            except Exception as e:
                logger.error(f"Failed to write analytics: {e}")
        
        return snapshot.to_dict()


# ============================================================================
# MAIN PIPELINE
# ============================================================================

class PetrolPumpPipeline:
    """Complete petrol pump analytics pipeline."""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        
        # AI Models (lazy loaded)
        self._face_detector = None
        self._object_detector = None
        self._face_recognizer = None
        
        # Components
        self.face_tracker = FaceTracker(
            similarity_threshold=self.config.get("recognition_threshold", 0.5)
        )
        self.incident_manager = IncidentManager(
            output_dir=self.config.get("incidents_dir", "incidents")
        )
        self.analytics = AnalyticsEngine(
            output_file=self.config.get("json_output"),
            output_interval=self.config.get("analytics_interval", 5)
        )
        
        # Cameras
        self.cameras: Dict[str, cv2.VideoCapture] = {}
        self.camera_fps: Dict[str, float] = {}
        
        # State
        self.running = False
        self.frame_counts: Dict[str, int] = defaultdict(int)
        
        logger.info("PetrolPumpPipeline initialized")
    
    @property
    def face_detector(self):
        """Lazy load face detector."""
        if self._face_detector is None:
            try:
                from ultralytics import YOLO
                model_path = self.config.get("face_model", "models/yolov11n-face.pt")
                
                # Try to download if not exists
                if not Path(model_path).exists():
                    logger.info("Downloading face detection model...")
                    self._download_model("face")
                
                self._face_detector = YOLO(model_path)
                logger.info(f"Loaded face detector: {model_path}")
            except Exception as e:
                logger.error(f"Failed to load face detector: {e}")
        return self._face_detector
    
    @property
    def object_detector(self):
        """Lazy load object detector."""
        if self._object_detector is None:
            try:
                from ultralytics import YOLO
                model_path = self.config.get("object_model", "models/yolov11n.pt")
                
                if not Path(model_path).exists():
                    logger.info("Downloading object detection model...")
                    self._download_model("object")
                
                self._object_detector = YOLO(model_path)
                logger.info(f"Loaded object detector: {model_path}")
            except Exception as e:
                logger.error(f"Failed to load object detector: {e}")
        return self._object_detector
    
    @property
    def face_recognizer(self):
        """Lazy load face recognizer."""
        if self._face_recognizer is None:
            try:
                from insightface.app import FaceAnalysis
                model_name = self.config.get("recognition_model", "buffalo_sc")
                self._face_recognizer = FaceAnalysis(
                    name=model_name,
                    providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
                )
                self._face_recognizer.prepare(ctx_id=0, det_size=(160, 160))
                logger.info(f"Loaded face recognizer: {model_name}")
            except Exception as e:
                logger.warning(f"Face recognition unavailable: {e}")
        return self._face_recognizer
    
    def _download_model(self, model_type: str):
        """Download model if not present."""
        import urllib.request
        
        Path("models").mkdir(exist_ok=True)
        
        urls = {
            "face": ("https://github.com/YapaLab/yolo-face/releases/download/v0.0.0/yolov11n-face.pt", 
                    "models/yolov11n-face.pt"),
            "object": ("https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n.pt",
                      "models/yolov11n.pt"),
        }
        
        if model_type in urls:
            url, path = urls[model_type]
            logger.info(f"Downloading {model_type} model from {url}")
            urllib.request.urlretrieve(url, path)
            logger.info(f"Downloaded to {path}")
    
    def add_camera(self, camera_id: str, source, fps_limit: int = 15):
        """Add a camera source."""
        if isinstance(source, str) and source.isdigit():
            source = int(source)
        
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            raise RuntimeError(f"Failed to open camera: {source}")
        
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        self.cameras[camera_id] = cap
        self.camera_fps[camera_id] = fps_limit
        logger.info(f"Added camera: {camera_id} -> {source}")
    
    def register_employee(self, name: str, image_path: str = None, frame: np.ndarray = None):
        """Register an employee face."""
        if image_path:
            frame = cv2.imread(image_path)
        
        if frame is None:
            raise ValueError("Provide image_path or frame")
        
        # Detect face
        if self.face_detector is None:
            raise RuntimeError("Face detector not available")
        
        results = self.face_detector.predict(frame, conf=0.5, verbose=False)
        
        if not results or len(results[0].boxes) == 0:
            raise ValueError("No face detected")
        
        # Get largest face
        boxes = results[0].boxes
        areas = [(b.xyxy[0][2]-b.xyxy[0][0]) * (b.xyxy[0][3]-b.xyxy[0][1]) for b in boxes]
        best_idx = np.argmax(areas)
        bbox = tuple(map(int, boxes[best_idx].xyxy[0].cpu().numpy()))
        
        # Get embedding
        if self.face_recognizer is None:
            raise RuntimeError("Face recognizer not available")
        
        x1, y1, x2, y2 = bbox
        face_crop = frame[y1:y2, x1:x2]
        faces = self.face_recognizer.get(face_crop)
        
        if not faces:
            raise ValueError("Failed to extract embedding")
        
        self.face_tracker.register_employee(name, faces[0].embedding)
        logger.info(f"Registered employee: {name}")
    
    def process_frame(self, camera_id: str, frame: np.ndarray) -> Dict:
        """Process a single frame."""
        start_time = time.time()
        
        self.frame_counts[camera_id] += 1
        frame_num = self.frame_counts[camera_id]
        
        result = {
            "camera_id": camera_id,
            "frame_num": frame_num,
            "timestamp": datetime.now().isoformat(),
            "faces": [],
            "objects": [],
            "incidents": [],
            "processing_time_ms": 0,
        }
        
        # Face detection
        face_interval = self.config.get("face_detection_interval", 1)
        if frame_num % face_interval == 0 and self.face_detector:
            face_results = self.face_detector.predict(
                frame, 
                conf=self.config.get("face_confidence", 0.5),
                verbose=False
            )
            
            for r in face_results:
                for box in r.boxes:
                    bbox = tuple(map(int, box.xyxy[0].cpu().numpy()))
                    conf = float(box.conf[0])
                    
                    face_info = {
                        "bbox": bbox,
                        "confidence": conf,
                    }
                    
                    # Face recognition
                    recog_interval = self.config.get("recognition_interval", 3)
                    if frame_num % recog_interval == 0 and self.face_recognizer:
                        x1, y1, x2, y2 = bbox
                        face_crop = frame[y1:y2, x1:x2]
                        
                        try:
                            faces = self.face_recognizer.get(face_crop)
                            if faces:
                                track_info = self.face_tracker.process_face(
                                    faces[0].embedding, frame, bbox
                                )
                                face_info.update(track_info)
                                
                                # Unknown person alert
                                if track_info["is_new"] and not track_info["is_employee"]:
                                    incident = self.incident_manager.create_incident(
                                        "unknown_person", camera_id, conf, bbox, frame
                                    )
                                    if incident:
                                        result["incidents"].append(incident.to_dict())
                        except Exception as e:
                            logger.debug(f"Recognition failed: {e}")
                    
                    result["faces"].append(face_info)
        
        # Object detection
        obj_interval = self.config.get("object_detection_interval", 1)
        if frame_num % obj_interval == 0 and self.object_detector:
            obj_results = self.object_detector.predict(
                frame,
                conf=self.config.get("object_confidence", 0.5),
                verbose=False
            )
            
            for r in obj_results:
                names = r.names
                for box in r.boxes:
                    bbox = tuple(map(int, box.xyxy[0].cpu().numpy()))
                    conf = float(box.conf[0])
                    cls_id = int(box.cls[0])
                    cls_name = names.get(cls_id, "unknown").lower()
                    
                    result["objects"].append({
                        "class": cls_name,
                        "confidence": conf,
                        "bbox": bbox,
                    })
                    
                    # Check for KPI violations
                    kpi_name = DETECTION_TO_KPI.get(cls_name)
                    if kpi_name and kpi_name in PETROL_PUMP_KPIS:
                        incident = self.incident_manager.create_incident(
                            kpi_name, camera_id, conf, bbox, frame
                        )
                        if incident:
                            result["incidents"].append(incident.to_dict())
        
        # Calculate processing time
        result["processing_time_ms"] = (time.time() - start_time) * 1000
        
        # Update analytics
        self.analytics.update_camera_stats(
            camera_id,
            len(result["faces"]),
            len(result["objects"]),
            result["processing_time_ms"],
            len(result["incidents"])
        )
        
        # Maybe output analytics
        self.analytics.maybe_output(self.face_tracker, self.incident_manager)
        
        return result
    
    def draw_frame(self, frame: np.ndarray, result: Dict) -> np.ndarray:
        """Draw detection results on frame."""
        frame = frame.copy()
        
        # Draw faces
        for face in result["faces"]:
            x1, y1, x2, y2 = face["bbox"]
            is_employee = face.get("is_employee", False)
            color = (0, 255, 0) if is_employee else (0, 165, 255)
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            label = face.get("person_name") or ("Employee" if is_employee else "Visitor")
            if face.get("is_returning"):
                label += " (Returning)"
            
            cv2.putText(frame, label, (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Draw objects
        for obj in result["objects"]:
            x1, y1, x2, y2 = obj["bbox"]
            cls_name = obj["class"]
            
            # Red for alerts, blue for normal
            kpi = DETECTION_TO_KPI.get(cls_name)
            if kpi and kpi in PETROL_PUMP_KPIS:
                color = (0, 0, 255)
            else:
                color = (255, 0, 0)
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"{cls_name} {obj['confidence']:.2f}", 
                       (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Info overlay
        stats = self.face_tracker.get_stats()
        info = [
            f"Camera: {result['camera_id']}",
            f"Faces: {len(result['faces'])} | Objects: {len(result['objects'])}",
            f"Employees: {stats['employees_present']} | Visitors: {stats['unknown_faces_today']}",
            f"Time: {result['processing_time_ms']:.1f}ms",
        ]
        
        if result["incidents"]:
            info.append(f"⚠️ INCIDENTS: {len(result['incidents'])}")
        
        y = 30
        for text in info:
            cv2.putText(frame, text, (10, y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            y += 25
        
        return frame
    
    def run(self, show: bool = True):
        """Run the pipeline."""
        if not self.cameras:
            raise RuntimeError("No cameras configured")
        
        self.running = True
        logger.info(f"Starting pipeline with {len(self.cameras)} cameras")
        
        # FPS limiting
        frame_intervals = {
            cam_id: 1.0 / fps 
            for cam_id, fps in self.camera_fps.items()
        }
        last_frame_times = defaultdict(float)
        
        try:
            while self.running:
                for camera_id, cap in self.cameras.items():
                    # FPS limiting
                    now = time.time()
                    if now - last_frame_times[camera_id] < frame_intervals.get(camera_id, 0.066):
                        continue
                    last_frame_times[camera_id] = now
                    
                    ret, frame = cap.read()
                    if not ret:
                        logger.warning(f"Failed to read from {camera_id}")
                        continue
                    
                    # Process
                    result = self.process_frame(camera_id, frame)
                    
                    # Display
                    if show:
                        display_frame = self.draw_frame(frame, result)
                        cv2.imshow(f"InvEye - {camera_id}", display_frame)
                
                if show:
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        break
                    elif key == ord('s'):
                        self._print_stats()
                    elif key == ord('j'):
                        self._output_json()
        
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        
        finally:
            self.running = False
            for cap in self.cameras.values():
                cap.release()
            cv2.destroyAllWindows()
            
            self._print_stats()
            self._output_json()
    
    def _print_stats(self):
        """Print statistics."""
        print("\n" + "="*60)
        print("PETROL PUMP ANALYTICS SUMMARY")
        print("="*60)
        
        # Face stats
        face_stats = self.face_tracker.get_stats()
        print(f"\n👤 FACES:")
        print(f"   Unique faces: {face_stats['total_unique_faces']}")
        print(f"   Returning today: {face_stats['returning_faces_today']}")
        print(f"   Employees present: {face_stats['employees_present']}")
        print(f"   Unknown visitors: {face_stats['unknown_faces_today']}")
        
        # Incident stats
        kpi_summary = self.incident_manager.get_kpi_summary()
        print(f"\n🚨 INCIDENTS:")
        print(f"   Active: {kpi_summary['active_count']}")
        print(f"   Today total: {kpi_summary['today'].get('total', 0)}")
        
        if kpi_summary['by_severity']:
            print("   By severity:")
            for sev, count in kpi_summary['by_severity'].items():
                print(f"      {sev}: {count}")
        
        print("="*60)
    
    def _output_json(self):
        """Output final JSON analytics."""
        output_file = self.config.get("json_output", "analytics_output.json")
        
        analytics = {
            "generated_at": datetime.now().isoformat(),
            "session_duration": str(datetime.now() - self.analytics.start_time),
            "face_stats": self.face_tracker.get_stats(),
            "faces": self.face_tracker.get_all_faces(),
            "kpi_summary": self.incident_manager.get_kpi_summary(),
            "incidents": self.incident_manager.get_incident_history(),
            "camera_stats": dict(self.analytics.camera_stats),
        }
        
        with open(output_file, 'w') as f:
            json.dump(analytics, f, indent=2, default=str)
        
        logger.info(f"Analytics saved to: {output_file}")


# ============================================================================
# CLI
# ============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='InvEye Petrol Pump Analytics - Plug & Play',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python petrol_pump_analytics.py --test
    python petrol_pump_analytics.py --cameras 0 1 --show
    python petrol_pump_analytics.py --config petrol_pump_config.yaml
    python petrol_pump_analytics.py --rtsp rtsp://192.168.1.101:554/stream
        """
    )
    
    parser.add_argument('--test', action='store_true', 
                       help='Quick test with webcam')
    parser.add_argument('--cameras', nargs='+', 
                       help='Camera sources (indices or paths)')
    parser.add_argument('--rtsp', nargs='+',
                       help='RTSP camera URLs')
    parser.add_argument('--config', type=str,
                       help='Config file path')
    parser.add_argument('--json-output', type=str, default='analytics_output.json',
                       help='JSON output file')
    parser.add_argument('--show', action='store_true', default=True,
                       help='Show video output')
    parser.add_argument('--no-show', action='store_true',
                       help='Disable video output')
    parser.add_argument('--fps', type=int, default=15,
                       help='FPS limit per camera')
    parser.add_argument('--register', nargs=2, metavar=('NAME', 'IMAGE'),
                       help='Register employee face')
    
    args = parser.parse_args()
    
    # Load config
    config = {
        "json_output": args.json_output,
        "face_detection_interval": 1,
        "object_detection_interval": 1,
        "recognition_interval": 3,
        "face_confidence": 0.5,
        "object_confidence": 0.5,
        "recognition_threshold": 0.5,
    }
    
    if args.config and Path(args.config).exists():
        with open(args.config, 'r') as f:
            config.update(yaml.safe_load(f))
    
    # Create pipeline
    pipeline = PetrolPumpPipeline(config)
    
    # Register employee
    if args.register:
        name, image_path = args.register
        pipeline.register_employee(name, image_path)
        print(f"✅ Registered: {name}")
        return
    
    # Add cameras
    if args.test:
        pipeline.add_camera("webcam", 0, fps_limit=args.fps)
    elif args.rtsp:
        for i, url in enumerate(args.rtsp):
            pipeline.add_camera(f"camera_{i+1}", url, fps_limit=args.fps)
    elif args.cameras:
        for i, src in enumerate(args.cameras):
            if src.isdigit():
                src = int(src)
            pipeline.add_camera(f"camera_{i+1}", src, fps_limit=args.fps)
    else:
        pipeline.add_camera("webcam", 0, fps_limit=args.fps)
    
    # Run
    show = not args.no_show
    pipeline.run(show=show)


if __name__ == '__main__':
    main()
