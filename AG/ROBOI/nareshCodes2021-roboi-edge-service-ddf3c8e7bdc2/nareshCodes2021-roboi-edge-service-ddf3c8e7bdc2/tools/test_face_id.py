import sys
import os
import cv2
import argparse

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.face_recognizer import RoboFaceID

def main():
    parser = argparse.ArgumentParser(description="Test Face Recognition on a static image.")
    parser.add_argument("image_path", help="Path to the image to test")
    parser.add_argument("--threshold", type=float, default=0.5, help="Recognition threshold (default: 0.5)")
    args = parser.parse_args()

    if not os.path.exists(args.image_path):
        print(f"Error: Image not found at {args.image_path}")
        return

    # Initialize Engine
    print("Initializing RoboFaceID engine...")
    face_id = RoboFaceID()
    
    # Load Image
    img = cv2.imread(args.image_path)
    if img is None:
        print(f"Error: Could not read image {args.image_path}")
        return

    print(f"Processing image: {args.image_path}")
    
    # In a real scenario, we'd use YOLO to get the face bbox.
    # For this test script, we'll let InsightFace detect faces in the whole image first
    # and then try to recognize them.
    
    # We use face_id.app.get directly for detection since this is a test script
    faces = face_id.app.get(img)
    print(f"Detected {len(faces)} face(s).")

    for i, face in enumerate(faces):
        bbox = face.bbox.astype(int)
        print(f"\nFace {i+1}:")
        print(f"  BBox: {bbox}")
        print(f"  Detection Confidence: {face.det_score:.4f}")
        
        # Call the actual recognize method we use in the runner
        name, sim = face_id.recognize(img, bbox, 1, threshold=args.threshold)
        
        print(f"  Result: {name}")
        print(f"  Similarity Score: {sim:.4f}")
        
        # Draw on the image
        color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
        cv2.rectangle(img, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
        label = f"{name} ({sim:.2f})"
        cv2.putText(img, label, (bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Save output
    out_path = "face_test_result.jpg"
    cv2.imwrite(out_path, img)
    print(f"\nResult saved to {out_path}")

if __name__ == "__main__":
    main()
