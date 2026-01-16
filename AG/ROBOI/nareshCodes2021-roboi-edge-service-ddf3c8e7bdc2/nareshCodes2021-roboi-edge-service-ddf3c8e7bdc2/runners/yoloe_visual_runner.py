"""
YOLOE Visual Prompt Runner
Uses visual prompts (bounding boxes) to teach the model what to detect.
"""
import cv2
import numpy as np
import argparse
import os
from ultralytics import YOLO
from ultralytics.models.yolo.yoloe import YOLOEVPSegPredictor

# Try to import PaddleOCR
try:
    from paddleocr import PaddleOCR
    PADDLE_AVAILABLE = True
except ImportError:
    PADDLE_AVAILABLE = False

def init_ocr():
    if not PADDLE_AVAILABLE:
        return None
    try:
        ocr = PaddleOCR(lang='en', use_doc_orientation_classify=False, use_doc_unwarping=False)
        return ocr
    except:
        return None

def read_license_plate(ocr, image, bbox, debug=False):
    if ocr is None:
        return None
    try:
        x1, y1, x2, y2 = map(int, bbox)
        pad = 15
        h, w = image.shape[:2]
        x1, y1 = max(0, x1 - pad), max(0, y1 - pad)
        x2, y2 = min(w, x2 + pad), min(h, y2 + pad)
        plate_img = image[y1:y2, x1:x2]
        
        if plate_img.size == 0:
            print("      Empty crop region")
            return None
        
        # Save debug image
        if debug:
            cv2.imwrite("debug_plate_crop.png", plate_img)
            print(f"      Debug: Saved plate crop to debug_plate_crop.png ({plate_img.shape})")
        
        # Preprocess for better OCR
        # 1. Resize to larger size
        scale = 2
        plate_img = cv2.resize(plate_img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        
        # 2. Convert to grayscale
        gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
        
        # 3. Apply adaptive threshold
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                       cv2.THRESH_BINARY, 11, 2)
        
        # 4. Convert back to BGR for PaddleOCR
        processed = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
        
        if debug:
            cv2.imwrite("debug_plate_processed.png", processed)
            print(f"      Debug: Saved processed plate to debug_plate_processed.png")
        
        # Try OCR on processed image
        result = ocr.ocr(processed)
        if result and result[0]:
            texts = [line[1][0] for line in result[0]]
            return " ".join(texts)
        
        # If processed fails, try original color
        result = ocr.ocr(plate_img)
        if result and result[0]:
            texts = [line[1][0] for line in result[0]]
            return " ".join(texts)
            
    except Exception as e:
        print(f"      OCR Error: {e}")
    return None

def main():
    parser = argparse.ArgumentParser(description="YOLOE Visual Prompt Runner")
    parser.add_argument("--source", type=str, required=True, help="Path to image")
    parser.add_argument("--model", type=str, default="yoloe-26s-seg.pt", help="YOLOE model")
    parser.add_argument("--output-dir", type=str, default="output_visual", help="Output directory")
    parser.add_argument("--show", action="store_true", help="Show result")
    parser.add_argument("--conf", type=float, default=0.15, help="Confidence threshold")
    
    # Visual prompt arguments
    parser.add_argument("--plate-box", type=str, default=None, 
                        help="License plate box: x1,y1,x2,y2 (e.g., '390,865,470,925')")
    parser.add_argument("--nozzle-box", type=str, default=None,
                        help="Nozzle box: x1,y1,x2,y2 (e.g., '485,540,570,600')")
    parser.add_argument("--draw-prompts", action="store_true",
                        help="Draw the visual prompt boxes on the image first to help you find coordinates")
    args = parser.parse_args()

    # Read image to get dimensions
    image = cv2.imread(args.source)
    if image is None:
        print(f"Error: Could not read image {args.source}")
        return
    
    h, w = image.shape[:2]
    print(f"Image size: {w}x{h}")

    # If user wants to see the image with grid to find coordinates
    if args.draw_prompts:
        print("\n=== DRAW MODE: Click on image corners to find coordinates ===")
        print("Look at the image and note the coordinates for license plate and nozzle")
        
        # Draw grid
        grid_img = image.copy()
        for x in range(0, w, 100):
            cv2.line(grid_img, (x, 0), (x, h), (128, 128, 128), 1)
            cv2.putText(grid_img, str(x), (x, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        for y in range(0, h, 100):
            cv2.line(grid_img, (0, y), (w, y), (128, 128, 128), 1)
            cv2.putText(grid_img, str(y), (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        cv2.imshow("Grid - Find Coordinates", grid_img)
        print("Press any key to close...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return

    # Build visual prompts
    bboxes = []
    cls_ids = []
    class_names = []
    
    if args.plate_box:
        coords = [float(x) for x in args.plate_box.split(',')]
        bboxes.append(coords)
        cls_ids.append(0)
        class_names.append("license_plate")
        print(f"Visual prompt: License plate at {coords}")
    
    if args.nozzle_box:
        coords = [float(x) for x in args.nozzle_box.split(',')]
        bboxes.append(coords)
        cls_ids.append(1)
        class_names.append("fuel_nozzle")
        print(f"Visual prompt: Fuel nozzle at {coords}")

    if not bboxes:
        print("Error: No visual prompts provided!")
        print("Use --plate-box and/or --nozzle-box to specify example locations")
        print("Use --draw-prompts to see a grid and find coordinates")
        return

    # Initialize OCR
    print("Initializing PaddleOCR...")
    ocr = init_ocr()
    if ocr:
        print("PaddleOCR ready!")

    # Load model
    print(f"\nLoading model: {args.model}")
    model = YOLO(args.model)

    # Create visual prompts
    visual_prompts = dict(
        bboxes=np.array(bboxes),
        cls=np.array(cls_ids),
    )
    print(f"\nRunning inference with {len(bboxes)} visual prompts...")

    # Run inference with visual prompts
    results = model.predict(
        args.source,
        visual_prompts=visual_prompts,
        predictor=YOLOEVPSegPredictor,
        conf=args.conf,
        verbose=False
    )

    result = results[0]
    annotated = result.plot()

    # Process detections
    plate_text = None
    if result.boxes is not None:
        print(f"\nDetected {len(result.boxes)} objects:")
        for i, box in enumerate(result.boxes):
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            bbox = box.xyxy[0].cpu().numpy()
            
            cls_name = class_names[cls_id] if cls_id < len(class_names) else f"class_{cls_id}"
            print(f"  [{i}] {cls_name}: {conf:.2f} at {bbox}")
            
            # OCR for license plates
            if cls_name == "license_plate" and ocr:
                # Try OCR on detected box
                text = read_license_plate(ocr, image, bbox, debug=True)
                if text:
                    plate_text = text
                    print(f"      📋 OCR (detected): {text}")
                    x1, y1 = int(bbox[0]), int(bbox[1])
                    cv2.putText(annotated, text, (x1, y1-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                else:
                    print(f"      ⚠️ OCR failed on detected box")
    
    # Also try OCR on the original prompt box (user-provided, may be more accurate)
    if args.plate_box and ocr and not plate_text:
        print("\n  Trying OCR on original prompt box...")
        coords = [float(x) for x in args.plate_box.split(',')]
        text = read_license_plate(ocr, image, coords, debug=True)
        if text:
            plate_text = text
            print(f"      📋 OCR (prompt box): {text}")
            x1, y1 = int(coords[0]), int(coords[1])
            cv2.putText(annotated, text, (x1, y1-15), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        else:
            print(f"      ⚠️ OCR also failed on prompt box")

    # Save output
    os.makedirs(args.output_dir, exist_ok=True)
    filename = os.path.basename(args.source)
    output_path = os.path.join(args.output_dir, f"vp_{filename}")
    cv2.imwrite(output_path, annotated)
    print(f"\nSaved to: {output_path}")

    # Show
    if args.show:
        cv2.imshow("Visual Prompt Detection", annotated)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    print("Done!")

if __name__ == "__main__":
    main()
