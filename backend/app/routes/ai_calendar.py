"""
AI Calendar API Routes
Provides AI-powered farming calendar recommendations
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
from app.services.ml_inference import ModelInferenceService

router = APIRouter()
ml_inference = ModelInferenceService()


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
async def get_model_status():
    """Check if AI calendar model is available"""
    availability = ml_inference.check_model_availability()
    
    return {
        "ai_calendar_model_available": availability.get("ai_calendar", False),
        "model_path": str(ml_inference.model_paths.get("ai_calendar", ""))
    }
