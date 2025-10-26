"""
AI Pest & Disease Intelligence Engine
Advanced triage system, preventative biosecurity, outbreak pattern recognition.

Key Features:
1. AI-Driven Severity & Intervention Timing - Triage based on severity + stage
2. Preventative Biosecurity AI - Weather + SMI → pre-emptive alerts
3. AI-Enhanced Localized Action Plans - Community efficacy feedback optimization
4. Confidence Scoring & Expert Triage - Low confidence → route to extension officers
5. Outbreak Pattern Recognition - Identify invasive pests and hotspots

Author: AgriShield AI Team
Date: October 2025
"""

import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import random


# ============================================================================
# PEST/DISEASE DATABASE (Extended with AI Parameters)
# ============================================================================

PEST_DISEASE_DATABASE = {
    "late_blight": {
        "name": "Late Blight",
        "pathogen": "Phytophthora infestans",
        "type": "fungal",
        "affected_crops": ["potato", "tomato"],
        "severity_levels": {
            "early": {"leaf_coverage": (0, 10), "action_urgency": "low", "days_to_critical": 5},
            "moderate": {"leaf_coverage": (10, 30), "action_urgency": "medium", "days_to_critical": 3},
            "severe": {"leaf_coverage": (30, 100), "action_urgency": "critical", "days_to_critical": 1}
        },
        "weather_requirements": {
            "optimal_temp_range": (10, 25),
            "min_humidity": 90,
            "min_rain_hours": 12,  # Hours of leaf wetness
            "incubation_days": 3
        },
        "ipm_remedies": {
            "cultural": ["Remove infected plants", "Improve drainage", "Increase plant spacing"],
            "biological": ["Bacillus subtilis spray"],
            "organic": ["Copper-based fungicide", "Bordeaux mixture"],
            "chemical": ["Metalaxyl + Mancozeb (Ridomil Gold)", "Cymoxanil + Famoxadone (Equation Pro)"]
        },
        "efficacy_threshold": 0.7,  # If <70% report success, recommend rotation
        "resistance_risk": "high",
        "economic_loss_per_day": 500  # KES per acre per day of delay
    },
    
    "fall_armyworm": {
        "name": "Fall Armyworm",
        "pathogen": "Spodoptera frugiperda",
        "type": "insect",
        "affected_crops": ["maize", "sorghum", "rice"],
        "severity_levels": {
            "early": {"plant_damage": (0, 20), "action_urgency": "low", "days_to_critical": 7},
            "moderate": {"plant_damage": (20, 50), "action_urgency": "medium", "days_to_critical": 4},
            "severe": {"plant_damage": (50, 100), "action_urgency": "critical", "days_to_critical": 2}
        },
        "weather_requirements": {
            "optimal_temp_range": (25, 30),
            "min_humidity": 60,
            "egg_to_larva_days": 3
        },
        "ipm_remedies": {
            "cultural": ["Manual removal of egg masses", "Destroy crop residues", "Intercrop with beans"],
            "biological": ["Trichogramma wasps", "Neem oil spray", "Bt (Bacillus thuringiensis)"],
            "organic": ["Diatomaceous earth", "Garlic-chili spray"],
            "chemical": ["Chlorantraniliprole (Ampligo)", "Emamectin benzoate (Proclaim)"]
        },
        "efficacy_threshold": 0.75,
        "resistance_risk": "medium",
        "economic_loss_per_day": 400
    },
    
    "aphids": {
        "name": "Aphids",
        "pathogen": "Aphidoidea spp.",
        "type": "insect",
        "affected_crops": ["beans", "peas", "cabbage", "tomato"],
        "severity_levels": {
            "early": {"colony_size": (0, 50), "action_urgency": "low", "days_to_critical": 10},
            "moderate": {"colony_size": (50, 200), "action_urgency": "medium", "days_to_critical": 5},
            "severe": {"colony_size": (200, 1000), "action_urgency": "critical", "days_to_critical": 2}
        },
        "weather_requirements": {
            "optimal_temp_range": (20, 30),
            "min_humidity": 40,
            "reproduction_days": 7  # Generation time
        },
        "ipm_remedies": {
            "cultural": ["Plant marigolds (repellent)", "Remove weeds", "Use reflective mulch"],
            "biological": ["Ladybugs", "Lacewings", "Soapy water spray"],
            "organic": ["Neem oil", "Garlic spray", "Pyrethrum"],
            "chemical": ["Imidacloprid (Confidor)", "Acetamiprid (Assail)"]
        },
        "efficacy_threshold": 0.8,
        "resistance_risk": "high",
        "economic_loss_per_day": 200
    },
    
    "maize_streak_virus": {
        "name": "Maize Streak Virus",
        "pathogen": "Maize streak virus (MSV)",
        "type": "viral",
        "affected_crops": ["maize"],
        "severity_levels": {
            "early": {"plant_infection": (0, 10), "action_urgency": "low", "days_to_critical": 999},
            "moderate": {"plant_infection": (10, 40), "action_urgency": "medium", "days_to_critical": 999},
            "severe": {"plant_infection": (40, 100), "action_urgency": "high", "days_to_critical": 999}
        },
        "weather_requirements": {
            "optimal_temp_range": (25, 30),
            "vector": "leafhopper",  # Cicadulina mbila
            "min_humidity": 50
        },
        "ipm_remedies": {
            "cultural": ["Plant resistant varieties", "Early planting", "Remove infected plants", "Control leafhopper vectors"],
            "biological": ["No biological control (viral)"],
            "organic": ["No organic treatment (viral)"],
            "chemical": ["Vector control: Imidacloprid for leafhoppers"]
        },
        "efficacy_threshold": 0.5,  # Viral diseases are hard to control
        "resistance_risk": "low",  # No resistance (plant resistance varieties work)
        "economic_loss_per_day": 100  # Less urgent (no cure, focus on prevention)
    },
    
    "bean_rust": {
        "name": "Bean Rust",
        "pathogen": "Uromyces appendiculatus",
        "type": "fungal",
        "affected_crops": ["beans"],
        "severity_levels": {
            "early": {"leaf_coverage": (0, 15), "action_urgency": "low", "days_to_critical": 7},
            "moderate": {"leaf_coverage": (15, 40), "action_urgency": "medium", "days_to_critical": 4},
            "severe": {"leaf_coverage": (40, 100), "action_urgency": "critical", "days_to_critical": 2}
        },
        "weather_requirements": {
            "optimal_temp_range": (17, 27),
            "min_humidity": 95,
            "dew_required": True,
            "incubation_days": 7
        },
        "ipm_remedies": {
            "cultural": ["Remove infected leaves", "Improve air circulation", "Avoid overhead watering"],
            "biological": ["Bacillus subtilis"],
            "organic": ["Sulfur-based fungicide", "Copper spray"],
            "chemical": ["Tebuconazole (Folicur)", "Propiconazole (Tilt)"]
        },
        "efficacy_threshold": 0.75,
        "resistance_risk": "medium",
        "economic_loss_per_day": 300
    }
}


# ============================================================================
# AI-DRIVEN SEVERITY ANALYSIS & INTERVENTION TIMING
# ============================================================================

def analyze_pest_severity_with_ai(
    pest_disease_id: str,
    image_analysis: Dict,  # From CV model: {"leaf_coverage": 25, "plant_damage": 30, etc.}
    crop: str,
    crop_stage: str,  # "emergence", "vegetative", "flowering", "maturity"
    days_since_planting: int,
    gps_location: Tuple[float, float]
) -> Dict:
    """
    AI-driven triage: Analyze severity and determine intervention timing.
    
    Args:
        pest_disease_id: ID from PEST_DISEASE_DATABASE
        image_analysis: CV model output with severity metrics
        crop: Crop type
        crop_stage: Current growth stage
        days_since_planting: Days since planting
        gps_location: (latitude, longitude)
    
    Returns:
        {
            "severity": "early",  # early, moderate, severe
            "severity_score": 2.3,  # 0-10 scale
            "action_urgency": "low",  # low, medium, high, critical
            "days_to_critical": 5,
            "intervention_strategy": "ipm_organic",  # ipm_cultural, ipm_organic, ipm_chemical
            "recommended_actions": [...],
            "estimated_loss_if_no_action": 2500,  # KES
            "optimal_intervention_window": "24-48 hours",
            "ai_reasoning": "Early stage + low coverage = localized organic treatment sufficient"
        }
    """
    pest_data = PEST_DISEASE_DATABASE.get(pest_disease_id)
    if not pest_data:
        return {"error": f"Unknown pest/disease: {pest_disease_id}"}
    
    # 1. Determine Severity Level
    severity_metrics = image_analysis.get("leaf_coverage") or image_analysis.get("plant_damage") or 0
    
    severity_level = "early"
    for level_name, level_data in pest_data["severity_levels"].items():
        range_key = "leaf_coverage" if "leaf_coverage" in level_data else "plant_damage"
        if range_key in level_data:
            min_val, max_val = level_data[range_key]
            if min_val <= severity_metrics < max_val:
                severity_level = level_name
                break
    
    severity_info = pest_data["severity_levels"][severity_level]
    action_urgency = severity_info["action_urgency"]
    days_to_critical = severity_info["days_to_critical"]
    
    # 2. Severity Score (0-10)
    severity_score = (severity_metrics / 100) * 10  # Convert % to 0-10 scale
    
    # Adjust for crop stage (early stages = more vulnerable)
    if crop_stage in ["emergence", "vegetative"] and severity_metrics > 20:
        severity_score += 2  # Young crops more vulnerable
        action_urgency = "critical" if action_urgency == "high" else action_urgency
    
    # 3. Intervention Strategy
    if severity_level == "early" and severity_score < 3:
        intervention_strategy = "ipm_cultural"
        recommended_actions = pest_data["ipm_remedies"]["cultural"][:3]
    elif severity_level == "early" or (severity_level == "moderate" and severity_score < 5):
        intervention_strategy = "ipm_organic"
        recommended_actions = (
            pest_data["ipm_remedies"]["cultural"][:2] +
            pest_data["ipm_remedies"]["biological"][:2] +
            pest_data["ipm_remedies"]["organic"][:2]
        )
    else:
        intervention_strategy = "ipm_chemical"
        recommended_actions = (
            pest_data["ipm_remedies"]["cultural"][:1] +
            pest_data["ipm_remedies"]["chemical"][:2]
        )
    
    # 4. Estimated Economic Loss
    economic_loss_per_day = pest_data.get("economic_loss_per_day", 300)
    estimated_loss = economic_loss_per_day * days_to_critical
    
    # 5. Optimal Intervention Window
    if action_urgency == "critical":
        optimal_window = "Immediate (0-12 hours)"
    elif action_urgency == "high":
        optimal_window = "12-24 hours"
    elif action_urgency == "medium":
        optimal_window = "24-48 hours"
    else:
        optimal_window = "2-7 days"
    
    # 6. AI Reasoning
    reasoning_parts = []
    reasoning_parts.append(f"{severity_level.capitalize()} stage")
    reasoning_parts.append(f"{severity_metrics}% coverage")
    if crop_stage in ["emergence", "vegetative"]:
        reasoning_parts.append("vulnerable growth stage")
    reasoning_parts.append(f"{intervention_strategy.replace('ipm_', '')} treatment sufficient")
    
    ai_reasoning = " + ".join(reasoning_parts)
    
    return {
        "pest_disease": pest_data["name"],
        "pathogen": pest_data["pathogen"],
        "type": pest_data["type"],
        "severity": severity_level,
        "severity_score": round(severity_score, 1),
        "action_urgency": action_urgency,
        "days_to_critical": days_to_critical,
        "intervention_strategy": intervention_strategy,
        "recommended_actions": recommended_actions,
        "estimated_loss_if_no_action": estimated_loss,
        "optimal_intervention_window": optimal_window,
        "ai_reasoning": ai_reasoning,
        "resistance_risk": pest_data["resistance_risk"]
    }


# ============================================================================
# PREVENTATIVE BIOSECURITY AI
# ============================================================================

def predict_pest_outbreak_risk(
    crop: str,
    gps_location: Tuple[float, float],
    weather_forecast: Dict,  # 7-day forecast from LCRS
    soil_moisture_index: float,  # 0-10 (from SMI)
    current_date: datetime
) -> List[Dict]:
    """
    Preventative biosecurity: Predict pest/disease outbreaks BEFORE they occur.
    
    Args:
        crop: Crop type
        gps_location: (latitude, longitude)
        weather_forecast: {
            "next_7_days": [
                {"date": "2025-10-25", "temp_min": 15, "temp_max": 25, "humidity": 85, "rainfall": 20},
                ...
            ]
        }
        soil_moisture_index: Current SMI (0-10, 10=saturated)
        current_date: Current datetime
    
    Returns:
        [
            {
                "pest_disease": "late_blight",
                "risk_score": 8.5,  # 0-10
                "risk_category": "high",  # low, moderate, high, critical
                "predicted_onset": "2025-10-27",  # Date of likely outbreak
                "days_until_onset": 3,
                "triggering_conditions": ["High humidity (90%)", "Cool temps (15-25°C)", "48h rain"],
                "preventative_actions": [...],
                "confidence": 0.85
            },
            ...
        ]
    """
    forecasts = weather_forecast.get("next_7_days", [])
    if not forecasts:
        return []
    
    outbreak_predictions = []
    
    # Check each pest/disease in database
    for pest_id, pest_data in PEST_DISEASE_DATABASE.items():
        # Filter by crop
        if crop not in pest_data["affected_crops"]:
            continue
        
        weather_reqs = pest_data["weather_requirements"]
        
        # Analyze forecast for favorable conditions
        favorable_days = []
        for i, day_forecast in enumerate(forecasts):
            temp_min = day_forecast.get("temp_min", 20)
            temp_max = day_forecast.get("temp_max", 30)
            humidity = day_forecast.get("humidity", 60)
            rainfall = day_forecast.get("rainfall", 0)
            
            # Check temperature range
            optimal_temp = weather_reqs["optimal_temp_range"]
            temp_match = (optimal_temp[0] <= temp_min <= optimal_temp[1] or
                          optimal_temp[0] <= temp_max <= optimal_temp[1])
            
            # Check humidity
            humidity_match = humidity >= weather_reqs.get("min_humidity", 60)
            
            # Check rainfall (for fungal diseases)
            rain_match = True
            if pest_data["type"] == "fungal":
                rain_match = rainfall > 5  # Significant rain
            
            # Check soil moisture (for fungal diseases)
            smi_match = True
            if pest_data["type"] == "fungal" and soil_moisture_index < 6:
                smi_match = False  # Dry soil = lower fungal risk
            
            if temp_match and humidity_match and rain_match and smi_match:
                favorable_days.append({
                    "date": day_forecast.get("date"),
                    "days_from_now": i + 1
                })
        
        # If 2+ consecutive favorable days, predict outbreak
        if len(favorable_days) >= 2:
            # Check if days are consecutive
            consecutive_count = 1
            for j in range(1, len(favorable_days)):
                if favorable_days[j]["days_from_now"] == favorable_days[j-1]["days_from_now"] + 1:
                    consecutive_count += 1
                else:
                    break
            
            if consecutive_count >= 2:
                # Calculate risk score
                risk_score = 0
                
                # Base risk from consecutive days
                risk_score += min(consecutive_count * 2, 6)  # Max 6 points
                
                # Humidity factor
                avg_humidity = sum(d.get("humidity", 60) for d in forecasts[:3]) / 3
                if avg_humidity >= weather_reqs.get("min_humidity", 60):
                    risk_score += 2
                
                # Soil moisture factor (for fungal)
                if pest_data["type"] == "fungal" and soil_moisture_index >= 7:
                    risk_score += 2
                
                risk_score = min(risk_score, 10)
                
                # Risk category
                if risk_score >= 8:
                    risk_category = "critical"
                elif risk_score >= 6:
                    risk_category = "high"
                elif risk_score >= 4:
                    risk_category = "moderate"
                else:
                    risk_category = "low"
                
                # Predicted onset date (incubation period)
                incubation_days = weather_reqs.get("incubation_days", 3)
                onset_date = (current_date + timedelta(days=favorable_days[0]["days_from_now"] + incubation_days)).strftime("%Y-%m-%d")
                days_until_onset = favorable_days[0]["days_from_now"] + incubation_days
                
                # Triggering conditions
                triggers = []
                avg_temp = sum((d.get("temp_min", 20) + d.get("temp_max", 30)) / 2 for d in forecasts[:3]) / 3
                triggers.append(f"Optimal temp ({avg_temp:.0f}°C)")
                triggers.append(f"High humidity ({avg_humidity:.0f}%)")
                if any(d.get("rainfall", 0) > 10 for d in forecasts[:3]):
                    triggers.append("Heavy rainfall forecast")
                if soil_moisture_index >= 7:
                    triggers.append(f"Wet soil (SMI {soil_moisture_index})")
                
                # Preventative actions
                preventative_actions = pest_data["ipm_remedies"]["cultural"][:3]
                
                # Confidence (based on forecast accuracy and historical data)
                confidence = 0.75 if consecutive_count >= 3 else 0.65
                
                outbreak_predictions.append({
                    "pest_disease": pest_data["name"],
                    "pest_disease_id": pest_id,
                    "type": pest_data["type"],
                    "risk_score": round(risk_score, 1),
                    "risk_category": risk_category,
                    "predicted_onset": onset_date,
                    "days_until_onset": days_until_onset,
                    "triggering_conditions": triggers,
                    "preventative_actions": preventative_actions,
                    "confidence": confidence
                })
    
    # Sort by risk score (highest first)
    outbreak_predictions.sort(key=lambda x: x["risk_score"], reverse=True)
    
    return outbreak_predictions


# ============================================================================
# AI-ENHANCED LOCALIZED ACTION PLAN (EFFICACY OPTIMIZATION)
# ============================================================================

def optimize_action_plan_with_community_feedback(
    pest_disease_id: str,
    gps_location: Tuple[float, float],
    crop: str,
    variety: str,
    recommended_actions: List[str],
    community_feedback: List[Dict]  # From nearby farmers in Farming Zone Group
) -> Dict:
    """
    Optimize action plan based on local efficacy feedback.
    
    Args:
        pest_disease_id: Pest/disease ID
        gps_location: (latitude, longitude)
        crop: Crop type
        variety: Crop variety
        recommended_actions: Initial AI recommendations
        community_feedback: [
            {"action": "Neem spray", "success": True, "lat": -1.28, "lon": 36.82, "date": "2025-10-15"},
            {"action": "Confidor", "success": False, "lat": -1.29, "lon": 36.83, "date": "2025-10-20"},
            ...
        ]
    
    Returns:
        {
            "optimized_actions": [...],
            "actions_to_avoid": [...],
            "local_efficacy": {"Neem spray": 0.85, "Confidor": 0.45},
            "resistance_detected": True,
            "recommended_rotation": "Switch to Emamectin benzoate (different chemical class)",
            "nearest_effective_remedy": {"action": "Bt spray", "distance_km": 3.5, "success_rate": 0.9}
        }
    """
    pest_data = PEST_DISEASE_DATABASE.get(pest_disease_id)
    if not pest_data:
        return {"error": f"Unknown pest/disease: {pest_disease_id}"}
    
    # 1. Filter feedback to nearby locations (within 20km)
    nearby_feedback = []
    for feedback in community_feedback:
        distance_km = _calculate_distance(
            gps_location[0], gps_location[1],
            feedback["lat"], feedback["lon"]
        )
        if distance_km <= 20:  # Within 20km
            nearby_feedback.append({**feedback, "distance_km": distance_km})
    
    if not nearby_feedback:
        # No local feedback, return original recommendations
        return {
            "optimized_actions": recommended_actions,
            "actions_to_avoid": [],
            "local_efficacy": {},
            "resistance_detected": False,
            "recommended_rotation": None,
            "nearest_effective_remedy": None
        }
    
    # 2. Calculate local efficacy for each action
    action_efficacy = {}
    for action in set(f["action"] for f in nearby_feedback):
        action_feedback = [f for f in nearby_feedback if f["action"] == action]
        success_count = sum(1 for f in action_feedback if f.get("success"))
        efficacy_rate = success_count / len(action_feedback) if action_feedback else 0
        action_efficacy[action] = efficacy_rate
    
    # 3. Detect resistance (chemical efficacy < threshold)
    efficacy_threshold = pest_data.get("efficacy_threshold", 0.7)
    actions_to_avoid = []
    resistance_detected = False
    
    for action, efficacy in action_efficacy.items():
        if efficacy < efficacy_threshold:
            # Check if it's a chemical (from chemical remedies list)
            if action in pest_data["ipm_remedies"].get("chemical", []):
                actions_to_avoid.append(action)
                resistance_detected = True
    
    # 4. Optimize action list
    optimized_actions = []
    
    # Keep actions with good efficacy
    for action in recommended_actions:
        if action in action_efficacy:
            if action_efficacy[action] >= efficacy_threshold:
                optimized_actions.append(action)
        else:
            # No feedback yet, include it
            optimized_actions.append(action)
    
    # If resistance detected, recommend rotation to different chemical class
    recommended_rotation = None
    if resistance_detected and pest_data["resistance_risk"] in ["medium", "high"]:
        # Get all chemicals from database
        all_chemicals = pest_data["ipm_remedies"].get("chemical", [])
        # Filter out low-efficacy chemicals
        effective_chemicals = [c for c in all_chemicals if c not in actions_to_avoid]
        if effective_chemicals:
            recommended_rotation = f"Switch to {effective_chemicals[0]} (different chemical class to prevent resistance)"
            optimized_actions.append(effective_chemicals[0])
    
    # 5. Find nearest effective remedy
    nearest_effective = None
    if nearby_feedback:
        # Find most effective action within 10km
        effective_feedback = [
            f for f in nearby_feedback
            if f.get("success") and f["distance_km"] <= 10
        ]
        if effective_feedback:
            # Group by action and calculate success rate
            action_stats = {}
            for f in effective_feedback:
                action = f["action"]
                if action not in action_stats:
                    action_stats[action] = {"total": 0, "success": 0, "min_distance": 999}
                action_stats[action]["total"] += 1
                if f.get("success"):
                    action_stats[action]["success"] += 1
                action_stats[action]["min_distance"] = min(action_stats[action]["min_distance"], f["distance_km"])
            
            # Find best action
            best_action = max(
                action_stats.items(),
                key=lambda x: x[1]["success"] / x[1]["total"]
            )
            nearest_effective = {
                "action": best_action[0],
                "distance_km": round(best_action[1]["min_distance"], 1),
                "success_rate": round(best_action[1]["success"] / best_action[1]["total"], 2)
            }
    
    return {
        "optimized_actions": optimized_actions,
        "actions_to_avoid": actions_to_avoid,
        "local_efficacy": {k: round(v, 2) for k, v in action_efficacy.items()},
        "resistance_detected": resistance_detected,
        "recommended_rotation": recommended_rotation,
        "nearest_effective_remedy": nearest_effective
    }


def _calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two GPS points (Haversine formula)."""
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


# ============================================================================
# CONFIDENCE SCORING & EXPERT TRIAGE
# ============================================================================

def assess_diagnosis_confidence_and_triage(
    pest_disease_id: str,
    cv_model_confidence: float,  # 0-1 from CV model
    image_quality: Dict,  # {"brightness": 0.8, "sharpness": 0.7, "leaf_visibility": 0.9}
    symptom_clarity: float,  # 0-1 (how clear are symptoms)
    farmer_notes: Optional[str] = None
) -> Dict:
    """
    Assess AI diagnosis confidence and route to expert if needed.
    
    Args:
        pest_disease_id: Identified pest/disease
        cv_model_confidence: Raw confidence from CV model (0-1)
        image_quality: Quality metrics from image analysis
        symptom_clarity: How clear are disease symptoms (0-1)
        farmer_notes: Optional farmer observations
    
    Returns:
        {
            "final_confidence": 0.82,  # Adjusted confidence score
            "confidence_category": "high",  # low, medium, high, very_high
            "requires_expert_triage": False,
            "triage_reason": None,
            "expert_routing": {
                "route_to": "extension_officer",  # or "ngo_expert", "research_station"
                "urgency": "routine",  # routine, priority, urgent
                "data_package": {...}  # Image + location + notes for expert
            },
            "farmer_action": "proceed_with_ai_recommendation"  # or "wait_for_expert"
        }
    """
    # 1. Adjust confidence based on image quality
    adjusted_confidence = cv_model_confidence
    
    # Penalize for poor image quality
    brightness = image_quality.get("brightness", 0.5)
    sharpness = image_quality.get("sharpness", 0.5)
    leaf_visibility = image_quality.get("leaf_visibility", 0.5)
    
    avg_quality = (brightness + sharpness + leaf_visibility) / 3
    if avg_quality < 0.6:
        adjusted_confidence *= 0.8  # Reduce confidence by 20%
    
    # Adjust for symptom clarity
    if symptom_clarity < 0.6:
        adjusted_confidence *= 0.85  # Reduce confidence by 15%
    
    # Boost confidence if symptoms are very clear
    if symptom_clarity > 0.9:
        adjusted_confidence = min(adjusted_confidence * 1.1, 1.0)
    
    final_confidence = min(adjusted_confidence, 1.0)
    
    # 2. Confidence Category
    if final_confidence >= 0.85:
        confidence_category = "very_high"
    elif final_confidence >= 0.75:
        confidence_category = "high"
    elif final_confidence >= 0.60:
        confidence_category = "medium"
    else:
        confidence_category = "low"
    
    # 3. Expert Triage Decision
    CONFIDENCE_THRESHOLD = 0.75
    requires_triage = final_confidence < CONFIDENCE_THRESHOLD
    
    triage_reason = None
    expert_routing = None
    farmer_action = "proceed_with_ai_recommendation"
    
    if requires_triage:
        triage_reason = []
        if cv_model_confidence < 0.70:
            triage_reason.append("Low CV model confidence")
        if avg_quality < 0.6:
            triage_reason.append("Poor image quality")
        if symptom_clarity < 0.6:
            triage_reason.append("Unclear symptoms")
        
        triage_reason_str = ", ".join(triage_reason)
        
        # Determine routing
        pest_data = PEST_DISEASE_DATABASE.get(pest_disease_id, {})
        
        # Urgency based on action urgency
        if pest_data.get("severity_levels", {}).get("moderate", {}).get("action_urgency") == "critical":
            urgency = "urgent"
        elif final_confidence < 0.50:
            urgency = "priority"
        else:
            urgency = "routine"
        
        expert_routing = {
            "route_to": "extension_officer",  # Default routing
            "urgency": urgency,
            "data_package": {
                "pest_disease_id": pest_disease_id,
                "cv_confidence": cv_model_confidence,
                "final_confidence": final_confidence,
                "image_quality": image_quality,
                "symptom_clarity": symptom_clarity,
                "farmer_notes": farmer_notes,
                "triage_reason": triage_reason_str
            }
        }
        
        farmer_action = "wait_for_expert" if urgency == "urgent" else "proceed_with_caution"
    
    return {
        "final_confidence": round(final_confidence, 2),
        "confidence_category": confidence_category,
        "requires_expert_triage": requires_triage,
        "triage_reason": triage_reason,
        "expert_routing": expert_routing,
        "farmer_action": farmer_action
    }


# ============================================================================
# OUTBREAK PATTERN RECOGNITION
# ============================================================================

def detect_outbreak_patterns(
    pest_disease_id: str,
    recent_reports: List[Dict],  # Last 30 days of reports in region
    analysis_date: datetime
) -> Dict:
    """
    Analyze pest report patterns to detect invasive pests and outbreak hotspots.
    
    Args:
        pest_disease_id: Pest/disease being analyzed
        recent_reports: [
            {"lat": -1.28, "lon": 36.82, "date": "2025-10-20", "severity": "moderate"},
            ...
        ]
        analysis_date: Current date
    
    Returns:
        {
            "outbreak_detected": True,
            "outbreak_type": "invasive_pest",  # invasive_pest, localized_hotspot, seasonal_spike
            "spread_rate": 2.5,  # km per day
            "affected_area_km2": 150,
            "epicenter": {"lat": -1.28, "lon": 36.82},
            "alert_radius": 15,  # Expand alert radius from 5km to 15km
            "severity": "critical",
            "recommended_response": "Ministry of Agriculture notification + regional quarantine",
            "confidence": 0.88
        }
    """
    if len(recent_reports) < 5:
        # Not enough data
        return {
            "outbreak_detected": False,
            "reason": "Insufficient reports for pattern analysis"
        }
    
    # 1. Calculate spread rate
    # Sort reports by date
    sorted_reports = sorted(recent_reports, key=lambda x: x["date"])
    
    # Calculate geographic spread over time
    first_report = sorted_reports[0]
    last_report = sorted_reports[-1]
    
    first_date = datetime.fromisoformat(first_report["date"])
    last_date = datetime.fromisoformat(last_report["date"])
    days_elapsed = (last_date - first_date).days
    
    if days_elapsed == 0:
        days_elapsed = 1  # Avoid division by zero
    
    # Find max distance between first and last reports
    max_distance = _calculate_distance(
        first_report["lat"], first_report["lon"],
        last_report["lat"], last_report["lon"]
    )
    
    spread_rate = max_distance / days_elapsed if days_elapsed > 0 else 0
    
    # 2. Calculate affected area
    # Find bounding box
    lats = [r["lat"] for r in recent_reports]
    lons = [r["lon"] for r in recent_reports]
    
    lat_min, lat_max = min(lats), max(lats)
    lon_min, lon_max = min(lons), max(lons)
    
    # Approximate area (rough estimate)
    lat_km = (lat_max - lat_min) * 111  # 1 degree lat ≈ 111 km
    lon_km = (lon_max - lon_min) * 111 * math.cos(math.radians((lat_min + lat_max) / 2))
    affected_area = lat_km * lon_km
    
    # 3. Find epicenter (centroid)
    epicenter_lat = sum(lats) / len(lats)
    epicenter_lon = sum(lons) / len(lons)
    
    # 4. Detect outbreak type
    outbreak_detected = False
    outbreak_type = None
    severity = "low"
    alert_radius = 5  # Default
    recommended_response = "Continue monitoring"
    
    # Invasive pest criteria: Fast spread (>1 km/day) + large area (>50 km²)
    if spread_rate > 1.0 and affected_area > 50:
        outbreak_detected = True
        outbreak_type = "invasive_pest"
        severity = "critical"
        alert_radius = 15  # Expand to 15km
        recommended_response = "URGENT: Ministry of Agriculture notification + regional quarantine + mass treatment campaign"
    
    # Localized hotspot: Slow spread (<0.5 km/day) but high density
    elif spread_rate < 0.5 and len(recent_reports) > 10 and affected_area < 50:
        outbreak_detected = True
        outbreak_type = "localized_hotspot"
        severity = "high"
        alert_radius = 10
        recommended_response = "Localized intervention + farmer training + intensified monitoring"
    
    # Seasonal spike: Many reports in short time
    elif len(recent_reports) > 15 and days_elapsed < 14:
        outbreak_detected = True
        outbreak_type = "seasonal_spike"
        severity = "moderate"
        alert_radius = 8
        recommended_response = "Seasonal alert + preventative measures + community mobilization"
    
    # 5. Calculate confidence
    confidence = 0.5  # Base
    
    if len(recent_reports) > 20:
        confidence += 0.2  # More reports = higher confidence
    if days_elapsed >= 7:
        confidence += 0.15  # Longer observation = higher confidence
    if spread_rate > 0.5:
        confidence += 0.15  # Clear spread pattern
    
    confidence = min(confidence, 0.95)
    
    return {
        "outbreak_detected": outbreak_detected,
        "outbreak_type": outbreak_type,
        "spread_rate": round(spread_rate, 2),
        "affected_area_km2": int(affected_area),
        "epicenter": {"lat": round(epicenter_lat, 4), "lon": round(epicenter_lon, 4)},
        "alert_radius": alert_radius,
        "severity": severity,
        "recommended_response": recommended_response,
        "total_reports": len(recent_reports),
        "days_tracked": days_elapsed,
        "confidence": round(confidence, 2)
    }
