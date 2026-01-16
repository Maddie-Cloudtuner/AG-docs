import os
import requests
MODEL_DIR = "models/face"

MODELS = {
    "face_detection_yunet.onnx": "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx",
    "face_recognition_sface.onnx": "https://github.com/opencv/opencv_zoo/raw/main/models/face_recognition_sface/face_recognition_sface_2021dec_int8.onnx"
}

def download_models():
    print(f"Creating directory {MODEL_DIR}...")
    os.makedirs(MODEL_DIR, exist_ok=True)

    for filename, url in MODELS.items():
        path = os.path.join(MODEL_DIR, filename)
        if os.path.exists(path):
            print(f"Model already exists at {path}")
            continue

        print(f"Downloading {filename} from {url}...")
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print(f"Download complete: {path}")
        except Exception as e:
            print(f"Error downloading {filename}: {e}")
            sys.exit(1)

if __name__ == "__main__":
    download_models()
