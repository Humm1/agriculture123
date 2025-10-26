import json
from pathlib import Path
from threading import Lock
from datetime import datetime, timedelta

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

def append_readings(sensor_id: str, readings: list):
    """readings: list of {ts, temperature, humidity, lat?, lon?}"""
    allr = _load('sensor_readings.json', {})
    arr = allr.get(sensor_id, [])
    for r in readings:
        # normalize timestamp
        if 'ts' not in r:
            r['ts'] = datetime.utcnow().isoformat()
        arr.append(r)
    allr[sensor_id] = arr
    _save('sensor_readings.json', allr)

def get_readings(sensor_id: str, limit: int = 100):
    allr = _load('sensor_readings.json', {})
    arr = allr.get(sensor_id, [])
    return arr[-limit:]

def load_crop_profiles():
    return _load('crop_profiles.json', {
        "maize": {
            "temperature": {"min":10, "max":25},
            "humidity": {"min":50, "max":70}
        },
        "potatoes": {
            "temperature": {"min":4, "max":10},
            "humidity": {"min":85, "max":95}
        }
    })

def save_crop_profiles(profiles: dict):
    _save('crop_profiles.json', profiles)

def set_farmer_settings(farmer_id: str, settings: dict):
    allf = _load('farmer_settings.json', {})
    allf[farmer_id] = settings
    _save('farmer_settings.json', allf)

def get_farmer_settings(farmer_id: str):
    allf = _load('farmer_settings.json', {})
    return allf.get(farmer_id, {})

def log_alert(alert: dict):
    logs = _load('alerts_log.json', [])
    logs.append(alert)
    _save('alerts_log.json', logs)


# ============================================================================
# AI STORAGE INTELLIGENCE - NEW PERSISTENCE FUNCTIONS
# ============================================================================

def get_storage_metadata(sensor_id: str):
    """
    Get storage metadata for AI analysis.
    
    Returns:
        {
            "quantity_kg": 100,
            "harvest_moisture": 14.5,
            "days_in_storage": 30,
            "storage_method": "traditional_crib",
            "harvest_date": "2025-09-15"
        }
    """
    all_meta = _load('storage_metadata.json', {})
    return all_meta.get(sensor_id, {
        'quantity_kg': 100,  # Default
        'harvest_moisture': None,
        'days_in_storage': 0,
        'storage_method': 'traditional_crib',
        'harvest_date': None
    })


def set_storage_metadata(sensor_id: str, metadata: dict):
    """
    Set storage metadata for AI tracking.
    
    Args:
        sensor_id: Sensor identifier
        metadata: {
            "quantity_kg": 250,
            "harvest_moisture": 15.2,
            "storage_method": "pics_bags",
            "harvest_date": "2025-10-15",
            "crop": "maize"
        }
    """
    all_meta = _load('storage_metadata.json', {})
    
    # Calculate days in storage if harvest_date provided
    if 'harvest_date' in metadata:
        try:
            harvest_date = datetime.fromisoformat(metadata['harvest_date'])
            days_in_storage = (datetime.now() - harvest_date).days
            metadata['days_in_storage'] = days_in_storage
        except:
            pass
    
    all_meta[sensor_id] = metadata
    _save('storage_metadata.json', all_meta)


def get_farmer_alert_history(farmer_id: str, limit: int = 50):
    """
    Get farmer's alert history for alert fatigue analysis.
    
    Returns:
        [
            {"alert_id": "x", "sent_at": "2025-10-20T10:00:00", "acknowledged": False},
            ...
        ]
    """
    logs = _load('alerts_log.json', [])
    farmer_alerts = [
        {
            'alert_id': f"{a.get('sensor_id')}_{a.get('ts')}",
            'sent_at': a.get('ts'),
            'acknowledged': a.get('acknowledged', False),
            'level': a.get('level', 'unknown')
        }
        for a in logs
        if a.get('farmer_id') == farmer_id
    ]
    return farmer_alerts[-limit:]


def acknowledge_alert(farmer_id: str, alert_id: str):
    """
    Mark alert as acknowledged by farmer (used for alert fatigue tracking).
    """
    logs = _load('alerts_log.json', [])
    for alert in logs:
        if alert.get('farmer_id') == farmer_id:
            # Match by timestamp or sensor_id
            generated_id = f"{alert.get('sensor_id')}_{alert.get('ts')}"
            if generated_id == alert_id:
                alert['acknowledged'] = True
                alert['acknowledged_at'] = datetime.utcnow().isoformat()
                break
    _save('alerts_log.json', logs)


def get_current_weather(lat: float = None, lon: float = None):
    """
    Get current outdoor weather for remediation strategy.
    In production, this would call a weather API.
    
    Returns:
        {
            "temp": 24,
            "humidity": 55,
            "forecast_24h": [
                {"hour": 14, "humidity": 45, "temp": 26},
                {"hour": 15, "humidity": 48, "temp": 25},
                ...
            ]
        }
    """
    # Simulated weather data for now
    # In production: call OpenWeatherMap, WeatherAPI, or LCRS engine
    
    if lat is None or lon is None:
        # Default weather (no location)
        return {
            'temp': 22,
            'humidity': 60,
            'forecast_24h': [
                {'hour': h, 'humidity': 55 + (h % 5), 'temp': 20 + (h % 8)}
                for h in range(24)
            ]
        }
    
    # Simulate location-based weather
    # (In production, integrate with LCRS climate engine)
    return {
        'temp': 24,
        'humidity': 58,
        'forecast_24h': [
            {'hour': 9, 'humidity': 65, 'temp': 20},
            {'hour': 10, 'humidity': 60, 'temp': 22},
            {'hour': 11, 'humidity': 50, 'temp': 24},
            {'hour': 12, 'humidity': 45, 'temp': 26},
            {'hour': 13, 'humidity': 43, 'temp': 27},
            {'hour': 14, 'humidity': 42, 'temp': 27},
            {'hour': 15, 'humidity': 45, 'temp': 26},
            {'hour': 16, 'humidity': 50, 'temp': 25},
            {'hour': 17, 'humidity': 55, 'temp': 23},
            {'hour': 18, 'humidity': 60, 'temp': 21},
        ]
    }


# ============================================================================
# AI PEST INTELLIGENCE - PERSISTENCE FUNCTIONS
# ============================================================================

def get_weather_forecast(lat: float, lon: float, days: int = 7):
    """
    Get weather forecast for preventative pest alerts.
    In production, integrate with LCRS climate engine.
    
    Returns:
        {
            "next_7_days": [
                {"date": "2025-10-25", "temp_min": 15, "temp_max": 25, "humidity": 85, "rainfall": 20},
                ...
            ]
        }
    """
    from datetime import timedelta
    
    # Simulated forecast
    forecast = []
    base_date = datetime.now()
    
    for i in range(days):
        date = (base_date + timedelta(days=i+1)).strftime("%Y-%m-%d")
        forecast.append({
            "date": date,
            "temp_min": 15 + (i % 5),
            "temp_max": 25 + (i % 8),
            "humidity": 70 + (i % 20),
            "rainfall": max(0, 15 - (i * 2))  # Decreasing rainfall
        })
    
    return {"next_7_days": forecast}


def get_soil_moisture_index(field_id: str) -> float:
    """
    Get soil moisture index (SMI) for field.
    In production, integrate with BLE sensors or satellite data.
    
    Returns: 0-10 (0=dry, 10=saturated)
    """
    # Simulated SMI
    # In production: Query BLE sensors or climate engine
    return 6.5  # Default moderate moisture


def log_pest_report(report: dict):
    """
    Log pest/disease report for outbreak detection.
    
    Args:
        report: {
            "pest_disease_id": "late_blight",
            "lat": -1.28,
            "lon": 36.82,
            "date": "2025-10-24",
            "severity": "moderate",
            "crop": "potato",
            "farmer_id": "farmer_001"
        }
    """
    all_reports = _load('pest_reports.json', [])
    all_reports.append(report)
    _save('pest_reports.json', all_reports)


def get_recent_pest_reports(pest_disease_id: str, days: int = 30):
    """
    Get recent pest reports for outbreak pattern analysis.
    """
    all_reports = _load('pest_reports.json', [])
    
    # Filter by pest_disease_id and date
    cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
    
    filtered = [
        r for r in all_reports
        if r.get("pest_disease_id") == pest_disease_id and r.get("date", "") >= cutoff_date
    ]
    
    return filtered


def get_all_recent_pest_reports(days: int = 30):
    """Get all recent pest reports (any pest/disease)."""
    all_reports = _load('pest_reports.json', [])
    cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
    
    return [r for r in all_reports if r.get("date", "") >= cutoff_date]


def get_community_pest_feedback(lat: float, lon: float, radius_km: int = 20):
    """
    Get community efficacy feedback for pest treatments.
    
    Returns:
        [
            {"action": "Neem spray", "success": True, "lat": -1.28, "lon": 36.82, "date": "2025-10-15"},
            ...
        ]
    """
    import math
    
    all_feedback = _load('pest_efficacy_feedback.json', [])
    
    # Filter by distance
    nearby_feedback = []
    for feedback in all_feedback:
        f_lat = feedback.get("lat", 0)
        f_lon = feedback.get("lon", 0)
        
        # Haversine distance
        R = 6371  # Earth radius in km
        dlat = math.radians(f_lat - lat)
        dlon = math.radians(f_lon - lon)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat)) * math.cos(math.radians(f_lat)) *
             math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        
        if distance <= radius_km:
            nearby_feedback.append(feedback)
    
    return nearby_feedback


def log_pest_efficacy_feedback(feedback: dict):
    """
    Log farmer's efficacy feedback for community learning.
    
    Args:
        feedback: {
            "pest_disease_id": "fall_armyworm",
            "action": "Neem spray",
            "success": True,
            "lat": -1.28,
            "lon": 36.82,
            "farmer_id": "farmer_001",
            "date": "2025-10-24",
            "notes": "Worked well on young larvae"
        }
    """
    all_feedback = _load('pest_efficacy_feedback.json', [])
    all_feedback.append(feedback)
    _save('pest_efficacy_feedback.json', all_feedback)


def get_expert_triage_queue(extension_officer_id: str = None):
    """
    Get queue of low-confidence diagnoses requiring expert review.
    
    Returns:
        [
            {
                "case_id": "case_001",
                "farmer_id": "farmer_001",
                "pest_disease_id": "late_blight",
                "cv_confidence": 0.62,
                "image_url": "...",
                "farmer_notes": "Leaves turning brown",
                "urgency": "priority",
                "submitted_at": "2025-10-24T10:00:00"
            },
            ...
        ]
    """
    all_cases = _load('expert_triage_queue.json', [])
    
    # Filter pending cases (not yet confirmed)
    pending = [c for c in all_cases if not c.get("confirmed")]
    
    # If extension_officer_id provided, filter by region/area
    # (In production, implement regional assignment)
    
    return pending


def log_expert_diagnosis(confirmation: dict):
    """
    Log expert's diagnosis confirmation/correction.
    
    Args:
        confirmation: {
            "case_id": "case_001",
            "expert_diagnosis": "late_blight",
            "expert_recommendations": "Apply copper fungicide immediately",
            "confidence": 0.95,
            "extension_officer_id": "officer_001",
            "confirmed_at": "2025-10-24T12:00:00"
        }
    """
    # Update triage queue
    all_cases = _load('expert_triage_queue.json', [])
    for case in all_cases:
        if case.get("case_id") == confirmation["case_id"]:
            case["confirmed"] = True
            case["expert_diagnosis"] = confirmation
            break
    _save('expert_triage_queue.json', all_cases)
    
    # Also log to expert confirmations for AI training
    all_confirmations = _load('expert_confirmations.json', [])
    all_confirmations.append(confirmation)
    _save('expert_confirmations.json', all_confirmations)


def get_triage_case(case_id: str):
    """Get specific triage case details."""
    all_cases = _load('expert_triage_queue.json', [])
    for case in all_cases:
        if case.get("case_id") == case_id:
            return case
    return None
