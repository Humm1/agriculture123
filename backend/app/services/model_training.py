"""
Model Training Service
Uses Supabase data to retrain and improve AI models
"""

import os
import tensorflow as tf
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
import requests
from io import BytesIO
from PIL import Image
import json
from datetime import datetime

from app.services.data_collection import DataCollectionService


class ModelTrainingService:
    """Service to retrain models using collected data"""
    
    def __init__(self):
        self.data_service = DataCollectionService()
        self.models_dir = Path("models")
        self.models_dir.mkdir(exist_ok=True)
        self.training_logs_dir = Path("training_logs")
        self.training_logs_dir.mkdir(exist_ok=True)
        
        # Image preprocessing parameters
        self.img_size = (224, 224)
        self.batch_size = 32
        self.epochs = 10
    
    # ===================================
    # DATA PREPARATION
    # ===================================
    
    def download_and_preprocess_images(
        self, 
        image_urls: List[str], 
        labels: List[str]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Download images from URLs and preprocess them
        
        Args:
            image_urls: List of image URLs from Supabase storage
            labels: Corresponding labels
        
        Returns:
            Tuple of (images array, labels array)
        """
        print(f"📥 Downloading and preprocessing {len(image_urls)} images...")
        
        images = []
        valid_labels = []
        
        for idx, (url, label) in enumerate(zip(image_urls, labels)):
            try:
                # Download image
                response = requests.get(url, timeout=10)
                img = Image.open(BytesIO(response.content))
                
                # Convert to RGB if needed
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize
                img = img.resize(self.img_size)
                
                # Convert to array and normalize
                img_array = np.array(img) / 255.0
                
                images.append(img_array)
                valid_labels.append(label)
                
                if (idx + 1) % 10 == 0:
                    print(f"  Processed {idx + 1}/{len(image_urls)} images")
                    
            except Exception as e:
                print(f"  ⚠️ Failed to process image {idx}: {e}")
                continue
        
        if not images:
            raise ValueError("No valid images were downloaded")
        
        print(f"✅ Successfully processed {len(images)} images")
        
        # Convert to numpy arrays
        X = np.array(images)
        
        # Encode labels
        unique_labels = sorted(list(set(valid_labels)))
        label_to_idx = {label: idx for idx, label in enumerate(unique_labels)}
        y = np.array([label_to_idx[label] for label in valid_labels])
        
        # Save label mapping
        self._save_label_mapping(unique_labels, label_to_idx)
        
        return X, y, unique_labels
    
    def _save_label_mapping(self, labels: List[str], mapping: Dict):
        """Save label to index mapping"""
        mapping_data = {
            "labels": labels,
            "mapping": mapping,
            "created_at": datetime.now().isoformat()
        }
        
        filepath = self.models_dir / "label_mapping.json"
        with open(filepath, 'w') as f:
            json.dump(mapping_data, f, indent=2)
        
        print(f"💾 Saved label mapping to {filepath}")
    
    # ===================================
    # MODEL BUILDING
    # ===================================
    
    def build_classification_model(
        self, 
        num_classes: int,
        model_type: str = "mobilenet"
    ) -> tf.keras.Model:
        """
        Build a classification model
        
        Args:
            num_classes: Number of output classes
            model_type: Base model architecture ('mobilenet', 'resnet', 'efficientnet')
        
        Returns:
            Compiled Keras model
        """
        print(f"🏗️ Building {model_type} model with {num_classes} classes...")
        
        # Load base model
        if model_type == "mobilenet":
            base_model = tf.keras.applications.MobileNetV2(
                input_shape=(*self.img_size, 3),
                include_top=False,
                weights='imagenet'
            )
        elif model_type == "resnet":
            base_model = tf.keras.applications.ResNet50(
                input_shape=(*self.img_size, 3),
                include_top=False,
                weights='imagenet'
            )
        elif model_type == "efficientnet":
            base_model = tf.keras.applications.EfficientNetB0(
                input_shape=(*self.img_size, 3),
                include_top=False,
                weights='imagenet'
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        # Freeze base model
        base_model.trainable = False
        
        # Build complete model
        model = tf.keras.Sequential([
            base_model,
            tf.keras.layers.GlobalAveragePooling2D(),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(256, activation='relu'),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(num_classes, activation='softmax')
        ])
        
        # Compile
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy', tf.keras.metrics.TopKCategoricalAccuracy(k=3, name='top_3_accuracy')]
        )
        
        print("✅ Model built successfully")
        return model
    
    # ===================================
    # MODEL TRAINING
    # ===================================
    
    def train_pest_detection_model(
        self,
        min_samples_per_class: int = 10,
        validation_split: float = 0.2
    ) -> Dict:
        """
        Train pest detection model with Supabase data
        
        Args:
            min_samples_per_class: Minimum samples required per class
            validation_split: Fraction of data for validation
        
        Returns:
            Training history and metrics
        """
        print("🚀 Starting pest detection model training...")
        
        # Fetch training data
        training_data = self.data_service.fetch_pest_training_data()
        
        if len(training_data["labels"]) < min_samples_per_class:
            raise ValueError(f"Not enough training data. Need at least {min_samples_per_class} samples.")
        
        # Download and preprocess images
        X, y, unique_labels = self.download_and_preprocess_images(
            training_data["image_urls"],
            training_data["labels"]
        )
        
        # Check class distribution
        unique, counts = np.unique(y, return_counts=True)
        class_dist = dict(zip([unique_labels[i] for i in unique], counts))
        print(f"📊 Class distribution: {class_dist}")
        
        # Build model
        model = self.build_classification_model(len(unique_labels))
        
        # Data augmentation
        data_augmentation = tf.keras.Sequential([
            tf.keras.layers.RandomFlip("horizontal"),
            tf.keras.layers.RandomRotation(0.2),
            tf.keras.layers.RandomZoom(0.2),
            tf.keras.layers.RandomContrast(0.2)
        ])
        
        # Split data
        split_idx = int(len(X) * (1 - validation_split))
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]
        
        print(f"📚 Training set: {len(X_train)} samples")
        print(f"🔍 Validation set: {len(X_val)} samples")
        
        # Callbacks
        callbacks = [
            tf.keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=3,
                restore_best_weights=True
            ),
            tf.keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=2,
                min_lr=1e-7
            ),
            tf.keras.callbacks.ModelCheckpoint(
                filepath=str(self.models_dir / 'pest_detection_best.h5'),
                monitor='val_accuracy',
                save_best_only=True
            )
        ]
        
        # Train model
        print("🏋️ Training model...")
        history = model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=self.epochs,
            batch_size=self.batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        # Save final model
        model_path = self.models_dir / f"pest_detection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.h5"
        model.save(model_path)
        print(f"💾 Model saved to {model_path}")
        
        # Evaluate
        val_loss, val_acc, val_top3 = model.evaluate(X_val, y_val, verbose=0)
        
        results = {
            "model_path": str(model_path),
            "training_samples": len(X_train),
            "validation_samples": len(X_val),
            "num_classes": len(unique_labels),
            "classes": unique_labels,
            "class_distribution": class_dist,
            "final_val_accuracy": float(val_acc),
            "final_val_top3_accuracy": float(val_top3),
            "final_val_loss": float(val_loss),
            "training_history": {
                "accuracy": [float(x) for x in history.history['accuracy']],
                "val_accuracy": [float(x) for x in history.history['val_accuracy']],
                "loss": [float(x) for x in history.history['loss']],
                "val_loss": [float(x) for x in history.history['val_loss']]
            }
        }
        
        # Save training results
        self._save_training_results("pest_detection", results)
        
        print(f"✅ Training complete! Validation accuracy: {val_acc:.4f}")
        return results
    
    def train_disease_detection_model(
        self,
        min_samples_per_class: int = 10,
        validation_split: float = 0.2
    ) -> Dict:
        """Train disease detection model with Supabase data"""
        print("🚀 Starting disease detection model training...")
        
        training_data = self.data_service.fetch_disease_training_data()
        
        if len(training_data["labels"]) < min_samples_per_class:
            raise ValueError(f"Not enough training data. Need at least {min_samples_per_class} samples.")
        
        X, y, unique_labels = self.download_and_preprocess_images(
            training_data["image_urls"],
            training_data["labels"]
        )
        
        unique, counts = np.unique(y, return_counts=True)
        class_dist = dict(zip([unique_labels[i] for i in unique], counts))
        print(f"📊 Class distribution: {class_dist}")
        
        model = self.build_classification_model(len(unique_labels))
        
        split_idx = int(len(X) * (1 - validation_split))
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]
        
        print(f"📚 Training set: {len(X_train)} samples")
        print(f"🔍 Validation set: {len(X_val)} samples")
        
        callbacks = [
            tf.keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=3,
                restore_best_weights=True
            ),
            tf.keras.callbacks.ModelCheckpoint(
                filepath=str(self.models_dir / 'disease_detection_best.h5'),
                monitor='val_accuracy',
                save_best_only=True
            )
        ]
        
        print("🏋️ Training model...")
        history = model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=self.epochs,
            batch_size=self.batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        model_path = self.models_dir / f"disease_detection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.h5"
        model.save(model_path)
        print(f"💾 Model saved to {model_path}")
        
        val_loss, val_acc, val_top3 = model.evaluate(X_val, y_val, verbose=0)
        
        results = {
            "model_path": str(model_path),
            "training_samples": len(X_train),
            "validation_samples": len(X_val),
            "num_classes": len(unique_labels),
            "classes": unique_labels,
            "class_distribution": class_dist,
            "final_val_accuracy": float(val_acc),
            "final_val_top3_accuracy": float(val_top3),
            "final_val_loss": float(val_loss)
        }
        
        self._save_training_results("disease_detection", results)
        
        print(f"✅ Training complete! Validation accuracy: {val_acc:.4f}")
        return results
    
    def train_storage_assessment_model(
        self,
        min_samples_per_class: int = 10,
        validation_split: float = 0.2
    ) -> Dict:
        """Train storage condition assessment model"""
        print("🚀 Starting storage assessment model training...")
        
        training_data = self.data_service.fetch_storage_training_data()
        
        if len(training_data["labels"]) < min_samples_per_class:
            raise ValueError(f"Not enough training data. Need at least {min_samples_per_class} samples.")
        
        X, y, unique_labels = self.download_and_preprocess_images(
            training_data["image_urls"],
            training_data["labels"]
        )
        
        # Storage has ordered classes (excellent > good > fair > poor > critical)
        ordered_labels = ['excellent', 'good', 'fair', 'poor', 'critical']
        unique_labels = [l for l in ordered_labels if l in unique_labels]
        
        unique, counts = np.unique(y, return_counts=True)
        class_dist = dict(zip([unique_labels[i] for i in unique], counts))
        print(f"📊 Class distribution: {class_dist}")
        
        model = self.build_classification_model(len(unique_labels))
        
        split_idx = int(len(X) * (1 - validation_split))
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]
        
        print(f"📚 Training set: {len(X_train)} samples")
        print(f"🔍 Validation set: {len(X_val)} samples")
        
        callbacks = [
            tf.keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=3,
                restore_best_weights=True
            ),
            tf.keras.callbacks.ModelCheckpoint(
                filepath=str(self.models_dir / 'storage_assessment_best.h5'),
                monitor='val_accuracy',
                save_best_only=True
            )
        ]
        
        print("🏋️ Training model...")
        history = model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=self.epochs,
            batch_size=self.batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        model_path = self.models_dir / f"storage_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.h5"
        model.save(model_path)
        print(f"💾 Model saved to {model_path}")
        
        val_loss, val_acc, val_top3 = model.evaluate(X_val, y_val, verbose=0)
        
        results = {
            "model_path": str(model_path),
            "training_samples": len(X_train),
            "validation_samples": len(X_val),
            "num_classes": len(unique_labels),
            "classes": unique_labels,
            "class_distribution": class_dist,
            "final_val_accuracy": float(val_acc),
            "final_val_top3_accuracy": float(val_top3),
            "final_val_loss": float(val_loss)
        }
        
        self._save_training_results("storage_assessment", results)
        
        print(f"✅ Training complete! Validation accuracy: {val_acc:.4f}")
        return results
    
    # ===================================
    # MODEL EVALUATION
    # ===================================
    
    def evaluate_model_performance(self, model_type: str) -> Dict:
        """
        Evaluate trained model against new Supabase data
        
        Args:
            model_type: 'pest', 'disease', or 'storage'
        
        Returns:
            Evaluation metrics
        """
        print(f"📊 Evaluating {model_type} model performance...")
        
        # Load model
        model_pattern = f"{model_type}_detection_*.h5" if model_type != "storage" else f"storage_assessment_*.h5"
        model_files = sorted(self.models_dir.glob(model_pattern))
        
        if not model_files:
            raise FileNotFoundError(f"No trained {model_type} model found")
        
        latest_model = model_files[-1]
        print(f"📂 Loading model: {latest_model}")
        model = tf.keras.models.load_model(latest_model)
        
        # Fetch test data (different from training)
        if model_type == "pest":
            test_data = self.data_service.fetch_pest_training_data()
        elif model_type == "disease":
            test_data = self.data_service.fetch_disease_training_data()
        else:
            test_data = self.data_service.fetch_storage_training_data()
        
        if not test_data["labels"]:
            print("⚠️ No test data available")
            return {}
        
        # Preprocess
        X_test, y_test, labels = self.download_and_preprocess_images(
            test_data["image_urls"],
            test_data["labels"]
        )
        
        # Evaluate
        results = model.evaluate(X_test, y_test, verbose=0)
        
        metrics = {
            "model_path": str(latest_model),
            "test_samples": len(X_test),
            "test_loss": float(results[0]),
            "test_accuracy": float(results[1]),
            "test_top3_accuracy": float(results[2]) if len(results) > 2 else None
        }
        
        print(f"✅ Evaluation complete! Test accuracy: {metrics['test_accuracy']:.4f}")
        return metrics
    
    # ===================================
    # HELPER METHODS
    # ===================================
    
    def _save_training_results(self, model_type: str, results: Dict):
        """Save training results to JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = self.training_logs_dir / f"{model_type}_training_{timestamp}.json"
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"📝 Training results saved to {filepath}")
    
    def get_training_history(self, model_type: str = None) -> List[Dict]:
        """Get training history for a model type"""
        if model_type:
            pattern = f"{model_type}_training_*.json"
        else:
            pattern = "*_training_*.json"
        
        history_files = sorted(self.training_logs_dir.glob(pattern))
        
        history = []
        for file in history_files:
            with open(file, 'r') as f:
                history.append(json.load(f))
        
        return history


# ===================================
# CLI INTERFACE
# ===================================

if __name__ == "__main__":
    import sys
    
    service = ModelTrainingService()
    
    if len(sys.argv) < 2:
        print("Usage: python model_training.py [pest|disease|storage|all]")
        sys.exit(1)
    
    model_type = sys.argv[1].lower()
    
    try:
        if model_type == "pest":
            results = service.train_pest_detection_model()
        elif model_type == "disease":
            results = service.train_disease_detection_model()
        elif model_type == "storage":
            results = service.train_storage_assessment_model()
        elif model_type == "all":
            print("🚀 Training all models...\n")
            pest_results = service.train_pest_detection_model()
            print("\n" + "="*50 + "\n")
            disease_results = service.train_disease_detection_model()
            print("\n" + "="*50 + "\n")
            storage_results = service.train_storage_assessment_model()
            print("\n✅ All models trained successfully!")
        else:
            print(f"❌ Unknown model type: {model_type}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Training failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
