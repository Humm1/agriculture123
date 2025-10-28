"""
Enhanced Model Training Service
Integrates synthetic dataset generation with model training
"""

import os
import sys
import json
import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple, List
import threading

# TensorFlow
try:
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    from tensorflow.keras.applications import MobileNetV3Small
    from tensorflow.keras.preprocessing.image import ImageDataGenerator
    HAS_TF = True
except ImportError:
    HAS_TF = False

# Scikit-learn
try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_squared_error, r2_score
    from sklearn.preprocessing import LabelEncoder, MinMaxScaler
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False


class EnhancedModelTrainingService:
    """Service for training all AgroShield AI models"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.training_data_dir = self.base_dir / "training_data"
        self.models_dir = self.base_dir / "trained_models"
        self.models_dir.mkdir(exist_ok=True)
        
        # Training status tracking
        self.training_status = {
            "is_training": False,
            "current_model": None,
            "progress": 0,
            "message": "Idle",
            "start_time": None,
            "results": None,
            "error": None
        }
        
        self.training_history = []
        self._load_training_history()
    
    def _load_training_history(self):
        """Load training history from file"""
        history_file = self.models_dir / "training_history.json"
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    self.training_history = json.load(f)
            except:
                self.training_history = []
    
    def _save_training_history(self):
        """Save training history to file"""
        history_file = self.models_dir / "training_history.json"
        with open(history_file, 'w') as f:
            json.dump(self.training_history, f, indent=2)
    
    def _update_status(self, progress: int, message: str):
        """Update training status"""
        self.training_status["progress"] = progress
        self.training_status["message"] = message
        print(f"[{progress}%] {message}")
    
    def _add_to_history(self, model_type: str, results: Dict):
        """Add training run to history"""
        self.training_history.append({
            "model_type": model_type,
            "timestamp": datetime.now().isoformat(),
            "results": results
        })
        self._save_training_history()
    
    # ========================================================================
    # PEST DETECTION MODEL
    # ========================================================================
    
    def train_pest_detection_model(self, epochs: int = 10) -> Dict:
        """Train pest detection model"""
        if not HAS_TF:
            raise RuntimeError("TensorFlow not installed")
        
        self._update_status(10, "Starting pest detection model training...")
        
        data_dir = self.training_data_dir / "pest_detection"
        if not data_dir.exists():
            raise FileNotFoundError(f"Dataset not found: {data_dir}")
        
        self._update_status(20, "Loading pest detection dataset...")
        
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
        
        train_generator = train_datagen.flow_from_directory(
            data_dir,
            target_size=(224, 224),
            batch_size=32,
            class_mode='categorical',
            subset='training'
        )
        
        val_generator = train_datagen.flow_from_directory(
            data_dir,
            target_size=(224, 224),
            batch_size=32,
            class_mode='categorical',
            subset='validation'
        )
        
        num_classes = len(train_generator.class_indices)
        
        self._update_status(30, f"Building model for {num_classes} pest classes...")
        
        # Build model with MobileNetV3
        base_model = MobileNetV3Small(
            input_shape=(224, 224, 3),
            include_top=False,
            weights='imagenet'
        )
        base_model.trainable = False
        
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
        
        self._update_status(40, f"Training for {epochs} epochs...")
        
        # Train
        history = model.fit(
            train_generator,
            validation_data=val_generator,
            epochs=epochs,
            verbose=0
        )
        
        self._update_status(80, "Saving pest detection model...")
        
        # Save model
        model_path = self.models_dir / "pest_detection_model.h5"
        model.save(str(model_path))
        
        # Save class mapping
        class_mapping = {v: k for k, v in train_generator.class_indices.items()}
        with open(self.models_dir / "pest_detection_classes.json", 'w') as f:
            json.dump(class_mapping, f, indent=2)
        
        # Results
        results = {
            "model_type": "pest_detection",
            "classes": list(train_generator.class_indices.keys()),
            "num_classes": num_classes,
            "training_samples": train_generator.samples,
            "validation_samples": val_generator.samples,
            "epochs": epochs,
            "final_accuracy": float(history.history['accuracy'][-1]),
            "final_val_accuracy": float(history.history['val_accuracy'][-1]),
            "model_path": str(model_path),
            "trained_at": datetime.now().isoformat()
        }
        
        self._update_status(100, "Pest detection training completed!")
        return results
    
    # ========================================================================
    # DISEASE DETECTION MODEL
    # ========================================================================
    
    def train_disease_detection_model(self, epochs: int = 10) -> Dict:
        """Train disease detection model"""
        if not HAS_TF:
            raise RuntimeError("TensorFlow not installed")
        
        self._update_status(10, "Starting disease detection model training...")
        
        data_dir = self.training_data_dir / "disease_detection"
        if not data_dir.exists():
            raise FileNotFoundError(f"Dataset not found: {data_dir}")
        
        self._update_status(20, "Loading disease detection dataset...")
        
        train_datagen = ImageDataGenerator(
            rescale=1./255,
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            horizontal_flip=True,
            zoom_range=0.2,
            validation_split=0.2
        )
        
        train_generator = train_datagen.flow_from_directory(
            data_dir,
            target_size=(224, 224),
            batch_size=32,
            class_mode='categorical',
            subset='training'
        )
        
        val_generator = train_datagen.flow_from_directory(
            data_dir,
            target_size=(224, 224),
            batch_size=32,
            class_mode='categorical',
            subset='validation'
        )
        
        num_classes = len(train_generator.class_indices)
        
        self._update_status(30, f"Building model for {num_classes} disease classes...")
        
        base_model = MobileNetV3Small(
            input_shape=(224, 224, 3),
            include_top=False,
            weights='imagenet'
        )
        base_model.trainable = False
        
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
        
        self._update_status(40, f"Training for {epochs} epochs...")
        
        history = model.fit(
            train_generator,
            validation_data=val_generator,
            epochs=epochs,
            verbose=0
        )
        
        self._update_status(80, "Saving disease detection model...")
        
        model_path = self.models_dir / "disease_detection_model.h5"
        model.save(str(model_path))
        
        class_mapping = {v: k for k, v in train_generator.class_indices.items()}
        with open(self.models_dir / "disease_detection_classes.json", 'w') as f:
            json.dump(class_mapping, f, indent=2)
        
        results = {
            "model_type": "disease_detection",
            "classes": list(train_generator.class_indices.keys()),
            "num_classes": num_classes,
            "training_samples": train_generator.samples,
            "validation_samples": val_generator.samples,
            "epochs": epochs,
            "final_accuracy": float(history.history['accuracy'][-1]),
            "final_val_accuracy": float(history.history['val_accuracy'][-1]),
            "model_path": str(model_path),
            "trained_at": datetime.now().isoformat()
        }
        
        self._update_status(100, "Disease detection training completed!")
        return results
    
    # ========================================================================
    # SOIL DIAGNOSTICS MODEL
    # ========================================================================
    
    def train_soil_diagnostics_model(self, epochs: int = 15) -> Dict:
        """Train soil type classification model"""
        if not HAS_TF:
            raise RuntimeError("TensorFlow not installed")
        
        self._update_status(10, "Starting soil diagnostics model training...")
        
        data_dir = self.training_data_dir / "soil_diagnostics"
        if not data_dir.exists():
            raise FileNotFoundError(f"Dataset not found: {data_dir}")
        
        self._update_status(20, "Loading soil diagnostics dataset...")
        
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
        
        self._update_status(30, f"Building CNN for {num_classes} soil types...")
        
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
        
        self._update_status(40, f"Training for {epochs} epochs...")
        
        history = model.fit(
            train_generator,
            validation_data=val_generator,
            epochs=epochs,
            verbose=0
        )
        
        self._update_status(80, "Saving soil diagnostics model...")
        
        model_path = self.models_dir / "soil_diagnostics_model.h5"
        model.save(str(model_path))
        
        class_mapping = {v: k for k, v in train_generator.class_indices.items()}
        with open(self.models_dir / "soil_diagnostics_classes.json", 'w') as f:
            json.dump(class_mapping, f, indent=2)
        
        results = {
            "model_type": "soil_diagnostics",
            "classes": list(train_generator.class_indices.keys()),
            "num_classes": num_classes,
            "training_samples": train_generator.samples,
            "validation_samples": val_generator.samples,
            "epochs": epochs,
            "final_accuracy": float(history.history['accuracy'][-1]),
            "final_val_accuracy": float(history.history['val_accuracy'][-1]),
            "model_path": str(model_path),
            "trained_at": datetime.now().isoformat()
        }
        
        self._update_status(100, "Soil diagnostics training completed!")
        return results
    
    # ========================================================================
    # YIELD PREDICTION MODEL
    # ========================================================================
    
    def train_yield_prediction_model(self) -> Dict:
        """Train yield prediction Random Forest model"""
        if not HAS_SKLEARN:
            raise RuntimeError("Scikit-learn not installed")
        
        self._update_status(10, "Starting yield prediction model training...")
        
        data_file = self.training_data_dir / "yield_prediction" / "yield_prediction.csv"
        if not data_file.exists():
            raise FileNotFoundError(f"Dataset not found: {data_file}")
        
        self._update_status(20, "Loading yield prediction dataset...")
        
        df = pd.read_csv(data_file)
        
        categorical_cols = ['crop', 'pest_pressure', 'disease_occurrence', 'quality_grade']
        df_encoded = df.copy()
        encoders = {}
        
        for col in categorical_cols:
            if col in df.columns:
                le = LabelEncoder()
                df_encoded[col] = le.fit_transform(df[col])
                encoders[col] = le
        
        target = 'yield_per_hectare_tons'
        features = [col for col in df_encoded.columns if col not in [target, 'total_yield_tons']]
        
        X = df_encoded[features]
        y = df_encoded[target]
        
        self._update_status(30, "Splitting data and training Random Forest...")
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        from sklearn.ensemble import RandomForestRegressor
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )
        
        self._update_status(50, "Training Random Forest...")
        model.fit(X_train, y_train)
        
        self._update_status(80, "Evaluating model...")
        
        test_pred = model.predict(X_test)
        test_r2 = r2_score(y_test, test_pred)
        test_rmse = np.sqrt(mean_squared_error(y_test, test_pred))
        
        # Feature importance
        importance = pd.DataFrame({
            'feature': features,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        self._update_status(90, "Saving yield prediction model...")
        
        model_path = self.models_dir / "yield_prediction_model.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump({
                'model': model,
                'encoders': encoders,
                'features': features
            }, f)
        
        results = {
            "model_type": "yield_prediction",
            "features": features,
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "test_r2": float(test_r2),
            "test_rmse": float(test_rmse),
            "top_features": importance.head(5).to_dict('records'),
            "model_path": str(model_path),
            "trained_at": datetime.now().isoformat()
        }
        
        self._update_status(100, "Yield prediction training completed!")
        return results
    
    # ========================================================================
    # CLIMATE PREDICTION MODEL
    # ========================================================================
    
    def train_climate_prediction_model(self, epochs: int = 20) -> Dict:
        """Train LSTM climate prediction model"""
        if not HAS_TF:
            raise RuntimeError("TensorFlow not installed")
        
        self._update_status(10, "Starting climate prediction model training...")
        
        data_file = self.training_data_dir / "climate_prediction" / "climate_timeseries.csv"
        if not data_file.exists():
            raise FileNotFoundError(f"Dataset not found: {data_file}")
        
        self._update_status(20, "Loading climate timeseries data...")
        
        df = pd.read_csv(data_file)
        feature_cols = [col for col in df.columns if col != 'date']
        data = df[feature_cols].values
        
        # Normalize
        scaler = MinMaxScaler()
        data_scaled = scaler.fit_transform(data)
        
        # Create sequences
        sequence_length = 30
        X, y = [], []
        
        for i in range(len(data_scaled) - sequence_length - 7):
            X.append(data_scaled[i:i + sequence_length])
            y.append(data_scaled[i + sequence_length:i + sequence_length + 7, 0])
        
        X = np.array(X)
        y = np.array(y)
        
        split = int(0.8 * len(X))
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]
        
        self._update_status(30, "Building LSTM model...")
        
        model = keras.Sequential([
            layers.LSTM(64, return_sequences=True, input_shape=(sequence_length, len(feature_cols))),
            layers.Dropout(0.2),
            layers.LSTM(32, return_sequences=False),
            layers.Dropout(0.2),
            layers.Dense(32, activation='relu'),
            layers.Dense(7)
        ])
        
        model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        
        self._update_status(40, f"Training LSTM for {epochs} epochs...")
        
        history = model.fit(
            X_train, y_train,
            validation_data=(X_test, y_test),
            epochs=epochs,
            batch_size=32,
            verbose=0
        )
        
        self._update_status(80, "Saving climate prediction model...")
        
        model_path = self.models_dir / "climate_prediction_model.h5"
        model.save(str(model_path))
        
        with open(self.models_dir / "climate_scaler.pkl", 'wb') as f:
            pickle.dump(scaler, f)
        
        results = {
            "model_type": "climate_prediction",
            "sequence_length": sequence_length,
            "features": feature_cols,
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "epochs": epochs,
            "final_loss": float(history.history['loss'][-1]),
            "final_val_loss": float(history.history['val_loss'][-1]),
            "final_mae": float(history.history['mae'][-1]),
            "model_path": str(model_path),
            "trained_at": datetime.now().isoformat()
        }
        
        self._update_status(100, "Climate prediction training completed!")
        return results
    
    # ========================================================================
    # ORCHESTRATION
    # ========================================================================
    
    def train_model(self, model_type: str, **kwargs) -> Dict:
        """Train a specific model"""
        self.training_status["is_training"] = True
        self.training_status["current_model"] = model_type
        self.training_status["start_time"] = datetime.now().isoformat()
        self.training_status["error"] = None
        self.training_status["results"] = None
        
        try:
            if model_type == "pest_detection":
                results = self.train_pest_detection_model(**kwargs)
            elif model_type == "disease_detection":
                results = self.train_disease_detection_model(**kwargs)
            elif model_type == "soil_diagnostics":
                results = self.train_soil_diagnostics_model(**kwargs)
            elif model_type == "yield_prediction":
                results = self.train_yield_prediction_model()
            elif model_type == "climate_prediction":
                results = self.train_climate_prediction_model(**kwargs)
            else:
                raise ValueError(f"Unknown model type: {model_type}")
            
            self.training_status["results"] = results
            self._add_to_history(model_type, results)
            return results
            
        except Exception as e:
            self.training_status["error"] = str(e)
            self.training_status["message"] = f"Training failed: {str(e)}"
            raise
        finally:
            self.training_status["is_training"] = False
            self.training_status["current_model"] = None
    
    def get_status(self) -> Dict:
        """Get current training status"""
        return self.training_status.copy()
    
    def get_history(self, model_type: Optional[str] = None) -> List[Dict]:
        """Get training history"""
        if model_type:
            return [h for h in self.training_history if h["model_type"] == model_type]
        return self.training_history
    
    def get_available_models(self) -> Dict:
        """Get list of trained models"""
        models = {}
        for model_file in self.models_dir.glob("*.h5"):
            model_name = model_file.stem
            models[model_name] = {
                "path": str(model_file),
                "size_mb": model_file.stat().st_size / (1024 * 1024),
                "modified": datetime.fromtimestamp(model_file.stat().st_mtime).isoformat()
            }
        
        for model_file in self.models_dir.glob("*.pkl"):
            model_name = model_file.stem
            models[model_name] = {
                "path": str(model_file),
                "size_mb": model_file.stat().st_size / (1024 * 1024),
                "modified": datetime.fromtimestamp(model_file.stat().st_mtime).isoformat()
            }
        
        return models
