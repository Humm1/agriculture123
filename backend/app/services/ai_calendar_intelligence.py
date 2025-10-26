"""
AI Calendar Intelligence Engine
Dynamic, weather-adjusted calendar with AI-optimized practice timing

Key Features:
1. Dynamic weather-adjusted calendar (continuously adjusts dates)
2. AI-optimized nutrient application timing based on leaching
3. AI-refined harvest predictions from photo tracking
4. Real-time soil moisture index integration
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

# Data directory
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

CALENDAR_ADJUSTMENTS_FILE = DATA_DIR / "ai_calendar_adjustments.json"
PRACTICE_OPTIMIZATIONS_FILE = DATA_DIR / "ai_practice_optimizations.json"


def load_calendar_adjustments() -> Dict:
    """Load AI calendar adjustments"""
    if CALENDAR_ADJUSTMENTS_FILE.exists():
        with open(CALENDAR_ADJUSTMENTS_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_calendar_adjustments(adjustments: Dict):
    """Save AI calendar adjustments"""
    with open(CALENDAR_ADJUSTMENTS_FILE, 'w') as f:
        json.dump(adjustments, f, indent=2)


def load_practice_optimizations() -> Dict:
    """Load practice optimization history"""
    if PRACTICE_OPTIMIZATIONS_FILE.exists():
        with open(PRACTICE_OPTIMIZATIONS_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_practice_optimizations(optimizations: Dict):
    """Save practice optimizations"""
    with open(PRACTICE_OPTIMIZATIONS_FILE, 'w') as f:
        json.dump(optimizations, f, indent=2)


# =============================================================================
# A. DYNAMIC, WEATHER-ADJUSTED CALENDAR
# =============================================================================

def adjust_practice_date_with_weather(
    field_id: str,
    practice_name: str,
    original_date: str,
    current_date: str,
    weather_forecast: Dict,
    soil_moisture_index: Optional[float] = None
) -> Dict:
    """
    AI-powered practice date adjustment based on real-time weather
    
    The AI continuously monitors:
    - Recent rainfall (past 7 days)
    - Temperature trends
    - Soil Moisture Index (SMI) from BLE sensors
    - Weather forecast (next 5 days)
    
    Args:
        field_id: Field identifier
        practice_name: Practice to adjust (e.g., "Weeding - Round 1")
        original_date: Originally scheduled date (ISO format)
        current_date: Current date (ISO format)
        weather_forecast: Weather data from LCRS engine
        soil_moisture_index: Optional SMI from BLE sensor (0-1 scale)
    
    Returns:
        Adjusted date with reasoning
    """
    
    orig_date = datetime.fromisoformat(original_date.replace('Z', ''))
    curr_date = datetime.fromisoformat(current_date.replace('Z', ''))
    
    # =========================================================================
    # STEP 1: Analyze recent weather conditions
    # =========================================================================
    recent_rainfall_mm = weather_forecast.get("rainfall_last_7_days", 0)
    forecast_rainfall_mm = weather_forecast.get("forecast_next_3_days", 0)
    avg_temp = weather_forecast.get("avg_temperature", 25)
    
    # =========================================================================
    # STEP 2: Determine if practice should be adjusted
    # =========================================================================
    adjustment_needed = False
    adjustment_days = 0
    reasons = []
    
    # Practice-specific adjustments
    if "weeding" in practice_name.lower():
        adjustment_needed, adjustment_days, reasons = _adjust_weeding_date(
            orig_date, curr_date, recent_rainfall_mm, forecast_rainfall_mm, soil_moisture_index
        )
    
    elif "fertilizer" in practice_name.lower() or "top-dress" in practice_name.lower():
        adjustment_needed, adjustment_days, reasons = _adjust_fertilizer_date(
            orig_date, curr_date, recent_rainfall_mm, forecast_rainfall_mm, soil_moisture_index
        )
    
    elif "pest scouting" in practice_name.lower():
        adjustment_needed, adjustment_days, reasons = _adjust_pest_scouting_date(
            orig_date, curr_date, avg_temp, recent_rainfall_mm
        )
    
    # =========================================================================
    # STEP 3: Calculate adjusted date
    # =========================================================================
    if adjustment_needed:
        adjusted_date = orig_date + timedelta(days=adjustment_days)
    else:
        adjusted_date = orig_date
    
    # =========================================================================
    # STEP 4: Generate alert
    # =========================================================================
    result = {
        "field_id": field_id,
        "practice_name": practice_name,
        "original_date": original_date,
        "adjusted_date": adjusted_date.isoformat(),
        "adjustment_days": adjustment_days,
        "adjustment_made": adjustment_needed,
        "analyzed_at": datetime.utcnow().isoformat(),
        "reasoning": reasons,
        "weather_context": {
            "recent_rainfall_mm": recent_rainfall_mm,
            "forecast_rainfall_mm": forecast_rainfall_mm,
            "soil_moisture_index": soil_moisture_index or "not_available"
        }
    }
    
    # Save adjustment
    adjustments = load_calendar_adjustments()
    adjustment_id = f"{field_id}_{practice_name.replace(' ', '_')}_{datetime.utcnow().strftime('%Y%m%d')}"
    adjustments[adjustment_id] = result
    save_calendar_adjustments(adjustments)
    
    # Generate farmer alert
    if adjustment_needed:
        result["farmer_alert"] = _generate_adjustment_alert(
            practice_name, orig_date, adjusted_date, reasons
        )
    
    return result


def _adjust_weeding_date(
    orig_date: datetime,
    curr_date: datetime,
    recent_rain: float,
    forecast_rain: float,
    smi: Optional[float]
) -> tuple:
    """Adjust weeding date based on soil workability"""
    
    # If soil is too wet, delay
    if recent_rain > 50:  # Heavy rain in past week
        if forecast_rain > 20:  # More rain coming
            return True, 2, [
                "Heavy rain last week ({}mm)".format(int(recent_rain)),
                "More rain forecast ({}mm in next 3 days)".format(int(forecast_rain)),
                "Soil too wet for weeding - would compact soil",
                "**Action:** Delay 2 days to allow drying"
            ]
    
    # If very dry and weeding overdue, do it now
    days_overdue = (curr_date - orig_date).days
    if days_overdue >= 3 and recent_rain < 10:
        return True, -days_overdue, [
            "Practice overdue by {} days".format(days_overdue),
            "Soil dry enough to work ({}mm recent rain)".format(int(recent_rain)),
            "**Action:** Weed TODAY - weeds are establishing"
        ]
    
    # If rain coming tomorrow and practice due today
    if days_overdue == 0 and forecast_rain > 20:
        return True, -1, [
            "Heavy rain forecast tomorrow ({}mm)".format(int(forecast_rain)),
            "Soil will be too wet after rain",
            "**Action:** Weed TODAY before rain"
        ]
    
    return False, 0, ["No adjustment needed - conditions optimal"]


def _adjust_fertilizer_date(
    orig_date: datetime,
    curr_date: datetime,
    recent_rain: float,
    forecast_rain: float,
    smi: Optional[float]
) -> tuple:
    """
    Adjust fertilizer date to optimize nutrient availability and minimize leaching
    
    Key principle: Apply fertilizer 1-2 days before moderate rain
    - Too much rain = leaching (wasted money)
    - No rain = nutrients not absorbed
    """
    
    days_overdue = (curr_date - orig_date).days
    
    # If heavy rain forecast (>40mm), DELAY to avoid leaching
    if forecast_rain > 40:
        return True, 5, [
            "⚠️ Heavy rain forecast ({}mm)".format(int(forecast_rain)),
            "Risk of nutrient leaching (N and K wash away)",
            "Leaching wastes ~40% of applied fertilizer",
            "**Action:** Wait 5 days until after heavy rains"
        ]
    
    # If moderate rain forecast (15-40mm), apply NOW (ideal)
    if 15 <= forecast_rain <= 40:
        if days_overdue >= -2:  # Within 2 days of schedule
            return True, -days_overdue, [
                "✅ Ideal conditions: Moderate rain forecast ({}mm)".format(int(forecast_rain)),
                "Rain will help nutrients dissolve and reach roots",
                "No leaching risk at this rainfall level",
                "**Action:** Apply fertilizer TODAY for maximum efficiency"
            ]
    
    # If very dry (no rain in 10 days), push back
    if recent_rain < 5 and forecast_rain < 10:
        return True, 3, [
            "Soil very dry (only {}mm recent rain)".format(int(recent_rain)),
            "No rain forecast - nutrients won't dissolve",
            "Fertilizer will sit on surface unused",
            "**Action:** Wait 3 days for rain forecast update"
        ]
    
    # If overdue and conditions acceptable, apply now
    if days_overdue >= 3 and recent_rain > 10:
        return True, -days_overdue, [
            "Fertilizer overdue by {} days".format(days_overdue),
            "Recent rain adequate ({}mm)".format(int(recent_rain)),
            "**Action:** Apply TODAY - crop needs nutrients now"
        ]
    
    return False, 0, ["Timing optimal - apply as scheduled"]


def _adjust_pest_scouting_date(
    orig_date: datetime,
    curr_date: datetime,
    avg_temp: float,
    recent_rain: float
) -> tuple:
    """Adjust pest scouting based on conditions favorable to pests"""
    
    days_overdue = (curr_date - orig_date).days
    
    # Hot and dry = aphid risk
    if avg_temp > 28 and recent_rain < 15:
        return True, -max(days_overdue, 0), [
            "🐛 HIGH PEST RISK: Hot ({}°C) and dry conditions".format(int(avg_temp)),
            "Aphids thrive in hot, dry weather",
            "**Action:** Scout TODAY for early detection"
        ]
    
    # Wet and warm = fungal + caterpillar risk
    if 22 <= avg_temp <= 28 and recent_rain > 30:
        return True, -max(days_overdue, 0), [
            "🐛 HIGH PEST RISK: Warm and wet conditions",
            "Fall armyworm and fungal diseases active",
            "**Action:** Scout TODAY for early signs"
        ]
    
    return False, 0, ["Pest pressure moderate - scout as scheduled"]


def _generate_adjustment_alert(
    practice: str,
    orig_date: datetime,
    adjusted_date: datetime,
    reasons: List[str]
) -> Dict:
    """Generate farmer-friendly adjustment alert"""
    
    days_diff = (adjusted_date - orig_date).days
    
    if days_diff > 0:
        action = "DELAY"
        emoji = "⏸️"
    else:
        action = "ADVANCE"
        emoji = "⏩"
    
    return {
        "title": f"📅 **{practice} - Date {action}ED**",
        "emoji": emoji,
        "original_date": orig_date.strftime("%B %d, %Y"),
        "new_date": adjusted_date.strftime("%B %d, %Y"),
        "days_changed": abs(days_diff),
        "direction": action.lower(),
        "reasons": reasons,
        "urgency": "high" if abs(days_diff) >= 3 else "medium"
    }


# =============================================================================
# B. AI-OPTIMIZED NUTRIENT APPLICATION TIMING
# =============================================================================

def optimize_fertilizer_timing_with_leaching(
    field_id: str,
    fertilizer_type: str,
    scheduled_date: str,
    soil_texture: str,
    recent_rainfall: float,
    forecast_rainfall_5day: List[float]
) -> Dict:
    """
    Optimize fertilizer timing to minimize leaching losses
    
    Leaching risk factors:
    - Nitrogen: Highly mobile, leaches easily in sandy soils
    - Phosphorus: Less mobile, but can leach in acidic soils
    - Potassium: Moderately mobile
    
    Soil texture impact:
    - Sandy soils: High leaching risk (water drains fast)
    - Clay soils: Low leaching risk (water retention high)
    - Loam: Moderate risk
    
    Args:
        field_id: Field identifier
        fertilizer_type: "nitrogen" (CAN, Urea), "phosphorus" (DAP), "potassium" (MOP), "npk"
        scheduled_date: Originally planned date
        soil_texture: "sandy", "loam", "clay"
        recent_rainfall: Past 7 days rainfall (mm)
        forecast_rainfall_5day: Next 5 days rainfall forecast [day1, day2, ...]
    
    Returns:
        Optimized application date with leaching risk analysis
    """
    
    # =========================================================================
    # STEP 1: Calculate leaching risk score
    # =========================================================================
    leaching_risk = _calculate_leaching_risk(
        fertilizer_type, soil_texture, recent_rainfall, forecast_rainfall_5day
    )
    
    # =========================================================================
    # STEP 2: Find optimal application window
    # =========================================================================
    optimal_day = _find_optimal_application_day(
        fertilizer_type, soil_texture, forecast_rainfall_5day
    )
    
    scheduled = datetime.fromisoformat(scheduled_date.replace('Z', ''))
    optimal_date = scheduled + timedelta(days=optimal_day)
    
    # =========================================================================
    # STEP 3: Generate recommendation
    # =========================================================================
    result = {
        "field_id": field_id,
        "fertilizer_type": fertilizer_type,
        "scheduled_date": scheduled_date,
        "optimal_date": optimal_date.isoformat(),
        "days_adjustment": optimal_day,
        "leaching_risk_analysis": leaching_risk,
        "soil_texture": soil_texture,
        "recent_rainfall_mm": recent_rainfall,
        "forecast_rainfall_5day": forecast_rainfall_5day,
        "analyzed_at": datetime.utcnow().isoformat()
    }
    
    # Generate farmer guidance
    result["farmer_guidance"] = _generate_leaching_guidance(
        fertilizer_type, leaching_risk, optimal_day, forecast_rainfall_5day
    )
    
    # Save optimization
    optimizations = load_practice_optimizations()
    opt_id = f"{field_id}_fert_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    optimizations[opt_id] = result
    save_practice_optimizations(optimizations)
    
    return result


def _calculate_leaching_risk(
    fertilizer_type: str,
    soil_texture: str,
    recent_rain: float,
    forecast_rain: List[float]
) -> Dict:
    """Calculate leaching risk score (0-10, where 10 = extreme risk)"""
    
    # Base mobility scores
    mobility = {
        "nitrogen": 9,  # Highly mobile (NO3- ion)
        "phosphorus": 3,  # Low mobility (binds to soil)
        "potassium": 6,  # Moderately mobile (K+ ion)
        "npk": 7  # Average of components
    }
    
    base_risk = mobility.get(fertilizer_type, 5)
    
    # Soil texture multiplier
    texture_multipliers = {
        "sandy": 1.5,  # High leaching
        "loam": 1.0,  # Moderate
        "clay": 0.6  # Low leaching
    }
    soil_multiplier = texture_multipliers.get(soil_texture.lower(), 1.0)
    
    # Recent rainfall impact
    if recent_rain > 100:
        rain_factor = 1.4
    elif recent_rain > 50:
        rain_factor = 1.2
    else:
        rain_factor = 1.0
    
    # Forecast rainfall impact
    total_forecast = sum(forecast_rain)
    if total_forecast > 100:
        forecast_factor = 1.5
    elif total_forecast > 50:
        forecast_factor = 1.3
    else:
        forecast_factor = 1.0
    
    # Calculate composite risk
    risk_score = base_risk * soil_multiplier * rain_factor * forecast_factor
    risk_score = min(10.0, risk_score)
    
    return {
        "risk_score": round(risk_score, 1),
        "risk_level": "extreme" if risk_score >= 8 else ("high" if risk_score >= 6 else ("medium" if risk_score >= 4 else "low")),
        "base_mobility": mobility.get(fertilizer_type, 5),
        "soil_impact": soil_multiplier,
        "recent_rain_impact": rain_factor,
        "forecast_rain_impact": forecast_factor,
        "expected_loss_percent": _estimate_leaching_loss(risk_score)
    }


def _estimate_leaching_loss(risk_score: float) -> int:
    """Estimate percentage of nutrient loss due to leaching"""
    if risk_score >= 8:
        return 60  # Extreme loss
    elif risk_score >= 6:
        return 40  # High loss
    elif risk_score >= 4:
        return 20  # Moderate loss
    return 5  # Minimal loss


def _find_optimal_application_day(
    fertilizer_type: str,
    soil_texture: str,
    forecast_rain: List[float]
) -> int:
    """
    Find optimal day within 5-day window
    Returns: day offset (0 = today, 1 = tomorrow, etc.)
    """
    
    # Ideal: 1-2 days before moderate rain (15-35mm)
    for day in range(len(forecast_rain)):
        if 15 <= forecast_rain[day] <= 35:
            # Check if day before has no heavy rain
            if day == 0 or forecast_rain[day - 1] < 40:
                return max(0, day - 1)  # Apply day before rain
    
    # Avoid: Heavy rain days (>40mm)
    for day in range(len(forecast_rain)):
        if forecast_rain[day] > 40:
            # Push to after heavy rain
            return day + 2
    
    # If all dry, apply on day with lightest rain
    min_rain_day = forecast_rain.index(min(forecast_rain))
    return min_rain_day


def _generate_leaching_guidance(
    fertilizer_type: str,
    leaching_risk: Dict,
    optimal_day: int,
    forecast_rain: List[float]
) -> Dict:
    """Generate farmer-friendly leaching guidance"""
    
    risk_level = leaching_risk["risk_level"]
    expected_loss = leaching_risk["expected_loss_percent"]
    
    if risk_level == "extreme":
        message = f"🚨 **EXTREME LEACHING RISK:** Up to {expected_loss}% of fertilizer may wash away!"
        action = "WAIT {} days before applying - heavy rain will waste your money".format(optimal_day)
        savings = f"Waiting saves ~{int(expected_loss * 0.6)} KES per bag applied"
    
    elif risk_level == "high":
        message = f"⚠️ **HIGH LEACHING RISK:** {expected_loss}% nutrient loss expected"
        if optimal_day > 0:
            action = f"Delay {optimal_day} days for better timing"
        else:
            action = "Apply TODAY before heavy rain"
        savings = f"Proper timing saves ~{int(expected_loss * 0.4)} KES per bag"
    
    elif risk_level == "medium":
        message = f"✅ **MODERATE CONDITIONS:** ~{expected_loss}% loss expected"
        action = "Timing acceptable - apply as planned" if optimal_day == 0 else f"Optimize by waiting {optimal_day} day(s)"
        savings = "Minor efficiency gain possible"
    
    else:
        message = f"✅ **IDEAL CONDITIONS:** <{expected_loss}% loss expected"
        action = "Perfect timing - apply fertilizer now!"
        savings = "Maximum nutrient uptake efficiency"
    
    return {
        "risk_message": message,
        "recommended_action": action,
        "cost_savings": savings,
        "optimal_day_offset": optimal_day,
        "forecast_summary": _summarize_forecast(forecast_rain)
    }


def _summarize_forecast(forecast_rain: List[float]) -> str:
    """Summarize 5-day rainfall forecast"""
    labels = ["Today", "Tomorrow", "Day 3", "Day 4", "Day 5"]
    summary = []
    for i, rain in enumerate(forecast_rain[:5]):
        if rain > 40:
            summary.append(f"{labels[i]}: ⛈️ Heavy ({int(rain)}mm)")
        elif rain > 15:
            summary.append(f"{labels[i]}: 🌧️ Moderate ({int(rain)}mm)")
        elif rain > 5:
            summary.append(f"{labels[i]}: 🌦️ Light ({int(rain)}mm)")
        else:
            summary.append(f"{labels[i]}: ☀️ Dry")
    return " | ".join(summary)


# =============================================================================
# C. AI-REFINED HARVEST WINDOW PREDICTION
# =============================================================================

def refine_harvest_window_with_photos(
    field_id: str,
    original_harvest_date: str,
    actual_growth_scores: List[Dict],
    optimal_growth_curve: List[float],
    crop: str,
    variety: str
) -> Dict:
    """
    Refine harvest window based on actual vs expected growth
    
    Uses weekly photo health scores to determine if crop is:
    - Ahead of schedule (better than expected growth)
    - On schedule (growth matches model)
    - Behind schedule (stressed, growing slowly)
    
    Args:
        field_id: Field identifier
        original_harvest_date: Predicted harvest date from growth model
        actual_growth_scores: List of actual health scores from photos
        optimal_growth_curve: Expected health scores from growth model
        crop: Crop type
        variety: Variety name
    
    Returns:
        Refined harvest window with adjustment reasoning
    """
    
    # =========================================================================
    # STEP 1: Calculate growth deviation
    # =========================================================================
    deviation_analysis = _analyze_growth_deviation(
        actual_growth_scores, optimal_growth_curve
    )
    
    # =========================================================================
    # STEP 2: Determine harvest adjustment
    # =========================================================================
    days_adjustment = _calculate_harvest_adjustment(
        deviation_analysis, crop, variety
    )
    
    orig_date = datetime.fromisoformat(original_harvest_date.replace('Z', ''))
    adjusted_start = orig_date + timedelta(days=days_adjustment)
    adjusted_end = adjusted_start + timedelta(days=7)  # 7-day harvest window
    
    # =========================================================================
    # STEP 3: Generate refined harvest window
    # =========================================================================
    result = {
        "field_id": field_id,
        "original_harvest_date": original_harvest_date,
        "refined_harvest_window": {
            "start_date": adjusted_start.isoformat(),
            "end_date": adjusted_end.isoformat(),
            "optimal_date": (adjusted_start + timedelta(days=3)).isoformat()
        },
        "days_adjustment": days_adjustment,
        "growth_deviation_analysis": deviation_analysis,
        "analyzed_at": datetime.utcnow().isoformat()
    }
    
    # Generate farmer notification
    result["farmer_notification"] = _generate_harvest_adjustment_alert(
        crop, orig_date, adjusted_start, days_adjustment, deviation_analysis
    )
    
    return result


def _analyze_growth_deviation(
    actual_scores: List[Dict],
    optimal_curve: List[float]
) -> Dict:
    """Analyze how actual growth deviates from optimal"""
    
    if len(actual_scores) == 0:
        return {
            "status": "no_data",
            "message": "No photo data available for analysis"
        }
    
    # Calculate average deviation
    deviations = []
    for score_data in actual_scores:
        day = score_data.get("days_after_planting", 0)
        actual_score = score_data.get("health_score", 5)
        
        # Find corresponding optimal score
        if day < len(optimal_curve):
            expected_score = optimal_curve[day]
            deviation = actual_score - expected_score
            deviations.append(deviation)
    
    if len(deviations) == 0:
        return {"status": "insufficient_data"}
    
    avg_deviation = sum(deviations) / len(deviations)
    recent_deviation = sum(deviations[-3:]) / min(3, len(deviations))  # Last 3 weeks
    
    # Classify growth status
    if avg_deviation >= 1.0:
        status = "ahead_of_schedule"
        description = "Crop growing faster than expected (excellent conditions)"
    elif avg_deviation >= -0.5:
        status = "on_schedule"
        description = "Crop growing as expected (normal development)"
    elif avg_deviation >= -1.5:
        status = "slightly_behind"
        description = "Crop slightly stressed (minor delays expected)"
    else:
        status = "significantly_behind"
        description = "Crop significantly stressed (major delays expected)"
    
    return {
        "status": status,
        "description": description,
        "average_deviation": round(avg_deviation, 2),
        "recent_deviation": round(recent_deviation, 2),
        "trend": "improving" if recent_deviation > avg_deviation else ("stable" if abs(recent_deviation - avg_deviation) < 0.3 else "declining"),
        "data_points": len(deviations)
    }


def _calculate_harvest_adjustment(
    deviation: Dict,
    crop: str,
    variety: str
) -> int:
    """Calculate days to adjust harvest window"""
    
    status = deviation.get("status")
    avg_dev = deviation.get("average_deviation", 0)
    
    if status == "ahead_of_schedule":
        # Harvest earlier (crop maturing faster)
        return -5
    
    elif status == "on_schedule":
        # No adjustment
        return 0
    
    elif status == "slightly_behind":
        # Extend window by 5 days
        return 5
    
    elif status == "significantly_behind":
        # Extend window by 10-14 days
        if avg_dev < -2.0:
            return 14
        return 10
    
    return 0


def _generate_harvest_adjustment_alert(
    crop: str,
    orig_date: datetime,
    adjusted_date: datetime,
    days_adjustment: int,
    deviation: Dict
) -> Dict:
    """Generate farmer-friendly harvest adjustment alert"""
    
    if days_adjustment > 0:
        action = "DELAYED"
        emoji = "⏳"
        message = f"Your {crop} harvest is now predicted **{days_adjustment} days later** than originally planned."
    elif days_adjustment < 0:
        action = "ADVANCED"
        emoji = "🎉"
        message = f"Good news! Your {crop} is maturing faster. Harvest **{abs(days_adjustment)} days earlier**."
    else:
        action = "UNCHANGED"
        emoji = "✅"
        message = f"Your {crop} is developing perfectly on schedule."
    
    return {
        "title": f"{emoji} **Harvest Window {action}**",
        "message": message,
        "original_date": orig_date.strftime("%B %d, %Y"),
        "new_date": adjusted_date.strftime("%B %d, %Y"),
        "reason": deviation.get("description", ""),
        "trend": deviation.get("trend", "stable"),
        "action_required": "Plan harvest activities for new date" if days_adjustment != 0 else "Continue as planned"
    }
