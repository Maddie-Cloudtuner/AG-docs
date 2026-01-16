"""
Dataset Validation Script
==========================
Validates the merged YOLO dataset for:
1. Image-Label correspondence
2. Label format correctness
3. Class distribution
4. Missing files detection
5. data.yaml verification
"""

import os
from pathlib import Path
from collections import defaultdict
import yaml

# Configuration
DATASET_PATH = r"C:\Users\LENOVO\Desktop\my_docs\AG\InvEye\test 2.0\test 3.0-prod\merged_dataset"
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}

def validate_dataset():
    print("="*60)
    print(" DATASET VALIDATION REPORT")
    print("="*60)
    
    dataset_path = Path(DATASET_PATH)
    errors = []
    warnings = []
    stats = defaultdict(lambda: defaultdict(int))
    class_counts = defaultdict(int)
    
    # 1. Check data.yaml exists
    print("\n[1] Checking data.yaml...")
    yaml_path = dataset_path / "data.yaml"
    if yaml_path.exists():
        with open(yaml_path, 'r') as f:
            config = yaml.safe_load(f)
        print(f"   OK: data.yaml found")
        print(f"   Classes defined: {len(config.get('names', {}))}")
        for cid, cname in config.get('names', {}).items():
            print(f"      {cid}: {cname}")
    else:
        errors.append("data.yaml NOT FOUND!")
        config = {'names': {}}
    
    # 2. Check folder structure
    print("\n[2] Checking folder structure...")
    required_folders = [
        "images/train", "images/val", "images/test",
        "labels/train", "labels/val", "labels/test"
    ]
    for folder in required_folders:
        folder_path = dataset_path / folder
        if folder_path.exists():
            count = len(list(folder_path.iterdir()))
            print(f"   OK: {folder}/ ({count} files)")
            stats[folder.split('/')[1]][folder.split('/')[0]] = count
        else:
            errors.append(f"Missing folder: {folder}")
    
    # 3. Validate image-label pairs
    print("\n[3] Validating image-label correspondence...")
    
    for split in ['train', 'val', 'test']:
        img_dir = dataset_path / "images" / split
        lbl_dir = dataset_path / "labels" / split
        
        if not img_dir.exists() or not lbl_dir.exists():
            continue
        
        images = {f.stem for f in img_dir.iterdir() if f.suffix.lower() in IMAGE_EXTENSIONS}
        labels = {f.stem for f in lbl_dir.iterdir() if f.suffix == '.txt'}
        
        # Check for mismatches
        images_without_labels = images - labels
        labels_without_images = labels - images
        matched = images & labels
        
        print(f"\n   [{split.upper()}]")
        print(f"   Total images: {len(images)}")
        print(f"   Total labels: {len(labels)}")
        print(f"   Matched pairs: {len(matched)}")
        
        if images_without_labels:
            warnings.append(f"{split}: {len(images_without_labels)} images without labels")
            print(f"   WARNING: {len(images_without_labels)} images missing labels")
            if len(images_without_labels) <= 5:
                for name in list(images_without_labels)[:5]:
                    print(f"      - {name}")
        
        if labels_without_images:
            warnings.append(f"{split}: {len(labels_without_images)} labels without images")
            print(f"   WARNING: {len(labels_without_images)} labels missing images")
        
        # 4. Validate label format and count classes
        print(f"\n   Validating label format for {split}...")
        invalid_labels = 0
        empty_labels = 0
        
        for label_file in (lbl_dir).iterdir():
            if label_file.suffix != '.txt':
                continue
            
            try:
                with open(label_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().strip()
                
                if not content:
                    empty_labels += 1
                    continue
                
                for line in content.split('\n'):
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        try:
                            class_id = int(parts[0])
                            x, y, w, h = map(float, parts[1:5])
                            
                            # Count class
                            class_counts[class_id] += 1
                            
                            # Validate coordinates (0-1 range)
                            if not (0 <= x <= 1 and 0 <= y <= 1 and 0 <= w <= 1 and 0 <= h <= 1):
                                invalid_labels += 1
                        except ValueError:
                            invalid_labels += 1
                    elif len(parts) > 0:
                        invalid_labels += 1
                        
            except Exception as e:
                invalid_labels += 1
        
        if empty_labels > 0:
            warnings.append(f"{split}: {empty_labels} empty label files")
            print(f"   WARNING: {empty_labels} empty label files")
        
        if invalid_labels > 0:
            warnings.append(f"{split}: {invalid_labels} invalid label lines")
            print(f"   WARNING: {invalid_labels} invalid label lines")
        else:
            print(f"   OK: All labels have valid YOLO format")
    
    # 5. Class distribution
    print("\n[4] Class Distribution:")
    print("-" * 40)
    total_annotations = sum(class_counts.values())
    for class_id in sorted(class_counts.keys()):
        count = class_counts[class_id]
        class_name = config.get('names', {}).get(class_id, f"unknown_{class_id}")
        percentage = (count / total_annotations * 100) if total_annotations > 0 else 0
        bar = "#" * int(percentage / 2)
        print(f"   {class_id:2d}: {class_name:15s} | {count:7d} ({percentage:5.1f}%) {bar}")
    
    print(f"\n   Total annotations: {total_annotations}")
    
    # 6. Summary Report
    print("\n" + "="*60)
    print(" VALIDATION SUMMARY")
    print("="*60)
    
    if not errors and not warnings:
        print("\n   STATUS: PASS")
        print("   All checks passed! Dataset is ready for training.")
    elif errors:
        print(f"\n   STATUS: FAIL")
        print(f"   {len(errors)} error(s) found:")
        for e in errors:
            print(f"      - {e}")
    else:
        print(f"\n   STATUS: PASS (with {len(warnings)} warning(s))")
        print("   Warnings (non-critical):")
        for w in warnings[:10]:
            print(f"      - {w}")
    
    # 7. Quick stats
    print("\n   QUICK STATS:")
    train_imgs = stats['train'].get('images', 0)
    val_imgs = stats['val'].get('images', 0)
    test_imgs = stats['test'].get('images', 0)
    print(f"   - Train: {train_imgs:,} images")
    print(f"   - Val: {val_imgs:,} images")
    print(f"   - Test: {test_imgs:,} images")
    print(f"   - Total: {train_imgs + val_imgs + test_imgs:,} images")
    print(f"   - Classes used: {len(class_counts)}")
    print(f"   - Total annotations: {total_annotations:,}")
    
    print("\n" + "="*60)
    print(" VALIDATION COMPLETE")
    print("="*60)
    
    return len(errors) == 0

if __name__ == "__main__":
    validate_dataset()
