"""
Farm Calendar Generation System
Auto-generates complete season calendar from planting date with practice schedules

ENHANCED WITH AI:
- Dynamic weather-adjusted calendar (continuously adjusts practice dates)
- AI-optimized nutrient application timing (minimizes leaching losses)
- AI-refined harvest predictions from actual photo tracking data
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

from .growth_model import get_crop_model, get_current_growth_stage
from .lcrs_engine import estimate_weather_forecast_risk
from .ai_calendar_intelligence import (
    adjust_practice_date_with_weather,
    optimize_fertilizer_timing_with_leaching,
    refine_harvest_window_with_photos
)

# Data directory
DATA_DIR = Path(__file__).parent.parent / "data"
CALENDARS_FILE = DATA_DIR / "farm_calendars.json"


def load_calendars() -> Dict:
    """Load all farm calendars"""
    if CALENDARS_FILE.exists():
        with open(CALENDARS_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_calendars(calendars: Dict):
    """Save farm calendars"""
    with open(CALENDARS_FILE, 'w') as f:
        json.dump(calendars, f, indent=2)


def generate_season_calendar(
    field_id: str,
    crop: str,
    variety: str,
    planting_date: str,
    location: Dict[str, float]
) -> Dict:
    """
    Generate complete season calendar from planting date
    
    Args:
        field_id: Field identifier
        crop: Crop name
        variety: Variety name
        planting_date: ISO format date string
        location: GPS coordinates for weather adjustments
    
    Returns:
        Complete calendar with all scheduled activities
    """
    model = get_crop_model(crop, variety)
    planting = datetime.fromisoformat(planting_date.replace('Z', ''))
    
    # Generate base calendar from growth model
    calendar = {
        "field_id": field_id,
        "crop": crop,
        "variety": variety,
        "planting_date": planting_date,
        "location": location,
        "maturity_days": model["maturity_days"],
        "generated_at": datetime.utcnow().isoformat(),
        "practices": [],
        "stages": [],
        "harvest_window": {}
    }
    
    # Add growth stages to calendar
    for stage_key, stage_data in model["stages"].items():
        stage_start = planting + timedelta(days=stage_data["start"])
        stage_end = planting + timedelta(days=stage_data["end"])
        
        calendar["stages"].append({
            "stage_key": stage_key,
            "stage_name": stage_data["name"],
            "start_date": stage_start.isoformat(),
            "end_date": stage_end.isoformat(),
            "days_after_planting_start": stage_data["start"],
            "days_after_planting_end": stage_data["end"]
        })
    
    # Add critical practices to calendar
    for practice_key, practice_day in model["critical_practices"].items():
        due_date = planting + timedelta(days=practice_day)
        
        practice_info = _get_practice_details(practice_key, crop)
        
        calendar["practices"].append({
            "practice_key": practice_key,
            "practice_name": practice_info["name"],
            "due_date": due_date.isoformat(),
            "days_after_planting": practice_day,
            "description": practice_info["description"],
            "local_methods": practice_info["local_methods"],
            "commercial_methods": practice_info["commercial_methods"],
            "estimated_labor_hours": practice_info["labor_hours"],
            "status": "pending",
            "completed_date": None
        })
    
    # Calculate harvest window with weather adjustments
    calendar["harvest_window"] = _calculate_harvest_window(
        planting_date,
        model["maturity_days"],
        location,
        crop
    )
    
    # Add weekly photo prompts
    calendar["photo_schedule"] = _generate_photo_schedule(
        planting_date,
        model["maturity_days"]
    )
    
    # Save calendar
    calendars = load_calendars()
    if field_id not in calendars:
        calendars[field_id] = []
    calendars[field_id].append(calendar)
    save_calendars(calendars)
    
    return calendar


def _get_practice_details(practice_key: str, crop: str) -> Dict:
    """Get detailed information about a farm practice"""
    
    practice_library = {
        "first_weeding": {
            "name": "First Weeding",
            "description": "Remove weeds to reduce competition for nutrients, water, and sunlight",
            "local_methods": [
                "Hand weeding using jembe (hoe)",
                "Slash weeds with panga (machete)",
                "Family labor exchange (communal weeding)"
            ],
            "commercial_methods": [
                "Pre-emergence herbicide (Atrazine for maize)",
                "Post-emergence herbicide (2,4-D)",
                "Mechanical weeding with tractor"
            ],
            "labor_hours": 8
        },
        "second_weeding": {
            "name": "Second Weeding",
            "description": "Final weed removal before canopy closure",
            "local_methods": [
                "Hand weeding between rows",
                "Earthing up while weeding (creates ridges)"
            ],
            "commercial_methods": [
                "Selective herbicides",
                "Mechanical inter-row cultivation"
            ],
            "labor_hours": 6
        },
        "third_weeding": {
            "name": "Third Weeding",
            "description": "Late-season weed control (long-season crops only)",
            "local_methods": [
                "Spot weeding by hand",
                "Mulching to suppress new weeds"
            ],
            "commercial_methods": [
                "Spot spraying with herbicide"
            ],
            "labor_hours": 4
        },
        "first_top_dress": {
            "name": "First Top-Dress Fertilizer",
            "description": "Apply nitrogen fertilizer to support vegetative growth",
            "local_methods": [
                "Well-composted manure (2-3 wheelbarrows per 10m row)",
                "Compost tea application",
                "Green manure incorporation from legumes"
            ],
            "commercial_methods": [
                "CAN (Calcium Ammonium Nitrate) - 50kg/hectare",
                "Urea - 30kg/hectare",
                "NPK 17:17:17 - 50kg/hectare"
            ],
            "labor_hours": 4
        },
        "second_top_dress": {
            "name": "Second Top-Dress Fertilizer",
            "description": "Final nitrogen boost before flowering/grain fill",
            "local_methods": [
                "Liquid manure application",
                "Side-dress with compost"
            ],
            "commercial_methods": [
                "Urea - 25kg/hectare",
                "CAN - 40kg/hectare"
            ],
            "labor_hours": 3
        },
        "first_earthing_up": {
            "name": "First Earthing Up",
            "description": "Mound soil around potato plants to protect tubers from sunlight",
            "local_methods": [
                "Use jembe to pull soil from furrows onto ridges",
                "Create 15-20cm high ridges"
            ],
            "commercial_methods": [
                "Tractor-mounted ridger"
            ],
            "labor_hours": 6
        },
        "second_earthing_up": {
            "name": "Second Earthing Up",
            "description": "Final earthing to maximize tuber coverage",
            "local_methods": [
                "Build ridges to 25-30cm height",
                "Ensure no tubers are exposed"
            ],
            "commercial_methods": [
                "Tractor ridging with higher settings"
            ],
            "labor_hours": 5
        },
        "fertilizer_application": {
            "name": "Basal Fertilizer Application",
            "description": "Apply base fertilizer at or shortly after planting",
            "local_methods": [
                "Mix compost into planting holes",
                "Apply manure along rows before planting"
            ],
            "commercial_methods": [
                "DAP (Diammonium Phosphate) - 50kg/hectare",
                "NPK 23:23:0 - 60kg/hectare"
            ],
            "labor_hours": 4
        },
        "pest_scouting_start": {
            "name": "Begin Pest Scouting",
            "description": "Start regular field inspections for pests",
            "local_methods": [
                "Walk field 2-3 times per week",
                "Check leaves (top and bottom) for eggs/larvae",
                "Use local traps (molasses + water for Fall Armyworm)"
            ],
            "commercial_methods": [
                "Pheromone traps",
                "Threshold-based insecticide application"
            ],
            "labor_hours": 2
        },
        "disease_monitoring_start": {
            "name": "Begin Disease Monitoring",
            "description": "Start checking for disease symptoms",
            "local_methods": [
                "Inspect for leaf spots, wilting, discoloration",
                "Remove and burn infected plants",
                "Ensure good drainage to prevent fungal diseases"
            ],
            "commercial_methods": [
                "Preventive fungicide spray (e.g., Mancozeb for blight)",
                "Disease-specific treatments based on diagnosis"
            ],
            "labor_hours": 2
        },
        "blight_monitoring_start": {
            "name": "Begin Late Blight Monitoring",
            "description": "Critical for potatoes - monitor for late blight symptoms",
            "local_methods": [
                "Check for brown lesions on leaves",
                "Remove infected leaves immediately",
                "Avoid overhead watering"
            ],
            "commercial_methods": [
                "Preventive Ridomil spray every 10-14 days",
                "Curative fungicides if infection detected"
            ],
            "labor_hours": 2
        },
        "staking": {
            "name": "Install Stakes/Trellis",
            "description": "Provide support for climbing beans",
            "local_methods": [
                "Use bamboo poles or wooden stakes (2m high)",
                "String method with sisal rope",
                "Traditional tripod staking"
            ],
            "commercial_methods": [
                "Wire trellis system",
                "Metal stakes with netting"
            ],
            "labor_hours": 6
        },
        "transplanting": {
            "name": "Transplant Seedlings",
            "description": "Move rice seedlings from nursery to main field",
            "local_methods": [
                "Hand transplanting in rows (20cm spacing)",
                "2-3 seedlings per hill",
                "Transplant in morning or evening to reduce stress"
            ],
            "commercial_methods": [
                "Mechanical rice transplanter"
            ],
            "labor_hours": 16
        },
        "water_management_critical": {
            "name": "Critical Water Management",
            "description": "Maintain optimal water levels for rice",
            "local_methods": [
                "Maintain 5-10cm standing water",
                "Check and repair bunds daily",
                "Drain field 2 weeks before harvest"
            ],
            "commercial_methods": [
                "Automated irrigation with sensors",
                "Drip irrigation for upland rice"
            ],
            "labor_hours": 3
        }
    }
    
    return practice_library.get(practice_key, {
        "name": practice_key.replace('_', ' ').title(),
        "description": "Important farm practice",
        "local_methods": ["Consult local extension officer"],
        "commercial_methods": ["Commercial options available"],
        "labor_hours": 4
    })


def _calculate_harvest_window(
    planting_date: str,
    maturity_days: int,
    location: Dict[str, float],
    crop: str
) -> Dict:
    """
    Calculate harvest window with weather adjustments
    
    Returns:
        Harvest window with weather forecast and recommendations
    """
    planting = datetime.fromisoformat(planting_date.replace('Z', ''))
    
    # Base harvest date
    harvest_date = planting + timedelta(days=maturity_days)
    harvest_start = harvest_date - timedelta(days=7)  # 7-day window
    harvest_end = harvest_date + timedelta(days=7)
    
    # Get weather forecast for harvest period
    harvest_month = harvest_date.month
    weather_risk = estimate_weather_forecast_risk(location["latitude"], location["longitude"], harvest_month)
    
    # Adjust window based on weather
    if weather_risk["precipitation_risk"] == "high":
        recommendation = "⚠️ HIGH RAIN RISK during harvest. Plan covered drying space NOW. Consider harvesting early."
        urgency = "high"
    elif weather_risk["precipitation_risk"] == "low":
        recommendation = "✅ FAVORABLE DRY CONDITIONS expected. Optimal harvest window."
        urgency = "low"
    else:
        recommendation = "🌤️ MODERATE CONDITIONS. Monitor weather closely and be ready for quick harvest."
        urgency = "medium"
    
    return {
        "optimal_harvest_date": harvest_date.isoformat(),
        "harvest_window_start": harvest_start.isoformat(),
        "harvest_window_end": harvest_end.isoformat(),
        "days_after_planting": maturity_days,
        "weather_forecast": {
            "precipitation_risk": weather_risk["precipitation_risk"],
            "temperature_pattern": weather_risk["temperature_pattern"],
            "season": weather_risk["season"]
        },
        "recommendation": recommendation,
        "urgency": urgency,
        "harvest_tips": _get_harvest_tips(crop, weather_risk["precipitation_risk"])
    }


def _get_harvest_tips(crop: str, precipitation_risk: str) -> List[str]:
    """Get crop-specific harvest tips based on weather"""
    
    tips = {
        "maize": {
            "low": [
                "Harvest when husks are dry and brown",
                "Kernels should be hard (test with fingernail)",
                "Dry in sun for 2-3 weeks before storage",
                "Target moisture content: 13-14%"
            ],
            "medium": [
                "Harvest as soon as moisture content allows",
                "Use covered drying area if rain expected",
                "Turn cobs daily for even drying",
                "Test moisture before storage"
            ],
            "high": [
                "Harvest immediately to avoid mold",
                "CRITICAL: Use covered drying with good ventilation",
                "Consider artificial drying if available",
                "Check storage facility temperature/humidity NOW"
            ]
        },
        "beans": {
            "low": [
                "Harvest when pods are dry and brittle",
                "Best time: early morning after dew dries",
                "Thresh by beating or trampling",
                "Store in airtight containers"
            ],
            "medium": [
                "Harvest mature beans even if some pods are green",
                "Dry under shelter with good airflow",
                "Separate by dryness for staged threshing"
            ],
            "high": [
                "Harvest all mature pods immediately",
                "Hang plants under roof for drying",
                "Prevent contact with wet ground",
                "Use raised drying racks"
            ]
        },
        "potatoes": {
            "low": [
                "Wait 2 weeks after vines die back",
                "Harvest on dry, sunny day",
                "Cure in shade for 10-14 days",
                "Store in cool, dark place"
            ],
            "medium": [
                "Harvest during dry spell",
                "Remove soil gently to avoid bruising",
                "Cure immediately in well-ventilated area"
            ],
            "high": [
                "Harvest urgently to prevent rot",
                "Remove excess soil before storage",
                "Discard damaged tubers immediately",
                "Ensure storage has LOW humidity"
            ]
        },
        "rice": {
            "low": [
                "Harvest at 20-25% moisture",
                "Cut and bundle for field drying",
                "Thresh when moisture drops to 14%"
            ],
            "medium": [
                "Harvest and move to covered area quickly",
                "Use tarpaulins for ground drying"
            ],
            "high": [
                "Harvest immediately despite rain",
                "Dry under cover with fans if possible",
                "Turn frequently to prevent heating"
            ]
        }
    }
    
    crop_tips = tips.get(crop.lower(), tips["maize"])  # Default to maize
    return crop_tips.get(precipitation_risk, crop_tips["low"])


def _generate_photo_schedule(planting_date: str, maturity_days: int) -> List[Dict]:
    """Generate weekly photo prompt schedule"""
    planting = datetime.fromisoformat(planting_date.replace('Z', ''))
    
    schedule = []
    photo_day = 7  # Start at day 7
    
    while photo_day < maturity_days:
        photo_date = planting + timedelta(days=photo_day)
        schedule.append({
            "photo_number": len(schedule) + 1,
            "due_date": photo_date.isoformat(),
            "days_after_planting": photo_day,
            "prompt": f"📸 Week {len(schedule) + 1} Photo: Capture overview and close-up of leaves",
            "status": "pending",
            "photo_url": None
        })
        photo_day += 7
    
    return schedule


def get_calendar(field_id: str) -> Optional[Dict]:
    """Get the most recent calendar for a field"""
    calendars = load_calendars()
    if field_id in calendars and calendars[field_id]:
        return calendars[field_id][-1]  # Return most recent
    return None


def get_pending_practices(field_id: str, days_lookahead: int = 7) -> List[Dict]:
    """Get practices due within the specified lookahead period"""
    calendar = get_calendar(field_id)
    if not calendar:
        return []
    
    now = datetime.utcnow()
    lookahead_date = now + timedelta(days=days_lookahead)
    
    pending = []
    for practice in calendar["practices"]:
        if practice["status"] == "pending":
            due_date = datetime.fromisoformat(practice["due_date"].replace('Z', ''))
            
            # Include if within lookahead or overdue
            if due_date <= lookahead_date:
                days_until = (due_date - now).days
                practice["days_until_due"] = days_until
                practice["is_overdue"] = days_until < 0
                pending.append(practice)
    
    return sorted(pending, key=lambda x: x["days_until_due"])


def mark_practice_completed(field_id: str, practice_key: str, completion_date: Optional[str] = None) -> Dict:
    """Mark a practice as completed"""
    calendars = load_calendars()
    
    if field_id not in calendars or not calendars[field_id]:
        raise ValueError(f"No calendar found for field {field_id}")
    
    calendar = calendars[field_id][-1]  # Get most recent calendar
    
    if completion_date is None:
        completion_date = datetime.utcnow().isoformat()
    
    practice_found = False
    for practice in calendar["practices"]:
        if practice["practice_key"] == practice_key:
            practice["status"] = "completed"
            practice["completed_date"] = completion_date
            practice_found = True
            break
    
    if not practice_found:
        raise ValueError(f"Practice {practice_key} not found in calendar")
    
    save_calendars(calendars)
    return calendar


def get_completion_rate(field_id: str) -> Dict:
    """Calculate completion rate for farm practices"""
    calendar = get_calendar(field_id)
    if not calendar:
        return {"completion_rate": 0, "completed": 0, "total": 0, "overdue": 0}
    
    total = len(calendar["practices"])
    completed = sum(1 for p in calendar["practices"] if p["status"] == "completed")
    
    now = datetime.utcnow()
    overdue = sum(1 for p in calendar["practices"]
                  if p["status"] != "completed" and 
                  datetime.fromisoformat(p["scheduled_date"].replace('Z', '')) < now)
    
    return {
        "completion_rate": round((completed / total * 100) if total > 0 else 0, 1),
        "completed": completed,
        "total": total,
        "overdue": overdue
    }


# =============================================================================
# AI-ENHANCED CALENDAR FUNCTIONS
# =============================================================================

def get_ai_adjusted_practices(
    field_id: str,
    weather_forecast: Dict,
    soil_moisture_index: Optional[float] = None
) -> List[Dict]:
    """
    Get upcoming practices with AI-adjusted dates based on real-time weather
    
    The AI continuously monitors weather and adjusts practice timing to:
    - Avoid weeding when soil is too wet (compaction risk)
    - Optimize fertilizer timing to minimize leaching
    - Advance pest scouting when conditions favor outbreaks
    
    Args:
        field_id: Field identifier
        weather_forecast: Weather data from LCRS engine
        soil_moisture_index: Optional SMI from BLE sensor (0-1 scale)
    
    Returns:
        List of practices with AI-adjusted dates and reasoning
    """
    calendar = get_calendar(field_id)
    if not calendar:
        return []
    
    pending = get_pending_practices(field_id, lookahead_days=14)
    current_date = datetime.utcnow().isoformat()
    
    adjusted_practices = []
    for practice in pending:
        # Get AI adjustment
        adjustment = adjust_practice_date_with_weather(
            field_id=field_id,
            practice_name=practice["name"],
            original_date=practice["scheduled_date"],
            current_date=current_date,
            weather_forecast=weather_forecast,
            soil_moisture_index=soil_moisture_index
        )
        
        # Merge with practice data
        practice_with_adjustment = {
            **practice,
            "ai_adjusted_date": adjustment["adjusted_date"],
            "adjustment_days": adjustment["adjustment_days"],
            "adjustment_made": adjustment["adjustment_made"],
            "adjustment_reasoning": adjustment["reasoning"],
            "farmer_alert": adjustment.get("farmer_alert")
        }
        adjusted_practices.append(practice_with_adjustment)
    
    return adjusted_practices


def get_optimized_fertilizer_timing(
    field_id: str,
    fertilizer_type: str,
    scheduled_date: str,
    soil_texture: str,
    weather_forecast: Dict
) -> Dict:
    """
    Get AI-optimized fertilizer application timing
    
    Minimizes nutrient leaching by analyzing:
    - Recent rainfall (past 7 days)
    - Rainfall forecast (next 5 days)
    - Soil texture (sandy = high leaching risk)
    - Fertilizer mobility (N > K > P)
    
    Args:
        field_id: Field identifier
        fertilizer_type: "nitrogen", "phosphorus", "potassium", "npk"
        scheduled_date: Originally planned date
        soil_texture: "sandy", "loam", "clay"
        weather_forecast: Weather data with rainfall array
    
    Returns:
        Optimized timing with leaching risk analysis
    """
    recent_rainfall = weather_forecast.get("rainfall_last_7_days", 0)
    forecast_5day = weather_forecast.get("rainfall_next_5_days", [0, 0, 0, 0, 0])
    
    optimization = optimize_fertilizer_timing_with_leaching(
        field_id=field_id,
        fertilizer_type=fertilizer_type,
        scheduled_date=scheduled_date,
        soil_texture=soil_texture,
        recent_rainfall=recent_rainfall,
        forecast_rainfall_5day=forecast_5day
    )
    
    return optimization


def get_refined_harvest_window(
    field_id: str,
    crop: str,
    variety: str
) -> Dict:
    """
    Get AI-refined harvest window based on actual growth photos
    
    Uses weekly health scores to determine if crop is:
    - Ahead of schedule → Harvest earlier
    - On schedule → Harvest as planned
    - Behind schedule → Extend harvest window
    
    Args:
        field_id: Field identifier
        crop: Crop type
        variety: Variety name
    
    Returns:
        Refined harvest window with adjustment reasoning
    """
    # Get calendar
    calendar = get_calendar(field_id)
    if not calendar:
        return {"error": "Calendar not found"}
    
    original_harvest = calendar["harvest_window"]["start_date"]
    
    # Get actual growth scores from photo tracking
    from .growth_tracking import get_growth_photos
    growth_photos = get_growth_photos(field_id)
    
    if not growth_photos:
        return {
            "status": "no_adjustment",
            "message": "No photo data available - using original harvest window",
            "harvest_window": calendar["harvest_window"]
        }
    
    # Convert photos to score format
    actual_scores = [
        {
            "days_after_planting": photo["days_after_planting"],
            "health_score": photo["health_score"]
        }
        for photo in growth_photos
    ]
    
    # Get optimal growth curve
    from .growth_model import calculate_optimal_growth_curve
    maturity_days = calendar["maturity_days"]
    optimal_curve = calculate_optimal_growth_curve(crop, variety, maturity_days)
    
    # Refine harvest window with AI
    refined = refine_harvest_window_with_photos(
        field_id=field_id,
        original_harvest_date=original_harvest,
        actual_growth_scores=actual_scores,
        optimal_growth_curve=optimal_curve,
        crop=crop,
        variety=variety
    )
    
    # Update calendar with refined window
    calendar["harvest_window"] = refined["refined_harvest_window"]
    calendar["harvest_window_refined_at"] = datetime.utcnow().isoformat()
    calendar["harvest_adjustment_days"] = refined["days_adjustment"]
    
    calendars = load_calendars()
    calendars[field_id][-1] = calendar
    save_calendars(calendars)
    
    return refined


def generate_practice_optimization_alert(field_id: str, practice_name: str) -> Dict:
    """
    Generate AI-powered alert for a specific practice
    
    Example alerts:
    - "Weeding: Delay 2 days - heavy rain forecast"
    - "Fertilizer: Apply TODAY - ideal rain window in 24 hours"
    - "Pest Scouting: URGENT - hot/dry conditions favor aphids"
    
    Args:
        field_id: Field identifier
        practice_name: Practice to check (e.g., "Weeding - Round 1")
    
    Returns:
        Alert with emoji, urgency, and actionable guidance
    """
    calendar = get_calendar(field_id)
    if not calendar:
        return {"error": "Calendar not found"}
    
    # Find practice
    practice = None
    for p in calendar["practices"]:
        if p["name"] == practice_name:
            practice = p
            break
    
    if not practice:
        return {"error": f"Practice '{practice_name}' not found"}
    
    # Get weather forecast (mock for now - in production, call LCRS engine)
    weather_forecast = {
        "rainfall_last_7_days": 25,
        "forecast_next_3_days": 45,
        "avg_temperature": 26
    }
    
    # Get AI adjustment
    adjustment = adjust_practice_date_with_weather(
        field_id=field_id,
        practice_name=practice_name,
        original_date=practice["scheduled_date"],
        current_date=datetime.utcnow().isoformat(),
        weather_forecast=weather_forecast
    )
    
    if not adjustment["adjustment_made"]:
        return {
            "alert_type": "on_schedule",
            "emoji": "✅",
            "title": f"{practice_name} - On Schedule",
            "message": "Conditions are optimal. Proceed as planned.",
            "urgency": "low"
        }
    
    # Return farmer alert
    return adjustment["farmer_alert"]
    
    return {
        "completion_rate": round((completed / total) * 100, 1) if total > 0 else 0,
        "completed": completed,
        "total": total,
        "overdue": overdue
    }
