"""
Dataset Merger for Fire & Fight Detection
Combines multiple datasets into a single YOLO-format dataset
"""

import os
import shutil
import random
from pathlib import Path
from collections import defaultdict
import yaml

# Configuration
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
DATASETS_DIR = PROJECT_DIR / "datasets"
OUTPUT_DIR = DATASETS_DIR / "combined"

# Split ratios
TRAIN_RATIO = 0.80
VAL_RATIO = 0.15
TEST_RATIO = 0.05

# Class mapping - CUSTOMIZE THIS based on your existing model
# Map source class names/IDs to unified class IDs
CLASS_MAPPING = {
    # Standard COCO classes (keep your existing ones)
    "person": 0,
    "car": 1,
    "truck": 2,
    "bicycle": 3,
    "motorcycle": 4,
    # Add more of your existing classes here...
    
    # New detection classes
    "fire": 10,
    "flame": 10,       # Alias -> fire
    "smoke": 11,
    "fighting": 12,
    "violence": 12,    # Alias -> fighting
    "aggression": 12,  # Alias -> fighting
    "fight": 12,       # Alias -> fighting
}

# Final class names for the combined model
FINAL_CLASSES = {
    0: "person",
    1: "car", 
    2: "truck",
    3: "bicycle",
    4: "motorcycle",
    10: "fire",
    11: "smoke",
    12: "fighting"
}


def create_output_structure():
    """Create output directory structure"""
    if OUTPUT_DIR.exists():
        print(f"⚠️ Output directory exists. Cleaning...")
        shutil.rmtree(OUTPUT_DIR)
    
    for split in ["train", "valid", "test"]:
        (OUTPUT_DIR / split / "images").mkdir(parents=True, exist_ok=True)
        (OUTPUT_DIR / split / "labels").mkdir(parents=True, exist_ok=True)
    
    print(f"✅ Created output structure at {OUTPUT_DIR}")


def find_dataset_pairs(dataset_path):
    """Find all image-label pairs in a dataset"""
    pairs = []
    
    # Common YOLO dataset structures
    possible_structures = [
        ("images", "labels"),
        ("train/images", "train/labels"),
        ("valid/images", "valid/labels"),
        ("test/images", "test/labels"),
    ]
    
    for img_rel, label_rel in possible_structures:
        img_dir = dataset_path / img_rel
        label_dir = dataset_path / label_rel
        
        if not img_dir.exists():
            continue
            
        for img_file in img_dir.iterdir():
            if img_file.suffix.lower() in [".jpg", ".jpeg", ".png", ".bmp", ".webp"]:
                # Find corresponding label file
                label_file = label_dir / f"{img_file.stem}.txt"
                
                if label_file.exists():
                    pairs.append((img_file, label_file))
    
    return pairs


def scan_all_datasets():
    """Scan all datasets and collect image-label pairs"""
    all_pairs = []
    
    print("\n📂 Scanning datasets...")
    print("-" * 40)
    
    for dataset_dir in DATASETS_DIR.iterdir():
        if dataset_dir.is_dir() and dataset_dir.name != "combined":
            pairs = find_dataset_pairs(dataset_dir)
            
            if pairs:
                print(f"  ✓ {dataset_dir.name}: {len(pairs)} pairs")
                all_pairs.extend(pairs)
            else:
                print(f"  ✗ {dataset_dir.name}: No valid pairs found")
    
    print("-" * 40)
    print(f"📊 Total pairs collected: {len(all_pairs)}")
    
    return all_pairs


def copy_and_process_files(pairs, split_name, start_idx=0):
    """Copy and process files for a specific split"""
    copied = 0
    
    for i, (img_file, label_file) in enumerate(pairs):
        # Create unique filename
        new_name = f"{split_name}_{start_idx + i:06d}"
        
        # Copy image
        dst_img = OUTPUT_DIR / split_name / "images" / f"{new_name}{img_file.suffix}"
        shutil.copy2(img_file, dst_img)
        
        # Copy label (can add class remapping here if needed)
        dst_label = OUTPUT_DIR / split_name / "labels" / f"{new_name}.txt"
        shutil.copy2(label_file, dst_label)
        
        copied += 1
    
    return copied


def split_and_copy_datasets(all_pairs):
    """Split pairs into train/val/test and copy to output"""
    
    # Shuffle for random split
    random.seed(42)  # For reproducibility
    random.shuffle(all_pairs)
    
    # Calculate split sizes
    n_total = len(all_pairs)
    n_train = int(n_total * TRAIN_RATIO)
    n_val = int(n_total * VAL_RATIO)
    
    # Split
    splits = {
        "train": all_pairs[:n_train],
        "valid": all_pairs[n_train:n_train + n_val],
        "test": all_pairs[n_train + n_val:]
    }
    
    print("\n📁 Copying files to splits...")
    print("-" * 40)
    
    for split_name, pairs in splits.items():
        count = copy_and_process_files(pairs, split_name)
        print(f"  ✓ {split_name}: {count} samples")
    
    return splits


def create_yaml_config():
    """Create dataset YAML configuration file"""
    
    # Renumber classes to be contiguous (0, 1, 2, ...)
    # YOLOv8 prefers contiguous class IDs
    contiguous_classes = {}
    for new_id, (old_id, name) in enumerate(sorted(FINAL_CLASSES.items())):
        contiguous_classes[new_id] = name
    
    config = {
        "path": str(OUTPUT_DIR.absolute()),
        "train": "train/images",
        "val": "valid/images",
        "test": "test/images",
        "names": contiguous_classes
    }
    
    yaml_path = PROJECT_DIR / "combined_dataset.yaml"
    with open(yaml_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    print(f"\n✅ Created dataset config: {yaml_path}")
    
    # Also create a copy in the output directory
    shutil.copy2(yaml_path, OUTPUT_DIR / "data.yaml")
    
    return yaml_path


def analyze_class_distribution(splits):
    """Analyze and display class distribution"""
    
    print("\n📊 Class Distribution Analysis")
    print("=" * 50)
    
    for split_name, pairs in splits.items():
        class_counts = defaultdict(int)
        total_objects = 0
        
        for _, label_file in pairs:
            try:
                with open(label_file, 'r') as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) >= 5:
                            class_id = int(parts[0])
                            class_counts[class_id] += 1
                            total_objects += 1
            except Exception:
                pass
        
        print(f"\n{split_name.upper()} ({len(pairs)} images, {total_objects} objects):")
        for class_id in sorted(class_counts.keys()):
            class_name = FINAL_CLASSES.get(class_id, f"class_{class_id}")
            count = class_counts[class_id]
            pct = (count / total_objects * 100) if total_objects > 0 else 0
            print(f"  Class {class_id} ({class_name}): {count} ({pct:.1f}%)")


def main():
    print("=" * 50)
    print("🔀 Dataset Merger for Fire & Fight Detection")
    print("=" * 50)
    
    # Ensure datasets directory exists
    if not DATASETS_DIR.exists():
        print(f"❌ Datasets directory not found: {DATASETS_DIR}")
        print("   Please run download_datasets.py first!")
        return
    
    # Step 1: Create output structure
    create_output_structure()
    
    # Step 2: Scan all datasets
    all_pairs = scan_all_datasets()
    
    if not all_pairs:
        print("\n❌ No image-label pairs found!")
        print("   Please download datasets first using download_datasets.py")
        return
    
    # Step 3: Split and copy
    splits = split_and_copy_datasets(all_pairs)
    
    # Step 4: Create YAML config
    create_yaml_config()
    
    # Step 5: Analyze distribution
    analyze_class_distribution(splits)
    
    print("\n" + "=" * 50)
    print("✅ Dataset merging complete!")
    print("=" * 50)
    print(f"\n📂 Output: {OUTPUT_DIR}")
    print(f"📄 Config: {PROJECT_DIR / 'combined_dataset.yaml'}")
    print("\nNext step: Run train.py to train the model")


if __name__ == "__main__":
    main()
