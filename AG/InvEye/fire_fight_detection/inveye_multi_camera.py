#!/usr/bin/env python3
"""
InvEye Multi-Camera Fire & Fight Detection
DeepStream + YOLO11 Pipeline for Jetson Orin Nano

Supports 4 simultaneous camera streams with:
- Object detection (person, vehicle, etc.)
- Fire & smoke detection
- Fight/violence detection

Setup:
1. Clone DeepStream-YOLO: git clone https://github.com/marcoslucianops/DeepStream-Yolo
2. Copy export_yolo11.py to ultralytics folder
3. Download YOLO11s model and fine-tune with fire/fight data
4. Export to TensorRT engine
5. Run this script on Jetson

Usage:
    python3 inveye_multi_camera.py --config cameras.yaml
"""

import sys
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GLib, GstRtspServer

import pyds
import json
import time
import threading
import argparse
import yaml
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import requests

# Initialize GStreamer
Gst.init(None)


# ============================================================
# CONFIGURATION
# ============================================================

# Detection classes - InvEye Employee + Petrol Pump focused
CLASS_NAMES = {
    # Core Detection
    0: "person",
    1: "face",
    2: "helmet",
    3: "safety_vest",
    4: "uniform",
    
    # Vehicles
    5: "car",
    6: "motorcycle",
    7: "auto_rickshaw",
    8: "bus",
    9: "truck",
    10: "bicycle",
    
    # PPE & Safety
    11: "hard_hat",
    12: "gloves",
    13: "mask",
    14: "safety_goggles",
    15: "high_vis_jacket",
    16: "safety_shoes",
    
    # Objects
    17: "mobile_phone",
    18: "laptop",
    19: "bag",
    20: "fire_extinguisher",
    21: "fuel_nozzle",
    22: "cash_register",
    
    # Zones & Equipment
    23: "fuel_dispenser",
    24: "vehicle_queue",
    25: "pump_island",
    26: "office_desk",
    27: "entry_gate",
    
    # 🚨 Alert Classes
    28: "fire",
    29: "smoke",
    30: "fighting",
    31: "crowd",
    
    # Compliance Violations
    32: "no_helmet",
    33: "no_vest",
    34: "smoking",
    35: "loitering",
}

# Alert classes - these trigger immediate notifications
ALERT_CLASSES = {"fire", "smoke", "fighting", "crowd", "no_helmet", "no_vest", "smoking"}

# Colors for visualization (R, G, B)
CLASS_COLORS = {
    # People
    "person": (0, 255, 0),          # Green
    "face": (0, 200, 0),            # Dark Green
    
    # Vehicles
    "car": (255, 255, 0),           # Yellow
    "motorcycle": (255, 200, 0),    # Gold
    "truck": (255, 165, 0),         # Orange
    "bus": (255, 140, 0),           # Dark Orange
    "auto_rickshaw": (255, 180, 0), # Light Orange
    
    # Safety Equipment
    "helmet": (0, 255, 255),        # Cyan
    "safety_vest": (0, 200, 255),   # Light Blue
    "hard_hat": (0, 180, 255),      # Sky Blue
    
    # 🚨 Alerts (Red spectrum)
    "fire": (255, 0, 0),            # Red
    "smoke": (128, 128, 128),       # Gray
    "fighting": (255, 0, 255),      # Magenta
    "crowd": (255, 100, 100),       # Light Red
    
    # Violations (Pink/Red)
    "no_helmet": (255, 50, 50),     # Bright Red
    "no_vest": (255, 80, 80),       # Red
    "smoking": (200, 0, 0),         # Dark Red
    "loitering": (180, 0, 180),     # Purple
}


# ============================================================
# DEEPSTREAM PIPELINE
# ============================================================

class InvEyeDeepStreamPipeline:
    """
    Multi-camera DeepStream pipeline for Jetson Orin Nano
    Processes 4 cameras simultaneously with YOLO11
    """
    
    def __init__(self, config_path: str):
        self.config = self.load_config(config_path)
        self.pipeline = None
        self.loop = None
        
        # Detection tracking
        self.detection_buffer = defaultdict(list)
        self.alert_callback = None
        self.frame_count = 0
        
        # Cloud upload queue
        self.upload_queue = []
        self.last_upload_time = time.time()
        
        print(f"[InvEye] Initializing with {len(self.config['cameras'])} cameras")
    
    def load_config(self, config_path: str) -> dict:
        """Load camera configuration from YAML"""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def create_pipeline(self):
        """Create GStreamer DeepStream pipeline"""
        
        pipeline_str = self._build_pipeline_string()
        print(f"[InvEye] Creating pipeline...")
        
        self.pipeline = Gst.parse_launch(pipeline_str)
        
        if not self.pipeline:
            raise RuntimeError("Failed to create pipeline")
        
        # Add probe to get detection results
        tiler = self.pipeline.get_by_name("tiler")
        if tiler:
            tiler_src_pad = tiler.get_static_pad("src")
            tiler_src_pad.add_probe(
                Gst.PadProbeType.BUFFER,
                self._detection_probe_callback,
                0
            )
        
        # Bus for messages
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self._bus_message_callback)
        
        print("[InvEye] Pipeline created successfully")
        return self.pipeline
    
    def _build_pipeline_string(self) -> str:
        """Build GStreamer pipeline string for multi-camera"""
        
        num_cameras = len(self.config['cameras'])
        model_config = self.config.get('model', {})
        
        # Source elements for each camera
        sources = []
        for i, cam in enumerate(self.config['cameras']):
            rtsp_url = cam['rtsp_url']
            source = f"""
                rtspsrc location="{rtsp_url}" latency=100 ! 
                rtph264depay ! h264parse ! nvv4l2decoder ! 
                m.sink_{i}
            """
            sources.append(source.strip())
        
        # Complete pipeline
        pipeline = f"""
            nvstreammux name=m batch-size={num_cameras} 
                width={model_config.get('width', 640)} 
                height={model_config.get('height', 640)} 
                batched-push-timeout=40000 
                live-source=1
            
            {' '.join(sources)}
            
            m. ! queue ! 
            nvinfer config-file-path="{self.config.get('nvinfer_config', 'config_infer.txt')}" ! 
            nvtracker ll-lib-file=/opt/nvidia/deepstream/deepstream/lib/libnvds_nvmultiobjecttracker.so !
            
            nvmultistreamtiler name=tiler 
                rows={int((num_cameras + 1) / 2)} 
                columns=2 
                width=1920 height=1080 !
            
            nvvideoconvert ! 
            nvdsosd ! 
            nvvideoconvert !
            
            nveglglessink sync=0
        """
        
        return pipeline.replace('\n', ' ').strip()
    
    def _detection_probe_callback(self, pad, info, user_data):
        """Process detection results from each frame"""
        
        gst_buffer = info.get_buffer()
        if not gst_buffer:
            return Gst.PadProbeReturn.OK
        
        batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))
        if not batch_meta:
            return Gst.PadProbeReturn.OK
        
        l_frame = batch_meta.frame_meta_list
        
        while l_frame:
            try:
                frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
            except StopIteration:
                break
            
            source_id = frame_meta.source_id
            frame_number = frame_meta.frame_num
            
            detections = []
            alerts = []
            
            l_obj = frame_meta.obj_meta_list
            while l_obj:
                try:
                    obj_meta = pyds.NvDsObjectMeta.cast(l_obj.data)
                except StopIteration:
                    break
                
                # Get detection info
                class_id = obj_meta.class_id
                class_name = CLASS_NAMES.get(class_id, f"class_{class_id}")
                confidence = obj_meta.confidence
                
                # Bounding box
                rect = obj_meta.rect_params
                bbox = {
                    "x": rect.left,
                    "y": rect.top,
                    "width": rect.width,
                    "height": rect.height
                }
                
                detection = {
                    "class_id": class_id,
                    "class_name": class_name,
                    "confidence": confidence,
                    "bbox": bbox,
                    "tracker_id": obj_meta.object_id
                }
                detections.append(detection)
                
                # Check for alert conditions
                if class_name in ALERT_CLASSES:
                    alert = {
                        "type": class_name.upper(),
                        "confidence": confidence,
                        "source_id": source_id,
                        "timestamp": datetime.now().isoformat(),
                        "bbox": bbox
                    }
                    alerts.append(alert)
                    print(f"🚨 ALERT [{class_name.upper()}] Camera {source_id} - Confidence: {confidence:.2f}")
                
                # Set display text
                display_text = f"{class_name}: {confidence:.2f}"
                obj_meta.text_params.display_text = display_text
                
                # Set box color
                if class_name in CLASS_COLORS:
                    r, g, b = CLASS_COLORS[class_name]
                    obj_meta.rect_params.border_color.set(r/255, g/255, b/255, 1.0)
                    if class_name in ALERT_CLASSES:
                        obj_meta.rect_params.border_width = 4
                
                try:
                    l_obj = l_obj.next
                except StopIteration:
                    break
            
            # Store frame data
            frame_data = {
                "source_id": source_id,
                "frame_number": frame_number,
                "timestamp": datetime.now().isoformat(),
                "detections": detections,
                "alerts": alerts
            }
            
            self.detection_buffer[source_id].append(frame_data)
            
            # Trigger alert callback
            if alerts and self.alert_callback:
                self.alert_callback(alerts)
            
            # Upload to cloud periodically
            self.frame_count += 1
            if self.frame_count % self.config.get('upload_interval', 90) == 0:
                self._upload_to_cloud()
            
            try:
                l_frame = l_frame.next
            except StopIteration:
                break
        
        return Gst.PadProbeReturn.OK
    
    def _bus_message_callback(self, bus, message):
        """Handle GStreamer bus messages"""
        
        t = message.type
        
        if t == Gst.MessageType.EOS:
            print("[InvEye] End of stream")
            self.stop()
        
        elif t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print(f"[InvEye] Error: {err}, Debug: {debug}")
            self.stop()
        
        elif t == Gst.MessageType.WARNING:
            err, debug = message.parse_warning()
            print(f"[InvEye] Warning: {err}")
        
        elif t == Gst.MessageType.STATE_CHANGED:
            if message.src == self.pipeline:
                old, new, pending = message.parse_state_changed()
                print(f"[InvEye] Pipeline state: {old.value_nick} -> {new.value_nick}")
        
        return True
    
    def _upload_to_cloud(self):
        """Upload detection metadata to cloud (NOT video)"""
        
        api_url = self.config.get('cloud_api', {}).get('url')
        api_key = self.config.get('cloud_api', {}).get('key')
        
        if not api_url:
            return
        
        # Aggregate data from all sources
        payload = {
            "device_id": self.config.get('device_id', 'jetson-001'),
            "timestamp": datetime.now().isoformat(),
            "cameras": {}
        }
        
        for source_id, frames in self.detection_buffer.items():
            if frames:
                # Summarize last batch
                camera_name = self.config['cameras'][source_id].get('name', f'camera_{source_id}')
                
                all_detections = []
                all_alerts = []
                for frame in frames[-30:]:  # Last 30 frames
                    all_detections.extend(frame['detections'])
                    all_alerts.extend(frame['alerts'])
                
                # Count by class
                class_counts = defaultdict(int)
                for det in all_detections:
                    class_counts[det['class_name']] += 1
                
                payload['cameras'][camera_name] = {
                    "source_id": source_id,
                    "frame_count": len(frames),
                    "detection_counts": dict(class_counts),
                    "alerts": all_alerts,
                    "avg_detections_per_frame": len(all_detections) / max(len(frames[-30:]), 1)
                }
        
        # Clear buffer
        self.detection_buffer.clear()
        
        # Send to cloud
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                api_url,
                json=payload,
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                data_size = len(json.dumps(payload))
                print(f"[InvEye] Uploaded {data_size} bytes to cloud")
            else:
                print(f"[InvEye] Cloud upload failed: {response.status_code}")
        
        except Exception as e:
            print(f"[InvEye] Cloud upload error: {e}")
    
    def set_alert_callback(self, callback):
        """Set callback function for alerts"""
        self.alert_callback = callback
    
    def start(self):
        """Start the pipeline"""
        
        if not self.pipeline:
            self.create_pipeline()
        
        print("[InvEye] Starting pipeline...")
        self.pipeline.set_state(Gst.State.PLAYING)
        
        self.loop = GLib.MainLoop()
        
        try:
            print("[InvEye] Pipeline running. Press Ctrl+C to stop.")
            self.loop.run()
        except KeyboardInterrupt:
            print("\n[InvEye] Stopping...")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the pipeline"""
        
        if self.pipeline:
            self.pipeline.set_state(Gst.State.NULL)
        
        if self.loop and self.loop.is_running():
            self.loop.quit()
        
        # Final upload
        self._upload_to_cloud()
        print("[InvEye] Pipeline stopped")


# ============================================================
# ALERT HANDLER
# ============================================================

class AlertHandler:
    """Handle and route alerts from detections"""
    
    def __init__(self, config: dict):
        self.config = config
        self.alert_history = []
        self.cooldown = config.get('alert_cooldown', 30)  # seconds
        self.last_alert_time = {}
    
    def handle_alert(self, alerts: list):
        """Process incoming alerts"""
        
        for alert in alerts:
            alert_key = f"{alert['type']}_{alert['source_id']}"
            
            # Check cooldown
            last_time = self.last_alert_time.get(alert_key, 0)
            if time.time() - last_time < self.cooldown:
                continue
            
            self.last_alert_time[alert_key] = time.time()
            self.alert_history.append(alert)
            
            # Send notifications
            self._send_notification(alert)
    
    def _send_notification(self, alert: dict):
        """Send alert notification"""
        
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║ 🚨 INVEYE ALERT                                               ║
╠══════════════════════════════════════════════════════════════╣
║ Type: {alert['type']:<54} ║
║ Camera: {alert['source_id']:<52} ║
║ Confidence: {alert['confidence']:.2%:<48} ║
║ Time: {alert['timestamp']:<54} ║
╚══════════════════════════════════════════════════════════════╝
        """)
        
        # Webhook notification
        webhook_url = self.config.get('webhook_url')
        if webhook_url:
            try:
                requests.post(
                    webhook_url,
                    json=alert,
                    timeout=3
                )
            except Exception as e:
                print(f"[Alert] Webhook failed: {e}")


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="InvEye Multi-Camera Detection for Jetson Orin Nano"
    )
    parser.add_argument(
        "--config", "-c",
        default="cameras.yaml",
        help="Path to camera configuration YAML"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output"
    )
    
    args = parser.parse_args()
    
    # Check config exists
    if not Path(args.config).exists():
        print(f"Error: Config file not found: {args.config}")
        print("Creating sample config...")
        create_sample_config(args.config)
        print(f"Edit {args.config} with your camera settings and run again.")
        return
    
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║   🔥 InvEye Fire & Fight Detection                          ║
    ║   DeepStream + YOLO11 Multi-Camera Pipeline                  ║
    ║                                                              ║
    ║   Jetson Orin Nano | 4 Camera Support                        ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Load config
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)
    
    # Create alert handler
    alert_handler = AlertHandler(config.get('alerts', {}))
    
    # Create and run pipeline
    pipeline = InvEyeDeepStreamPipeline(args.config)
    pipeline.set_alert_callback(alert_handler.handle_alert)
    pipeline.start()


def create_sample_config(path: str):
    """Create sample camera configuration"""
    
    sample_config = {
        "device_id": "inveye-orin-001",
        
        "cameras": [
            {
                "id": "cam_entrance",
                "name": "Entrance Camera",
                "rtsp_url": "rtsp://admin:password@192.168.1.101:554/stream1",
                "type": "indoor"
            },
            {
                "id": "cam_office1",
                "name": "Office Area 1",
                "rtsp_url": "rtsp://admin:password@192.168.1.102:554/stream1",
                "type": "indoor"
            },
            {
                "id": "cam_office2",
                "name": "Office Area 2",
                "rtsp_url": "rtsp://admin:password@192.168.1.103:554/stream1",
                "type": "indoor"
            },
            {
                "id": "cam_parking",
                "name": "Parking Area",
                "rtsp_url": "rtsp://admin:password@192.168.1.104:554/stream1",
                "type": "outdoor"
            }
        ],
        
        "model": {
            "engine_path": "yolo11s_fire_fight.engine",
            "width": 640,
            "height": 640,
            "batch_size": 4
        },
        
        "nvinfer_config": "config_infer_yolo11.txt",
        
        "tracking": {
            "enabled": True,
            "max_age": 30
        },
        
        "upload_interval": 90,  # frames
        
        "cloud_api": {
            "url": "https://api.cloudtuner.ai/v1/inveye/detections",
            "key": "your-api-key-here"
        },
        
        "alerts": {
            "alert_cooldown": 30,
            "webhook_url": "https://hooks.slack.com/your-webhook"
        }
    }
    
    with open(path, 'w') as f:
        yaml.dump(sample_config, f, default_flow_style=False, sort_keys=False)


if __name__ == "__main__":
    main()
