import os
import cv2
import numpy as np
import face_recognition
from core.logger import get_app_logger

logger = get_app_logger("face-id")

class RoboFaceID:
    def __init__(self, model_root=None):
        """
        Initializes the face_recognition engine using dlib.
        """
        logger.info("Initializing Dlib-based Face Recognition Engine")
        
        self.face_db = []
        self.load_database()

    def load_database(self, faces_path="data/faces"):
        """
        Loads reference images and generates face encodings.
        """
        if not os.path.exists(faces_path):
            logger.warning(f"Faces database path not found: {faces_path}")
            return

        # Sort filenames for consistent ID assignment
        files = sorted([f for f in os.listdir(faces_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        
        seen_names = {}
        next_id = 1

        for filename in files:
            name = os.path.splitext(filename)[0].lower()
            if name not in seen_names:
                seen_names[name] = next_id
                next_id += 1
            
            p_id = seen_names[name]
            img_path = os.path.join(faces_path, filename)
            
            try:
                # Load image with face_recognition (it uses PIL/RGB)
                img = face_recognition.load_image_file(img_path)
                encodings = face_recognition.face_encodings(img)
                
                if len(encodings) > 0:
                    # Take the first face encoding found
                    self.face_db.append({
                        "name": name,
                        "id": p_id,
                        "encoding": encodings[0]
                    })
                    logger.info(f"Registered (Dlib): {name} (ID: {p_id})")
                else:
                    logger.warning(f"No face in {img_path}. Skipping.")
            except Exception as e:
                logger.error(f"Failed to process {img_path}: {e}")

    def recognize(self, frame, bbox, frame_id, threshold=0.6):
        """
        Recognizes a face by cropping the provided bbox area first.
        Optimized for Dlib/Face Recognition.
        """
        try:
            h, w, _ = frame.shape
            x1, y1, x2, y2 = map(int, bbox)
            
            # --- 1. Optimized Square Cropping (Same logic as before for consistency) ---
            bw = x2 - x1
            bh = y2 - y1
            head_cx = x1 + (bw / 2)
            head_cy = y1 + (bh * 0.15)
            
            square_size = int(max(bw * 1.5, bh * 0.6)) # Slightly wider for dlib
            
            cx1 = int(head_cx - (square_size / 2))
            cy1 = int(head_cy - (square_size * 0.45))
            cx2 = cx1 + square_size
            cy2 = cy1 + square_size
            
            # Clamp to image bounds
            cx1, cy1 = max(0, cx1), max(0, cy1)
            cx2, cy2 = min(w, cx2), min(h, cy2)
            
            person_crop = frame[cy1:cy2, cx1:cx2]
            
            if person_crop.size == 0 or person_crop.shape[0] < 20 or person_crop.shape[1] < 20:
                return "Stranger", 1.0, 0

            # --- 2. Run Face Recognition on the CROP ---
            # face_recognition expects RGB
            rgb_crop = cv2.cvtColor(person_crop, cv2.COLOR_BGR2RGB)
            
            # Get encodings for the crop (assuming one face)
            face_encodings = face_recognition.face_encodings(rgb_crop)
            
            if not face_encodings:
                # Fallback to whole body in case head was cut off too much
                body_crop = frame[max(0, y1):min(h, y2), max(0, x1):min(w, x2)]
                rgb_body = cv2.cvtColor(body_crop, cv2.COLOR_BGR2RGB)
                face_encodings = face_recognition.face_encodings(rgb_body)

            if not face_encodings:
                return "Stranger", 1.0, 0

            target_encoding = face_encodings[0]
            
            # Match
            known_encodings = [f["encoding"] for f in self.face_db]
            if not known_encodings:
                return "Stranger", 1.0, 0

            # Calculate distances
            face_distances = face_recognition.face_distance(known_encodings, target_encoding)
            best_match_index = np.argmin(face_distances)
            min_dist = face_distances[best_match_index]
            
            # Confidence for dlib is often 1 - distance (heuristic)
            confidence = 1.0 - min_dist
            
            # Threshold: face_recognition distance of 0.6 is common (lower is better)
            # Our threshold parameter is a 'confidence' threshold, so:
            if confidence >= threshold:
                best_match = self.face_db[best_match_index]
                name = best_match["name"]
                p_id = best_match["id"]
                logger.info(f"Dlib Match: {name} | Score={confidence:.4f}")
                return name, float(confidence), p_id
            
            logger.info(f"Dlib No Match | BestCandidateScore={confidence:.4f}")
            return "Stranger", 1.0, 0

        except Exception as e:
            logger.error(f"Dlib Recognition Error: {e}")
            return "Error", 0.0, -1