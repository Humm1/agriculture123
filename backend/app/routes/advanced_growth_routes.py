"""
Advanced Growth Tracking API Routes
Comprehensive plant growth monitoring with AI analysis
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import uuid
import os
from pathlib import Path

from app.services.advanced_growth_tracking import AdvancedGrowthTrackingService
from app.services.supabase_client import get_supabase_client

router = APIRouter()

# Ensure uploads directory exists
UPLOAD_DIR = Path("uploads/plots")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# REQUEST/RESPONSE MODELS
# ============================================================

class LocationModel(BaseModel):
    latitude: float
    longitude: float

class CreatePlotRequest(BaseModel):
    crop_name: str
    plot_name: str
    initial_image_url: str
    planting_date: str  # ISO format
    location: LocationModel
    soil_image_url: Optional[str] = None
    area_size: Optional[float] = None
    notes: Optional[str] = None

class CreateGrowthLogRequest(BaseModel):
    plot_id: str
    image_urls: List[str]
    log_type: str = "regular_checkin"  # initial_setup, regular_checkin, milestone, harvest
    notes: Optional[str] = None

class DiagnosePestDiseaseRequest(BaseModel):
    plot_id: str
    image_url: str
    location: LocationModel

class ManualPlotCreationRequest(BaseModel):
    crop_name: str
    plot_name: str
    planting_date: str  # ISO format
    latitude: float
    longitude: float
    area_size: Optional[float] = None
    notes: Optional[str] = None
    soil_type: Optional[str] = None

# ============================================================
# IMAGE UPLOAD ENDPOINTS
# ============================================================

@router.post("/upload/plot-image")
async def upload_plot_image(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    image_type: str = Form("initial")  # initial, progress, soil, pest, harvest
):
    """
    Upload plot image (initial, progress, soil, pest, or harvest photo)
    
    Returns URL to uploaded image
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Generate unique filename
        file_extension = file.filename.split('.')[-1]
        unique_filename = f"{user_id}_{uuid.uuid4()}.{file_extension}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Return URL with proper base URL
        # Use environment variable or default to DigitalOcean URL
        base_url = os.getenv('API_BASE_URL', 'https://urchin-app-86rjy.ondigitalocean.app')
        image_url = f"{base_url}/uploads/plots/{unique_filename}"
        
        return {
            "success": True,
            "image_url": image_url,
            "filename": unique_filename,
            "image_type": image_type
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/plots/create-manual")
async def create_plot_manual(
    user_id: str = Form(...),
    crop_name: str = Form(...),
    plot_name: str = Form(...),
    planting_date: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    area_size: Optional[float] = Form(None),
    notes: Optional[str] = Form(None),
    soil_type: Optional[str] = Form(None),
    initial_image: Optional[UploadFile] = File(None),
    soil_image: Optional[UploadFile] = File(None)
):
    """
    Create plot with manual data entry and optional image uploads
    
    Accepts:
    - Form data for plot details
    - Optional initial plant image
    - Optional soil image
    
    Returns:
    - Created plot with scheduled events
    """
    try:
        supabase = get_supabase_client()
        
        # Upload images if provided
        initial_image_url = None
        soil_image_url = None
        
        if initial_image:
            # Save initial image
            file_extension = initial_image.filename.split('.')[-1]
            unique_filename = f"{user_id}_initial_{uuid.uuid4()}.{file_extension}"
            file_path = UPLOAD_DIR / unique_filename
            
            with open(file_path, "wb") as buffer:
                content = await initial_image.read()
                buffer.write(content)
            
            base_url = os.getenv('API_BASE_URL', 'https://urchin-app-86rjy.ondigitalocean.app')
            initial_image_url = f"{base_url}/uploads/plots/{unique_filename}"
            print(f"Initial image saved: {initial_image_url}")
        
        if soil_image:
            # Save soil image
            file_extension = soil_image.filename.split('.')[-1]
            unique_filename = f"{user_id}_soil_{uuid.uuid4()}.{file_extension}"
            file_path = UPLOAD_DIR / unique_filename
            
            with open(file_path, "wb") as buffer:
                content = await soil_image.read()
                buffer.write(content)
            
            base_url = os.getenv('API_BASE_URL', 'https://urchin-app-86rjy.ondigitalocean.app')
            soil_image_url = f"{base_url}/uploads/plots/{unique_filename}"
            print(f"Soil image saved: {soil_image_url}")
        
        # Create plot in database
        plot_id = str(uuid.uuid4())
        plot_data = {
            "id": plot_id,
            "user_id": user_id,
            "crop_name": crop_name,
            "plot_name": plot_name,
            "planting_date": planting_date,
            "location": {
                "latitude": latitude,
                "longitude": longitude
            },
            "area_size": area_size,
            "notes": notes,
            "initial_image_url": initial_image_url or "https://via.placeholder.com/400x300?text=No+Image",
            "soil_image_url": soil_image_url,
            "setup_completed_at": datetime.utcnow().isoformat(),
            "soil_analysis": {
                "soil_type": soil_type or "Not analyzed",
                "manually_entered": True
            }
        }
        
        result = supabase.table('digital_plots').insert(plot_data).execute()
        
        # Create initial scheduled events for the plot
        from ..services.growth_calendar_integration import generate_seasonal_calendar
        
        try:
            calendar_events = await generate_seasonal_calendar(
                plot_id=plot_id,
                user_id=user_id,
                crop_name=crop_name,
                planting_date=planting_date,
                location={"latitude": latitude, "longitude": longitude},
                supabase_client=supabase
            )
        except Exception as e:
            print(f"Calendar generation error: {e}")
            calendar_events = None
        
        # Save uploaded images to plot_images table if provided
        if initial_image_url or soil_image_url:
            images_to_insert = []
            
            if initial_image_url:
                image_record = {
                    "id": str(uuid.uuid4()),
                    "plot_id": plot_id,
                    "user_id": user_id,
                    "image_url": initial_image_url,
                    "image_type": "initial",
                    "description": "Initial plot image",
                    "captured_at": planting_date
                }
                images_to_insert.append(image_record)
                print(f"Inserting initial image record: {image_record}")
            
            if soil_image_url:
                image_record = {
                    "id": str(uuid.uuid4()),
                    "plot_id": plot_id,
                    "user_id": user_id,
                    "image_url": soil_image_url,
                    "image_type": "soil",
                    "description": "Soil sample image",
                    "captured_at": planting_date
                }
                images_to_insert.append(image_record)
                print(f"Inserting soil image record: {image_record}")
            
            if images_to_insert:
                try:
                    image_result = supabase.table('plot_images').insert(images_to_insert).execute()
                    print(f"Images inserted successfully: {len(images_to_insert)} images")
                    print(f"Insert result: {image_result.data}")
                except Exception as img_error:
                    print(f"Error inserting images to plot_images table: {img_error}")
                    # Don't fail the whole request if image insert fails
                    pass
        
        return {
            "success": True,
            "message": "Plot created successfully!",
            "plot": result.data[0] if result.data else None,
            "plot_id": plot_id,
            "calendar_events": calendar_events
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# 1. DIGITAL PLOT SETUP
# ============================================================

@router.post("/plots/create")
async def create_digital_plot(request: CreatePlotRequest, user_id: str = "demo_user"):
    """
    Create a new digital plot with comprehensive setup
    
    User provides:
    - Initial photo of plant/planting area
    - Planting date from calendar
    - Location (crucial for regional predictions)
    - Soil image for analysis
    
    AI analyzes:
    - Soil type, organic matter, pH
    - Provides soil recommendations
    """
    try:
        supabase = get_supabase_client()
        service = AdvancedGrowthTrackingService(supabase)
        
        result = await service.create_digital_plot(
            user_id=user_id,
            crop_name=request.crop_name,
            plot_name=request.plot_name,
            initial_image_url=request.initial_image_url,
            planting_date=request.planting_date,
            location=request.location.dict(),
            soil_image_url=request.soil_image_url,
            area_size=request.area_size,
            notes=request.notes
        )
        
        return {
            "success": True,
            "message": "Digital plot created successfully!",
            "data": result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/soil/analyze")
async def analyze_soil(image_url: str):
    """
    Analyze soil image using AI
    
    Returns:
    - Soil type (Clay, Loam, Sandy, etc.)
    - Organic matter content
    - pH range estimate
    - Moisture level
    - Improvement recommendations
    """
    try:
        supabase = get_supabase_client()
        service = AdvancedGrowthTrackingService(supabase)
        
        analysis = await service.analyze_soil_ai(image_url)
        
        return {
            "success": True,
            "soil_analysis": analysis
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/plots/{plot_id}")
async def get_plot_details(plot_id: str):
    """Get comprehensive plot details including setup and logs"""
    try:
        supabase = get_supabase_client()
        
        # Fetch plot
        plot = supabase.table('digital_plots')\
            .select('*')\
            .eq('id', plot_id)\
            .single()\
            .execute()
        
        # Fetch recent logs
        logs = supabase.table('growth_logs')\
            .select('*')\
            .eq('plot_id', plot_id)\
            .order('timestamp', desc=True)\
            .limit(10)\
            .execute()
        
        return {
            "success": True,
            "plot": plot.data,
            "recent_logs": logs.data
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/plots/user/{user_id}")
async def get_user_plots(user_id: str):
    """Get all plots for a user"""
    try:
        supabase = get_supabase_client()
        
        plots = supabase.table('digital_plots')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('setup_completed_at', desc=True)\
            .execute()
        
        return {
            "success": True,
            "plots": plots.data,
            "count": len(plots.data)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# 2. GROWTH LOGS & CHECK-INS
# ============================================================

@router.post("/logs/create")
async def create_growth_log(request: CreateGrowthLogRequest, user_id: str = "demo_user"):
    """
    Create growth log with AI health analysis
    
    User uploads photos focusing on:
    - Leaves (chlorophyll/nitrogen analysis)
    - Stems (structural health)
    - Fruit/flowers (development stage)
    
    AI analyzes:
    - Growth rate vs previous photos
    - Chlorophyll/Nitrogen index
    - Water stress indicators
    - Overall health score (1-100)
    """
    try:
        supabase = get_supabase_client()
        service = AdvancedGrowthTrackingService(supabase)
        
        result = await service.create_growth_log(
            plot_id=request.plot_id,
            user_id=user_id,
            image_urls=request.image_urls,
            log_type=request.log_type,
            notes=request.notes
        )
        
        return {
            "success": True,
            "message": "Growth log created with AI analysis!",
            "data": result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/health/analyze")
async def analyze_plant_health(image_url: str):
    """
    Comprehensive plant health analysis
    
    Analyzes:
    - Overall health score (1-100)
    - Chlorophyll index
    - Nitrogen status
    - Water stress
    - Growth stage
    - Biomarkers and alerts
    """
    try:
        supabase = get_supabase_client()
        service = AdvancedGrowthTrackingService(supabase)
        
        analysis = await service.analyze_plant_health_comprehensive(image_url)
        
        return {
            "success": True,
            "health_analysis": analysis
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs/plot/{plot_id}")
async def get_plot_logs(plot_id: str, limit: int = 20):
    """Get growth logs for a plot"""
    try:
        supabase = get_supabase_client()
        
        logs = supabase.table('growth_logs')\
            .select('*')\
            .eq('plot_id', plot_id)\
            .order('timestamp', desc=True)\
            .limit(limit)\
            .execute()
        
        return {
            "success": True,
            "logs": logs.data,
            "count": len(logs.data)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard/{plot_id}")
async def get_health_dashboard(plot_id: str):
    """
    Get comprehensive health dashboard for a plot
    
    Includes:
    - Current health metrics
    - Growth progress over time
    - Active alerts
    - Biomarker trends
    """
    try:
        supabase = get_supabase_client()
        
        # Get latest log
        latest_log = supabase.table('growth_logs')\
            .select('*')\
            .eq('plot_id', plot_id)\
            .order('timestamp', desc=True)\
            .limit(1)\
            .execute()
        
        if not latest_log.data:
            raise HTTPException(status_code=404, detail="No logs found for this plot")
        
        log = latest_log.data[0]
        health_analysis = log.get('health_analysis', {})
        growth_comparison = log.get('growth_comparison', {})
        
        # Get historical data for trends
        all_logs = supabase.table('growth_logs')\
            .select('*')\
            .eq('plot_id', plot_id)\
            .order('timestamp', desc=False)\
            .execute()
        
        # Build trend data
        health_trend = [
            {
                "timestamp": l.get('timestamp'),
                "health_score": l.get('health_analysis', {}).get('overall_health_score', 0),
                "chlorophyll_index": l.get('health_analysis', {}).get('chlorophyll_index', 0)
            }
            for l in all_logs.data
        ]
        
        return {
            "success": True,
            "dashboard": {
                "current_status": {
                    "health_score": health_analysis.get('overall_health_score', 0),
                    "health_grade": health_analysis.get('health_grade', 'N/A'),
                    "chlorophyll_index": health_analysis.get('chlorophyll_index', 0),
                    "nitrogen_status": health_analysis.get('nitrogen_status', 'Unknown'),
                    "water_stress": health_analysis.get('water_stress', 'Unknown'),
                    "growth_stage": health_analysis.get('growth_stage', 'Unknown')
                },
                "growth_progress": growth_comparison,
                "alerts": health_analysis.get('alerts', []),
                "biomarkers": health_analysis.get('biomarkers', {}),
                "trends": {
                    "health_history": health_trend
                },
                "last_updated": log.get('timestamp')
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# 3. PEST & DISEASE DIAGNOSIS
# ============================================================

@router.post("/diagnosis/comprehensive")
async def diagnose_pest_disease_comprehensive(request: DiagnosePestDiseaseRequest):
    """
    Comprehensive pest/disease diagnosis with regional intelligence
    
    AI analyzes:
    1. Visual symptoms (powdery mildew, aphid damage, leaf spots)
    2. Regional weather and nearby reports
    3. Impact on yield and quality
    4. Actionable treatment plan
    
    Output includes:
    - "Alert: Hornworms reported by 3 growers within 15 miles. Your risk is High."
    - "Early Blight will reduce yield by 30-40% if untreated"
    - Specific treatment recommendations
    """
    try:
        supabase = get_supabase_client()
        service = AdvancedGrowthTrackingService(supabase)
        
        diagnosis = await service.diagnose_pest_disease_regional(
            plot_id=request.plot_id,
            image_url=request.image_url,
            location=request.location.dict()
        )
        
        # Save diagnosis to database
        diagnosis_data = {
            "plot_id": request.plot_id,
            "user_id": request.user_id if hasattr(request, 'user_id') else None,
            "image_url": request.image_url,
            "location": request.location.dict(),
            "diagnosis": diagnosis.get("diagnosis"),
            "regional_intelligence": diagnosis.get("regional_intelligence"),
            "impact_assessment": diagnosis.get("impact_assessment"),
            "treatment_plan": diagnosis.get("treatment_plan")
        }
        
        saved_diagnosis = supabase.table('pest_disease_diagnoses').insert(diagnosis_data).execute()
        
        # 🌱 AI CALENDAR: Auto-schedule treatment events
        calendar_result = None
        try:
            from ..services.growth_calendar_integration import schedule_treatment_from_diagnosis
            
            calendar_result = await schedule_treatment_from_diagnosis(
                plot_id=request.plot_id,
                user_id=request.user_id if hasattr(request, 'user_id') else None,
                diagnosis=diagnosis.get("diagnosis"),
                treatment_plan=diagnosis.get("treatment_plan"),
                supabase_client=supabase
            )
        except Exception as e:
            print(f"Treatment scheduling error: {e}")
        
        return {
            "success": True,
            "diagnosis": diagnosis,
            "diagnosis_id": saved_diagnosis.data[0]["id"] if saved_diagnosis.data else None,
            "treatment_schedule": calendar_result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/diagnosis/regional-risk/{plot_id}")
async def get_regional_pest_risk(plot_id: str):
    """
    Get regional pest/disease risk for a plot
    
    Shows:
    - Nearby pest/disease reports
    - Active threats in the region
    - Weather factors
    - Risk level
    """
    try:
        supabase = get_supabase_client()
        
        # Get plot location
        plot = supabase.table('digital_plots')\
            .select('location')\
            .eq('id', plot_id)\
            .single()\
            .execute()
        
        location = plot.data.get('location', {})
        service = AdvancedGrowthTrackingService(supabase)
        
        risk = await service._assess_regional_risk(location, [])
        
        return {
            "success": True,
            "regional_risk": risk
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# 4. HARVEST & QUALITY FORECASTING
# ============================================================

@router.get("/forecast/harvest/{plot_id}")
async def forecast_harvest(plot_id: str):
    """
    AI-powered harvest forecasting
    
    Uses:
    - Planting date
    - Current health score
    - Growth rate
    - Pest pressure
    
    Predicts:
    - Estimated harvest date
    - Quality score (A+ to C-)
    - Yield estimate
    - Recommendations for improvement
    
    Example output:
    - "Estimated Harvest: August 10-20"
    - "5 days later than average due to early-season water stress"
    - "Current Predicted Quality: B-"
    - "You can improve to A by treating Early Blight this week"
    """
    try:
        supabase = get_supabase_client()
        service = AdvancedGrowthTrackingService(supabase)
        
        forecast = await service.forecast_harvest_quality(plot_id)
        
        return {
            "success": True,
            "forecast": forecast
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/forecast/quality/{plot_id}")
async def get_quality_prediction(plot_id: str):
    """
    Get quality prediction and improvement recommendations
    
    Shows:
    - Current predicted quality score
    - Factors affecting quality
    - Recommendations to improve
    - Potential quality gain from each action
    """
    try:
        supabase = get_supabase_client()
        service = AdvancedGrowthTrackingService(supabase)
        
        forecast = await service.forecast_harvest_quality(plot_id)
        
        return {
            "success": True,
            "quality_prediction": forecast.get('quality_prediction', {}),
            "recommendations": forecast.get('recommendations', [])
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# CALENDAR & SCHEDULED EVENTS ENDPOINTS
# ============================================================

@router.get("/calendar/{plot_id}")
async def get_plot_calendar(plot_id: str, status: Optional[str] = None):
    """
    Get scheduled events for a plot
    
    Filters:
    - status: scheduled, completed, in_progress, skipped, cancelled
    
    Returns all farm practices, photo reminders, and treatments
    """
    try:
        supabase = get_supabase_client()
        
        query = supabase.table('scheduled_events')\
            .select('*')\
            .eq('plot_id', plot_id)\
            .order('scheduled_date', desc=False)
        
        if status:
            query = query.eq('status', status)
        
        events = query.execute()
        
        # Group by event type
        grouped_events = {
            "farm_practices": [],
            "photo_reminders": [],
            "treatment_applications": [],
            "urgent_practices": [],
            "alert_actions": []
        }
        
        for event in events.data:
            event_type = event.get('event_type', 'farm_practice')
            if event_type in grouped_events:
                grouped_events[event_type].append(event)
        
        return {
            "success": True,
            "plot_id": plot_id,
            "total_events": len(events.data),
            "grouped_events": grouped_events,
            "all_events": events.data
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/calendar/user/{user_id}/upcoming")
async def get_user_upcoming_events(
    user_id: str,
    days_ahead: int = 7
):
    """
    Get upcoming events for user across all plots
    
    Perfect for dashboard "What's Next" section
    """
    try:
        supabase = get_supabase_client()
        
        future_date = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat()
        
        events = supabase.table('scheduled_events')\
            .select('*, digital_plots(plot_name, crop_name)')\
            .eq('user_id', user_id)\
            .eq('status', 'scheduled')\
            .gte('scheduled_date', datetime.utcnow().isoformat())\
            .lte('scheduled_date', future_date)\
            .order('scheduled_date', desc=False)\
            .execute()
        
        # Group by date
        events_by_date = {}
        for event in events.data:
            date_key = event['scheduled_date'][:10]  # YYYY-MM-DD
            if date_key not in events_by_date:
                events_by_date[date_key] = []
            events_by_date[date_key].append(event)
        
        return {
            "success": True,
            "user_id": user_id,
            "days_ahead": days_ahead,
            "total_events": len(events.data),
            "events_by_date": events_by_date,
            "all_events": events.data
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/calendar/event/{event_id}/complete")
async def complete_event(
    event_id: str,
    completion_notes: Optional[str] = None,
    actual_labor_hours: Optional[float] = None,
    completion_images: Optional[List[str]] = None
):
    """
    Mark event as completed
    
    Records:
    - Completion date
    - Notes
    - Actual labor hours
    - Photos of completed work
    """
    try:
        supabase = get_supabase_client()
        
        update_data = {
            "status": "completed",
            "completed_date": datetime.utcnow().isoformat()
        }
        
        if completion_notes:
            update_data["completion_notes"] = completion_notes
        if actual_labor_hours:
            update_data["actual_labor_hours"] = actual_labor_hours
        if completion_images:
            update_data["completion_images"] = completion_images
        
        result = supabase.table('scheduled_events')\
            .update(update_data)\
            .eq('id', event_id)\
            .execute()
        
        return {
            "success": True,
            "message": "Event marked as completed",
            "event": result.data[0] if result.data else None
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/calendar/event/{event_id}/reschedule")
async def reschedule_event(
    event_id: str,
    new_date: str,
    reason: Optional[str] = None
):
    """
    Reschedule an event
    
    Useful when weather, health issues, or other factors delay work
    """
    try:
        supabase = get_supabase_client()
        
        # Get original date
        event = supabase.table('scheduled_events')\
            .select('scheduled_date')\
            .eq('id', event_id)\
            .single()\
            .execute()
        
        update_data = {
            "scheduled_date": new_date,
            "original_date": event.data.get('scheduled_date'),
            "adjustment_reason": reason or "User rescheduled",
            "adjusted_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table('scheduled_events')\
            .update(update_data)\
            .eq('id', event_id)\
            .execute()
        
        return {
            "success": True,
            "message": "Event rescheduled successfully",
            "event": result.data[0] if result.data else None
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/calendar/event/custom")
async def create_custom_event(
    plot_id: str,
    user_id: str,
    practice_name: str,
    scheduled_date: str,
    description: Optional[str] = None,
    priority: str = "moderate"
):
    """
    Create custom event (user-created, not AI-generated)
    
    Allows farmers to add their own practices to calendar
    """
    try:
        supabase = get_supabase_client()
        
        event_data = {
            "plot_id": plot_id,
            "user_id": user_id,
            "event_type": "farm_practice",
            "practice_name": practice_name,
            "scheduled_date": scheduled_date,
            "description": description or f"Custom practice: {practice_name}",
            "priority": priority,
            "status": "scheduled",
            "source": "user_created",
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table('scheduled_events')\
            .insert(event_data)\
            .execute()
        
        return {
            "success": True,
            "message": "Custom event created",
            "event": result.data[0] if result.data else None
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/calendar/event/{event_id}")
async def delete_event(event_id: str):
    """Delete/cancel scheduled event"""
    try:
        supabase = get_supabase_client()
        
        result = supabase.table('scheduled_events')\
            .delete()\
            .eq('id', event_id)\
            .execute()
        
        return {
            "success": True,
            "message": "Event deleted successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# UTILITY ENDPOINTS
# ============================================================

@router.post("/seed-demo-data/{user_id}")
async def seed_demo_data(user_id: str):
    """
    Create demo plot and events for testing
    Useful when a user has no plots yet
    """
    try:
        supabase = get_supabase_client()
        from datetime import timedelta
        import uuid
        
        # Create demo plot
        plot_id = str(uuid.uuid4())
        plot_data = {
            "id": plot_id,
            "user_id": user_id,
            "plot_name": "Demo Maize Plot",
            "crop_name": "Maize",
            "initial_image_url": "https://example.com/maize-initial.jpg",
            "planting_date": datetime.utcnow().isoformat(),
            "location": {
                "latitude": -1.286389,
                "longitude": 36.817223
            },
            "area_size": 2.5,
            "notes": "Demo plot for growth tracking",
            "setup_completed_at": datetime.utcnow().isoformat()
        }
        
        supabase.table('digital_plots').insert(plot_data).execute()
        
        # Create demo events
        events = [
            {
                "id": str(uuid.uuid4()),
                "plot_id": plot_id,
                "user_id": user_id,
                "event_type": "farm_practice",
                "practice_name": "Irrigation",
                "scheduled_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
                "status": "scheduled",
                "description": "Water the crops - soil moisture is low",
                "priority": "urgent",
                "estimated_labor_hours": 3
            },
            {
                "id": str(uuid.uuid4()),
                "plot_id": plot_id,
                "user_id": user_id,
                "event_type": "photo_reminder",
                "practice_name": "Weekly Photo Check",
                "scheduled_date": (datetime.utcnow() + timedelta(days=2)).isoformat(),
                "status": "scheduled",
                "description": "Take photos of plant growth for AI analysis",
                "priority": "medium",
                "estimated_labor_hours": 0.5
            },
            {
                "id": str(uuid.uuid4()),
                "plot_id": plot_id,
                "user_id": user_id,
                "event_type": "farm_practice",
                "practice_name": "Weeding",
                "scheduled_date": (datetime.utcnow() + timedelta(days=3)).isoformat(),
                "status": "scheduled",
                "description": "Manual weeding to remove competing plants",
                "priority": "high",
                "estimated_labor_hours": 4
            },
            {
                "id": str(uuid.uuid4()),
                "plot_id": plot_id,
                "user_id": user_id,
                "event_type": "alert_action",
                "practice_name": "Pest Monitoring",
                "scheduled_date": (datetime.utcnow() + timedelta(days=5)).isoformat(),
                "status": "scheduled",
                "description": "Check for fall armyworm and other pests",
                "priority": "high",
                "estimated_labor_hours": 1
            },
            {
                "id": str(uuid.uuid4()),
                "plot_id": plot_id,
                "user_id": user_id,
                "event_type": "farm_practice",
                "practice_name": "Fertilizer Application",
                "scheduled_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
                "status": "scheduled",
                "description": "Apply NPK 23:23:0 fertilizer",
                "priority": "high",
                "estimated_labor_hours": 2
            }
        ]
        
        supabase.table('scheduled_events').insert(events).execute()
        
        return {
            "success": True,
            "message": f"Demo data created successfully for user {user_id}",
            "plot_id": plot_id,
            "events_created": len(events)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check for advanced growth tracking system"""
    return {
        "status": "healthy",
        "service": "Advanced Growth Tracking",
        "features": [
            "Digital plot setup with soil analysis",
            "Regular health check-ins with biomarker tracking",
            "Pest/disease diagnosis with regional risk",
            "Harvest forecasting and quality prediction"
        ],
        "version": "1.0.0"
    }

@router.get("/stats/user/{user_id}")
async def get_user_stats(user_id: str):
    """Get user statistics across all plots"""
    try:
        supabase = get_supabase_client()
        
        # Get all user plots
        plots = supabase.table('digital_plots')\
            .select('*')\
            .eq('user_id', user_id)\
            .execute()
        
        # Get all logs
        total_logs = 0
        avg_health = []
        
        for plot in plots.data:
            logs = supabase.table('growth_logs')\
                .select('*')\
                .eq('plot_id', plot['id'])\
                .execute()
            
            total_logs += len(logs.data)
            
            for log in logs.data:
                health = log.get('health_analysis', {}).get('overall_health_score')
                if health:
                    avg_health.append(health)
        
        return {
            "success": True,
            "stats": {
                "total_plots": len(plots.data),
                "active_plots": sum(1 for p in plots.data if p.get('status') == 'active'),
                "total_check_ins": total_logs,
                "average_health_score": round(sum(avg_health) / len(avg_health), 1) if avg_health else 0,
                "plots_monitored": [
                    {
                        "id": p['id'],
                        "name": p['plot_name'],
                        "crop": p['crop_name'],
                        "days_since_planting": (datetime.utcnow() - datetime.fromisoformat(p['planting_date'])).days
                    }
                    for p in plots.data
                ]
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
