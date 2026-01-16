import cv2
from core.logger import get_app_logger

logger = get_app_logger("visual-utils")

def draw_annotations(frame, objects):
    """
    Draws bounding boxes and labels on a frame.
    objects: list of dicts with {'label', 'confidence', 'bbox': {'top', 'left', 'width', 'height'}}
    """
    if frame is None:
        logger.error("Received None frame in draw_annotations")
        return None

    for obj in objects:
        try:
            bbox = obj["bbox"]
            display_label = obj.get("display_label")
            raw_label = obj["label"]
            conf = obj.get("confidence", 0.0)
            
            if display_label:
                text = display_label
            else:
                text = f"{raw_label} {conf:.2f}"
            
            left = int(bbox["left"])
            top = int(bbox["top"])
            right = left + int(bbox["width"])
            bottom = top + int(bbox["height"])
            
            # Basic validation to avoid OpenCV crashes
            if left < 0 or top < 0 or right > frame.shape[1] or bottom > frame.shape[0]:
                logger.warning(f"BBox out of bounds for {raw_label}: ({left}, {top}, {right}, {bottom}) | Frame: {frame.shape}")
                # Clamp coordinates
                left = max(0, left)
                top = max(0, top)
                right = min(frame.shape[1], right)
                bottom = min(frame.shape[0], bottom)

            # Draw Box
            color = (0, 255, 0) # Default Green
            if raw_label.lower() in ["fire", "smoke"]:
                color = (0, 0, 255) # Red for Fire
            elif raw_label.lower() in ["violence"]:
                color = (255, 0, 0) # Blue/Red for Violence? Let's use Red for violence too.
                color = (0, 0, 255)
            
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            
            # Draw Label with Background
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            thickness = 2
            (text_w, text_h), _ = cv2.getTextSize(text, font, font_scale, thickness)
            
            # Background Rect
            cv2.rectangle(frame, (left, top - 25), (left + text_w, top), color, -1)
            # Text
            cv2.putText(frame, text, (left, top - 7), font, font_scale, (255, 255, 255), thickness)
        
        except Exception as e:
            logger.error(f"Failed to draw annotation for {obj.get('label', 'unknown')}: {e}")
            continue
            
    return frame
