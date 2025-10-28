"""
AI Calendar Dataset Generation and Training
Generates training data for AI-powered farming calendar recommendations
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from pathlib import Path
import random

# Crop data
CROPS = {
    "maize": {"season": ["long_rains", "short_rains"], "cycle_days": 120, "ideal_temp": 25},
    "beans": {"season": ["long_rains", "short_rains"], "cycle_days": 90, "ideal_temp": 22},
    "tomatoes": {"season": ["long_rains"], "cycle_days": 75, "ideal_temp": 24},
    "cabbage": {"season": ["short_rains"], "cycle_days": 70, "ideal_temp": 18},
    "kale": {"season": ["all_year"], "cycle_days": 60, "ideal_temp": 20},
    "potatoes": {"season": ["short_rains"], "cycle_days": 100, "ideal_temp": 18},
    "wheat": {"season": ["long_rains"], "cycle_days": 130, "ideal_temp": 20}
}

# Farming practices
PRACTICES = [
    "land_preparation", "planting", "fertilizer_application", "weeding", 
    "pest_control", "disease_management", "irrigation", "harvesting",
    "post_harvest_handling", "soil_testing"
]

# Practice schedules (days after planting)
PRACTICE_SCHEDULES = {
    "land_preparation": [-14],  # Before planting
    "planting": [0],
    "fertilizer_application": [7, 30, 60],
    "weeding": [14, 35, 56],
    "pest_control": [21, 42, 63],
    "disease_management": [28, 56],
    "irrigation": [3, 7, 10, 14, 21, 28],  # Regular intervals
    "harvesting": [None],  # At maturity
    "post_harvest_handling": [None],  # After harvest
    "soil_testing": [-30, 120]  # Before and after season
}


def generate_ai_calendar_dataset(num_samples=5000, output_dir="training_data/ai_calendar"):
    """
    Generate dataset for AI calendar recommendations
    
    Features:
    - crop type
    - planting date
    - region/county
    - soil type
    - current growth stage
    - days since planting
    - season (long rains, short rains)
    - temperature
    - rainfall
    - pest pressure
    - disease occurrence
    
    Target:
    - next recommended practice
    - optimal timing (days from now)
    - priority (high, medium, low)
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"📅 Generating AI Calendar dataset ({num_samples} samples)...")
    
    records = []
    counties = ["Nairobi", "Kiambu", "Nakuru", "Meru", "Kisumu", "Eldoret", "Machakos"]
    soil_types = ["sandy", "loamy", "clay", "silty", "peaty", "chalky"]
    seasons = ["long_rains", "short_rains", "dry_season"]
    growth_stages = ["seedling", "vegetative", "flowering", "fruiting", "mature"]
    
    for i in range(num_samples):
        # Random crop
        crop = random.choice(list(CROPS.keys()))
        crop_info = CROPS[crop]
        
        # Random planting date (within last year)
        days_ago = random.randint(0, crop_info['cycle_days'] + 30)
        planting_date = datetime.now() - timedelta(days=days_ago)
        days_since_planting = days_ago
        
        # Determine growth stage
        cycle_progress = days_since_planting / crop_info['cycle_days']
        if cycle_progress < 0.2:
            growth_stage = "seedling"
        elif cycle_progress < 0.5:
            growth_stage = "vegetative"
        elif cycle_progress < 0.7:
            growth_stage = "flowering"
        elif cycle_progress < 0.95:
            growth_stage = "fruiting"
        else:
            growth_stage = "mature"
        
        # Environmental conditions
        season = random.choice(crop_info['season']) if crop_info['season'] != ["all_year"] else random.choice(seasons)
        county = random.choice(counties)
        soil_type = random.choice(soil_types)
        temperature = crop_info['ideal_temp'] + random.uniform(-5, 5)
        rainfall = random.uniform(50, 200) if season != "dry_season" else random.uniform(0, 50)
        
        # Pest/disease pressure
        pest_pressure = random.choice(["none", "low", "medium", "high"])
        disease_occurrence = random.choice(["none", "low", "medium", "high"])
        
        # Determine next practice based on days since planting
        next_practice = None
        days_until_practice = None
        priority = "low"
        
        # Find next scheduled practice
        for practice, schedules in PRACTICE_SCHEDULES.items():
            if None in schedules:  # Special cases
                if practice == "harvesting" and cycle_progress >= 0.95:
                    next_practice = practice
                    days_until_practice = max(0, crop_info['cycle_days'] - days_since_planting)
                    priority = "high"
                    break
                elif practice == "post_harvest_handling" and cycle_progress >= 1.0:
                    next_practice = practice
                    days_until_practice = 0
                    priority = "high"
                    break
            else:
                for schedule_day in schedules:
                    days_diff = schedule_day - days_since_planting
                    if days_diff >= -3 and days_diff <= 7:  # Within practice window
                        if next_practice is None or days_diff < days_until_practice:
                            next_practice = practice
                            days_until_practice = max(0, days_diff)
                            
                            # Set priority based on timing
                            if days_diff <= 0:
                                priority = "high"
                            elif days_diff <= 3:
                                priority = "medium"
                            else:
                                priority = "low"
        
        # Emergency practices
        if pest_pressure in ["medium", "high"]:
            next_practice = "pest_control"
            days_until_practice = 0
            priority = "high"
        elif disease_occurrence in ["medium", "high"]:
            next_practice = "disease_management"
            days_until_practice = 0
            priority = "high"
        
        # Default if no practice found
        if next_practice is None:
            next_practice = random.choice(["weeding", "irrigation", "fertilizer_application"])
            days_until_practice = random.randint(1, 7)
            priority = "medium"
        
        records.append({
            "crop": crop,
            "planting_date": planting_date.strftime("%Y-%m-%d"),
            "days_since_planting": days_since_planting,
            "growth_stage": growth_stage,
            "season": season,
            "county": county,
            "soil_type": soil_type,
            "temperature": round(temperature, 1),
            "rainfall_mm": round(rainfall, 1),
            "pest_pressure": pest_pressure,
            "disease_occurrence": disease_occurrence,
            "next_practice": next_practice,
            "days_until_practice": days_until_practice,
            "priority": priority
        })
        
        if (i + 1) % 1000 == 0:
            print(f"  Generated {i + 1}/{num_samples} records...")
    
    # Create DataFrame
    df = pd.DataFrame(records)
    
    # Save as CSV
    csv_path = output_path / "ai_calendar.csv"
    df.to_csv(csv_path, index=False)
    print(f"✅ Saved {len(df)} records to {csv_path}")
    
    # Save metadata
    metadata = {
        "dataset_name": "AI Farming Calendar",
        "num_samples": len(df),
        "num_crops": len(CROPS),
        "num_practices": len(PRACTICES),
        "features": list(df.columns[:11]),
        "targets": list(df.columns[11:]),
        "created_at": datetime.now().isoformat(),
        "description": "Dataset for predicting next farming practice with timing and priority"
    }
    
    metadata_path = output_path / "metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"✅ Saved metadata to {metadata_path}")
    
    # Print statistics
    print(f"\n📊 Dataset Statistics:")
    print(f"   Total samples: {len(df)}")
    print(f"   Crops: {df['crop'].nunique()}")
    print(f"   Practices: {df['next_practice'].nunique()}")
    print(f"   \nPractice distribution:")
    print(df['next_practice'].value_counts())
    print(f"   \nPriority distribution:")
    print(df['priority'].value_counts())
    
    return df


def train_ai_calendar_model(data_path="training_data/ai_calendar/ai_calendar.csv"):
    """
    Train Random Forest model for calendar recommendations
    """
    print("\n🤖 Training AI Calendar Model...")
    
    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import train_test_split
        from sklearn.preprocessing import LabelEncoder
        from sklearn.metrics import classification_report, accuracy_score
        import pickle
    except ImportError:
        print("❌ scikit-learn not installed")
        return
    
    # Load data
    df = pd.read_csv(data_path)
    print(f"📊 Loaded {len(df)} records")
    
    # Prepare features
    categorical_cols = ['crop', 'growth_stage', 'season', 'county', 'soil_type', 
                       'pest_pressure', 'disease_occurrence']
    
    # Encode categorical variables
    encoders = {}
    df_encoded = df.copy()
    
    for col in categorical_cols:
        le = LabelEncoder()
        df_encoded[col] = le.fit_transform(df[col])
        encoders[col] = le
    
    # Also encode targets
    practice_encoder = LabelEncoder()
    df_encoded['next_practice_encoded'] = practice_encoder.fit_transform(df['next_practice'])
    encoders['next_practice'] = practice_encoder
    
    priority_encoder = LabelEncoder()
    df_encoded['priority_encoded'] = priority_encoder.fit_transform(df['priority'])
    encoders['priority'] = priority_encoder
    
    # Features and targets
    feature_cols = ['crop', 'days_since_planting', 'growth_stage', 'season', 'county',
                   'soil_type', 'temperature', 'rainfall_mm', 'pest_pressure', 'disease_occurrence']
    
    X = df_encoded[feature_cols]
    y_practice = df_encoded['next_practice_encoded']
    y_timing = df_encoded['days_until_practice']
    y_priority = df_encoded['priority_encoded']
    
    # Split data
    X_train, X_test, y_practice_train, y_practice_test, y_timing_train, y_timing_test, y_priority_train, y_priority_test = train_test_split(
        X, y_practice, y_timing, y_priority, test_size=0.2, random_state=42
    )
    
    print(f"Training set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    # Train practice classifier
    print("\n🔹 Training Practice Classifier...")
    practice_model = RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)
    practice_model.fit(X_train, y_practice_train)
    
    practice_pred = practice_model.predict(X_test)
    practice_acc = accuracy_score(y_practice_test, practice_pred)
    print(f"Practice Prediction Accuracy: {practice_acc:.3f}")
    
    # Train timing regressor
    print("\n🔹 Training Timing Predictor...")
    from sklearn.ensemble import RandomForestRegressor
    timing_model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    timing_model.fit(X_train, y_timing_train)
    
    from sklearn.metrics import mean_absolute_error
    timing_pred = timing_model.predict(X_test)
    timing_mae = mean_absolute_error(y_timing_test, timing_pred)
    print(f"Timing Prediction MAE: {timing_mae:.2f} days")
    
    # Train priority classifier
    print("\n🔹 Training Priority Classifier...")
    priority_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    priority_model.fit(X_train, y_priority_train)
    
    priority_pred = priority_model.predict(X_test)
    priority_acc = accuracy_score(y_priority_test, priority_pred)
    print(f"Priority Prediction Accuracy: {priority_acc:.3f}")
    
    # Save models
    models_dir = Path("trained_models")
    models_dir.mkdir(exist_ok=True)
    
    model_data = {
        'practice_model': practice_model,
        'timing_model': timing_model,
        'priority_model': priority_model,
        'encoders': encoders,
        'features': feature_cols
    }
    
    model_path = models_dir / "ai_calendar_model.pkl"
    with open(model_path, 'wb') as f:
        pickle.dump(model_data, f)
    
    print(f"\n✅ Models saved to {model_path}")
    
    # Save results
    results = {
        "practice_accuracy": float(practice_acc),
        "timing_mae": float(timing_mae),
        "priority_accuracy": float(priority_acc),
        "test_samples": len(X_test),
        "trained_at": datetime.now().isoformat()
    }
    
    results_path = models_dir / "ai_calendar_results.json"
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"✅ Results saved to {results_path}")
    
    return model_data


if __name__ == "__main__":
    # Generate dataset
    df = generate_ai_calendar_dataset(num_samples=5000)
    
    # Train model
    models = train_ai_calendar_model()
    
    print("\n🎉 AI Calendar dataset and models ready!")
