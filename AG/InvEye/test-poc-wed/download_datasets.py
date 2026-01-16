"""
🔥 👊 👤 Automated Dataset Downloader for AI Model Training
============================================================
Downloads public datasets for Fire, Fight, and Face Detection/Recognition

Author: InvEye Team
Usage:
    python download_datasets.py --all              # Download all datasets
    python download_datasets.py --fire             # Download fire/smoke datasets
    python download_datasets.py --fight            # Download fight/violence datasets
    python download_datasets.py --face             # Download face datasets
    python download_datasets.py --roboflow-key YOUR_KEY  # Set Roboflow API key

Requirements:
    pip install roboflow kaggle requests tqdm gdown
"""

import os
import sys
import argparse
import subprocess
import zipfile
import shutil
from pathlib import Path

# Try to import optional dependencies
try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    print("⚠️ tqdm not installed. Install with: pip install tqdm")

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("⚠️ requests not installed. Install with: pip install requests")


# ============================================================================
# CONFIGURATION - Edit these paths and API keys
# ============================================================================

# Base directory for all datasets
BASE_DIR = Path("./datasets")

# API Keys (set these or use command line arguments)
ROBOFLOW_API_KEY = os.environ.get("ROBOFLOW_API_KEY", "")
KAGGLE_USERNAME = os.environ.get("KAGGLE_USERNAME", "")
KAGGLE_KEY = os.environ.get("KAGGLE_KEY", "")


# ============================================================================
# DATASET DEFINITIONS
# ============================================================================

FIRE_DATASETS = {
    "roboflow": [
        {
            "name": "Fire Detection v2",
            "workspace": "fire-detection-kbsxn",
            "project": "fire-detection-qagzv",
            "version": 2,
            "images": "7,000+",
            "classes": ["fire", "smoke"]
        },
        {
            "name": "Fire & Smoke Dataset",
            "workspace": "fire-smoke-detection",
            "project": "fire-and-smoke-xspvt",
            "version": 1,
            "images": "4,500+",
            "classes": ["fire", "smoke", "neutral"]
        },
        {
            "name": "Smoke Detection",
            "workspace": "smoke-detection-cdyif",
            "project": "smoke-detection-iyy4l",
            "version": 1,
            "images": "3,200+",
            "classes": ["smoke"]
        },
    ],
    "kaggle": [
        {
            "name": "Fire Dataset (FireNet)",
            "dataset": "phylake1337/fire-dataset",
            "images": "2,700+",
            "classes": ["fire", "normal"]
        },
        {
            "name": "Corsican Fire Database",
            "dataset": "brsdincer/corsican-fire-database",
            "images": "1,000+",
            "classes": ["fire"]
        },
    ],
    "github": [
        {
            "name": "D-Fire Dataset",
            "repo": "https://github.com/gaiasd/DFireDataset.git",
            "images": "21,000+",
            "classes": ["fire", "smoke"]
        },
    ]
}

FIGHT_DATASETS = {
    "roboflow": [
        {
            "name": "Violence Detection (Security)",
            "workspace": "securityviolence",
            "project": "violence-detection-bxcxf",
            "version": 1,
            "images": "6,160",
            "classes": ["violence", "non_violence"]
        },
        {
            "name": "Violence_maksad",
            "workspace": "jaishreeram-uqqfn",
            "project": "violence_maksad",
            "version": 1,
            "images": "8,290",
            "classes": ["violence"]
        },
        {
            "name": "Fight Detection",
            "workspace": "fight-bx8oy",
            "project": "fight-detection-6hkff",
            "version": 1,
            "images": "5,000",
            "classes": ["fight", "no_fight"]
        },
        {
            "name": "Crime Detection",
            "workspace": "berdav",
            "project": "crime_detection-g30fi",
            "version": 1,
            "images": "8,686",
            "classes": ["knife", "Violence", "guns", "NonViolence"]
        },
        {
            "name": "Weapon Detection",
            "workspace": "yolov7test",
            "project": "weapon-detection",
            "version": 1,
            "images": "9,670",
            "classes": ["handgun", "pistol", "rifle", "weapon", "knife"]
        },
    ],
    "kaggle": [
        {
            "name": "Real Life Violence Situations",
            "dataset": "mohamedmustafa/real-life-violence-situations-dataset",
            "images": "11,000+ frames",
            "classes": ["violence", "non_violence"]
        },
        {
            "name": "Hockey Fight Videos",
            "dataset": "yassershrief/hockey-fight-videos",
            "images": "1,000 clips",
            "classes": ["fight", "no_fight"]
        },
        {
            "name": "UCF Crime Dataset",
            "dataset": "odins0n/ucf-crime-dataset",
            "images": "1,900 videos",
            "classes": ["anomaly", "normal"]
        },
    ],
    "github": [
        {
            "name": "RWF-2000 (Real World Fights)",
            "repo": "https://github.com/mcheng89/real-world-fight-dataset.git",
            "images": "2,000 clips",
            "classes": ["fight", "non_fight"]
        },
    ]
}

FACE_DATASETS = {
    "roboflow": [
        {
            "name": "Face Detection Dataset",
            "workspace": "mohamed-traore-2ekkp",
            "project": "face-detection-mik1i",
            "version": 1,
            "images": "5,000+",
            "classes": ["face"]
        },
        {
            "name": "Face Mask Detection",
            "workspace": "ditworkspace",
            "project": "face-mask-detection-yolov5",
            "version": 1,
            "images": "8,000+",
            "classes": ["with_mask", "without_mask"]
        },
    ],
    "kaggle": [
        {
            "name": "Face Detection Dataset",
            "dataset": "fareselmenshawii/face-detection-dataset",
            "images": "16,700",
            "classes": ["face"]
        },
        {
            "name": "Labeled Faces in the Wild (LFW)",
            "dataset": "jessicali9530/lfw-dataset",
            "images": "13,000+",
            "classes": ["5,749 identities"]
        },
        {
            "name": "CelebA Dataset",
            "dataset": "jessicali9530/celeba-dataset",
            "images": "202,599",
            "classes": ["10,177 celebrities"]
        },
    ],
    "github": [
        {
            "name": "FFHQ Dataset",
            "repo": "https://github.com/NVlabs/ffhq-dataset.git",
            "images": "70,000",
            "classes": ["high-quality faces"]
        },
    ],
    "direct": [
        {
            "name": "WIDER FACE",
            "url": "https://drive.google.com/uc?id=15hGDLhsx8bLgLcLM3Y_8rSRMX_XFDdZN",
            "images": "32,000+",
            "classes": ["face"]
        },
    ]
}


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def print_banner():
    """Print the script banner."""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║     🔥 👊 👤 AUTOMATED DATASET DOWNLOADER FOR AI TRAINING 👤 👊 🔥    ║
║                                                                    ║
║  Downloads: Fire/Smoke | Fight/Violence | Face Detection/Recognition  ║
╚════════════════════════════════════════════════════════════════════╝
    """)


def create_directories():
    """Create the dataset directory structure."""
    dirs = [
        BASE_DIR / "fire_smoke" / "roboflow",
        BASE_DIR / "fire_smoke" / "kaggle",
        BASE_DIR / "fire_smoke" / "github",
        BASE_DIR / "fight_violence" / "roboflow",
        BASE_DIR / "fight_violence" / "kaggle",
        BASE_DIR / "fight_violence" / "github",
        BASE_DIR / "face_detection" / "roboflow",
        BASE_DIR / "face_detection" / "kaggle",
        BASE_DIR / "face_detection" / "github",
        BASE_DIR / "face_recognition" / "kaggle",
        BASE_DIR / "combined",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        print(f"📁 Created: {d}")


def check_dependencies():
    """Check if required dependencies are installed."""
    missing = []
    
    try:
        import roboflow
    except ImportError:
        missing.append("roboflow")
    
    try:
        import kaggle
    except ImportError:
        missing.append("kaggle")
    
    try:
        import gdown
    except ImportError:
        missing.append("gdown")
    
    if missing:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing)}")
        print(f"   Install with: pip install {' '.join(missing)}")
        return False
    return True


def setup_kaggle_credentials():
    """Setup Kaggle API credentials."""
    kaggle_dir = Path.home() / ".kaggle"
    kaggle_json = kaggle_dir / "kaggle.json"
    
    if not kaggle_json.exists():
        print("\n⚠️  Kaggle credentials not found!")
        print("   1. Go to https://www.kaggle.com/account")
        print("   2. Click 'Create New API Token'")
        print("   3. Save kaggle.json to ~/.kaggle/")
        print("   4. Run this script again\n")
        return False
    return True


# ============================================================================
# DOWNLOAD FUNCTIONS
# ============================================================================

def download_roboflow_datasets(datasets, output_dir, api_key):
    """Download datasets from Roboflow."""
    if not api_key:
        print("❌ Roboflow API key not provided. Skipping Roboflow datasets.")
        print("   Get your free API key from: https://roboflow.com/")
        return
    
    try:
        from roboflow import Roboflow
    except ImportError:
        print("❌ roboflow package not installed. Run: pip install roboflow")
        return
    
    rf = Roboflow(api_key=api_key)
    
    for ds in datasets:
        print(f"\n📥 Downloading: {ds['name']} ({ds['images']} images)")
        print(f"   Classes: {', '.join(ds['classes'])}")
        
        try:
            project = rf.workspace(ds['workspace']).project(ds['project'])
            version = project.version(ds['version'])
            dataset = version.download("yolov8", location=str(output_dir / ds['project']))
            print(f"   ✅ Downloaded to: {output_dir / ds['project']}")
        except Exception as e:
            print(f"   ❌ Failed: {e}")


def download_kaggle_datasets(datasets, output_dir):
    """Download datasets from Kaggle."""
    if not setup_kaggle_credentials():
        return
    
    for ds in datasets:
        print(f"\n📥 Downloading: {ds['name']} ({ds['images']} images)")
        print(f"   Classes: {', '.join(ds['classes']) if isinstance(ds['classes'], list) else ds['classes']}")
        
        try:
            dataset_name = ds['dataset'].split('/')[-1]
            target_dir = output_dir / dataset_name
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Download using Kaggle CLI
            cmd = f"kaggle datasets download -d {ds['dataset']} -p {target_dir} --unzip"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"   ✅ Downloaded to: {target_dir}")
            else:
                print(f"   ❌ Failed: {result.stderr}")
        except Exception as e:
            print(f"   ❌ Failed: {e}")


def download_github_datasets(datasets, output_dir):
    """Clone datasets from GitHub."""
    for ds in datasets:
        print(f"\n📥 Cloning: {ds['name']} ({ds['images']} images)")
        print(f"   Classes: {', '.join(ds['classes']) if isinstance(ds['classes'], list) else ds['classes']}")
        
        try:
            repo_name = ds['repo'].split('/')[-1].replace('.git', '')
            target_dir = output_dir / repo_name
            
            if target_dir.exists():
                print(f"   ⚠️ Already exists: {target_dir}")
                continue
            
            cmd = f"git clone {ds['repo']} {target_dir}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"   ✅ Cloned to: {target_dir}")
            else:
                print(f"   ❌ Failed: {result.stderr}")
        except Exception as e:
            print(f"   ❌ Failed: {e}")


def download_direct_datasets(datasets, output_dir):
    """Download datasets from direct URLs using gdown."""
    try:
        import gdown
    except ImportError:
        print("❌ gdown not installed. Run: pip install gdown")
        return
    
    for ds in datasets:
        print(f"\n📥 Downloading: {ds['name']} ({ds['images']} images)")
        
        try:
            target_file = output_dir / f"{ds['name'].replace(' ', '_')}.zip"
            gdown.download(ds['url'], str(target_file), quiet=False)
            
            # Unzip if it's a zip file
            if target_file.suffix == '.zip':
                with zipfile.ZipFile(target_file, 'r') as zip_ref:
                    zip_ref.extractall(output_dir / ds['name'].replace(' ', '_'))
                target_file.unlink()
            
            print(f"   ✅ Downloaded to: {output_dir}")
        except Exception as e:
            print(f"   ❌ Failed: {e}")


# ============================================================================
# MAIN DOWNLOAD FUNCTIONS
# ============================================================================

def download_fire_datasets(api_key):
    """Download all fire/smoke detection datasets."""
    print("\n" + "="*60)
    print("🔥 FIRE & SMOKE DETECTION DATASETS")
    print("="*60)
    
    output_dir = BASE_DIR / "fire_smoke"
    
    # Roboflow
    print("\n--- Roboflow Datasets ---")
    download_roboflow_datasets(FIRE_DATASETS["roboflow"], output_dir / "roboflow", api_key)
    
    # Kaggle
    print("\n--- Kaggle Datasets ---")
    download_kaggle_datasets(FIRE_DATASETS["kaggle"], output_dir / "kaggle")
    
    # GitHub
    print("\n--- GitHub Datasets ---")
    download_github_datasets(FIRE_DATASETS["github"], output_dir / "github")


def download_fight_datasets(api_key):
    """Download all fight/violence detection datasets."""
    print("\n" + "="*60)
    print("👊 FIGHT & VIOLENCE DETECTION DATASETS")
    print("="*60)
    
    output_dir = BASE_DIR / "fight_violence"
    
    # Roboflow
    print("\n--- Roboflow Datasets ---")
    download_roboflow_datasets(FIGHT_DATASETS["roboflow"], output_dir / "roboflow", api_key)
    
    # Kaggle
    print("\n--- Kaggle Datasets ---")
    download_kaggle_datasets(FIGHT_DATASETS["kaggle"], output_dir / "kaggle")
    
    # GitHub
    print("\n--- GitHub Datasets ---")
    download_github_datasets(FIGHT_DATASETS["github"], output_dir / "github")


def download_face_datasets(api_key):
    """Download all face detection/recognition datasets."""
    print("\n" + "="*60)
    print("👤 FACE DETECTION & RECOGNITION DATASETS")
    print("="*60)
    
    output_dir = BASE_DIR / "face_detection"
    
    # Roboflow
    print("\n--- Roboflow Datasets ---")
    download_roboflow_datasets(FACE_DATASETS["roboflow"], output_dir / "roboflow", api_key)
    
    # Kaggle
    print("\n--- Kaggle Datasets ---")
    download_kaggle_datasets(FACE_DATASETS["kaggle"], output_dir / "kaggle")
    
    # GitHub
    print("\n--- GitHub Datasets ---")
    download_github_datasets(FACE_DATASETS["github"], output_dir / "github")
    
    # Direct downloads
    if "direct" in FACE_DATASETS:
        print("\n--- Direct Downloads ---")
        download_direct_datasets(FACE_DATASETS["direct"], output_dir)


def print_summary():
    """Print download summary."""
    print("\n" + "="*60)
    print("📊 DOWNLOAD SUMMARY")
    print("="*60)
    
    total_size = 0
    for category in ["fire_smoke", "fight_violence", "face_detection"]:
        cat_dir = BASE_DIR / category
        if cat_dir.exists():
            size = sum(f.stat().st_size for f in cat_dir.rglob('*') if f.is_file())
            total_size += size
            print(f"\n{category}:")
            for source in ["roboflow", "kaggle", "github"]:
                source_dir = cat_dir / source
                if source_dir.exists():
                    count = len(list(source_dir.iterdir()))
                    print(f"   {source}: {count} datasets")
    
    print(f"\n📦 Total size: {total_size / (1024**3):.2f} GB")
    print(f"📁 Location: {BASE_DIR.absolute()}")


def generate_yaml_config():
    """Generate a combined dataset YAML configuration."""
    yaml_content = """# Combined Dataset Configuration for YOLOv8
# Auto-generated by download_datasets.py

path: ./datasets/combined
train: train/images
val: valid/images
test: test/images

names:
  0: fire
  1: smoke
  2: fighting
  3: violence
  4: face
  5: weapon

# Dataset Statistics (after merging):
# - Fire: ~15,000 images
# - Smoke: ~10,000 images
# - Fighting: ~25,000 images
# - Face: ~50,000 images
"""
    
    config_path = BASE_DIR / "combined_dataset.yaml"
    with open(config_path, 'w') as f:
        f.write(yaml_content)
    
    print(f"\n✅ Generated config: {config_path}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Download public datasets for Fire, Fight, and Face Detection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python download_datasets.py --all --roboflow-key YOUR_KEY
  python download_datasets.py --fire --fight
  python download_datasets.py --face --skip-roboflow
        """
    )
    
    parser.add_argument("--all", action="store_true", help="Download all datasets")
    parser.add_argument("--fire", action="store_true", help="Download fire/smoke datasets")
    parser.add_argument("--fight", action="store_true", help="Download fight/violence datasets")
    parser.add_argument("--face", action="store_true", help="Download face detection datasets")
    parser.add_argument("--roboflow-key", type=str, help="Roboflow API key")
    parser.add_argument("--skip-roboflow", action="store_true", help="Skip Roboflow downloads")
    parser.add_argument("--skip-kaggle", action="store_true", help="Skip Kaggle downloads")
    parser.add_argument("--skip-github", action="store_true", help="Skip GitHub cloning")
    parser.add_argument("--output-dir", type=str, default="./datasets", help="Output directory")
    parser.add_argument("--list", action="store_true", help="List available datasets without downloading")
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Set output directory
    global BASE_DIR
    BASE_DIR = Path(args.output_dir)
    
    # Get API key
    api_key = args.roboflow_key or ROBOFLOW_API_KEY
    
    # List mode
    if args.list:
        print("\n📋 AVAILABLE DATASETS:\n")
        
        print("🔥 FIRE & SMOKE:")
        for source, datasets in FIRE_DATASETS.items():
            for ds in datasets:
                print(f"   [{source}] {ds['name']} - {ds['images']} images")
        
        print("\n👊 FIGHT & VIOLENCE:")
        for source, datasets in FIGHT_DATASETS.items():
            for ds in datasets:
                print(f"   [{source}] {ds['name']} - {ds['images']} images")
        
        print("\n👤 FACE DETECTION/RECOGNITION:")
        for source, datasets in FACE_DATASETS.items():
            for ds in datasets:
                print(f"   [{source}] {ds['name']} - {ds['images']} images")
        
        return
    
    # Create directories
    create_directories()
    
    # Check if any category is selected
    if not any([args.all, args.fire, args.fight, args.face]):
        print("⚠️  No dataset category selected!")
        print("   Use --all, --fire, --fight, or --face")
        print("   Run with --help for more options")
        return
    
    # Download datasets
    if args.all or args.fire:
        download_fire_datasets(api_key if not args.skip_roboflow else None)
    
    if args.all or args.fight:
        download_fight_datasets(api_key if not args.skip_roboflow else None)
    
    if args.all or args.face:
        download_face_datasets(api_key if not args.skip_roboflow else None)
    
    # Generate combined YAML config
    generate_yaml_config()
    
    # Print summary
    print_summary()
    
    print("\n✅ Download complete!")
    print("\nNext steps:")
    print("1. Verify downloaded datasets")
    print("2. Run merge script to combine datasets (coming soon)")
    print("3. Train with: yolo train data=datasets/combined_dataset.yaml")


if __name__ == "__main__":
    main()
