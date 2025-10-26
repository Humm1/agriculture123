"""
Climate data persistence for weather, soil moisture, and risk scores.
Stores crowdsourced rain reports, soil moisture index, and LCRS calculations.
"""
import json
from pathlib import Path
from threading import Lock
from datetime import datetime, timedelta
from typing import List, Dict, Optional

BASE = Path(__file__).resolve().parent.parent / 'data'
BASE.mkdir(exist_ok=True)
_lock = Lock()

def _load(fname, default):
    path = BASE / fname
    if not path.exists():
        return default
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)

def _save(fname, data):
    path = BASE / fname
    with _lock:
        with path.open('w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)

# ============================================================================
# WEATHER & RAIN REPORTS
# ============================================================================

def add_rain_report(farmer_id: str, location: dict, amount: str, ts: str = None):
    """Add crowdsourced rain report: {farmer_id, location: {lat, lon}, amount: 'none'|'light'|'moderate'|'heavy', ts}"""
    reports = _load('rain_reports.json', [])
    if not ts:
        ts = datetime.utcnow().isoformat()
    reports.append({
        'farmer_id': farmer_id,
        'location': location,
        'amount': amount,
        'ts': ts
    })
    _save('rain_reports.json', reports)

def get_rain_reports(days: int = 7, location: dict = None) -> List[Dict]:
    """Get rain reports from last N days, optionally filtered by location proximity"""
    reports = _load('rain_reports.json', [])
    cutoff = datetime.utcnow() - timedelta(days=days)
    recent = [r for r in reports if datetime.fromisoformat(r['ts']) >= cutoff]
    
    if location and 'lat' in location and 'lon' in location:
        # Simple proximity filter (within ~50km = 0.5 degrees)
        lat, lon = location['lat'], location['lon']
        recent = [r for r in recent if abs(r['location']['lat'] - lat) < 0.5 and abs(r['location']['lon'] - lon) < 0.5]
    
    return recent

# ============================================================================
# SOIL MOISTURE REPORTS
# ============================================================================

def add_soil_report(farmer_id: str, field_id: str, moisture_level: str, ts: str = None):
    """Add farmer's soil moisture report: 'dry', 'damp', 'saturated'"""
    reports = _load('soil_reports.json', {})
    if not ts:
        ts = datetime.utcnow().isoformat()
    
    if farmer_id not in reports:
        reports[farmer_id] = {}
    if field_id not in reports[farmer_id]:
        reports[farmer_id][field_id] = []
    
    reports[farmer_id][field_id].append({
        'moisture_level': moisture_level,
        'ts': ts
    })
    _save('soil_reports.json', reports)

def get_latest_soil_report(farmer_id: str, field_id: str) -> Optional[Dict]:
    """Get farmer's latest soil moisture report for a field"""
    reports = _load('soil_reports.json', {})
    if farmer_id not in reports or field_id not in reports[farmer_id]:
        return None
    field_reports = reports[farmer_id][field_id]
    return field_reports[-1] if field_reports else None

def calculate_soil_moisture_index(moisture_level: str) -> float:
    """Convert qualitative soil moisture to numeric index (0-100)"""
    levels = {
        'dry': 20,
        'damp': 60,
        'saturated': 95
    }
    return levels.get(moisture_level.lower(), 50)

# ============================================================================
# LCRS (Localized Climate Risk Score)
# ============================================================================

def save_lcrs(farmer_id: str, field_id: str, score: float, factors: dict, valid_until: str):
    """Save calculated LCRS for a farmer's field"""
    all_scores = _load('lcrs_scores.json', {})
    if farmer_id not in all_scores:
        all_scores[farmer_id] = {}
    
    all_scores[farmer_id][field_id] = {
        'score': score,
        'factors': factors,
        'calculated_at': datetime.utcnow().isoformat(),
        'valid_until': valid_until
    }
    _save('lcrs_scores.json', all_scores)

def get_lcrs(farmer_id: str, field_id: str) -> Optional[Dict]:
    """Get latest LCRS for farmer's field"""
    all_scores = _load('lcrs_scores.json', {})
    if farmer_id not in all_scores or field_id not in all_scores[farmer_id]:
        return None
    return all_scores[farmer_id][field_id]

# ============================================================================
# PLANTING RECORDS
# ============================================================================

def add_planting_record(farmer_id: str, field_id: str, crop: str, planting_date: str, 
                       variety: str = None, area_hectares: float = None):
    """Record when farmer plants a crop"""
    records = _load('planting_records.json', {})
    if farmer_id not in records:
        records[farmer_id] = {}
    if field_id not in records[farmer_id]:
        records[farmer_id][field_id] = []
    
    records[farmer_id][field_id].append({
        'crop': crop,
        'variety': variety,
        'planting_date': planting_date,
        'area_hectares': area_hectares,
        'recorded_at': datetime.utcnow().isoformat()
    })
    _save('planting_records.json', records)

def get_active_plantings(farmer_id: str, field_id: str = None) -> List[Dict]:
    """Get active plantings (last 12 months) for farmer"""
    records = _load('planting_records.json', {})
    if farmer_id not in records:
        return []
    
    cutoff = datetime.utcnow() - timedelta(days=365)
    active = []
    
    if field_id:
        fields = {field_id: records[farmer_id].get(field_id, [])}
    else:
        fields = records[farmer_id]
    
    for fid, plantings in fields.items():
        for p in plantings:
            if datetime.fromisoformat(p['planting_date']) >= cutoff:
                active.append({**p, 'field_id': fid})
    
    return active

# ============================================================================
# HARVEST PREDICTIONS
# ============================================================================

def save_harvest_prediction(farmer_id: str, field_id: str, planting_date: str, 
                           crop: str, predicted_harvest_date: str, 
                           weather_conditions: dict, storage_status: dict):
    """Save harvest prediction with weather forecast and storage check"""
    predictions = _load('harvest_predictions.json', {})
    if farmer_id not in predictions:
        predictions[farmer_id] = {}
    
    key = f"{field_id}_{planting_date}_{crop}"
    predictions[farmer_id][key] = {
        'field_id': field_id,
        'crop': crop,
        'planting_date': planting_date,
        'predicted_harvest_date': predicted_harvest_date,
        'weather_conditions': weather_conditions,
        'storage_status': storage_status,
        'calculated_at': datetime.utcnow().isoformat()
    }
    _save('harvest_predictions.json', predictions)

def get_harvest_predictions(farmer_id: str) -> List[Dict]:
    """Get all harvest predictions for farmer"""
    predictions = _load('harvest_predictions.json', {})
    if farmer_id not in predictions:
        return []
    return list(predictions[farmer_id].values())
