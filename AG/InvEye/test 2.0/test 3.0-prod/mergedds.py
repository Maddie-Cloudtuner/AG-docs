"""
Antigravity Dataset Merger (Enterprise Edition)
===============================================
Optimized for Invincible Ocean / Cloudtuner.ai contexts.

Features:
- 🚀 Multi-threaded: Uses multiple CPU cores to prevent timeouts.
- 🛡️ Crash-Proof: Skips bad files/zips instead of stopping (Runtime Error protection).
- 📊 Universal: Generates data compatible with multiple YOLO models (v5, v8, v11).
- 🔄 Auto-Recovery: Handles existing folders gracefully.

Author: Antigravity Team
Date: 2025-12-31
"""

import os
import shutil
import zipfile
import random
import yaml
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# ============================================================
# ⚙️ CONFIGURATION
# ============================================================

# Windows Paths (Raw strings 'r' to handle backslashes)
DATASETS_ROOT = r"C:\Users\LENOVO\Desktop\my_docs\AG\InvEye\test 2.0\test 3.0-prod\datasets"
OUTPUT_DIR = r"C:\Users\LENOVO\Desktop\my_docs\AG\InvEye\test 2.0\test 3.0-prod\merged_dataset"

# Performance Settings
MAX_WORKERS = 8  # Number of parallel threads (Higher = Faster, but uses more CPU)

# Class Mapping
CLASS_MAPPING = {
    # COCO Standard
    "person": (0, "person"), "bicycle": (1, "bicycle"), "car": (2, "car"),
    "motorcycle": (3, "motorcycle"), "bus": (4, "bus"), "truck": (5, "truck"),
    
    # Custom / Antigravity Classes
    "mobile": (16, "cell_phone"), "cell_phone": (16, "cell_phone"), "phone": (16, "cell_phone"),
    "clock": (17, "clock"), "scissors": (18, "scissors"),
    "fire": (19, "fire"), "smoke": (20, "smoke"),
    "cig": (21, "cigarette"), "cigarette": (21, "cigarette"),
    "nozzle": (22, "du_nozzle"), "du": (22, "du_nozzle"),
    "license": (23, "license_plate"), "license_plate": (23, "license_plate"),
    "container": (24, "container"), "face": (25, "face"),
}

TRAIN_RATIO = 0.7
VAL_RATIO = 0.2
TEST_RATIO = 0.1
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}

# ============================================================
# 🛠️ CORE FUNCTIONS
# ============================================================

def safe_extract_zip(zip_path):
    """Safely extracts a zip file without crashing the script."""
    try:
        extract_to = zip_path.parent / zip_path.stem
        if extract_to.exists():
            return 0 # Already extracted
            
        print(f"   📦 Extracting: {zip_path.name}")
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(extract_to)
        return 1
    except zipfile.BadZipFile:
        print(f"   ❌ ERROR: Bad Zip File skipped: {zip_path.name}")
        return 0
    except Exception as e:
        print(f"   ⚠️ WARNING: Issue extracting {zip_path.name}: {e}")
        return 0

def find_images_and_labels(folder_path):
    """Recursively finds images and their matching labels."""
    folder = Path(folder_path)
    pairs = []
    
    try:
        # 1. Find all images first
        all_images = [f for f in folder.rglob("*") if f.suffix.lower() in IMAGE_EXTENSIONS]
        
        for img_file in all_images:
            label_file = None
            
            # Strategy A: Check same folder (flat structure)
            potential_flat = img_file.with_suffix(".txt")
            if potential_flat.exists():
                label_file = potential_flat
            
            # Strategy B: Check ../labels/ folder (standard YOLO)
            else:
                parts = list(img_file.parts)
                if "images" in parts:
                    idx = len(parts) - 1 - parts[::-1].index("images")
                    parts[idx] = "labels"
                    potential_yolo = Path(*parts).with_suffix(".txt")
                    if potential_yolo.exists():
                        label_file = potential_yolo

            if label_file:
                pairs.append((img_file, label_file))
                
    except Exception as e:
        print(f"   ❌ Error scanning folder {folder_path}: {e}")
        
    return pairs

def process_single_pair(args):
    """
    Worker function for Multi-Threading.
    Copies image and writes new label.
    """
    img_path, lbl_path, tid, tname, output_dir, split_name, unique_id = args
    
    try:
        # Create unique filename to prevent overwrites
        new_name = f"{tname}_{unique_id}"
        
        # 1. Copy Image
        new_img_path = output_dir / 'images' / split_name / (new_name + img_path.suffix)
        shutil.copy2(img_path, new_img_path)
        
        # 2. Process Label (Remap Class ID)
        with open(lbl_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            
        new_lines = []
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 5:
                # Force the new Class ID
                parts[0] = str(tid)
                new_lines.append(" ".join(parts))
        
        # 3. Write New Label
        new_lbl_path = output_dir / 'labels' / split_name / (new_name + ".txt")
        with open(new_lbl_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(new_lines))
            
        return True # Success
    except Exception as e:
        print(f"   ❌ Error processing {img_path.name}: {e}")
        return False # Failure

# ============================================================
# 🎬 MAIN EXECUTION
# ============================================================

def main():
    print("="*60)
    print(" 🚀 ANTIGRAVITY DATASET MERGER (Multi-Threaded)")
    print("="*60)
    
    datasets_root = Path(DATASETS_ROOT)
    output_dir = Path(OUTPUT_DIR)
    
    # 1. Setup Directories
    for split in ['train', 'val', 'test']:
        (output_dir / 'images' / split).mkdir(parents=True, exist_ok=True)
        (output_dir / 'labels' / split).mkdir(parents=True, exist_ok=True)

    all_tasks = [] 
    
    # 2. Scan & Extract (Single Threaded for safety on Zips)
    print("\n🔍 Scanning folders...")
    for folder in datasets_root.iterdir():
        if not folder.is_dir(): continue
        
        key = folder.name.lower()
        if key in CLASS_MAPPING:
            tid, tname = CLASS_MAPPING[key]
            print(f"   📂 Found '{folder.name}' -> Mapping to Class {tid} ({tname})")
            
            # Extract Zips
            zip_files = list(folder.glob("*.zip"))
            if zip_files:
                for zf in zip_files:
                    safe_extract_zip(zf)
            
            # Find Data
            pairs = find_images_and_labels(folder)
            print(f"      -> Found {len(pairs)} images")
            
            for img, lbl in pairs:
                all_tasks.append((img, lbl, tid, tname))
        else:
            print(f"   ⚠️ Skipping unknown folder: {folder.name}")

    if not all_tasks:
        print("\n❌ CRITICAL: No data found. Please check paths.")
        return

    # 3. Shuffle & Split
    print(f"\n🎲 Shuffling {len(all_tasks)} total items...")
    random.shuffle(all_tasks)
    
    n_total = len(all_tasks)
    n_train = int(n_total * TRAIN_RATIO)
    n_val = int(n_total * VAL_RATIO)
    
    splits = {
        'train': all_tasks[:n_train],
        'val': all_tasks[n_train:n_train+n_val],
        'test': all_tasks[n_train+n_val:]
    }

    # 4. Multi-Threaded Processing (The "Fast" Part)
    print(f"\n⚡ Starting Parallel Processing (Using {MAX_WORKERS} threads)...")
    
    for split_name, tasks in splits.items():
        if not tasks: continue
        print(f"   👉 Processing {split_name.upper()} set ({len(tasks)} images)...")
        
        # Prepare arguments for workers
        worker_args = []
        for i, (img, lbl, tid, tname) in enumerate(tasks):
            unique_id = f"{i:06d}" # Simple 000001 ID
            worker_args.append((img, lbl, tid, tname, output_dir, split_name, unique_id))
        
        # Run in parallel
        start_time = time.time()
        success_count = 0
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # Submit all tasks
            futures = [executor.submit(process_single_pair, arg) for arg in worker_args]
            
            # Monitor progress
            total = len(futures)
            for i, future in enumerate(as_completed(futures)):
                if future.result():
                    success_count += 1
                
                # Heartbeat logging every 10% or 100 items
                if (i + 1) % 100 == 0 or (i + 1) == total:
                    print(f"      [{split_name}] Progress: {i + 1}/{total} ({(i+1)/total*100:.1f}%)")

        duration = time.time() - start_time
        print(f"      ✅ Done in {duration:.2f}s. Success rate: {success_count}/{len(tasks)}")

    # 5. Generate YAML
    print("\n📝 Generating data.yaml...")
    names_list = ["unused"] * (max(id for id, _ in CLASS_MAPPING.values()) + 1)
    used_ids = set()
    for _, (cid, cname) in CLASS_MAPPING.items():
        names_list[cid] = cname
        used_ids.add(cid)
        
    yaml_content = {
        'path': str(output_dir),
        'train': 'images/train',
        'val': 'images/val',
        'test': 'images/test',
        'names': {i: n for i, n in enumerate(names_list) if i in used_ids}
    }
    
    with open(output_dir / "data.yaml", 'w') as f:
        yaml.dump(yaml_content, f, sort_keys=False)

    print("\n" + "="*60)
    print("✅ ANTIGRAVITY DATASET MERGE COMPLETE")
    print("="*60)

if __name__ == "__main__":
    # Required for Windows Multiprocessing safety
    main()