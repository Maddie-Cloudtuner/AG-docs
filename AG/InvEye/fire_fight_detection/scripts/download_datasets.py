"""
Dataset Downloader for Fire & Fight Detection
Downloads datasets from Roboflow, Kaggle, and GitHub
"""

import os
import subprocess
import zipfile
import shutil
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).parent.parent / "datasets"
BASE_DIR.mkdir(exist_ok=True)


def download_roboflow_datasets():
    """Download datasets from Roboflow (requires API key)"""
    try:
        from roboflow import Roboflow
        
        # Get API key from environment or input
        api_key = os.environ.get("ROBOFLOW_API_KEY") or input("Enter Roboflow API Key: ")
        rf = Roboflow(api_key=api_key)
        
        # Fire Detection Dataset
        print("📥 Downloading Fire Detection dataset...")
        try:
            project = rf.workspace("roboflow-universe-projects").project("fire-detection-pjbqs")
            project.version(1).download("yolov8", location=str(BASE_DIR / "fire_roboflow"))
        except Exception as e:
            print(f"   ⚠️ Fire dataset failed: {e}")
        
        # Smoke Detection Dataset  
        print("📥 Downloading Smoke Detection dataset...")
        try:
            project = rf.workspace("smoke-detection-cdyif").project("smoke-detection-iyy4l")
            project.version(1).download("yolov8", location=str(BASE_DIR / "smoke_roboflow"))
        except Exception as e:
            print(f"   ⚠️ Smoke dataset failed: {e}")
        
        print("✅ Roboflow datasets downloaded!")
        return True
        
    except ImportError:
        print("⚠️ Roboflow not installed. Run: pip install roboflow")
        return False


def download_kaggle_datasets():
    """Download datasets from Kaggle"""
    try:
        # Check if kaggle is configured
        kaggle_config = Path.home() / ".kaggle" / "kaggle.json"
        if not kaggle_config.exists():
            print("⚠️ Kaggle not configured. Please setup ~/.kaggle/kaggle.json")
            return False
        
        datasets = [
            ("phylake1337/fire-dataset", "kaggle_fire"),
            ("mohamedmustafa/real-life-violence-situations-dataset", "kaggle_violence"),
        ]
        
        for dataset_name, folder_name in datasets:
            output_path = BASE_DIR / folder_name
            output_path.mkdir(exist_ok=True)
            
            print(f"📥 Downloading {dataset_name}...")
            try:
                subprocess.run([
                    "kaggle", "datasets", "download", "-d", dataset_name,
                    "-p", str(output_path)
                ], check=True)
            except subprocess.CalledProcessError as e:
                print(f"   ⚠️ Failed: {e}")
                continue
        
        # Unzip files
        for zip_file in BASE_DIR.glob("**/*.zip"):
            print(f"📦 Extracting {zip_file.name}...")
            with zipfile.ZipFile(zip_file, 'r') as z:
                z.extractall(zip_file.parent)
            zip_file.unlink()
            
        print("✅ Kaggle datasets downloaded!")
        return True
        
    except Exception as e:
        print(f"⚠️ Kaggle download failed: {e}")
        return False


def download_github_datasets():
    """Clone datasets from GitHub"""
    repos = [
        ("https://github.com/gaiasd/DFireDataset.git", "dfire"),
    ]
    
    for url, name in repos:
        dest = BASE_DIR / name
        if not dest.exists():
            print(f"📥 Cloning {name}...")
            try:
                subprocess.run(["git", "clone", "--depth", "1", url, str(dest)], check=True)
            except subprocess.CalledProcessError as e:
                print(f"   ⚠️ Clone failed: {e}")
        else:
            print(f"✓ {name} already exists")
    
    print("✅ GitHub datasets cloned!")


def print_summary():
    """Print summary of downloaded datasets"""
    print("\n" + "=" * 50)
    print("📊 Dataset Summary")
    print("=" * 50)
    
    for dataset_dir in BASE_DIR.iterdir():
        if dataset_dir.is_dir():
            # Count images
            images = list(dataset_dir.glob("**/*.jpg")) + \
                     list(dataset_dir.glob("**/*.jpeg")) + \
                     list(dataset_dir.glob("**/*.png"))
            print(f"  📂 {dataset_dir.name}: {len(images)} images")
    
    print(f"\n📂 All datasets saved to: {BASE_DIR.absolute()}")


def main():
    print("=" * 50)
    print("🔥 Fire & Fight Detection Dataset Downloader")
    print("=" * 50)
    print(f"📂 Output directory: {BASE_DIR.absolute()}\n")
    
    # Try each source
    print("\n[1/3] Roboflow Datasets")
    print("-" * 30)
    download_roboflow_datasets()
    
    print("\n[2/3] Kaggle Datasets")
    print("-" * 30)
    download_kaggle_datasets()
    
    print("\n[3/3] GitHub Datasets")
    print("-" * 30)
    download_github_datasets()
    
    # Summary
    print_summary()
    
    print("\n✅ Dataset download complete!")
    print("Next step: Run merge_datasets.py to combine all datasets")


if __name__ == "__main__":
    main()
