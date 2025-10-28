"""
ML Model Inference Service
Loads trained models and performs predictions for pest, disease, and soil classification
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import json
import pickle
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from PIL import Image
import requests
from io import BytesIO

# Import central model manager
from app.services.model_manager import get_model_manager

# TensorFlow
try:
    import tensorflow as tf
    from tensorflow import keras
    HAS_TF = True
except ImportError:
    HAS_TF = False
    print("[ML INFERENCE] TensorFlow not installed. Using fallback mode.")

# Scikit-learn
try:
    from sklearn.preprocessing import MinMaxScaler
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False


class ModelInferenceService:
    """Service for loading trained models and making predictions"""
    
    def __init__(self):
        # Use central model manager
        self.model_manager = get_model_manager()
        
        self.base_dir = Path(__file__).parent.parent.parent
        self.models_dir = self.base_dir / "trained_models"
        
        # Legacy support - will be deprecated
        self.models = {}
        self.class_mappings = {}
        self.scalers = {}
        
        print("[ML INFERENCE] ML Inference Service initialized with Model Manager")
    
    def _load_model(self, model_type: str):
        """Load a trained model into memory using Model Manager"""
        # Try to get from Model Manager first
        model = self.model_manager.get_model(model_type)
        
        if model is not None:
            self.models[model_type] = model  # Cache locally for compatibility
            return model
        
        # Fallback to old method if model manager doesn't have it
        print(f"[ML INFERENCE] Model {model_type} not available from Model Manager, using fallback")
        
        # Legacy fallback code...
        model_paths = {
            "pest_detection": self.models_dir / "pest_detection_model.h5",
            "disease_detection": self.models_dir / "disease_detection_model.h5",
            "ai_calendar": self.models_dir / "ai_calendar_model.pkl",
            "soil_diagnostics": self.models_dir / "soil_diagnostics_model.h5",
            "yield_prediction": self.models_dir / "yield_prediction_model.pkl",
            "climate_prediction": self.models_dir / "climate_prediction_model.h5",
        }
        
        model_path = model_paths.get(model_type)
        if not model_path or not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        # Load based on file extension
        if model_path.suffix == '.h5':
            if not HAS_TF:
                raise RuntimeError("TensorFlow required for .h5 models")
            model = keras.models.load_model(str(model_path))
            print(f"[OK] Loaded {model_type} model from {model_path}")
        elif model_path.suffix == '.pkl':
            if not HAS_SKLEARN:
                raise RuntimeError("Scikit-learn required for .pkl models")
            with open(model_path, 'rb') as f:
                data = pickle.load(f)
                model = data['model'] if 'model' in data else data
                if 'encoders' in data:
                    self.scalers[model_type] = data.get('encoders')
            print(f"[OK] Loaded {model_type} model from {model_path}")
        else:
            raise ValueError(f"Unsupported model format: {model_path.suffix}")
        
        self.models[model_type] = model
        return model
    
    def _load_class_mapping(self, model_type: str) -> Dict:
        """Load class mapping for classification models"""
        # Try Model Manager first
        mapping = self.model_manager.get_class_mapping(model_type)
        
        if mapping:
            self.class_mappings[model_type] = mapping
            return mapping
        
        # Fallback to local file
        class_mapping_paths = {
            "pest_detection": self.models_dir / "pest_detection_classes.json",
            "disease_detection": self.models_dir / "disease_detection_classes.json",
            "soil_diagnostics": self.models_dir / "soil_diagnostics_classes.json",
        }
        
        mapping_path = class_mapping_paths.get(model_type)
        if not mapping_path or not mapping_path.exists():
            return {}
        
        with open(mapping_path, 'r') as f:
            mapping = json.load(f)
        
        self.class_mappings[model_type] = mapping
        return mapping
    
    def _preprocess_image(self, image_source, target_size=(224, 224)) -> np.ndarray:
        """Preprocess image for CNN models"""
        # Load image from URL or file path
        if isinstance(image_source, str):
            if image_source.startswith('http'):
                response = requests.get(image_source, timeout=10)
                img = Image.open(BytesIO(response.content))
            else:
                img = Image.open(image_source)
        else:
            img = image_source
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize
        img = img.resize(target_size)
        
        # Convert to array and normalize
        img_array = np.array(img) / 255.0
        
        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
    
    # ========================================================================
    # PEST DETECTION
    # ========================================================================
    
    def predict_pest(self, image_source, top_k: int = 3) -> Dict:
        """
        Predict pest type from image
        
        Args:
            image_source: URL, file path, or PIL Image
            top_k: Number of top predictions to return
        
        Returns:
            {
                "pest_type": "aphids",
                "confidence": 0.92,
                "top_predictions": [
                    {"class": "aphids", "confidence": 0.92},
                    {"class": "whiteflies", "confidence": 0.05},
                    {"class": "healthy", "confidence": 0.02}
                ],
                "model_used": "pest_detection_model"
            }
        """
        try:
            # Load model and classes
            model = self._load_model("pest_detection")
            class_mapping = self._load_class_mapping("pest_detection")
            
            # Preprocess image
            img_array = self._preprocess_image(image_source)
            
            # Predict
            predictions = model.predict(img_array, verbose=0)[0]
            
            # Get top k predictions
            top_indices = np.argsort(predictions)[-top_k:][::-1]
            top_predictions = [
                {
                    "class": class_mapping.get(str(idx), f"class_{idx}"),
                    "confidence": float(predictions[idx])
                }
                for idx in top_indices
            ]
            
            # Primary prediction
            primary_idx = top_indices[0]
            pest_type = class_mapping.get(str(primary_idx), "unknown")
            confidence = float(predictions[primary_idx])
            
            return {
                "pest_type": pest_type,
                "confidence": confidence,
                "top_predictions": top_predictions,
                "model_used": "pest_detection_model",
                "is_healthy": pest_type == "healthy",
                "severity": self._estimate_severity(pest_type, confidence)
            }
        
        except Exception as e:
            print(f"❌ Pest prediction error: {str(e)}")
            # Fallback to simulated prediction
            return self._fallback_pest_prediction()
    
    # ========================================================================
    # DISEASE DETECTION
    # ========================================================================
    
    def predict_disease(self, image_source, top_k: int = 3) -> Dict:
        """
        Predict disease type from plant image
        
        Returns:
            {
                "disease_type": "late_blight",
                "confidence": 0.88,
                "top_predictions": [...],
                "model_used": "disease_detection_model",
                "is_healthy": false,
                "severity": "high"
            }
        """
        try:
            # Load model and classes
            model = self._load_model("disease_detection")
            class_mapping = self._load_class_mapping("disease_detection")
            
            # Preprocess image
            img_array = self._preprocess_image(image_source)
            
            # Predict
            predictions = model.predict(img_array, verbose=0)[0]
            
            # Get top k predictions
            top_indices = np.argsort(predictions)[-top_k:][::-1]
            top_predictions = [
                {
                    "class": class_mapping.get(str(idx), f"class_{idx}"),
                    "confidence": float(predictions[idx])
                }
                for idx in top_indices
            ]
            
            # Primary prediction
            primary_idx = top_indices[0]
            disease_type = class_mapping.get(str(primary_idx), "unknown")
            confidence = float(predictions[primary_idx])
            
            return {
                "disease_type": disease_type,
                "confidence": confidence,
                "top_predictions": top_predictions,
                "model_used": "disease_detection_model",
                "is_healthy": disease_type == "healthy",
                "severity": self._estimate_severity(disease_type, confidence)
            }
        
        except Exception as e:
            print(f"❌ Disease prediction error: {str(e)}")
            return self._fallback_disease_prediction()
    
    # ========================================================================
    # SOIL DIAGNOSTICS
    # ========================================================================
    
    def predict_soil_type(self, image_source, top_k: int = 3) -> Dict:
        """
        Predict soil type from image
        
        Returns:
            {
                "soil_type": "loamy",
                "confidence": 0.85,
                "top_predictions": [...],
                "characteristics": {...},
                "recommendations": [...]
            }
        """
        try:
            # Load model and classes
            model = self._load_model("soil_diagnostics")
            class_mapping = self._load_class_mapping("soil_diagnostics")
            
            # Preprocess image
            img_array = self._preprocess_image(image_source)
            
            # Predict
            predictions = model.predict(img_array, verbose=0)[0]
            
            # Get top k predictions
            top_indices = np.argsort(predictions)[-top_k:][::-1]
            top_predictions = [
                {
                    "class": class_mapping.get(str(idx), f"class_{idx}"),
                    "confidence": float(predictions[idx])
                }
                for idx in top_indices
            ]
            
            # Primary prediction
            primary_idx = top_indices[0]
            soil_type = class_mapping.get(str(primary_idx), "unknown")
            confidence = float(predictions[primary_idx])
            
            # Get soil characteristics
            characteristics = self._get_soil_characteristics(soil_type)
            recommendations = self._get_soil_recommendations(soil_type)
            
            return {
                "soil_type": soil_type,
                "confidence": confidence,
                "top_predictions": top_predictions,
                "model_used": "soil_diagnostics_model",
                "characteristics": characteristics,
                "recommendations": recommendations
            }
        
        except Exception as e:
            print(f"❌ Soil prediction error: {str(e)}")
            return self._fallback_soil_prediction()
    
    # ========================================================================
    # COMBINED ANALYSIS
    # ========================================================================
    
    def analyze_plant_image(self, image_source) -> Dict:
        """
        Run both pest and disease detection on an image
        
        Returns comprehensive analysis with both predictions
        """
        pest_result = self.predict_pest(image_source)
        disease_result = self.predict_disease(image_source)
        
        # Determine primary issue
        if pest_result['confidence'] > disease_result['confidence']:
            primary_issue = "pest"
            primary_diagnosis = pest_result['pest_type']
            primary_confidence = pest_result['confidence']
        else:
            primary_issue = "disease"
            primary_diagnosis = disease_result['disease_type']
            primary_confidence = disease_result['confidence']
        
        is_healthy = pest_result['is_healthy'] and disease_result['is_healthy']
        
        return {
            "primary_issue": primary_issue,
            "primary_diagnosis": primary_diagnosis,
            "primary_confidence": primary_confidence,
            "is_healthy": is_healthy,
            "pest_analysis": pest_result,
            "disease_analysis": disease_result,
            "severity": max(pest_result['severity'], disease_result['severity'], 
                           key=lambda x: ['low', 'medium', 'high', 'critical'].index(x))
        }
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _estimate_severity(self, diagnosis: str, confidence: float) -> str:
        """Estimate severity based on diagnosis and confidence"""
        if diagnosis == "healthy":
            return "none"
        
        if confidence >= 0.9:
            return "high"
        elif confidence >= 0.75:
            return "medium"
        else:
            return "low"
    
    def _get_soil_characteristics(self, soil_type: str) -> Dict:
        """Get characteristics for soil type"""
        characteristics = {
            "sandy": {
                "texture": "Coarse, gritty",
                "drainage": "Excellent",
                "water_retention": "Poor",
                "nutrient_retention": "Low",
                "workability": "Easy"
            },
            "loamy": {
                "texture": "Balanced, crumbly",
                "drainage": "Good",
                "water_retention": "Good",
                "nutrient_retention": "High",
                "workability": "Excellent"
            },
            "clay": {
                "texture": "Fine, smooth",
                "drainage": "Poor",
                "water_retention": "Excellent",
                "nutrient_retention": "High",
                "workability": "Difficult when wet"
            },
            "silty": {
                "texture": "Smooth, slippery",
                "drainage": "Moderate",
                "water_retention": "Good",
                "nutrient_retention": "Moderate",
                "workability": "Moderate"
            },
            "peaty": {
                "texture": "Spongy, organic",
                "drainage": "Variable",
                "water_retention": "Excellent",
                "nutrient_retention": "High",
                "workability": "Easy"
            },
            "chalky": {
                "texture": "Stony, alkaline",
                "drainage": "Good",
                "water_retention": "Poor",
                "nutrient_retention": "Low",
                "workability": "Moderate"
            }
        }
        return characteristics.get(soil_type, {})
    
    def _get_soil_recommendations(self, soil_type: str) -> List[str]:
        """Get recommendations for soil type"""
        recommendations = {
            "sandy": [
                "Add organic matter to improve water retention",
                "Use mulch to reduce evaporation",
                "Apply fertilizers more frequently in smaller amounts",
                "Good for root vegetables like carrots and potatoes"
            ],
            "loamy": [
                "Ideal for most crops - maintain organic matter",
                "Practice crop rotation",
                "Minimal amendments needed",
                "Excellent for vegetables, fruits, and grains"
            ],
            "clay": [
                "Add gypsum or organic matter to improve structure",
                "Avoid working when wet to prevent compaction",
                "Raised beds can improve drainage",
                "Good for water-loving crops like rice"
            ],
            "silty": [
                "Add organic matter for structure",
                "Use cover crops to prevent erosion",
                "Ensure proper drainage",
                "Good for moisture-loving crops"
            ],
            "peaty": [
                "May need pH adjustment (often acidic)",
                "Add sand or compost for structure",
                "Excellent water retention",
                "Good for lettuce, brassicas"
            ],
            "chalky": [
                "Add acidic organic matter",
                "Regular fertilization needed",
                "Mulch to conserve moisture",
                "Choose alkaline-tolerant crops"
            ]
        }
        return recommendations.get(soil_type, [])
    
    def _fallback_pest_prediction(self) -> Dict:
        """Fallback prediction when model not available"""
        import random
        pests = ["aphids", "whiteflies", "armyworms", "thrips", "healthy"]
        pest = random.choice(pests)
        confidence = random.uniform(0.7, 0.95)
        
        return {
            "pest_type": pest,
            "confidence": confidence,
            "top_predictions": [{"class": pest, "confidence": confidence}],
            "model_used": "fallback_simulation",
            "is_healthy": pest == "healthy",
            "severity": "medium" if pest != "healthy" else "none"
        }
    
    def _fallback_disease_prediction(self) -> Dict:
        """Fallback prediction when model not available"""
        import random
        diseases = ["late_blight", "early_blight", "leaf_curl", "rust", "healthy"]
        disease = random.choice(diseases)
        confidence = random.uniform(0.7, 0.95)
        
        return {
            "disease_type": disease,
            "confidence": confidence,
            "top_predictions": [{"class": disease, "confidence": confidence}],
            "model_used": "fallback_simulation",
            "is_healthy": disease == "healthy",
            "severity": "medium" if disease != "healthy" else "none"
        }
    
    def _fallback_soil_prediction(self) -> Dict:
        """Fallback prediction when model not available"""
        import random
        soils = ["sandy", "loamy", "clay", "silty"]
        soil = random.choice(soils)
        confidence = random.uniform(0.7, 0.9)
        
        return {
            "soil_type": soil,
            "confidence": confidence,
            "top_predictions": [{"class": soil, "confidence": confidence}],
            "model_used": "fallback_simulation",
            "characteristics": self._get_soil_characteristics(soil),
            "recommendations": self._get_soil_recommendations(soil)
        }
    
    def check_model_availability(self) -> Dict[str, bool]:
        """Check which models are available"""
        availability = {}
        for model_type, path in self.model_paths.items():
            availability[model_type] = path.exists()
        return availability
    
    def predict_next_farming_practice(
        self, 
        crop: str,
        days_since_planting: int,
        growth_stage: str,
        season: str,
        county: str,
        soil_type: str,
        temperature: float,
        rainfall_mm: float,
        pest_pressure: str = "none",
        disease_occurrence: str = "none"
    ) -> Dict:
        """
        Predict next farming practice with timing and priority
        
        Args:
            crop: Crop name (maize, beans, tomatoes, etc.)
            days_since_planting: Days since planting
            growth_stage: Current growth stage (seedling, vegetative, flowering, fruiting, mature)
            season: Season (long_rains, short_rains, dry_season)
            county: County name
            soil_type: Soil type (sandy, loamy, clay, silty, peaty, chalky)
            temperature: Current temperature in Celsius
            rainfall_mm: Rainfall in mm
            pest_pressure: Pest pressure level (none, low, medium, high)
            disease_occurrence: Disease occurrence level (none, low, medium, high)
        
        Returns:
            Dictionary with next_practice, days_until_practice, priority, confidence
        """
        model_path = self.model_paths["ai_calendar"]
        
        if not model_path.exists():
            print(f"⚠️ AI Calendar model not found at {model_path}, using fallback")
            return self._fallback_calendar_prediction(
                crop, days_since_planting, growth_stage, pest_pressure, disease_occurrence
            )
        
        try:
            # Load model if not cached
            if "ai_calendar" not in self.models:
                with open(model_path, 'rb') as f:
                    model_data = pickle.load(f)
                self.models["ai_calendar"] = model_data
            else:
                model_data = self.models["ai_calendar"]
            
            practice_model = model_data['practice_model']
            timing_model = model_data['timing_model']
            priority_model = model_data['priority_model']
            encoders = model_data['encoders']
            feature_cols = model_data['features']
            
            # Prepare input
            input_data = {
                'crop': crop,
                'days_since_planting': days_since_planting,
                'growth_stage': growth_stage,
                'season': season,
                'county': county,
                'soil_type': soil_type,
                'temperature': temperature,
                'rainfall_mm': rainfall_mm,
                'pest_pressure': pest_pressure,
                'disease_occurrence': disease_occurrence
            }
            
            # Encode categorical features
            encoded_input = []
            for col in feature_cols:
                value = input_data[col]
                if col in encoders and col != 'days_since_planting' and col != 'temperature' and col != 'rainfall_mm':
                    try:
                        encoded_value = encoders[col].transform([value])[0]
                    except ValueError:
                        # Unknown category, use most common
                        encoded_value = 0
                    encoded_input.append(encoded_value)
                else:
                    encoded_input.append(value)
            
            # Make predictions
            X = np.array([encoded_input])
            
            # Predict practice
            practice_pred_encoded = practice_model.predict(X)[0]
            practice_proba = practice_model.predict_proba(X)[0]
            practice_confidence = float(np.max(practice_proba))
            practice = encoders['next_practice'].inverse_transform([practice_pred_encoded])[0]
            
            # Predict timing
            timing_pred = timing_model.predict(X)[0]
            days_until = max(0, int(round(timing_pred)))
            
            # Predict priority
            priority_pred_encoded = priority_model.predict(X)[0]
            priority_proba = priority_model.predict_proba(X)[0]
            priority_confidence = float(np.max(priority_proba))
            priority = encoders['priority'].inverse_transform([priority_pred_encoded])[0]
            
            # Get top 3 alternative practices
            top_3_indices = np.argsort(practice_proba)[-3:][::-1]
            alternative_practices = []
            for idx in top_3_indices:
                alt_practice = encoders['next_practice'].inverse_transform([idx])[0]
                alt_confidence = float(practice_proba[idx])
                alternative_practices.append({
                    "practice": alt_practice,
                    "confidence": alt_confidence
                })
            
            return {
                "next_practice": practice,
                "days_until_practice": days_until,
                "priority": priority,
                "confidence": practice_confidence,
                "priority_confidence": priority_confidence,
                "alternative_practices": alternative_practices,
                "practice_description": self._get_practice_description(practice),
                "model_used": "ai_calendar_random_forest"
            }
        
        except Exception as e:
            print(f"❌ Error in AI calendar prediction: {str(e)}")
            return self._fallback_calendar_prediction(
                crop, days_since_planting, growth_stage, pest_pressure, disease_occurrence
            )
    
    def _fallback_calendar_prediction(
        self, 
        crop: str, 
        days_since_planting: int, 
        growth_stage: str,
        pest_pressure: str,
        disease_occurrence: str
    ) -> Dict:
        """Fallback prediction when model not available"""
        import random
        
        # Emergency practices
        if pest_pressure in ["medium", "high"]:
            return {
                "next_practice": "pest_control",
                "days_until_practice": 0,
                "priority": "high",
                "confidence": 0.95,
                "priority_confidence": 0.95,
                "alternative_practices": [
                    {"practice": "pest_control", "confidence": 0.95},
                    {"practice": "disease_management", "confidence": 0.70},
                    {"practice": "weeding", "confidence": 0.50}
                ],
                "practice_description": self._get_practice_description("pest_control"),
                "model_used": "fallback_simulation"
            }
        
        if disease_occurrence in ["medium", "high"]:
            return {
                "next_practice": "disease_management",
                "days_until_practice": 0,
                "priority": "high",
                "confidence": 0.95,
                "priority_confidence": 0.95,
                "alternative_practices": [
                    {"practice": "disease_management", "confidence": 0.95},
                    {"practice": "pest_control", "confidence": 0.70},
                    {"practice": "fertilizer_application", "confidence": 0.50}
                ],
                "practice_description": self._get_practice_description("disease_management"),
                "model_used": "fallback_simulation"
            }
        
        # Stage-based recommendations
        if growth_stage == "seedling":
            practice = "weeding"
            days = random.randint(3, 7)
            priority = "medium"
        elif growth_stage == "vegetative":
            practice = "fertilizer_application"
            days = random.randint(5, 10)
            priority = "high"
        elif growth_stage == "flowering":
            practice = "irrigation"
            days = random.randint(1, 3)
            priority = "high"
        elif growth_stage == "fruiting":
            practice = "pest_control"
            days = random.randint(7, 14)
            priority = "medium"
        elif growth_stage == "mature":
            practice = "harvesting"
            days = random.randint(0, 3)
            priority = "high"
        else:
            practice = "irrigation"
            days = random.randint(3, 7)
            priority = "medium"
        
        confidence = random.uniform(0.75, 0.9)
        
        return {
            "next_practice": practice,
            "days_until_practice": days,
            "priority": priority,
            "confidence": confidence,
            "priority_confidence": confidence,
            "alternative_practices": [
                {"practice": practice, "confidence": confidence},
                {"practice": "irrigation", "confidence": confidence - 0.15},
                {"practice": "weeding", "confidence": confidence - 0.25}
            ],
            "practice_description": self._get_practice_description(practice),
            "model_used": "fallback_simulation"
        }
    
    def _get_practice_description(self, practice: str) -> str:
        """Get description for farming practice"""
        descriptions = {
            "land_preparation": "Prepare the land by plowing, harrowing, and leveling the soil for optimal planting conditions.",
            "planting": "Plant seeds or seedlings at the appropriate depth and spacing for optimal growth.",
            "fertilizer_application": "Apply fertilizers to provide essential nutrients for plant growth and development.",
            "weeding": "Remove unwanted weeds that compete with crops for nutrients, water, and sunlight.",
            "pest_control": "Apply pest control measures to protect crops from harmful insects and pests.",
            "disease_management": "Implement disease management practices including fungicides and resistant varieties.",
            "irrigation": "Water crops to maintain optimal soil moisture levels for plant growth.",
            "harvesting": "Harvest mature crops at the right time to ensure maximum yield and quality.",
            "post_harvest_handling": "Properly handle, dry, and store harvested crops to minimize post-harvest losses.",
            "soil_testing": "Test soil to determine nutrient levels and pH for informed fertilization decisions."
        }
        return descriptions.get(practice, "Perform scheduled farming practice.")

