"""
Example Model Training Script
Demonstrates how to use the generated datasets to train AgroShield AI models
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow warnings

import json
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

# TensorFlow for image models
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    from tensorflow.keras.applications import MobileNetV3Small
    from tensorflow.keras.preprocessing.image import ImageDataGenerator
    HAS_TF = True
except ImportError:
    print("⚠️  TensorFlow not installed. Install with: pip install tensorflow")
    HAS_TF = False

# Scikit-learn for tabular models
try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_squared_error, r2_score
    from sklearn.preprocessing import LabelEncoder
    HAS_SKLEARN = True
except ImportError:
    print("⚠️  Scikit-learn not installed. Install with: pip install scikit-learn")
    HAS_SKLEARN = False

BASE_DIR = Path(__file__).parent / "training_data"
MODELS_DIR = Path(__file__).parent / "trained_models"
MODELS_DIR.mkdir(exist_ok=True)


# ============================================================================
# IMAGE CLASSIFICATION EXAMPLE: PEST DETECTION
# ============================================================================

def train_pest_detection_model():
    """Train pest detection model using MobileNet V3"""
    if not HAS_TF:
        print("❌ TensorFlow required for image model training")
        return
    
    print("\n🐛 Training Pest Detection Model...")
    
    data_dir = BASE_DIR / "pest_detection"
    if not data_dir.exists():
        print(f"❌ Dataset not found: {data_dir}")
        return
    
    # Data augmentation
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        zoom_range=0.2,
        validation_split=0.2
    )
    
    # Load training data
    train_generator = train_datagen.flow_from_directory(
        data_dir,
        target_size=(224, 224),
        batch_size=32,
        class_mode='categorical',
        subset='training'
    )
    
    # Load validation data
    val_generator = train_datagen.flow_from_directory(
        data_dir,
        target_size=(224, 224),
        batch_size=32,
        class_mode='categorical',
        subset='validation'
    )
    
    num_classes = len(train_generator.class_indices)
    print(f"Classes: {list(train_generator.class_indices.keys())}")
    print(f"Training samples: {train_generator.samples}")
    print(f"Validation samples: {val_generator.samples}")
    
    # Build model with transfer learning
    base_model = MobileNetV3Small(
        input_shape=(224, 224, 3),
        include_top=False,
        weights='imagenet'
    )
    base_model.trainable = False  # Freeze base model
    
    model = keras.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(num_classes, activation='softmax')
    ])
    
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    print("\n📊 Model Architecture:")
    model.summary()
    
    # Train model
    print("\n🚀 Training...")
    history = model.fit(
        train_generator,
        validation_data=val_generator,
        epochs=10,
        verbose=1
    )
    
    # Save model
    model_path = MODELS_DIR / "pest_detection_model.h5"
    model.save(model_path)
    print(f"\n✅ Model saved: {model_path}")
    
    # Save class mapping
    class_mapping = {v: k for k, v in train_generator.class_indices.items()}
    with open(MODELS_DIR / "pest_detection_classes.json", 'w') as f:
        json.dump(class_mapping, f, indent=2)
    
    # Results
    final_acc = history.history['accuracy'][-1]
    final_val_acc = history.history['val_accuracy'][-1]
    print(f"\n📈 Results:")
    print(f"   Training accuracy: {final_acc:.2%}")
    print(f"   Validation accuracy: {final_val_acc:.2%}")
    
    return model, history


# ============================================================================
# IMAGE CLASSIFICATION EXAMPLE: SOIL DIAGNOSTICS
# ============================================================================

def train_soil_diagnostics_model():
    """Train soil type classification model"""
    if not HAS_TF:
        print("❌ TensorFlow required for image model training")
        return
    
    print("\n🌱 Training Soil Diagnostics Model...")
    
    data_dir = BASE_DIR / "soil_diagnostics"
    if not data_dir.exists():
        print(f"❌ Dataset not found: {data_dir}")
        return
    
    # Similar to pest detection but with different augmentation
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=30,
        zoom_range=0.3,
        horizontal_flip=True,
        vertical_flip=True,
        validation_split=0.2
    )
    
    train_generator = train_datagen.flow_from_directory(
        data_dir,
        target_size=(224, 224),
        batch_size=16,
        class_mode='categorical',
        subset='training'
    )
    
    val_generator = train_datagen.flow_from_directory(
        data_dir,
        target_size=(224, 224),
        batch_size=16,
        class_mode='categorical',
        subset='validation'
    )
    
    num_classes = len(train_generator.class_indices)
    print(f"Soil types: {list(train_generator.class_indices.keys())}")
    
    # Simple CNN for soil classification
    model = keras.Sequential([
        layers.Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(128, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        layers.Flatten(),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.4),
        layers.Dense(num_classes, activation='softmax')
    ])
    
    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # Train
    history = model.fit(
        train_generator,
        validation_data=val_generator,
        epochs=15,
        verbose=1
    )
    
    # Save
    model_path = MODELS_DIR / "soil_diagnostics_model.h5"
    model.save(model_path)
    print(f"\n✅ Model saved: {model_path}")
    
    return model, history


# ============================================================================
# REGRESSION EXAMPLE: YIELD PREDICTION
# ============================================================================

def train_yield_prediction_model():
    """Train yield prediction model using Random Forest"""
    if not HAS_SKLEARN:
        print("❌ Scikit-learn required for yield prediction")
        return
    
    print("\n🌾 Training Yield Prediction Model...")
    
    data_file = BASE_DIR / "yield_prediction" / "yield_prediction.csv"
    if not data_file.exists():
        print(f"❌ Dataset not found: {data_file}")
        return
    
    # Load data
    df = pd.read_csv(data_file)
    print(f"Loaded {len(df)} records")
    print(f"Features: {list(df.columns)}")
    
    # Prepare features
    categorical_cols = ['crop', 'pest_pressure', 'disease_occurrence', 'quality_grade']
    
    # Encode categorical variables
    df_encoded = df.copy()
    encoders = {}
    for col in categorical_cols:
        if col in df.columns:
            le = LabelEncoder()
            df_encoded[col] = le.fit_transform(df[col])
            encoders[col] = le
    
    # Features and target
    target = 'yield_per_hectare_tons'
    features = [col for col in df_encoded.columns if col not in [target, 'total_yield_tons']]
    
    X = df_encoded[features]
    y = df_encoded[target]
    
    print(f"\nFeatures: {features}")
    print(f"Target: {target}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"\nTraining set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    # Train Random Forest
    print("\n🚀 Training Random Forest...")
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=15,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    train_pred = model.predict(X_train)
    test_pred = model.predict(X_test)
    
    train_r2 = r2_score(y_train, train_pred)
    test_r2 = r2_score(y_test, test_pred)
    train_rmse = np.sqrt(mean_squared_error(y_train, train_pred))
    test_rmse = np.sqrt(mean_squared_error(y_test, test_pred))
    
    print(f"\n📈 Results:")
    print(f"   Training R²: {train_r2:.3f}")
    print(f"   Test R²: {test_r2:.3f}")
    print(f"   Training RMSE: {train_rmse:.2f} tons/hectare")
    print(f"   Test RMSE: {test_rmse:.2f} tons/hectare")
    
    # Feature importance
    importance = pd.DataFrame({
        'feature': features,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(f"\n🎯 Top 5 Important Features:")
    for _, row in importance.head(5).iterrows():
        print(f"   {row['feature']}: {row['importance']:.3f}")
    
    # Save model
    import pickle
    model_path = MODELS_DIR / "yield_prediction_model.pkl"
    with open(model_path, 'wb') as f:
        pickle.dump({
            'model': model,
            'encoders': encoders,
            'features': features
        }, f)
    print(f"\n✅ Model saved: {model_path}")
    
    return model, importance


# ============================================================================
# TIME SERIES EXAMPLE: CLIMATE PREDICTION
# ============================================================================

def train_climate_prediction_model():
    """Train LSTM model for climate forecasting"""
    if not HAS_TF:
        print("❌ TensorFlow required for LSTM training")
        return
    
    print("\n🌦️  Training Climate Prediction Model...")
    
    data_file = BASE_DIR / "climate_prediction" / "climate_timeseries.csv"
    if not data_file.exists():
        print(f"❌ Dataset not found: {data_file}")
        return
    
    # Load data
    df = pd.read_csv(data_file)
    print(f"Loaded {len(df)} daily records")
    
    # Prepare sequences
    feature_cols = [col for col in df.columns if col != 'date']
    data = df[feature_cols].values
    
    # Normalize
    from sklearn.preprocessing import MinMaxScaler
    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(data)
    
    # Create sequences
    sequence_length = 30
    X, y = [], []
    
    for i in range(len(data_scaled) - sequence_length - 7):
        X.append(data_scaled[i:i + sequence_length])
        y.append(data_scaled[i + sequence_length:i + sequence_length + 7, 0])  # Predict temp
    
    X = np.array(X)
    y = np.array(y)
    
    print(f"\nSequence shape: {X.shape}")
    print(f"Target shape: {y.shape}")
    
    # Split data
    split = int(0.8 * len(X))
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]
    
    # Build LSTM model
    model = keras.Sequential([
        layers.LSTM(64, return_sequences=True, input_shape=(sequence_length, len(feature_cols))),
        layers.Dropout(0.2),
        layers.LSTM(32, return_sequences=False),
        layers.Dropout(0.2),
        layers.Dense(32, activation='relu'),
        layers.Dense(7)  # Predict 7 days ahead
    ])
    
    model.compile(
        optimizer='adam',
        loss='mse',
        metrics=['mae']
    )
    
    print("\n🚀 Training LSTM...")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=20,
        batch_size=32,
        verbose=1
    )
    
    # Save model
    model_path = MODELS_DIR / "climate_prediction_model.h5"
    model.save(model_path)
    
    # Save scaler
    import pickle
    with open(MODELS_DIR / "climate_scaler.pkl", 'wb') as f:
        pickle.dump(scaler, f)
    
    print(f"\n✅ Model saved: {model_path}")
    
    return model, history


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Run all training examples"""
    print("\n" + "="*60)
    print("🚀 AgroShield Model Training Examples")
    print("="*60)
    
    if not BASE_DIR.exists():
        print(f"\n❌ Training data not found!")
        print(f"Run generate_training_datasets.py first")
        return
    
    print("\nSelect model to train:")
    print("1. Pest Detection (Image CNN)")
    print("2. Soil Diagnostics (Image CNN)")
    print("3. Yield Prediction (Random Forest)")
    print("4. Climate Prediction (LSTM)")
    print("5. Train All Models")
    
    choice = input("\nEnter choice (1-5): ").strip()
    
    if choice == '1':
        train_pest_detection_model()
    elif choice == '2':
        train_soil_diagnostics_model()
    elif choice == '3':
        train_yield_prediction_model()
    elif choice == '4':
        train_climate_prediction_model()
    elif choice == '5':
        train_pest_detection_model()
        train_soil_diagnostics_model()
        train_yield_prediction_model()
        train_climate_prediction_model()
    else:
        print("Invalid choice!")
    
    print("\n" + "="*60)
    print("✅ Training Complete!")
    print(f"Models saved to: {MODELS_DIR}")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
