# Petrol Pump VLM Prompt - Jetson AI Layer
# Input: YOLO detection context + captured frames
# Output: Validated analysis matching API format

PETROL_PUMP_PROMPT = """You are the AI verification layer for petrol pump CCTV analytics.

YOLO DETECTION CONTEXT:
{yolo_context}

Based on YOLO detections above and the images provided, verify and analyze:

1. plastic_fill: If person+nozzle detected but no vehicle → is fuel going into plastic container?
2. smoking: If hand_to_mouth pose detected → is this SMOKING, EATING, or NEITHER?
3. uniform: If staff detected → hat, tucked shirt, shoes visible? Rate 1-5
4. cleanliness: Spills, garbage, debris near pumps? Rate 1-5
5. clutter: Plastic chairs, buckets, loose items on driveway?
6. greeting: If staff+customer detected → Namaste gesture happening?
7. zero_display: Is attendant pointing at pump display showing zero?
8. du_open: Any dispenser panel open/ajar?
9. manhole: Underground tank access open?
10. unmanned_air: Vehicle at air station with no attendant?

RESPOND JSON ONLY:
{
  "ai_verified_people_count": 0,
  "validation_summary": "1-2 line description of scene and any violations",
  "triggers": [],
  "status": "safe",
  "checks": {
    "plastic_fill": {"found": false, "item": ""},
    "smoking": "NEITHER",
    "uniform": {"score": 5, "issues": []},
    "cleanliness": {"score": 5, "issues": []},
    "clutter": {"found": false, "items": []},
    "greeting": false,
    "zero_display": false,
    "du_open": "CLOSED",
    "manhole": false,
    "unmanned_air": false
  }
}

TRIGGER RULES:
- plastic_fill.found=true → add "fuel_in_plastic"
- smoking="SMOKING" → add "smoking_detected" + status="critical"
- uniform.score<3 → add "uniform_violation"
- cleanliness.score<3 → add "cleanliness_issue"
- du_open!="CLOSED" → add "du_cover_open" + status="critical"
- manhole=true → add "manhole_open" + status="critical"
- unmanned_air=true → add "unmanned_air_station"

Set status: critical (safety issues), warning (compliance issues), safe (all clear)."""


def build_prompt(yolo_detections: dict) -> str:
    """Build prompt with YOLO context for VLM inference."""
    context = f"""
    Camera: {yolo_detections.get('cam_name', 'unknown')}
    People Count: {yolo_detections.get('people_count', 0)}
    Detected Objects: {', '.join(yolo_detections.get('detected_labels', []))}
    Triggers from YOLO: {', '.join(yolo_detections.get('triggers', []))}
    """
    return PETROL_PUMP_PROMPT.replace("{yolo_context}", context.strip())


# Example usage:
# yolo_output = {"cam_name": "pump_1", "people_count": 2, "detected_labels": ["person", "nozzle"], "triggers": []}
# prompt = build_prompt(yolo_output)
# response = vlm.generate(prompt, images)
