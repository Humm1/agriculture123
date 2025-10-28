"""
AI Calendar API Routes
Provides AI-powered farming calendar recommendations based on crop lifecycle
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from app.services.ml_inference import ModelInferenceService
from app.services.crop_lifecycle_calendar import get_lifecycle_calendar

router = APIRouter()
ml_inference = ModelInferenceService()
lifecycle_calendar = get_lifecycle_calendar()


class CalendarPredictionRequest(BaseModel):
    """Request model for calendar prediction"""
    crop: str
    planting_date: str  # YYYY-MM-DD format
    county: str
    soil_type: str
    season: str
    temperature: Optional[float] = 25.0
    rainfall_mm: Optional[float] = 100.0
    pest_pressure: Optional[str] = "none"
    disease_occurrence: Optional[str] = "none"


class CalendarPredictionResponse(BaseModel):
    """Response model for calendar prediction"""
    next_practice: str
    practice_description: str
    days_until_practice: int
    recommended_date: str
    priority: str
    confidence: float
    alternative_practices: List[dict]
    current_growth_stage: str
    days_since_planting: int
    model_used: str


@router.post("/predict", response_model=CalendarPredictionResponse)
async def predict_next_practice(request: CalendarPredictionRequest):
    """
    Predict the next farming practice with AI
    
    Returns:
    - next_practice: Recommended practice
    - days_until_practice: Days from now
    - recommended_date: Date to perform practice
    - priority: high/medium/low
    - confidence: Model confidence (0-1)
    """
    try:
        # Parse planting date
        planting_date = datetime.strptime(request.planting_date, "%Y-%m-%d")
        days_since_planting = (datetime.now() - planting_date).days
        
        if days_since_planting < 0:
            raise HTTPException(status_code=400, detail="Planting date cannot be in the future")
        
        # Determine growth stage based on days since planting
        # Typical crop cycle: 0-20 days = seedling, 21-60 = vegetative, 
        # 61-90 = flowering, 91-110 = fruiting, 110+ = mature
        if days_since_planting <= 20:
            growth_stage = "seedling"
        elif days_since_planting <= 60:
            growth_stage = "vegetative"
        elif days_since_planting <= 90:
            growth_stage = "flowering"
        elif days_since_planting <= 110:
            growth_stage = "fruiting"
        else:
            growth_stage = "mature"
        
        # Make prediction
        prediction = ml_inference.predict_next_farming_practice(
            crop=request.crop,
            days_since_planting=days_since_planting,
            growth_stage=growth_stage,
            season=request.season,
            county=request.county,
            soil_type=request.soil_type,
            temperature=request.temperature,
            rainfall_mm=request.rainfall_mm,
            pest_pressure=request.pest_pressure,
            disease_occurrence=request.disease_occurrence
        )
        
        # Calculate recommended date
        recommended_date = datetime.now() + timedelta(days=prediction["days_until_practice"])
        
        return {
            "next_practice": prediction["next_practice"],
            "practice_description": prediction["practice_description"],
            "days_until_practice": prediction["days_until_practice"],
            "recommended_date": recommended_date.strftime("%Y-%m-%d"),
            "priority": prediction["priority"],
            "confidence": prediction["confidence"],
            "alternative_practices": prediction["alternative_practices"],
            "current_growth_stage": growth_stage,
            "days_since_planting": days_since_planting,
            "model_used": prediction["model_used"]
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


class CalendarScheduleRequest(BaseModel):
    """Request for full season calendar"""
    crop: str
    planting_date: str
    county: str
    soil_type: str
    season: str


@router.post("/schedule")
async def generate_season_schedule(request: CalendarScheduleRequest):
    """
    Generate a full season farming calendar
    
    Returns a list of all recommended practices with dates
    """
    try:
        planting_date = datetime.strptime(request.planting_date, "%Y-%m-%d")
        
        # Typical practices schedule (days after planting)
        practice_schedule = [
            {"practice": "land_preparation", "days": -14, "priority": "high"},
            {"practice": "planting", "days": 0, "priority": "high"},
            {"practice": "fertilizer_application", "days": 7, "priority": "high"},
            {"practice": "weeding", "days": 14, "priority": "medium"},
            {"practice": "pest_control", "days": 21, "priority": "medium"},
            {"practice": "disease_management", "days": 28, "priority": "medium"},
            {"practice": "fertilizer_application", "days": 30, "priority": "high"},
            {"practice": "weeding", "days": 35, "priority": "medium"},
            {"practice": "pest_control", "days": 42, "priority": "medium"},
            {"practice": "disease_management", "days": 56, "priority": "medium"},
            {"practice": "weeding", "days": 56, "priority": "low"},
            {"practice": "fertilizer_application", "days": 60, "priority": "medium"},
            {"practice": "pest_control", "days": 63, "priority": "medium"},
            {"practice": "harvesting", "days": 120, "priority": "high"},
            {"practice": "post_harvest_handling", "days": 125, "priority": "high"},
        ]
        
        # Build schedule with dates
        schedule = []
        for item in practice_schedule:
            practice_date = planting_date + timedelta(days=item["days"])
            schedule.append({
                "practice": item["practice"],
                "description": ml_inference._get_practice_description(item["practice"]),
                "date": practice_date.strftime("%Y-%m-%d"),
                "days_from_planting": item["days"],
                "priority": item["priority"],
                "status": "completed" if practice_date < datetime.now() else (
                    "upcoming" if (practice_date - datetime.now()).days <= 7 else "scheduled"
                )
            })
        
        return {
            "crop": request.crop,
            "planting_date": request.planting_date,
            "schedule": schedule,
            "total_practices": len(schedule)
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schedule generation error: {str(e)}")


@router.get("/model-status")
async def check_model_status():
    """Check if AI calendar model is available"""
    availability = ml_inference.check_model_availability()
    
    return {
        "ai_calendar_model_available": availability.get("ai_calendar", False),
        "model_path": str(ml_inference.model_paths.get("ai_calendar", ""))
    }


# ============================================================
# LIFECYCLE CALENDAR ENDPOINTS
# ============================================================

class LifecycleCalendarRequest(BaseModel):
    """Request for lifecycle calendar generation"""
    crop: str
    variety: str
    planting_date: str  # ISO format
    plot_id: str
    location: Optional[Dict[str, float]] = None
    soil_type: Optional[str] = None


@router.post("/lifecycle/generate")
async def generate_lifecycle_calendar(request: LifecycleCalendarRequest):
    """
    Generate comprehensive crop lifecycle calendar
    
    Features:
    - All growth stages with dates
    - Stage-specific practices
    - AI-optimized scheduling
    - Resource planning
    - Risk alerts
    
    Returns complete calendar from planting to harvest
    """
    try:
        calendar = lifecycle_calendar.generate_lifecycle_calendar(
            crop=request.crop,
            variety=request.variety,
            planting_date=request.planting_date,
            plot_id=request.plot_id,
            location=request.location,
            soil_type=request.soil_type
        )
        
        return calendar
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lifecycle/{plot_id}/current-stage")
async def get_current_growth_stage(plot_id: str, planting_date: str):
    """
    Get current growth stage for a plot
    
    Returns:
    - Current stage name
    - Days in current stage
    - Next stage information
    - Upcoming practices
    """
    try:
        from app.services.growth_model import get_current_growth_stage
        
        planting = datetime.fromisoformat(planting_date.replace('Z', ''))
        days_since_planting = (datetime.utcnow() - planting).days
        
        # This would need crop info - simplified for now
        stage = get_current_growth_stage("maize", "short_season", days_since_planting)
        
        return {
            "success": True,
            "plot_id": plot_id,
            "days_since_planting": days_since_planting,
            "current_stage": stage,
            "planting_date": planting_date
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lifecycle/stages/{crop}/{variety}")
async def get_crop_stages(crop: str, variety: str):
    """
    Get all growth stages for a specific crop variety
    
    Returns detailed stage information including:
    - Stage names and duration
    - Critical practices per stage
    - Monitoring requirements
    - Resource needs
    """
    try:
        from app.services.growth_model import CROP_GROWTH_MODELS
        
        crop_lower = crop.lower()
        variety_lower = variety.lower()
        
        if crop_lower not in CROP_GROWTH_MODELS:
            raise HTTPException(status_code=404, detail=f"Crop {crop} not found")
        
        crop_model = CROP_GROWTH_MODELS[crop_lower]
        
        if "varieties" in crop_model:
            if variety_lower in crop_model["varieties"]:
                variety_data = crop_model["varieties"][variety_lower]
                
                return {
                    "success": True,
                    "crop": crop,
                    "variety": variety,
                    "maturity_days": variety_data["maturity_days"],
                    "stages": variety_data["stages"],
                    "critical_practices": variety_data.get("critical_practices", {}),
                    "water_requirements": variety_data.get("water_requirements", {})
                }
        
        raise HTTPException(status_code=404, detail=f"Variety {variety} not found for {crop}")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lifecycle/practices/upcoming")
async def get_upcoming_practices(
    plot_id: str,
    planting_date: str,
    crop: str,
    variety: str,
    days_ahead: int = 14
):
    """
    Get upcoming practices for the next N days
    
    Returns practices scheduled within the specified timeframe
    with AI optimization status
    """
    try:
        calendar_result = lifecycle_calendar.generate_lifecycle_calendar(
            crop=crop,
            variety=variety,
            planting_date=planting_date,
            plot_id=plot_id
        )
        
        if not calendar_result.get("success"):
            raise HTTPException(status_code=400, detail=calendar_result.get("error"))
        
        calendar_data = calendar_result["calendar"]
        current_date = datetime.utcnow()
        cutoff_date = current_date + timedelta(days=days_ahead)
        
        upcoming = []
        for practice in calendar_data["practices"]:
            practice_date = datetime.fromisoformat(practice["scheduled_date"])
            
            if current_date <= practice_date <= cutoff_date:
                days_until = (practice_date - current_date).days
                practice["days_until"] = days_until
                upcoming.append(practice)
        
        # Sort by date
        upcoming.sort(key=lambda x: x["scheduled_date"])
        
        return {
            "success": True,
            "plot_id": plot_id,
            "days_ahead": days_ahead,
            "practices_count": len(upcoming),
            "practices": upcoming,
            "ai_enabled": calendar_result.get("ai_features_enabled", False)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lifecycle/milestones/{plot_id}")
async def get_crop_milestones(
    plot_id: str,
    crop: str,
    variety: str,
    planting_date: str
):
    """
    Get all major milestones in crop lifecycle
    
    Returns key events like:
    - Planting
    - First emergence
    - Flowering
    - Harvest readiness
    """
    try:
        calendar_result = lifecycle_calendar.generate_lifecycle_calendar(
            crop=crop,
            variety=variety,
            planting_date=planting_date,
            plot_id=plot_id
        )
        
        if not calendar_result.get("success"):
            raise HTTPException(status_code=400, detail=calendar_result.get("error"))
        
        calendar_data = calendar_result["calendar"]
        
        return {
            "success": True,
            "plot_id": plot_id,
            "milestones": calendar_data["milestones"],
            "expected_harvest_date": calendar_data["expected_harvest_date"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lifecycle/resources/{plot_id}")
async def get_resource_plan(
    plot_id: str,
    crop: str,
    variety: str,
    planting_date: str
):
    """
    Get resource requirements plan for entire crop lifecycle
    
    Returns:
    - Total labor hours needed
    - Estimated costs
    - Input requirements
    - Equipment needed
    - Breakdown by stage
    """
    try:
        calendar_result = lifecycle_calendar.generate_lifecycle_calendar(
            crop=crop,
            variety=variety,
            planting_date=planting_date,
            plot_id=plot_id
        )
        
        if not calendar_result.get("success"):
            raise HTTPException(status_code=400, detail=calendar_result.get("error"))
        
        calendar_data = calendar_result["calendar"]
        
        return {
            "success": True,
            "plot_id": plot_id,
            "crop": crop,
            "variety": variety,
            "resource_plan": calendar_data["resource_plan"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lifecycle/risks/{plot_id}")
async def get_risk_calendar(
    plot_id: str,
    crop: str,
    variety: str,
    planting_date: str
):
    """
    Get risk calendar showing potential issues by growth stage
    
    Returns:
    - Stage-specific risks (pests, diseases, weather)
    - Monitoring frequency
    - AI detection availability
    """
    try:
        calendar_result = lifecycle_calendar.generate_lifecycle_calendar(
            crop=crop,
            variety=variety,
            planting_date=planting_date,
            plot_id=plot_id
        )
        
        if not calendar_result.get("success"):
            raise HTTPException(status_code=400, detail=calendar_result.get("error"))
        
        calendar_data = calendar_result["calendar"]
        
        return {
            "success": True,
            "plot_id": plot_id,
            "risk_calendar": calendar_data["risk_calendar"],
            "ai_detection_available": calendar_data.get("ai_enabled", False)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/features/ai-status")
async def get_ai_calendar_features():
    """
    Get status of AI features in calendar system
    
    Returns which AI capabilities are available
    """
    try:
        from app.services.model_manager import get_model_manager
        
        model_manager = get_model_manager()
        models = model_manager.list_available_models()
        
        features = {
            "lifecycle_calendar": True,  # Always available
            "ai_scheduling": models.get("ai_calendar", {}).get("available", False),
            "weather_optimization": True,  # Rule-based available
            "pest_detection": models.get("pest_detection", {}).get("available", False),
            "disease_detection": models.get("disease_detection", {}).get("available", False),
            "plant_health_monitoring": models.get("plant_health", {}).get("available", False),
            "yield_prediction": models.get("yield_prediction", {}).get("available", False)
        }
        
        available_count = sum(1 for v in features.values() if v)
        
        return {
            "success": True,
            "features": features,
            "summary": {
                "total_features": len(features),
                "available_features": available_count,
                "percentage_ready": round((available_count / len(features)) * 100, 1)
            },
            "message": f"{available_count}/{len(features)} AI calendar features available"
        }
    
    except ImportError:
        return {
            "success": True,
            "features": {
                "lifecycle_calendar": True,
                "ai_scheduling": False,
                "weather_optimization": False,
                "pest_detection": False,
                "disease_detection": False,
                "plant_health_monitoring": False,
                "yield_prediction": False
            },
            "summary": {
                "total_features": 7,
                "available_features": 1,
                "percentage_ready": 14.3
            },
            "message": "1/7 AI calendar features available (basic lifecycle calendar only)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/crops/supported")
async def get_supported_crops():
    """
    Get list of crops supported by lifecycle calendar
    
    Returns crops with their varieties and maturity periods
    """
    try:
        from app.services.growth_model import CROP_GROWTH_MODELS
        
        crops = []
        
        for crop_name, crop_data in CROP_GROWTH_MODELS.items():
            varieties = []
            
            if "varieties" in crop_data:
                for variety_name, variety_data in crop_data["varieties"].items():
                    varieties.append({
                        "variety_id": variety_name,
                        "name": variety_data.get("name", variety_name),
                        "maturity_days": variety_data.get("maturity_days", 0),
                        "stages_count": len(variety_data.get("stages", {}))
                    })
            
            crops.append({
                "crop_id": crop_name,
                "crop_name": crop_name.title(),
                "varieties": varieties,
                "default_variety": crop_data.get("default_variety", "")
            })
        
        return {
            "success": True,
            "crops_count": len(crops),
            "crops": crops
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
