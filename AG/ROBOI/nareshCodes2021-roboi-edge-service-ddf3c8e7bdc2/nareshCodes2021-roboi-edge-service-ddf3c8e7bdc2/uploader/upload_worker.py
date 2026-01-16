import os
import time
import zipfile
import shutil
import logging
import datetime
from google.cloud import storage
import yaml
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "configs", "app_config.yaml")
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Setup Logging
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "uploader.log"),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

def load_config():
    try:
        with open(CONFIG_PATH, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logging.error(f"Failed to load config: {e}")
        return {}

def get_target_bucket():
    config = load_config()
    # Support both env var and config
    bucket_name = config.get('cloud_storage', {}).get('bucket_name')
    if not bucket_name:
        bucket_name = os.environ.get("ROBOI_BUCKET_NAME")
    return bucket_name

def convert_mp4_to_webm(file_path):
    """
    Converts an MP4 file to WebM using ffmpeg and removes the original MP4.
    Returns the new file path if successful, otherwise None.
    """
    try:
        if not file_path.endswith(".mp4"):
            return file_path
            
        webm_path = file_path.replace(".mp4", ".webm")
        # ffmpeg command: fast conversion, reasonable quality
        command = [
            "ffmpeg", "-y", 
            "-i", file_path,
            "-c:v", "libvpx-vp9", "-b:v", "0", "-crf", "30", # VP9, constant quality
            "-an", # No audio for efficiency (add -c:a libopus if audio needed)
            "-f", "webm",
            webm_path
        ]
        
        logging.info(f"Converting {file_path} to {webm_path}...")
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Verify WebM exists
        if os.path.exists(webm_path):
            os.remove(file_path) # Remove original MP4
            logging.info(f"Conversion successful. Removed {file_path}")
            return webm_path
        else:
            logging.error(f"Conversion failed: WebM file not created for {file_path}")
            return None
            
    except Exception as e:
        logging.error(f"Failed to convert {file_path}: {e}")
        return None

def scan_and_upload(captures_dir):
    if not os.path.exists(captures_dir):
        logging.warning(f"Captures directory not found: {captures_dir}")
        return

    # Check for GCS Bucket
    bucket_name = get_target_bucket()
    if not bucket_name:
        logging.error("No bucket name configured. Set 'cloud_storage.bucket_name' in app_config.yaml or ROBOI_BUCKET_NAME env var.")
        return

    # Initialize GCS Client
    try:
        key_path = os.path.join(BASE_DIR, "vertex-ai-user.json")
        if os.path.exists(key_path):
            logging.info(f"Using service account key: {key_path}")
            storage_client = storage.Client.from_service_account_json(key_path)
        else:
            logging.warning(f"Key file not found at {key_path}, falling back to default credentials")
            storage_client = storage.Client()
            
        bucket = storage_client.bucket(bucket_name)
    except Exception as e:
        logging.error(f"Failed to initialize GCS client: {e}")
        return

    # Iterate over directories in captures_dir
    for item in os.listdir(captures_dir):
        item_path = os.path.join(captures_dir, item)
        
        if os.path.isdir(item_path):
            # Check for marker file
            ready_marker = os.path.join(item_path, ".upload_ready")
            if os.path.exists(ready_marker):
                logging.info(f"Processing event: {item}")
                process_event_direct_upload(item_path, bucket)

def process_event(event_dir, bucket):
    try:
        dir_name = os.path.basename(event_dir)
        bypass_path = event_dir + ".zip" 
        
        # 1. Zip the directory
        logging.info(f"Zipping {dir_name}...")
        make_zipfile(bypass_path, event_dir)
        
        # 2. Upload the zip
        blob_name = f"events/{dir_name}.zip"
        blob = bucket.blob(blob_name)
        
        logging.info(f"Uploading {blob_name} to {bucket.name}...")
        blob.upload_from_filename(bypass_path)
        logging.info(f"Upload complete: {blob_name}")
        
        # 3. Cleanup
        logging.info(f"Cleaning up {dir_name}...")
        os.remove(bypass_path) # Remove zip
        shutil.rmtree(event_dir) # Remove original dir
        logging.info(f"Cleanup successful for {dir_name}")
        
    except Exception as e:
        logging.error(f"Failed to process {event_dir}: {e}")

def upload_single_file(bucket, blob_name, file_path):
    """Helper for parallel upload."""
    try:
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(file_path)
        return True
    except Exception as e:
        logging.error(f"Failed to upload {file_path}: {e}")
        return False

def process_event_direct_upload(event_dir, bucket):
    """
    Uploads directory contents directly without zipping using parallel threads.
    Structure: events/{dir_name}/{filename}
    """
    try:
        dir_name = os.path.basename(event_dir)
        logging.info(f"Starting direct upload for {dir_name}...")
        
        file_count = 0
        files_to_upload = []

        # 1. Walk and Gather Files
        for root, dirs, files in os.walk(event_dir):
            for file in files:
                if file == ".upload_ready":
                    continue
                    
                file_path = os.path.join(root, file)
                
                # Convert MP4 to WebM
                if file_path.endswith(".mp4"):
                    new_path = convert_mp4_to_webm(file_path)
                    if new_path:
                        file_path = new_path
                        # Re-calculate file name for blob since extension changed
                        file = os.path.basename(file_path)
                    else:
                        logging.warning(f"Skipping upload for failed conversion: {file_path}")
                        continue
                
                rel_path = os.path.relpath(file_path, event_dir)
                blob_name = f"events/{dir_name}/{rel_path}"
                
                files_to_upload.append((blob_name, file_path))
        
        # 2. Parallel Upload
        # Adjust max_workers based on Jetson capabilities/network
        with ThreadPoolExecutor(max_workers=10) as executor:
            # key: future, val: file_path (for error tracking)
            future_to_file = {
                executor.submit(upload_single_file, bucket, bn, fp): fp 
                for bn, fp in files_to_upload
            }
            
            for future in as_completed(future_to_file):
                if future.result():
                    file_count += 1
        
        logging.info(f"Uploaded {file_count}/{len(files_to_upload)} files for {dir_name}")
        
        # 3. Cleanup
        logging.info(f"Cleaning up {dir_name}...")
        shutil.rmtree(event_dir) 
        logging.info(f"Cleanup successful for {dir_name}")

    except Exception as e:
        logging.error(f"Failed to process (direct) {event_dir}: {e}")

def make_zipfile(output_filename, source_dir):
    with zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # Keep relative structure inside zip
                arcname = os.path.relpath(file_path, os.path.dirname(source_dir))
                zipf.write(file_path, arcname)

if __name__ == "__main__":
    logging.info("Starting Upload Worker...")
    
    # Assuming standard captures path
    CAPTURES_DIR = os.path.join(BASE_DIR, "data", "captures")
    
    while True:
        try:
            scan_and_upload(CAPTURES_DIR)
        except Exception as e:
            logging.error(f"Worker Loop Error: {e}")
        
        # Scan every 5 seconds
        time.sleep(5)
