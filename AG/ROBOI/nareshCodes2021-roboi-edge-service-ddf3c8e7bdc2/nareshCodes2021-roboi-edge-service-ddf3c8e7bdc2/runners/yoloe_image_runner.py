import cv2
import sys
import os
import argparse
from ultralytics import YOLO
from pathlib import Path

# Try to import PaddleOCR
try:
    from paddleocr import PaddleOCR
    PADDLE_AVAILABLE = True
except ImportError:
    PADDLE_AVAILABLE = False
    print("Warning: PaddleOCR not installed. License plate OCR disabled.")
    print("Install with: pip install paddlepaddle paddleocr")

# Default classes for YOLOE (natural language prompts)
# Use descriptive phrases that the AI model can understand
YOLOE_CLASSES = [
    # Vehicles
    "person", "car", "truck", "bus", "motorcycle", "bicycle", "auto rickshaw", "scooter",
    # License plate detection - multiple variations for better detection
    "license plate", "number plate", "vehicle registration plate",
    "motorcycle license plate", "car number plate", "vehicle plate",
    "Indian license plate", "registration number plate",
    # Petrol pump specific
    "fuel nozzle", "petrol pump nozzle", "gas pump handle", "fuel dispenser",
    "petrol pump", "gas station pump", "fuel pump",
    # Safety
    "fire", "smoke", "cigarette", "fire extinguisher",
    # Common objects
    "cell phone", "mobile phone", "bottle", "backpack", "handbag",
    "face", "helmet", "safety vest"
]

# Your custom model class names (for reference)
CUSTOM_MODEL_CLASSES = [
    "person", "bicycle", "car", "motorcycle", "bus", "truck",
    "fire hydrant", "dog", "backpack", "handbag", "suitcase",
    "bottle", "knife", "chair", "toilet", "tv",
    "cell phone", "clock", "scissors",
    "fire", "smoke", "cigarette",
    "du_nozzle", "license_plate", "container", "face"
]

def init_ocr():
    """Initialize PaddleOCR for license plate reading"""
    if not PADDLE_AVAILABLE:
        return None
    try:
        # Updated for PaddleOCR 3.x - removed deprecated parameters
        ocr = PaddleOCR(lang='en', use_doc_orientation_classify=False, use_doc_unwarping=False)
        return ocr
    except Exception as e:
        print(f"Warning: Could not initialize PaddleOCR: {e}")
        return None

def read_license_plate(ocr, image, bbox):
    """Extract and read license plate text from bounding box"""
    if ocr is None:
        return None
    
    try:
        x1, y1, x2, y2 = map(int, bbox)
        # Add padding
        pad = 5
        h, w = image.shape[:2]
        x1 = max(0, x1 - pad)
        y1 = max(0, y1 - pad)
        x2 = min(w, x2 + pad)
        y2 = min(h, y2 + pad)
        
        # Crop license plate region
        plate_img = image[y1:y2, x1:x2]
        
        if plate_img.size == 0:
            return None
        
        # Run OCR
        result = ocr.ocr(plate_img, cls=True)
        
        if result and result[0]:
            texts = [line[1][0] for line in result[0]]
            return " ".join(texts)
        return None
    except Exception as e:
        return None

def is_yoloe_model(model_path):
    """Check if the model is a YOLOE model"""
    return "yoloe" in model_path.lower()

def main():
    parser = argparse.ArgumentParser(description="YOLO/YOLOE Runner with License Plate OCR")
    parser.add_argument("--source", type=str, required=True, help="Path to input image file or directory")
    parser.add_argument("--model", type=str, default="yoloe-26s-seg.pt", 
                        help="Model path. Use 'yoloe-26s-seg.pt' for YOLOE or your custom .pt file")
    parser.add_argument("--output-dir", type=str, default="output_yoloe", help="Directory to save labeled images")
    parser.add_argument("--conf", type=float, default=0.25, help="Confidence threshold")
    parser.add_argument("--show", action="store_true", help="Show image after processing")
    parser.add_argument("--classes", type=str, nargs='+', default=None, 
                        help="Classes to detect (only for YOLOE models)")
    parser.add_argument("--no-ocr", action="store_true", help="Disable license plate OCR")
    parser.add_argument("--verbose", action="store_true", help="Print ALL detected objects")
    args = parser.parse_args()

    # Initialize OCR if not disabled
    ocr = None
    if not args.no_ocr:
        print("Initializing PaddleOCR for license plate reading...")
        ocr = init_ocr()
        if ocr:
            print("PaddleOCR initialized successfully!")

    # Load Model
    print(f"Loading model: {args.model}")
    try:
        model = YOLO(args.model)
    except Exception as e:
        print(f"Error loading model: {e}")
        sys.exit(1)

    # Set text prompts for YOLOE models only
    use_yoloe = is_yoloe_model(args.model)
    if use_yoloe:
        classes = args.classes if args.classes else YOLOE_CLASSES
        print(f"YOLOE mode: Setting {len(classes)} classes to detect")
        model.set_classes(classes, model.get_text_pe(classes))
        # Map class names for OCR detection - include all variations
        license_classes = [
            "license plate", "number plate", "vehicle registration plate",
            "motorcycle license plate", "car number plate", "vehicle plate",
            "indian license plate", "registration number plate"
        ]
        nozzle_classes = [
            "fuel nozzle", "petrol pump nozzle", "gas pump handle", 
            "fuel dispenser", "petrol pump", "gas station pump", "fuel pump"
        ]
    else:
        print(f"Custom model mode: Using model's built-in classes")
        # For custom model, use your label indices
        license_classes = ["license_plate"]  # class 23 in your model
        nozzle_classes = ["du_nozzle"]  # class 22 in your model

    # Prepare input images
    images = []
    if os.path.isdir(args.source):
        for file in os.listdir(args.source):
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                images.append(os.path.join(args.source, file))
    elif os.path.isfile(args.source):
        images.append(args.source)
    else:
        print(f"Error: Source not found: {args.source}")
        sys.exit(1)

    if not images:
        print("No images found to process.")
        sys.exit(0)

    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)

    print(f"Processing {len(images)} images...")

    for img_path in images:
        try:
            print(f"\nProcessing: {img_path}")
            frame = cv2.imread(img_path)
            if frame is None:
                print(f"Warning: Could not read image {img_path}")
                continue

            # Inference
            results = model(frame, conf=args.conf, verbose=False)[0]

            # Process detections
            detected_plates = []
            detected_nozzles = []
            
            if results.boxes is not None and len(results.boxes) > 0:
                print(f"  Found {len(results.boxes)} detections:")
                for i, box in enumerate(results.boxes):
                    cls_id = int(box.cls[0])
                    cls_name = results.names[cls_id]
                    conf = float(box.conf[0])
                    bbox = box.xyxy[0].cpu().numpy()
                    
                    # Print ALL detections if verbose
                    if args.verbose:
                        print(f"    [{i}] {cls_name}: {conf:.2f}")
                    
                    # Check for license plates
                    if cls_name.lower() in [c.lower() for c in license_classes]:
                        plate_text = read_license_plate(ocr, frame, bbox) if ocr else None
                        detected_plates.append({
                            "bbox": bbox,
                            "confidence": conf,
                            "text": plate_text
                        })
                        if plate_text:
                            print(f"  📋 License Plate: {plate_text} (conf: {conf:.2f})")
                        else:
                            print(f"  📋 License Plate detected (conf: {conf:.2f}) - OCR failed")
                    
                    # Check for nozzles
                    if cls_name.lower() in [c.lower() for c in nozzle_classes]:
                        detected_nozzles.append({
                            "bbox": bbox,
                            "confidence": conf
                        })
                        print(f"  ⛽ Fuel Nozzle detected (conf: {conf:.2f})")

            # Draw annotations
            annotated_frame = results.plot()
            
            # Add OCR text overlay for license plates
            for plate in detected_plates:
                if plate["text"]:
                    x1, y1, x2, y2 = map(int, plate["bbox"])
                    # Draw text above the plate
                    cv2.putText(annotated_frame, plate["text"], 
                               (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                               0.7, (0, 255, 0), 2)

            # Save
            filename = os.path.basename(img_path)
            output_path = os.path.join(args.output_dir, f"detected_{filename}")
            cv2.imwrite(output_path, annotated_frame)
            print(f"  Saved to {output_path}")

            # Summary
            total_objects = len(results.boxes) if results.boxes is not None else 0
            print(f"  Summary: {total_objects} objects, {len(detected_plates)} plates, {len(detected_nozzles)} nozzles")

            # Show
            if args.show:
                cv2.imshow("Detection Results", annotated_frame)
                key = cv2.waitKey(0)
                if key & 0xFF == ord('q'):
                    print("Quitting display...")
                    args.show = False
                
        except Exception as e:
            print(f"Error processing {img_path}: {e}")
            import traceback
            traceback.print_exc()

    if args.show:
        cv2.destroyAllWindows()
    print("\nDone!")

if __name__ == "__main__":
    main()
