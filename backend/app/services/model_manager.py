"""
Unified ML Model Manager
Central service for loading and managing all trained AI models
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional, Any
import json

# Singleton instance
_model_manager_instance = None


class MLModelManager:
    """
    Central manager for all trained ML models.
    Ensures models are loaded once and shared across the application.
    """
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.models_dir = self.base_dir / "trained_models"
        self.data_dir = self.base_dir / "training_data"
        self.public_data_dir = self.base_dir / "training_data_public"
        
        # Model registry
        self.models = {}
        self.metadata = {}
        
        # Model paths configuration
        self.model_config = {
            "pest_detection": {
                "path": self.models_dir / "pest_detection_mobilenet_v3.h5",
                "alt_path": self.models_dir / "pest_detection_model.h5",
                "type": "tensorflow",
                "classes_file": self.models_dir / "pest_detection_classes.json",
                "input_shape": (224, 224, 3),
                "description": "Identifies 7 common agricultural pests"
            },
            "disease_detection": {
                "path": self.models_dir / "disease_detection_efficientnet.h5",
                "alt_path": self.models_dir / "disease_detection_model.h5",
                "type": "tensorflow",
                "classes_file": self.models_dir / "disease_detection_classes.json",
                "input_shape": (224, 224, 3),
                "description": "Detects 38 plant disease classes"
            },
            "soil_diagnostics": {
                "path": self.models_dir / "soil_diagnostics_custom_cnn.h5",
                "alt_path": self.models_dir / "soil_diagnostics_model.h5",
                "type": "tensorflow",
                "classes_file": self.models_dir / "soil_diagnostics_classes.json",
                "input_shape": (224, 224, 3),
                "description": "Classifies 6 Kenyan soil types"
            },
            "yield_prediction": {
                "path": self.models_dir / "yield_prediction_rf.pkl",
                "alt_path": self.models_dir / "yield_prediction_model.pkl",
                "type": "sklearn",
                "description": "Predicts crop yields based on conditions"
            },
            "climate_prediction": {
                "path": self.models_dir / "climate_prediction_lstm.h5",
                "alt_path": self.models_dir / "climate_prediction_model.h5",
                "type": "tensorflow",
                "input_shape": (30, 10),  # 30 timesteps, 10 features
                "description": "Forecasts weather patterns"
            },
            "storage_assessment": {
                "path": self.models_dir / "storage_assessment_cnn.h5",
                "alt_path": self.models_dir / "storage_assessment_model.h5",
                "type": "tensorflow",
                "classes_file": self.models_dir / "storage_assessment_classes.json",
                "input_shape": (224, 224, 3),
                "description": "Evaluates crop storage conditions"
            },
            "plant_health": {
                "path": self.models_dir / "plant_health_mobilenet.h5",
                "alt_path": self.models_dir / "plant_health_model.h5",
                "type": "tensorflow",
                "classes_file": self.models_dir / "plant_health_classes.json",
                "input_shape": (224, 224, 3),
                "description": "Overall plant health monitoring"
            },
            "ai_calendar": {
                "path": self.models_dir / "ai_calendar_model.pkl",
                "type": "sklearn",
                "description": "Smart farming calendar recommendations"
            }
        }
        
        # Initialize
        self._check_models_directory()
        self._scan_available_models()
    
    def _check_models_directory(self):
        """Ensure models directory exists"""
        if not self.models_dir.exists():
            self.models_dir.mkdir(parents=True, exist_ok=True)
            print(f"[MODEL MANAGER] Created models directory: {self.models_dir}")
    
    def _scan_available_models(self):
        """Scan for available trained models"""
        available = {}
        
        for model_name, config in self.model_config.items():
            primary_path = config["path"]
            alt_path = config.get("alt_path")
            
            if primary_path.exists():
                available[model_name] = str(primary_path)
            elif alt_path and alt_path.exists():
                available[model_name] = str(alt_path)
                # Update config to use alt path
                config["path"] = alt_path
        
        self.metadata["available_models"] = available
        self.metadata["total_available"] = len(available)
        self.metadata["total_configured"] = len(self.model_config)
        
        if available:
            print(f"[MODEL MANAGER] Found {len(available)}/{len(self.model_config)} models:")
            for name in available:
                print(f"   - {name}")
        else:
            print("[MODEL MANAGER] No trained models found. Run training first:")
            print("   python master_train_models.py --train-all")
    
    def get_model(self, model_name: str) -> Optional[Any]:
        """
        Get a loaded model by name.
        Models are lazy-loaded on first request.
        
        Args:
            model_name: Name of the model (e.g., 'pest_detection')
        
        Returns:
            Loaded model object or None if not available
        """
        # Check if already loaded
        if model_name in self.models:
            return self.models[model_name]
        
        # Check if model exists
        if model_name not in self.model_config:
            print(f"[MODEL MANAGER] Unknown model: {model_name}")
            return None
        
        config = self.model_config[model_name]
        model_path = config["path"]
        
        if not model_path.exists():
            print(f"[MODEL MANAGER] Model not found: {model_path}")
            return None
        
        # Load model based on type
        try:
            if config["type"] == "tensorflow":
                import tensorflow as tf
                from tensorflow import keras
                model = keras.models.load_model(str(model_path))
                print(f"[MODEL MANAGER] Loaded TensorFlow model: {model_name}")
            
            elif config["type"] == "sklearn":
                import pickle
                with open(model_path, 'rb') as f:
                    data = pickle.load(f)
                    model = data.get('model', data)  # Handle both formats
                print(f"[MODEL MANAGER] Loaded sklearn model: {model_name}")
            
            else:
                print(f"[MODEL MANAGER] Unsupported model type: {config['type']}")
                return None
            
            # Cache the model
            self.models[model_name] = model
            return model
        
        except Exception as e:
            print(f"[MODEL MANAGER] Error loading {model_name}: {str(e)}")
            return None
    
    def get_model_config(self, model_name: str) -> Optional[Dict]:
        """Get configuration for a specific model"""
        return self.model_config.get(model_name)
    
    def get_class_mapping(self, model_name: str) -> Dict:
        """Get class labels for classification models"""
        config = self.model_config.get(model_name)
        if not config:
            return {}
        
        classes_file = config.get("classes_file")
        if not classes_file or not classes_file.exists():
            return {}
        
        try:
            with open(classes_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"[MODEL MANAGER] Error loading classes for {model_name}: {str(e)}")
            return {}
    
    def list_available_models(self) -> Dict:
        """List all available models with their status"""
        result = {}
        
        for model_name, config in self.model_config.items():
            model_path = config["path"]
            alt_path = config.get("alt_path")
            
            is_available = model_path.exists() or (alt_path and alt_path.exists())
            is_loaded = model_name in self.models
            
            result[model_name] = {
                "available": is_available,
                "loaded": is_loaded,
                "type": config["type"],
                "description": config["description"],
                "path": str(model_path) if model_path.exists() else (str(alt_path) if alt_path and alt_path.exists() else None)
            }
        
        return result
    
    def get_training_data_info(self) -> Dict:
        """Get information about available training datasets"""
        info = {
            "synthetic_data": {},
            "public_data": {},
            "total_datasets": 0
        }
        
        # Check synthetic data
        if self.data_dir.exists():
            synthetic_dirs = [d for d in self.data_dir.iterdir() if d.is_dir()]
            for data_dir in synthetic_dirs:
                metadata_file = data_dir / "metadata.json"
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                        info["synthetic_data"][data_dir.name] = {
                            "samples": len(metadata) if isinstance(metadata, list) else metadata.get("records", 0),
                            "path": str(data_dir)
                        }
                    except:
                        pass
        
        # Check public API data
        if self.public_data_dir.exists():
            public_dirs = [d for d in self.public_data_dir.iterdir() if d.is_dir()]
            for data_dir in public_dirs:
                # Count files or check metadata
                file_count = len(list(data_dir.rglob("*.jpg"))) + len(list(data_dir.rglob("*.png"))) + len(list(data_dir.rglob("*.csv")))
                if file_count > 0:
                    info["public_data"][data_dir.name] = {
                        "files": file_count,
                        "path": str(data_dir)
                    }
        
        info["total_datasets"] = len(info["synthetic_data"]) + len(info["public_data"])
        
        return info
    
    def get_system_status(self) -> Dict:
        """Get complete system status"""
        return {
            "models": self.list_available_models(),
            "training_data": self.get_training_data_info(),
            "paths": {
                "models_dir": str(self.models_dir),
                "data_dir": str(self.data_dir),
                "public_data_dir": str(self.public_data_dir)
            },
            "summary": {
                "total_models_configured": len(self.model_config),
                "total_models_available": self.metadata.get("total_available", 0),
                "total_models_loaded": len(self.models)
            }
        }
    
    def unload_model(self, model_name: str):
        """Unload a model from memory"""
        if model_name in self.models:
            del self.models[model_name]
            print(f"[MODEL MANAGER] Unloaded model: {model_name}")
    
    def unload_all_models(self):
        """Unload all models from memory"""
        self.models.clear()
        print("[MODEL MANAGER] All models unloaded")


def get_model_manager() -> MLModelManager:
    """Get the singleton MLModelManager instance"""
    global _model_manager_instance
    
    if _model_manager_instance is None:
        _model_manager_instance = MLModelManager()
    
    return _model_manager_instance


# Convenience functions
def get_model(model_name: str):
    """Convenience function to get a model"""
    return get_model_manager().get_model(model_name)


def list_models():
    """Convenience function to list available models"""
    return get_model_manager().list_available_models()


def get_system_status():
    """Convenience function to get system status"""
    return get_model_manager().get_system_status()
