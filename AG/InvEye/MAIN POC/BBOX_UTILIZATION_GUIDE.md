# Bounding Box (BBox) Data Utilization Guide

## Overview

The detection system outputs bounding box coordinates in the format:
```json
"bbox": {"top": 170, "left": 116, "width": 112, "height": 213}
```

This data enables powerful analytics beyond simple detection counts.

---

## Use Cases for BBox Data

### 1. **Zone-Based Analytics**
Define virtual zones and check if detections fall within specific areas.

```python
def is_in_zone(bbox, zone):
    """Check if bbox center is within a zone"""
    center_x = bbox['left'] + bbox['width'] / 2
    center_y = bbox['top'] + bbox['height'] / 2
    return (zone['x1'] <= center_x <= zone['x2'] and 
            zone['y1'] <= center_y <= zone['y2'])

# Define zones (pixel coordinates)
ZONES = {
    'entry': {'x1': 0, 'y1': 0, 'x2': 200, 'y2': 480},
    'queue': {'x1': 200, 'y1': 100, 'x2': 400, 'y2': 380},
    'pump': {'x1': 400, 'y1': 0, 'x2': 640, 'y2': 480}
}
```

**Applications:**
- Count people in queue vs at pump
- Detect unauthorized zone access
- Track customer journey (entry → queue → pump → exit)

---

### 2. **Dwell Time Tracking**
Track how long objects stay in specific locations using bbox position over time.

```python
from collections import defaultdict
import time

class DwellTracker:
    def __init__(self, threshold_seconds=30):
        self.tracked = defaultdict(dict)
        self.threshold = threshold_seconds
    
    def update(self, cam_id, detections):
        current_time = time.time()
        for det in detections:
            # Create position hash for matching
            pos_key = f"{det['bbox']['left']//50}_{det['bbox']['top']//50}"
            
            if pos_key not in self.tracked[cam_id]:
                self.tracked[cam_id][pos_key] = current_time
            else:
                dwell = current_time - self.tracked[cam_id][pos_key]
                if dwell > self.threshold:
                    print(f"⚠️ Long dwell detected: {dwell:.0f}s at {pos_key}")
```

**Applications:**
- Detect loitering/suspicious behavior
- Queue wait time estimation
- Service time at pump

---

### 3. **Overlap & Proximity Detection**
Check if two bboxes are close or overlapping (crowd detection, social distancing).

```python
def bbox_iou(box1, box2):
    """Calculate Intersection over Union"""
    x1 = max(box1['left'], box2['left'])
    y1 = max(box1['top'], box2['top'])
    x2 = min(box1['left'] + box1['width'], box2['left'] + box2['width'])
    y2 = min(box1['top'] + box1['height'], box2['top'] + box2['height'])
    
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    area1 = box1['width'] * box1['height']
    area2 = box2['width'] * box2['height']
    
    return inter / (area1 + area2 - inter + 1e-6)

def check_crowding(detections, iou_threshold=0.1):
    """Detect if people are crowded together"""
    persons = [d for d in detections if d['label'] == 'person']
    for i, p1 in enumerate(persons):
        for p2 in persons[i+1:]:
            if bbox_iou(p1['bbox'], p2['bbox']) > iou_threshold:
                return True  # Crowd detected
    return False
```

**Applications:**
- Mob gathering detection
- Social distancing alerts
- Customer-staff interaction detection

---

### 4. **Size-Based Filtering**
Filter detections by bbox size (area) to remove noise or identify specific objects.

```python
def filter_by_size(detections, min_area=1000, max_area=50000):
    """Filter detections by bounding box area"""
    filtered = []
    for det in detections:
        area = det['bbox']['width'] * det['bbox']['height']
        if min_area <= area <= max_area:
            filtered.append(det)
    return filtered

# Example: Get only large person detections (close to camera)
large_persons = [d for d in detections 
                 if d['label'] == 'person' 
                 and d['bbox']['width'] * d['bbox']['height'] > 5000]
```

**Applications:**
- Distance estimation (larger bbox = closer)
- Filter false positives
- Child vs adult detection (smaller bbox)

---

### 5. **Motion & Direction Tracking**
Track bbox movement between frames to determine direction.

```python
class DirectionTracker:
    def __init__(self):
        self.previous_positions = {}
    
    def get_direction(self, cam_id, detections):
        movements = []
        current = {self._get_id(d): d['bbox'] for d in detections}
        
        if cam_id in self.previous_positions:
            for obj_id, curr_bbox in current.items():
                if obj_id in self.previous_positions[cam_id]:
                    prev = self.previous_positions[cam_id][obj_id]
                    dx = curr_bbox['left'] - prev['left']
                    dy = curr_bbox['top'] - prev['top']
                    
                    if abs(dx) > 10:  # Horizontal movement
                        direction = 'RIGHT' if dx > 0 else 'LEFT'
                        movements.append({'id': obj_id, 'direction': direction})
        
        self.previous_positions[cam_id] = current
        return movements
    
    def _get_id(self, detection):
        # Use position + label as pseudo-ID
        return f"{detection['label']}_{detection['bbox']['left']//30}"
```

**Applications:**
- Entry vs exit counting (directional)
- Traffic flow analysis
- Abnormal movement patterns

---

### 6. **Heatmap Generation**
Aggregate bbox positions over time to create activity heatmaps.

```python
import numpy as np

class HeatmapGenerator:
    def __init__(self, width=640, height=480, grid_size=20):
        self.grid = np.zeros((height // grid_size, width // grid_size))
        self.grid_size = grid_size
    
    def add_detection(self, bbox):
        cx = (bbox['left'] + bbox['width'] // 2) // self.grid_size
        cy = (bbox['top'] + bbox['height'] // 2) // self.grid_size
        if 0 <= cy < self.grid.shape[0] and 0 <= cx < self.grid.shape[1]:
            self.grid[cy, cx] += 1
    
    def get_hotspots(self, threshold=10):
        """Get grid cells with activity above threshold"""
        hotspots = np.argwhere(self.grid > threshold)
        return [(y * self.grid_size, x * self.grid_size) for y, x in hotspots]
```

**Applications:**
- Identify high-traffic areas
- Optimize camera placement
- Safety zone violation heatmaps

---

## Data Schema Reference

```json
{
  "type": "METRIC",
  "meta": {
    "ts": 1767078122,        // Unix timestamp
    "cam_id": "CAFETERIA",   // Camera identifier
    "site": "HEAD_OFFICE",   // Site/location
    "status": "SAFE"         // Overall status
  },
  "data": {
    "people_count": 2,
    "detections": [
      {
        "label": "person",
        "class_id": 0,
        "confidence": 0.91,
        "model_id": 1,
        "bbox": {
          "top": 170,      // Y coordinate (pixels from top)
          "left": 116,     // X coordinate (pixels from left)
          "width": 112,    // Box width
          "height": 213    // Box height
        },
        "recognition": {
          "identity": "Stranger",
          "confidence": 1.0,
          "identity_id": 0
        }
      }
    ]
  }
}
```

---

## Quick Integration Example

```python
def process_detection(data):
    """Full processing pipeline"""
    cam_id = data['meta']['cam_id']
    detections = data['data']['detections']
    
    # Filter persons only
    persons = [d for d in detections if d['label'] == 'person']
    
    # Check zones
    for person in persons:
        if is_in_zone(person['bbox'], ZONES['restricted']):
            alert("Unauthorized access!", cam_id, person)
    
    # Check crowding
    if check_crowding(persons):
        alert("Crowd gathering detected!", cam_id)
    
    # Update heatmap
    for person in persons:
        heatmap.add_detection(person['bbox'])
    
    return {
        'people_count': len(persons),
        'in_queue': sum(1 for p in persons if is_in_zone(p['bbox'], ZONES['queue'])),
        'crowded': check_crowding(persons)
    }
```

---

## Summary Table

| Use Case | Key Function | Output |
|----------|--------------|--------|
| Zone Analytics | `is_in_zone()` | People per zone count |
| Dwell Time | Position tracking over time | Loitering alerts |
| Proximity | `bbox_iou()` | Crowd detection |
| Size Filter | Area calculation | Distance estimation |
| Direction | Frame-to-frame delta | Entry/exit counting |
| Heatmaps | Grid accumulation | Traffic hotspots |

---

*Document created: 2024-12-30*
