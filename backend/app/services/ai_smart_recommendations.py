"""
AI Smart Recommendations Engine (The "Advisor")
===============================================

This module implements AI-powered personalized recommendations for farmers:

1. **Dynamic Calendar Optimization:**
   - Real-time analysis of LCRS (Climate Risk Score) + SMI (Soil Moisture Index)
   - Simulates yield outcomes to find optimal planting window
   - Provides % yield improvement vs. alternative dates

2. **AI-Driven Financial Risk Scenarios:**
   - Integrates crop price volatility + predicted yield risk
   - Calculates net profit predictions for each crop option
   - Presents risk-adjusted recommendations (high profit vs. low risk)

3. **AI-Personalized Micro-Action Alerts:**
   - Customizes advice based on farmer's growth stage + historical actions
   - Learns from farmer behavior (e.g., mulching frequency, fertilizer preference)
   - Delivers highly relevant, context-specific alerts

Core Innovation:
- Moves from generic advice to optimized financial scenarios
- Maximizes profit while managing downside risk
- Adapts recommendations to individual farmer practices

Author: AgroShield AI Team
Date: October 2025
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import math


# ============================================================================
# CROP YIELD MODELS & MARKET DATA
# ============================================================================

CROP_YIELD_MODELS = {
    "maize": {
        "base_yield_kg_per_acre": 2500,
        "optimal_planting_window": {
            "start_day": -10,  # Days before long rains
            "end_day": 10,  # Days after long rains start
            "peak_day": 0  # Optimal = exactly when rains start
        },
        "water_stress_sensitivity": 0.8,  # 0-1 (1 = very sensitive)
        "temperature_sensitivity": 0.6,
        "growth_days": 120,
        "critical_water_periods": ["flowering", "grain_filling"]  # Days 60-90
    },
    "potato": {
        "base_yield_kg_per_acre": 8000,
        "optimal_planting_window": {
            "start_day": -5,
            "end_day": 15,
            "peak_day": 5
        },
        "water_stress_sensitivity": 0.9,
        "temperature_sensitivity": 0.7,
        "growth_days": 90,
        "critical_water_periods": ["tuber_formation", "tuber_bulking"]  # Days 30-70
    },
    "beans": {
        "base_yield_kg_per_acre": 800,
        "optimal_planting_window": {
            "start_day": 0,
            "end_day": 20,
            "peak_day": 10
        },
        "water_stress_sensitivity": 0.7,
        "temperature_sensitivity": 0.5,
        "growth_days": 75,
        "critical_water_periods": ["flowering", "pod_filling"]  # Days 40-60
    },
    "tomato": {
        "base_yield_kg_per_acre": 12000,
        "optimal_planting_window": {
            "start_day": -15,
            "end_day": 10,
            "peak_day": -5
        },
        "water_stress_sensitivity": 0.85,
        "temperature_sensitivity": 0.8,
        "growth_days": 90,
        "critical_water_periods": ["flowering", "fruit_development"]  # Days 45-75
    },
    "cabbage": {
        "base_yield_kg_per_acre": 15000,
        "optimal_planting_window": {
            "start_day": -10,
            "end_day": 15,
            "peak_day": 5
        },
        "water_stress_sensitivity": 0.75,
        "temperature_sensitivity": 0.6,
        "growth_days": 75,
        "critical_water_periods": ["head_formation"]  # Days 40-65
    },
    "sorghum": {
        "base_yield_kg_per_acre": 2000,
        "optimal_planting_window": {
            "start_day": -5,
            "end_day": 20,
            "peak_day": 10
        },
        "water_stress_sensitivity": 0.4,  # Drought tolerant
        "temperature_sensitivity": 0.3,
        "growth_days": 110,
        "critical_water_periods": ["flowering"]  # Days 60-75
    }
}


MARKET_PRICE_DATA = {
    "maize": {
        "current_price_kes_per_kg": 50,
        "price_volatility": 0.25,  # 25% price fluctuation
        "seasonal_price_multiplier": {
            "harvest_season": 0.7,  # Low prices (supply glut)
            "planting_season": 1.0,
            "lean_season": 1.3  # High prices (low supply)
        },
        "production_cost_kes_per_acre": 15000
    },
    "potato": {
        "current_price_kes_per_kg": 45,
        "price_volatility": 0.30,
        "seasonal_price_multiplier": {
            "harvest_season": 0.65,
            "planting_season": 1.0,
            "lean_season": 1.4
        },
        "production_cost_kes_per_acre": 35000
    },
    "beans": {
        "current_price_kes_per_kg": 120,
        "price_volatility": 0.20,
        "seasonal_price_multiplier": {
            "harvest_season": 0.75,
            "planting_season": 1.0,
            "lean_season": 1.25
        },
        "production_cost_kes_per_acre": 12000
    },
    "tomato": {
        "current_price_kes_per_kg": 60,
        "price_volatility": 0.40,  # High volatility
        "seasonal_price_multiplier": {
            "harvest_season": 0.5,  # Prices crash at harvest
            "planting_season": 1.0,
            "lean_season": 1.6
        },
        "production_cost_kes_per_acre": 45000
    },
    "cabbage": {
        "current_price_kes_per_kg": 30,
        "price_volatility": 0.35,
        "seasonal_price_multiplier": {
            "harvest_season": 0.6,
            "planting_season": 1.0,
            "lean_season": 1.5
        },
        "production_cost_kes_per_acre": 25000
    },
    "sorghum": {
        "current_price_kes_per_kg": 55,
        "price_volatility": 0.15,  # Stable prices
        "seasonal_price_multiplier": {
            "harvest_season": 0.8,
            "planting_season": 1.0,
            "lean_season": 1.2
        },
        "production_cost_kes_per_acre": 12000
    }
}


# ============================================================================
# FARMER HISTORICAL BEHAVIOR TRACKING
# ============================================================================

# Track farmer practices for personalization
FARMER_PRACTICE_PROFILES = {}


def update_farmer_practice_profile(farmer_id: str, action: str, context: Dict):
    """
    Track farmer actions to build personalized recommendations.
    
    Args:
        farmer_id: Farmer identifier
        action: Action type (e.g., "fertilizer_application", "mulching", "irrigation")
        context: Action context (crop, date, quantity, etc.)
    """
    if farmer_id not in FARMER_PRACTICE_PROFILES:
        FARMER_PRACTICE_PROFILES[farmer_id] = {
            "fertilizer_preference": "unknown",  # chemical/organic/mixed
            "mulching_frequency": "unknown",  # never/sometimes/always
            "irrigation_access": "unknown",  # none/manual/automatic
            "risk_tolerance": "medium",  # low/medium/high
            "action_history": []
        }
    
    profile = FARMER_PRACTICE_PROFILES[farmer_id]
    profile["action_history"].append({
        "action": action,
        "context": context,
        "timestamp": datetime.now().isoformat()
    })
    
    # Infer preferences from actions
    _infer_farmer_preferences(farmer_id)


def _infer_farmer_preferences(farmer_id: str):
    """Infer farmer preferences from historical actions."""
    profile = FARMER_PRACTICE_PROFILES[farmer_id]
    history = profile["action_history"]
    
    if len(history) < 3:
        return  # Not enough data
    
    # Analyze fertilizer preference
    fertilizer_actions = [a for a in history if a["action"] == "fertilizer_application"]
    if len(fertilizer_actions) >= 2:
        organic_count = sum(1 for a in fertilizer_actions if "organic" in a["context"].get("type", ""))
        chemical_count = len(fertilizer_actions) - organic_count
        
        if organic_count > chemical_count * 2:
            profile["fertilizer_preference"] = "organic"
        elif chemical_count > organic_count * 2:
            profile["fertilizer_preference"] = "chemical"
        else:
            profile["fertilizer_preference"] = "mixed"
    
    # Analyze mulching frequency
    mulching_actions = [a for a in history if a["action"] == "mulching"]
    if len(mulching_actions) >= 2:
        profile["mulching_frequency"] = "always" if len(mulching_actions) >= 3 else "sometimes"
    elif len(history) >= 5 and len(mulching_actions) == 0:
        profile["mulching_frequency"] = "never"
    
    # Analyze irrigation access
    irrigation_actions = [a for a in history if a["action"] == "irrigation"]
    if len(irrigation_actions) >= 1:
        profile["irrigation_access"] = "manual" if len(irrigation_actions) < 5 else "automatic"
    elif len(history) >= 5 and len(irrigation_actions) == 0:
        profile["irrigation_access"] = "none"


# ============================================================================
# DYNAMIC CALENDAR OPTIMIZATION
# ============================================================================

def optimize_planting_window(
    crop: str,
    lat: float,
    lon: float,
    field_id: str,
    current_date: Optional[datetime] = None,
    lcrs: Optional[float] = None,
    smi: Optional[float] = None,
    micro_climate_forecast: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    AI-powered dynamic planting window optimization.
    
    Simulates yield outcomes for different planting dates to find optimal window.
    
    Args:
        crop: Crop type (e.g., "maize", "potato")
        lat: Farm latitude
        lon: Farm longitude
        field_id: Field identifier
        current_date: Reference date (default: today)
        lcrs: Long-term Climate Risk Score (0-10)
        smi: Soil Moisture Index (0-10)
        micro_climate_forecast: 30-day weather forecast
    
    Returns:
        dict: Optimal planting recommendation with yield projections
    """
    if current_date is None:
        current_date = datetime.now()
    
    if crop not in CROP_YIELD_MODELS:
        return {"error": f"Crop '{crop}' not supported"}
    
    crop_model = CROP_YIELD_MODELS[crop]
    
    # Get weather forecast (simulate if not provided)
    if micro_climate_forecast is None:
        from app.services.ai_hyperlocal_prediction import synthesize_micro_climate_forecast
        micro_climate_forecast = synthesize_micro_climate_forecast(lat, lon, forecast_days=30)
    
    # Get current LCRS and SMI (simulate if not provided)
    if lcrs is None:
        lcrs = _simulate_lcrs(lat, lon)
    if smi is None:
        from app.services import persistence
        smi = persistence.get_soil_moisture_index(field_id)
    
    # Simulate yield for planting dates from -10 to +20 days
    planting_scenarios = []
    
    for days_offset in range(-10, 21):
        planting_date = current_date + timedelta(days=days_offset)
        
        # Simulate yield for this planting date
        yield_prediction = _simulate_crop_yield(
            crop, crop_model, planting_date, micro_climate_forecast, lcrs, smi
        )
        
        planting_scenarios.append({
            "planting_date": planting_date.strftime("%Y-%m-%d"),
            "days_from_today": days_offset,
            "predicted_yield_kg": yield_prediction["yield_kg"],
            "yield_vs_optimal_percent": yield_prediction["yield_vs_optimal_percent"],
            "risk_factors": yield_prediction["risk_factors"],
            "confidence": yield_prediction["confidence"]
        })
    
    # Find optimal planting date
    optimal_scenario = max(planting_scenarios, key=lambda x: x["predicted_yield_kg"])
    today_scenario = next(s for s in planting_scenarios if s["days_from_today"] == 0)
    
    # Calculate opportunity cost of waiting
    yield_improvement_waiting = optimal_scenario["predicted_yield_kg"] - today_scenario["predicted_yield_kg"]
    yield_improvement_percent = (yield_improvement_waiting / today_scenario["predicted_yield_kg"]) * 100
    
    return {
        "crop": crop,
        "location": {"lat": lat, "lon": lon},
        "current_date": current_date.strftime("%Y-%m-%d"),
        "optimal_planting_date": optimal_scenario["planting_date"],
        "days_until_optimal": optimal_scenario["days_from_today"],
        "recommendation": _generate_planting_recommendation(
            optimal_scenario, today_scenario, yield_improvement_percent
        ),
        "planting_today": today_scenario,
        "planting_optimal": optimal_scenario,
        "yield_improvement_if_wait": {
            "kg_per_acre": round(yield_improvement_waiting, 0),
            "percent": round(yield_improvement_percent, 1)
        },
        "all_scenarios": planting_scenarios,
        "environmental_conditions": {
            "lcrs": lcrs,
            "smi": smi,
            "current_weather": micro_climate_forecast["forecast"][0]
        },
        "ai_confidence": optimal_scenario["confidence"]
    }


def _simulate_crop_yield(
    crop: str,
    crop_model: Dict,
    planting_date: datetime,
    micro_climate_forecast: Dict,
    lcrs: float,
    smi: float
) -> Dict[str, Any]:
    """
    Simulate crop yield based on planting date and environmental conditions.
    
    Returns:
        dict: Yield prediction with risk factors and confidence
    """
    base_yield = crop_model["base_yield_kg_per_acre"]
    growth_days = crop_model["growth_days"]
    
    # Calculate days from optimal planting window
    # Assume optimal = day 0 of forecast (today)
    days_from_optimal = (planting_date - datetime.now()).days
    optimal_window = crop_model["optimal_planting_window"]
    
    # Penalty for planting outside optimal window
    if optimal_window["start_day"] <= days_from_optimal <= optimal_window["end_day"]:
        # Within optimal window
        distance_from_peak = abs(days_from_optimal - optimal_window["peak_day"])
        window_penalty = 1.0 - (distance_from_peak / 20) * 0.2  # Max 20% penalty
    else:
        # Outside optimal window
        if days_from_optimal < optimal_window["start_day"]:
            distance_outside = optimal_window["start_day"] - days_from_optimal
        else:
            distance_outside = days_from_optimal - optimal_window["end_day"]
        
        window_penalty = max(0.5, 1.0 - (distance_outside / 10) * 0.5)  # Max 50% penalty
    
    # Analyze weather during growth period
    forecast_days = micro_climate_forecast.get("forecast", [])
    weather_penalty = _calculate_weather_penalty(
        crop_model, forecast_days, days_from_optimal, growth_days
    )
    
    # Climate risk penalty (LCRS)
    lcrs_penalty = 1.0 - (lcrs / 20)  # LCRS 10 = 50% penalty, LCRS 0 = no penalty
    
    # Soil moisture penalty
    optimal_smi = 7.0
    smi_penalty = 1.0 - (abs(smi - optimal_smi) / 20)  # Max 50% penalty
    
    # Calculate final yield
    final_yield = base_yield * window_penalty * weather_penalty * lcrs_penalty * smi_penalty
    
    # Yield vs. optimal (100% = perfect conditions)
    yield_vs_optimal = (final_yield / base_yield) * 100
    
    # Identify risk factors
    risk_factors = []
    if window_penalty < 0.9:
        risk_factors.append(f"Outside optimal planting window ({round((1-window_penalty)*100)}% penalty)")
    if weather_penalty < 0.9:
        risk_factors.append(f"Unfavorable weather forecast ({round((1-weather_penalty)*100)}% penalty)")
    if lcrs_penalty < 0.9:
        risk_factors.append(f"High climate risk (LCRS: {lcrs:.1f})")
    if smi_penalty < 0.9:
        risk_factors.append(f"Suboptimal soil moisture (SMI: {smi:.1f})")
    
    # Confidence based on data quality
    forecast_confidence = micro_climate_forecast.get("model_confidence", 0.75)
    confidence = min(forecast_confidence, 0.90)
    
    return {
        "yield_kg": round(final_yield, 0),
        "yield_vs_optimal_percent": round(yield_vs_optimal, 1),
        "risk_factors": risk_factors,
        "confidence": confidence,
        "penalties": {
            "planting_window": round(window_penalty, 2),
            "weather": round(weather_penalty, 2),
            "climate_risk": round(lcrs_penalty, 2),
            "soil_moisture": round(smi_penalty, 2)
        }
    }


def _calculate_weather_penalty(
    crop_model: Dict,
    forecast_days: List[Dict],
    planting_offset: int,
    growth_days: int
) -> float:
    """
    Calculate yield penalty based on weather forecast during growth period.
    
    Args:
        crop_model: Crop yield model
        forecast_days: Weather forecast
        planting_offset: Days from today to planting
        growth_days: Crop growth duration
    
    Returns:
        float: Weather penalty (0-1, where 1 = perfect weather)
    """
    water_stress_sensitivity = crop_model["water_stress_sensitivity"]
    temp_sensitivity = crop_model["temperature_sensitivity"]
    
    # Extract relevant forecast period
    start_idx = max(0, planting_offset)
    end_idx = min(len(forecast_days), planting_offset + growth_days)
    
    if start_idx >= len(forecast_days):
        # Beyond forecast range (low confidence)
        return 0.70
    
    growth_forecast = forecast_days[start_idx:end_idx]
    
    if not growth_forecast:
        return 0.70
    
    # Analyze water stress
    total_rainfall = sum(day.get("rainfall_mm", 0) for day in growth_forecast)
    optimal_rainfall = growth_days * 3  # ~3mm per day optimal
    
    if total_rainfall < optimal_rainfall * 0.5:
        water_penalty = 1.0 - (water_stress_sensitivity * 0.4)  # Up to 40% penalty
    elif total_rainfall < optimal_rainfall * 0.75:
        water_penalty = 1.0 - (water_stress_sensitivity * 0.2)
    else:
        water_penalty = 1.0
    
    # Analyze temperature stress
    avg_temp = sum(day.get("temperature", 22) for day in growth_forecast) / len(growth_forecast)
    
    if avg_temp < 15 or avg_temp > 35:
        temp_penalty = 1.0 - (temp_sensitivity * 0.3)  # Up to 30% penalty
    elif avg_temp < 18 or avg_temp > 30:
        temp_penalty = 1.0 - (temp_sensitivity * 0.15)
    else:
        temp_penalty = 1.0
    
    return water_penalty * temp_penalty


def _generate_planting_recommendation(
    optimal_scenario: Dict,
    today_scenario: Dict,
    yield_improvement_percent: float
) -> str:
    """Generate human-readable planting recommendation."""
    if optimal_scenario["days_from_today"] == 0:
        return f"✅ **PLANT TODAY:** Conditions are optimal. Predicted yield: {optimal_scenario['predicted_yield_kg']:.0f} kg/acre."
    
    elif optimal_scenario["days_from_today"] > 0 and yield_improvement_percent >= 10:
        return f"⏳ **WAIT {optimal_scenario['days_from_today']} DAYS:** Delaying planting increases yield by {yield_improvement_percent:.1f}% ({optimal_scenario['predicted_yield_kg'] - today_scenario['predicted_yield_kg']:.0f} kg more)."
    
    elif optimal_scenario["days_from_today"] > 0 and yield_improvement_percent >= 5:
        return f"⚖️ **SLIGHT ADVANTAGE TO WAIT:** Waiting {optimal_scenario['days_from_today']} days improves yield by {yield_improvement_percent:.1f}%, but planting today is also acceptable."
    
    elif optimal_scenario["days_from_today"] < 0:
        return f"⚠️ **OPTIMAL WINDOW PASSED:** Best planting date was {abs(optimal_scenario['days_from_today'])} days ago. Plant as soon as possible to minimize losses."
    
    else:
        return f"✅ **PLANT NOW:** Minimal difference between now and optimal date. Current conditions are good."


# ============================================================================
# AI-DRIVEN FINANCIAL RISK SCENARIOS
# ============================================================================

def generate_financial_risk_scenarios(
    crops: List[str],
    lat: float,
    lon: float,
    field_size_acres: float,
    farmer_id: Optional[str] = None,
    lcrs: Optional[float] = None
) -> Dict[str, Any]:
    """
    Generate financial risk scenarios for multiple crop options.
    
    Integrates crop price volatility + predicted yield risk to calculate
    risk-adjusted net profit for each crop.
    
    Args:
        crops: List of crop options to compare (e.g., ["maize", "sorghum", "beans"])
        lat: Farm latitude
        lon: Farm longitude
        field_size_acres: Field size in acres
        farmer_id: Farmer identifier (optional, for personalization)
        lcrs: Long-term Climate Risk Score (0-10)
    
    Returns:
        dict: Financial scenarios for each crop with risk/profit analysis
    """
    if lcrs is None:
        lcrs = _simulate_lcrs(lat, lon)
    
    scenarios = []
    
    for crop in crops:
        if crop not in CROP_YIELD_MODELS or crop not in MARKET_PRICE_DATA:
            continue
        
        crop_model = CROP_YIELD_MODELS[crop]
        market_data = MARKET_PRICE_DATA[crop]
        
        # Predict yield
        base_yield = crop_model["base_yield_kg_per_acre"]
        climate_risk_factor = 1.0 - (lcrs / 20)  # LCRS 10 = 50% reduction
        predicted_yield = base_yield * climate_risk_factor * field_size_acres
        
        # Calculate yield risk (probability of failure)
        yield_risk_percent = _calculate_yield_risk(crop_model, lcrs)
        
        # Predict market price at harvest
        harvest_date = datetime.now() + timedelta(days=crop_model["growth_days"])
        harvest_season = _determine_season(harvest_date)
        price_multiplier = market_data["seasonal_price_multiplier"][harvest_season]
        predicted_price = market_data["current_price_kes_per_kg"] * price_multiplier
        
        # Calculate price risk (volatility)
        price_volatility = market_data["price_volatility"]
        price_risk_range = {
            "min": predicted_price * (1 - price_volatility),
            "max": predicted_price * (1 + price_volatility)
        }
        
        # Calculate gross revenue
        gross_revenue = predicted_yield * predicted_price
        
        # Calculate production costs
        production_cost = market_data["production_cost_kes_per_acre"] * field_size_acres
        
        # Calculate net profit
        net_profit = gross_revenue - production_cost
        
        # Calculate worst-case scenario (high yield risk + low price)
        worst_case_yield = predicted_yield * (1 - yield_risk_percent / 100)
        worst_case_price = price_risk_range["min"]
        worst_case_profit = (worst_case_yield * worst_case_price) - production_cost
        
        # Calculate best-case scenario (optimal yield + high price)
        best_case_yield = predicted_yield * 1.2  # 20% above prediction
        best_case_price = price_risk_range["max"]
        best_case_profit = (best_case_yield * best_case_price) - production_cost
        
        # Overall risk score
        combined_risk = (yield_risk_percent + (price_volatility * 100)) / 2
        
        scenarios.append({
            "crop": crop,
            "predicted_yield_kg": round(predicted_yield, 0),
            "yield_risk_percent": round(yield_risk_percent, 1),
            "predicted_price_kes_per_kg": round(predicted_price, 2),
            "price_volatility_percent": round(price_volatility * 100, 1),
            "gross_revenue_kes": round(gross_revenue, 0),
            "production_cost_kes": round(production_cost, 0),
            "net_profit_kes": round(net_profit, 0),
            "profit_scenarios": {
                "best_case": round(best_case_profit, 0),
                "expected": round(net_profit, 0),
                "worst_case": round(worst_case_profit, 0)
            },
            "risk_score": round(combined_risk, 1),
            "risk_category": _categorize_risk(combined_risk),
            "recommendation_score": _calculate_recommendation_score(
                net_profit, combined_risk, farmer_id
            )
        })
    
    # Sort by recommendation score (highest first)
    scenarios.sort(key=lambda x: x["recommendation_score"], reverse=True)
    
    # Generate comparison summary
    best_profit = max(scenarios, key=lambda x: x["net_profit_kes"])
    lowest_risk = min(scenarios, key=lambda x: x["risk_score"])
    
    return {
        "location": {"lat": lat, "lon": lon},
        "field_size_acres": field_size_acres,
        "climate_risk_score": lcrs,
        "scenarios": scenarios,
        "summary": {
            "highest_profit": {
                "crop": best_profit["crop"],
                "net_profit_kes": best_profit["net_profit_kes"],
                "risk_score": best_profit["risk_score"]
            },
            "lowest_risk": {
                "crop": lowest_risk["crop"],
                "net_profit_kes": lowest_risk["net_profit_kes"],
                "risk_score": lowest_risk["risk_score"]
            },
            "recommended": {
                "crop": scenarios[0]["crop"],
                "net_profit_kes": scenarios[0]["net_profit_kes"],
                "risk_score": scenarios[0]["risk_score"],
                "reasoning": _generate_recommendation_reasoning(scenarios[0], best_profit, lowest_risk)
            }
        },
        "generated_at": datetime.now().isoformat()
    }


def _calculate_yield_risk(crop_model: Dict, lcrs: float) -> float:
    """
    Calculate probability of crop failure based on climate risk and crop sensitivity.
    
    Returns:
        float: Yield risk percentage (0-100)
    """
    water_sensitivity = crop_model["water_stress_sensitivity"]
    
    # Base risk from LCRS
    base_risk = lcrs * 5  # LCRS 10 = 50% risk
    
    # Adjust by crop sensitivity
    adjusted_risk = base_risk * (0.5 + water_sensitivity * 0.5)
    
    return min(adjusted_risk, 80)  # Cap at 80%


def _calculate_recommendation_score(
    net_profit: float,
    risk_score: float,
    farmer_id: Optional[str]
) -> float:
    """
    Calculate recommendation score balancing profit and risk.
    
    Considers farmer's risk tolerance if available.
    
    Returns:
        float: Recommendation score (0-100)
    """
    # Normalize profit (assume 0-200,000 KES range)
    profit_score = min(net_profit / 2000, 100)
    
    # Risk penalty
    risk_penalty = risk_score
    
    # Get farmer risk tolerance
    if farmer_id and farmer_id in FARMER_PRACTICE_PROFILES:
        risk_tolerance = FARMER_PRACTICE_PROFILES[farmer_id]["risk_tolerance"]
        if risk_tolerance == "high":
            risk_weight = 0.3  # High risk tolerance = less penalty
        elif risk_tolerance == "low":
            risk_weight = 0.7  # Low risk tolerance = more penalty
        else:
            risk_weight = 0.5  # Medium
    else:
        risk_weight = 0.5
    
    # Combined score
    score = profit_score * (1 - risk_weight) + (100 - risk_penalty) * risk_weight
    
    return round(score, 1)


def _generate_recommendation_reasoning(
    recommended: Dict,
    best_profit: Dict,
    lowest_risk: Dict
) -> str:
    """Generate human-readable reasoning for recommendation."""
    if recommended["crop"] == best_profit["crop"]:
        return f"Highest profit potential ({recommended['net_profit_kes']:,.0f} KES) with acceptable risk ({recommended['risk_score']:.1f}%)."
    elif recommended["crop"] == lowest_risk["crop"]:
        return f"Lowest risk ({recommended['risk_score']:.1f}%) with good profit ({recommended['net_profit_kes']:,.0f} KES). Safe option."
    else:
        return f"Best balance of profit ({recommended['net_profit_kes']:,.0f} KES) and risk ({recommended['risk_score']:.1f}%)."


# ============================================================================
# AI-PERSONALIZED MICRO-ACTION ALERTS
# ============================================================================

def generate_personalized_alert(
    farmer_id: str,
    crop: str,
    crop_stage: str,
    days_since_planting: int,
    current_weather: Dict,
    smi: float,
    alert_type: str
) -> Dict[str, Any]:
    """
    Generate AI-personalized micro-action alert based on farmer's historical practices.
    
    Args:
        farmer_id: Farmer identifier
        crop: Crop type
        crop_stage: Current growth stage (e.g., "vegetative", "flowering")
        days_since_planting: Days since planting
        current_weather: Current weather conditions
        smi: Soil Moisture Index (0-10)
        alert_type: Type of alert (e.g., "water_stress", "nutrient_deficiency", "pest_risk")
    
    Returns:
        dict: Personalized alert with specific actions
    """
    # Get farmer practice profile
    if farmer_id not in FARMER_PRACTICE_PROFILES:
        FARMER_PRACTICE_PROFILES[farmer_id] = {
            "fertilizer_preference": "unknown",
            "mulching_frequency": "unknown",
            "irrigation_access": "unknown",
            "risk_tolerance": "medium",
            "action_history": []
        }
    
    profile = FARMER_PRACTICE_PROFILES[farmer_id]
    
    # Generate base alert
    if alert_type == "water_stress":
        alert = _generate_water_stress_alert(
            crop, crop_stage, days_since_planting, current_weather, smi, profile
        )
    elif alert_type == "nutrient_deficiency":
        alert = _generate_nutrient_alert(
            crop, crop_stage, days_since_planting, profile
        )
    elif alert_type == "pest_risk":
        alert = _generate_pest_risk_alert(
            crop, crop_stage, current_weather, profile
        )
    else:
        alert = {"error": f"Unknown alert type: {alert_type}"}
    
    # Add personalization metadata
    alert["farmer_id"] = farmer_id
    alert["personalization_factors"] = {
        "fertilizer_preference": profile["fertilizer_preference"],
        "mulching_frequency": profile["mulching_frequency"],
        "irrigation_access": profile["irrigation_access"]
    }
    alert["generated_at"] = datetime.now().isoformat()
    
    return alert


def _generate_water_stress_alert(
    crop: str,
    crop_stage: str,
    days_since_planting: int,
    current_weather: Dict,
    smi: float,
    profile: Dict
) -> Dict[str, Any]:
    """Generate personalized water stress alert."""
    # Base message
    severity = "critical" if smi < 3 else "moderate" if smi < 5 else "mild"
    
    # Personalize based on farmer practices
    if profile["mulching_frequency"] == "always":
        action = f"💧 **Water Alert:** Since you've already mulched and no rain is coming, consider targeted spot watering for your {crop} to save the weakest plants."
    elif profile["mulching_frequency"] == "never" and profile["irrigation_access"] == "none":
        action = f"💧 **URGENT Water Alert:** {crop} at {crop_stage} stage needs water! No rain forecast. Apply mulch immediately to conserve soil moisture. Consider emergency manual watering for critical plants."
    elif profile["irrigation_access"] == "manual":
        action = f"💧 **Water Alert:** {crop} showing water stress (SMI: {smi:.1f}). Manual irrigation recommended for next 2-3 days. Focus on {crop_stage} stage plants."
    elif profile["irrigation_access"] == "automatic":
        action = f"💧 **Water Alert:** Activate irrigation system for {crop}. Current SMI: {smi:.1f}. Recommended: 30mm over next 3 days."
    else:
        action = f"💧 **Water Alert:** {crop} needs water (SMI: {smi:.1f}). No rain forecast for 5+ days. Take action now."
    
    return {
        "alert_type": "water_stress",
        "severity": severity,
        "crop": crop,
        "crop_stage": crop_stage,
        "message": action,
        "smi": smi,
        "recommended_actions": _get_personalized_water_actions(profile),
        "urgency": "high" if severity == "critical" else "medium"
    }


def _generate_nutrient_alert(
    crop: str,
    crop_stage: str,
    days_since_planting: int,
    profile: Dict
) -> Dict[str, Any]:
    """Generate personalized nutrient deficiency alert."""
    # Personalize based on fertilizer preference
    if profile["fertilizer_preference"] == "organic":
        action = f"🌱 **Nutrient Alert:** Your {crop} leaves are showing early yellowing (low Nitrogen). Your next fertilizer session should be pulled forward by 5 days. Apply **composted manure** or **chicken manure tea** now."
    elif profile["fertilizer_preference"] == "chemical":
        action = f"🌱 **Nutrient Alert:** Your {crop} needs Nitrogen boost. Apply **CAN (Calcium Ammonium Nitrate)** at 50 kg/acre immediately. Next application in 3 weeks."
    else:
        action = f"🌱 **Nutrient Alert:** {crop} showing yellowing leaves (Nitrogen deficiency). Options: (1) Organic: Composted manure, (2) Chemical: CAN 50 kg/acre."
    
    return {
        "alert_type": "nutrient_deficiency",
        "severity": "moderate",
        "crop": crop,
        "crop_stage": crop_stage,
        "message": action,
        "deficient_nutrient": "Nitrogen",
        "recommended_actions": _get_personalized_nutrient_actions(profile),
        "urgency": "medium"
    }


def _generate_pest_risk_alert(
    crop: str,
    crop_stage: str,
    current_weather: Dict,
    profile: Dict
) -> Dict[str, Any]:
    """Generate personalized pest risk alert."""
    action = f"🐛 **Pest Risk Alert:** Weather conditions favor pest activity on {crop}. Scout your field daily for signs of infestation."
    
    return {
        "alert_type": "pest_risk",
        "severity": "moderate",
        "crop": crop,
        "crop_stage": crop_stage,
        "message": action,
        "recommended_actions": ["Daily field scouting", "Inspect underside of leaves", "Check for egg masses"],
        "urgency": "medium"
    }


def _get_personalized_water_actions(profile: Dict) -> List[str]:
    """Get personalized water conservation actions."""
    actions = []
    
    if profile["mulching_frequency"] == "never":
        actions.append("Apply mulch (grass, crop residue) to reduce evaporation")
    
    if profile["irrigation_access"] == "manual":
        actions.append("Targeted manual watering (focus on stressed plants)")
    elif profile["irrigation_access"] == "automatic":
        actions.append("Activate drip irrigation system")
    else:
        actions.append("Emergency manual watering using buckets")
    
    actions.append("Weed control (reduces water competition)")
    
    return actions


def _get_personalized_nutrient_actions(profile: Dict) -> List[str]:
    """Get personalized nutrient management actions."""
    if profile["fertilizer_preference"] == "organic":
        return [
            "Apply composted manure (2 tons/acre)",
            "Use chicken manure tea (foliar spray)",
            "Plant nitrogen-fixing cover crops"
        ]
    elif profile["fertilizer_preference"] == "chemical":
        return [
            "Apply CAN (Calcium Ammonium Nitrate) 50 kg/acre",
            "Use foliar nitrogen spray for quick boost",
            "Follow up with NPK in 3 weeks"
        ]
    else:
        return [
            "Organic option: Composted manure",
            "Chemical option: CAN 50 kg/acre",
            "Combination: Manure + half-rate CAN"
        ]


# ============================================================================
# SIMULATION HELPERS
# ============================================================================

def _simulate_lcrs(lat: float, lon: float) -> float:
    """Simulate Long-term Climate Risk Score (replace with real calculation in production)."""
    import random
    return random.uniform(3.0, 8.0)


def _determine_season(date: datetime) -> str:
    """Determine agricultural season based on date."""
    month = date.month
    
    # Kenya agricultural seasons (approximate)
    if month in [3, 4, 5]:
        return "planting_season"  # Long rains
    elif month in [6, 7, 8]:
        return "harvest_season"  # Long rains harvest
    elif month in [10, 11]:
        return "planting_season"  # Short rains
    elif month in [12, 1]:
        return "harvest_season"  # Short rains harvest
    else:
        return "lean_season"  # Off-season


def _categorize_risk(risk_score: float) -> str:
    """Categorize combined risk score."""
    if risk_score >= 50:
        return "high"
    elif risk_score >= 30:
        return "moderate"
    else:
        return "low"


# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

__all__ = [
    "optimize_planting_window",
    "generate_financial_risk_scenarios",
    "generate_personalized_alert",
    "update_farmer_practice_profile",
    "CROP_YIELD_MODELS",
    "MARKET_PRICE_DATA"
]
