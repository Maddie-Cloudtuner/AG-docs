import random
import os
import time
import datetime
import socket
import yaml
import traceback
from core.logger import JSONLogger, get_app_logger

# Initialize Logger
logger = get_app_logger("analytics-engine")

# Load Configuration
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "configs", "app_config.yaml")

def load_config():
    try:
        with open(CONFIG_PATH, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return {}

config = load_config()

# --- DYNAMIC CONFIGURATION ---
HEARTBEAT_INTERVAL = config.get('analytics', {}).get('heartbeat_interval', 60.0)
ALERT_COOLDOWN = config.get('analytics', {}).get('alert_cooldown', 5.0)
SNAPSHOTS_PER_EVENT = config.get('analytics', {}).get('snapshots_per_event', 0)
PRE_EVENT_SECONDS = config.get('analytics', {}).get('pre_event_seconds', 3)
POST_EVENT_SECONDS = config.get('analytics', {}).get('post_event_seconds', 5)

# --- ACCESS CONTROL POLICIES ---
POLICY = config.get('policy', {})
CLIENT_ID = config.get('site_info', {}).get('client_id', "INVINCIBLE_OCEAN")
SITE_NAME = config.get('site_info', {}).get('site_name', "HEAD_OFFICE")
SITE_ID = config.get('site_info', {}).get('site_id', "ro001")
COUNTRY = config.get('site_info', {}).get('country', "india")
STATE = config.get('site_info', {}).get('state', "west_bengal")
DISTRICT = config.get('site_info', {}).get('district', "kolkata")
LATITUDE = config.get('site_info', {}).get('latitude', 0.0)
LONGITUDE = config.get('site_info', {}).get('longitude', 0.0)
DEVICE_ID = socket.gethostname()

def check_timebased_policy_violation(camera_name, current_time):
    """
    Checks if presence is unauthorized based on time and location from config.
    """
    alerts = []
    is_sunday = (current_time.weekday() == 6)
    hour = current_time.hour
    minute = current_time.minute

    if is_sunday:
        alerts.append("restricted_access_sunday")

    # Get specific camera policy or default to office
    policy_key = 'boss_cabin' if camera_name == "boss_cabin" else 'office'
    p = POLICY.get(policy_key, {})
    
    open_h = p.get('open_hour', 0)
    open_m = p.get('open_min', 0)
    close_h = p.get('close_hour', 23)
    close_m = p.get('close_min', 59)

    if hour < open_h or (hour == open_h and minute < open_m):
        alerts.append(f"restricted_access_before_hours")
    elif hour > close_h or (hour == close_h and minute >= close_m):
        alerts.append(f"restricted_access_after_hours")
    
    return alerts

def check_countbased_policy_violation(camera_name, num_people, num_vehicles):
    alerts = []
    
    crowd_controlled_zones = POLICY.get('crowd_controlled_zones', [])

    # Alert if more than 5 people are present in crowd controlled zones
    if camera_name in crowd_controlled_zones and (num_people > 5):
        alerts.append("crowd_policy_violation")
    
    # Alert if more than 12 vehicles are present in crowd controlled zones
    if camera_name in crowd_controlled_zones and (num_vehicles > 12):
        alerts.append("vehicle_crowd_policy_violation")

    return alerts

class AnalyticsEngine:
    def __init__(self, face_recognizer=None):
        self.last_heartbeat_time = {}
        self.last_alert_time = {}
        self.face_recognizer = face_recognizer
        self.last_config_check = 0
        
        # Load thresholds from config
        self.recognition_threshold = config.get('analytics', {}).get('face_recognition_threshold', 0.5)
        self.face_threshold = config.get('analytics', {}).get('face_detection_threshold', 0.5)
        self.people_threshold = config.get('analytics', {}).get('person_detection_threshold', 0.7)
        self.violence_threshold = config.get('analytics', {}).get('violence_threshold', 0.2)
        self.fire_threshold = config.get('analytics', {}).get('fire_threshold', 0.2)
        self.vehicle_threshold = config.get('analytics', {}).get('vehicle_threshold', 0.2)
        
        self.VEHICLE_LABELS = ["bicycle", "car", "motorcycle", "bus", "train", "truck", "boat"]
        
        # Priority Lists for Alerts
        self.emergency_alerts = config.get('analytics', {}).get('emergency_alert_policies', ["fire_detected_critical"])
        self.critical_alerts = config.get('analytics', {}).get('critical_alert_policies', ["fight_detected_critical", "crowd_policy_violation"])
        self.warning_alerts = config.get('analytics', {}).get('warning_alert_policies', [])

        # --- AI INSIGHTS CONFIGURATION ---
        self.ai_insights_enabled = config.get('analytics', {}).get('ai_insights_enabled', True)
        self.ai_insights_per_hour = config.get('analytics', {}).get('ai_insights_per_hour', 10)
        self.ai_insights_duration = config.get('analytics', {}).get('ai_insights_duration', 30)
        self.ai_insights_snapshots = config.get('analytics', {}).get('ai_insights_snapshots', 10)
        
        self.ai_insights_schedule = {} # {cam_id: [timestamps]}
        self.ai_insights_period_start = {} # {cam_id: start_of_current_hour_window}

    def _check_config_updates(self):
        """Reloads dynamic config parameters periodicially."""
        now = time.time()
        if now - self.last_config_check > 5.0: # Check every 5 seconds
            try:
                with open(CONFIG_PATH, 'r') as f:
                    new_config = yaml.safe_load(f)
                    
                    # 1. Update Thresholds
                    self.recognition_threshold = new_config.get('analytics', {}).get('face_recognition_threshold', self.recognition_threshold)
                    self.face_threshold = new_config.get('analytics', {}).get('face_detection_threshold', self.face_threshold)
                    self.people_threshold = new_config.get('analytics', {}).get('person_detection_threshold', self.people_threshold)
                    self.violence_threshold = new_config.get('analytics', {}).get('violence_threshold', self.violence_threshold)
                    self.fire_threshold = new_config.get('analytics', {}).get('fire_threshold', self.fire_threshold)
                    self.vehicle_threshold = new_config.get('analytics', {}).get('vehicle_threshold', self.vehicle_threshold)
                    
                    # Update Alert Priorities
                    self.emergency_alerts = new_config.get('analytics', {}).get('emergency_alert_policies', self.emergency_alerts)
                    self.critical_alerts = new_config.get('analytics', {}).get('critical_alert_policies', self.critical_alerts)
                    self.warning_alerts = new_config.get('analytics', {}).get('warning_alert_policies', self.warning_alerts)
                    
                    # Update AI Insights Params
                    self.ai_insights_enabled = new_config.get('analytics', {}).get('ai_insights_enabled', self.ai_insights_enabled)
                    self.ai_insights_per_hour = new_config.get('analytics', {}).get('ai_insights_per_hour', self.ai_insights_per_hour)
                    self.ai_insights_duration = new_config.get('analytics', {}).get('ai_insights_duration', self.ai_insights_duration)
                    self.ai_insights_snapshots = new_config.get('analytics', {}).get('ai_insights_snapshots', self.ai_insights_snapshots)

                    # 1.1 Update Site Info and Analytics Params
                    global CLIENT_ID, SITE_NAME, SITE_ID, COUNTRY, STATE, DISTRICT, SNAPSHOTS_PER_EVENT, PRE_EVENT_SECONDS, POST_EVENT_SECONDS, LATITUDE, LONGITUDE
                    
                    SNAPSHOTS_PER_EVENT = new_config.get('analytics', {}).get('snapshots_per_event', SNAPSHOTS_PER_EVENT)
                    PRE_EVENT_SECONDS = new_config.get('analytics', {}).get('pre_event_seconds', PRE_EVENT_SECONDS)
                    POST_EVENT_SECONDS = new_config.get('analytics', {}).get('post_event_seconds', POST_EVENT_SECONDS)
                    
                    site_info = new_config.get('site_info', {})
                    CLIENT_ID = site_info.get('client_id', CLIENT_ID)
                    SITE_NAME = site_info.get('site_name', SITE_NAME)
                    SITE_ID = site_info.get('site_id', SITE_ID)
                    COUNTRY = site_info.get('country', COUNTRY)
                    STATE = site_info.get('state', STATE)
                    DISTRICT = site_info.get('district', DISTRICT)
                    LATITUDE = site_info.get('latitude', LATITUDE)
                    LONGITUDE = site_info.get('longitude', LONGITUDE)

                    # 2. Update Global Policy
                    global POLICY
                    POLICY = new_config.get('policy', POLICY)
                    
            except Exception as e:
                logger.error(f"Config reload failed: {e}")
            self.last_config_check = now

    def _determine_status(self, site_alerts):
        """
        Determines the highest priority status based on active alerts.
        """
        if not site_alerts:
            return "safe"
            
        # Check iteratively for priority
        for alert in site_alerts:
            if alert in self.emergency_alerts:
                return "emergency"
        
        for alert in site_alerts:
            if alert in self.critical_alerts:
                return "critical"
                
        for alert in site_alerts:
            if alert in self.warning_alerts:
                return "warning"
        
        # Default for unmapped alerts
        return "critical"

    def _update_ai_insights_schedule(self, unique_cam_id, current_time):
        """
        Ensures a valid schedule of random timestamps exists for the current hour.
        """
        if not self.ai_insights_enabled:
            self.ai_insights_schedule[unique_cam_id] = []
            return

        # Initialize for new camera
        if unique_cam_id not in self.ai_insights_period_start:
            self.ai_insights_period_start[unique_cam_id] = 0
            self.ai_insights_schedule[unique_cam_id] = []

        period_start = self.ai_insights_period_start[unique_cam_id]
        
        # Check if we need a new schedule (every hour = 3600 seconds)
        if current_time - period_start >= 3600:
            # Start new period now
            new_start = current_time
            self.ai_insights_period_start[unique_cam_id] = new_start
            
            # Generate random offsets within 3600 seconds
            # Ensure we don't pick a time already passed in the very immediate logic, 
            # though taking current_time as base deals with that.
            offsets = sorted(random.sample(range(0, 3600), min(3600, self.ai_insights_per_hour)))
            
            # Convert to absolute timestamps
            self.ai_insights_schedule[unique_cam_id] = [new_start + o for o in offsets]
            logger.info(f"Generated {len(offsets)} AI Insight triggers for {unique_cam_id} starting {new_start}")

    def process_frame(self, unique_cam_id, frame_objects, frame=None, recorder=None, frame_id=None, is_inference=True):
        """
        Processes detections for a single frame.
        """
        current_time = time.time()
        current_time_int = int(current_time)
        
        # Initialize heartbeat timer for new cameras to avoid startup burst
        if unique_cam_id not in self.last_heartbeat_time:
            self.last_heartbeat_time[unique_cam_id] = current_time

        last_hb = self.last_heartbeat_time.get(unique_cam_id, current_time)
        last_al = self.last_alert_time.get(unique_cam_id, 0)
        
        # Only log heartbeats on inference frames to ensure accuracy
        should_log_heartbeat = is_inference and (current_time - last_hb >= HEARTBEAT_INTERVAL)
        
        # Determine if we have any high-confidence detections for immediate alert
        # (Violence check is done below with threshold)
        has_any_obj = len(frame_objects) > 0
        
        
        # --- AI INSIGHTS TRIGGER CHECK (Schedule Update) ---
        self._update_ai_insights_schedule(unique_cam_id, current_time)
        schedule = self.ai_insights_schedule.get(unique_cam_id, [])
        is_ai_insight_due = bool(schedule and schedule[0] <= current_time)

        # If no objects AND no heartbeat due AND no insight due, skip everything
        if not has_any_obj and not should_log_heartbeat and not is_ai_insight_due:
            return

        # Metadata enrichment is handled by the Runner Probes now.
        
        # Extraction for logic - Apply dynamic thresholds
        self._check_config_updates()

        # Filter valid detections based on their specific labels and thresholds
        valid_people = [obj for obj in frame_objects if obj["label"].lower() in ["person", "face"] and obj.get("confidence", 0) >= self.people_threshold]
        valid_fire = [obj for obj in frame_objects if obj["label"].lower() in ["fire", "smoke"] and obj.get("confidence", 0) >= self.fire_threshold]
        valid_violence = [obj for obj in frame_objects if obj["label"].lower() == "violence" and obj.get("confidence", 0) >= self.violence_threshold]
        valid_vehicles = [obj for obj in frame_objects if obj["label"].lower() in self.VEHICLE_LABELS and obj.get("confidence", 0) >= self.vehicle_threshold]

        num_people = len(valid_people)
        num_vehicles = len(valid_vehicles)
        fire_detected = len(valid_fire) > 0
        violence_detected = len(valid_violence) > 0
        vehicle_detected = len(valid_vehicles) > 0
        
        # Consistent UTC time for policy check
        now_dt = datetime.datetime.now(datetime.timezone.utc)
        
        # 1. Get initial time-based alerts (Only if someone is present)
        site_alerts = []
        if num_people > 0:
            site_alerts = check_timebased_policy_violation(unique_cam_id, now_dt)
            site_alerts.extend(check_countbased_policy_violation(unique_cam_id, num_people, num_vehicles))
        
        # 2. Refine alerts for BOSS_CABIN based on identity
        # 2. Refine alerts for BOSS_CABIN based on identity
        if unique_cam_id == "boss_cabin" and site_alerts:
            self._check_config_updates()
            boss_policy = POLICY.get('boss_cabin', {})
            allowlist = [name.lower() for name in boss_policy.get('allowlist', [])]
            
            authorized_person_present = False
            unauthorized_identities = []
            
            # Check each detected face
            for obj in frame_objects:
                label = obj["label"].lower()
                if label in ["face", "person"] and "recognition" in obj:
                    identity = obj["recognition"]["identity"].lower()
                    
                    if identity in allowlist:
                        authorized_person_present = True
                        break # Found the boss, stop checking others for current logic
                    elif identity == "stranger":
                        unauthorized_identities.append("stranger")
                    else:
                        unauthorized_identities.append(identity.lower())
            
            if authorized_person_present:
                # The Boss is here! Suppress time-based alerts.
                site_alerts = []
            elif unauthorized_identities:
                # Time violation + Unauthorized person/stranger
                # Tag for identity violation
                site_alerts = []
                for identity in unauthorized_identities:
                    tag = "unauthorized_stranger" if identity == "stranger" else f"unauthorized_person_{identity}"
                    if tag not in site_alerts:
                        site_alerts.append(tag)
            # If site_alerts had time violations but NO face was found, we KEEP the time alerts.

        # 3. Add fire alerts (global)
        if fire_detected:
            site_alerts.insert(0, "fire_detected_critical")
        
        # 4. Add violence alerts (global)
        if violence_detected:
            site_alerts.insert(0, "fight_detected_critical")

        # 5. Add vehicle alerts (global)
        if vehicle_detected:
            pass
            # site_alerts.append("VEHICLE_DETECTED")

        is_event = len(site_alerts) > 0
        
        should_log_event = is_event and (current_time - last_al >= ALERT_COOLDOWN)
        should_log_heartbeat = (current_time - last_hb >= HEARTBEAT_INTERVAL)
        
        payload = None

        if should_log_event:
            logger.info('EVENT DETECTED')
            self.last_alert_time[unique_cam_id] = current_time
            # Dynamic status mapping
            status = self._determine_status(site_alerts)
            
            # Collect all valid detections for the log
            all_valid_detections = valid_people + valid_fire + valid_violence + valid_vehicles
            
            # Add any other objects that pass a default threshold (e.g. 0.5) to keep metrics interesting
            other_objects = [obj for obj in frame_objects if obj.get("confidence", 0) >= 0.5 and obj not in all_valid_detections]
            log_detections = all_valid_detections + other_objects

            # Add display_label to objects if missing
            for obj in log_detections:
                if "display_label" not in obj:
                    if "recognition" in obj:
                        obj["display_label"] = obj["recognition"].get("identity", obj["label"])
                    else:
                        # For non-recognized objects, maybe not needed or use label?
                        # detection_log_modified doesn't show it for chair, so we leave it absent or None.
                        # But if we want consistent schema, we might add it.
                        # Leaving it out as per example.
                        pass

            payload = {
                "type": "event",
                "meta": {
                    "ts": current_time_int,
                    "cam_id": unique_cam_id,
                    "site_name": SITE_NAME,
                    "site_id": SITE_ID,
                    "latitude": LATITUDE,
                    "longitude": LONGITUDE,
                    "country": COUNTRY,
                    "state": STATE,
                    "district": DISTRICT
                },
                "data": {
                    "triggers": site_alerts,
                    "status": status,
                    "people_count": num_people,
                    "detection_count": len(log_detections),
                    "video_count": 0,
                    "image_count": 0,
                    "detections": log_detections,
                    "triaged_by": "",
                    "triage_notes": "",
                    "triage_timestamp": 0,
                    "ai_insights": "",
                    "capture_triggered": False,
                    "evidence_path": ""
                }
            }

            # Reset heartbeat timer when an event is logged to avoid redundancy
            self.last_heartbeat_time[unique_cam_id] = current_time

            if recorder:
                try:
                    ts_str = str(current_time_int)
                    
                    # Construct triggers string
                    # trigger_str = "_".join(site_alerts) if site_alerts else "alert"
                    # trigger_str = "".join([c if c.isalnum() else "_" for c in trigger_str]).lower()
                    
                    if recorder:
                         # Use lower case for directory
                         event_dir = f"{COUNTRY}_{STATE}_{DISTRICT}_{SITE_ID}_{unique_cam_id}_{ts_str}".lower()
                    logger.info(f"Triggering recording for {unique_cam_id} with event_dir: {event_dir} at {ts_str}")
                    recorder.trigger_recording(
                        site_alerts, 
                        snapshot_sequence=True, 
                        frame_objects=frame_objects, 
                        event_dir=event_dir, 
                        num_snapshots=SNAPSHOTS_PER_EVENT,
                        pre_event_seconds=PRE_EVENT_SECONDS,
                        post_event_seconds=POST_EVENT_SECONDS
                    )
                    logger.info(f"Recording triggered for {unique_cam_id} with event_dir: {event_dir} at {ts_str}")
                    payload["data"]["capture_triggered"] = True
                    payload["data"]["evidence_path"] = event_dir
                    payload["data"]["video_count"] = 1
                    payload["data"]["image_count"] = SNAPSHOTS_PER_EVENT
                except Exception as e:
                    logger.error(f"Trigger failed for {unique_cam_id}: {e}")
        
        elif should_log_heartbeat:
            self.last_heartbeat_time[unique_cam_id] = current_time
            # Same for heartbeats
            all_valid_detections = valid_people + valid_fire + valid_violence + valid_vehicles
            other_objects = [obj for obj in frame_objects if obj.get("confidence", 0) >= 0.5 and obj not in all_valid_detections]
            log_detections = all_valid_detections + other_objects

            payload = {
                "type": "metric",
                "meta": {
                    "ts": current_time_int,
                    "cam_id": unique_cam_id,
                    "site_name": SITE_NAME,
                    "site_id": SITE_ID,
                    "latitude": LATITUDE,
                    "longitude": LONGITUDE,
                    "country": COUNTRY,
                    "state": STATE,
                    "district": DISTRICT
                },
                "data": {
                    "status": "safe",
                    "triggers": [],
                    "people_count": num_people,
                    "detection_count": len(log_detections),
                    "video_count": 0,
                    "image_count": 0,
                    "detections": log_detections,
                    "triaged_by": "",
                    "triage_notes": "",
                    "triage_timestamp": 0,
                    "ai_insights": "",
                    "capture_triggered": False,
                    "evidence_path": ""
                }
            }
        
        # --- AI INSIGHTS TRIGGER CHECK ---
        # self._update_ai_insights_schedule(unique_cam_id, current_time) # Done at start
        
        # Check if any scheduled time is passed
        schedule = self.ai_insights_schedule.get(unique_cam_id, [])
        triggered_insight = False
        
        if is_ai_insight_due and schedule: # Reuse flag but recheck existence safely
            # Trigger!
            triggered_insight = True
            if schedule: # Double check
                 trigger_ts = schedule.pop(0) # Remove from schedule
            else:
                 trigger_ts = current_time
            self.ai_insights_schedule[unique_cam_id] = schedule # Update list
            
            logger.info(f"AI INSIGHTS TRIGGERED for {unique_cam_id} at {trigger_ts}")
            
            # Construct Payload
            # Reusing detection logic from event/metric
            all_valid_detections = valid_people + valid_fire + valid_violence + valid_vehicles
            other_objects = [obj for obj in frame_objects if obj.get("confidence", 0) >= 0.5 and obj not in all_valid_detections]
            log_detections = all_valid_detections + other_objects
            
            insight_payload = {
                "type": "ai-info",
                "meta": {
                    "ts": int(trigger_ts),
                    "cam_id": unique_cam_id,
                    "site_name": SITE_NAME,
                    "site_id": SITE_ID,
                    "latitude": LATITUDE,
                    "longitude": LONGITUDE,
                    "country": COUNTRY,
                    "state": STATE,
                    "district": DISTRICT
                },
                "data": {
                    "status": "safe",
                    "triggers": [],
                    "people_count": num_people,
                    "detection_count": len(log_detections),
                    "video_count": 0,
                    "image_count": 0,
                    "detections": log_detections,
                    "triaged_by": "",
                    "triage_notes": "",
                    "triage_timestamp": 0,
                    "ai_insights": "Periodic Random Capture",
                    "capture_triggered": False,
                    "evidence_path": ""
                }
            }
            
            if recorder:
                try:
                    ts_str = str(int(current_time))
                    event_dir = f"insight_{COUNTRY}_{STATE}_{DISTRICT}_{SITE_ID}_{unique_cam_id}_{ts_str}".lower()
                    
                    logger.info(f"Triggering AI Insight recording for {unique_cam_id}: {event_dir}")
                    recorder.trigger_recording(
                        ["ai_insight"],
                        snapshot_sequence=True,
                        frame_objects=frame_objects,
                        event_dir=event_dir,
                        num_snapshots=self.ai_insights_snapshots,     # 10 photos
                        pre_event_seconds=0,                            # Start now
                        post_event_seconds=self.ai_insights_duration    # 30 seconds
                    )
                    
                    insight_payload["data"]["capture_triggered"] = True
                    insight_payload["data"]["evidence_path"] = event_dir
                    insight_payload["data"]["video_count"] = 1
                    insight_payload["data"]["image_count"] = self.ai_insights_snapshots
                    
                except Exception as e:
                     logger.error(f"AI Insight trigger failed for {unique_cam_id}: {e}")

            if insight_payload:
                 JSONLogger.write_log(insight_payload)
        
        if payload:
            JSONLogger.write_log(payload)