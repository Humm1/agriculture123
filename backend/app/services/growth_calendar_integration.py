"""
Growth Tracker + AI Calendar Integration
Auto-schedules farm practices based on growth tracking AI analysis

Key Features:
1. Auto-schedule events when plot is created (full season calendar)
2. Dynamic event updates based on health analysis
3. Smart pest/disease treatment scheduling
4. Weather-adjusted practice timing
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

from .calendar_generator import generate_season_calendar, load_calendars
from .ai_calendar_intelligence import (
    adjust_practice_date_with_weather,
    optimize_fertilizer_timing_with_leaching,
    refine_harvest_window_with_photos
)

# Data directory
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

GROWTH_EVENTS_FILE = DATA_DIR / "growth_tracker_events.json"


def load_growth_events() -> Dict:
    """Load growth tracker scheduled events"""
    if GROWTH_EVENTS_FILE.exists():
        with open(GROWTH_EVENTS_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_growth_events(events: Dict):
    """Save growth tracker events"""
    with open(GROWTH_EVENTS_FILE, 'w') as f:
        json.dump(events, f, indent=2)


# =============================================================================
# 1. AUTO-SCHEDULE EVENTS WHEN PLOT IS CREATED
# =============================================================================

async def schedule_full_season_calendar(
    plot_id: str,
    user_id: str,
    crop_name: str,
    planting_date: str,
    location: Dict[str, float],
    soil_analysis: Optional[Dict] = None,
    supabase_client=None
) -> Dict:
    """
    Auto-generate complete season calendar when plot is created
    
    Schedules:
    - Weeding events (2-3 times based on crop)
    - Fertilizer applications (top-dressing based on soil analysis)
    - Pest scouting (weekly during critical stages)
    - Disease monitoring
    - Earthing up (for potatoes)
    - Harvest window
    
    Args:
        plot_id: Digital plot UUID
        user_id: User UUID
        crop_name: Crop being grown
        planting_date: ISO format date
        location: GPS coordinates
        soil_analysis: Optional soil analysis results
        supabase_client: Supabase client for storage
    
    Returns:
        Complete season calendar with scheduled events
    """
    
    # Generate base calendar using calendar_generator
    variety = "Standard"  # Can be enhanced to accept variety
    calendar = generate_season_calendar(
        field_id=plot_id,
        crop=crop_name,
        variety=variety,
        planting_date=planting_date,
        location=location
    )
    
    # Convert calendar practices to database-ready events
    scheduled_events = []
    
    for practice in calendar.get("practices", []):
        event = {
            "plot_id": plot_id,
            "user_id": user_id,
            "event_type": "farm_practice",
            "practice_name": practice["practice_name"],
            "practice_key": practice["practice_key"],
            "scheduled_date": practice["due_date"],
            "days_after_planting": practice["days_after_planting"],
            "description": practice["description"],
            "local_methods": practice["local_methods"],
            "commercial_methods": practice["commercial_methods"],
            "estimated_labor_hours": practice["estimated_labor_hours"],
            "status": "scheduled",
            "source": "auto_generated",
            "created_at": datetime.utcnow().isoformat(),
            "reminders_enabled": True,
            "reminder_days_before": 1  # Remind 1 day before
        }
        
        # Enhance with soil-specific recommendations
        if soil_analysis and "fertilizer" in practice["practice_key"].lower():
            event["soil_recommendations"] = _get_soil_based_fertilizer_recommendations(
                soil_analysis, practice["practice_name"]
            )
        
        scheduled_events.append(event)
    
    # Add photo reminder events
    for photo_prompt in calendar.get("photo_schedule", []):
        event = {
            "plot_id": plot_id,
            "user_id": user_id,
            "event_type": "photo_reminder",
            "practice_name": f"Photo Check-in - {photo_prompt['stage']}",
            "scheduled_date": photo_prompt["date"],
            "days_after_planting": photo_prompt["days_after_planting"],
            "description": f"Take photos: {', '.join(photo_prompt['focus_areas'])}",
            "photo_focus_areas": photo_prompt["focus_areas"],
            "status": "scheduled",
            "source": "auto_generated",
            "created_at": datetime.utcnow().isoformat(),
            "reminders_enabled": True,
            "reminder_days_before": 0  # Remind on the day
        }
        scheduled_events.append(event)
    
    # Store in Supabase
    if supabase_client:
        try:
            for event in scheduled_events:
                supabase_client.table("scheduled_events").insert(event).execute()
        except Exception as e:
            print(f"Error storing events in Supabase: {e}")
    
    # Store locally as backup
    events = load_growth_events()
    if plot_id not in events:
        events[plot_id] = []
    events[plot_id].extend(scheduled_events)
    save_growth_events(events)
    
    return {
        "success": True,
        "plot_id": plot_id,
        "total_events_scheduled": len(scheduled_events),
        "calendar": calendar,
        "scheduled_events": scheduled_events,
        "harvest_window": calendar.get("harvest_window", {}),
        "maturity_days": calendar.get("maturity_days", 0)
    }


# =============================================================================
# 2. DYNAMIC EVENT UPDATES FROM HEALTH ANALYSIS
# =============================================================================

async def update_events_from_health_analysis(
    plot_id: str,
    user_id: str,
    health_analysis: Dict,
    growth_comparison: Optional[Dict] = None,
    supabase_client=None
) -> Dict:
    """
    Dynamically adjust scheduled events based on plant health
    
    Actions:
    - If nitrogen deficiency detected → Schedule/prioritize fertilizer
    - If water stress high → Schedule irrigation reminder
    - If growth rate slow → Adjust harvest window
    - If health declining → Schedule emergency check-in
    
    Args:
        plot_id: Digital plot UUID
        user_id: User UUID
        health_analysis: Health analysis from growth log
        growth_comparison: Growth comparison data
        supabase_client: Supabase client
    
    Returns:
        Updated events and recommendations
    """
    
    updates = {
        "plot_id": plot_id,
        "analyzed_at": datetime.utcnow().isoformat(),
        "actions_taken": [],
        "new_events": [],
        "adjusted_events": []
    }
    
    health_score = health_analysis.get("overall_health_score", 100)
    nitrogen_status = health_analysis.get("nitrogen_status", "Adequate")
    water_stress = health_analysis.get("water_stress", "None")
    alerts = health_analysis.get("alerts", [])
    
    # =========================================================================
    # ACTION 1: Nitrogen Deficiency → Schedule Fertilizer
    # =========================================================================
    if nitrogen_status in ["Deficient", "Moderate"]:
        event = {
            "plot_id": plot_id,
            "user_id": user_id,
            "event_type": "urgent_practice",
            "practice_name": "Emergency Nitrogen Application",
            "scheduled_date": (datetime.utcnow() + timedelta(days=2)).isoformat(),
            "description": f"Nitrogen status: {nitrogen_status}. Apply nitrogen-rich fertilizer immediately.",
            "local_methods": [
                "Apply well-decomposed manure (2 wheelbarrows per 10m row)",
                "Foliar spray with compost tea",
                "Side-dress with urea (diluted 1 tbsp per 4L water)"
            ],
            "commercial_methods": [
                "CAN (Calcium Ammonium Nitrate) - 25kg/hectare",
                "Urea foliar spray - 2% solution",
                "NPK 21-0-0 - 30kg/hectare"
            ],
            "priority": "high",
            "status": "scheduled",
            "source": "health_analysis",
            "health_trigger": f"Nitrogen Deficiency Detected: {health_analysis.get('nitrogen_description', '')}",
            "created_at": datetime.utcnow().isoformat()
        }
        
        updates["new_events"].append(event)
        updates["actions_taken"].append("Scheduled emergency nitrogen application")
        
        # Store event
        if supabase_client:
            try:
                supabase_client.table("scheduled_events").insert(event).execute()
            except Exception as e:
                print(f"Error storing event: {e}")
    
    # =========================================================================
    # ACTION 2: High Water Stress → Schedule Irrigation
    # =========================================================================
    if water_stress == "High":
        event = {
            "plot_id": plot_id,
            "user_id": user_id,
            "event_type": "urgent_practice",
            "practice_name": "Irrigation - Water Stress Detected",
            "scheduled_date": datetime.utcnow().isoformat(),  # Immediate
            "description": "High water stress detected. Irrigate immediately.",
            "local_methods": [
                "Water at base of plants (avoid leaves)",
                "Apply 20-30L per plant",
                "Water early morning or evening",
                "Mulch to retain moisture"
            ],
            "commercial_methods": [
                "Drip irrigation - run for 2-3 hours",
                "Sprinkler system - deep watering"
            ],
            "priority": "urgent",
            "status": "scheduled",
            "source": "health_analysis",
            "health_trigger": f"Water Stress: {health_analysis.get('water_description', '')}",
            "created_at": datetime.utcnow().isoformat()
        }
        
        updates["new_events"].append(event)
        updates["actions_taken"].append("Scheduled urgent irrigation")
        
        if supabase_client:
            try:
                supabase_client.table("scheduled_events").insert(event).execute()
            except Exception as e:
                print(f"Error storing event: {e}")
    
    # =========================================================================
    # ACTION 3: Health Declining → Schedule Emergency Check-in
    # =========================================================================
    if growth_comparison and growth_comparison.get("trend") == "declining":
        health_change = growth_comparison.get("health_score_change", 0)
        if health_change < -10:  # Significant decline
            event = {
                "plot_id": plot_id,
                "user_id": user_id,
                "event_type": "photo_reminder",
                "practice_name": "Emergency Health Check",
                "scheduled_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
                "description": f"Health declining rapidly ({health_change:.1f} points). Take detailed photos for diagnosis.",
                "photo_focus_areas": ["leaves", "stems", "soil", "overall_plant"],
                "priority": "high",
                "status": "scheduled",
                "source": "health_analysis",
                "health_trigger": f"Health declining by {health_change:.1f} points",
                "created_at": datetime.utcnow().isoformat()
            }
            
            updates["new_events"].append(event)
            updates["actions_taken"].append("Scheduled emergency health check")
            
            if supabase_client:
                try:
                    supabase_client.table("scheduled_events").insert(event).execute()
                except Exception as e:
                    print(f"Error storing event: {e}")
    
    # =========================================================================
    # ACTION 4: Process Alerts
    # =========================================================================
    for alert in alerts:
        if alert.get("severity") == "high":
            event = {
                "plot_id": plot_id,
                "user_id": user_id,
                "event_type": "alert_action",
                "practice_name": f"Action Required: {alert.get('type', 'Unknown')}",
                "scheduled_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
                "description": alert.get("message", ""),
                "priority": "high",
                "status": "scheduled",
                "source": "health_analysis",
                "health_trigger": alert.get("message", ""),
                "created_at": datetime.utcnow().isoformat()
            }
            
            updates["new_events"].append(event)
            updates["actions_taken"].append(f"Scheduled action for alert: {alert.get('type')}")
    
    return updates


# =============================================================================
# 3. SMART PEST/DISEASE TREATMENT SCHEDULING
# =============================================================================

async def schedule_treatment_from_diagnosis(
    plot_id: str,
    user_id: str,
    diagnosis: Dict,
    treatment_plan: Dict,
    supabase_client=None
) -> Dict:
    """
    Auto-schedule treatment events from pest/disease diagnosis
    
    Creates:
    - Immediate treatment application events
    - Follow-up treatment events (if multiple applications needed)
    - Monitoring check-ins
    - Treatment effectiveness evaluation
    
    Args:
        plot_id: Digital plot UUID
        user_id: User UUID
        diagnosis: Diagnosis results
        treatment_plan: Treatment plan from diagnosis
        supabase_client: Supabase client
    
    Returns:
        Scheduled treatment events
    """
    
    scheduled_events = []
    
    treatments = treatment_plan.get("treatments", [])
    
    for idx, treatment in enumerate(treatments):
        priority = treatment.get("priority", "moderate")
        category = treatment.get("category", "treatment")
        product = treatment.get("product", "")
        application = treatment.get("application", {})
        frequency = application.get("frequency", "Apply once")
        
        # Parse frequency to determine number of applications
        num_applications = 1
        days_between = 7
        
        if "every" in frequency.lower():
            # Extract days between applications
            import re
            match = re.search(r'(\d+)', frequency)
            if match:
                days_between = int(match.group(1))
            
            # Estimate number of applications
            if "2-3 weeks" in frequency.lower():
                num_applications = 3
            elif "until" in frequency.lower():
                num_applications = 4
            else:
                num_applications = 2
        
        # Schedule applications
        for app_num in range(num_applications):
            days_offset = app_num * days_between
            
            if app_num == 0 and priority == "urgent":
                days_offset = 0  # Immediate for urgent
            
            scheduled_date = datetime.utcnow() + timedelta(days=days_offset)
            
            event = {
                "plot_id": plot_id,
                "user_id": user_id,
                "event_type": "treatment_application",
                "practice_name": f"{product} - Application {app_num + 1}/{num_applications}",
                "scheduled_date": scheduled_date.isoformat(),
                "description": f"{treatment.get('category', '').title()} application for {diagnosis.get('diagnosis', {}).get('primary_concern', {}).get('name', 'detected issue')}",
                "treatment_details": {
                    "product": product,
                    "method": application.get("method", ""),
                    "timing": application.get("timing", ""),
                    "coverage": application.get("coverage", "")
                },
                "local_methods": treatment.get("products", {}).get("organic", []),
                "commercial_methods": treatment.get("products", {}).get("chemical", []),
                "best_practices": treatment.get("best_practices", []),
                "priority": priority if app_num == 0 else "moderate",
                "status": "scheduled",
                "source": "diagnosis",
                "diagnosis_trigger": f"{diagnosis.get('diagnosis', {}).get('primary_concern', {}).get('name', 'Issue')} - {diagnosis.get('diagnosis', {}).get('primary_concern', {}).get('severity', 'moderate')} severity",
                "created_at": datetime.utcnow().isoformat(),
                "application_number": app_num + 1,
                "total_applications": num_applications
            }
            
            scheduled_events.append(event)
            
            # Store in Supabase
            if supabase_client:
                try:
                    supabase_client.table("scheduled_events").insert(event).execute()
                except Exception as e:
                    print(f"Error storing treatment event: {e}")
        
        # Schedule monitoring check-in after treatment
        monitoring_date = datetime.utcnow() + timedelta(days=(num_applications * days_between) + 3)
        
        monitoring_event = {
            "plot_id": plot_id,
            "user_id": user_id,
            "event_type": "photo_reminder",
            "practice_name": f"Treatment Effectiveness Check - {product}",
            "scheduled_date": monitoring_date.isoformat(),
            "description": f"Take photos to evaluate treatment effectiveness for {diagnosis.get('diagnosis', {}).get('primary_concern', {}).get('name', 'issue')}",
            "photo_focus_areas": ["affected_areas", "leaves", "overall_plant"],
            "status": "scheduled",
            "source": "diagnosis_followup",
            "created_at": datetime.utcnow().isoformat()
        }
        
        scheduled_events.append(monitoring_event)
        
        if supabase_client:
            try:
                supabase_client.table("scheduled_events").insert(monitoring_event).execute()
            except Exception as e:
                print(f"Error storing monitoring event: {e}")
    
    # Store locally
    events = load_growth_events()
    if plot_id not in events:
        events[plot_id] = []
    events[plot_id].extend(scheduled_events)
    save_growth_events(events)
    
    return {
        "success": True,
        "plot_id": plot_id,
        "total_events_scheduled": len(scheduled_events),
        "scheduled_events": scheduled_events,
        "treatment_timeline": treatment_plan.get("treatment_timeline", ""),
        "estimated_cost": treatment_plan.get("estimated_cost", "")
    }


# =============================================================================
# 4. WEATHER-ADJUSTED EVENT TIMING
# =============================================================================

async def adjust_upcoming_events_for_weather(
    plot_id: str,
    weather_forecast: Dict,
    soil_moisture_index: Optional[float] = None,
    supabase_client=None
) -> Dict:
    """
    Adjust upcoming scheduled events based on weather forecast
    
    Uses AI calendar intelligence to:
    - Delay weeding if rain expected
    - Optimize fertilizer timing to avoid leaching
    - Adjust pest scouting based on temperature
    
    Args:
        plot_id: Digital plot UUID
        weather_forecast: Weather data
        soil_moisture_index: Optional SMI from BLE sensors
        supabase_client: Supabase client
    
    Returns:
        Adjusted events
    """
    
    adjustments = {
        "plot_id": plot_id,
        "adjusted_at": datetime.utcnow().isoformat(),
        "adjustments_made": []
    }
    
    # Get upcoming events (next 14 days)
    if supabase_client:
        try:
            future_date = (datetime.utcnow() + timedelta(days=14)).isoformat()
            response = supabase_client.table("scheduled_events").select("*").eq("plot_id", plot_id).gte("scheduled_date", datetime.utcnow().isoformat()).lte("scheduled_date", future_date).eq("status", "scheduled").execute()
            
            upcoming_events = response.data
            
            for event in upcoming_events:
                practice_name = event.get("practice_name", "")
                original_date = event.get("scheduled_date", "")
                
                # Use AI calendar intelligence to adjust
                adjustment = adjust_practice_date_with_weather(
                    field_id=plot_id,
                    practice_name=practice_name,
                    original_date=original_date,
                    current_date=datetime.utcnow().isoformat(),
                    weather_forecast=weather_forecast,
                    soil_moisture_index=soil_moisture_index
                )
                
                if adjustment.get("adjustment_made"):
                    # Update event in database
                    supabase_client.table("scheduled_events").update({
                        "scheduled_date": adjustment["adjusted_date"],
                        "adjustment_reason": ", ".join(adjustment.get("reasoning", [])),
                        "original_date": original_date,
                        "adjusted_at": datetime.utcnow().isoformat()
                    }).eq("id", event["id"]).execute()
                    
                    adjustments["adjustments_made"].append({
                        "event_id": event["id"],
                        "practice_name": practice_name,
                        "original_date": original_date,
                        "adjusted_date": adjustment["adjusted_date"],
                        "adjustment_days": adjustment["adjustment_days"],
                        "reasoning": adjustment["reasoning"]
                    })
        
        except Exception as e:
            print(f"Error adjusting events: {e}")
    
    return adjustments


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _get_soil_based_fertilizer_recommendations(
    soil_analysis: Dict,
    practice_name: str
) -> Dict:
    """Generate soil-specific fertilizer recommendations"""
    
    soil_type = soil_analysis.get("soil_type", "Loam")
    organic_matter = soil_analysis.get("organic_matter", "Moderate")
    ph_range = soil_analysis.get("ph_range", "6.0-7.0")
    
    recommendations = {
        "soil_context": f"Soil Type: {soil_type}, Organic Matter: {organic_matter}, pH: {ph_range}",
        "adjustments": []
    }
    
    # Clay soils - need less frequent but heavier applications
    if "clay" in soil_type.lower():
        recommendations["adjustments"].append(
            "🏺 Clay soil: Apply fertilizer less frequently but in larger amounts (nutrient retention is good)"
        )
        recommendations["adjustments"].append(
            "💧 Avoid waterlogging - apply during dry periods"
        )
    
    # Sandy soils - need more frequent lighter applications
    elif "sand" in soil_type.lower():
        recommendations["adjustments"].append(
            "🏖️ Sandy soil: Apply smaller amounts more frequently (nutrients leach quickly)"
        )
        recommendations["adjustments"].append(
            "⏰ Apply just before light rain if possible (helps incorporation)"
        )
    
    # Low organic matter - prioritize compost
    if organic_matter == "Low":
        recommendations["adjustments"].append(
            "🌿 Low organic matter: Prioritize compost/manure over chemical fertilizers"
        )
    
    # pH adjustments
    if "5" in ph_range or "4" in ph_range:  # Acidic
        recommendations["adjustments"].append(
            "🧪 Acidic soil: Consider lime application before fertilizing"
        )
    elif "8" in ph_range or "9" in ph_range:  # Alkaline
        recommendations["adjustments"].append(
            "🧪 Alkaline soil: Use acidifying fertilizers like ammonium sulfate"
        )
    
    return recommendations
