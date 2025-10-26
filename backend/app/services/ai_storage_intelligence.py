"""
AI Storage Intelligence Engine
Predictive spoilage modeling, smart alert prioritization, and optimized remediation strategies.

Key Features:
1. Predictive Spoilage Modeling - Days to critical risk calculation
2. Smart Alert Prioritization - History-aware severity scoring
3. AI-Optimized Remediation - Weather-aware actionable advice
4. Stored Pest Prediction - Life cycle analysis for weevils, moths, beetles
5. Local Storage Strategy - Harvest-quality-based preservation planning

Author: AgriShield AI Team
Date: October 2025
"""

import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple


# ============================================================================
# CROP STORAGE PROFILES (Extended with AI Parameters)
# ============================================================================

CROP_STORAGE_PROFILES = {
    "maize": {
        "safe_temp_min": 10,
        "safe_temp_max": 21,
        "safe_humidity_min": 50,
        "safe_humidity_max": 65,
        "critical_humidity": 70,  # Mold growth accelerates rapidly above this
        "optimal_moisture_content": 13.5,  # % at harvest for safe storage
        "mold_susceptibility": 8,  # 0-10 scale (maize is highly susceptible)
        "weevil_susceptibility": 9,
        "common_pests": ["maize_weevil", "larger_grain_borer", "angoumois_grain_moth"],
        "spoilage_rate_multiplier": 1.2,  # How fast conditions deteriorate
        "economic_value_per_kg": 45,  # KES (for loss calculation)
    },
    "beans": {
        "safe_temp_min": 10,
        "safe_temp_max": 18,
        "safe_humidity_min": 50,
        "safe_humidity_max": 60,
        "critical_humidity": 65,
        "optimal_moisture_content": 12.0,
        "mold_susceptibility": 6,
        "weevil_susceptibility": 7,
        "common_pests": ["bean_weevil", "bean_bruchid"],
        "spoilage_rate_multiplier": 1.0,
        "economic_value_per_kg": 120,
    },
    "potatoes": {
        "safe_temp_min": 7,
        "safe_temp_max": 10,
        "safe_humidity_min": 85,
        "safe_humidity_max": 95,
        "critical_humidity": 98,  # Sprout and rot risk
        "optimal_moisture_content": None,  # Fresh produce
        "mold_susceptibility": 9,  # Very high (tuber rot)
        "weevil_susceptibility": 3,  # Low
        "common_pests": ["potato_tuber_moth", "bacterial_soft_rot"],
        "spoilage_rate_multiplier": 1.8,  # Deteriorates quickly
        "economic_value_per_kg": 65,
    },
    "rice": {
        "safe_temp_min": 10,
        "safe_temp_max": 21,
        "safe_humidity_min": 50,
        "safe_humidity_max": 65,
        "critical_humidity": 70,
        "optimal_moisture_content": 14.0,
        "mold_susceptibility": 7,
        "weevil_susceptibility": 8,
        "common_pests": ["rice_weevil", "angoumois_grain_moth"],
        "spoilage_rate_multiplier": 1.1,
        "economic_value_per_kg": 95,
    },
    "cassava": {
        "safe_temp_min": 0,
        "safe_temp_max": 5,
        "safe_humidity_min": 85,
        "safe_humidity_max": 95,
        "critical_humidity": 98,
        "optimal_moisture_content": None,  # Fresh root
        "mold_susceptibility": 10,  # Extremely high (2-4 days shelf life)
        "weevil_susceptibility": 2,
        "common_pests": ["cassava_mealybug", "bacterial_wilt"],
        "spoilage_rate_multiplier": 2.5,  # Fastest deterioration
        "economic_value_per_kg": 35,
    },
}


# ============================================================================
# PEST LIFE CYCLE MODELS (Temperature-Dependent Development)
# ============================================================================

PEST_LIFE_CYCLES = {
    "maize_weevil": {
        "species": "Sitophilus zeamais",
        "egg_to_adult_days": {
            15: 120,  # Temperature (°C): Days to adult emergence
            20: 60,
            25: 35,
            30: 28,
            35: 25,  # Optimal for development
        },
        "optimal_temp_range": (27, 31),
        "mortality_temp_min": 10,  # Below this, eggs die
        "mortality_temp_max": 40,  # Above this, larvae die
        "detection_threshold": 0.7,  # 70% of development = alert
    },
    "larger_grain_borer": {
        "species": "Prostephanus truncatus",
        "egg_to_adult_days": {
            20: 50,
            25: 32,
            30: 25,
            35: 23,
        },
        "optimal_temp_range": (28, 32),
        "mortality_temp_min": 15,
        "mortality_temp_max": 38,
        "detection_threshold": 0.65,
    },
    "bean_weevil": {
        "species": "Acanthoscelides obtectus",
        "egg_to_adult_days": {
            15: 90,
            20: 50,
            25: 28,
            30: 21,
        },
        "optimal_temp_range": (25, 30),
        "mortality_temp_min": 10,
        "mortality_temp_max": 35,
        "detection_threshold": 0.7,
    },
    "angoumois_grain_moth": {
        "species": "Sitotroga cerealella",
        "egg_to_adult_days": {
            20: 45,
            25: 30,
            30: 22,
            35: 18,
        },
        "optimal_temp_range": (28, 32),
        "mortality_temp_min": 12,
        "mortality_temp_max": 38,
        "detection_threshold": 0.6,
    },
}


# ============================================================================
# MOLD GROWTH MODELS (Temperature × Humidity Risk)
# ============================================================================

def calculate_mold_risk_score(temp_c: float, humidity_pct: float, 
                               crop_susceptibility: int) -> float:
    """
    Calculate mold growth risk score (0-10).
    
    Formula: Risk = Temp_Factor × Humidity_Factor × Susceptibility_Factor
    
    Critical zones:
    - Temp 20-30°C + Humidity >70% = Rapid mold growth
    - Temp >30°C + Humidity >80% = Extreme risk (aflatoxin production)
    
    Args:
        temp_c: Current temperature (Celsius)
        humidity_pct: Current relative humidity (%)
        crop_susceptibility: Crop's mold susceptibility (0-10)
    
    Returns:
        Risk score: 0-10 (0=safe, 10=critical)
    """
    # Temperature factor (mold grows best 20-30°C)
    if 20 <= temp_c <= 30:
        temp_factor = 1.0
    elif 15 <= temp_c < 20 or 30 < temp_c <= 35:
        temp_factor = 0.6
    elif temp_c < 15 or temp_c > 35:
        temp_factor = 0.2  # Too cold or too hot for mold
    else:
        temp_factor = 0.0
    
    # Humidity factor (mold needs >60% humidity)
    if humidity_pct >= 80:
        humidity_factor = 1.0
    elif 70 <= humidity_pct < 80:
        humidity_factor = 0.8
    elif 60 <= humidity_pct < 70:
        humidity_factor = 0.5
    else:
        humidity_factor = 0.1  # Below 60%, slow mold growth
    
    # Susceptibility factor (crop-specific)
    susceptibility_factor = crop_susceptibility / 10.0
    
    # Combined risk score
    risk = temp_factor * humidity_factor * susceptibility_factor * 10
    
    return min(risk, 10.0)  # Cap at 10


def predict_days_to_critical_mold(temp_c: float, humidity_pct: float,
                                    crop_susceptibility: int,
                                    spoilage_multiplier: float) -> int:
    """
    Predict days until mold reaches critical levels.
    
    Args:
        temp_c: Current temperature
        humidity_pct: Current humidity
        crop_susceptibility: Crop's mold susceptibility (0-10)
        spoilage_multiplier: Crop's deterioration speed multiplier
    
    Returns:
        Days to critical risk (1-30 days, or 999 if safe)
    """
    risk_score = calculate_mold_risk_score(temp_c, humidity_pct, crop_susceptibility)
    
    if risk_score < 3.0:
        return 999  # Safe conditions
    
    # Base days formula: Higher risk = fewer days
    # Risk 3-5: ~20-30 days
    # Risk 5-7: ~10-15 days
    # Risk 7-9: ~3-7 days
    # Risk 9-10: 1-2 days
    base_days = 30 - (risk_score * 3)
    
    # Apply crop-specific spoilage multiplier
    adjusted_days = base_days / spoilage_multiplier
    
    return max(1, int(adjusted_days))


# ============================================================================
# PREDICTIVE SPOILAGE MODELING
# ============================================================================

def analyze_storage_conditions_with_ai(
    crop: str,
    temp_c: float,
    humidity_pct: float,
    stored_quantity_kg: float,
    harvest_moisture_content: Optional[float] = None,
    days_in_storage: int = 0,
    sensor_history: Optional[List[Dict]] = None
) -> Dict:
    """
    AI-powered storage condition analysis with spoilage prediction.
    
    Args:
        crop: Crop type (maize, beans, potatoes, rice, cassava)
        temp_c: Current temperature (Celsius)
        humidity_pct: Current relative humidity (%)
        stored_quantity_kg: Amount stored (kg)
        harvest_moisture_content: Moisture % at harvest (optional)
        days_in_storage: How long crop has been stored
        sensor_history: Last 24 hours of sensor readings (optional)
    
    Returns:
        {
            "current_risk_score": 7.2,  # 0-10 scale
            "risk_category": "high",  # safe, low, moderate, high, critical
            "days_to_critical": 5,  # Days until spoilage risk
            "spoilage_probability": 0.65,  # 65% chance of mold/spoilage
            "predicted_loss_kg": 45.0,  # Estimated loss if no action
            "predicted_loss_kes": 2025,  # Economic loss
            "mold_risk": {...},  # Mold-specific analysis
            "pest_risk": {...},  # Pest-specific analysis
            "trend": "worsening",  # improving, stable, worsening
            "critical_factors": ["High humidity", "Optimal mold temperature"],
            "ai_confidence": 0.85
        }
    """
    profile = CROP_STORAGE_PROFILES.get(crop)
    if not profile:
        return {"error": f"Unknown crop: {crop}"}
    
    # 1. Mold Risk Analysis
    mold_risk_score = calculate_mold_risk_score(
        temp_c, humidity_pct, profile["mold_susceptibility"]
    )
    days_to_mold = predict_days_to_critical_mold(
        temp_c, humidity_pct, profile["mold_susceptibility"],
        profile["spoilage_rate_multiplier"]
    )
    
    # 2. Pest Risk Analysis
    pest_risks = []
    for pest_name in profile["common_pests"]:
        if pest_name in PEST_LIFE_CYCLES:
            pest_data = PEST_LIFE_CYCLES[pest_name]
            development_stage = calculate_pest_development_stage(
                temp_c, days_in_storage, pest_data
            )
            
            if development_stage >= pest_data["detection_threshold"]:
                days_to_emergence = estimate_days_to_pest_emergence(
                    temp_c, development_stage, pest_data
                )
                pest_risks.append({
                    "pest": pest_name.replace("_", " ").title(),
                    "species": pest_data["species"],
                    "development_stage": round(development_stage * 100, 1),  # %
                    "days_to_emergence": days_to_emergence,
                    "urgency": "high" if days_to_emergence <= 3 else "moderate"
                })
    
    # 3. Combined Risk Score
    pest_risk_score = 0
    if pest_risks:
        # Highest pest risk
        min_days = min(p["days_to_emergence"] for p in pest_risks)
        pest_risk_score = max(0, 10 - min_days)  # 10 if 0 days, 0 if 10+ days
    
    overall_risk = max(mold_risk_score, pest_risk_score)
    
    # 4. Risk Category
    if overall_risk < 3:
        risk_category = "safe"
        spoilage_prob = 0.05
    elif overall_risk < 5:
        risk_category = "low"
        spoilage_prob = 0.15
    elif overall_risk < 7:
        risk_category = "moderate"
        spoilage_prob = 0.35
    elif overall_risk < 9:
        risk_category = "high"
        spoilage_prob = 0.65
    else:
        risk_category = "critical"
        spoilage_prob = 0.90
    
    # 5. Predicted Loss Calculation
    if risk_category in ["high", "critical"]:
        # Loss % increases with time if no action
        loss_percentage = spoilage_prob * (1 + (days_in_storage / 100))
        predicted_loss_kg = stored_quantity_kg * loss_percentage
        predicted_loss_kes = predicted_loss_kg * profile["economic_value_per_kg"]
    else:
        predicted_loss_kg = 0
        predicted_loss_kes = 0
    
    # 6. Trend Analysis (if history available)
    trend = "stable"
    if sensor_history and len(sensor_history) >= 3:
        trend = analyze_storage_trend(sensor_history, profile)
    
    # 7. Critical Factors
    critical_factors = []
    if humidity_pct > profile["critical_humidity"]:
        critical_factors.append(f"Humidity critically high ({humidity_pct}%)")
    if 20 <= temp_c <= 30 and humidity_pct > 70:
        critical_factors.append("Optimal mold growth conditions")
    if harvest_moisture_content and harvest_moisture_content > profile.get("optimal_moisture_content", 14):
        critical_factors.append(f"Wet harvest ({harvest_moisture_content}% moisture)")
    if pest_risks:
        critical_factors.append(f"{len(pest_risks)} pest(s) nearing emergence")
    if temp_c < profile["safe_temp_min"]:
        critical_factors.append("Temperature too low (quality loss)")
    if temp_c > profile["safe_temp_max"]:
        critical_factors.append("Temperature too high (pest activity)")
    
    # 8. AI Confidence (based on data quality)
    confidence = 0.75  # Base confidence
    if sensor_history and len(sensor_history) >= 10:
        confidence += 0.10  # Good historical data
    if harvest_moisture_content is not None:
        confidence += 0.05  # Known moisture content
    if days_in_storage > 0:
        confidence += 0.05  # Storage duration known
    
    return {
        "current_risk_score": round(overall_risk, 1),
        "risk_category": risk_category,
        "days_to_critical": min(days_to_mold, 999),
        "spoilage_probability": round(spoilage_prob, 2),
        "predicted_loss_kg": round(predicted_loss_kg, 1),
        "predicted_loss_kes": int(predicted_loss_kes),
        "mold_risk": {
            "score": round(mold_risk_score, 1),
            "days_to_critical": days_to_mold if days_to_mold < 999 else None,
            "temp_status": "optimal_for_mold" if 20 <= temp_c <= 30 else "suboptimal",
            "humidity_status": "critical" if humidity_pct > profile["critical_humidity"] else "safe"
        },
        "pest_risk": {
            "score": round(pest_risk_score, 1),
            "active_threats": pest_risks,
            "total_pests": len(pest_risks)
        },
        "trend": trend,
        "critical_factors": critical_factors,
        "ai_confidence": round(confidence, 2)
    }


def calculate_pest_development_stage(temp_c: float, days_in_storage: int,
                                       pest_data: Dict) -> float:
    """
    Calculate pest development stage (0.0-1.0) based on temperature and time.
    
    Returns:
        0.0 = just laid eggs
        0.7 = detection threshold (alert farmer)
        1.0 = adult emergence
    """
    # Check mortality thresholds
    if temp_c < pest_data["mortality_temp_min"] or temp_c > pest_data["mortality_temp_max"]:
        return 0.0  # Eggs/larvae die in extreme temps
    
    # Interpolate development days from temperature
    life_cycle = pest_data["egg_to_adult_days"]
    temps = sorted(life_cycle.keys())
    
    if temp_c <= temps[0]:
        days_to_adult = life_cycle[temps[0]]
    elif temp_c >= temps[-1]:
        days_to_adult = life_cycle[temps[-1]]
    else:
        # Linear interpolation
        for i in range(len(temps) - 1):
            if temps[i] <= temp_c <= temps[i + 1]:
                t1, t2 = temps[i], temps[i + 1]
                d1, d2 = life_cycle[t1], life_cycle[t2]
                days_to_adult = d1 + (temp_c - t1) * (d2 - d1) / (t2 - t1)
                break
    
    # Calculate development stage
    development_stage = days_in_storage / days_to_adult
    
    return min(development_stage, 1.0)  # Cap at 1.0


def estimate_days_to_pest_emergence(temp_c: float, current_stage: float,
                                      pest_data: Dict) -> int:
    """
    Estimate days until pest adults emerge.
    """
    life_cycle = pest_data["egg_to_adult_days"]
    temps = sorted(life_cycle.keys())
    
    # Get days to adult at current temp
    if temp_c <= temps[0]:
        days_to_adult = life_cycle[temps[0]]
    elif temp_c >= temps[-1]:
        days_to_adult = life_cycle[temps[-1]]
    else:
        for i in range(len(temps) - 1):
            if temps[i] <= temp_c <= temps[i + 1]:
                t1, t2 = temps[i], temps[i + 1]
                d1, d2 = life_cycle[t1], life_cycle[t2]
                days_to_adult = d1 + (temp_c - t1) * (d2 - d1) / (t2 - t1)
                break
    
    # Remaining days
    remaining_development = 1.0 - current_stage
    days_remaining = int(remaining_development * days_to_adult)
    
    return max(0, days_remaining)


def analyze_storage_trend(sensor_history: List[Dict], profile: Dict) -> str:
    """
    Analyze if storage conditions are improving, stable, or worsening.
    
    Args:
        sensor_history: List of {"temp": float, "humidity": float, "timestamp": str}
        profile: Crop storage profile
    
    Returns:
        "improving", "stable", or "worsening"
    """
    if len(sensor_history) < 3:
        return "stable"
    
    # Calculate risk scores for last 3 readings
    risks = []
    for reading in sensor_history[-3:]:
        risk = calculate_mold_risk_score(
            reading["temp"], reading["humidity"], profile["mold_susceptibility"]
        )
        risks.append(risk)
    
    # Analyze trend
    if risks[-1] < risks[0] - 1.0:
        return "improving"
    elif risks[-1] > risks[0] + 1.0:
        return "worsening"
    else:
        return "stable"


# ============================================================================
# SMART ALERT PRIORITIZATION
# ============================================================================

def prioritize_storage_alert(
    risk_analysis: Dict,
    farmer_alert_history: Optional[List[Dict]] = None,
    time_of_day: Optional[int] = None
) -> Dict:
    """
    AI-powered alert prioritization based on risk severity and farmer behavior.
    
    Args:
        risk_analysis: Output from analyze_storage_conditions_with_ai()
        farmer_alert_history: Past alerts and farmer response
            [{"alert_id": "x", "sent_at": "2025-10-20", "acknowledged": False}, ...]
        time_of_day: Current hour (0-23) for optimal notification timing
    
    Returns:
        {
            "priority": "critical",  # low, medium, high, critical
            "send_immediately": True,
            "notification_type": "sms+push",  # sms, push, sms+push
            "optimal_send_time": "11:00 AM",  # Best time to send (if not immediate)
            "alert_fatigue_risk": 0.3,  # 0-1 (how likely farmer will ignore)
            "reasoning": "Critical mold risk + high economic loss"
        }
    """
    risk_category = risk_analysis["risk_category"]
    risk_score = risk_analysis["current_risk_score"]
    days_to_critical = risk_analysis["days_to_critical"]
    predicted_loss = risk_analysis["predicted_loss_kes"]
    
    # 1. Base Priority from Risk
    if risk_category == "critical":
        priority = "critical"
        send_immediately = True
        notification_type = "sms+push"
    elif risk_category == "high":
        priority = "high"
        send_immediately = days_to_critical <= 3
        notification_type = "sms+push"
    elif risk_category == "moderate":
        priority = "medium"
        send_immediately = False
        notification_type = "push"
    else:
        priority = "low"
        send_immediately = False
        notification_type = "push"
    
    # 2. Economic Loss Adjustment
    if predicted_loss > 5000:  # >5000 KES loss
        priority = "critical" if priority != "critical" else priority
        send_immediately = True
    elif predicted_loss > 2000:
        if priority == "medium":
            priority = "high"
    
    # 3. Alert Fatigue Analysis
    alert_fatigue_risk = 0.0
    if farmer_alert_history:
        recent_alerts = [a for a in farmer_alert_history if _is_recent(a["sent_at"], days=7)]
        if len(recent_alerts) > 5:
            alert_fatigue_risk += 0.3  # Too many alerts recently
        
        # Check acknowledgment rate
        acknowledged = [a for a in recent_alerts if a.get("acknowledged")]
        if recent_alerts and len(acknowledged) / len(recent_alerts) < 0.5:
            alert_fatigue_risk += 0.2  # Farmer ignoring alerts
    
    # Reduce priority if high fatigue risk (unless critical)
    if alert_fatigue_risk > 0.4 and priority != "critical":
        if priority == "high":
            priority = "medium"
        send_immediately = False
    
    # 4. Optimal Send Time (if not immediate)
    if time_of_day is not None and not send_immediately:
        optimal_time = _calculate_optimal_send_time(time_of_day, risk_analysis)
    else:
        optimal_time = None
    
    # 5. Reasoning
    reasons = []
    if risk_category in ["high", "critical"]:
        reasons.append(f"{risk_category.capitalize()} {risk_analysis['mold_risk']['score']} mold risk")
    if days_to_critical <= 5:
        reasons.append(f"Only {days_to_critical} days to critical")
    if predicted_loss > 2000:
        reasons.append(f"High economic loss ({predicted_loss} KES)")
    if risk_analysis["pest_risk"]["total_pests"] > 0:
        reasons.append(f"{risk_analysis['pest_risk']['total_pests']} pest(s) emerging")
    if alert_fatigue_risk > 0.4:
        reasons.append("Alert fatigue detected - reducing frequency")
    
    reasoning = " + ".join(reasons) if reasons else "Routine monitoring"
    
    return {
        "priority": priority,
        "send_immediately": send_immediately,
        "notification_type": notification_type,
        "optimal_send_time": optimal_time,
        "alert_fatigue_risk": round(alert_fatigue_risk, 2),
        "reasoning": reasoning
    }


def _is_recent(date_str: str, days: int) -> bool:
    """Check if date is within last N days."""
    try:
        date = datetime.fromisoformat(date_str.replace("Z", ""))
        return (datetime.now() - date).days <= days
    except:
        return False


def _calculate_optimal_send_time(current_hour: int, risk_analysis: Dict) -> str:
    """
    Calculate best time to send non-urgent alert.
    Avoid early morning (5-7 AM) and late night (10 PM - 5 AM).
    """
    # Optimal farmer availability: 8 AM - 9 PM
    if 8 <= current_hour <= 21:
        return "Now"
    elif current_hour < 8:
        return "8:00 AM"
    else:
        return "8:00 AM (tomorrow)"


# ============================================================================
# AI-OPTIMIZED REMEDIATION STRATEGY
# ============================================================================

def generate_ai_remediation_strategy(
    risk_analysis: Dict,
    crop: str,
    outdoor_weather: Optional[Dict] = None,
    time_of_day: Optional[int] = None,
    storage_method: str = "traditional_crib"
) -> Dict:
    """
    Generate hyper-specific, weather-aware remediation advice.
    
    Args:
        risk_analysis: Output from analyze_storage_conditions_with_ai()
        crop: Crop type
        outdoor_weather: {
            "temp": 24,
            "humidity": 55,
            "forecast_24h": [{"hour": 14, "humidity": 45}, ...]
        }
        time_of_day: Current hour (0-23)
        storage_method: "traditional_crib", "pics_bags", "hermetic_bags"
    
    Returns:
        {
            "primary_action": "Ventilate storage",
            "optimal_action_time": "11:00 AM - 2:00 PM",
            "detailed_steps": ["Open all vents", "Use fan if available", ...],
            "expected_improvement": "Humidity drops to 55% (safe zone)",
            "alternative_if_weather_bad": "Use desiccant packs (200g per 50kg)",
            "urgency_emoji": "⚠️",
            "cost_estimate": "0 KES (free ventilation)",
            "ai_confidence": 0.9
        }
    """
    profile = CROP_STORAGE_PROFILES.get(crop)
    if not profile:
        return {"error": f"Unknown crop: {crop}"}
    
    risk_category = risk_analysis["risk_category"]
    mold_risk = risk_analysis["mold_risk"]
    pest_risk = risk_analysis["pest_risk"]
    
    # Determine primary threat
    if mold_risk["score"] > pest_risk["score"]:
        primary_threat = "mold"
    elif pest_risk["total_pests"] > 0:
        primary_threat = "pest"
    else:
        primary_threat = "none"
    
    # Generate strategy based on threat
    if primary_threat == "mold":
        return _generate_mold_remediation(
            risk_analysis, profile, outdoor_weather, time_of_day, storage_method
        )
    elif primary_threat == "pest":
        return _generate_pest_remediation(
            risk_analysis, profile, pest_risk, storage_method
        )
    else:
        return {
            "primary_action": "Continue monitoring",
            "detailed_steps": ["Check sensors daily", "Maintain current conditions"],
            "expected_improvement": "Conditions stable",
            "urgency_emoji": "✅",
            "cost_estimate": "0 KES",
            "ai_confidence": 0.95
        }


def _generate_mold_remediation(
    risk_analysis: Dict,
    profile: Dict,
    outdoor_weather: Optional[Dict],
    time_of_day: Optional[int],
    storage_method: str
) -> Dict:
    """Generate mold-specific remediation strategy."""
    mold_score = risk_analysis["mold_risk"]["score"]
    days_to_critical = risk_analysis["days_to_critical"]
    
    # Find optimal ventilation window (lowest outdoor humidity)
    if outdoor_weather and "forecast_24h" in outdoor_weather:
        best_window = min(
            outdoor_weather["forecast_24h"],
            key=lambda x: x.get("humidity", 100)
        )
        optimal_time = f"{best_window['hour']}:00"
        outdoor_humidity = best_window["humidity"]
    else:
        optimal_time = "11:00 AM - 2:00 PM"  # Default (usually driest)
        outdoor_humidity = 50  # Assume moderate
    
    # Strategy
    if mold_score >= 7:
        urgency = "🚨"
        primary_action = "URGENT: Ventilate storage immediately"
        steps = [
            f"Open all vents/windows NOW",
            f"Best ventilation window: {optimal_time} (outdoor humidity: {outdoor_humidity}%)",
            "Turn stored crop to aerate",
            "Remove any visibly moldy produce",
            "Consider sun-drying if possible"
        ]
        expected = f"Humidity drops below {profile['critical_humidity']}% within 2-4 hours"
        cost = "0 KES (ventilation)"
        
        if storage_method == "hermetic_bags":
            steps.append("Note: Hermetic bags prevent ventilation - consider temporary opening")
    elif mold_score >= 5:
        urgency = "⚠️"
        primary_action = "Increase ventilation"
        steps = [
            f"Open vents during {optimal_time}",
            "Check outdoor humidity first (open if <indoor humidity)",
            "Inspect for early mold signs",
            "Consider moving to better-ventilated area"
        ]
        expected = f"Humidity stabilizes at safe levels (<{profile['safe_humidity_max']}%)"
        cost = "0 KES"
    else:
        urgency = "⏰"
        primary_action = "Monitor and prepare ventilation"
        steps = [
            "Check sensors every 6 hours",
            f"Prepare to ventilate if humidity rises above {profile['safe_humidity_max']}%"
        ]
        expected = "Early intervention prevents mold"
        cost = "0 KES"
    
    # Alternative (if weather is bad - high outdoor humidity)
    if outdoor_weather and outdoor_weather.get("humidity", 50) > 75:
        alternative = "Outdoor humidity too high - use desiccant packs (200g silica gel per 50kg crop) - Cost: ~500 KES"
    else:
        alternative = None
    
    return {
        "primary_action": primary_action,
        "optimal_action_time": optimal_time,
        "detailed_steps": steps,
        "expected_improvement": expected,
        "alternative_if_weather_bad": alternative,
        "urgency_emoji": urgency,
        "cost_estimate": cost,
        "ai_confidence": 0.85 if outdoor_weather else 0.75
    }


def _generate_pest_remediation(
    risk_analysis: Dict,
    profile: Dict,
    pest_risk: Dict,
    storage_method: str
) -> Dict:
    """Generate pest-specific remediation strategy."""
    pests = pest_risk["active_threats"]
    
    if not pests:
        return {}
    
    # Find most urgent pest
    urgent_pest = min(pests, key=lambda p: p["days_to_emergence"])
    days_left = urgent_pest["days_to_emergence"]
    
    if days_left <= 3:
        urgency = "🐛🚨"
        primary_action = f"URGENT: Prevent {urgent_pest['pest']} emergence"
        steps = [
            f"Adult {urgent_pest['pest']} will emerge in {days_left} days",
            "Option 1: Apply organic pesticide NOW (neem oil, diatomaceous earth)",
            "Option 2: Seal crop in PICS bags (suffocates larvae)",
            "Option 3: Sun-dry crop (kills larvae if <10% moisture)",
            "Inspect weekly for adult pests"
        ]
        cost = "Neem oil: ~300 KES | PICS bags: ~150 KES/bag | Sun-drying: 0 KES"
    elif days_left <= 7:
        urgency = "🐛⚠️"
        primary_action = f"Prepare for {urgent_pest['pest']} emergence"
        steps = [
            f"Larvae at {urgent_pest['development_stage']}% development",
            "Inspect crop for pest entry holes",
            "Prepare PICS bags or hermetic storage",
            "Source organic pesticide (backup plan)"
        ]
        cost = "PICS bags: ~150 KES/bag (recommended)"
    else:
        urgency = "🐛"
        primary_action = "Monitor pest development"
        steps = [
            f"Estimated emergence: {days_left} days",
            "Check storage temperature (higher temp = faster development)",
            "Seal any cracks in storage structure"
        ]
        cost = "0 KES (monitoring)"
    
    return {
        "primary_action": primary_action,
        "optimal_action_time": "Within 24 hours" if days_left <= 3 else "This week",
        "detailed_steps": steps,
        "expected_improvement": "Prevent pest infestation and crop damage",
        "urgency_emoji": urgency,
        "cost_estimate": cost,
        "ai_confidence": 0.80
    }


# ============================================================================
# LOCAL STORAGE STRATEGY (Harvest-Quality-Based Planning)
# ============================================================================

def recommend_storage_strategy_at_harvest(
    crop: str,
    harvest_quantity_kg: float,
    harvest_moisture_content: float,
    harvest_quality: str,  # "excellent", "good", "fair", "poor"
    lcrs_forecast: Dict,  # From climate engine
    farmer_budget: Optional[int] = None
) -> Dict:
    """
    AI-based storage method recommendation at harvest.
    
    Args:
        crop: Crop type
        harvest_quantity_kg: Amount harvested
        harvest_moisture_content: Moisture % at harvest
        harvest_quality: Crop quality assessment
        lcrs_forecast: {"next_3_months": "dry", "rainfall_prob": 0.2, ...}
        farmer_budget: Available budget for storage (KES)
    
    Returns:
        {
            "recommended_method": "pics_bags",
            "reasoning": "High moisture + wet season forecast = mold risk",
            "expected_storage_duration": "4-6 months",
            "estimated_cost": 1500,  # KES
            "alternative_methods": [{...}, {...}],
            "optimal_sell_date": "2025-12-15",
            "sell_reasoning": "Prices peak in December, mold risk increases after that"
        }
    """
    profile = CROP_STORAGE_PROFILES.get(crop)
    if not profile:
        return {"error": f"Unknown crop: {crop}"}
    
    optimal_moisture = profile.get("optimal_moisture_content", 13.5)
    
    # Evaluate harvest condition
    moisture_excess = harvest_moisture_content - optimal_moisture if optimal_moisture else 0
    
    # Risk factors
    high_moisture = moisture_excess > 2  # >2% above optimal
    wet_season_coming = lcrs_forecast.get("next_3_months") in ["wet", "moderate"]
    poor_quality = harvest_quality in ["fair", "poor"]
    
    # Storage method recommendations (ranked)
    methods = []
    
    # 1. PICS Bags (hermetic)
    pics_cost = (harvest_quantity_kg / 50) * 150  # 150 KES per 50kg bag
    methods.append({
        "method": "pics_bags",
        "description": "Hermetic PICS bags (suffocates pests, maintains dryness)",
        "pros": ["Prevents pest infestation (100%)", "Maintains grain quality", "No pesticides needed"],
        "cons": ["Initial cost", "Bags wear out after 2-3 seasons"],
        "cost": int(pics_cost),
        "storage_duration": "6-8 months",
        "suitability_score": 0.9 if high_moisture or wet_season_coming else 0.7
    })
    
    # 2. Traditional Crib (ventilated)
    methods.append({
        "method": "traditional_crib",
        "description": "Open-air crib with good ventilation",
        "pros": ["Low cost", "Good airflow", "Easy monitoring"],
        "cons": ["Pest vulnerable", "Requires pesticides", "Weather-dependent"],
        "cost": 0,  # Already have
        "storage_duration": "3-4 months",
        "suitability_score": 0.8 if not high_moisture and not wet_season_coming else 0.4
    })
    
    # 3. Metal Silos
    silo_cost = (harvest_quantity_kg / 1000) * 15000  # 15,000 KES per ton capacity
    methods.append({
        "method": "metal_silo",
        "description": "Airtight metal silo",
        "pros": ["Long-term storage (12+ months)", "Excellent pest protection", "Reusable"],
        "cons": ["High initial cost", "Requires good drying"],
        "cost": int(silo_cost),
        "storage_duration": "12+ months",
        "suitability_score": 0.9 if harvest_quantity_kg > 500 else 0.5  # Only for large harvests
    })
    
    # Sort by suitability
    methods.sort(key=lambda x: x["suitability_score"], reverse=True)
    
    # Budget filter
    if farmer_budget:
        affordable = [m for m in methods if m["cost"] <= farmer_budget]
        if affordable:
            recommended = affordable[0]
        else:
            recommended = min(methods, key=lambda x: x["cost"])  # Cheapest
    else:
        recommended = methods[0]  # Best suitability
    
    # Reasoning
    reasons = []
    if high_moisture:
        reasons.append(f"Harvest moisture ({harvest_moisture_content}%) above safe level")
    if wet_season_coming:
        reasons.append("Wet season forecast increases mold risk")
    if poor_quality:
        reasons.append("Fair/poor quality requires better preservation")
    
    reasoning = " + ".join(reasons) if reasons else "Standard storage conditions"
    
    # Optimal sell date
    if crop in ["maize", "beans", "rice"]:
        # Prices usually peak 3-4 months post-harvest (scarcity)
        optimal_sell_date = (datetime.now() + timedelta(days=100)).strftime("%Y-%m-%d")
        sell_reasoning = "Prices peak 3-4 months post-harvest when supply is low"
    else:
        optimal_sell_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        sell_reasoning = f"{crop.capitalize()} deteriorates quickly - sell within 1 month"
    
    return {
        "recommended_method": recommended["method"],
        "reasoning": reasoning,
        "expected_storage_duration": recommended["storage_duration"],
        "estimated_cost": recommended["cost"],
        "alternative_methods": methods[1:],  # Other options
        "optimal_sell_date": optimal_sell_date,
        "sell_reasoning": sell_reasoning,
        "ai_confidence": 0.85
    }
