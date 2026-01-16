"""
🔀 Dataset Merger for YOLO Training
=====================================
Merges multiple datasets into a unified YOLO format for training.
Handles class remapping, train/val/test splits, and label normalization.

Author: InvEye Team
Usage:
    python merge_datasets.py --input ./datasets --output ./datasets/combined
    python merge_datasets.py --fire-only
    python merge_datasets.py --verify

Optimized for: Jetson Orin Nano deployment
"""

import os
import sys
import shutil
import random
import argparse
import yaml
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False


# ============================================================================
# CONFIGURATION
# ============================================================================

# Class mapping for unified dataset
# All source classes will be mapped to these target classes
CLASS_MAPPING = {
    # Fire/Smoke classes
    "fire": 0,
    "Fire": 0,
    "FIRE": 0,
    
    "smoke": 1,
    "Smoke": 1,
    "SMOKE": 1,
    
    # Fight/Violence classes
    "fighting": 2,
    "fight": 2,
    "Fight": 2,
    "violence": 2,
    "Violence": 2,
    "aggressor": 2,
    "aggression": 2,
    
    # Non-violence (will be excluded or kept as negative samples)
    "non_violence": -1,  # -1 means exclude
    "NonViolence": -1,
    "no_fight": -1,
    "normal": -1,
    "neutral": -1,
    
    # Face classes
    "face": 3,
    "Face": 3,
    "human_face": 3,
    
    # Weapon classes (bonus)
    "weapon": 4,
    "handgun": 4,
    "pistol": 4,
    "rifle": 4,
    "gun": 4,
    "guns": 4,
    "knife": 5,
    "Knife": 5,
    
    # Person (for context)
    "person": 6,
    "Person": 6,
    "human": 6,
}

# Target class names for YAML config
TARGET_CLASSES = {
    0: "fire",
    1: "smoke", 
    2: "fighting",
    3: "face",
    4: "weapon",
    5: "knife",
    6: "person",
}

# Split ratios
TRAIN_RATIO = 0.7
VAL_RATIO = 0.2
TEST_RATIO = 0.1


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def print_banner():
    print("""
╔════════════════════════════════════════════════════════════════════╗
║          🔀 DATASET MERGER FOR UNIFIED YOLO TRAINING 🔀           ║
║                                                                    ║
║  Merges: Fire | Smoke | Fight | Face | Weapon datasets            ║
║  Optimized for: Jetson Orin Nano deployment                        ║
╚════════════════════════════════════════════════════════════════════╝
    """)


def find_datasets(base_dir):
    """Find all YOLO-format datasets in the directory structure."""
    datasets = []
    base_path = Path(base_dir)
    
    # Look for data.yaml files (Roboflow format)
    for yaml_file in base_path.rglob("data.yaml"):
        datasets.append({
            "type": "roboflow",
            "path": yaml_file.parent,
            "config": yaml_file
        })
    
    # Look for directories with images and labels folders
    for img_dir in base_path.rglob("images"):
        if img_dir.is_dir():
            label_dir = img_dir.parent / "labels"
            if label_dir.exists():
                datasets.append({
                    "type": "yolo",
                    "path": img_dir.parent,
                    "images": img_dir,
                    "labels": label_dir
                })
    
    return datasets


def parse_yolo_label(label_file, source_classes=None):
    """Parse a YOLO format label file and remap classes."""
    labels = []
    
    if not label_file.exists():
        return labels
    
    with open(label_file, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 5:
                class_id = int(parts[0])
                x_center = float(parts[1])
                y_center = float(parts[2])
                width = float(parts[3])
                height = float(parts[4])
                
                # Remap class if source_classes provided
                if source_classes and class_id < len(source_classes):
                    class_name = source_classes[class_id]
                    if class_name in CLASS_MAPPING:
                        new_class_id = CLASS_MAPPING[class_name]
                        if new_class_id >= 0:  # Skip excluded classes
                            labels.append({
                                "class_id": new_class_id,
                                "x_center": x_center,
                                "y_center": y_center,
                                "width": width,
                                "height": height
                            })
                else:
                    labels.append({
                        "class_id": class_id,
                        "x_center": x_center,
                        "y_center": y_center,
                        "width": width,
                        "height": height
                    })
    
    return labels


def write_yolo_label(label_file, labels):
    """Write labels in YOLO format."""
    with open(label_file, 'w') as f:
        for label in labels:
            line = f"{label['class_id']} {label['x_center']:.6f} {label['y_center']:.6f} {label['width']:.6f} {label['height']:.6f}\n"
            f.write(line)


def load_dataset_config(config_file):
    """Load dataset configuration from YAML file."""
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    # Extract class names
    if 'names' in config:
        if isinstance(config['names'], dict):
            return list(config['names'].values())
        else:
            return config['names']
    
    return None


def copy_and_remap(src_img, src_label, dst_img, dst_label, source_classes, prefix):
    """Copy image and remapped label to destination."""
    try:
        # Copy image with prefix
        new_img_name = f"{prefix}_{src_img.name}"
        shutil.copy2(src_img, dst_img / new_img_name)
        
        # Parse and remap labels
        labels = parse_yolo_label(src_label, source_classes)
        
        if labels:  # Only write if there are valid labels
            new_label_name = f"{prefix}_{src_label.stem}.txt"
            write_yolo_label(dst_label / new_label_name, labels)
            return True
        else:
            # Still keep image for negative samples
            return True
            
    except Exception as e:
        print(f"Error processing {src_img}: {e}")
        return False


# ============================================================================
# MAIN MERGE FUNCTIONS
# ============================================================================

def merge_roboflow_dataset(dataset, output_dir, prefix, stats):
    """Merge a Roboflow-format dataset."""
    config = load_dataset_config(dataset['config'])
    base_path = dataset['path']
    
    processed = 0
    
    for split in ['train', 'valid', 'test']:
        img_dir = base_path / split / 'images'
        label_dir = base_path / split / 'labels'
        
        if not img_dir.exists():
            continue
        
        # Map split names
        out_split = 'valid' if split == 'val' else split
        out_img_dir = output_dir / out_split / 'images'
        out_label_dir = output_dir / out_split / 'labels'
        
        out_img_dir.mkdir(parents=True, exist_ok=True)
        out_label_dir.mkdir(parents=True, exist_ok=True)
        
        # Process each image
        for img_file in img_dir.glob('*'):
            if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']:
                label_file = label_dir / f"{img_file.stem}.txt"
                
                if copy_and_remap(img_file, label_file, out_img_dir, out_label_dir, config, prefix):
                    processed += 1
                    
                    # Update class stats
                    if label_file.exists():
                        labels = parse_yolo_label(label_file, config)
                        for label in labels:
                            stats['classes'][label['class_id']] += 1
    
    stats['images'] += processed
    return processed


def merge_yolo_dataset(dataset, output_dir, prefix, stats, split_data=True):
    """Merge a standard YOLO-format dataset."""
    img_dir = dataset['images']
    label_dir = dataset['labels']
    
    # Get all images
    images = list(img_dir.glob('*'))
    images = [img for img in images if img.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']]
    
    if split_data:
        # Shuffle and split
        random.shuffle(images)
        n_train = int(len(images) * TRAIN_RATIO)
        n_val = int(len(images) * VAL_RATIO)
        
        splits = {
            'train': images[:n_train],
            'valid': images[n_train:n_train + n_val],
            'test': images[n_train + n_val:]
        }
    else:
        splits = {'train': images}
    
    processed = 0
    
    for split_name, split_images in splits.items():
        out_img_dir = output_dir / split_name / 'images'
        out_label_dir = output_dir / split_name / 'labels'
        
        out_img_dir.mkdir(parents=True, exist_ok=True)
        out_label_dir.mkdir(parents=True, exist_ok=True)
        
        for img_file in split_images:
            label_file = label_dir / f"{img_file.stem}.txt"
            
            if copy_and_remap(img_file, label_file, out_img_dir, out_label_dir, None, prefix):
                processed += 1
    
    stats['images'] += processed
    return processed


def merge_all_datasets(input_dir, output_dir, categories=None):
    """Merge all datasets into a unified format."""
    print(f"\n📂 Scanning for datasets in: {input_dir}")
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Clear output directory
    if output_path.exists():
        print(f"⚠️  Clearing existing output directory: {output_path}")
        shutil.rmtree(output_path)
    
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Statistics
    stats = {
        'images': 0,
        'classes': defaultdict(int),
        'datasets': 0
    }
    
    # Process each category
    category_dirs = ['fire_smoke', 'fight_violence', 'face_detection']
    
    if categories:
        category_dirs = [c for c in category_dirs if c in categories]
    
    for category in category_dirs:
        category_path = input_path / category
        if not category_path.exists():
            print(f"⚠️  Category not found: {category}")
            continue
        
        print(f"\n{'='*60}")
        print(f"📁 Processing: {category.upper()}")
        print('='*60)
        
        # Find datasets in this category
        datasets = find_datasets(category_path)
        print(f"   Found {len(datasets)} datasets")
        
        for i, dataset in enumerate(datasets):
            prefix = f"{category[:4]}_{i:03d}"
            
            if dataset['type'] == 'roboflow':
                print(f"   📥 Merging (Roboflow): {dataset['path'].name}")
                merge_roboflow_dataset(dataset, output_path, prefix, stats)
            else:
                print(f"   📥 Merging (YOLO): {dataset['path'].name}")
                merge_yolo_dataset(dataset, output_path, prefix, stats)
            
            stats['datasets'] += 1
    
    return stats


def generate_yaml_config(output_dir, stats):
    """Generate the final YAML configuration file."""
    output_path = Path(output_dir)
    
    # Count images in each split
    train_count = len(list((output_path / 'train' / 'images').glob('*'))) if (output_path / 'train' / 'images').exists() else 0
    val_count = len(list((output_path / 'valid' / 'images').glob('*'))) if (output_path / 'valid' / 'images').exists() else 0
    test_count = len(list((output_path / 'test' / 'images').glob('*'))) if (output_path / 'test' / 'images').exists() else 0
    
    # Determine which classes have data
    active_classes = {k: v for k, v in TARGET_CLASSES.items() if stats['classes'].get(k, 0) > 0}
    
    # If no classes detected, use all classes
    if not active_classes:
        active_classes = TARGET_CLASSES
    
    yaml_content = f"""# Combined Dataset Configuration
# Generated by merge_datasets.py
# Optimized for Jetson Orin Nano deployment

path: {output_path.absolute()}
train: train/images
val: valid/images
test: test/images

# Class definitions
names:
"""
    
    for class_id, class_name in sorted(active_classes.items()):
        yaml_content += f"  {class_id}: {class_name}\n"
    
    yaml_content += f"""
# Dataset Statistics
# Total images: {stats['images']}
# Train: {train_count}
# Valid: {val_count}
# Test: {test_count}
# Datasets merged: {stats['datasets']}

# Class distribution:
"""
    
    for class_id, count in sorted(stats['classes'].items()):
        class_name = TARGET_CLASSES.get(class_id, f"class_{class_id}")
        yaml_content += f"#   {class_name}: {count}\n"
    
    config_path = output_path / 'data.yaml'
    with open(config_path, 'w') as f:
        f.write(yaml_content)
    
    print(f"\n✅ Generated config: {config_path}")
    return config_path


def verify_dataset(dataset_dir):
    """Verify the merged dataset integrity."""
    print("\n🔍 Verifying dataset...")
    
    dataset_path = Path(dataset_dir)
    issues = []
    
    for split in ['train', 'valid', 'test']:
        img_dir = dataset_path / split / 'images'
        label_dir = dataset_path / split / 'labels'
        
        if not img_dir.exists():
            issues.append(f"Missing {split}/images directory")
            continue
        
        images = list(img_dir.glob('*'))
        labels = list(label_dir.glob('*.txt')) if label_dir.exists() else []
        
        print(f"   {split}: {len(images)} images, {len(labels)} labels")
        
        # Check for orphan labels
        img_stems = {img.stem for img in images}
        for label in labels:
            if label.stem not in img_stems:
                issues.append(f"Orphan label: {label}")
    
    if issues:
        print(f"\n⚠️  Found {len(issues)} issues:")
        for issue in issues[:10]:
            print(f"   - {issue}")
    else:
        print("\n✅ Dataset verification passed!")
    
    return len(issues) == 0


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Merge multiple datasets into unified YOLO format",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--input", type=str, default="./datasets",
                        help="Input directory containing downloaded datasets")
    parser.add_argument("--output", type=str, default="./datasets/combined",
                        help="Output directory for merged dataset")
    parser.add_argument("--fire-only", action="store_true",
                        help="Only merge fire/smoke datasets")
    parser.add_argument("--fight-only", action="store_true",
                        help="Only merge fight/violence datasets")
    parser.add_argument("--face-only", action="store_true",
                        help="Only merge face detection datasets")
    parser.add_argument("--verify", action="store_true",
                        help="Verify existing merged dataset")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for reproducibility")
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Set random seed
    random.seed(args.seed)
    
    # Verify mode
    if args.verify:
        verify_dataset(args.output)
        return
    
    # Determine categories to merge
    categories = None
    if args.fire_only:
        categories = ['fire_smoke']
    elif args.fight_only:
        categories = ['fight_violence']
    elif args.face_only:
        categories = ['face_detection']
    
    # Merge datasets
    stats = merge_all_datasets(args.input, args.output, categories)
    
    # Generate config
    generate_yaml_config(args.output, stats)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 MERGE SUMMARY")
    print("="*60)
    print(f"   Datasets processed: {stats['datasets']}")
    print(f"   Total images: {stats['images']}")
    print(f"   Output directory: {args.output}")
    print("\n   Class distribution:")
    for class_id, count in sorted(stats['classes'].items()):
        class_name = TARGET_CLASSES.get(class_id, f"class_{class_id}")
        print(f"      {class_name}: {count}")
    
    # Verify
    print()
    verify_dataset(args.output)
    
    print("\n✅ Merge complete!")
    print("\nNext steps:")
    print(f"   1. Train: yolo train data={args.output}/data.yaml model=yolov8n.pt")
    print(f"   2. Export: yolo export model=best.pt format=engine device=0")


if __name__ == "__main__":
    main()
