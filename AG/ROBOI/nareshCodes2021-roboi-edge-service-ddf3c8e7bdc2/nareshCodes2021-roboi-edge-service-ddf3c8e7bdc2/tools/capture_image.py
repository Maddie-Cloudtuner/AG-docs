import cv2
import os
import datetime
from core.visual_utils import draw_annotations
from core.logger import get_app_logger

logger = get_app_logger("image-capture")

def capture_frame(frame_copy, cam_name, frame_num, alert_types, output_dir="data/captures", frame_objects=None, override_filename=None):
    """
    Saves a single frame as a WEBP image, optionally with annotations.
    """
    try:
        # Resolve directory: If output_dir is a custom full path (from a recorder event folder), use it directly.
        # Otherwise, append cam_name.
        if output_dir == "data/captures":
            cam_dir = os.path.join(output_dir, str(cam_name))
        else:
            cam_dir = output_dir
            
        os.makedirs(cam_dir, exist_ok=True)

        # Enforce sequential naming 1.webp, 2.webp, ... n.webp
        # Scan for existing numbered files to find the next index
        existing_files = os.listdir(cam_dir)
        max_idx = 0
        for f in existing_files:
            if f.endswith(".webp"):
                try:
                    # check if the filename is an integer
                    name_no_ext = os.path.splitext(f)[0]
                    idx = int(name_no_ext)
                    if idx > max_idx:
                        max_idx = idx
                except ValueError:
                    # Ignore files that aren't named "integer.webp"
                    pass
        
        next_idx = max_idx + 1
        filename = f"{next_idx}.webp"
            
        filepath = os.path.join(cam_dir, filename)

        # Ensure frame is BGR for OpenCV saving
        if frame_copy.shape[2] == 4:
            frame_copy = cv2.cvtColor(frame_copy, cv2.COLOR_RGBA2BGR)

        # Draw Annotations if provided
        # This ensures images have detection labels as requested
        if frame_objects:
            frame_copy = draw_annotations(frame_copy, frame_objects)

        cv2.imwrite(filepath, frame_copy)
        return filepath

    except Exception as e:
        logger.error(f"Failed to save image for {cam_name}: {e}")
        return None
