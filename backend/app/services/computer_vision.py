"""
Computer Vision Integration Module
===================================

Integrates AI models for:
1. Custom soil classifier (Kenya soil types)
2. Plant disease/pest detection (TensorFlow Hub PlantVillage)
3. Google Cloud Vision API (fallback for low-confidence cases)
4. Image preprocessing pipeline

Implements confidence thresholds:
- >0.75: Auto-approve
- 0.65-0.75: Proceed with caution
- <0.65: Route to expert

Author: AgroShield AI Team
Date: October 2025
"""

import os
import io
import requests
import json
import numpy as np
from PIL import Image
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime


# ============================================================================
# CONFIGURATION
# ============================================================================

CV_CONFIG = {
    "soil_classifier": {
        "enabled": False,  # Set to True after training custom model
        "model_path": "models/kenya_soil_classifier.h5",
        "confidence_threshold": 0.75
    },
    "plant_disease": {
        "enabled": False,  # Set to True after TF Hub integration
        "tfhub_model_url": "https://tfhub.dev/google/cropnet/classifier/cassava_disease_V1/2",
        "model_path": "models/plant_disease_model",
        "confidence_threshold": 0.75
    },
    "google_cloud_vision": {
        "enabled": False,  # Set to True after obtaining API key
        "api_key": os.getenv("GOOGLE_CLOUD_VISION_API_KEY"),
        "base_url": "https://vision.googleapis.com/v1/images:annotate"
    },
    "image_preprocessing": {
        "target_size": (224, 224),  # Standard for most CV models
        "max_file_size_mb": 5,
        "allowed_formats": ["jpg", "jpeg", "png"],
        "auto_orient": True,
        "enhance_contrast": True
    }
}


# Soil type classes (Kenya)
KENYA_SOIL_TYPES = {
    0: "ferralsols_red",       # Red volcanic soils (Central Highlands)
    1: "nitisols_humic",       # Humic nitisols (Highland areas)
    2: "acrisols_sandy",       # Sandy acrisols (Coastal regions)
    3: "vertisols_black",      # Black cotton soils (Rift Valley)
    4: "luvisols_brown",       # Brown luvisols (Western Kenya)
    5: "arenosols_sandy",      # Sandy arenosols (Arid areas)
}


SOIL_FERTILITY_PROFILES = {
    "ferralsols_red": {
        "fertility_score": 8.5,
        "ph_range": (5.0, 6.5),
        "organic_matter": "high",
        "nitrogen": "medium",
        "phosphorus": "high",
        "potassium": "high",
        "best_crops": ["coffee", "tea", "maize", "beans"]
    },
    "nitisols_humic": {
        "fertility_score": 9.0,
        "ph_range": (5.5, 7.0),
        "organic_matter": "very_high",
        "nitrogen": "high",
        "phosphorus": "high",
        "potassium": "high",
        "best_crops": ["wheat", "barley", "potato", "cabbage"]
    },
    "acrisols_sandy": {
        "fertility_score": 5.5,
        "ph_range": (5.0, 6.0),
        "organic_matter": "low",
        "nitrogen": "low",
        "phosphorus": "medium",
        "potassium": "low",
        "best_crops": ["cassava", "coconut", "cashew"]
    },
    "vertisols_black": {
        "fertility_score": 7.5,
        "ph_range": (7.0, 8.5),
        "organic_matter": "medium",
        "nitrogen": "medium",
        "phosphorus": "medium",
        "potassium": "high",
        "best_crops": ["cotton", "sorghum", "sunflower"]
    },
    "luvisols_brown": {
        "fertility_score": 7.0,
        "ph_range": (6.0, 7.5),
        "organic_matter": "medium",
        "nitrogen": "medium",
        "phosphorus": "medium",
        "potassium": "medium",
        "best_crops": ["maize", "beans", "sugarcane"]
    },
    "arenosols_sandy": {
        "fertility_score": 4.0,
        "ph_range": (6.0, 7.0),
        "organic_matter": "very_low",
        "nitrogen": "very_low",
        "phosphorus": "low",
        "potassium": "low",
        "best_crops": ["millet", "sorghum", "drought_resistant_varieties"]
    }
}


# ============================================================================
# IMAGE PREPROCESSING PIPELINE
# ============================================================================

def preprocess_image(
    image_data: bytes,
    target_size: Tuple[int, int] = (224, 224),
    enhance: bool = True
) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Preprocess image for CV models.
    
    Steps:
    1. Load image from bytes
    2. Auto-orient based on EXIF
    3. Validate format and size
    4. Resize to target size
    5. Enhance contrast (optional)
    6. Normalize pixel values
    7. Assess image quality
    
    Args:
        image_data: Raw image bytes
        target_size: Target dimensions (width, height)
        enhance: Whether to enhance contrast
    
    Returns:
        tuple: (preprocessed_array, quality_metrics)
    """
    try:
        # Load image
        image = Image.open(io.BytesIO(image_data))
        
        # Auto-orient based on EXIF
        if CV_CONFIG["image_preprocessing"]["auto_orient"]:
            image = _auto_orient_image(image)
        
        # Validate format
        if image.format.lower() not in CV_CONFIG["image_preprocessing"]["allowed_formats"]:
            raise ValueError(f"Unsupported format: {image.format}")
        
        # Validate size
        max_size_bytes = CV_CONFIG["image_preprocessing"]["max_file_size_mb"] * 1024 * 1024
        if len(image_data) > max_size_bytes:
            raise ValueError(f"Image too large: {len(image_data) / 1024 / 1024:.1f}MB")
        
        # Assess quality before preprocessing
        quality_metrics = _assess_image_quality(image)
        
        # Convert to RGB if needed
        if image.mode != "RGB":
            image = image.convert("RGB")
        
        # Resize
        image = image.resize(target_size, Image.Resampling.LANCZOS)
        
        # Enhance contrast
        if enhance and CV_CONFIG["image_preprocessing"]["enhance_contrast"]:
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.2)  # 20% contrast boost
        
        # Convert to numpy array
        img_array = np.array(image, dtype=np.float32)
        
        # Normalize to [0, 1]
        img_array = img_array / 255.0
        
        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array, quality_metrics
    
    except Exception as e:
        raise ValueError(f"Image preprocessing failed: {str(e)}")


def _auto_orient_image(image: Image.Image) -> Image.Image:
    """Auto-orient image based on EXIF data."""
    try:
        from PIL import ImageOps
        return ImageOps.exif_transpose(image)
    except:
        return image


def _assess_image_quality(image: Image.Image) -> Dict[str, float]:
    """
    Assess image quality metrics.
    
    Metrics:
    - Brightness (0-1)
    - Sharpness (0-1)
    - Resolution quality (0-1)
    - Overall quality (0-1)
    """
    img_array = np.array(image)
    
    # Brightness (average pixel intensity)
    brightness = np.mean(img_array) / 255.0
    
    # Sharpness (Laplacian variance - edge detection)
    gray = np.mean(img_array, axis=2) if len(img_array.shape) == 3 else img_array
    laplacian_var = _calculate_laplacian_variance(gray)
    sharpness = min(laplacian_var / 1000, 1.0)  # Normalize
    
    # Resolution quality
    width, height = image.size
    min_dimension = min(width, height)
    resolution_quality = min(min_dimension / 500, 1.0)  # 500px = ideal
    
    # Overall quality
    overall = (brightness * 0.3 + sharpness * 0.4 + resolution_quality * 0.3)
    
    return {
        "brightness": round(brightness, 3),
        "sharpness": round(sharpness, 3),
        "resolution_quality": round(resolution_quality, 3),
        "overall_quality": round(overall, 3),
        "width": width,
        "height": height
    }


def _calculate_laplacian_variance(gray_image: np.ndarray) -> float:
    """Calculate Laplacian variance (measure of sharpness)."""
    # Simple Laplacian kernel
    kernel = np.array([[0, 1, 0],
                      [1, -4, 1],
                      [0, 1, 0]])
    
    from scipy import signal
    laplacian = signal.convolve2d(gray_image, kernel, mode='valid')
    return np.var(laplacian)


# ============================================================================
# SOIL CLASSIFICATION
# ============================================================================

def classify_soil_from_image(
    image_data: bytes,
    gps_location: Optional[Tuple[float, float]] = None
) -> Dict[str, Any]:
    """
    Classify soil type from image using custom trained model.
    
    Args:
        image_data: Raw image bytes
        gps_location: Optional (lat, lon) for context
    
    Returns:
        dict: Soil classification with fertility profile
    """
    # Preprocess image
    try:
        img_array, quality_metrics = preprocess_image(image_data)
    except Exception as e:
        return {
            "error": f"Image preprocessing failed: {str(e)}",
            "quality_metrics": None
        }
    
    # Check if custom model is available
    if CV_CONFIG["soil_classifier"]["enabled"]:
        return _classify_with_custom_model(img_array, quality_metrics, gps_location)
    else:
        return _simulate_soil_classification(quality_metrics, gps_location)


def _classify_with_custom_model(
    img_array: np.ndarray,
    quality_metrics: Dict,
    gps_location: Optional[Tuple[float, float]]
) -> Dict[str, Any]:
    """Classify soil using custom TensorFlow model."""
    try:
        import tensorflow as tf
        
        # Load model
        model_path = CV_CONFIG["soil_classifier"]["model_path"]
        model = tf.keras.models.load_model(model_path)
        
        # Make prediction
        predictions = model.predict(img_array, verbose=0)
        
        # Get top prediction
        soil_class = np.argmax(predictions[0])
        confidence = float(predictions[0][soil_class])
        
        soil_type = KENYA_SOIL_TYPES.get(soil_class, "unknown")
        fertility_profile = SOIL_FERTILITY_PROFILES.get(soil_type, {})
        
        # Adjust confidence based on image quality
        adjusted_confidence = confidence * quality_metrics["overall_quality"]
        
        return {
            "soil_type": soil_type,
            "soil_class_id": int(soil_class),
            "confidence": round(confidence, 3),
            "adjusted_confidence": round(adjusted_confidence, 3),
            "confidence_category": _categorize_confidence(adjusted_confidence),
            "fertility_profile": fertility_profile,
            "image_quality": quality_metrics,
            "gps_location": gps_location,
            "model": "custom_kenya_soil_classifier",
            "requires_expert_verification": adjusted_confidence < 0.65
        }
    
    except Exception as e:
        return {
            "error": f"Model inference failed: {str(e)}",
            "fallback": _simulate_soil_classification(quality_metrics, gps_location)
        }


def _simulate_soil_classification(
    quality_metrics: Dict,
    gps_location: Optional[Tuple[float, float]]
) -> Dict[str, Any]:
    """Simulate soil classification when model unavailable."""
    import random
    
    # Use GPS to guess soil type (Kenya regions)
    if gps_location:
        lat, lon = gps_location
        
        # Central Highlands (-1 to 0 lat, 36-37 lon) → Red volcanic
        if -1 <= lat <= 0 and 36 <= lon <= 37:
            soil_type = "ferralsols_red"
        # Rift Valley (-1 to 1 lat, 35-36 lon) → Black cotton
        elif -1 <= lat <= 1 and 35 <= lon <= 36:
            soil_type = "vertisols_black"
        # Coastal (lat < -3, lon > 39) → Sandy
        elif lat < -3 and lon > 39:
            soil_type = "acrisols_sandy"
        else:
            soil_type = random.choice(list(SOIL_FERTILITY_PROFILES.keys()))
    else:
        soil_type = random.choice(list(SOIL_FERTILITY_PROFILES.keys()))
    
    confidence = random.uniform(0.60, 0.80)
    fertility_profile = SOIL_FERTILITY_PROFILES[soil_type]
    
    return {
        "soil_type": soil_type,
        "confidence": round(confidence, 3),
        "confidence_category": _categorize_confidence(confidence),
        "fertility_profile": fertility_profile,
        "image_quality": quality_metrics,
        "gps_location": gps_location,
        "model": "simulated_fallback",
        "requires_expert_verification": confidence < 0.65,
        "note": "Custom soil classifier not configured. Using simulation."
    }


# ============================================================================
# PLANT DISEASE/PEST DETECTION
# ============================================================================

def detect_plant_disease(
    image_data: bytes,
    crop: str,
    fallback_to_google_vision: bool = True
) -> Dict[str, Any]:
    """
    Detect plant disease/pest from leaf image.
    
    Uses TensorFlow Hub PlantVillage model with Google Cloud Vision fallback.
    
    Args:
        image_data: Raw image bytes
        crop: Crop type (for context)
        fallback_to_google_vision: Use Google Vision if confidence low
    
    Returns:
        dict: Disease/pest detection with confidence
    """
    # Preprocess image
    try:
        img_array, quality_metrics = preprocess_image(image_data)
    except Exception as e:
        return {
            "error": f"Image preprocessing failed: {str(e)}",
            "quality_metrics": None
        }
    
    # Check if TF Hub model is available
    if CV_CONFIG["plant_disease"]["enabled"]:
        result = _detect_with_tfhub_model(img_array, quality_metrics, crop)
    else:
        result = _simulate_disease_detection(quality_metrics, crop)
    
    # Fallback to Google Cloud Vision if confidence low
    if (fallback_to_google_vision and 
        CV_CONFIG["google_cloud_vision"]["enabled"] and
        result.get("adjusted_confidence", 1.0) < 0.65):
        
        google_result = _detect_with_google_vision(image_data, crop)
        result["google_vision_fallback"] = google_result
    
    return result


def _detect_with_tfhub_model(
    img_array: np.ndarray,
    quality_metrics: Dict,
    crop: str
) -> Dict[str, Any]:
    """Detect disease using TensorFlow Hub model."""
    try:
        import tensorflow as tf
        import tensorflow_hub as hub
        
        # Load TF Hub model
        model_url = CV_CONFIG["plant_disease"]["tfhub_model_url"]
        model = hub.load(model_url)
        
        # Make prediction
        predictions = model(img_array)
        
        # Parse results (model-specific)
        disease_class = np.argmax(predictions)
        confidence = float(np.max(predictions))
        
        # Map to disease name (model-specific)
        disease_name = _map_disease_class_to_name(disease_class, crop)
        
        # Adjust confidence based on image quality
        adjusted_confidence = confidence * quality_metrics["overall_quality"]
        
        return {
            "disease_id": _disease_name_to_id(disease_name),
            "disease_name": disease_name,
            "crop": crop,
            "confidence": round(confidence, 3),
            "adjusted_confidence": round(adjusted_confidence, 3),
            "confidence_category": _categorize_confidence(adjusted_confidence),
            "image_quality": quality_metrics,
            "model": "tensorflow_hub_plantvil lage",
            "requires_expert_verification": adjusted_confidence < 0.65
        }
    
    except Exception as e:
        return {
            "error": f"TF Hub model inference failed: {str(e)}",
            "fallback": _simulate_disease_detection(quality_metrics, crop)
        }


def _detect_with_google_vision(image_data: bytes, crop: str) -> Dict[str, Any]:
    """Use Google Cloud Vision API as fallback."""
    try:
        api_key = CV_CONFIG["google_cloud_vision"]["api_key"]
        base_url = CV_CONFIG["google_cloud_vision"]["base_url"]
        
        import base64
        image_b64 = base64.b64encode(image_data).decode('utf-8')
        
        request_payload = {
            "requests": [{
                "image": {"content": image_b64},
                "features": [
                    {"type": "LABEL_DETECTION", "maxResults": 5},
                    {"type": "IMAGE_PROPERTIES"}
                ]
            }]
        }
        
        response = requests.post(
            f"{base_url}?key={api_key}",
            json=request_payload,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            labels = data["responses"][0].get("labelAnnotations", [])
            
            # Filter for disease-related labels
            disease_labels = [l for l in labels if any(
                keyword in l["description"].lower() 
                for keyword in ["disease", "pest", "blight", "rust", "mold"]
            )]
            
            if disease_labels:
                top_label = disease_labels[0]
                return {
                    "disease_name": top_label["description"],
                    "confidence": top_label["score"],
                    "source": "google_cloud_vision"
                }
        
        return {"error": "No disease detected by Google Vision"}
    
    except Exception as e:
        return {"error": f"Google Vision API error: {str(e)}"}


def _simulate_disease_detection(quality_metrics: Dict, crop: str) -> Dict[str, Any]:
    """Simulate disease detection when model unavailable."""
    import random
    
    # Common diseases by crop
    crop_diseases = {
        "maize": ["fall_armyworm", "maize_streak_virus", "northern_corn_leaf_blight"],
        "potato": ["late_blight", "early_blight", "potato_virus_y"],
        "tomato": ["late_blight", "early_blight", "tomato_mosaic_virus"],
        "beans": ["bean_rust", "bean_anthracnose", "bean_mosaic_virus"],
        "wheat": ["wheat_rust", "wheat_blight", "powdery_mildew"]
    }
    
    diseases = crop_diseases.get(crop, ["unknown_disease"])
    disease_id = random.choice(diseases)
    confidence = random.uniform(0.60, 0.85)
    
    return {
        "disease_id": disease_id,
        "disease_name": disease_id.replace("_", " ").title(),
        "crop": crop,
        "confidence": round(confidence, 3),
        "confidence_category": _categorize_confidence(confidence),
        "image_quality": quality_metrics,
        "model": "simulated_fallback",
        "requires_expert_verification": confidence < 0.65,
        "note": "Plant disease model not configured. Using simulation."
    }


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def _categorize_confidence(confidence: float) -> str:
    """Categorize confidence level."""
    if confidence >= 0.85:
        return "very_high"
    elif confidence >= 0.75:
        return "high"
    elif confidence >= 0.65:
        return "medium"
    else:
        return "low"


def _map_disease_class_to_name(class_id: int, crop: str) -> str:
    """Map model output class ID to disease name (model-specific)."""
    # Placeholder - replace with actual model class mapping
    disease_map = {
        0: "healthy",
        1: "late_blight",
        2: "early_blight",
        3: "bacterial_spot",
        4: "septoria_leaf_spot"
    }
    return disease_map.get(class_id, "unknown")


def _disease_name_to_id(disease_name: str) -> str:
    """Convert disease name to standardized ID."""
    return disease_name.lower().replace(" ", "_")


# ============================================================================
# SETUP INSTRUCTIONS
# ============================================================================

def print_setup_instructions():
    """Print setup instructions for computer vision APIs."""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║         Computer Vision Integration Setup Instructions        ║
╚═══════════════════════════════════════════════════════════════╝

1. CUSTOM SOIL CLASSIFIER
   -----------------------
   a) Collect 500+ labeled soil images (Kenya soil types)
   b) Train TensorFlow/Keras model:
      - Input: 224x224 RGB images
      - Output: 6 classes (ferralsols, nitisols, acrisols, etc.)
      - Architecture: MobileNetV2 or EfficientNet
   c) Save model: models/kenya_soil_classifier.h5
   d) Enable in config:
      CV_CONFIG["soil_classifier"]["enabled"] = True

2. TENSORFLOW HUB PLANT DISEASE MODEL
   -----------------------
   a) Install: pip install tensorflow tensorflow-hub
   b) Test with PlantVillage model:
      https://tfhub.dev/google/cropnet/classifier/cassava_disease_V1/2
   c) Or train custom model on Kenya crops
   d) Enable in config:
      CV_CONFIG["plant_disease"]["enabled"] = True

3. GOOGLE CLOUD VISION API (FALLBACK)
   -----------------------
   a) Enable Vision API in Google Cloud Console
   b) Create API key
   c) Set environment variable:
      export GOOGLE_CLOUD_VISION_API_KEY=your-api-key
   d) Enable in config:
      CV_CONFIG["google_cloud_vision"]["enabled"] = True

4. IMAGE PREPROCESSING
   -----------------------
   ✓ Already configured
   - Target size: 224x224 (standard for CV models)
   - Max file size: 5MB
   - Formats: JPG, PNG
   - Auto-orient: Enabled
   - Contrast enhancement: Enabled

5. CONFIDENCE THRESHOLDS
   -----------------------
   ✓ Already configured
   - >0.75: Auto-approve (high confidence)
   - 0.65-0.75: Proceed with caution (medium)
   - <0.65: Route to expert (low confidence)

6. TESTING
   -----------------------
   from app.services.computer_vision import (
       classify_soil_from_image,
       detect_plant_disease
   )
   
   # Test soil classification
   with open("soil_sample.jpg", "rb") as f:
       result = classify_soil_from_image(f.read(), gps_location=(-1.29, 36.82))
       print(result)
   
   # Test disease detection
   with open("leaf_sample.jpg", "rb") as f:
       result = detect_plant_disease(f.read(), crop="maize")
       print(result)

═══════════════════════════════════════════════════════════════
Current Status:
  Soil Classifier: {'ENABLED' if CV_CONFIG["soil_classifier"]["enabled"] else 'DISABLED'}
  Plant Disease Model: {'ENABLED' if CV_CONFIG["plant_disease"]["enabled"] else 'DISABLED'}
  Google Cloud Vision: {'ENABLED' if CV_CONFIG["google_cloud_vision"]["enabled"] else 'DISABLED'}
  Image Preprocessing: ENABLED
═══════════════════════════════════════════════════════════════
    """)


# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

__all__ = [
    "classify_soil_from_image",
    "detect_plant_disease",
    "preprocess_image",
    "print_setup_instructions",
    "CV_CONFIG",
    "KENYA_SOIL_TYPES",
    "SOIL_FERTILITY_PROFILES"
]


if __name__ == "__main__":
    print_setup_instructions()
