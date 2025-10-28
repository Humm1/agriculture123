"""
Dataset Validator
Validates generated training datasets for quality and completeness
"""

import json
from pathlib import Path
from PIL import Image
import pandas as pd

BASE_DIR = Path(__file__).parent / "training_data"


def validate_image_dataset(dataset_name, expected_classes):
    """Validate image-based datasets"""
    print(f"\n📸 Validating {dataset_name}...")
    
    dataset_dir = BASE_DIR / dataset_name
    if not dataset_dir.exists():
        print(f"   ❌ Directory not found: {dataset_dir}")
        return False
    
    # Load metadata
    metadata_file = dataset_dir / "metadata.json"
    if not metadata_file.exists():
        print(f"   ❌ Metadata file not found")
        return False
    
    with open(metadata_file) as f:
        metadata = json.load(f)
    
    # Check classes
    classes_found = set()
    image_count = 0
    corrupted_images = []
    
    for class_name in expected_classes:
        class_dir = dataset_dir / class_name
        if not class_dir.exists():
            print(f"   ⚠️  Class directory missing: {class_name}")
            continue
        
        classes_found.add(class_name)
        
        # Check images in class
        for img_file in class_dir.glob("*.jpg"):
            try:
                img = Image.open(img_file)
                img.verify()  # Verify it's a valid image
                image_count += 1
            except Exception as e:
                corrupted_images.append(str(img_file))
    
    # Report results
    print(f"   ✅ Classes: {len(classes_found)}/{len(expected_classes)}")
    print(f"   ✅ Total images: {image_count}")
    print(f"   ✅ Metadata records: {len(metadata)}")
    
    if corrupted_images:
        print(f"   ⚠️  Corrupted images: {len(corrupted_images)}")
        for img in corrupted_images[:5]:
            print(f"      - {img}")
    
    if len(classes_found) == len(expected_classes) and image_count > 0:
        print(f"   ✅ {dataset_name} validation PASSED")
        return True
    else:
        print(f"   ❌ {dataset_name} validation FAILED")
        return False


def validate_csv_dataset(dataset_name, expected_file):
    """Validate CSV-based datasets"""
    print(f"\n📊 Validating {dataset_name}...")
    
    dataset_dir = BASE_DIR / dataset_name
    csv_file = dataset_dir / expected_file
    
    if not csv_file.exists():
        print(f"   ❌ CSV file not found: {csv_file}")
        return False
    
    # Load and validate CSV
    try:
        df = pd.read_csv(csv_file)
        print(f"   ✅ Records: {len(df)}")
        print(f"   ✅ Features: {len(df.columns)}")
        print(f"   ✅ Missing values: {df.isnull().sum().sum()}")
        
        # Load metadata
        metadata_file = dataset_dir / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file) as f:
                metadata = json.load(f)
            print(f"   ✅ Metadata: {metadata.get('description', 'N/A')}")
        
        print(f"   ✅ {dataset_name} validation PASSED")
        return True
    except Exception as e:
        print(f"   ❌ Error loading CSV: {e}")
        return False


def validate_all_datasets():
    """Run validation on all datasets"""
    print("\n" + "="*60)
    print("🔍 AgroShield Dataset Validation")
    print("="*60)
    
    if not BASE_DIR.exists():
        print(f"\n❌ Training data directory not found: {BASE_DIR}")
        print("Run generate_training_datasets.py first!")
        return
    
    results = {}
    
    # Image datasets
    results['pest_detection'] = validate_image_dataset(
        'pest_detection',
        ['aphids', 'whiteflies', 'armyworms', 'leaf_miners', 'thrips', 'cutworms', 'healthy']
    )
    
    results['disease_detection'] = validate_image_dataset(
        'disease_detection',
        ['early_blight', 'late_blight', 'leaf_curl', 'powdery_mildew', 'rust', 'bacterial_spot', 'healthy']
    )
    
    results['storage_assessment'] = validate_image_dataset(
        'storage_assessment',
        ['excellent', 'good', 'fair', 'poor', 'spoiled']
    )
    
    results['soil_diagnostics'] = validate_image_dataset(
        'soil_diagnostics',
        ['sandy', 'loamy', 'clay', 'silty', 'peaty', 'chalky']
    )
    
    results['plant_health'] = validate_image_dataset(
        'plant_health',
        ['seedling', 'vegetative', 'flowering', 'fruiting', 'mature', 'stressed', 'diseased']
    )
    
    # CSV datasets
    results['climate_prediction'] = validate_csv_dataset(
        'climate_prediction',
        'climate_timeseries.csv'
    )
    
    results['yield_prediction'] = validate_csv_dataset(
        'yield_prediction',
        'yield_prediction.csv'
    )
    
    # Summary
    print("\n" + "="*60)
    print("📋 Validation Summary")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for dataset, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {dataset}: {'PASSED' if status else 'FAILED'}")
    
    print(f"\n{'✅' if passed == total else '⚠️ '} {passed}/{total} datasets validated successfully")
    
    # Check summary file
    summary_file = BASE_DIR / "dataset_summary.json"
    if summary_file.exists():
        with open(summary_file) as f:
            summary = json.load(f)
        print(f"\n📄 Summary file found:")
        print(f"   Total images: {summary.get('total_images', 'N/A'):,}")
        print(f"   Total records: {summary.get('total_records', 'N/A'):,}")
        print(f"   Generated: {summary.get('generation_date', 'N/A')}")
    
    print("\n" + "="*60 + "\n")
    
    return all(results.values())


if __name__ == "__main__":
    success = validate_all_datasets()
    exit(0 if success else 1)
