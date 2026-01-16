#!/usr/bin/env python3
"""
Indian Petrol Pump Analytics - YOLO11 Training Script (Ubuntu/Jetson)
======================================================================
Run on: Ubuntu with External GPU / Jetson Orin Nano Dev Kit

Usage:
    # Full pipeline (download + merge + train + export)
    python3 train_petrol_pump_yolo11.py --full

    # Step by step:
    python3 train_petrol_pump_yolo11.py --download-only   # Download datasets
    python3 train_petrol_pump_yolo11.py --train           # Train model
    python3 train_petrol_pump_yolo11.py --export          # Export ONNX/TensorRT

    # Custom options:
    python3 train_petrol_pump_yolo11.py --full --epochs 50 --batch 8
"""

import os
import sys
import shutil
import argparse
import platform
import subprocess
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

# ============================================================================
# CONFIGURATION
# ============================================================================

# Detect platform
IS_JETSON = os.path.exists('/etc/nv_tegra_release')
IS_UBUNTU = platform.system() == 'Linux'

# Base directories
if IS_JETSON:
    BASE_DIR = Path('/home/nvidia/petrol_pump_training')
elif IS_UBUNTU:
    BASE_DIR = Path.home() / 'petrol_pump_training'
else:
    BASE_DIR = Path(__file__).parent / 'training_workspace'

DATASETS_DIR = BASE_DIR / 'source_datasets'
OUTPUT_DIR = BASE_DIR / 'Final_Dataset'
MODELS_DIR = BASE_DIR / 'models'

# Master Schema (18 classes)
MASTER_SCHEMA = {
    0: 'person', 1: 'car', 2: 'motorcycle', 3: 'heavy_vehicle',
    4: 'fire', 5: 'smoke', 6: 'cigarette', 7: 'violence',
    8: 'nozzle', 9: 'testing_jar', 10: 'du_cover_open', 11: 'manhole_open',
    12: 'air_pump', 13: 'uniform', 14: 'helmet', 15: 'plastic_item',
    16: 'garbage', 17: 'cell_phone'
}

# ============================================================================
# VERIFIED PUBLIC DATASET CONFIGURATIONS
# ============================================================================

DATASET_CONFIGS = {
    # --- FIRE & SMOKE ---
    'd_fire': {
        'type': 'git',
        'url': 'https://github.com/gaiasd/DFireDataset.git',
        'mapping': {0: 4, 1: 5},  # fire->4, smoke->5
        'description': 'D-Fire Dataset (21,000+ images, YOLO ready)'
    },
    'fire_kaggle': {
        'type': 'kaggle',
        'kaggle': 'phylake1337/fire-dataset',
        'mapping': {0: 4, 1: 4},  # fire images
        'description': 'FIRE Dataset Kaggle (2,700+ outdoor fire images)'
    },
    
    # --- VIOLENCE DETECTION ---
    'violence_real': {
        'type': 'kaggle',
        'kaggle': 'mohamedmustafa/real-life-violence-situations-dataset',
        'mapping': {0: 7},  # violence->7
        'description': 'Real Life Violence (2,000 videos)'
    },
    'ucf_crime': {
        'type': 'kaggle',
        'kaggle': 'odins0n/ucf-crime-dataset',
        'mapping': {0: 7},  # anomaly/violence->7
        'description': 'UCF Crime Dataset (1,900 videos)'
    },
    
    # --- LOW-LIGHT & NIGHT ---
    'exdark': {
        'type': 'git',
        'url': 'https://github.com/cs-chan/Exclusively-Dark-Image-Dataset.git',
        'mapping': {
            0: 0,   # Bicycle -> motorcycle (close enough)
            1: 1,   # Boat -> skip
            2: 15,  # Bottle -> plastic_item
            3: 3,   # Bus -> heavy_vehicle
            4: 1,   # Car -> car
            5: 15,  # Chair -> plastic_item
            6: 0,   # Person (various) -> person
            7: 2,   # Motorbike -> motorcycle
            8: 0,   # People -> person
        },
        'description': 'ExDark (7,363 low-light images, 12 classes)'
    },
    
    # --- INDIAN DRIVING ---
    'idd': {
        'type': 'manual',
        'url': 'https://idd.insaan.iiit.ac.in/',
        'mapping': {
            0: 0,   # person -> person
            1: 0,   # rider -> person
            2: 1,   # car -> car
            3: 2,   # motorcycle -> motorcycle
            4: 2,   # autorickshaw -> motorcycle
            5: 3,   # truck -> heavy_vehicle
            6: 3,   # bus -> heavy_vehicle
        },
        'description': 'India Driving Dataset (10K+ Indian street images) - MANUAL DOWNLOAD'
    },
    
    # --- CROWD/PERSON DETECTION ---
    'crowdhuman': {
        'type': 'manual',
        'url': 'https://www.crowdhuman.org/',
        'mapping': {0: 0},  # person -> person
        'description': 'CrowdHuman (dense crowd scenarios) - MANUAL DOWNLOAD'
    },
    
    # --- FACE DETECTION ---
    'face_detection': {
        'type': 'kaggle',
        'kaggle': 'fareselmenshawii/face-detection-dataset',
        'mapping': {0: 0},  # face -> person (for counting)
        'description': 'Face Detection (16,700 YOLO format)'
    },
}

# Training configuration - Optimized for Jetson Orin Nano
TRAINING_CONFIG = {
    'model': 'yolo11n.pt',  # Nano model for edge deployment
    'epochs': 100,
    'imgsz': 640,
    'batch': 8 if IS_JETSON else 16,  # Smaller batch on Jetson
    'patience': 20,
    'workers': 2 if IS_JETSON else 4,
    'device': 0,  # GPU
    'amp': True,  # Mixed precision
    'cache': True if not IS_JETSON else False,  # Cache on disk if enough RAM
}


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def print_banner():
    """Print startup banner."""
    print("=" * 60)
    print("🛢️  INDIAN PETROL PUMP ANALYTICS - YOLO11 TRAINING")
    print("=" * 60)
    print(f"Platform: {'Jetson Orin Nano' if IS_JETSON else 'Windows/Linux'}")
    print(f"Base Dir: {BASE_DIR}")
    print(f"Classes:  {len(MASTER_SCHEMA)}")
    print("=" * 60)


def setup_directories():
    """Create all necessary directories."""
    print("\n📁 Setting up directories...")
    for d in [DATASETS_DIR, OUTPUT_DIR, MODELS_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    
    # Create output structure
    for split in ['train', 'val']:
        (OUTPUT_DIR / 'images' / split).mkdir(parents=True, exist_ok=True)
        (OUTPUT_DIR / 'labels' / split).mkdir(parents=True, exist_ok=True)
    
    # Create placeholder folders for manual data collection
    placeholders = ['du_cover_open', 'air_pump']
    placeholder_dir = OUTPUT_DIR / 'manual_collection_needed'
    placeholder_dir.mkdir(exist_ok=True)
    for name in placeholders:
        (placeholder_dir / name).mkdir(exist_ok=True)
    
    print("✅ Directories created")


def install_dependencies():
    """Install required Python packages."""
    print("\n📦 Checking dependencies...")
    
    packages = ['ultralytics', 'gdown', 'PyYAML', 'tqdm']
    
    for pkg in packages:
        try:
            __import__(pkg.lower().replace('-', '_'))
        except ImportError:
            print(f"   Installing {pkg}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', pkg])
    
    print("✅ Dependencies ready")


# ============================================================================
# DATASET DOWNLOAD (Ubuntu/Jetson)
# ============================================================================

def run_cmd(cmd: List[str], cwd: Optional[Path] = None) -> bool:
    """Run shell command and return success."""
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False


def download_git_repo(url: str, dest_dir: Path) -> bool:
    """Clone a git repository."""
    if dest_dir.exists() and any(dest_dir.iterdir()):
        print(f"      Already exists, skipping clone")
        return True
    
    print(f"      git clone {url}")
    return run_cmd(['git', 'clone', '--depth', '1', url, str(dest_dir)])


def download_kaggle_dataset(dataset_slug: str, dest_dir: Path) -> bool:
    """Download dataset from Kaggle."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    # Check kaggle CLI
    if not run_cmd(['kaggle', '--version']):
        print("      ⚠️ Kaggle CLI not found. Install: pip3 install kaggle")
        print("         Then put kaggle.json in ~/.kaggle/")
        return False
    
    print(f"      kaggle datasets download -d {dataset_slug}")
    if run_cmd(['kaggle', 'datasets', 'download', '-d', dataset_slug, 
                '-p', str(dest_dir), '--unzip']):
        return True
    return False


def download_with_wget(url: str, dest_path: Path) -> bool:
    """Download file using wget."""
    print(f"      wget {url}")
    return run_cmd(['wget', '-q', '-O', str(dest_path), url])


def extract_archive(archive_path: Path, dest_dir: Path):
    """Extract zip/tar archive."""
    import zipfile
    import tarfile
    
    if archive_path.suffix == '.zip':
        with zipfile.ZipFile(archive_path, 'r') as z:
            z.extractall(dest_dir)
    elif archive_path.suffix in ['.tar', '.gz', '.tgz']:
        with tarfile.open(archive_path) as t:
            t.extractall(dest_dir)
    archive_path.unlink()


def download_all_datasets():
    """Download all configured datasets."""
    print("\n📥 Downloading datasets...")
    print("=" * 50)
    
    manual_needed = []
    
    for name, config in DATASET_CONFIGS.items():
        dest_dir = DATASETS_DIR / name
        dtype = config.get('type', 'url')
        
        print(f"\n📦 {name}: {config['description']}")
        
        # Skip if already exists
        if dest_dir.exists() and any(dest_dir.iterdir()):
            print(f"   ✅ Already downloaded")
            continue
        
        dest_dir.mkdir(parents=True, exist_ok=True)
        success = False
        
        if dtype == 'git':
            success = download_git_repo(config['url'], dest_dir)
            
        elif dtype == 'kaggle':
            success = download_kaggle_dataset(config['kaggle'], dest_dir)
            
        elif dtype == 'manual':
            manual_needed.append((name, config['url'], config['description']))
            print(f"   ⚠️ MANUAL DOWNLOAD REQUIRED")
            print(f"      URL: {config['url']}")
            print(f"      Save to: {dest_dir}")
            continue
            
        elif dtype == 'url' or 'url' in config:
            zip_path = dest_dir / f'{name}.zip'
            if download_with_wget(config['url'], zip_path):
                if zip_path.exists():
                    extract_archive(zip_path, dest_dir)
                    success = True
        
        if success:
            print(f"   ✅ Downloaded successfully")
        else:
            print(f"   ❌ Download failed")
    
    # Print manual download summary
    if manual_needed:
        print("\n" + "=" * 50)
        print("⚠️  MANUAL DOWNLOADS REQUIRED:")
        print("=" * 50)
        for name, url, desc in manual_needed:
            print(f"\n   {name}: {desc}")
            print(f"   URL: {url}")
            print(f"   Save to: {DATASETS_DIR / name}")
    
    print("\n✅ Download phase complete")


# ============================================================================
# DATASET MERGING & CLASS REMAPPING
# ============================================================================

def remap_labels(label_path: Path, mapping: Dict[int, Optional[int]]) -> List[str]:
    """Remap class IDs in a YOLO label file."""
    if not label_path.exists():
        return []
    
    remapped = []
    with open(label_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 5:
                try:
                    src_id = int(parts[0])
                    if src_id in mapping and mapping[src_id] is not None:
                        target_id = mapping[src_id]
                        remapped.append(f"{target_id} {' '.join(parts[1:])}")
                except ValueError:
                    continue
    return remapped


def find_yolo_structure(base_path: Path) -> Tuple[Optional[Path], Optional[Path]]:
    """Find YOLO images/labels directories in various folder structures."""
    candidates = [
        (base_path / 'images', base_path / 'labels'),
        (base_path / 'train' / 'images', base_path / 'train' / 'labels'),
        (base_path / 'data' / 'images', base_path / 'data' / 'labels'),
        (base_path / 'dataset' / 'images', base_path / 'dataset' / 'labels'),
    ]
    
    # Also check first-level subdirectories
    if base_path.exists():
        for subdir in base_path.iterdir():
            if subdir.is_dir():
                candidates.append((subdir / 'images', subdir / 'labels'))
                candidates.append((subdir / 'train' / 'images', subdir / 'train' / 'labels'))
    
    for img_dir, lbl_dir in candidates:
        if img_dir.exists() and lbl_dir.exists():
            return img_dir, lbl_dir
    
    return None, None


def merge_datasets():
    """Merge all source datasets into Final_Dataset with class remapping."""
    print("\n🔄 Merging datasets with class remapping...")
    
    stats = defaultdict(int)
    total_images = 0
    img_exts = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
    
    for name, config in DATASET_CONFIGS.items():
        source_dir = DATASETS_DIR / name
        
        if not source_dir.exists():
            print(f"   ⚠️  {name}: Not found, skipping")
            continue
        
        img_dir, lbl_dir = find_yolo_structure(source_dir)
        
        if img_dir is None:
            print(f"   ⚠️  {name}: No YOLO structure found")
            continue
        
        count = 0
        mapping = config['mapping']
        
        # Process both train and val splits if they exist
        for split_name in ['train', 'val', '']:
            img_split = img_dir / split_name if split_name else img_dir
            lbl_split = lbl_dir / split_name if split_name else lbl_dir
            out_split = 'train' if split_name != 'val' else 'val'
            
            if not img_split.exists():
                continue
            
            for img_path in img_split.iterdir():
                if img_path.suffix.lower() not in img_exts:
                    continue
                
                lbl_path = lbl_split / f'{img_path.stem}.txt'
                remapped = remap_labels(lbl_path, mapping)
                
                if not remapped:
                    continue
                
                # Copy with unique prefix
                unique_name = f'{name}_{img_path.stem}'
                out_img = OUTPUT_DIR / 'images' / out_split / f'{unique_name}{img_path.suffix}'
                out_lbl = OUTPUT_DIR / 'labels' / out_split / f'{unique_name}.txt'
                
                shutil.copy2(img_path, out_img)
                with open(out_lbl, 'w') as f:
                    f.write('\n'.join(remapped))
                
                count += 1
                for line in remapped:
                    cls_id = int(line.split()[0])
                    stats[cls_id] += 1
        
        print(f"   ✅ {name}: {count} images merged")
        total_images += count
    
    print(f"\n📊 Total: {total_images} images merged")
    print("\n📈 Class Distribution:")
    for cls_id in sorted(MASTER_SCHEMA.keys()):
        count = stats.get(cls_id, 0)
        marker = '✅' if count > 0 else '⚠️ (needs data)'
        print(f"   {cls_id:2d}: {MASTER_SCHEMA[cls_id]:<15} = {count:>5} {marker}")
    
    return stats


def generate_data_yaml():
    """Generate data.yaml for YOLO training."""
    import yaml
    
    yaml_content = {
        'path': str(OUTPUT_DIR.absolute()),
        'train': 'images/train',
        'val': 'images/val',
        'nc': len(MASTER_SCHEMA),
        'names': MASTER_SCHEMA
    }
    
    yaml_path = OUTPUT_DIR / 'data.yaml'
    with open(yaml_path, 'w') as f:
        yaml.dump(yaml_content, f, default_flow_style=False, sort_keys=False)
    
    print(f"\n✅ Generated: {yaml_path}")
    return yaml_path


# ============================================================================
# TRAINING
# ============================================================================

def train_model():
    """Train YOLO11 model."""
    from ultralytics import YOLO
    
    yaml_path = OUTPUT_DIR / 'data.yaml'
    
    if not yaml_path.exists():
        print("❌ data.yaml not found. Run with --download first.")
        return None
    
    print("\n🚀 Starting YOLO11 Training...")
    print(f"   Model: {TRAINING_CONFIG['model']}")
    print(f"   Epochs: {TRAINING_CONFIG['epochs']}")
    print(f"   Batch Size: {TRAINING_CONFIG['batch']}")
    print(f"   Image Size: {TRAINING_CONFIG['imgsz']}")
    
    # Load model
    model = YOLO(TRAINING_CONFIG['model'])
    
    # Train
    results = model.train(
        data=str(yaml_path),
        epochs=TRAINING_CONFIG['epochs'],
        imgsz=TRAINING_CONFIG['imgsz'],
        batch=TRAINING_CONFIG['batch'],
        patience=TRAINING_CONFIG['patience'],
        device=TRAINING_CONFIG['device'],
        workers=TRAINING_CONFIG['workers'],
        project=str(MODELS_DIR),
        name='petrol_pump_yolo11',
        exist_ok=True,
        amp=TRAINING_CONFIG['amp'],
        cache=TRAINING_CONFIG['cache'],
        # Augmentation for Indian conditions
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,  # Important for low-light
        degrees=10,
        translate=0.1,
        scale=0.5,
        flipud=0.0,
        fliplr=0.5,
        mosaic=1.0,
        mixup=0.1,
    )
    
    best_model_path = MODELS_DIR / 'petrol_pump_yolo11' / 'weights' / 'best.pt'
    print(f"\n✅ Training complete!")
    print(f"   Best model: {best_model_path}")
    
    return best_model_path


# ============================================================================
# EXPORT FOR JETSON
# ============================================================================

def export_model(model_path: Optional[Path] = None):
    """Export model to ONNX and TensorRT for Jetson deployment."""
    from ultralytics import YOLO
    
    if model_path is None:
        model_path = MODELS_DIR / 'petrol_pump_yolo11' / 'weights' / 'best.pt'
    
    if not model_path.exists():
        print(f"❌ Model not found: {model_path}")
        return
    
    print(f"\n📦 Exporting model: {model_path}")
    
    model = YOLO(str(model_path))
    
    # Export to ONNX
    print("   → Exporting to ONNX...")
    model.export(format='onnx', imgsz=640, simplify=True, opset=12)
    
    # Export to TensorRT (if on Jetson)
    if IS_JETSON:
        print("   → Exporting to TensorRT (optimized for Jetson)...")
        try:
            model.export(format='engine', imgsz=640, half=True, device=0)
        except Exception as e:
            print(f"   ⚠️ TensorRT export failed: {e}")
            print("      You can export later using: model.export(format='engine')")
    
    print("\n✅ Export complete!")
    print(f"   📁 Models saved in: {model_path.parent}")
    
    # List exported files
    for f in model_path.parent.iterdir():
        print(f"      - {f.name}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Indian Petrol Pump Analytics - YOLO11 Training',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--download-only', action='store_true',
                        help='Only download and merge datasets')
    parser.add_argument('--train', action='store_true',
                        help='Train the model (assumes data exists)')
    parser.add_argument('--export', action='store_true',
                        help='Export trained model to ONNX/TensorRT')
    parser.add_argument('--full', action='store_true',
                        help='Full pipeline: download + merge + train + export')
    parser.add_argument('--epochs', type=int, default=100,
                        help='Number of training epochs (default: 100)')
    parser.add_argument('--batch', type=int, default=None,
                        help='Batch size (default: auto based on platform)')
    
    args = parser.parse_args()
    
    # Update config if args provided
    if args.epochs:
        TRAINING_CONFIG['epochs'] = args.epochs
    if args.batch:
        TRAINING_CONFIG['batch'] = args.batch
    
    print_banner()
    install_dependencies()
    setup_directories()
    
    if args.download_only or args.full:
        download_all_datasets()
        merge_datasets()
        generate_data_yaml()
    
    if args.train or args.full:
        model_path = train_model()
        if model_path and (args.export or args.full):
            export_model(model_path)
    
    if args.export and not args.full and not args.train:
        export_model()
    
    if not any([args.download_only, args.train, args.export, args.full]):
        print("\n⚠️ No action specified. Use one of:")
        print("   --download-only  : Download and prepare datasets")
        print("   --train          : Train model (data must exist)")
        print("   --export         : Export to ONNX/TensorRT")
        print("   --full           : Complete pipeline")
        print("\nExample: python train_petrol_pump_yolo11.py --full --epochs 50")


if __name__ == '__main__':
    main()
