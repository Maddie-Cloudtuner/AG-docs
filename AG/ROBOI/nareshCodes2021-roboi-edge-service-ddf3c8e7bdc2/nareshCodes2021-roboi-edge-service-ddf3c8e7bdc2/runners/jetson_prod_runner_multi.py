#!/usr/bin/env python3
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import json
import datetime
import socket
import traceback
from pathlib import Path
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
import numpy as np
import cv2
from tools import capture_image
from tools.capture_video import VideoRecorder
from core.analytics_engine import AnalyticsEngine, CONFIG_PATH
from core.face_recognizer import RoboFaceID
from core.logger import JSONLogger, get_app_logger
import yaml

# Initialize Logger
logger = get_app_logger("prod-runner")

def load_runner_config():
    try:
        with open(CONFIG_PATH, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load config for runner: {e}")
        return {}

config = load_runner_config()
camera_config = config.get('cameras', {})


# Cache streammux sink pads to avoid duplicate requests
streammux_sinkpads = {}

# Import DeepStream bindings
try:
    import pyds
except ImportError:
    logger.error("Critical: pyds not found! Is deepstream-python installed?")
    sys.exit(1)
except Exception as e:
    logger.error(f"Critical: Failed to import DeepStream bindings: {e}")
    logger.error(traceback.format_exc())
    sys.exit(1)
    
# --- CONFIGURATION ---
# Initialize Recorders (Will be populated in main)
recorders = {} 
sources = {} # Track source bin elements: {source_id: GstElement}
source_status = {} # Track status: {source_id: "ACTIVE" | "EOS" | "ERROR" | "RESTARTING"}
# --- DEPLOYMENT CONFIGURATION ---
CLIENT_ID = config.get('site_info', {}).get('client_id', "INVINCIBLE_OCEAN")
SITE_ID = config.get('site_info', {}).get('site_id', "HEAD_OFFICE")
DEVICE_ID = socket.gethostname()

PGIE_CONFIG_FILE = "configs/deepstream/config_primary_gie.txt"
TRACKER_CONFIG_FILE = "configs/deepstream/config_tracker.yml"

TILED_OUTPUT_WIDTH = 1280
TILED_OUTPUT_HEIGHT = 720

# Initialize Engine
det_threshold = config.get('analytics', {}).get('face_detection_threshold', 0.6)
face_recognizer = RoboFaceID(score_threshold=det_threshold)
engine = AnalyticsEngine(face_recognizer=face_recognizer)

# Map the Source ID (0, 1, 2...) to unique Camera UUIDs/Names
CAMERA_MAP = {int(k): cam['name'] for k, cam in camera_config.items()}

def tiler_sink_pad_buffer_probe(pad, info, u_data):
    gst_buffer = info.get_buffer()
    if not gst_buffer:
        return Gst.PadProbeReturn.OK

    batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))
    if not batch_meta:
        return Gst.PadProbeReturn.OK

    l_frame = batch_meta.frame_meta_list
    while l_frame is not None:
        try:
            frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
        except StopIteration:
            break

        source_id = frame_meta.source_id
        unique_cam_id = CAMERA_MAP.get(source_id, f"UNKNOWN_CAM_{source_id}")
        
        # --- VIDEO BUFFER PREPARATION ---
        # (We extract the frame here, but we'll add it to the recorder AFTER objects are found)
        extracted_frame = None
        try:
            n_frame = pyds.get_nvds_buf_surface(hash(gst_buffer), frame_meta.batch_id)
            frame_copy = np.array(n_frame, copy=True, order='C')
            extracted_frame = cv2.cvtColor(frame_copy, cv2.COLOR_RGBA2BGR)
        except Exception:
            pass

        # Extract Objects
        frame_objects = []
        l_obj = frame_meta.obj_meta_list
        
        has_real_person = False
        has_any_person = False
        raw_detections = []

        while l_obj is not None:
            try:
                obj_meta = pyds.NvDsObjectMeta.cast(l_obj.data)
            except StopIteration:
                break
            
            model_id = obj_meta.unique_component_id
            label = obj_meta.obj_label.lower()
            conf = obj_meta.confidence
            
            if model_id == 1 and label == "person":
                if conf > 0:
                    has_real_person = True
                    has_any_person = True
                elif conf == -0.1: # Tracker shadow
                    has_any_person = True
            
            raw_detections.append((model_id, label, conf, obj_meta))
            
            try: 
                l_obj = l_obj.next
            except StopIteration:
                break

        # Filter and consolidate results
        for m_id, label, conf, obj_meta in raw_detections:
            keep = False
            if m_id == 1: # Primary (Person)
                keep = True # Keep real and shadows
            elif m_id == 2: # Fire
                keep = True # Independent
            elif m_id == 3: # Fight
                # Only keep violence if a person is present in the frame
                if label == "violence" and has_any_person:
                    keep = True
                elif label == "non_violence":
                    keep = False 

            if keep and conf > 0:
                obj_data = {
                    "label": obj_meta.obj_label,
                    "class_id": obj_meta.class_id,
                    "confidence": round(conf, 4),
                    "model_id": m_id,
                    "bbox": {
                        "top": round(obj_meta.rect_params.top),
                        "left": round(obj_meta.rect_params.left),
                        "width": round(obj_meta.rect_params.width),
                        "height": round(obj_meta.rect_params.height)
                    }
                }
                
                # --- FACE RECOGNITION (RUNNER LEVEL) ---
                if label in ["person", "face"] and extracted_frame is not None:
                     # Calculate absolute bbox coords
                     bbox_coords = [
                        obj_data["bbox"]["left"], 
                        obj_data["bbox"]["top"], 
                        obj_data["bbox"]["left"] + obj_data["bbox"]["width"], 
                        obj_data["bbox"]["top"] + obj_data["bbox"]["height"]
                    ]
                     try:
                        # Use frame_meta.frame_num as fallback ID
                        f_id = frame_meta.frame_num 
                        name, face_conf, face_id = face_recognizer.recognize(
                            extracted_frame, bbox_coords, f_id, 
                            recognition_threshold=det_threshold,
                            detection_threshold=0.7 # Using default from config
                        )
                        obj_data["recognition"] = {
                            "identity": name,
                            "confidence": face_conf,
                            "identity_id": face_id
                        }
                        obj_data["display_label"] = f"{name} ({int(face_conf*100)}%)" if name != "Stranger" else "Stranger"
                     except Exception as e:
                        pass # logger.error(f"Face ID failed: {e}")
                # ---------------------------------------

                frame_objects.append(obj_data)
                
                # if conf > 0:
                #     print(f"DEBUG: Model {m_id} confirmed {label} ({conf:.2f})")

        # Pass to Shared Logic
        recorder = recorders.get(unique_cam_id)
        
        # ADD TO BUFFER WITH METADATA (For visual debugging in snapshots/videos)
        if recorder and extracted_frame is not None:
            recorder.add_frame(extracted_frame, frame_objects=frame_objects)
            
        # Only pass frame for face recognition if a REAL person was detected
        analysis_frame = extracted_frame if has_real_person else None
        
        # Determine if this is an inference frame (Inference runs every PGIE_INTERVAL + 1 frames)
        # PGIE interval is 4 in configs/deepstream/config_primary_gie.txt
        is_inference = (frame_meta.frame_num % 5 == 0)

        engine.process_frame(
            unique_cam_id, 
            frame_objects, 
            frame=analysis_frame, 
            recorder=recorder, 
            frame_id=frame_meta.frame_num,
            is_inference=is_inference
        )

        try:
            l_frame = l_frame.next
        except StopIteration:
            break
            
    return Gst.PadProbeReturn.OK

def restart_source_bin(source_id):
    """
    Callback function to reset the source bin state.
    """
    cam_name = CAMERA_MAP.get(source_id, f"UNKNOWN_{source_id}")
    source = sources.get(source_id)
    
    if not source:
        logger.error(f"Cannot restart source {source_id}: Element not found in global dict.")
        return False
        
    logger.info(f"Executing restart for Camera {cam_name} (ID: {source_id})")
    
    try:
        # Toggle State: PLAYING -> NULL -> PLAYING
        source.set_state(Gst.State.NULL)
        # We might need a small sleep here or just rely on the next loop
        # But setting to NULL and immediately to PLAYING usually resets the connection
        if source.set_state(Gst.State.PLAYING) == Gst.StateChangeReturn.FAILURE:
             logger.error(f"Failed to set Camera {cam_name} to PLAYING.")
             source_status[source_id] = "ERROR"
        else:
              logger.info(f"Camera {cam_name} set to PLAYING. Waiting for stream...")
              source_status[source_id] = "RESTARTING"
              
              # Log Success Attempt
              alert_payload = {
                    "meta": {
                        "ts": int(time.time()),
                        "client": CLIENT_ID,
                        "site": SITE_ID,
                        "cam_id": cam_name,
                        "src_id": source_id
                    },
                    "alerts": ["CAMERA_RESTART_ATTEMPT"],
                    "message": f"Camera {cam_name} restart command sent."
              }
            #   JSONLogger.write_log(alert_payload)
             
    except Exception as e:
        logger.error(f"Exception during restart of {cam_name}: {e}")
        
    return False # Don't repeat this specific timer call

def attempt_restart(source_id):
    """
    Schedules a restart for the given source ID.
    """
    cam_name = CAMERA_MAP.get(source_id, f"UNKNOWN_{source_id}")
    
    # Update status
    source_status[source_id] = "EOS_COOLDOWN"
    
    logger.warning(f"Scheduling restart for Camera {cam_name} in 10 seconds...")
    GLib.timeout_add_seconds(10, restart_source_bin, source_id)


def log_system_status():
    """
    Periodic callback to log the status of all cameras.
    """
    try:
        status_lines = []
        for src_id, name in CAMERA_MAP.items():
            status = source_status.get(src_id, "UNKNOWN")
            status_lines.append(f"{name}: {status}")
            
        logger.info(f"SYSTEM MONITOR: [{' | '.join(status_lines)}]")
    except Exception as e:
        logger.error(f"Status Log Error: {e}")
        
    return True # Repeat every 60s

def bus_call(bus, message, loop):
    t = message.type
    if t == Gst.MessageType.EOS:
        # sys.stdout.write("End of stream\n")
        # loop.quit()
        
        # Parse source of EOS
        # EOS usually comes from the sink or the pipeline, but we check if we can pinpoint a source bin
        # However, in DeepStream with nvstreammux, single source EOS might be handled differently.
        # If nvstreammux handles EOS, it might send a tailored event or we might just see 'End of stream' if it's the whole pipe.
        # But typically individual source EOS bubbles up.
        
        src_name = message.src.get_name()
        logger.warning(f"EOS received from {src_name}")

        # Try to find which camera it is
        if "uri-decode-bin-" in src_name:
            try:
                import re
                match = re.search(r"uri-decode-bin-(\d+)", src_name)
                if match:
                   stream_index = int(match.group(1))
                   cam_name = CAMERA_MAP.get(stream_index, f"UNKNOWN_{stream_index}")
                   
                   # Log to JSON for alerts
                   alert_payload = {
                        "meta": {
                            "ts": int(time.time()),
                            "client": CLIENT_ID,
                            "site": SITE_ID,
                            "cam_id": cam_name,
                            "src_id": stream_index
                        },
                        "alerts": ["CAMERA_EOS_RESTART"],
                        "message": f"EOS received for camera {cam_name}. Restarting..."
                   }
                #    JSONLogger.write_log(alert_payload)
                   
                   logger.error(f"EOS DETECTED for Camera: {cam_name} (ID: {stream_index}). Triggering restart.")
                   
                   # Trigger Restart Logic
                   attempt_restart(stream_index)
                   return True
            except Exception:
                pass
        
        
        # If EOS comes from pipeline/sink (global EOS), it means ALL sources are done (or configured to end together).
        # CRITICAL FIX: If we ignore global EOS, the app stays alive but processes NOTHING.
        # We MUST quit so the shell script can restart the service.
        logger.critical("Global EOS received from pipeline. Quitting to allow shell script to restart service.")
        loop.quit()
        return True

    elif t == Gst.MessageType.WARNING:
        err, debug = message.parse_warning()
        sys.stderr.write("Warning: %s: %s\n" % (err, debug))

        # Ignore benign ONVIF metadata warnings
        if "VND.ONVIF.METADATA" in debug and "No decoder available" in str(err):
            return True
        
        # Also check warnings for camera issues (e.g. initial disconnects)
        error_context = f"{message.src.get_name()} {debug}"
        if "uri-decode-bin-" in error_context:
            try:
                import re
                match = re.search(r"uri-decode-bin-(\d+)", error_context)
                if match:
                    stream_index = int(match.group(1))
                    cam_name = CAMERA_MAP.get(stream_index, f"UNKNOWN_CAM_{stream_index}")
                    
                    alert_payload = {
                         "meta": {
                            "ver": "1.0",
                            "ts": int(time.time()),
                            "client": CLIENT_ID,
                            "site": SITE_ID,
                            "device": DEVICE_ID,
                            "cam_id": cam_name,
                            "src_id": stream_index
                        },
                        "alerts": ["CAMERA_WARNING"],
                        "error_msg": str(err)
                    }
                    # JSONLogger.write_log(alert_payload)
                    logger.warning(f"Camera Issue Detected: {cam_name}")
            except Exception as e:
                logger.error(f"Failed to log camera warning: {e}")

    elif t == Gst.MessageType.STATE_CHANGED:
        old_state, new_state, pending_state = message.parse_state_changed()
        src_name = message.src.get_name()
        
        # Only log state changes for the source bins (cameras)
        if "uri-decode-bin-" in src_name:
            try:
                # Extract Stream Index
                import re
                match = re.search(r"uri-decode-bin-(\d+)", src_name)
                if match:
                    stream_index = int(match.group(1))
                    cam_name = CAMERA_MAP.get(stream_index, f"UNKNOWN_CAM_{stream_index}")
                    
                    state_map = {
                        Gst.State.VOID_PENDING: "VOID_PENDING",
                        Gst.State.NULL: "NULL",
                        Gst.State.READY: "READY",
                        Gst.State.PAUSED: "PAUSED",
                        Gst.State.PLAYING: "PLAYING"
                    }
                    
                    old_s = state_map.get(old_state, str(old_state))
                    new_s = state_map.get(new_state, str(new_state))
                    
                    log_msg = f"Camera State Change: {cam_name} [{old_s} -> {new_s}]"
                    
                    # Log critical transitions
                    if new_state == Gst.State.NULL:
                        logger.error(log_msg) 
                        # Log to JSON for alerts
                        alert_payload = {
                            "meta": {
                                "ts": int(time.time()),
                                "client": CLIENT_ID,
                                "site": SITE_ID,
                                "cam_id": cam_name,
                                "src_id": stream_index
                            },
                            "alerts": ["CAMERA_STATE_NULL"],
                            "message": f"Camera went to NULL state (Effectively Offline)"
                        }
                        # JSONLogger.write_log(alert_payload)
                        
                    elif new_state == Gst.State.PLAYING:
                        logger.info(log_msg)
                        source_status[stream_index] = "ACTIVE"
                    else:
                        pass # logger.debug(log_msg)

            except Exception as e:
                logger.error(f"Failed to log state change: {e}")

    elif t == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        sys.stderr.write("Error: %s: %s\n" % (err, debug))
        
        # Robust check: Search for 'uri-decode-bin-X' in the debug string or source name
        # The error often comes from GstRTSPSrc which is INSIDE the bin.
        # Debug string looks like: "... /GstPipeline:pipeline0/GstURIDecodeBin:uri-decode-bin-2/..."
        error_context = f"{message.src.get_name()} {debug}"
        
        if "uri-decode-bin-" in error_context:
            try:
                # Regex or string splitting to find the ID
                # Find substring after "uri-decode-bin-"
                # Simple parsing assuming standard naming
                import re
                match = re.search(r"uri-decode-bin-(\d+)", error_context)
                if match:
                    stream_index = int(match.group(1))
                    cam_name = CAMERA_MAP.get(stream_index, f"UNKNOWN_CAM_{stream_index}")
                    
                    # Create detailed alert payload
                    alert_payload = {
                         "meta": {
                            "ver": "1.0",
                            "ts": int(time.time()),
                            "client": CLIENT_ID,
                            "site": SITE_ID,
                            "device": DEVICE_ID,
                            "cam_id": cam_name,
                            "src_id": stream_index
                        },
                        "alerts": ["CAMERA_OFFLINE"],
                        "error_msg": str(err)
                    }
                    # JSONLogger.write_log(alert_payload)
                    logger.error(f"Camera Offline Detected: {cam_name} - {err}")
                    
                    source_status[stream_index] = "ERROR"
                    attempt_restart(stream_index)

                    # DO NOT QUIT LOOP - Let other cameras continue
                    return True
                    
            except Exception as e:
                logger.error(f"Failed to log camera offline: {e}")

        # For critical pipeline errors (not individual camera sources), we quit
        loop.quit()
    return True

def main(args):
    # Standard GStreamer Initialization
    Gst.init(None)
    
    num_sources = len(args)
    print(f"INFO: Starting Pipeline with {num_sources} sources.")

    # Initialize Recorders
    global recorders
    for i in range(len(args)):
        cam_name = CAMERA_MAP.get(i, f"UNKNOWN_CAM_{i}")
        recorders[cam_name] = VideoRecorder(cam_name, resolution=(640, 384), buffer_seconds=10,draw_on_video=True)

    # Create Pipeline
    pipeline = Gst.Pipeline()
    streammux = Gst.ElementFactory.make("nvstreammux", "Stream-muxer")
    streammux.set_property('width', 640)
    streammux.set_property('height', 384)
    streammux.set_property('batch-size', num_sources) 
    streammux.set_property('batched-push-timeout', 40000)
    streammux.set_property('live-source', 1) # Critical for RTSP
    pipeline.add(streammux)

    # Handle RTSP Inputs
    for i, uri in enumerate(args):
        print(f"Creating source_bin for stream {i}")
        source = Gst.ElementFactory.make("uridecodebin", f"uri-decode-bin-{i}")
        source.set_property("uri", uri)
        queue = Gst.ElementFactory.make("queue", f"queue-{i}")
        conv = Gst.ElementFactory.make("nvvideoconvert", f"conv-{i}")
        capsfilter = Gst.ElementFactory.make("capsfilter", f"caps-{i}")
        capsfilter.set_property("caps", Gst.Caps.from_string("video/x-raw(memory:NVMM)"))
        pipeline.add(source)
        sources[i] = source # Save reference for restarting
        
        pipeline.add(queue)
        pipeline.add(conv)
        pipeline.add(capsfilter)
        queue.link(conv)
        conv.link(capsfilter)
        def on_pad_added(src, pad, queue=queue):
            caps = pad.get_current_caps() or pad.get_caps()
            if not caps: return
            name = caps.get_structure(0).get_name()
            if not name.startswith("video"): return
            sink_pad = queue.get_static_pad("sink")
            if not sink_pad.is_linked(): pad.link(sink_pad)
        source.connect("pad-added", on_pad_added)
        mux_sink_pad = streammux.request_pad_simple(f"sink_{i}")
        capsfilter.get_static_pad("src").link(mux_sink_pad)


    # --- INFERENCE ENGINES ---
    pgie = Gst.ElementFactory.make("nvinfer", "primary-inference")
    pgie.set_property('config-file-path', PGIE_CONFIG_FILE)
    pgie.set_property("batch-size", num_sources) 

    fire_gie = Gst.ElementFactory.make("nvinfer", "fire-inference")
    fire_gie.set_property("config-file-path", "configs/deepstream/config_fire_gie.txt")
    fire_gie.set_property("batch-size", num_sources)

    fight_gie = Gst.ElementFactory.make("nvinfer", "fight-inference")
    fight_gie.set_property("config-file-path", "configs/deepstream/config_fight_gie.txt")
    fight_gie.set_property("batch-size", num_sources)

    tracker = Gst.ElementFactory.make("nvtracker", "tracker")
    tracker.set_property('ll-config-file', TRACKER_CONFIG_FILE)
    tracker.set_property('ll-lib-file', '/opt/nvidia/deepstream/deepstream/lib/libnvds_nvmultiobjecttracker.so')

    # --- QUEUES FOR STABILITY ---
    q_pgie = Gst.ElementFactory.make("queue", "q_pgie")
    q_tracker = Gst.ElementFactory.make("queue", "q_tracker")
    q_fire = Gst.ElementFactory.make("queue", "q_fire")
    q_fight = Gst.ElementFactory.make("queue", "q_fight")
    
    # Optional: Tiler and Rendering (Keeping it simple for now to avoid hangs)
    sink = Gst.ElementFactory.make("fakesink", "nvvideo-renderer")
    sink.set_property("sync", 0)
    sink.set_property("async", 0)
    
    # Tiler & Sink
    tiler = Gst.ElementFactory.make("nvmultistreamtiler", "nvtiler")
    tiler.set_property("width", TILED_OUTPUT_WIDTH)
    tiler.set_property("height", TILED_OUTPUT_HEIGHT)
    nvvidconv = Gst.ElementFactory.make("nvvideoconvert", "nvvideo-converter")
    
    sink = Gst.ElementFactory.make("fakesink", "nvvideo-renderer")
    sink.set_property("sync", 0)  # Go as fast as possible
    sink.set_property("async", 0) # Start immediately

    nvvidconv_rgba = Gst.ElementFactory.make("nvvideoconvert", "nvvidconv-rgba")
    caps_rgba = Gst.ElementFactory.make("capsfilter", "caps-rgba")
    caps_rgba.set_property("caps", Gst.Caps.from_string("video/x-raw(memory:NVMM), format=RGBA"))

    # --- ADD ALL ELEMENTS ---
    pipeline.add(pgie)
    pipeline.add(q_pgie)
    pipeline.add(tracker)
    pipeline.add(q_tracker)
    pipeline.add(fire_gie)
    pipeline.add(q_fire)
    pipeline.add(fight_gie)
    pipeline.add(q_fight)
    pipeline.add(nvvidconv_rgba) # Add
    pipeline.add(caps_rgba)       # Add
    pipeline.add(sink)

    # --- LINKING WITH QUEUES ---
    # Stream -> PGIE -> Q -> Fire -> Q -> Fight -> Q -> Tracker -> ...
    
    # Link Chain: Mux -> PGIE -> Q -> Tracker -> Q -> Fire -> Q -> Fight -> Q -> Conv_RGBA -> Caps_RGBA -> Sink
    streammux.link(pgie)
    pgie.link(q_pgie)
    q_pgie.link(tracker)
    tracker.link(q_tracker)
    q_tracker.link(fire_gie)
    fire_gie.link(q_fire)
    q_fire.link(fight_gie)
    fight_gie.link(q_fight)
    q_fight.link(nvvidconv_rgba)
    nvvidconv_rgba.link(caps_rgba)
    caps_rgba.link(sink)

    # Probe
    # Probe (On caps_rgba src pad to ensure RGBA data is available)
    caps_rgba_src = caps_rgba.get_static_pad("src")
    if not caps_rgba_src:
        sys.stderr.write(" Unable to get caps_rgba src pad \n")
    else:
        caps_rgba_src.add_probe(Gst.PadProbeType.BUFFER, tiler_sink_pad_buffer_probe, 0)

    # Event Loop
    loop = GLib.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", bus_call, loop)

    print("Starting pipeline... Check 'detection_log.json'.")
    pipeline.set_state(Gst.State.PLAYING)
    
    # Start System Status Logger (Every 60s)
    GLib.timeout_add_seconds(60, log_system_status)
    
    try:
        loop.run()
    except KeyboardInterrupt:
        logger.info("Service interrupted by user.")
    except Exception as e:
        logger.error(f"Critical Pipeline Failure: {e}")
        logger.error(traceback.format_exc())
    finally:
        pipeline.set_state(Gst.State.NULL)
        logger.info("Cleanup complete.")

if __name__ == '__main__':
    # Load URIs from config
    rtsp_uris = [cam['uri'] for cam in camera_config.values()]
    if not rtsp_uris:
        logger.error("No RTSP URIs found in configuration!")
        sys.exit(1)
    sys.exit(main(rtsp_uris))