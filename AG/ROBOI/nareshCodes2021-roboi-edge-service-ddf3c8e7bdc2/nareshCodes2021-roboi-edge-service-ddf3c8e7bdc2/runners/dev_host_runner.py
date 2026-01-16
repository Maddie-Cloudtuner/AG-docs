import sys
import os
import cv2
import time
import yaml
import traceback
from ultralytics import YOLO

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.analytics_engine import AnalyticsEngine, CONFIG_PATH
from tools.capture_video import VideoRecorder
from core.visual_utils import draw_annotations
from core.face_recognizer import RoboFaceID
from core.logger import get_app_logger

# Initialize Logger
logger = get_app_logger("dev-runner")

import onnxruntime as ort
print(f"ONNX Available Providers: {ort.get_available_providers()}")

def load_runner_config():
    try:
        with open(CONFIG_PATH, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Critical: Failed to load config for runner: {e}")
        logger.error(traceback.format_exc())
        return {}

config = load_runner_config()
camera_config = config.get('cameras', {})

# --- CONFIGURATION ---
MODEL_PATH = "models/exports/yolo11_finetuned.pt" 
MODEL_CONF = 0.15 # Lowered from default 0.25 to catch small fires
RTSP_URIS = [cam['uri'] for cam in camera_config.values()]
CAMERA_MAP = {int(k): cam['name'] for k, cam in camera_config.items()}

def main():
    caps = []
    recorders = {}
    try:
        logger.info("Initializing YOLO model...")
        model = YOLO(MODEL_PATH)
        
        # Initialize Face Recognizer & Analytics Engine
        det_threshold = config.get('analytics', {}).get('face_detection_threshold', 0.6)
        face_engine = RoboFaceID(score_threshold=det_threshold)
        engine = AnalyticsEngine(face_recognizer=face_engine)
        
        # Initialize Recorders & Caps
        for i, uri in enumerate(RTSP_URIS):
            try:
                cap = cv2.VideoCapture(uri)
                if not cap.isOpened():
                    logger.error(f"Connection Failed: Could not open RTSP stream for {CAMERA_MAP.get(i, i)}")
                    continue
                
                cam_name = CAMERA_MAP.get(i, f"UNKNOWN_CAM_{i}")
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = int(cap.get(cv2.CAP_PROP_FPS)) or 15
                
                logger.info(f"Initialized recorder for {cam_name} ({width}x{height} @ {fps}fps)")
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1) # Internal buffer size 1
                recorders[cam_name] = VideoRecorder(cam_name, resolution=(width, height), fps=fps, buffer_seconds=10, draw_on_video=True)
                caps.append((i, cam_name, cap))
            except Exception as e:
                logger.error(f"Setup Error for stream {i}: {e}")
                logger.error(traceback.format_exc())

        if not caps:
            logger.error("Critical: No active camera streams found. Exiting.")
            return

        logger.info("Starting Dev Host Loop...")
        fps_limit = 15
        target_frame_time = 1.0 / fps_limit
        frame_count = 0
        
        while True:
            loop_start = time.time()
            frame_count += 1
            
            for cam_id, cam_name, cap in caps:
                try:
                    # 1. Flush the buffer
                    for _ in range(5):
                        if not cap.grab():
                            break
                    
                    # 2. Retrieve the latest grabbed frame
                    ret, frame = cap.retrieve()
                    if not ret:
                        ret, frame = cap.read()
                        if not ret:
                            logger.warning(f"Frame Loss: Failed to grab frame from {cam_name}")
                            continue

                    # Inference
                    results = model(frame, verbose=False, conf=MODEL_CONF)[0]
                    
                    # Diagnostic: Print all raw detections for debugging
                    for box in results.boxes:
                        lbl = results.names[int(box.cls[0])]
                        conf = float(box.conf[0])
                        if lbl in ["fire", "smoke"]:
                            logger.info(f"DIAGNOSTIC Detection: {lbl} @ {conf:.2f} confidence from {cam_name}")
                    
                    
                    # Adapt to Standard Format
                    frame_objects = []
                    for box in results.boxes:
                        obj = {
                            "label": results.names[int(box.cls[0])],
                            "class_id": int(box.cls[0]),
                            "confidence": float(box.conf[0]),
                            "bbox": {
                                "top": int(box.xyxy[0][1]),
                                "left": int(box.xyxy[0][0]),
                                "width": int(box.xyxy[0][2] - box.xyxy[0][0]),
                                "height": int(box.xyxy[0][3] - box.xyxy[0][1])
                            }
                        }
                        frame_objects.append(obj)

                    # 1. Enrich Metadata (Face Recognition happens here - INLINE)
                    if face_engine:
                        for obj in frame_objects:
                            label = obj.get("label", "").lower()
                            if label in ["person", "face"]:
                                bbox = obj.get("bbox", {})
                                x = bbox.get("left", 0)
                                y = bbox.get("top", 0)
                                w = bbox.get("width", 0)
                                h = bbox.get("height", 0)
                                
                                bbox_coords = [x, y, x+w, y+h]
                                
                                try:
                                    # Use frame_count as ID
                                    name, face_conf, face_id = face_engine.recognize(
                                        frame, bbox_coords, frame_count, 
                                        recognition_threshold=engine.recognition_threshold,
                                        detection_threshold=det_threshold
                                    )
                                    
                                    obj["recognition"] = {
                                        "identity": name,
                                        "confidence": face_conf,
                                        "identity_id": face_id
                                    }
                                    obj["display_label"] = f"{name} ({int(face_conf*100)}%)" if name != "Stranger" else "Stranger"
                                except Exception as e:
                                    logger.warning(f"Metadata enrichment failed: {e}")

                    # 2. Add to Recorder Buffer (now has recognition labels)
                    recorders[cam_name].add_frame(frame, frame_objects=frame_objects)

                    # 3. Process Logic (Handles alerts/logging, avoids redundant enrichment)
                    engine.process_frame(cam_name, frame_objects, frame=frame, recorder=recorders[cam_name], frame_id=frame_count)

                    # Display Annotated Frame (visual_utils uses engine-enriched metadata)
                    display_frame = draw_annotations(frame.copy(), frame_objects)
                    cv2.imshow(f"Dev Host - {cam_name}", cv2.resize(display_frame, (720, 480)))
                except Exception as e:
                    logger.error(f"Runtime Error in loop for {cam_name}: {e}")

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
            # Control FPS
            elapsed = time.time() - loop_start
            sleep_time = target_frame_time - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)
                
    except KeyboardInterrupt:
        logger.info("Service interrupted by user.")
    except Exception as e:
        logger.error(f"Critical System Failure: {e}")
        logger.error(traceback.format_exc())
    finally:
        for _, _, cap in caps:
            cap.release()
        cv2.destroyAllWindows()
        logger.info("Cleanup complete. Resource released.")

if __name__ == "__main__":
    main()