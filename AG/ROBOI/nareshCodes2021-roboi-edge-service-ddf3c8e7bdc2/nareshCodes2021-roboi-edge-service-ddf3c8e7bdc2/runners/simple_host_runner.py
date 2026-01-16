import cv2
import sys
import os
import argparse
from ultralytics import YOLO

def main():
    parser = argparse.ArgumentParser(description="Simple Host Runner for YOLO on Video")
    parser.add_argument("--video", type=str, required=True, help="Path to input video file")
    parser.add_argument("--model", type=str, default="models/exports/yolo11_finetuned.pt", help="Path to YOLO model")
    parser.add_argument("--output", type=str, default="output_labeled.mp4", help="Path to output video file")
    parser.add_argument("--conf", type=float, default=0.25, help="Confidence threshold")
    parser.add_argument("--start-time", type=str, default="0", help="Start time in MM:SS or SS format")
    parser.add_argument("--show", action="store_true", help="Show video while processing")
    parser.add_argument("--width", type=int, default=1920, help="Output video width")
    parser.add_argument("--height", type=int, default=1080, help="Output video height")
    parser.add_argument("--fps", type=float, default=30.0, help="Output video FPS")
    args = parser.parse_args()

    # Check input file
    if not os.path.exists(args.video):
        print(f"Error: Video file not found: {args.video}")
        sys.exit(1)

    # Load Model
    print(f"Loading model: {args.model}")
    try:
        model = YOLO(args.model)
    except Exception as e:
        print(f"Error loading model: {e}")
        sys.exit(1)

    # Open Video
    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        print("Error: Could not open video.")
        sys.exit(1)

    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"Processing {args.video} ({width}x{height} @ {fps}fps)")

    # Seek to start time
    start_seconds = 0
    try:
        if ":" in args.start_time:
            parts = args.start_time.split(":")
            start_seconds = int(parts[0]) * 60 + int(parts[1])
        else:
            start_seconds = int(args.start_time)
    except ValueError:
        print("Error: Invalid time format. Use MM:SS or SS.")
        sys.exit(1)

    if start_seconds > 0:
        print(f"Seeking to {start_seconds} seconds...")
        cap.set(cv2.CAP_PROP_POS_MSEC, start_seconds * 1000)

    # Setup Writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(args.output, fourcc, args.fps, (args.width, args.height))

    frame_count = 0
    
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Resize
            frame = cv2.resize(frame, (args.width, args.height))

            frame_count += 1
            if frame_count % 50 == 0:
                print(f"Processing frame {frame_count}/{total_frames}...")

            # Inference
            results = model(frame, conf=args.conf, verbose=False)[0]

            # Draw
            annotated_frame = results.plot()

            # Show
            if args.show:
                cv2.imshow("YOLO Processing", annotated_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            # Write
            out.write(annotated_frame)

    except KeyboardInterrupt:
        print("Interrupted by user.")
    except Exception as e:
        print(f"Error during processing: {e}")
    finally:
        cap.release()
        out.release()
        if args.show:
            cv2.destroyAllWindows()
        print(f"Done! Saved to {args.output}")

if __name__ == "__main__":
    main()
