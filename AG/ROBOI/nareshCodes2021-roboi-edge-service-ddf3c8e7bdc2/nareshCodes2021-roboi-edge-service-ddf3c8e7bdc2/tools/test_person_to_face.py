import sys
import os
import cv2
import numpy as np

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.face_recognizer import RoboFaceID

def main():
    # Initialize Engine
    print("Initializing RoboFaceID engine...")
    face_id = RoboFaceID()
    
    # Use one of the reference images
    image_path = "data/faces/sampad.jpg"
    if not os.path.exists(image_path):
        print(f"Error: Image not found at {image_path}")
        return

    img = cv2.imread(image_path)
    h, w = img.shape[:2]
    
    print(f"Testing with image: {image_path} ({w}x{h})")
    
    # Simulate a "person" bbox that covers the whole image
    # In reality, YOLO would give something like [left, top, right, bottom]
    person_bbox = [0, 0, w, h]
    
    print(f"Simulating 'person' detection with bbox: {person_bbox}")
    
    # Recognize
    name, sim, r_id = face_id.recognize(img, person_bbox, 1)
    
    print(f"\nResult:")
    print(f"  Identity: {name}")
    print(f"  ID: {r_id}")
    print(f"  Confidence: {sim:.4f}")
    
    if name != "Unknown":
        print("SUCCESS: Face recognized within person bounding box!")
    else:
        print("FAILURE: Face not recognized. Check logs.")

if __name__ == "__main__":
    main()
