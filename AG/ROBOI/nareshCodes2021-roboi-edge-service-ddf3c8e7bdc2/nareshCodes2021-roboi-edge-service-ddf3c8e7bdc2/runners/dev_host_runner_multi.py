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
# --- CONFIGURATION ---
model_conf = config.get('models', {})
MODEL_GEN_PATH = model_conf.get('primary', "models/exports/yolo11n.pt")
MODEL_FIRE_PATH = model_conf.get('fire', "models/exports/yolo11n_fire.pt")
MODEL_FIGHT_PATH = model_conf.get('fight', "models/exports/yolo8n_fight.pt")

RTSP_URIS = [cam['uri'] for cam in camera_config.values()]
CAMERA_MAP = {int(k): cam['name'] for k, cam in camera_config.items()}

def main():
    try:
        logger.info("Initializing Multi-Model Pipeline...")
        logger.info(f"Loading Primary Model: {MODEL_GEN_PATH}")
        model_gen = YOLO(MODEL_GEN_PATH)
        
        logger.info(f"Loading Fire Model: {MODEL_FIRE_PATH}")
        model_fire = YOLO(MODEL_FIRE_PATH)
        
        logger.info(f"Loading Fight Model: {MODEL_FIGHT_PATH}")
        model_fight = YOLO(MODEL_FIGHT_PATH)
        
        # Initialize Face Recognizer & Analytics Engine
        det_threshold = config.get('analytics', {}).get('face_detection_threshold', 0.6)
        face_engine = RoboFaceID(score_threshold=det_threshold)
        engine = AnalyticsEngine(face_recognizer=face_engine)
        
        # Initialize Recorders & Caps
        caps = []
        recorders = {}
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

                    # --- MULTI-MODEL INFERENCE PIPELINE ---
                    frame_objects = []
                    person_present = False
                    
                    # 1. Primary Model (General Objects) - Run every 4 frames
                    if frame_count % 4 == 0:
                        results_gen = model_gen(frame, verbose=False)[0]
                        for box in results_gen.boxes:
                            label = results_gen.names[int(box.cls[0])]
                            
                            # Check for Person Presence (for conditional fight logic)
                            if label.lower() == "person":
                                person_present = True
                                
                            frame_objects.append({
                                "label": label,
                                "class_id": int(box.cls[0]),
                                "confidence": float(box.conf[0]),
                                "bbox": {
                                    "top": int(box.xyxy[0][1]),
                                    "left": int(box.xyxy[0][0]),
                                    "width": int(box.xyxy[0][2] - box.xyxy[0][0]),
                                    "height": int(box.xyxy[0][3] - box.xyxy[0][1])
                                }
                            })
                    
                    # 2. Fire Model (Specialized) - Run every 30 frames
                    if frame_count % 30 == 0:
                        results_fire = model_fire(frame, verbose=False, conf=0.4)[0]
                        for box in results_fire.boxes:
                            frame_objects.append({
                                "label": results_fire.names[int(box.cls[0])], # e.g. 'fire', 'smoke'
                                "class_id": int(box.cls[0]),
                                "confidence": float(box.conf[0]),
                                "bbox": {
                                    "top": int(box.xyxy[0][1]),
                                    "left": int(box.xyxy[0][0]),
                                    "width": int(box.xyxy[0][2] - box.xyxy[0][0]),
                                    "height": int(box.xyxy[0][3] - box.xyxy[0][1])
                                }
                            })

                    # 3. Fight Model (Smart Trigger) - Run every 15 frames
                    # Only runs if 'person' was detected in the PRIMARY model THIS frame
                    # (Note: Since primary runs every 4, and fight every 15, we align them: % 15 != % 4 usually
                    # But the user logic "fight never occurs if no person present" implies we need to know.
                    # Simple Fix: If Primary didn't run this frame, we shouldn't trust old data blindly, 
                    # BUT for smooth demo, let's assume if it's a "Fight Frame" (15), we force Primary to run?
                    # No, let's stick to independent schedules but use the flag from the last Primary run?
                    # Better: The user asked for specific intervals. 
                    # If %15 == 0, we run Fight. But we check `person_present` from THIS frame if %4 happened,
                    # or from the *last* known state? 
                    # Safest: Only run Fight if Primary ALSO ran and found a person.
                    # LCM of 4 and 15 is 60. They overlap rarely.
                    # LET'S ADJUST: Run Primary every 5 frames, Fight every 15. Then they overlap perfectly.
                    # Or just run Fight if % 15 == 0. If % 4 != 0, we might miss the person update.
                    # REVISED STRATEGY: 
                    # If (frame % 4 == 0) -> Run Primary. Update person_present.
                    # If (frame % 15 == 0) AND (person_present == True) -> Run Fight.
                    # This assumes 'person_present' holds state until the next Primary run.
                    
                    if frame_count % 15 == 0 and person_present:
                        # High threshold for violence to avoid false alarms
                        results_fight = model_fight(frame, verbose=False, conf=0.65)[0]
                        for box in results_fight.boxes:
                            label = results_fight.names[int(box.cls[0])]
                            # Some fight models output 'violence' and 'non-violence'
                            # We only care about positive violence detection
                            if "violence" in label.lower() and "non" not in label.lower():
                                frame_objects.append({
                                    "label": "violence", # Normalize logic label
                                    "class_id": int(box.cls[0]),
                                    "confidence": float(box.conf[0]),
                                    "bbox": {
                                        "top": int(box.xyxy[0][1]),
                                        "left": int(box.xyxy[0][0]),
                                        "width": int(box.xyxy[0][2] - box.xyxy[0][0]),
                                        "height": int(box.xyxy[0][3] - box.xyxy[0][1])
                                    }
                                })
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