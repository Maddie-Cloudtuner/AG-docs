import cv2
import sys
import os
import argparse
from ultralytics import YOLO
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Simple Host Runner for YOLO on Images")
    parser.add_argument("--source", type=str, required=True, help="Path to input image file or directory")
    parser.add_argument("--model", type=str, default="models/exports/roboi_base_14012026.pt", help="Path to YOLO model")
    parser.add_argument("--output-dir", type=str, default="output_images", help="Directory to save labeled images")
    parser.add_argument("--conf", type=float, default=0.25, help="Confidence threshold")
    parser.add_argument("--show", action="store_true", help="Show image after processing")
    args = parser.parse_args()

    # Load Model
    print(f"Loading model: {args.model}")
    try:
        model = YOLO(args.model)
    except Exception as e:
        print(f"Error loading model: {e}")
        sys.exit(1)

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
            print(f"Processing: {img_path}")
            frame = cv2.imread(img_path)
            if frame is None:
                print(f"Warning: Could not read image {img_path}")
                continue

            # Inference
            results = model(frame, conf=args.conf, verbose=False)[0]

            # Draw
            annotated_frame = results.plot()

            # Save
            filename = os.path.basename(img_path)
            output_path = os.path.join(args.output_dir, f"labeled_{filename}")
            cv2.imwrite(output_path, annotated_frame)
            print(f"Saved to {output_path}")

            # Show
            if args.show:
                cv2.imshow("YOLO Image Detection", annotated_frame)
                key = cv2.waitKey(0) # Wait indefinitely for a key press
                if key & 0xFF == ord('q'):
                    print("Quitting display...")
                    args.show = False # Stop showing subsequent images
                
        except Exception as e:
            print(f"Error processing {img_path}: {e}")

    if args.show:
        cv2.destroyAllWindows()
    print("Done!")

if __name__ == "__main__":
    main()
