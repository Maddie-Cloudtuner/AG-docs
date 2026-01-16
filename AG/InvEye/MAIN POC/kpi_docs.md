# ⛽ Smart Petrol Pump Monitoring System (Edge-AI)

## 1. Project Overview

**Vision:** Automated "Eyes-on-Ground" for petrol pump operations.
**Goal:** Transform 12+ CCTV RTSP feeds into actionable insights regarding Safety, SOP Compliance, and Customer Analytics without manual monitoring.
**Hardware Stack:** NVIDIA Jetson Orin Nano Super Devkits (3x per site).
**Core Strategy:** **"Trigger & Verify"** Architecture. High-speed object detection (YOLO) acts as the trigger, and Large Vision Models (VLMs) act as the auditor for complex reasoning.

## 2. System Architecture

The pipeline follows a tiered approach to balance high-speed inference with high-intelligence reasoning.

### Tier 1: The Watcher (Real-Time Detection)

- **Engine:** NVIDIA DeepStream SDK.
- **Models:** YOLOv8 (Objects), Pose Estimation (Actions), DeepSort (Tracking), LPRNet (License Plates).
- **Frequency:** 15 FPS per channel.
- **Role:** Detects atoms (Car, Person, Fire, Nozzle, Cone) and tracks movement vectors.
- **Output:** Bounding Boxes, Class IDs, Track IDs.

### Tier 2: The Logic Gate (Heuristics)

- **Engine:** Python (Custom Business Logic).
- **Role:** Spatial and Temporal filtering.
  - _Example:_ "Is the Person inside the Pump Zone?"
  - _Example:_ "Has Track_ID #45 been stationary for > 15 minutes?"
- **Output:** Triggers for Alerts or VLM requests.

### Tier 3: The Auditor (Vision Language Models)

- **Engine:** Gemini 1.5 Flash (Cloud API) or NanoLLaVA (Edge).
- **Trigger:** Invoked only when Tier 2 detects a potential SOP step or Violation.
- **Role:** Contextual understanding.
  - _Example:_ "I see a person pointing at the pump (Pose). **VLM Check:** Is the pump screen showing 0.00?"
- **Output:** Text verification (True/False) and confidence score.

### Tier 4: Visualization & Reporting

- **Transport:** MQTT (JSON Metadata) + S3/MinIO (Image Evidences).
- **Dashboard:** Web UI showing real-time alerts, compliance heatmaps, and cleanliness logs.

---

## 3. Workflow Logic: "Trigger & Verify"

We do not send video to the VLM. We use standard CV to find the _moment of interest_, frame it, and ask the VLM a specific question.

1.  **Input:** 12 Cameras -> RTSP -> Jetson.
2.  **Filter:** DeepStream drops frames with no motion/objects.
3.  **Detect:** YOLO finds a "Person" and a "Testing Jar".
4.  **Logic:** Distance between Person and Jar < 0.5m? -> **trigger_event**.
5.  **Audit:** Crop image of Person+Jar -> Send to VLM -> Prompt: _"Is the nozzle inside the jar?"_
6.  **Action:** If VLM = Yes, Log "5L Test Completed" to Dashboard.

---

## 4. KPI Implementation Strategy

The following table defines the technical pipeline for every SOP/KPI.

**Legend:**

- **YOLO:** Standard Object Detection.
- **Pose:** Keypoint Skeleton Detection.
- **Logic:** Python `if/else`, Polygon Zones, Time calc.
- **VLM:** Vision Language Model (Gemini/GPT-4o/Edge).
- **OCR:** Optical Character Recognition.

| Sr No. | KPI Name                     | Pipeline Strategy             | Implementation Logic                                                                                                                                                           |
| :----- | :--------------------------- | :---------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1**  | **5 Litre Testing (Pump)**   | **YOLO → Logic → VLM**        | **YOLO:** Detect `Jar`, `Nozzle`, `Person`.<br>**Logic:** When Nozzle & Jar overlap.<br>**VLM:** "Is the fuel nozzle tip physically inside the testing jar?"                   |
| **2**  | **% Conversion of Vehicles** | **YOLO → Tracker → Logic**    | **YOLO:** Detect `Vehicle`.<br>**Logic:** Count unique IDs entering `Entry_Zone` vs unique IDs stopping in `Fueling_Zone`.                                                     |
| **3**  | **5 Litre Return to Tank**   | **YOLO → Tracker → VLM**      | **YOLO:** Track `Person` carrying `Jar`.<br>**Logic:** When Person enters `Tank_Fill_Zone`.<br>**VLM:** "Is the person pouring liquid from the jar into the underground tank?" |
| **4**  | **Opening of DU Cover**      | **YOLO (Custom Class)**       | **YOLO:** Train a specific class for `open_dispenser_cover`. Alert if confidence > 80%.                                                                                        |
| **5**  | **Man-hole Chamber Open**    | **YOLO (Custom Class)**       | **YOLO:** Train specific class for `open_manhole`. Alert immediately.                                                                                                          |
| **6**  | **Fuel in Plastic Bottles**  | **YOLO → Logic → VLM**        | **YOLO:** Detect `Person`, `Nozzle`.<br>**Logic:** Nozzle active but NO `Vehicle` in zone.<br>**VLM:** "Is the nozzle filling a plastic bottle or unauthorized container?"     |
| **7**  | **FSM Attendance**           | **Face Recognition**          | Use ArcFace or Dlib. Match detected faces against employee database at start of shift.                                                                                         |
| **8**  | **Smoking in Premises**      | **Pose → VLM**                | **Pose:** Detect `Hand_to_Mouth` gesture.<br>**VLM:** "Is this person holding a cigarette or smoking?" (Filters out eating/yawning).                                           |
| **9**  | **Repeat Customer (ANPR)**   | **LPRNet (OCR)**              | Standard LPRNet model in DeepStream. Log Plate Number + Timestamp to DB.                                                                                                       |
| **10** | **Uniform & Hygiene**        | **YOLO → VLM**                | **YOLO:** Detect `FSM` (Staff).<br>**Trigger:** Once per hour per staff.<br>**VLM:** "Is the person wearing a blue hat, tucked-in shirt, and safety shoes? Rate appearance."   |
| **11** | **Cleanliness of DUs**       | **Time → VLM**                | **Trigger:** Snapshot every 30/60 mins.<br>**VLM:** "Identify garbage, oil spills, or stickers on the pump island. Is it clean?"                                               |
| **12** | **Left without Fueling**     | **YOLO → Tracker → Logic**    | **Logic:** `Track_ID` enters `Site`, dwells < 5 mins, never enters `Fueling_Zone`, enters `Exit_Zone`.                                                                         |
| **13** | **Plastic Items/Clutter**    | **Time → VLM**                | **Trigger:** Snapshot every 30 mins.<br>**VLM:** "List all plastic chairs, buckets, or loose items on the driveway."                                                           |
| **14** | **Mob Gathering**            | **YOLO → Logic**              | **YOLO:** Detect `Person`.<br>**Logic:** If `Count(Person)` > 10 in a defined Polygon Zone.                                                                                    |
| **15** | **Greeting (Namaste)**       | **Pose → VLM**                | **Pose:** Detect wrists/elbows close (Prayer pose).<br>**VLM:** "Is the attendant greeting a customer with a Namaste gesture?"                                                 |
| **16** | **Showing Zero**             | **Pose → VLM**                | **Pose:** Detect FSM `Pointing` gesture near DU.<br>**VLM:** "Read the pump display. Does it show zero? Is the attendant pointing at it?"                                      |
| **17** | **Manned Air Filling**       | **YOLO → Logic**              | **Logic:** If `Vehicle` in `Air_Zone` AND `Person` NOT in `Air_Zone` for > 60 seconds.                                                                                         |
| **--** | **Fire Detection**           | **YOLO (Fire Class)**         | Standard detection. High priority alert.                                                                                                                                       |
| **--** | **Fight Detection**          | **Pose / Action Recognition** | Use a lightweight Action Recognition model (e.g., LSTM on Pose keypoints) for rapid movement/violence.                                                                         |
