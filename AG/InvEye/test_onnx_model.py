"""
Test YOLO ONNX Model on CPU
============================
This script converts a .pt file to ONNX and tests it on your CPU system.
No GPU required!

Usage:
    python test_onnx_model.py --model path/to/best.pt --image path/to/test.jpg
    python test_onnx_model.py --model path/to/model.onnx --image path/to/test.jpg
    python test_onnx_model.py --model path/to/best.pt --video path/to/video.mp4
"""

import argparse
import os
import cv2
from pathlib import Path

def install_dependencies():
    """Install required packages if not present."""
    try:
        from ultralytics import YOLO
    except ImportError:
        print("Installing ultralytics...")
        os.system("pip install ultralytics")
    
    try:
        import onnxruntime
    except ImportError:
        print("Installing onnxruntime (CPU version)...")
        os.system("pip install onnxruntime")


def convert_pt_to_onnx(pt_path):
    """Convert .pt model to ONNX format."""
    from ultralytics import YOLO
    
    print(f"\n📦 Loading model: {pt_path}")
    model = YOLO(pt_path)
    
    print("🔄 Converting to ONNX (this may take a minute)...")
    onnx_path = model.export(format='onnx', imgsz=640, opset=12, simplify=True)
    
    print(f"✅ ONNX model saved: {onnx_path}")
    return onnx_path


def test_on_image(model_path, image_path, conf=0.5):
    """Test model on a single image."""
    from ultralytics import YOLO
    
    print(f"\n🖼️ Testing on image: {image_path}")
    
    # Load model (works with both .pt and .onnx)
    model = YOLO(model_path)
    
    # Run inference
    results = model.predict(
        source=image_path,
        conf=conf,
        save=True,
        save_txt=True,
        project='runs/detect',
        name='test_results'
    )
    
    # Print results
    print("\n📊 Detection Results:")
    print("-" * 50)
    
    for r in results:
        if len(r.boxes) == 0:
            print("No objects detected.")
        else:
            for box in r.boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                label = r.names[cls]
                print(f"  • {label}: {conf:.2%}")
    
    print(f"\n💾 Results saved to: runs/detect/test_results/")
    
    # Show image if possible
    try:
        annotated = results[0].plot()
        cv2.imshow('Detection Result', annotated)
        print("Press any key to close the image window...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    except Exception as e:
        print(f"Could not display image: {e}")


def test_on_video(model_path, video_path, conf=0.5):
    """Test model on a video file."""
    from ultralytics import YOLO
    
    print(f"\n🎬 Testing on video: {video_path}")
    
    model = YOLO(model_path)
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return
    
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"Video: {fps} FPS, {total_frames} frames")
    print("Press 'q' to quit...")
    
    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Run inference
        results = model.predict(frame, conf=conf, verbose=False)
        
        # Draw results
        annotated = results[0].plot()
        
        # Add frame info
        cv2.putText(annotated, f"Frame: {frame_count}/{total_frames}", 
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.imshow('Video Detection', annotated)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print(f"✅ Processed {frame_count} frames")


def test_on_webcam(model_path, conf=0.5):
    """Test model on webcam feed."""
    from ultralytics import YOLO
    
    print("\n📷 Testing on webcam...")
    print("Press 'q' to quit...")
    
    model = YOLO(model_path)
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        results = model.predict(frame, conf=conf, verbose=False)
        annotated = results[0].plot()
        
        cv2.imshow('Webcam Detection', annotated)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(description='Test YOLO model (PT or ONNX) on CPU')
    parser.add_argument('--model', type=str, required=True, help='Path to .pt or .onnx model')
    parser.add_argument('--image', type=str, help='Path to test image')
    parser.add_argument('--video', type=str, help='Path to test video')
    parser.add_argument('--webcam', action='store_true', help='Test on webcam')
    parser.add_argument('--conf', type=float, default=0.5, help='Confidence threshold (default: 0.5)')
    parser.add_argument('--convert-only', action='store_true', help='Only convert PT to ONNX, no testing')
    
    args = parser.parse_args()
    
    # Install dependencies
    install_dependencies()
    
    model_path = args.model
    
    # Check if model exists
    if not os.path.exists(model_path):
        print(f"❌ Error: Model not found: {model_path}")
        return
    
    # Convert PT to ONNX if needed
    if model_path.endswith('.pt'):
        onnx_path = convert_pt_to_onnx(model_path)
        if args.convert_only:
            print("\n✅ Conversion complete. ONNX model ready for deployment.")
            return
        # Use ONNX for testing (faster on CPU)
        model_path = onnx_path
    
    # Run tests
    if args.image:
        test_on_image(model_path, args.image, args.conf)
    elif args.video:
        test_on_video(model_path, args.video, args.conf)
    elif args.webcam:
        test_on_webcam(model_path, args.conf)
    else:
        print("\n⚠️ No test source specified. Use --image, --video, or --webcam")
        print("\nExamples:")
        print("  python test_onnx_model.py --model best.pt --image test.jpg")
        print("  python test_onnx_model.py --model best.onnx --video video.mp4")
        print("  python test_onnx_model.py --model best.pt --webcam")
        print("  python test_onnx_model.py --model best.pt --convert-only")


if __name__ == '__main__':
    main()
