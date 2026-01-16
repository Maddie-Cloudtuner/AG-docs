"""
YOLO Dataset Merger Script
===========================
Merges multiple YOLO-format datasets into one unified dataset with proper class remapping.

Features:
- Automatically extracts ZIP files
- Handles multiple dataset formats (YOLO, Roboflow exports)
- Remaps class IDs to unified schema
- Creates train/val/test splits
- Generates data.yaml

Author: InvEye Team
Date: 2025-12-31
"""

import os
import shutil
import zipfile
import random
import yaml
from pathlib import Path
from collections import defaultdict

# ============================================================
# CONFIGURATION - EDIT THIS SECTION
# ============================================================

# Path to your datasets folder
DATASETS_ROOT = r"C:\Users\LENOVO\Desktop\my_docs\AG\InvEye\test 2.0\test 3.0-prod\datasets"

# Output folder for merged dataset
OUTPUT_DIR = r"C:\Users\LENOVO\Desktop\my_docs\AG\InvEye\test 2.0\test 3.0-prod\merged_dataset"

# Class mapping: folder_name -> (target_class_id, target_class_name)
# Based on COCO classes + custom classes for petrol pump analytics
#
# COCO Classes (0-15):
#   0: person, 1: bicycle, 2: car, 3: motorcycle, 4: bus, 5: truck
#   6: fire hydrant, 7: dog, 8: backpack, 9: handbag, 10: suitcase
#   11: bottle, 12: knife, 13: chair, 14: toilet, 15: tv
#
# Custom Classes (16-24):
#   16: cell phone, 17: clock, 18: scissors, 19: fire, 20: smoke
#   21: cigarette, 22: du_nozzle, 23: license_plate, 24: container
#
CLASS_MAPPING = {
    # Folder name -> (class_id, class_name)
    
    # COCO-compatible folders (if you have these)
    "person": (0, "person"),
    "bicycle": (1, "bicycle"),
    "car": (2, "car"),
    "motorcycle": (3, "motorcycle"),
    "bus": (4, "bus"),
    "truck": (5, "truck"),
    "fire_hydrant": (6, "fire_hydrant"),
    "dog": (7, "dog"),
    "backpack": (8, "backpack"),
    "handbag": (9, "handbag"),
    "suitcase": (10, "suitcase"),
    "bottle": (11, "bottle"),
    "knife": (12, "knife"),
    "chair": (13, "chair"),
    "toilet": (14, "toilet"),
    "tv": (15, "tv"),
    
    # Your custom folders
    "mobile": (16, "cell_phone"),
    "cell_phone": (16, "cell_phone"),
    "phone": (16, "cell_phone"),
    "clock": (17, "clock"),
    "scissors": (18, "scissors"),
    "fire": (19, "fire"),
    "smoke": (20, "smoke"),
    "cig": (21, "cigarette"),
    "cigarette": (21, "cigarette"),
    "nozzle": (22, "du_nozzle"),
    "du": (22, "du_nozzle"),
    "license": (23, "license_plate"),
    "license_plate": (23, "license_plate"),
    "container": (24, "container"),
    "face": (25, "face"),
}

# Train/Val/Test split ratios
TRAIN_RATIO = 0.7
VAL_RATIO = 0.2
TEST_RATIO = 0.1

# Image extensions to look for
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def extract_zip_files(folder_path):
    """Extract all ZIP files in a folder."""
    zip_files = list(Path(folder_path).glob("*.zip"))
    for zip_file in zip_files:
        print(f"  📦 Extracting: {zip_file.name}")
        extract_to = zip_file.parent / zip_file.stem
        try:
            with zipfile.ZipFile(zip_file, 'r') as zf:
                zf.extractall(extract_to)
            print(f"  ✅ Extracted to: {extract_to}")
        except Exception as e:
            print(f"  ❌ Failed to extract {zip_file.name}: {e}")
    return len(zip_files)


def find_images_and_labels(folder_path):
    """
    Find all image-label pairs in a folder.
    Handles various YOLO dataset structures:
    - images/ + labels/
    - train/images + train/labels
    - Flat structure with .txt next to images
    """
    folder = Path(folder_path)
    pairs = []
    
    # Strategy 1: Look for images/ and labels/ folders
    images_dirs = list(folder.rglob("images"))
    labels_dirs = list(folder.rglob("labels"))
    
    if images_dirs and labels_dirs:
        for img_dir in images_dirs:
            for img_file in img_dir.iterdir():
                if img_file.suffix.lower() in IMAGE_EXTENSIONS:
                    # Find corresponding label
                    label_name = img_file.stem + ".txt"
                    for lbl_dir in labels_dirs:
                        label_file = lbl_dir / label_name
                        if label_file.exists():
                            pairs.append((img_file, label_file))
                            break
    
    # Strategy 2: Flat structure (image.jpg + image.txt in same folder)
    if not pairs:
        for img_file in folder.rglob("*"):
            if img_file.suffix.lower() in IMAGE_EXTENSIONS:
                label_file = img_file.with_suffix(".txt")
                if label_file.exists():
                    pairs.append((img_file, label_file))
    
    return pairs


def remap_labels(label_content, source_class_id, target_class_id):
    """
    Remap class IDs in YOLO label content.
    If source_class_id is None, remap ALL classes to target_class_id.
    """
    new_lines = []
    for line in label_content.strip().split('\n'):
        if not line.strip():
            continue
        parts = line.strip().split()
        if len(parts) >= 5:
            # YOLO format: class_id x_center y_center width height
            parts[0] = str(target_class_id)
            new_lines.append(' '.join(parts))
    return '\n'.join(new_lines)


def create_output_structure(output_dir):
    """Create the output directory structure."""
    dirs = [
        "images/train", "images/val", "images/test",
        "labels/train", "labels/val", "labels/test"
    ]
    for d in dirs:
        (Path(output_dir) / d).mkdir(parents=True, exist_ok=True)
    print(f"✅ Created output structure at: {output_dir}")


def generate_data_yaml(output_dir, class_names):
    """Generate the data.yaml file for YOLO training."""
    yaml_content = {
        'path': str(output_dir),
        'train': 'images/train',
        'val': 'images/val',
        'test': 'images/test',
        'names': {i: name for i, name in enumerate(class_names)},
        'nc': len(class_names)
    }
    
    yaml_path = Path(output_dir) / "data.yaml"
    with open(yaml_path, 'w') as f:
        yaml.dump(yaml_content, f, default_flow_style=False, sort_keys=False)
    
    print(f"✅ Generated data.yaml with {len(class_names)} classes")
    return yaml_path


# ============================================================
# MAIN PROCESSING
# ============================================================

def main():
    print("=" * 60)
    print("🔥 YOLO Dataset Merger Script")
    print("=" * 60)
    
    datasets_root = Path(DATASETS_ROOT)
    output_dir = Path(OUTPUT_DIR)
    
    if not datasets_root.exists():
        print(f"❌ Datasets folder not found: {datasets_root}")
        return
    
    # Step 1: Create output structure
    print("\n📁 Step 1: Creating output structure...")
    create_output_structure(output_dir)
    
    # Step 2: Process each category folder
    print("\n📊 Step 2: Processing category folders...")
    
    all_pairs = []  # (image_path, label_path, target_class_id, target_class_name)
    stats = defaultdict(int)
    
    for folder in datasets_root.iterdir():
        if not folder.is_dir():
            continue
        
        folder_name = folder.name.lower()
        print(f"\n📂 Processing: {folder_name}/")
        
        # Check if this folder is in our mapping
        if folder_name not in CLASS_MAPPING:
            print(f"  ⚠️ Skipping (not in CLASS_MAPPING)")
            continue
        
        target_class_id, target_class_name = CLASS_MAPPING[folder_name]
        print(f"  → Mapping to class {target_class_id}: {target_class_name}")
        
        # Extract ZIP files if any
        zip_count = extract_zip_files(folder)
        if zip_count > 0:
            print(f"  📦 Extracted {zip_count} ZIP file(s)")
        
        # Find image-label pairs
        pairs = find_images_and_labels(folder)
        print(f"  🖼️ Found {len(pairs)} image-label pairs")
        
        for img_path, lbl_path in pairs:
            all_pairs.append((img_path, lbl_path, target_class_id, target_class_name))
            stats[target_class_name] += 1
    
    if not all_pairs:
        print("\n❌ No image-label pairs found! Check your folder structure.")
        return
    
    print(f"\n📈 Total pairs found: {len(all_pairs)}")
    print("Class distribution:")
    for class_name, count in sorted(stats.items()):
        print(f"  - {class_name}: {count}")
    
    # Step 3: Shuffle and split
    print("\n🔀 Step 3: Shuffling and splitting...")
    random.shuffle(all_pairs)
    
    n_total = len(all_pairs)
    n_train = int(n_total * TRAIN_RATIO)
    n_val = int(n_total * VAL_RATIO)
    
    train_pairs = all_pairs[:n_train]
    val_pairs = all_pairs[n_train:n_train + n_val]
    test_pairs = all_pairs[n_train + n_val:]
    
    print(f"  Train: {len(train_pairs)}")
    print(f"  Val: {len(val_pairs)}")
    print(f"  Test: {len(test_pairs)}")
    
    # Step 4: Copy and remap
    print("\n📋 Step 4: Copying files and remapping classes...")
    
    def process_split(pairs, split_name):
        for i, (img_path, lbl_path, target_class_id, target_class_name) in enumerate(pairs):
            # Generate unique filename
            new_filename = f"{target_class_name}_{i:06d}"
            
            # Copy image
            new_img_path = output_dir / "images" / split_name / (new_filename + img_path.suffix.lower())
            shutil.copy2(img_path, new_img_path)
            
            # Read, remap, and save label
            with open(lbl_path, 'r') as f:
                label_content = f.read()
            
            remapped_content = remap_labels(label_content, None, target_class_id)
            
            new_lbl_path = output_dir / "labels" / split_name / (new_filename + ".txt")
            with open(new_lbl_path, 'w') as f:
                f.write(remapped_content)
        
        print(f"  ✅ {split_name}: {len(pairs)} files copied")
    
    process_split(train_pairs, "train")
    process_split(val_pairs, "val")
    process_split(test_pairs, "test")
    
    # Step 5: Generate data.yaml
    print("\n📄 Step 5: Generating data.yaml...")
    
    # Get unique class names in order
    class_names = [""] * (max(v[0] for v in CLASS_MAPPING.values()) + 1)
    for folder_name, (class_id, class_name) in CLASS_MAPPING.items():
        class_names[class_id] = class_name
    class_names = [name for name in class_names if name]  # Remove empty
    
    generate_data_yaml(output_dir, class_names)
    
    # Final summary
    print("\n" + "=" * 60)
    print("✅ DATASET MERGE COMPLETE!")
    print("=" * 60)
    print(f"\n📁 Output: {output_dir}")
    print(f"📊 Total images: {len(all_pairs)}")
    print(f"🏷️ Classes: {len(class_names)}")
    print("\n📝 Class mapping:")
    for i, name in enumerate(class_names):
        print(f"   {i}: {name}")
    print(f"\n🚀 Ready for YOLO training!")
    print(f"   Use: data.yaml at {output_dir / 'data.yaml'}")


if __name__ == "__main__":
    main()
