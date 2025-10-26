"""
TensorFlow Model Integration System
====================================

Integrates TensorFlow models with real-world APIs for Predictive, Context-Aware Agriculture (PCA).

Models:
1. Plant Health & Disease Detection (TensorFlow Lite on-device)
2. Soil & Nutrient Diagnostics (Computer Vision + Regression)
3. Climate & Disaster Prediction (LSTM Time-Series)
4. Spoilage Prediction (Classification + Time-Series)

Real-World Integrations:
- Disease Database APIs (CGIAR, KEPHIS)
- Meteorological APIs (OpenWeatherMap)
- Geological/Soil APIs (FAO Soil Maps)
- BLE Sensor Data Streams
- Hugging Face NLP for SMS generation

Author: AgroShield AI Team
Date: October 2025
"""

import os
import json
import requests
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
import base64


# ============================================================================
# CONFIGURATION
# ============================================================================

TENSORFLOW_CONFIG = {
    "models": {
        "plant_health": {
            "tflite_path": "models/plant_health_mobilenet_v3.tflite",
            "model_type": "classification",
            "input_shape": (224, 224, 3),
            "confidence_threshold": 0.75,
            "edge_deployment": True  # Run on device
        },
        "soil_diagnostics": {
            "tflite_path": "models/soil_diagnostics_efficientnet_b0.tflite",
            "model_type": "regression",
            "input_shape": (224, 224, 3),
            "confidence_threshold": 0.70,
            "edge_deployment": True
        },
        "climate_prediction": {
            "model_path": "models/climate_lstm_model.h5",
            "model_type": "time_series",
            "lookback_days": 30,
            "forecast_days": 7,
            "edge_deployment": False  # Cloud processing
        },
        "spoilage_prediction": {
            "model_path": "models/spoilage_classification_model.h5",
            "model_type": "classification_time_series",
            "confidence_threshold": 0.65,
            "edge_deployment": False
        }
    },
    "apis": {
        "disease_database": {
            "enabled": False,
            "providers": {
                "cgiar": {
                    "base_url": "https://api.cgiar.org/plant-health/v1",
                    "api_key": os.getenv("CGIAR_API_KEY")
                },
                "kephis": {
                    "base_url": "https://api.kephis.go.ke/diseases/v1",
                    "api_key": os.getenv("KEPHIS_API_KEY")
                }
            }
        },
        "meteorological": {
            "enabled": False,
            "providers": {
                "openweathermap": {
                    "base_url": "https://api.openweathermap.org/data/2.5",
                    "api_key": os.getenv("OPENWEATHER_API_KEY")
                },
                "accuweather": {
                    "base_url": "https://api.accuweather.com",
                    "api_key": os.getenv("ACCUWEATHER_API_KEY")
                }
            }
        },
        "soil_geological": {
            "enabled": False,
            "providers": {
                "fao_soilgrids": {
                    "base_url": "https://rest.isric.org/soilgrids/v2.0",
                    "api_key": None  # Free API
                }
            }
        },
        "huggingface": {
            "enabled": False,
            "api_key": os.getenv("HUGGINGFACE_API_KEY"),
            "model": "facebook/mbart-large-50-many-to-many-mmt",  # Multilingual translation
            "base_url": "https://api-inference.huggingface.co/models"
        }
    },
    "edge_deployment": {
        "tflite_delegate": "gpu",  # gpu, nnapi, or cpu
        "num_threads": 4,
        "offline_mode": True  # Cache models for offline use
    }
}


class DiagnosisSeverity(Enum):
    """Disease severity levels."""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"


# ============================================================================
# A. PLANT HEALTH & DISEASE DETECTION (TensorFlow Lite)
# ============================================================================

def diagnose_plant_health_tflite(
    image_data: bytes,
    crop: str,
    lat: float,
    lon: float,
    use_context: bool = True
) -> Dict[str, Any]:
    """
    Diagnose plant health using TensorFlow Lite on-device model.
    
    Edge Computing: Runs locally on smartphone for instant, offline diagnosis.
    
    Args:
        image_data: Raw image bytes from camera
        crop: Crop type (maize, potato, coffee, etc.)
        lat: GPS latitude
        lon: GPS longitude
        use_context: Whether to enhance with real-world API context
    
    Returns:
        dict: Comprehensive diagnosis with context-aware action plan
    """
    # Step 1: Run TFLite model on-device (instant, offline)
    diagnosis = _run_tflite_inference(
        image_data,
        model_path=TENSORFLOW_CONFIG["models"]["plant_health"]["tflite_path"],
        model_type="classification"
    )
    
    # Step 2: Enhance with real-world context if online
    if use_context and diagnosis["confidence"] >= 0.75:
        diagnosis = _enhance_diagnosis_with_context(
            diagnosis=diagnosis,
            crop=crop,
            lat=lat,
            lon=lon
        )
    
    # Step 3: Generate actionable SMS/notification
    diagnosis["sms_message"] = _generate_farmer_sms(
        diagnosis=diagnosis,
        language="swahili"
    )
    
    return diagnosis


def _run_tflite_inference(
    image_data: bytes,
    model_path: str,
    model_type: str
) -> Dict[str, Any]:
    """
    Run TensorFlow Lite inference on-device.
    
    This is a placeholder - actual implementation requires TensorFlow Lite runtime.
    """
    try:
        # In production, use TensorFlow Lite Interpreter
        # import tensorflow as tf
        # interpreter = tf.lite.Interpreter(model_path=model_path)
        # interpreter.allocate_tensors()
        
        # For now, simulate inference
        return _simulate_tflite_inference(image_data, model_type)
    
    except Exception as e:
        return {
            "error": f"TFLite inference failed: {str(e)}",
            "fallback": "cloud_processing_required"
        }


def _simulate_tflite_inference(image_data: bytes, model_type: str) -> Dict[str, Any]:
    """Simulate TFLite inference for development."""
    import random
    
    # Simulate disease classification
    diseases = [
        {"id": "maize_blight", "name": "Maize Leaf Blight", "severity": DiagnosisSeverity.SEVERE},
        {"id": "late_blight", "name": "Late Blight", "severity": DiagnosisSeverity.CRITICAL},
        {"id": "fall_armyworm", "name": "Fall Armyworm", "severity": DiagnosisSeverity.MODERATE},
        {"id": "healthy", "name": "Healthy Plant", "severity": DiagnosisSeverity.MILD}
    ]
    
    disease = random.choice(diseases)
    confidence = random.uniform(0.75, 0.98)
    
    return {
        "disease_id": disease["id"],
        "disease_name": disease["name"],
        "severity": disease["severity"].value,
        "confidence": round(confidence, 3),
        "model": "tflite_mobilenet_v3",
        "inference_time_ms": random.randint(50, 150),
        "edge_computed": True
    }


def _enhance_diagnosis_with_context(
    diagnosis: Dict,
    crop: str,
    lat: float,
    lon: float
) -> Dict[str, Any]:
    """
    Enhance diagnosis with real-world API context.
    
    Integrations:
    1. Disease Database API - Latest treatments
    2. Meteorological API - Weather conditions
    3. Contagion Risk Model - Outbreak tracking
    """
    # Get latest treatment recommendations
    treatments = _get_disease_treatments_api(diagnosis["disease_id"], crop)
    
    # Get weather context
    weather = _get_weather_context_api(lat, lon)
    
    # Calculate contagion risk
    contagion_risk = _calculate_contagion_risk(
        disease_id=diagnosis["disease_id"],
        lat=lat,
        lon=lon
    )
    
    # Generate context-aware action plan
    action_plan = _generate_contextual_action_plan(
        diagnosis=diagnosis,
        treatments=treatments,
        weather=weather,
        contagion_risk=contagion_risk
    )
    
    diagnosis.update({
        "treatments": treatments,
        "weather_context": weather,
        "contagion_risk": contagion_risk,
        "action_plan": action_plan,
        "context_enhanced": True
    })
    
    return diagnosis


def _get_disease_treatments_api(disease_id: str, crop: str) -> List[Dict[str, Any]]:
    """
    Query disease database APIs for latest treatments.
    
    APIs: CGIAR, KEPHIS, or curated NGO database
    """
    if not TENSORFLOW_CONFIG["apis"]["disease_database"]["enabled"]:
        return _get_fallback_treatments(disease_id, crop)
    
    try:
        # Try CGIAR API first
        cgiar_config = TENSORFLOW_CONFIG["apis"]["disease_database"]["providers"]["cgiar"]
        
        response = requests.get(
            f"{cgiar_config['base_url']}/treatments",
            params={
                "disease_id": disease_id,
                "crop": crop,
                "country": "kenya"
            },
            headers={"Authorization": f"Bearer {cgiar_config['api_key']}"},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            return _parse_treatment_data(data)
        
        # Fallback to KEPHIS
        kephis_config = TENSORFLOW_CONFIG["apis"]["disease_database"]["providers"]["kephis"]
        
        response = requests.get(
            f"{kephis_config['base_url']}/registered-treatments",
            params={"disease": disease_id, "crop": crop},
            headers={"X-API-Key": kephis_config['api_key']},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            return _parse_treatment_data(data)
    
    except Exception as e:
        print(f"Disease database API error: {str(e)}")
    
    return _get_fallback_treatments(disease_id, crop)


def _get_fallback_treatments(disease_id: str, crop: str) -> List[Dict[str, Any]]:
    """Fallback treatments when API unavailable."""
    treatment_db = {
        "maize_blight": [
            {
                "name": "Neem Oil Spray",
                "type": "organic",
                "application": "Spray leaves thoroughly, repeat every 7 days",
                "timing": "Apply early morning or late evening",
                "cost_ksh": 350,
                "effectiveness": 0.75
            },
            {
                "name": "Copper-based fungicide",
                "type": "chemical",
                "application": "Mix 30g per 20L water, spray every 10-14 days",
                "timing": "Apply before rain forecast",
                "cost_ksh": 800,
                "effectiveness": 0.90
            }
        ],
        "late_blight": [
            {
                "name": "Mancozeb 80WP",
                "type": "chemical",
                "application": "50g per 20L water, spray every 7 days",
                "timing": "Critical: Apply within 24 hours of detection",
                "cost_ksh": 600,
                "effectiveness": 0.85
            },
            {
                "name": "Bordeaux mixture",
                "type": "organic",
                "application": "Mix fresh, spray every 5 days",
                "timing": "Apply preventatively before rain",
                "cost_ksh": 400,
                "effectiveness": 0.70
            }
        ],
        "fall_armyworm": [
            {
                "name": "Neem-based biopesticide",
                "type": "organic",
                "application": "Apply to whorl, repeat every 3 days",
                "timing": "Early morning application",
                "cost_ksh": 450,
                "effectiveness": 0.65
            },
            {
                "name": "Lambda-cyhalothrin",
                "type": "chemical",
                "application": "10ml per 20L water, target larvae directly",
                "timing": "Apply when larvae are small",
                "cost_ksh": 1200,
                "effectiveness": 0.92
            }
        ]
    }
    
    return treatment_db.get(disease_id, [])


def _parse_treatment_data(api_response: Dict) -> List[Dict[str, Any]]:
    """Parse treatment data from API response."""
    treatments = []
    
    for item in api_response.get("treatments", []):
        treatments.append({
            "name": item.get("product_name"),
            "type": item.get("treatment_type"),
            "application": item.get("application_method"),
            "timing": item.get("timing_guidance"),
            "cost_ksh": item.get("retail_price_ksh"),
            "effectiveness": item.get("efficacy_rating", 0.75),
            "registration_number": item.get("registration_id"),
            "supplier": item.get("approved_supplier")
        })
    
    return treatments


def _get_weather_context_api(lat: float, lon: float) -> Dict[str, Any]:
    """
    Get weather context from meteorological API.
    
    APIs: OpenWeatherMap, AccuWeather, or national weather service
    """
    if not TENSORFLOW_CONFIG["apis"]["meteorological"]["enabled"]:
        return _get_fallback_weather(lat, lon)
    
    try:
        # Try OpenWeatherMap API
        owm_config = TENSORFLOW_CONFIG["apis"]["meteorological"]["providers"]["openweathermap"]
        
        response = requests.get(
            f"{owm_config['base_url']}/forecast",
            params={
                "lat": lat,
                "lon": lon,
                "appid": owm_config['api_key'],
                "units": "metric",
                "cnt": 8  # Next 24 hours (3-hour intervals)
            },
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            return _parse_weather_data(data)
    
    except Exception as e:
        print(f"Weather API error: {str(e)}")
    
    return _get_fallback_weather(lat, lon)


def _get_fallback_weather(lat: float, lon: float) -> Dict[str, Any]:
    """Fallback weather when API unavailable."""
    import random
    
    # Simulate weather data based on Kenya climate
    return {
        "current_temp_c": round(random.uniform(20, 30), 1),
        "rainfall_next_24h_mm": round(random.uniform(0, 25), 1),
        "rainfall_probability": round(random.uniform(0, 100), 0),
        "rain_warning": random.choice([True, False]),
        "wind_speed_kmh": round(random.uniform(5, 20), 1),
        "conditions": random.choice(["clear", "partly_cloudy", "rain_expected"]),
        "source": "simulated"
    }


def _parse_weather_data(api_response: Dict) -> Dict[str, Any]:
    """Parse weather data from API."""
    forecast_list = api_response.get("list", [])
    
    if not forecast_list:
        return {}
    
    # Sum rainfall for next 24 hours
    total_rain = sum(item.get("rain", {}).get("3h", 0) for item in forecast_list)
    
    # Check for rain probability
    rain_prob = max(item.get("pop", 0) * 100 for item in forecast_list)
    
    current = forecast_list[0]
    
    return {
        "current_temp_c": current["main"]["temp"],
        "rainfall_next_24h_mm": round(total_rain, 1),
        "rainfall_probability": round(rain_prob, 0),
        "rain_warning": rain_prob > 70,
        "wind_speed_kmh": round(current["wind"]["speed"] * 3.6, 1),
        "conditions": current["weather"][0]["main"].lower(),
        "source": "openweathermap"
    }


def _calculate_contagion_risk(disease_id: str, lat: float, lon: float) -> Dict[str, Any]:
    """
    Calculate contagion risk using spatial-temporal AI model.
    
    Tracks disease spread patterns and generates dynamic alert boundaries.
    """
    # Query recent disease reports in area
    recent_reports = _get_nearby_disease_reports(disease_id, lat, lon, radius_km=50)
    
    if len(recent_reports) < 3:
        return {
            "risk_level": "low",
            "nearby_cases": len(recent_reports),
            "alert_radius_km": 5,
            "spread_rate": 0
        }
    
    # Calculate spatial clustering
    cluster_density = len(recent_reports) / 50  # cases per km²
    
    # Calculate temporal spread rate
    if len(recent_reports) >= 2:
        dates = sorted([r["reported_date"] for r in recent_reports])
        days_elapsed = (datetime.fromisoformat(dates[-1]) - datetime.fromisoformat(dates[0])).days
        spread_rate = len(recent_reports) / max(days_elapsed, 1)
    else:
        spread_rate = 0
    
    # Determine risk level and alert radius
    if cluster_density > 0.5 and spread_rate > 0.5:
        risk_level = "critical"
        alert_radius = 15
    elif cluster_density > 0.3 or spread_rate > 0.3:
        risk_level = "high"
        alert_radius = 10
    elif cluster_density > 0.1 or spread_rate > 0.1:
        risk_level = "moderate"
        alert_radius = 7
    else:
        risk_level = "low"
        alert_radius = 5
    
    return {
        "risk_level": risk_level,
        "nearby_cases": len(recent_reports),
        "cluster_density": round(cluster_density, 3),
        "spread_rate_cases_per_day": round(spread_rate, 2),
        "alert_radius_km": alert_radius,
        "outbreak_detected": risk_level in ["high", "critical"]
    }


def _get_nearby_disease_reports(
    disease_id: str,
    lat: float,
    lon: float,
    radius_km: float
) -> List[Dict[str, Any]]:
    """Get recent disease reports from database."""
    # Simulate querying database
    # In production, query actual disease report database
    import random
    
    num_reports = random.randint(0, 10)
    
    return [
        {
            "report_id": f"report_{i}",
            "disease_id": disease_id,
            "lat": lat + random.uniform(-0.5, 0.5),
            "lon": lon + random.uniform(-0.5, 0.5),
            "reported_date": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
            "severity": random.choice(["mild", "moderate", "severe"])
        }
        for i in range(num_reports)
    ]


def _generate_contextual_action_plan(
    diagnosis: Dict,
    treatments: List[Dict],
    weather: Dict,
    contagion_risk: Dict
) -> Dict[str, Any]:
    """
    Generate context-aware action plan using rules-based engine.
    
    Combines AI diagnosis with real-world context for actionable guidance.
    """
    # Select best treatment based on context
    organic_treatments = [t for t in treatments if t["type"] == "organic"]
    chemical_treatments = [t for t in treatments if t["type"] == "chemical"]
    
    # Priority selection logic
    if diagnosis["severity"] in ["critical", "severe"]:
        # Severe cases: recommend most effective (usually chemical)
        if chemical_treatments:
            recommended = max(chemical_treatments, key=lambda t: t["effectiveness"])
        else:
            recommended = max(treatments, key=lambda t: t["effectiveness"])
    else:
        # Mild/moderate: prefer organic if effective enough
        if organic_treatments and any(t["effectiveness"] >= 0.70 for t in organic_treatments):
            recommended = max(organic_treatments, key=lambda t: t["effectiveness"])
        else:
            recommended = max(treatments, key=lambda t: t["effectiveness"])
    
    # Timing guidance based on weather
    if weather.get("rain_warning"):
        timing_warning = f"⚠️ CRITICAL: Heavy rain forecast ({weather['rainfall_next_24h_mm']}mm). Apply treatment BEFORE 10 AM to prevent wash-off."
        urgency = "immediate"
    else:
        timing_warning = f"Apply {recommended['timing']}"
        urgency = "standard"
    
    # Contagion-specific guidance
    if contagion_risk["outbreak_detected"]:
        contagion_warning = f"🚨 OUTBREAK ALERT: {contagion_risk['nearby_cases']} cases detected within {contagion_risk['alert_radius_km']}km. Monitor daily."
    else:
        contagion_warning = "No major outbreak detected in your area."
    
    return {
        "recommended_treatment": recommended,
        "timing_guidance": timing_warning,
        "urgency": urgency,
        "contagion_warning": contagion_warning,
        "estimated_cost_ksh": recommended["cost_ksh"],
        "follow_up_days": 7 if diagnosis["severity"] in ["severe", "critical"] else 14
    }


# ============================================================================
# SMS GENERATION WITH HUGGING FACE NLP
# ============================================================================

def _generate_farmer_sms(diagnosis: Dict, language: str = "swahili") -> str:
    """
    Generate farmer-friendly SMS using Hugging Face NLP.
    
    Translates complex diagnostic output into clear, actionable messages.
    """
    if not TENSORFLOW_CONFIG["apis"]["huggingface"]["enabled"]:
        return _generate_simple_sms(diagnosis, language)
    
    # Prepare context for NLP model
    context = _prepare_sms_context(diagnosis)
    
    # Generate text using Hugging Face API
    try:
        translated_message = _call_huggingface_api(context, language)
        return translated_message
    except:
        return _generate_simple_sms(diagnosis, language)


def _generate_simple_sms(diagnosis: Dict, language: str) -> str:
    """Generate simple SMS without NLP API."""
    disease_name = diagnosis.get("disease_name", "Unknown disease")
    severity = diagnosis.get("severity", "moderate")
    
    if language == "swahili":
        severity_sw = {
            "mild": "Nyepesi",
            "moderate": "Wastani",
            "severe": "Mbaya",
            "critical": "Hatari sana"
        }
        
        base_message = f"🌾 AGRO: Ugonjwa wa {disease_name} umegunduliwa ({severity_sw[severity]}). "
        
        if "action_plan" in diagnosis:
            treatment = diagnosis["action_plan"]["recommended_treatment"]["name"]
            base_message += f"Tumia {treatment}. "
            
            if diagnosis["action_plan"]["urgency"] == "immediate":
                base_message += "HARAKA! "
            
            if "weather_context" in diagnosis and diagnosis["weather_context"].get("rain_warning"):
                base_message += "Mvua inakuja - tumia kabla ya saa 10 asubuhi. "
        
        return base_message
    
    else:  # English
        base_message = f"🌾 AGRO: {disease_name} detected ({severity}). "
        
        if "action_plan" in diagnosis:
            treatment = diagnosis["action_plan"]["recommended_treatment"]["name"]
            base_message += f"Apply {treatment}. "
            
            if diagnosis["action_plan"]["urgency"] == "immediate":
                base_message += "URGENT! "
            
            if "weather_context" in diagnosis and diagnosis["weather_context"].get("rain_warning"):
                base_message += f"Rain coming - apply before 10 AM. "
        
        return base_message


def _prepare_sms_context(diagnosis: Dict) -> str:
    """Prepare context for NLP model."""
    context = f"Disease: {diagnosis.get('disease_name')}\n"
    context += f"Severity: {diagnosis.get('severity')}\n"
    
    if "action_plan" in diagnosis:
        context += f"Treatment: {diagnosis['action_plan']['recommended_treatment']['name']}\n"
        context += f"Timing: {diagnosis['action_plan']['timing_guidance']}\n"
    
    return context


def _call_huggingface_api(context: str, target_language: str) -> str:
    """Call Hugging Face API for translation."""
    hf_config = TENSORFLOW_CONFIG["apis"]["huggingface"]
    
    response = requests.post(
        f"{hf_config['base_url']}/{hf_config['model']}",
        headers={"Authorization": f"Bearer {hf_config['api_key']}"},
        json={
            "inputs": context,
            "parameters": {"src_lang": "en_XX", "tgt_lang": "sw_KE"}  # Swahili (Kenya)
        },
        timeout=10
    )
    
    if response.status_code == 200:
        return response.json()[0]["translation_text"]
    
    raise Exception(f"Hugging Face API error: {response.status_code}")


# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

__all__ = [
    "diagnose_plant_health_tflite",
    "TENSORFLOW_CONFIG",
    "DiagnosisSeverity"
]


if __name__ == "__main__":
    print("TensorFlow Model Integration System")
    print("=" * 60)
    print("\nModels configured:")
    for model_name, config in TENSORFLOW_CONFIG["models"].items():
        print(f"  - {model_name}: {config['model_type']}")
        print(f"    Edge deployment: {config['edge_deployment']}")
    
    print("\nAPI integrations:")
    for api_name, config in TENSORFLOW_CONFIG["apis"].items():
        status = "ENABLED" if config.get("enabled") else "DISABLED"
        print(f"  - {api_name}: {status}")
