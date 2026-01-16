"""
Detection Log Analyzer
Generates detailed statistics and identifies anomalies in detection_log.json
"""

import json
from collections import defaultdict
from statistics import mean, stdev

def load_detection_log(filepath):
    """Load and parse the detection log JSON file."""
    with open(filepath, 'r') as f:
        content = f.read().strip()
        # Handle JSON array or newline-delimited JSON
        if content.startswith('['):
            return json.loads(content)
        else:
            # Newline-delimited JSON objects
            entries = []
            for line in content.split('\n'):
                line = line.strip().rstrip(',')
                if line and line.startswith('{'):
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
            return entries

def analyze_detections(log_path):
    """Main analysis function."""
    print("=" * 70)
    print("DETECTION LOG ANALYSIS REPORT")
    print("=" * 70)
    
    # Load data
    print("\nLoading detection log...")
    entries = load_detection_log(log_path)
    print(f"Loaded {len(entries)} frames\n")
    
    # Initialize counters
    object_counts = defaultdict(int)
    object_confidences = defaultdict(list)
    detections_per_frame = []
    frame_anomalies = []
    
    # Process each frame
    for entry in entries:
        frame_id = entry.get('frame_id', 'unknown')
        detections = entry.get('detections', [])
        detections_per_frame.append(len(detections))
        
        for det in detections:
            label = det.get('label', 'unknown')
            confidence = det.get('confidence', 0)
            
            object_counts[label] += 1
            object_confidences[label].append(confidence)
    
    # ============================================================
    # PART 1: DETAILED STATISTICS
    # ============================================================
    print("=" * 70)
    print("PART 1: DETAILED STATISTICS BY OBJECT TYPE")
    print("=" * 70)
    
    # Sort by count (descending)
    sorted_objects = sorted(object_counts.items(), key=lambda x: -x[1])
    
    print(f"\n{'Object':<15} {'Count':>10} {'Avg Conf':>12} {'Min Conf':>10} {'Max Conf':>10} {'Std Dev':>10}")
    print("-" * 70)
    
    total_detections = 0
    for label, count in sorted_objects:
        confs = object_confidences[label]
        avg_conf = mean(confs)
        min_conf = min(confs)
        max_conf = max(confs)
        std_conf = stdev(confs) if len(confs) > 1 else 0
        total_detections += count
        
        print(f"{label:<15} {count:>10,} {avg_conf:>12.4f} {min_conf:>10.4f} {max_conf:>10.4f} {std_conf:>10.4f}")
    
    print("-" * 70)
    print(f"{'TOTAL':<15} {total_detections:>10,}")
    
    # Frame-level statistics
    print(f"\n{'FRAME-LEVEL STATISTICS':^70}")
    print("-" * 70)
    avg_det_per_frame = mean(detections_per_frame)
    min_det_per_frame = min(detections_per_frame)
    max_det_per_frame = max(detections_per_frame)
    std_det_per_frame = stdev(detections_per_frame) if len(detections_per_frame) > 1 else 0
    
    print(f"Total Frames Analyzed: {len(entries):,}")
    print(f"Average Detections/Frame: {avg_det_per_frame:.2f}")
    print(f"Min Detections in a Frame: {min_det_per_frame}")
    print(f"Max Detections in a Frame: {max_det_per_frame}")
    print(f"Std Dev of Detections/Frame: {std_det_per_frame:.2f}")
    
    # ============================================================
    # PART 2: ANOMALY DETECTION
    # ============================================================
    print("\n" + "=" * 70)
    print("PART 2: ANOMALY DETECTION")
    print("=" * 70)
    
    # Define thresholds for anomalies
    low_threshold = avg_det_per_frame - 2 * std_det_per_frame
    high_threshold = avg_det_per_frame + 2 * std_det_per_frame
    
    print(f"\nAnomaly Thresholds (±2 std dev):")
    print(f"  Low: < {low_threshold:.2f} detections")
    print(f"  High: > {high_threshold:.2f} detections")
    
    # Find frame anomalies (unusual detection counts)
    low_detection_frames = []
    high_detection_frames = []
    
    for i, entry in enumerate(entries):
        frame_id = entry.get('frame_id', i)
        det_count = len(entry.get('detections', []))
        
        if det_count < low_threshold:
            low_detection_frames.append((frame_id, det_count))
        elif det_count > high_threshold:
            high_detection_frames.append((frame_id, det_count))
    
    print(f"\n--- FRAMES WITH UNUSUALLY LOW DETECTIONS ({len(low_detection_frames)} found) ---")
    if low_detection_frames:
        for frame_id, count in low_detection_frames[:20]:  # Show first 20
            print(f"  Frame {frame_id}: {count} detections")
        if len(low_detection_frames) > 20:
            print(f"  ... and {len(low_detection_frames) - 20} more")
    else:
        print("  None found")
    
    print(f"\n--- FRAMES WITH UNUSUALLY HIGH DETECTIONS ({len(high_detection_frames)} found) ---")
    if high_detection_frames:
        for frame_id, count in high_detection_frames[:20]:  # Show first 20
            print(f"  Frame {frame_id}: {count} detections")
        if len(high_detection_frames) > 20:
            print(f"  ... and {len(high_detection_frames) - 20} more")
    else:
        print("  None found")
    
    # Confidence anomalies per object type
    print(f"\n--- LOW CONFIDENCE DETECTIONS (< 0.30) ---")
    low_conf_counts = defaultdict(int)
    for entry in entries:
        for det in entry.get('detections', []):
            if det.get('confidence', 0) < 0.30:
                low_conf_counts[det.get('label', 'unknown')] += 1
    
    if low_conf_counts:
        for label, count in sorted(low_conf_counts.items(), key=lambda x: -x[1]):
            pct = (count / object_counts[label]) * 100
            print(f"  {label}: {count} low-confidence detections ({pct:.1f}% of total)")
    else:
        print("  None found")
    
    # Sudden confidence drops between consecutive frames
    print(f"\n--- CONFIDENCE TREND ANALYSIS ---")
    for label in sorted(object_counts.keys()):
        confs = object_confidences[label]
        avg = mean(confs)
        if len(confs) > 1:
            std = stdev(confs)
            variance_pct = (std / avg) * 100 if avg > 0 else 0
            stability = "STABLE" if variance_pct < 20 else "VARIABLE" if variance_pct < 40 else "UNSTABLE"
            print(f"  {label}: {stability} (variance: {variance_pct:.1f}%)")
    
    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    log_path = r"c:\Users\LENOVO\Desktop\my_docs\AG\InvEye\poc\detection_log.json"
    analyze_detections(log_path)
