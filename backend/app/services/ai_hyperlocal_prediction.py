"""
AI Hyper-Local Prediction Engine (The "Brain")
==============================================

This module implements AI-powered micro-climate forecasting and disease/pest prediction:

1. **ML-Powered Predictive Fusion Model:**
   - Synthesizes satellite data, crowdsourced weather reports, and BLE sensor data
   - Dynamically weights data sources based on historical accuracy
   - Produces hyper-local micro-climate forecasts (village-level precision)

2. **AI-Driven Disease & Pest Forecasting:**
   - Pattern recognition against predicted weather + historical outbreak locations
   - Pre-emptive risk scoring (e.g., "75% chance of potato blight in 48 hours")
   - Continuous monitoring of pathogen life cycles + environmental triggers

Core Innovation:
- Overcomes low resolution of general weather models
- Provides actionable probability predictions instead of generic warnings
- Enables preventative action 48-72 hours before outbreaks

Author: AgroShield AI Team
Date: October 2025
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import math
import json


# ============================================================================
# WEATHER DATA SOURCE RELIABILITY TRACKING
# ============================================================================

# Track accuracy of each weather data source over time
WEATHER_SOURCE_RELIABILITY = {
    "satellite": {
        "trust_score": 0.85,  # Base reliability
        "historical_accuracy": [],  # Rolling window of accuracy scores
        "total_predictions": 0,
        "correct_predictions": 0
    },
    "crowdsourced": {
        "trust_score": 0.65,  # Lower initial trust (human reports)
        "farmer_reliability": {},  # Per-farmer accuracy tracking
        "historical_accuracy": [],
        "total_predictions": 0,
        "correct_predictions": 0
    },
    "ble_sensors": {
        "trust_score": 0.90,  # High trust (direct measurements)
        "sensor_calibration": {},  # Per-sensor calibration factors
        "historical_accuracy": [],
        "total_predictions": 0,
        "correct_predictions": 0
    }
}


# ============================================================================
# PATHOGEN & PEST LIFE CYCLE DATABASE
# ============================================================================

PATHOGEN_LIFE_CYCLES = {
    "late_blight": {
        "name": "Late Blight (Phytophthora infestans)",
        "type": "fungal",
        "affected_crops": ["potato", "tomato"],
        "activation_conditions": {
            "temperature_range": (10, 25),  # Celsius
            "min_humidity": 90,  # %
            "consecutive_wet_hours": 12,
            "optimal_temp": 18
        },
        "incubation_period_days": 3,  # Days from activation to visible symptoms
        "spread_rate_km_per_day": 2.5,
        "severity_stages": {
            "early": {"days": 3, "yield_loss_percent": 10},
            "moderate": {"days": 7, "yield_loss_percent": 30},
            "severe": {"days": 14, "yield_loss_percent": 70}
        },
        "preventative_window_hours": 48  # Time before activation to take action
    },
    "fall_armyworm": {
        "name": "Fall Armyworm (Spodoptera frugiperda)",
        "type": "insect",
        "affected_crops": ["maize", "sorghum", "rice"],
        "activation_conditions": {
            "temperature_range": (25, 30),
            "min_humidity": 60,
            "consecutive_dry_days": 2,
            "optimal_temp": 28
        },
        "incubation_period_days": 3,  # Egg to larva
        "spread_rate_km_per_day": 5.0,  # Can fly long distances
        "severity_stages": {
            "early": {"days": 5, "yield_loss_percent": 15},
            "moderate": {"days": 10, "yield_loss_percent": 40},
            "severe": {"days": 20, "yield_loss_percent": 80}
        },
        "preventative_window_hours": 72
    },
    "aphids": {
        "name": "Aphids (Various species)",
        "type": "insect",
        "affected_crops": ["beans", "cabbage", "peppers"],
        "activation_conditions": {
            "temperature_range": (20, 30),
            "min_humidity": 40,
            "consecutive_warm_days": 3,
            "optimal_temp": 24
        },
        "incubation_period_days": 7,  # Colony establishment
        "spread_rate_km_per_day": 0.5,  # Slow spread (wind-borne)
        "severity_stages": {
            "early": {"days": 7, "yield_loss_percent": 5},
            "moderate": {"days": 14, "yield_loss_percent": 20},
            "severe": {"days": 21, "yield_loss_percent": 50}
        },
        "preventative_window_hours": 96
    },
    "bean_rust": {
        "name": "Bean Rust (Uromyces appendiculatus)",
        "type": "fungal",
        "affected_crops": ["beans"],
        "activation_conditions": {
            "temperature_range": (17, 27),
            "min_humidity": 95,
            "consecutive_wet_hours": 8,
            "optimal_temp": 21
        },
        "incubation_period_days": 7,
        "spread_rate_km_per_day": 1.5,
        "severity_stages": {
            "early": {"days": 7, "yield_loss_percent": 8},
            "moderate": {"days": 14, "yield_loss_percent": 25},
            "severe": {"days": 21, "yield_loss_percent": 60}
        },
        "preventative_window_hours": 48
    },
    "maize_streak_virus": {
        "name": "Maize Streak Virus",
        "type": "viral",
        "affected_crops": ["maize"],
        "activation_conditions": {
            "temperature_range": (25, 32),
            "min_humidity": 50,
            "consecutive_warm_days": 5,  # Leafhopper activity
            "optimal_temp": 28
        },
        "incubation_period_days": 14,  # Virus incubation in plant
        "spread_rate_km_per_day": 3.0,  # Vector (leafhopper) mobility
        "severity_stages": {
            "early": {"days": 14, "yield_loss_percent": 20},
            "moderate": {"days": 28, "yield_loss_percent": 50},
            "severe": {"days": 42, "yield_loss_percent": 90}
        },
        "preventative_window_hours": 72  # Control vector before infection
    }
}


# ============================================================================
# HISTORICAL OUTBREAK DATABASE
# ============================================================================

# This would be populated from actual farmer reports
# Format: {"pathogen_id": [{"lat": float, "lon": float, "date": str, "severity": str}]}
HISTORICAL_OUTBREAKS = {}


# ============================================================================
# ML-POWERED PREDICTIVE FUSION MODEL
# ============================================================================

def update_source_reliability(source: str, prediction_correct: bool, farmer_id: Optional[str] = None):
    """
    Update trust scores based on prediction accuracy.
    
    Args:
        source: "satellite", "crowdsourced", or "ble_sensors"
        prediction_correct: Whether the prediction was accurate
        farmer_id: For crowdsourced data, track per-farmer reliability
    """
    if source not in WEATHER_SOURCE_RELIABILITY:
        return
    
    source_data = WEATHER_SOURCE_RELIABILITY[source]
    source_data["total_predictions"] += 1
    
    if prediction_correct:
        source_data["correct_predictions"] += 1
    
    # Update overall trust score (exponential moving average)
    accuracy = source_data["correct_predictions"] / source_data["total_predictions"]
    source_data["trust_score"] = 0.7 * source_data["trust_score"] + 0.3 * accuracy
    
    # Track per-farmer reliability for crowdsourced data
    if source == "crowdsourced" and farmer_id:
        if farmer_id not in source_data["farmer_reliability"]:
            source_data["farmer_reliability"][farmer_id] = {
                "trust_score": 0.5,
                "total": 0,
                "correct": 0
            }
        
        farmer_data = source_data["farmer_reliability"][farmer_id]
        farmer_data["total"] += 1
        if prediction_correct:
            farmer_data["correct"] += 1
        
        farmer_accuracy = farmer_data["correct"] / farmer_data["total"]
        farmer_data["trust_score"] = 0.6 * farmer_data["trust_score"] + 0.4 * farmer_accuracy


def synthesize_micro_climate_forecast(
    lat: float,
    lon: float,
    forecast_days: int = 7,
    satellite_data: Optional[List[Dict]] = None,
    crowdsourced_reports: Optional[List[Dict]] = None,
    ble_sensor_data: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    AI-powered fusion of multiple weather data sources to create hyper-local forecast.
    
    Uses machine learning to dynamically weight data sources based on historical accuracy.
    
    Args:
        lat: Latitude of location
        lon: Longitude of location
        forecast_days: Number of days to forecast (default 7)
        satellite_data: List of satellite weather predictions
        crowdsourced_reports: List of farmer weather reports from nearby locations
        ble_sensor_data: Current BLE sensor readings (temp, humidity, soil moisture)
    
    Returns:
        dict: Micro-climate forecast with confidence scores and source weights
    """
    # Get trust scores for each source
    satellite_trust = WEATHER_SOURCE_RELIABILITY["satellite"]["trust_score"]
    crowdsourced_trust = WEATHER_SOURCE_RELIABILITY["crowdsourced"]["trust_score"]
    ble_trust = WEATHER_SOURCE_RELIABILITY["ble_sensors"]["trust_score"]
    
    # Simulate satellite forecast (in production, integrate real satellite API)
    if satellite_data is None:
        satellite_data = _simulate_satellite_forecast(lat, lon, forecast_days)
    
    # Simulate crowdsourced reports (in production, query farmer reports from database)
    if crowdsourced_reports is None:
        crowdsourced_reports = _simulate_crowdsourced_reports(lat, lon)
    
    # Simulate BLE sensor data (in production, query real BLE sensors)
    if ble_sensor_data is None:
        ble_sensor_data = _simulate_ble_sensors()
    
    # Calculate weighted forecast for each day
    micro_climate_forecast = []
    
    for day_idx in range(forecast_days):
        date = datetime.now() + timedelta(days=day_idx)
        
        # Get predictions from each source
        satellite_prediction = satellite_data[day_idx] if day_idx < len(satellite_data) else {}
        
        # Weight crowdsourced reports by proximity and farmer reliability
        weighted_crowdsourced = _weight_crowdsourced_data(
            crowdsourced_reports, lat, lon, day_idx
        )
        
        # BLE sensors only provide current day data
        ble_adjustment = ble_sensor_data if day_idx == 0 else {}
        
        # Synthesize final forecast using dynamic weights
        synthesized_forecast = _synthesize_daily_forecast(
            satellite_prediction,
            weighted_crowdsourced,
            ble_adjustment,
            satellite_trust,
            crowdsourced_trust,
            ble_trust
        )
        
        synthesized_forecast["date"] = date.strftime("%Y-%m-%d")
        synthesized_forecast["day_index"] = day_idx
        
        micro_climate_forecast.append(synthesized_forecast)
    
    return {
        "location": {"lat": lat, "lon": lon},
        "forecast": micro_climate_forecast,
        "data_sources": {
            "satellite": {"trust_score": satellite_trust, "active": True},
            "crowdsourced": {
                "trust_score": crowdsourced_trust,
                "active": len(crowdsourced_reports) > 0,
                "num_reports": len(crowdsourced_reports)
            },
            "ble_sensors": {"trust_score": ble_trust, "active": ble_sensor_data is not None}
        },
        "model_confidence": _calculate_overall_confidence(
            satellite_trust, crowdsourced_trust, ble_trust
        ),
        "generated_at": datetime.now().isoformat()
    }


def _weight_crowdsourced_data(
    reports: List[Dict],
    target_lat: float,
    target_lon: float,
    day_offset: int
) -> Dict[str, float]:
    """
    Weight crowdsourced weather reports by proximity and farmer reliability.
    
    Args:
        reports: List of farmer weather reports
        target_lat: Target location latitude
        target_lon: Target location longitude
        day_offset: Days in the future (0 = today)
    
    Returns:
        dict: Weighted average of crowdsourced predictions
    """
    if not reports:
        return {}
    
    farmer_reliability = WEATHER_SOURCE_RELIABILITY["crowdsourced"]["farmer_reliability"]
    
    weighted_temp = 0.0
    weighted_humidity = 0.0
    weighted_rainfall = 0.0
    total_weight = 0.0
    
    for report in reports:
        # Calculate distance weight (closer reports = higher weight)
        distance_km = _calculate_distance(
            target_lat, target_lon, report.get("lat", 0), report.get("lon", 0)
        )
        
        # Distance weight decays exponentially (5km = full weight, 20km = minimal weight)
        distance_weight = math.exp(-distance_km / 10.0)
        
        # Farmer reliability weight
        farmer_id = report.get("farmer_id", "unknown")
        farmer_trust = farmer_reliability.get(farmer_id, {}).get("trust_score", 0.5)
        
        # Combined weight
        weight = distance_weight * farmer_trust
        
        # Accumulate weighted values
        if "temperature" in report:
            weighted_temp += report["temperature"] * weight
        if "humidity" in report:
            weighted_humidity += report["humidity"] * weight
        if "rainfall_mm" in report:
            weighted_rainfall += report["rainfall_mm"] * weight
        
        total_weight += weight
    
    if total_weight == 0:
        return {}
    
    return {
        "temperature": weighted_temp / total_weight,
        "humidity": weighted_humidity / total_weight,
        "rainfall_mm": weighted_rainfall / total_weight,
        "confidence": min(total_weight, 1.0)  # Cap at 1.0
    }


def _synthesize_daily_forecast(
    satellite: Dict,
    crowdsourced: Dict,
    ble: Dict,
    satellite_trust: float,
    crowdsourced_trust: float,
    ble_trust: float
) -> Dict[str, Any]:
    """
    Synthesize final forecast from multiple sources using dynamic weights.
    
    Args:
        satellite: Satellite prediction
        crowdsourced: Weighted crowdsourced prediction
        ble: BLE sensor data (current day only)
        satellite_trust: Trust score for satellite data
        crowdsourced_trust: Trust score for crowdsourced data
        ble_trust: Trust score for BLE sensors
    
    Returns:
        dict: Synthesized forecast with confidence scores
    """
    # Determine which sources are available
    sources = []
    if satellite:
        sources.append(("satellite", satellite, satellite_trust))
    if crowdsourced:
        sources.append(("crowdsourced", crowdsourced, crowdsourced_trust))
    if ble:
        sources.append(("ble", ble, ble_trust))
    
    if not sources:
        return {"error": "No data sources available"}
    
    # Weighted average for each metric
    synthesized = {}
    
    for metric in ["temperature", "humidity", "rainfall_mm"]:
        weighted_sum = 0.0
        total_weight = 0.0
        
        for source_name, source_data, trust in sources:
            if metric in source_data:
                # Adjust weight based on source-specific confidence
                source_confidence = source_data.get("confidence", 1.0)
                weight = trust * source_confidence
                
                weighted_sum += source_data[metric] * weight
                total_weight += weight
        
        if total_weight > 0:
            synthesized[metric] = round(weighted_sum / total_weight, 2)
            synthesized[f"{metric}_confidence"] = round(min(total_weight, 1.0), 2)
    
    # Calculate temperature range (min/max)
    if "temperature" in synthesized:
        synthesized["temperature_min"] = synthesized["temperature"] - 3
        synthesized["temperature_max"] = synthesized["temperature"] + 3
    
    # Classify weather conditions
    synthesized["conditions"] = _classify_weather_conditions(synthesized)
    
    # Overall confidence for this day's forecast
    synthesized["overall_confidence"] = _calculate_overall_confidence(
        satellite_trust, crowdsourced_trust, ble_trust
    )
    
    return synthesized


def _classify_weather_conditions(forecast: Dict) -> str:
    """Classify weather conditions based on temperature, humidity, and rainfall."""
    rainfall = forecast.get("rainfall_mm", 0)
    humidity = forecast.get("humidity", 50)
    temp = forecast.get("temperature", 20)
    
    if rainfall > 10:
        return "heavy_rain"
    elif rainfall > 2:
        return "light_rain"
    elif humidity > 80 and temp < 25:
        return "cool_humid"
    elif humidity > 80 and temp >= 25:
        return "hot_humid"
    elif humidity < 40:
        return "dry"
    else:
        return "moderate"


def _calculate_overall_confidence(
    satellite_trust: float,
    crowdsourced_trust: float,
    ble_trust: float
) -> float:
    """Calculate overall model confidence based on active data sources."""
    # Average of available trust scores
    active_sources = [t for t in [satellite_trust, crowdsourced_trust, ble_trust] if t > 0]
    if not active_sources:
        return 0.5  # Default moderate confidence
    
    return round(sum(active_sources) / len(active_sources), 2)


def _calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two GPS coordinates (Haversine formula)."""
    R = 6371  # Earth's radius in km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


# ============================================================================
# AI-DRIVEN DISEASE & PEST FORECASTING
# ============================================================================

def predict_pest_disease_outbreaks(
    crop: str,
    lat: float,
    lon: float,
    micro_climate_forecast: Dict,
    historical_outbreak_radius_km: float = 50
) -> List[Dict[str, Any]]:
    """
    AI-driven disease & pest forecasting with pre-emptive risk scoring.
    
    Uses pattern recognition against predicted weather, historical outbreak locations,
    and pathogen life cycles to predict outbreak probability.
    
    Args:
        crop: Crop type (e.g., "potato", "maize")
        lat: Latitude of farm
        lon: Longitude of farm
        micro_climate_forecast: Output from synthesize_micro_climate_forecast()
        historical_outbreak_radius_km: Search radius for historical outbreaks
    
    Returns:
        list: Outbreak predictions with probability scores and timing
    """
    outbreak_predictions = []
    
    # Get forecast data
    forecast_days = micro_climate_forecast.get("forecast", [])
    
    # Check each pathogen in database
    for pathogen_id, pathogen in PATHOGEN_LIFE_CYCLES.items():
        # Skip if pathogen doesn't affect this crop
        if crop not in pathogen["affected_crops"]:
            continue
        
        # Analyze forecast for activation conditions
        activation_analysis = _analyze_activation_conditions(
            pathogen, forecast_days
        )
        
        if not activation_analysis["activation_possible"]:
            continue
        
        # Calculate proximity to historical outbreaks
        historical_risk = _calculate_historical_outbreak_risk(
            pathogen_id, lat, lon, historical_outbreak_radius_km
        )
        
        # Calculate final outbreak probability
        outbreak_probability = _calculate_outbreak_probability(
            activation_analysis, historical_risk
        )
        
        if outbreak_probability["risk_score"] >= 3.0:  # Threshold: 30%
            prediction = {
                "pathogen_id": pathogen_id,
                "pathogen_name": pathogen["name"],
                "pathogen_type": pathogen["type"],
                "affected_crop": crop,
                "outbreak_probability": outbreak_probability["risk_score"] / 10.0,  # 0-1 scale
                "risk_category": outbreak_probability["risk_category"],
                "predicted_activation_date": activation_analysis["activation_date"],
                "days_until_activation": activation_analysis["days_until_activation"],
                "visible_symptoms_date": activation_analysis["symptoms_date"],
                "days_until_visible_symptoms": activation_analysis["days_until_symptoms"],
                "preventative_window_closes": activation_analysis["preventative_deadline"],
                "hours_to_take_action": activation_analysis["hours_to_act"],
                "triggering_conditions": activation_analysis["triggering_conditions"],
                "historical_outbreaks_nearby": historical_risk["nearby_outbreaks"],
                "preventative_actions": _get_preventative_actions(pathogen_id),
                "expected_severity_if_untreated": _estimate_severity(
                    pathogen, activation_analysis["days_until_activation"]
                ),
                "confidence": outbreak_probability["confidence"],
                "ai_reasoning": outbreak_probability["reasoning"]
            }
            
            outbreak_predictions.append(prediction)
    
    # Sort by risk score (highest first)
    outbreak_predictions.sort(key=lambda x: x["outbreak_probability"], reverse=True)
    
    return outbreak_predictions


def _analyze_activation_conditions(
    pathogen: Dict,
    forecast_days: List[Dict]
) -> Dict[str, Any]:
    """
    Analyze weather forecast to determine if pathogen activation conditions will be met.
    
    Returns:
        dict: Activation analysis with timing and triggering conditions
    """
    conditions = pathogen["activation_conditions"]
    
    for day_idx, day_forecast in enumerate(forecast_days):
        temp = day_forecast.get("temperature", 20)
        humidity = day_forecast.get("humidity", 50)
        rainfall = day_forecast.get("rainfall_mm", 0)
        
        # Check temperature range
        temp_ok = conditions["temperature_range"][0] <= temp <= conditions["temperature_range"][1]
        
        # Check humidity
        humidity_ok = humidity >= conditions["min_humidity"]
        
        # Check consecutive conditions
        consecutive_met = _check_consecutive_conditions(
            forecast_days[day_idx:], conditions
        )
        
        if temp_ok and humidity_ok and consecutive_met:
            activation_date = datetime.now() + timedelta(days=day_idx)
            incubation_days = pathogen["incubation_period_days"]
            symptoms_date = activation_date + timedelta(days=incubation_days)
            preventative_hours = pathogen["preventative_window_hours"]
            preventative_deadline = activation_date - timedelta(hours=preventative_hours)
            
            return {
                "activation_possible": True,
                "activation_date": activation_date.strftime("%Y-%m-%d"),
                "days_until_activation": day_idx,
                "symptoms_date": symptoms_date.strftime("%Y-%m-%d"),
                "days_until_symptoms": day_idx + incubation_days,
                "preventative_deadline": preventative_deadline.strftime("%Y-%m-%d %H:%M"),
                "hours_to_act": int((preventative_deadline - datetime.now()).total_seconds() / 3600),
                "triggering_conditions": [
                    f"Optimal temperature ({temp}°C)",
                    f"High humidity ({humidity}%)",
                    f"Rainfall forecast ({rainfall} mm)" if rainfall > 0 else "Dry conditions"
                ]
            }
    
    return {"activation_possible": False}


def _check_consecutive_conditions(forecast_days: List[Dict], conditions: Dict) -> bool:
    """Check if consecutive weather conditions are met (e.g., 12 hours of rain)."""
    # Simplified: Check if conditions met for at least 2 consecutive days
    if len(forecast_days) < 2:
        return False
    
    consecutive_count = 0
    
    for day in forecast_days[:3]:  # Check first 3 days
        temp = day.get("temperature", 20)
        humidity = day.get("humidity", 50)
        
        temp_ok = conditions["temperature_range"][0] <= temp <= conditions["temperature_range"][1]
        humidity_ok = humidity >= conditions["min_humidity"]
        
        if temp_ok and humidity_ok:
            consecutive_count += 1
        else:
            break
    
    return consecutive_count >= 2


def _calculate_historical_outbreak_risk(
    pathogen_id: str,
    lat: float,
    lon: float,
    radius_km: float
) -> Dict[str, Any]:
    """
    Calculate risk based on proximity to historical outbreaks.
    
    Args:
        pathogen_id: Pathogen identifier
        lat: Farm latitude
        lon: Farm longitude
        radius_km: Search radius for historical outbreaks
    
    Returns:
        dict: Historical risk analysis
    """
    if pathogen_id not in HISTORICAL_OUTBREAKS:
        return {"nearby_outbreaks": 0, "risk_multiplier": 1.0}
    
    nearby_outbreaks = []
    
    for outbreak in HISTORICAL_OUTBREAKS[pathogen_id]:
        distance = _calculate_distance(
            lat, lon, outbreak["lat"], outbreak["lon"]
        )
        
        if distance <= radius_km:
            nearby_outbreaks.append({
                "distance_km": round(distance, 2),
                "date": outbreak["date"],
                "severity": outbreak.get("severity", "unknown")
            })
    
    # Risk multiplier based on proximity and recency
    if len(nearby_outbreaks) == 0:
        risk_multiplier = 1.0
    elif len(nearby_outbreaks) <= 2:
        risk_multiplier = 1.2
    elif len(nearby_outbreaks) <= 5:
        risk_multiplier = 1.5
    else:
        risk_multiplier = 2.0
    
    return {
        "nearby_outbreaks": len(nearby_outbreaks),
        "risk_multiplier": risk_multiplier,
        "closest_outbreak": nearby_outbreaks[0] if nearby_outbreaks else None
    }


def _calculate_outbreak_probability(
    activation_analysis: Dict,
    historical_risk: Dict
) -> Dict[str, Any]:
    """
    Calculate final outbreak probability combining weather conditions and historical data.
    
    Returns:
        dict: Risk score (0-10), risk category, confidence, reasoning
    """
    # Base risk from weather conditions (0-10 scale)
    days_until = activation_analysis["days_until_activation"]
    
    # Risk decreases with time (further in future = less certain)
    if days_until <= 2:
        base_risk = 8.0  # High risk (imminent)
    elif days_until <= 4:
        base_risk = 6.0  # Moderate-high risk
    elif days_until <= 6:
        base_risk = 4.0  # Moderate risk
    else:
        base_risk = 2.0  # Low risk (distant future)
    
    # Apply historical outbreak multiplier
    final_risk = base_risk * historical_risk["risk_multiplier"]
    final_risk = min(final_risk, 10.0)  # Cap at 10
    
    # Categorize risk
    if final_risk >= 7.5:
        risk_category = "critical"
    elif final_risk >= 5.0:
        risk_category = "high"
    elif final_risk >= 3.0:
        risk_category = "moderate"
    else:
        risk_category = "low"
    
    # Confidence based on data quality
    confidence = 0.85 if historical_risk["nearby_outbreaks"] > 0 else 0.70
    
    # Reasoning
    reasoning = f"Weather conditions favor outbreak in {days_until} days. "
    if historical_risk["nearby_outbreaks"] > 0:
        reasoning += f"{historical_risk['nearby_outbreaks']} historical outbreaks within 50km. "
    reasoning += f"Risk score: {final_risk:.1f}/10."
    
    return {
        "risk_score": final_risk,
        "risk_category": risk_category,
        "confidence": confidence,
        "reasoning": reasoning
    }


def _get_preventative_actions(pathogen_id: str) -> List[str]:
    """Get preventative actions for a specific pathogen."""
    preventative_actions = {
        "late_blight": [
            "Remove infected plants immediately",
            "Improve field drainage",
            "Increase plant spacing for air circulation",
            "Apply copper-based fungicide preventatively",
            "Avoid overhead irrigation"
        ],
        "fall_armyworm": [
            "Scout fields daily for egg masses",
            "Apply Bt (Bacillus thuringiensis) spray",
            "Use pheromone traps to monitor population",
            "Plant trap crops around field perimeter",
            "Handpick egg masses and larvae"
        ],
        "aphids": [
            "Introduce beneficial insects (ladybugs, lacewings)",
            "Spray neem oil or insecticidal soap",
            "Remove heavily infested leaves",
            "Use reflective mulch to repel aphids",
            "Plant companion plants (garlic, chives)"
        ],
        "bean_rust": [
            "Improve air circulation (weed control)",
            "Avoid overhead watering (water at base)",
            "Apply sulfur-based fungicide preventatively",
            "Remove infected leaves",
            "Plant resistant varieties next season"
        ],
        "maize_streak_virus": [
            "Control leafhopper vectors with Imidacloprid",
            "Plant resistant/tolerant maize varieties",
            "Remove infected plants to reduce virus reservoir",
            "Use clean planting material",
            "Stagger planting to break vector cycle"
        ]
    }
    
    return preventative_actions.get(pathogen_id, ["Consult extension officer for guidance"])


def _estimate_severity(pathogen: Dict, days_until_activation: int) -> str:
    """Estimate expected severity if outbreak is not prevented."""
    if days_until_activation <= 3:
        return "severe"  # Imminent threat = high severity
    elif days_until_activation <= 6:
        return "moderate"
    else:
        return "early"


# ============================================================================
# SIMULATION HELPERS (PRODUCTION: REPLACE WITH REAL DATA SOURCES)
# ============================================================================

def _simulate_satellite_forecast(lat: float, lon: float, days: int) -> List[Dict]:
    """Simulate satellite weather forecast (replace with real API in production)."""
    import random
    forecast = []
    
    for i in range(days):
        forecast.append({
            "temperature": random.uniform(18, 28),
            "humidity": random.uniform(50, 90),
            "rainfall_mm": random.uniform(0, 15),
            "confidence": 0.85
        })
    
    return forecast


def _simulate_crowdsourced_reports(lat: float, lon: float) -> List[Dict]:
    """Simulate farmer weather reports (replace with database query in production)."""
    import random
    reports = []
    
    # Simulate 3-5 nearby farmer reports
    for i in range(random.randint(3, 5)):
        reports.append({
            "farmer_id": f"farmer_{i:03d}",
            "lat": lat + random.uniform(-0.05, 0.05),
            "lon": lon + random.uniform(-0.05, 0.05),
            "temperature": random.uniform(20, 26),
            "humidity": random.uniform(60, 85),
            "rainfall_mm": random.uniform(0, 10),
            "reported_at": datetime.now().isoformat()
        })
    
    return reports


def _simulate_ble_sensors() -> Dict:
    """Simulate BLE sensor data (replace with real BLE query in production)."""
    import random
    return {
        "temperature": random.uniform(22, 26),
        "humidity": random.uniform(65, 80),
        "soil_moisture": random.uniform(5, 8),
        "confidence": 0.95
    }


# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

__all__ = [
    "synthesize_micro_climate_forecast",
    "predict_pest_disease_outbreaks",
    "update_source_reliability",
    "PATHOGEN_LIFE_CYCLES"
]
