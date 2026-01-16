#!/usr/bin/env python3
"""
Face Registration Tool
======================

Register employee faces into the database for recognition.

Usage:
    # Register from image file
    python register_faces.py --person "John Doe" --image photo.jpg
    
    # Register from webcam
    python register_faces.py --person "Jane Doe" --webcam
    
    # Bulk register from folder
    python register_faces.py --folder employees/
    
    # List registered faces
    python register_faces.py --list
"""

import os
import sys
import argparse
import cv2
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from main_pipeline import ModelManager, FaceDatabase


def register_from_image(model_manager: ModelManager, face_db: FaceDatabase, 
                        person_id: str, image_path: str) -> bool:
    """Register face from image file."""
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return False
    
    frame = cv2.imread(image_path)
    if frame is None:
        print(f"❌ Failed to load image: {image_path}")
        return False
    
    print(f"📷 Processing image: {image_path}")
    
    # Detect faces
    faces = model_manager.detect_faces(frame, conf=0.5)
    
    if not faces:
        print(f"❌ No face detected in image")
        return False
    
    if len(faces) > 1:
        print(f"⚠️ Multiple faces detected ({len(faces)}), using largest face")
    
    # Use largest face
    largest_face = max(faces, key=lambda f: (f.bbox[2]-f.bbox[0]) * (f.bbox[3]-f.bbox[1]))
    
    # Get embedding
    embedding = model_manager.recognize_face(frame, largest_face.bbox)
    
    if embedding is None:
        print(f"❌ Failed to extract face embedding")
        return False
    
    # Save to database
    face_db.add_face(person_id, embedding, {
        'source': image_path,
        'registered_at': time.strftime('%Y-%m-%d %H:%M:%S')
    })
    
    print(f"✅ Registered: {person_id}")
    return True


def register_from_webcam(model_manager: ModelManager, face_db: FaceDatabase,
                         person_id: str, camera_index: int = 0) -> bool:
    """Register face from webcam capture."""
    
    cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        print(f"❌ Failed to open webcam {camera_index}")
        return False
    
    print(f"📹 Webcam opened. Press SPACE to capture, Q to quit")
    
    registered = False
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect faces for preview
        faces = model_manager.detect_faces(frame, conf=0.5)
        
        display_frame = frame.copy()
        
        for face in faces:
            x1, y1, x2, y2 = face.bbox
            cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # Instructions
        cv2.putText(display_frame, f"Registering: {person_id}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(display_frame, "SPACE: Capture | Q: Quit", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        if faces:
            cv2.putText(display_frame, f"Faces detected: {len(faces)}", (10, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        else:
            cv2.putText(display_frame, "No face detected", (10, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        cv2.imshow("Face Registration", display_frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord(' ') and faces:
            # Capture and register
            largest_face = max(faces, key=lambda f: (f.bbox[2]-f.bbox[0]) * (f.bbox[3]-f.bbox[1]))
            embedding = model_manager.recognize_face(frame, largest_face.bbox)
            
            if embedding is not None:
                face_db.add_face(person_id, embedding, {
                    'source': 'webcam',
                    'registered_at': time.strftime('%Y-%m-%d %H:%M:%S')
                })
                print(f"✅ Registered: {person_id}")
                registered = True
                break
            else:
                print("❌ Failed to extract embedding, try again")
        
        elif key == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    return registered


def register_from_folder(model_manager: ModelManager, face_db: FaceDatabase,
                         folder_path: str) -> int:
    """Bulk register faces from folder.
    
    Expected folder structure:
        folder/
            person1/
                photo1.jpg
                photo2.jpg
            person2/
                photo.jpg
    """
    
    folder = Path(folder_path)
    if not folder.exists():
        print(f"❌ Folder not found: {folder_path}")
        return 0
    
    registered_count = 0
    
    for person_dir in folder.iterdir():
        if not person_dir.is_dir():
            # Single image file - use filename as person ID
            if person_dir.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                person_id = person_dir.stem
                if register_from_image(model_manager, face_db, person_id, str(person_dir)):
                    registered_count += 1
            continue
        
        person_id = person_dir.name
        
        # Get first valid image in person's folder
        for image_file in person_dir.iterdir():
            if image_file.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                if register_from_image(model_manager, face_db, person_id, str(image_file)):
                    registered_count += 1
                    break  # Only use first image per person
    
    return registered_count


def list_registered_faces(face_db: FaceDatabase):
    """List all registered faces."""
    
    persons = face_db.get_all_persons()
    
    if not persons:
        print("📋 No faces registered")
        return
    
    print(f"\n📋 Registered Faces ({len(persons)} total):")
    print("="*50)
    
    for person_id in sorted(persons):
        meta = face_db.metadata.get(person_id, {})
        registered_at = meta.get('registered_at', 'Unknown')
        source = meta.get('source', 'Unknown')
        print(f"  👤 {person_id}")
        print(f"     Registered: {registered_at}")
        print(f"     Source: {source}")
        print()


def main():
    parser = argparse.ArgumentParser(description='Face Registration Tool')
    
    parser.add_argument('--person', type=str, help='Person ID/name to register')
    parser.add_argument('--image', type=str, help='Image file path')
    parser.add_argument('--webcam', action='store_true', help='Capture from webcam')
    parser.add_argument('--camera', type=int, default=0, help='Webcam index')
    parser.add_argument('--folder', type=str, help='Folder for bulk registration')
    parser.add_argument('--list', action='store_true', help='List registered faces')
    parser.add_argument('--delete', type=str, help='Delete a registered face')
    parser.add_argument('--db-path', type=str, default='face_database', help='Face database path')
    
    args = parser.parse_args()
    
    # Initialize
    config = {
        'device': 'cuda:0',
        'face_detection_model': 'models/yolov11n-face.pt',
        'recognition_model': 'buffalo_sc'
    }
    
    model_manager = ModelManager(config)
    face_db = FaceDatabase(args.db_path)
    
    # Handle commands
    if args.list:
        list_registered_faces(face_db)
        return
    
    if args.delete:
        if args.delete in face_db.embeddings:
            del face_db.embeddings[args.delete]
            if args.delete in face_db.metadata:
                del face_db.metadata[args.delete]
            face_db.save_database()
            print(f"✅ Deleted: {args.delete}")
        else:
            print(f"❌ Not found: {args.delete}")
        return
    
    if args.folder:
        count = register_from_folder(model_manager, face_db, args.folder)
        print(f"\n✅ Registered {count} faces from folder")
        return
    
    if args.person:
        if args.webcam:
            register_from_webcam(model_manager, face_db, args.person, args.camera)
        elif args.image:
            register_from_image(model_manager, face_db, args.person, args.image)
        else:
            print("❌ Specify --image or --webcam")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
