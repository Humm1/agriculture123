"""
Climate Engine API Routes

Endpoints for:
- Localized Climate Risk Score (LCRS)
- Planting window calculations
- Harvest predictions
- Soil moisture reports
- Crowdsourced rain reports
- Crop diversification recommendations
"""
from fastapi import APIRouter, Form, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, List
from app.services import climate_persistence, lcrs_engine, planting_window, harvest_prediction

router = APIRouter()

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class RainReportPayload(BaseModel):
    farmer_id: str
    location: Dict[str, float]  # {lat, lon}
    amount: str  # 'none' | 'light' | 'moderate' | 'heavy'

class SoilReportPayload(BaseModel):
    farmer_id: str
    field_id: str
    moisture_level: str  # 'dry' | 'damp' | 'saturated'

class LCRSRequest(BaseModel):
    farmer_id: str
    field_id: str
    location: Dict[str, float]
    forecast_months: Optional[int] = 3

class PlantingCheckRequest(BaseModel):
    farmer_id: str
    field_id: str
    crop: str
    location: Dict[str, float]

class PlantingRecordPayload(BaseModel):
    farmer_id: str
    field_id: str
    crop: str
    planting_date: str  # ISO date
    variety: Optional[str] = None
    area_hectares: Optional[float] = None

class HarvestAlertRequest(BaseModel):
    farmer_id: str
    field_id: str
    planting_date: str
    crop: str
    variety: Optional[str] = None
    location: Dict[str, float]
    sensor_id: Optional[str] = None
    language: Optional[str] = 'en'

class DiversificationRequest(BaseModel):
    farmer_id: str
    field_id: str
    location: Dict[str, float]
    total_area_hectares: float

# ============================================================================
# CROWDSOURCED DATA COLLECTION
# ============================================================================

@router.post('/rain_report')
async def submit_rain_report(payload: RainReportPayload):
    """Farmer submits crowdsourced rain report"""
    climate_persistence.add_rain_report(
        payload.farmer_id,
        payload.location,
        payload.amount
    )
    return JSONResponse({'submitted': True, 'message': 'Thank you for reporting rainfall!'})

@router.get('/rain_reports')
async def get_rain_reports(days: int = 7, lat: float = None, lon: float = None):
    """Get recent rain reports, optionally filtered by location"""
    location = {'lat': lat, 'lon': lon} if lat and lon else None
    reports = climate_persistence.get_rain_reports(days, location)
    return JSONResponse({'count': len(reports), 'reports': reports})

@router.post('/soil_report')
async def submit_soil_report(payload: SoilReportPayload):
    """Farmer submits soil moisture report"""
    climate_persistence.add_soil_report(
        payload.farmer_id,
        payload.field_id,
        payload.moisture_level
    )
    
    # Calculate SMI
    smi = climate_persistence.calculate_soil_moisture_index(payload.moisture_level)
    
    return JSONResponse({
        'submitted': True,
        'soil_moisture_index': smi,
        'message': f'Soil condition recorded: {payload.moisture_level} (SMI: {smi}%)'
    })

@router.get('/soil_report/{farmer_id}/{field_id}')
async def get_soil_report(farmer_id: str, field_id: str):
    """Get farmer's latest soil report"""
    report = climate_persistence.get_latest_soil_report(farmer_id, field_id)
    if not report:
        return JSONResponse({'error': 'No soil reports found'}, status_code=404)
    
    smi = climate_persistence.calculate_soil_moisture_index(report['moisture_level'])
    return JSONResponse({**report, 'soil_moisture_index': smi})

# ============================================================================
# LCRS (LOCALIZED CLIMATE RISK SCORE)
# ============================================================================

@router.post('/lcrs/calculate')
async def calculate_lcrs(payload: LCRSRequest):
    """Calculate Localized Climate Risk Score"""
    lcrs_data = lcrs_engine.calculate_lcrs(
        payload.farmer_id,
        payload.field_id,
        payload.location,
        payload.forecast_months
    )
    
    # Save to database
    climate_persistence.save_lcrs(
        payload.farmer_id,
        payload.field_id,
        lcrs_data['score'],
        lcrs_data['factors'],
        lcrs_data['valid_until']
    )
    
    return JSONResponse(lcrs_data)

@router.get('/lcrs/{farmer_id}/{field_id}')
async def get_lcrs(farmer_id: str, field_id: str):
    """Get cached LCRS for farmer's field"""
    lcrs_data = climate_persistence.get_lcrs(farmer_id, field_id)
    if not lcrs_data:
        return JSONResponse({'error': 'No LCRS calculated yet. Call /lcrs/calculate first.'}, status_code=404)
    
    return JSONResponse(lcrs_data)

# ============================================================================
# PLANTING WINDOW & ALERTS
# ============================================================================

@router.get('/planting_window/{crop}')
async def get_planting_window(crop: str, lat: float = None, lon: float = None):
    """Get optimal planting window for a crop"""
    location = {'lat': lat, 'lon': lon} if lat and lon else {}
    window = planting_window.get_optimal_planting_window(crop, location)
    return JSONResponse(window)

@router.post('/planting/check_status')
async def check_planting_status(payload: PlantingCheckRequest):
    """Check if farmer is on time, early, or late for planting"""
    status = planting_window.check_planting_status(
        payload.farmer_id,
        payload.field_id,
        payload.crop,
        payload.location
    )
    return JSONResponse(status)

@router.post('/planting/record')
async def record_planting(payload: PlantingRecordPayload):
    """Record when farmer plants a crop"""
    climate_persistence.add_planting_record(
        payload.farmer_id,
        payload.field_id,
        payload.crop,
        payload.planting_date,
        payload.variety,
        payload.area_hectares
    )
    return JSONResponse({'recorded': True, 'message': f'{payload.crop} planting recorded for {payload.planting_date}'})

@router.get('/planting/active/{farmer_id}')
async def get_active_plantings(farmer_id: str, field_id: str = None):
    """Get farmer's active plantings"""
    plantings = climate_persistence.get_active_plantings(farmer_id, field_id)
    return JSONResponse({'count': len(plantings), 'plantings': plantings})

# ============================================================================
# CROP DIVERSIFICATION
# ============================================================================

@router.post('/diversification/plan')
async def get_diversification_plan(payload: DiversificationRequest):
    """Generate crop diversification plan based on LCRS"""
    plan = planting_window.generate_diversification_plan(
        payload.farmer_id,
        payload.field_id,
        payload.location,
        payload.total_area_hectares
    )
    return JSONResponse(plan)

# ============================================================================
# HARVEST PREDICTION & ALERTS
# ============================================================================

@router.post('/harvest/predict')
async def predict_harvest(payload: HarvestAlertRequest):
    """Generate harvest prediction with weather forecast and storage check"""
    alert = harvest_prediction.generate_harvest_alert(
        payload.farmer_id,
        payload.field_id,
        payload.planting_date,
        payload.crop,
        payload.variety,
        payload.location,
        payload.sensor_id,
        payload.language
    )
    return JSONResponse(alert)

@router.get('/harvest/predictions/{farmer_id}')
async def get_harvest_predictions(farmer_id: str):
    """Get all harvest predictions for farmer"""
    predictions = climate_persistence.get_harvest_predictions(farmer_id)
    return JSONResponse({'count': len(predictions), 'predictions': predictions})

@router.get('/harvest/calendar/{farmer_id}')
async def get_harvest_calendar(farmer_id: str):
    """
    Get harvest calendar showing all upcoming harvests with alerts.
    Automatically checks weather and storage for each.
    """
    plantings = climate_persistence.get_active_plantings(farmer_id)
    calendar = []
    
    for planting in plantings:
        # Predict harvest
        harvest_pred = harvest_prediction.predict_harvest_date(
            planting['planting_date'],
            planting['crop'],
            planting.get('variety')
        )
        
        calendar.append({
            'field_id': planting['field_id'],
            'crop': planting['crop'],
            'variety': planting.get('variety'),
            'planting_date': planting['planting_date'],
            'harvest_date': harvest_pred['predicted_date'],
            'harvest_window': {
                'start': harvest_pred['harvest_window_start'],
                'end': harvest_pred['harvest_window_end']
            },
            'maturity_days': harvest_pred['maturity_days']
        })
    
    # Sort by harvest date
    calendar.sort(key=lambda x: x['harvest_date'])
    
    return JSONResponse({'count': len(calendar), 'calendar': calendar})

# ============================================================================
# DASHBOARD / SUMMARY
# ============================================================================

@router.get('/dashboard/{farmer_id}')
async def get_farmer_dashboard(farmer_id: str, field_id: str = None):
    """
    Get comprehensive farmer dashboard with:
    - Latest LCRS
    - Active plantings
    - Upcoming harvests
    - Recent soil/rain reports
    """
    # Get LCRS
    lcrs_data = climate_persistence.get_lcrs(farmer_id, field_id or 'default')
    
    # Get active plantings
    plantings = climate_persistence.get_active_plantings(farmer_id, field_id)
    
    # Get harvest predictions
    predictions = climate_persistence.get_harvest_predictions(farmer_id)
    
    # Get latest soil report
    soil_report = None
    if field_id:
        soil_report = climate_persistence.get_latest_soil_report(farmer_id, field_id)
    
    return JSONResponse({
        'lcrs': lcrs_data,
        'active_plantings': {'count': len(plantings), 'plantings': plantings},
        'upcoming_harvests': {'count': len(predictions), 'predictions': predictions},
        'latest_soil_report': soil_report
    })
