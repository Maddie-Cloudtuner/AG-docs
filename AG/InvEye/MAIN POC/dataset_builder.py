"""
Indian Petrol Pump Analytics - Dataset Builder
===============================================

This script merges multiple open-source datasets into a unified YOLO11 dataset
for Indian Petrol Pump surveillance analytics.

Author: Senior CV Data Engineer
Target: YOLO11 (Ultralytics)
Environment: Indian Petrol Pumps (Crowded, Low-light/Night compatible)

Usage:
    python dataset_builder.py --sources /path/to/source_datasets --output /path/to/Final_Dataset
    
    # Or with Roboflow API integration:
    python dataset_builder.py --use-roboflow --roboflow-key YOUR_API_KEY --output /path/to/Final_Dataset
"""

import os
import shutil
import argparse
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import random

# ============================================================================
# MASTER SCHEMA DEFINITION
# ============================================================================

MASTER_SCHEMA = {
    0: "person",
    1: "car",
    2: "motorcycle",
    3: "heavy_vehicle",
    4: "fire",
    5: "smoke",
    6: "cigarette",
    7: "violence",
    8: "nozzle",
    9: "testing_jar",
    10: "du_cover_open",
    11: "manhole_open",
    12: "air_pump",
    13: "uniform",
    14: "helmet",
    15: "plastic_item",
    16: "garbage",
    17: "cell_phone",
}

# Reverse mapping for lookup
CLASS_NAME_TO_ID = {v: k for k, v in MASTER_SCHEMA.items()}

# ============================================================================
# SOURCE DATASET MAPPINGS
# Each mapping: {source_class_id: target_class_id}
# ============================================================================

# 1. COCO General Dataset - Person, Car, Motorcycle, Truck, Bus, Bottles
COCO_MAPPING = {
    0: 0,    # person -> person
    2: 1,    # car -> car
    3: 2,    # motorcycle -> motorcycle
    7: 3,    # truck -> heavy_vehicle
    5: 3,    # bus -> heavy_vehicle
    39: 15,  # bottle -> plastic_item
    56: 15,  # chair -> plastic_item (outdoor furniture at pumps)
    # Ignore other COCO classes not relevant to petrol pumps
}

# 2. Indian Driving Dataset (IDD) - Traffic classes
IDD_MAPPING = {
    0: 0,    # person -> person
    1: 1,    # car -> car
    2: 2,    # motorcycle -> motorcycle (includes bikes)
    3: 3,    # truck -> heavy_vehicle
    4: 3,    # bus -> heavy_vehicle
    5: 2,    # autorickshaw -> motorcycle (similar class behavior)
    # Note: Map based on actual IDD class names
}

# Alternative IDD Mapping by class names (if source uses names)
IDD_NAME_MAPPING = {
    "person": 0,
    "rider": 0,
    "car": 1,
    "motorcycle": 2,
    "bike": 2,
    "autorickshaw": 2,
    "truck": 3,
    "bus": 3,
    "vehicle fallback": 3,
}

# 3. FASDD (Fire and Smoke Detection Dataset)
FASDD_MAPPING = {
    0: 4,    # fire -> fire
    1: 5,    # smoke -> smoke
}

# Alternative if FASDD uses different ordering
FASDD_ALT_MAPPING = {
    0: 5,    # smoke -> smoke (if smoke is 0 in source)
    1: 4,    # fire -> fire
}

# 4. Fire & Smoke Detection - Common datasets
FIRE_SMOKE_MAPPING = {
    0: 4,    # Fire -> fire
    1: 5,    # Smoke -> smoke
}

# 5. FPI-Det / Smoking Detection Dataset
FPI_DET_MAPPING = {
    0: 6,    # cigarette -> cigarette
    1: 17,   # cell_phone / phone -> cell_phone
    2: 0,    # person -> person
}

# Smoking Dataset - focused on cigarette detection
SMOKING_DATASET_MAPPING = {
    0: 6,    # cigarette -> cigarette
    1: 0,    # person_smoking -> person
}

# 6. Violence Detection Dataset (CCTV Violence)
VIOLENCE_MAPPING = {
    0: 7,    # violence/fight -> violence
    1: 0,    # person -> person
}

# 7. Fuel Nozzle Dataset (Roboflow)
FUEL_NOZZLE_MAPPING = {
    0: 8,    # nozzle -> nozzle
    1: 8,    # fuel_nozzle -> nozzle (alternate class name)
}

# 8. Petrol Pump Dataset (Roboflow)
PETROL_PUMP_MAPPING = {
    0: 8,    # nozzle -> nozzle
    1: 0,    # person -> person
    2: 1,    # car -> car
}

# 9. Plastic Bottle Dataset -> testing_jar alias
PLASTIC_BOTTLE_MAPPING = {
    0: 9,    # plastic_bottle -> testing_jar
    1: 15,   # bottle -> plastic_item
}

# 10. Manhole Detection Dataset
MANHOLE_MAPPING = {
    0: 11,   # manhole_open -> manhole_open
    1: 11,   # manhole -> manhole_open (assuming open state)
}

# 11. PPE (Personal Protective Equipment) Dataset
PPE_MAPPING = {
    0: 0,    # person -> person
    1: 14,   # helmet/hardhat -> helmet
    2: 13,   # vest/worker -> uniform
    3: 13,   # safety_vest -> uniform
    4: 14,   # hard_hat -> helmet
}

# Common PPE Dataset variations
PPE_ROBOFLOW_MAPPING = {
    0: 14,   # Hardhat -> helmet
    1: 13,   # Vest -> uniform
    2: 0,    # Person -> person
    3: None, # NO-Hardhat (ignore or handle separately)
    4: None, # NO-Vest (ignore or handle separately)
}

# 12. TACO (Trash Annotations in Context) Dataset - Cleanliness
TACO_MAPPING = {
    # TACO has 60 classes, we map litter-related ones to garbage
    0: 16,   # Aluminium foil -> garbage
    1: 16,   # Battery -> garbage
    2: 16,   # Blister pack -> garbage
    3: 15,   # Bottle -> plastic_item
    4: 15,   # Bottle cap -> plastic_item
    5: 16,   # Broken glass -> garbage
    6: 16,   # Can -> garbage
    7: 16,   # Carton -> garbage
    8: 16,   # Cigarette -> garbage (butt, not active cigarette)
    9: 16,   # Cup -> garbage
    10: 16,  # Food Can -> garbage
    11: 16,  # Food Container -> garbage
    12: 16,  # Food wrapper -> garbage
    # ... map all TACO litter classes to garbage (16)
}

# Simplified TACO mapping - all classes to garbage except bottles
TACO_SIMPLIFIED_MAPPING = {
    "litter": 16,
    "trash": 16,
    "garbage": 16,
    "bottle": 15,
    "plastic": 15,
}

# 13. Cell Phone Detection Dataset
CELL_PHONE_MAPPING = {
    0: 17,   # phone -> cell_phone
    1: 17,   # cell_phone -> cell_phone
    2: 17,   # mobile -> cell_phone
}

# ============================================================================
# DATASET SOURCE CONFIGURATIONS
# ============================================================================

class DatasetSource:
    """Configuration for a source dataset."""
    
    def __init__(
        self,
        name: str,
        path: str,
        mapping: Dict[int, Optional[int]],
        has_train: bool = True,
        has_val: bool = True,
        has_test: bool = False,
        class_names: Optional[Dict[int, str]] = None,
        description: str = ""
    ):
        self.name = name
        self.path = Path(path)
        self.mapping = mapping
        self.has_train = has_train
        self.has_val = has_val
        self.has_test = has_test
        self.class_names = class_names or {}
        self.description = description


# Default source dataset configurations (update paths as needed)
def get_default_sources(base_path: str) -> List[DatasetSource]:
    """Get default source dataset configurations."""
    base = Path(base_path)
    
    return [
        DatasetSource(
            name="IDD_Traffic",
            path=str(base / "IDD_Detection"),
            mapping=IDD_MAPPING,
            description="Indian Driving Dataset - Cars, Bikes, Trucks for traffic"
        ),
        DatasetSource(
            name="FASDD_Fire_Smoke",
            path=str(base / "FASDD"),
            mapping=FASDD_MAPPING,
            description="Fire and Smoke Detection Dataset"
        ),
        DatasetSource(
            name="FPI_Det",
            path=str(base / "FPI-Det"),
            mapping=FPI_DET_MAPPING,
            description="Phone and Cigarette Detection (Danger Behavior)"
        ),
        DatasetSource(
            name="Violence_CCTV",
            path=str(base / "Violence_Detection"),
            mapping=VIOLENCE_MAPPING,
            description="CCTV Violence/Fight Detection"
        ),
        DatasetSource(
            name="Fuel_Nozzle",
            path=str(base / "Fuel_Nozzle"),
            mapping=FUEL_NOZZLE_MAPPING,
            description="Petrol Pump Fuel Nozzle Detection"
        ),
        DatasetSource(
            name="PPE_Safety",
            path=str(base / "PPE_Dataset"),
            mapping=PPE_MAPPING,
            description="PPE Dataset for Helmet and Uniform detection"
        ),
        DatasetSource(
            name="TACO_Garbage",
            path=str(base / "TACO"),
            mapping=TACO_MAPPING,
            description="TACO Dataset for Litter/Garbage detection"
        ),
        DatasetSource(
            name="Manhole",
            path=str(base / "Manhole_Detection"),
            mapping=MANHOLE_MAPPING,
            description="Open Manhole Detection"
        ),
        DatasetSource(
            name="Plastic_Bottle",
            path=str(base / "Plastic_Bottle"),
            mapping=PLASTIC_BOTTLE_MAPPING,
            description="Plastic bottle -> testing_jar alias"
        ),
        DatasetSource(
            name="Cell_Phone",
            path=str(base / "Cell_Phone_Detection"),
            mapping=CELL_PHONE_MAPPING,
            description="Cell phone detection at pumps"
        ),
    ]


# ============================================================================
# CORE DATASET BUILDER CLASS
# ============================================================================

class PetrolPumpDatasetBuilder:
    """
    Main class for building the merged Indian Petrol Pump Analytics dataset.
    """
    
    def __init__(
        self,
        output_path: str,
        sources: Optional[List[DatasetSource]] = None,
        train_val_split: float = 0.85,
        seed: int = 42
    ):
        self.output_path = Path(output_path)
        self.sources = sources or []
        self.train_val_split = train_val_split
        self.seed = seed
        
        # Statistics tracking
        self.stats = defaultdict(lambda: defaultdict(int))
        self.processed_files = 0
        self.skipped_annotations = 0
        
        # Set random seed for reproducibility
        random.seed(seed)
        
    def setup_output_directory(self) -> None:
        """Create the output directory structure for YOLO format."""
        print(f"\n📁 Setting up output directory: {self.output_path}")
        
        # Main directories
        dirs = [
            self.output_path / "images" / "train",
            self.output_path / "images" / "val",
            self.output_path / "images" / "test",
            self.output_path / "labels" / "train",
            self.output_path / "labels" / "val",
            self.output_path / "labels" / "test",
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
            
        # Create placeholder directories for manual collection
        placeholders = [
            ("du_cover_open", 10),   # Dispenser Unit Cover Open
            ("air_pump", 12),        # Air Pump Machine
        ]
        
        placeholder_base = self.output_path / "placeholders_for_manual_collection"
        placeholder_base.mkdir(parents=True, exist_ok=True)
        
        for class_name, class_id in placeholders:
            placeholder_dir = placeholder_base / f"{class_id:02d}_{class_name}"
            placeholder_dir.mkdir(parents=True, exist_ok=True)
            
            # Create README for each placeholder
            readme_content = f"""# {class_name.upper()} - Manual Data Collection Required

Class ID: {class_id}
Class Name: {class_name}

## Instructions:
1. Collect images of {class_name} from Indian petrol pumps
2. Place images in this folder
3. Create corresponding YOLO format labels (.txt files)
4. Run the merge script again to include this data

## Label Format (YOLO):
{class_id} <x_center> <y_center> <width> <height>

Example:
{class_id} 0.5 0.5 0.3 0.4
"""
            with open(placeholder_dir / "README.md", "w") as f:
                f.write(readme_content)
                
        print(f"   ✅ Created directory structure")
        print(f"   📝 Created placeholder folders for manual collection:")
        for class_name, class_id in placeholders:
            print(f"      - {class_id}: {class_name}")
            
    def remap_label_file(
        self,
        source_label_path: Path,
        mapping: Dict[int, Optional[int]]
    ) -> List[str]:
        """
        Read a YOLO format label file and remap class IDs.
        
        Args:
            source_label_path: Path to source .txt label file
            mapping: Dictionary mapping source class IDs to target class IDs
            
        Returns:
            List of remapped annotation lines
        """
        remapped_lines = []
        
        if not source_label_path.exists():
            return remapped_lines
            
        with open(source_label_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                    
                parts = line.split()
                if len(parts) < 5:
                    continue
                    
                try:
                    source_class_id = int(parts[0])
                    
                    # Check if this class should be mapped
                    if source_class_id in mapping:
                        target_class_id = mapping[source_class_id]
                        
                        # Skip if mapping is None (ignore this class)
                        if target_class_id is None:
                            self.skipped_annotations += 1
                            continue
                            
                        # Create remapped line
                        bbox_parts = parts[1:]
                        remapped_line = f"{target_class_id} {' '.join(bbox_parts)}"
                        remapped_lines.append(remapped_line)
                        
                        # Track statistics
                        self.stats[target_class_id]["count"] += 1
                    else:
                        # Class not in mapping - skip
                        self.skipped_annotations += 1
                        
                except (ValueError, IndexError) as e:
                    print(f"   ⚠️ Error parsing line in {source_label_path}: {line}")
                    continue
                    
        return remapped_lines
    
    def process_source_dataset(
        self,
        source: DatasetSource,
        split: str = "train"
    ) -> Tuple[int, int]:
        """
        Process a single source dataset and copy to output.
        
        Args:
            source: DatasetSource configuration
            split: Data split ("train", "val", or "test")
            
        Returns:
            Tuple of (images_processed, labels_processed)
        """
        images_processed = 0
        labels_processed = 0
        
        # Construct source paths
        images_dir = source.path / "images" / split
        labels_dir = source.path / "labels" / split
        
        # Check if directories exist
        if not images_dir.exists():
            print(f"   ⚠️ Images directory not found: {images_dir}")
            return 0, 0
            
        if not labels_dir.exists():
            print(f"   ⚠️ Labels directory not found: {labels_dir}")
            return 0, 0
            
        # Process each image
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
        
        for image_path in images_dir.iterdir():
            if image_path.suffix.lower() not in image_extensions:
                continue
                
            # Find corresponding label file
            label_path = labels_dir / f"{image_path.stem}.txt"
            
            # Remap labels
            remapped_labels = self.remap_label_file(label_path, source.mapping)
            
            # Skip if no valid labels after remapping
            if not remapped_labels:
                continue
                
            # Generate unique filename to avoid collisions
            unique_name = f"{source.name}_{image_path.stem}"
            
            # Determine output split (can redistribute if needed)
            output_split = split
            
            # Copy image
            output_image_path = self.output_path / "images" / output_split / f"{unique_name}{image_path.suffix}"
            shutil.copy2(image_path, output_image_path)
            images_processed += 1
            
            # Write remapped labels
            output_label_path = self.output_path / "labels" / output_split / f"{unique_name}.txt"
            with open(output_label_path, 'w') as f:
                f.write('\n'.join(remapped_labels))
            labels_processed += 1
            
        return images_processed, labels_processed
    
    def add_source(self, source: DatasetSource) -> None:
        """Add a source dataset to the builder."""
        self.sources.append(source)
        print(f"   ➕ Added source: {source.name}")
        
    def process_all_sources(self) -> None:
        """Process all configured source datasets."""
        print(f"\n🔄 Processing {len(self.sources)} source datasets...")
        
        for source in self.sources:
            print(f"\n📊 Processing: {source.name}")
            print(f"   Path: {source.path}")
            print(f"   Description: {source.description}")
            
            if not source.path.exists():
                print(f"   ❌ Source path does not exist! Skipping...")
                continue
                
            total_images = 0
            total_labels = 0
            
            # Process each split
            for split in ["train", "val", "test"]:
                if split == "train" and not source.has_train:
                    continue
                if split == "val" and not source.has_val:
                    continue
                if split == "test" and not source.has_test:
                    continue
                    
                images, labels = self.process_source_dataset(source, split)
                total_images += images
                total_labels += labels
                print(f"   📁 {split}: {images} images, {labels} labels")
                
            print(f"   ✅ Total: {total_images} images, {total_labels} labels")
            
    def generate_data_yaml(self) -> str:
        """
        Generate the data.yaml file for YOLO training.
        
        Returns:
            Path to generated data.yaml file
        """
        print(f"\n📝 Generating data.yaml...")
        
        yaml_content = {
            "path": str(self.output_path.absolute()),
            "train": "images/train",
            "val": "images/val",
            "test": "images/test",
            "nc": len(MASTER_SCHEMA),
            "names": MASTER_SCHEMA,
        }
        
        yaml_path = self.output_path / "data.yaml"
        
        with open(yaml_path, 'w') as f:
            yaml.dump(yaml_content, f, default_flow_style=False, sort_keys=False)
            
        print(f"   ✅ Saved to: {yaml_path}")
        
        # Also create a human-readable version
        readme_content = f"""# Indian Petrol Pump Analytics Dataset

## Master Schema (18 Classes)

| ID | Class Name | Description |
|----|------------|-------------|
| 0 | person | People at the petrol pump |
| 1 | car | Cars/sedans |
| 2 | motorcycle | Motorcycles/bikes/autorickshaws |
| 3 | heavy_vehicle | Trucks/buses/heavy vehicles |
| 4 | fire | Active fire |
| 5 | smoke | Smoke detection |
| 6 | cigarette | Lit cigarette (safety hazard) |
| 7 | violence | Fighting/violence behavior |
| 8 | nozzle | Fuel dispenser nozzle |
| 9 | testing_jar | Testing jar (aliased from plastic bottle) |
| 10 | du_cover_open | Dispenser unit cover open (manual collection) |
| 11 | manhole_open | Open manhole |
| 12 | air_pump | Air pump machine (manual collection) |
| 13 | uniform | Staff uniform/vest |
| 14 | helmet | Safety helmet/hardhat |
| 15 | plastic_item | Plastic items (bottles, chairs, buckets) |
| 16 | garbage | Litter/trash |
| 17 | cell_phone | Cell phone (danger near fuel) |

## Dataset Structure

```
Final_Dataset/
├── images/
│   ├── train/
│   ├── val/
│   └── test/
├── labels/
│   ├── train/
│   ├── val/
│   └── test/
├── placeholders_for_manual_collection/
│   ├── 10_du_cover_open/
│   └── 12_air_pump/
├── data.yaml
└── README.md
```

## Usage with YOLO11

```python
from ultralytics import YOLO

# Train
model = YOLO('yolo11n.pt')
results = model.train(data='path/to/data.yaml', epochs=100, imgsz=640)

# Inference
model = YOLO('runs/detect/train/weights/best.pt')
results = model.predict(source='test_image.jpg')
```

## Class Distribution Statistics

Generated at: {self._get_timestamp()}

"""
        
        # Add statistics if available
        if self.stats:
            readme_content += "| Class ID | Class Name | Annotations |\n"
            readme_content += "|----------|------------|-------------|\n"
            for class_id in sorted(MASTER_SCHEMA.keys()):
                class_name = MASTER_SCHEMA[class_id]
                count = self.stats[class_id].get("count", 0)
                readme_content += f"| {class_id} | {class_name} | {count} |\n"
                
        readme_path = self.output_path / "README.md"
        with open(readme_path, 'w') as f:
            f.write(readme_content)
            
        print(f"   📄 Generated README.md with documentation")
        
        return str(yaml_path)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp string."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def print_statistics(self) -> None:
        """Print dataset building statistics."""
        print(f"\n📊 ===== DATASET BUILD STATISTICS =====")
        print(f"\nClass Distribution:")
        print(f"{'ID':<4} {'Class Name':<20} {'Annotations':<12}")
        print("-" * 40)
        
        total_annotations = 0
        for class_id in sorted(MASTER_SCHEMA.keys()):
            class_name = MASTER_SCHEMA[class_id]
            count = self.stats[class_id].get("count", 0)
            total_annotations += count
            marker = "⚠️" if count == 0 else "✅"
            print(f"{class_id:<4} {class_name:<20} {count:<12} {marker}")
            
        print("-" * 40)
        print(f"Total Annotations: {total_annotations}")
        print(f"Skipped Annotations: {self.skipped_annotations}")
        print(f"\n⚠️  Classes with 0 annotations need manual data collection!")
        
    def build(self) -> str:
        """
        Execute the full dataset build pipeline.
        
        Returns:
            Path to generated data.yaml
        """
        print("=" * 60)
        print("🚀 INDIAN PETROL PUMP ANALYTICS DATASET BUILDER")
        print("   Target: YOLO11 (Ultralytics)")
        print("   Environment: Indian Petrol Pumps")
        print("=" * 60)
        
        # Step 1: Setup output directory
        self.setup_output_directory()
        
        # Step 2: Process all source datasets
        self.process_all_sources()
        
        # Step 3: Generate data.yaml
        yaml_path = self.generate_data_yaml()
        
        # Step 4: Print statistics
        self.print_statistics()
        
        print(f"\n✅ Dataset build complete!")
        print(f"   Output: {self.output_path}")
        print(f"   data.yaml: {yaml_path}")
        
        return yaml_path


# ============================================================================
# ROBOFLOW INTEGRATION (Optional)
# ============================================================================

class RoboflowDatasetDownloader:
    """
    Helper class to download datasets from Roboflow.
    Requires: pip install roboflow
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self._rf = None
        
    @property
    def rf(self):
        """Lazy load Roboflow."""
        if self._rf is None:
            try:
                from roboflow import Roboflow
                self._rf = Roboflow(api_key=self.api_key)
            except ImportError:
                raise ImportError("Please install roboflow: pip install roboflow")
        return self._rf
    
    def download_dataset(
        self,
        workspace: str,
        project: str,
        version: int,
        output_dir: str,
        format: str = "yolov8"
    ) -> str:
        """
        Download a dataset from Roboflow.
        
        Args:
            workspace: Roboflow workspace name
            project: Project name
            version: Dataset version number
            output_dir: Directory to save dataset
            format: Export format (yolov8, yolov5, etc.)
            
        Returns:
            Path to downloaded dataset
        """
        print(f"📥 Downloading: {workspace}/{project} v{version}")
        
        project_obj = self.rf.workspace(workspace).project(project)
        dataset = project_obj.version(version).download(format, location=output_dir)
        
        print(f"   ✅ Downloaded to: {output_dir}")
        return output_dir


# Pre-configured Roboflow datasets for petrol pump analytics
ROBOFLOW_DATASETS = [
    {
        "name": "fire-smoke-detection",
        "workspace": "fire-smoke-detection-uvlhc",
        "project": "fire-smoke-detection-ml",
        "version": 1,
        "mapping": FASDD_MAPPING,
        "description": "Fire and Smoke Detection"
    },
    {
        "name": "fuel-nozzle",
        "workspace": "saurabh-shukla-qzmnn",
        "project": "fuel-nozzle-detection",
        "version": 1,
        "mapping": FUEL_NOZZLE_MAPPING,
        "description": "Fuel Nozzle Detection"
    },
    {
        "name": "ppe-detection",
        "workspace": "object-detect-ry6oy",
        "project": "construction-site-safety",
        "version": 1,
        "mapping": PPE_ROBOFLOW_MAPPING,
        "description": "PPE Detection (Helmet, Vest)"
    },
    {
        "name": "violence-detection",
        "workspace": "violence-detection-ptuqm",
        "project": "violence-detection-xzcmz", 
        "version": 1,
        "mapping": VIOLENCE_MAPPING,
        "description": "Violence/Fight Detection"
    },
    {
        "name": "smoking-detection",
        "workspace": "cigarette-detection", 
        "project": "cigarette-detection-crvxj",
        "version": 1,
        "mapping": SMOKING_DATASET_MAPPING,
        "description": "Cigarette/Smoking Detection"
    },
]


def download_roboflow_datasets(api_key: str, output_base: str) -> List[DatasetSource]:
    """
    Download all pre-configured Roboflow datasets.
    
    Args:
        api_key: Roboflow API key
        output_base: Base directory for downloads
        
    Returns:
        List of DatasetSource objects for the downloaded datasets
    """
    downloader = RoboflowDatasetDownloader(api_key)
    sources = []
    
    for ds_config in ROBOFLOW_DATASETS:
        try:
            output_dir = os.path.join(output_base, ds_config["name"])
            downloader.download_dataset(
                workspace=ds_config["workspace"],
                project=ds_config["project"],
                version=ds_config["version"],
                output_dir=output_dir
            )
            
            source = DatasetSource(
                name=ds_config["name"],
                path=output_dir,
                mapping=ds_config["mapping"],
                description=ds_config["description"]
            )
            sources.append(source)
            
        except Exception as e:
            print(f"   ❌ Failed to download {ds_config['name']}: {e}")
            
    return sources


# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

def main():
    """Main entry point for the dataset builder script."""
    parser = argparse.ArgumentParser(
        description="Build Indian Petrol Pump Analytics Dataset for YOLO11",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using local datasets
  python dataset_builder.py --sources ./source_datasets --output ./Final_Dataset
  
  # Using Roboflow API
  python dataset_builder.py --use-roboflow --roboflow-key YOUR_KEY --output ./Final_Dataset
  
  # Combine both
  python dataset_builder.py --sources ./local_data --use-roboflow --roboflow-key KEY --output ./Final_Dataset
"""
    )
    
    parser.add_argument(
        "--sources", "-s",
        type=str,
        default=None,
        help="Path to directory containing source datasets"
    )
    
    parser.add_argument(
        "--output", "-o", 
        type=str,
        default="./Final_Dataset",
        help="Output directory for merged dataset (default: ./Final_Dataset)"
    )
    
    parser.add_argument(
        "--use-roboflow",
        action="store_true",
        help="Download datasets from Roboflow"
    )
    
    parser.add_argument(
        "--roboflow-key",
        type=str,
        default=None,
        help="Roboflow API key (or set ROBOFLOW_API_KEY env var)"
    )
    
    parser.add_argument(
        "--train-split",
        type=float,
        default=0.85,
        help="Train/val split ratio (default: 0.85)"
    )
    
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)"
    )
    
    args = parser.parse_args()
    
    # Initialize builder
    builder = PetrolPumpDatasetBuilder(
        output_path=args.output,
        train_val_split=args.train_split,
        seed=args.seed
    )
    
    # Add local sources if provided
    if args.sources:
        default_sources = get_default_sources(args.sources)
        for source in default_sources:
            builder.add_source(source)
            
    # Download and add Roboflow sources if requested
    if args.use_roboflow:
        api_key = args.roboflow_key or os.environ.get("ROBOFLOW_API_KEY")
        if not api_key:
            print("❌ Roboflow API key required. Use --roboflow-key or set ROBOFLOW_API_KEY")
            return 1
            
        roboflow_download_dir = os.path.join(args.output, ".roboflow_cache")
        roboflow_sources = download_roboflow_datasets(api_key, roboflow_download_dir)
        for source in roboflow_sources:
            builder.add_source(source)
            
    # Check if we have any sources
    if not builder.sources:
        print("❌ No source datasets configured!")
        print("   Use --sources to specify local dataset directory")
        print("   Or use --use-roboflow with --roboflow-key to download from Roboflow")
        return 1
        
    # Build the dataset
    builder.build()
    
    return 0


if __name__ == "__main__":
    exit(main())
