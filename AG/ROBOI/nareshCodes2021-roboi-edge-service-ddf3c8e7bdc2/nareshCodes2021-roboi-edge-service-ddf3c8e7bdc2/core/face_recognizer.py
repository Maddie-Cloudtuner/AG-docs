import os
import cv2
import numpy as np
from core.logger import get_app_logger

logger = get_app_logger("face-id")

class RoboFaceID:
    def __init__(self, 
                 detector_path="models/face/face_detection_yunet.onnx",
                 recognizer_path="models/face/face_recognition_sface.onnx",
                 score_threshold=0.6):
        """
        Initializes YuNet Detector and SFace Recognizer (OpenCV Zoo).
        """
        logger.info(f"Initializing YuNet+SFace Engine (DetThresh: {score_threshold})...")
        
        self.face_db = []
        
        # 1. Initialize Detector (YuNet)
        if os.path.exists(detector_path):
            try:
                # YuNet parameters: score_threshold, nms_threshold, top_k
                self.detector = cv2.FaceDetectorYN.create(
                    detector_path, "", (320, 320), 
                    score_threshold=score_threshold, 
                    nms_threshold=0.3,
                    top_k=5000
                )
                
                # Try to enable CUDA
                try:
                    self.detector.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
                    self.detector.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
                    logger.info("YuNet: CUDA Backend Enabled")
                except Exception:
                    logger.warning("YuNet: CUDA not available, using CPU")
            except Exception as e:
                logger.error(f"Failed to initialize YuNet: {e}")
                self.detector = None
        else:
            logger.error(f"YuNet model not found at {detector_path}")
            self.detector = None

        # 2. Initialize Recognizer (SFace)
        if os.path.exists(recognizer_path):
            try:
                self.recognizer = cv2.FaceRecognizerSF.create(recognizer_path, "")
                
                # Try to enable CUDA
                try:
                    self.recognizer.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
                    self.recognizer.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
                    logger.info("SFace: CUDA Backend Enabled")
                except Exception:
                    logger.warning("SFace: CUDA not available, using CPU")
            except Exception as e:
                logger.error(f"Failed to initialize SFace: {e}")
                self.recognizer = None
        else:
            logger.error(f"SFace model not found at {recognizer_path}")
            self.recognizer = None

        self.load_database()

    def load_database(self, faces_path="data/faces"):
        """
        Loads reference images and generates embeddings using YuNet+SFace.
        """
        if not self.detector or not self.recognizer:
            logger.error("Detector or Recognizer not initialized. Registration skipped.")
            return

        if not os.path.exists(faces_path):
            logger.warning(f"Faces database path not found: {faces_path}")
            return

        files = sorted([f for f in os.listdir(faces_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        logger.info(f"Found {len(files)} potential face files in {faces_path}")
        
        seen_names = {}
        next_id = 1

        for filename in files:
            name = os.path.splitext(filename)[0].lower()
            if name not in seen_names:
                seen_names[name] = next_id
                next_id += 1
            
            p_id = seen_names[name]
            img_path = os.path.join(faces_path, filename)
            img = cv2.imread(img_path)
            
            if img is None:
                logger.warning(f"Failed to read image: {img_path}")
                continue
                
            embedding = self._get_embedding(img)
            if embedding is not None:
                self.face_db.append({
                    "name": name,
                    "id": p_id,
                    "embedding": embedding
                })
                logger.info(f"Registered (SFace): {name} (ID: {p_id})")
            else:
                logger.warning(f"Could not extract embedding for registration: {filename}")

    def _get_embedding(self, face_img, target_score_thresh=None):
        """
        Detects, aligns, and extracts SFace embedding.
        Now includes multi-scale retry and detailed diagnostic logging.
        """
        if not self.detector or not self.recognizer:
            return None
            
        try:
            h, w = face_img.shape[:2]
            if w == 0 or h == 0:
                return None

            # Default to current detector threshold if not provided
            if target_score_thresh is None:
                target_score_thresh = self.detector.getScoreThreshold()
            
            # --- Robust Detection Strategy ---
            # We try the original scale, then a standard 640-scale fallback
            scales_to_try = [(w, h)]
            if max(w, h) < 320 or max(w, h) > 1000:
                scales_to_try.append((640, int(640 * h / w)) if w >= h else (int(640 * w / h), 640))
            
            best_face = None
            max_conf_found = 0.0
            best_img_for_align = face_img

            for sw, sh in scales_to_try:
                # 1. Prepare Image
                if (sw, sh) != (w, h):
                    test_img = cv2.resize(face_img, (sw, sh))
                else:
                    test_img = face_img
                
                self.detector.setInputSize((sw, sh))
                
                # Temporarily lower threshold to 0.1 to see "what was missed"
                orig_thresh = self.detector.getScoreThreshold()
                self.detector.setScoreThreshold(0.1) 
                
                _, faces = self.detector.detect(test_img)
                self.detector.setScoreThreshold(orig_thresh) # Restore immediately

                if faces is not None:
                    for f in faces:
                        conf = float(f[14])
                        if conf > max_conf_found:
                            max_conf_found = conf
                        
                        # Use the face if it passes the REAL intended threshold
                        if conf >= target_score_thresh:
                            # If we scaled the image, we must scale the face coordinates back or 
                            # just use the current test_img for alignment (easier)
                            best_face = f
                            best_img_for_align = test_img
                            break
                
                if best_face is not None:
                    break

            # Diagnostics for failures
            if best_face is None:
                logger.info("No Face Recognized")
                # logger.warning(f"YuNet Diagnostic: Max confidence in {w}x{h} was {max_conf_found:.4f} (Threshold: {target_score_thresh})")
                return None
            
            # 2. Align Face
            aligned_face = self.recognizer.alignCrop(best_img_for_align, best_face)
            
            # 3. Extract Embedding
            embedding = self.recognizer.feature(aligned_face)
            return embedding

        except Exception as e:
            logger.error(f"Embedding extraction error: {e}")
            return None

    def recognize(self, frame, bbox, frame_id, recognition_threshold=0.4, detection_threshold=0.6):
        """
        Recognizes a face using SFace + Cosine Similarity.
        Threshold 0.363 is standard for SFace Cosine Matching.
        """
        if not self.detector or not self.recognizer or not self.face_db:
            return "Stranger", 1.0, 0

        try:
            h, w, _ = frame.shape
            x1, y1, x2, y2 = map(int, bbox)
            
            # --- 1. Person-to-Face Crop ---
            bw = x2 - x1
            bh = y2 - y1
            
            # Head-focused crop
            head_cx = x1 + (bw / 2)
            head_cy = y1 + (bh * 0.15)
            
            square_size = int(max(bw * 1.5, bh * 0.6))
            
            cx1 = int(head_cx - (square_size / 2))
            cy1 = int(head_cy - (square_size * 0.45))
            cx2 = cx1 + square_size
            cy2 = cy1 + square_size
            
            cx1, cy1 = max(0, cx1), max(0, cy1)
            cx2, cy2 = min(w, cx2), min(h, cy2)
            
            person_crop = frame[cy1:cy2, cx1:cx2]
            
            if person_crop.size == 0:
                return "Stranger", 1.0, 0

            # --- 2. Extract Embedding with specific detection threshold ---
            target_emb = self._get_embedding(person_crop, target_score_thresh=detection_threshold)
            if target_emb is None:
                return "Stranger", 1.0, 0

            # --- 3. Match against Database ---
            best_match = "Stranger"
            best_match_id = 0
            max_sim = 0.0
            
            for ref in self.face_db:
                # SFace score is cosine similarity
                sim = self.recognizer.match(target_emb, ref["embedding"], cv2.FaceRecognizerSF_FR_COSINE)
                if sim > max_sim:
                    max_sim = sim
                    if sim >= recognition_threshold:
                        best_match = ref["name"]
                        best_match_id = ref["id"]
            
            if best_match != "Stranger":
                logger.info(f"SFace Match: {best_match} | Similarity={max_sim:.4f}")
                return best_match, max_sim, best_match_id
            else:
                logger.info("No Match with Existing faces!")
            
            return "Stranger", 1.0, 0

        except Exception as e:
            logger.error(f"SFace Recognition Error: {e}")
            return "Error", 0.0, -1

if __name__ == "__main__":
    # Quick module test
    recognizer = RoboFaceID()
    test_img = np.zeros((480, 640, 3), dtype=np.uint8)
    dummy_bbox = [100, 100, 300, 400]
    res = recognizer.recognize(test_img, dummy_bbox, frame_id=0)
    print(f"Test Result: {res}")