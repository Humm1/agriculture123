"""
AgroShield Training Dataset Generator
Generates comprehensive pretrained datasets for all AI models

Models covered:
1. Pest Detection
2. Disease Detection
3. Storage Assessment
4. Soil Diagnostics
5. Plant Health
6. Climate Prediction
7. Yield Prediction
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFilter
import random
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# Create base directories
BASE_DIR = Path(__file__).parent / "training_data"
PEST_DIR = BASE_DIR / "pest_detection"
DISEASE_DIR = BASE_DIR / "disease_detection"
STORAGE_DIR = BASE_DIR / "storage_assessment"
SOIL_DIR = BASE_DIR / "soil_diagnostics"
PLANT_DIR = BASE_DIR / "plant_health"
CLIMATE_DIR = BASE_DIR / "climate_prediction"
YIELD_DIR = BASE_DIR / "yield_prediction"

# Create all directories
for dir_path in [PEST_DIR, DISEASE_DIR, STORAGE_DIR, SOIL_DIR, PLANT_DIR, CLIMATE_DIR, YIELD_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)


# ============================================================================
# 1. PEST DETECTION DATASET
# ============================================================================

def generate_pest_detection_data():
    """Generate synthetic pest detection dataset"""
    print("[PEST] Generating Pest Detection Dataset...")
    
    pests = {
        'aphids': {'count': 150, 'color': (100, 150, 100), 'size': 20},
        'whiteflies': {'count': 150, 'color': (240, 240, 240), 'size': 15},
        'armyworms': {'count': 150, 'color': (80, 100, 60), 'size': 30},
        'leaf_miners': {'count': 150, 'color': (120, 140, 100), 'size': 25},
        'thrips': {'count': 150, 'color': (90, 90, 70), 'size': 12},
        'cutworms': {'count': 150, 'color': (60, 80, 50), 'size': 35},
        'healthy': {'count': 200, 'color': None, 'size': 0}
    }
    
    metadata = []
    
    for pest_name, config in pests.items():
        pest_folder = PEST_DIR / pest_name
        pest_folder.mkdir(exist_ok=True)
        
        for i in range(config['count']):
            # Create synthetic image
            img = Image.new('RGB', (224, 224), color=(50, 120, 50))  # Green leaf background
            draw = ImageDraw.Draw(img)
            
            if pest_name != 'healthy':
                # Add pest patterns
                num_pests = random.randint(3, 15)
                for _ in range(num_pests):
                    x = random.randint(10, 214)
                    y = random.randint(10, 214)
                    size = config['size'] + random.randint(-5, 5)
                    color = tuple(c + random.randint(-20, 20) for c in config['color'])
                    draw.ellipse([x, y, x + size, y + size], fill=color)
                
                # Add texture
                img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
            
            # Add realistic variations
            img = img.filter(ImageFilter.SHARPEN)
            
            # Save image
            img_path = pest_folder / f"{pest_name}_{i:04d}.jpg"
            img.save(img_path, quality=85)
            
            # Store metadata
            metadata.append({
                'image_path': str(img_path.relative_to(BASE_DIR)),
                'label': pest_name,
                'severity': 'none' if pest_name == 'healthy' else random.choice(['low', 'medium', 'high']),
                'confidence': random.uniform(0.85, 0.99),
                'timestamp': datetime.now().isoformat()
            })
    
    # Save metadata
    with open(PEST_DIR / 'metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"[OK] Generated {len(metadata)} pest detection images")
    return metadata


# ============================================================================
# 2. DISEASE DETECTION DATASET
# ============================================================================

def generate_disease_detection_data():
    """Generate synthetic disease detection dataset"""
    print("[DISEASE] Generating Disease Detection Dataset...")
    
    diseases = {
        'early_blight': {'count': 150, 'pattern': 'spots', 'color': (139, 69, 19)},
        'late_blight': {'count': 150, 'pattern': 'blotches', 'color': (101, 67, 33)},
        'leaf_curl': {'count': 150, 'pattern': 'curled', 'color': (180, 180, 100)},
        'powdery_mildew': {'count': 150, 'pattern': 'powder', 'color': (230, 230, 230)},
        'rust': {'count': 150, 'pattern': 'rust_spots', 'color': (184, 115, 51)},
        'bacterial_spot': {'count': 150, 'pattern': 'small_spots', 'color': (50, 30, 20)},
        'healthy': {'count': 200, 'pattern': 'none', 'color': (50, 150, 50)}
    }
    
    metadata = []
    
    for disease_name, config in diseases.items():
        disease_folder = DISEASE_DIR / disease_name
        disease_folder.mkdir(exist_ok=True)
        
        for i in range(config['count']):
            # Create base leaf image
            img = Image.new('RGB', (224, 224), color=(40, 120, 40))
            draw = ImageDraw.Draw(img)
            
            if config['pattern'] == 'spots':
                # Draw circular spots
                for _ in range(random.randint(5, 20)):
                    x = random.randint(20, 200)
                    y = random.randint(20, 200)
                    r = random.randint(5, 15)
                    draw.ellipse([x-r, y-r, x+r, y+r], fill=config['color'])
            
            elif config['pattern'] == 'blotches':
                # Draw irregular blotches
                for _ in range(random.randint(3, 8)):
                    points = [(random.randint(20, 200), random.randint(20, 200)) for _ in range(6)]
                    draw.polygon(points, fill=config['color'])
            
            elif config['pattern'] == 'powder':
                # Draw powdery texture
                for _ in range(random.randint(100, 300)):
                    x = random.randint(0, 223)
                    y = random.randint(0, 223)
                    draw.point((x, y), fill=config['color'])
            
            elif config['pattern'] == 'rust_spots':
                # Draw rust-like spots
                for _ in range(random.randint(10, 30)):
                    x = random.randint(20, 200)
                    y = random.randint(20, 200)
                    r = random.randint(3, 8)
                    draw.ellipse([x-r, y-r, x+r, y+r], fill=config['color'])
            
            # Apply filters for realism
            img = img.filter(ImageFilter.GaussianBlur(radius=0.3))
            
            # Save image
            img_path = disease_folder / f"{disease_name}_{i:04d}.jpg"
            img.save(img_path, quality=85)
            
            # Store metadata
            metadata.append({
                'image_path': str(img_path.relative_to(BASE_DIR)),
                'label': disease_name,
                'severity': 'none' if disease_name == 'healthy' else random.choice(['mild', 'moderate', 'severe']),
                'affected_area_percent': 0 if disease_name == 'healthy' else random.uniform(5, 80),
                'timestamp': datetime.now().isoformat()
            })
    
    # Save metadata
    with open(DISEASE_DIR / 'metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"[OK] Generated {len(metadata)} disease detection images")
    return metadata


# ============================================================================
# 3. STORAGE ASSESSMENT DATASET
# ============================================================================

def generate_storage_assessment_data():
    """Generate synthetic storage condition assessment dataset"""
    print("[STORAGE] Generating Storage Assessment Dataset...")
    
    conditions = {
        'excellent': {'count': 150, 'quality': 95, 'color': (255, 220, 150)},
        'good': {'count': 150, 'quality': 80, 'color': (240, 210, 140)},
        'fair': {'count': 150, 'quality': 65, 'color': (220, 190, 120)},
        'poor': {'count': 150, 'quality': 45, 'color': (180, 150, 100)},
        'spoiled': {'count': 150, 'quality': 20, 'color': (120, 100, 70)}
    }
    
    metadata = []
    
    for condition, config in conditions.items():
        condition_folder = STORAGE_DIR / condition
        condition_folder.mkdir(exist_ok=True)
        
        for i in range(config['count']):
            # Create grain/crop storage image
            img = Image.new('RGB', (224, 224), color=config['color'])
            draw = ImageDraw.Draw(img)
            
            # Add quality indicators
            if condition in ['poor', 'spoiled']:
                # Add mold/damage spots
                for _ in range(random.randint(10, 40)):
                    x = random.randint(0, 223)
                    y = random.randint(0, 223)
                    r = random.randint(3, 10)
                    mold_color = (50 + random.randint(0, 50), 80 + random.randint(0, 30), 30)
                    draw.ellipse([x-r, y-r, x+r, y+r], fill=mold_color)
            
            # Add texture
            for _ in range(random.randint(50, 200)):
                x = random.randint(0, 223)
                y = random.randint(0, 223)
                variation = tuple(c + random.randint(-30, 30) for c in config['color'])
                draw.point((x, y), fill=variation)
            
            # Apply filters
            img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
            
            # Save image
            img_path = condition_folder / f"{condition}_{i:04d}.jpg"
            img.save(img_path, quality=85)
            
            # Generate associated sensor data
            temp = random.uniform(15, 35) if condition in ['excellent', 'good'] else random.uniform(25, 45)
            humidity = random.uniform(40, 60) if condition in ['excellent', 'good'] else random.uniform(60, 90)
            
            metadata.append({
                'image_path': str(img_path.relative_to(BASE_DIR)),
                'label': condition,
                'quality_score': config['quality'] + random.uniform(-5, 5),
                'temperature_c': round(temp, 1),
                'humidity_percent': round(humidity, 1),
                'mold_detected': condition in ['poor', 'spoiled'],
                'storage_days': random.randint(1, 180),
                'timestamp': datetime.now().isoformat()
            })
    
    # Save metadata
    with open(STORAGE_DIR / 'metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"[OK] Generated {len(metadata)} storage assessment images")
    return metadata


# ============================================================================
# 4. SOIL DIAGNOSTICS DATASET
# ============================================================================

def generate_soil_diagnostics_data():
    """Generate synthetic soil diagnostics dataset"""
    print("[SOIL] Generating Soil Diagnostics Dataset...")
    
    soil_types = {
        'sandy': {'count': 120, 'color': (210, 180, 140), 'ph': (5.5, 7.0)},
        'loamy': {'count': 120, 'color': (139, 90, 43), 'ph': (6.0, 7.5)},
        'clay': {'count': 120, 'color': (160, 82, 45), 'ph': (6.5, 8.0)},
        'silty': {'count': 120, 'color': (189, 154, 122), 'ph': (6.0, 7.0)},
        'peaty': {'count': 120, 'color': (85, 53, 36), 'ph': (4.5, 6.0)},
        'chalky': {'count': 120, 'color': (222, 184, 135), 'ph': (7.5, 9.0)}
    }
    
    metadata = []
    
    for soil_type, config in soil_types.items():
        soil_folder = SOIL_DIR / soil_type
        soil_folder.mkdir(exist_ok=True)
        
        for i in range(config['count']):
            # Create soil texture image
            img = Image.new('RGB', (224, 224), color=config['color'])
            draw = ImageDraw.Draw(img)
            
            # Add soil texture patterns
            if soil_type == 'sandy':
                # Granular texture
                for _ in range(random.randint(100, 300)):
                    x = random.randint(0, 223)
                    y = random.randint(0, 223)
                    size = random.randint(1, 3)
                    sand_color = tuple(c + random.randint(-20, 20) for c in config['color'])
                    draw.ellipse([x, y, x+size, y+size], fill=sand_color)
            
            elif soil_type == 'clay':
                # Smooth with cracks
                for _ in range(random.randint(5, 15)):
                    x1 = random.randint(0, 223)
                    y1 = random.randint(0, 223)
                    x2 = x1 + random.randint(-30, 30)
                    y2 = y1 + random.randint(20, 50)
                    draw.line([(x1, y1), (x2, y2)], fill=(100, 50, 30), width=2)
            
            # Add texture variation
            img = img.filter(ImageFilter.GaussianBlur(radius=0.3))
            
            # Save image
            img_path = soil_folder / f"{soil_type}_{i:04d}.jpg"
            img.save(img_path, quality=85)
            
            # Generate soil analysis data
            ph = round(random.uniform(*config['ph']), 1)
            
            metadata.append({
                'image_path': str(img_path.relative_to(BASE_DIR)),
                'label': soil_type,
                'ph': ph,
                'nitrogen_ppm': round(random.uniform(10, 100), 1),
                'phosphorus_ppm': round(random.uniform(5, 50), 1),
                'potassium_ppm': round(random.uniform(50, 200), 1),
                'organic_matter_percent': round(random.uniform(1, 10), 1),
                'moisture_percent': round(random.uniform(10, 40), 1),
                'texture': soil_type,
                'fertility_rating': random.choice(['low', 'medium', 'high']),
                'timestamp': datetime.now().isoformat()
            })
    
    # Save metadata
    with open(SOIL_DIR / 'metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"[OK] Generated {len(metadata)} soil diagnostic images")
    return metadata


# ============================================================================
# 5. PLANT HEALTH DATASET
# ============================================================================

def generate_plant_health_data():
    """Generate synthetic plant health assessment dataset"""
    print("[PLANT] Generating Plant Health Dataset...")
    
    health_stages = {
        'seedling': {'count': 100, 'size': 30, 'color': (144, 238, 144)},
        'vegetative': {'count': 100, 'size': 80, 'color': (34, 139, 34)},
        'flowering': {'count': 100, 'size': 100, 'color': (50, 205, 50)},
        'fruiting': {'count': 100, 'size': 120, 'color': (46, 139, 87)},
        'mature': {'count': 100, 'size': 150, 'color': (60, 179, 113)},
        'stressed': {'count': 100, 'size': 70, 'color': (189, 183, 107)},
        'diseased': {'count': 100, 'size': 60, 'color': (154, 205, 50)}
    }
    
    metadata = []
    
    for stage, config in health_stages.items():
        stage_folder = PLANT_DIR / stage
        stage_folder.mkdir(exist_ok=True)
        
        for i in range(config['count']):
            # Create plant image
            img = Image.new('RGB', (224, 224), color=(90, 70, 50))  # Soil background
            draw = ImageDraw.Draw(img)
            
            # Draw plant structure
            plant_height = config['size']
            base_x = 112
            base_y = 224
            
            # Stem
            draw.line([(base_x, base_y), (base_x, base_y - plant_height)], 
                     fill=(40, 80, 40), width=3)
            
            # Leaves
            num_leaves = random.randint(3, 8)
            for j in range(num_leaves):
                leaf_y = base_y - random.randint(20, plant_height)
                leaf_x = base_x + random.randint(-40, 40)
                leaf_size = random.randint(15, 35)
                draw.ellipse([leaf_x - leaf_size, leaf_y - leaf_size//2,
                            leaf_x + leaf_size, leaf_y + leaf_size//2],
                           fill=config['color'])
            
            # Add flowers if flowering stage
            if stage in ['flowering', 'fruiting']:
                for _ in range(random.randint(2, 5)):
                    fx = base_x + random.randint(-30, 30)
                    fy = base_y - plant_height + random.randint(-20, 20)
                    draw.ellipse([fx-5, fy-5, fx+5, fy+5], fill=(255, 192, 203))
            
            # Apply filters
            img = img.filter(ImageFilter.SMOOTH)
            
            # Save image
            img_path = stage_folder / f"{stage}_{i:04d}.jpg"
            img.save(img_path, quality=85)
            
            # Generate health metrics
            health_score = 95 if stage in ['vegetative', 'flowering', 'fruiting', 'mature'] else random.uniform(40, 70)
            
            metadata.append({
                'image_path': str(img_path.relative_to(BASE_DIR)),
                'label': stage,
                'health_score': round(health_score, 1),
                'growth_stage': stage,
                'leaf_count': num_leaves,
                'plant_height_cm': plant_height,
                'color_intensity': 'vibrant' if stage not in ['stressed', 'diseased'] else 'pale',
                'days_after_planting': random.randint(1, 120),
                'timestamp': datetime.now().isoformat()
            })
    
    # Save metadata
    with open(PLANT_DIR / 'metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"[OK] Generated {len(metadata)} plant health images")
    return metadata


# ============================================================================
# 6. CLIMATE PREDICTION DATASET
# ============================================================================

def generate_climate_prediction_data():
    """Generate synthetic climate time-series dataset"""
    print("[CLIMATE] Generating Climate Prediction Dataset...")
    
    # Generate 2 years of daily climate data
    start_date = datetime.now() - timedelta(days=730)
    
    climate_data = []
    
    for day in range(730):
        current_date = start_date + timedelta(days=day)
        
        # Seasonal patterns
        day_of_year = current_date.timetuple().tm_yday
        temp_seasonal = 25 + 10 * np.sin(2 * np.pi * day_of_year / 365)
        
        # Add daily variation and randomness
        temperature = temp_seasonal + random.uniform(-3, 3)
        humidity = 60 + 20 * np.sin(2 * np.pi * day_of_year / 365) + random.uniform(-10, 10)
        rainfall = max(0, np.random.exponential(5) if random.random() > 0.7 else 0)
        wind_speed = abs(random.gauss(10, 5))
        
        climate_data.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'temperature_c': round(temperature, 1),
            'humidity_percent': round(max(20, min(100, humidity)), 1),
            'rainfall_mm': round(rainfall, 1),
            'wind_speed_kmh': round(wind_speed, 1),
            'pressure_mb': round(1013 + random.uniform(-20, 20), 1),
            'cloud_cover_percent': round(random.uniform(0, 100), 0),
            'uv_index': round(random.uniform(0, 11), 1),
            'soil_temp_c': round(temperature - random.uniform(2, 5), 1),
            'evapotranspiration_mm': round(max(0, 5 + random.uniform(-2, 3)), 1)
        })
    
    # Save as CSV
    df = pd.DataFrame(climate_data)
    df.to_csv(CLIMATE_DIR / 'climate_timeseries.csv', index=False)
    
    # Save metadata
    metadata = {
        'description': 'Daily climate data for 2 years with seasonal patterns',
        'features': list(climate_data[0].keys()),
        'records': len(climate_data),
        'start_date': climate_data[0]['date'],
        'end_date': climate_data[-1]['date'],
        'use_case': 'LSTM time-series prediction',
        'sequence_length': 30,  # Use 30 days to predict next 7 days
        'prediction_horizon': 7
    }
    
    with open(CLIMATE_DIR / 'metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"[OK] Generated {len(climate_data)} climate records")
    return climate_data


# ============================================================================
# 7. YIELD PREDICTION DATASET
# ============================================================================

def generate_yield_prediction_data():
    """Generate synthetic crop yield prediction dataset"""
    print("[YIELD] Generating Yield Prediction Dataset...")
    
    crops = ['maize', 'wheat', 'rice', 'tomatoes', 'potatoes', 'beans', 'cassava']
    
    yield_data = []
    
    for _ in range(1000):
        crop = random.choice(crops)
        
        # Farm parameters
        area_hectares = round(random.uniform(0.5, 50), 2)
        soil_quality = random.uniform(0.3, 1.0)
        irrigation = random.choice([True, False])
        fertilizer_kg = round(random.uniform(0, 200), 1)
        
        # Climate factors
        avg_temp = round(random.uniform(18, 35), 1)
        total_rainfall = round(random.uniform(300, 1500), 1)
        sunshine_hours = round(random.uniform(1500, 3000), 0)
        
        # Calculate yield (simplified model with realistic variations)
        base_yield = {
            'maize': 6, 'wheat': 4, 'rice': 5, 
            'tomatoes': 40, 'potatoes': 25, 'beans': 2, 'cassava': 15
        }[crop]
        
        yield_per_hectare = base_yield * soil_quality
        yield_per_hectare *= (1.2 if irrigation else 0.8)
        yield_per_hectare *= (1 + min(fertilizer_kg / 100, 0.5))
        
        # Climate impact
        temp_factor = 1 - abs(avg_temp - 25) / 30
        rain_factor = 1 - abs(total_rainfall - 800) / 1000
        yield_per_hectare *= (0.7 + 0.3 * temp_factor)
        yield_per_hectare *= (0.7 + 0.3 * rain_factor)
        
        # Add randomness
        yield_per_hectare *= random.uniform(0.7, 1.3)
        
        total_yield = yield_per_hectare * area_hectares
        
        yield_data.append({
            'crop': crop,
            'area_hectares': area_hectares,
            'soil_quality_index': round(soil_quality, 2),
            'irrigation_system': irrigation,
            'fertilizer_kg_per_hectare': round(fertilizer_kg / area_hectares, 1),
            'avg_temperature_c': avg_temp,
            'total_rainfall_mm': total_rainfall,
            'sunshine_hours': sunshine_hours,
            'pest_pressure': random.choice(['low', 'medium', 'high']),
            'disease_occurrence': random.choice(['none', 'minor', 'moderate']),
            'yield_per_hectare_tons': round(yield_per_hectare, 2),
            'total_yield_tons': round(total_yield, 2),
            'quality_grade': random.choice(['A', 'B', 'C']),
            'planting_month': random.randint(1, 12),
            'harvest_month': random.randint(1, 12)
        })
    
    # Save as CSV
    df = pd.DataFrame(yield_data)
    df.to_csv(YIELD_DIR / 'yield_prediction.csv', index=False)
    
    # Save metadata
    metadata = {
        'description': 'Crop yield prediction dataset with environmental and management factors',
        'features': list(yield_data[0].keys()),
        'records': len(yield_data),
        'crops': crops,
        'target_variable': 'yield_per_hectare_tons',
        'use_case': 'Regression model for yield prediction',
        'model_type': 'Random Forest / Gradient Boosting'
    }
    
    with open(YIELD_DIR / 'metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"[OK] Generated {len(yield_data)} yield prediction records")
    return yield_data


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def generate_all_datasets():
    """Generate all training datasets"""
    print("\n" + "="*60)
    print("[*] AgroShield Training Dataset Generation Started")
    print("="*60 + "\n")
    
    # Generate all datasets
    pest_data = generate_pest_detection_data()
    disease_data = generate_disease_detection_data()
    storage_data = generate_storage_assessment_data()
    soil_data = generate_soil_diagnostics_data()
    plant_data = generate_plant_health_data()
    climate_data = generate_climate_prediction_data()
    yield_data = generate_yield_prediction_data()
    
    # Create summary report
    summary = {
        'generation_date': datetime.now().isoformat(),
        'datasets': {
            'pest_detection': {
                'images': len(pest_data),
                'classes': 7,
                'path': str(PEST_DIR.relative_to(BASE_DIR))
            },
            'disease_detection': {
                'images': len(disease_data),
                'classes': 7,
                'path': str(DISEASE_DIR.relative_to(BASE_DIR))
            },
            'storage_assessment': {
                'images': len(storage_data),
                'classes': 5,
                'path': str(STORAGE_DIR.relative_to(BASE_DIR))
            },
            'soil_diagnostics': {
                'images': len(soil_data),
                'classes': 6,
                'path': str(SOIL_DIR.relative_to(BASE_DIR))
            },
            'plant_health': {
                'images': len(plant_data),
                'classes': 7,
                'path': str(PLANT_DIR.relative_to(BASE_DIR))
            },
            'climate_prediction': {
                'records': len(climate_data),
                'time_series': True,
                'path': str(CLIMATE_DIR.relative_to(BASE_DIR))
            },
            'yield_prediction': {
                'records': len(yield_data),
                'regression': True,
                'path': str(YIELD_DIR.relative_to(BASE_DIR))
            }
        },
        'total_images': len(pest_data) + len(disease_data) + len(storage_data) + len(soil_data) + len(plant_data),
        'total_records': len(climate_data) + len(yield_data)
    }
    
    # Save summary
    with open(BASE_DIR / 'dataset_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("\n" + "="*60)
    print("[SUCCESS] ALL DATASETS GENERATED SUCCESSFULLY!")
    print("="*60)
    print(f"\n[SUMMARY]")
    print(f"   Total Images: {summary['total_images']:,}")
    print(f"   Total Records: {summary['total_records']:,}")
    print(f"   Location: {BASE_DIR}")
    print(f"\n[REPORT] Summary saved: {BASE_DIR / 'dataset_summary.json'}")
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    generate_all_datasets()
