"""
Harvest Prediction Engine

Predicts harvest dates and provides alerts based on:
- Planting date
- Crop maturity period
- Weather forecast during harvest window
- Storage facility readiness (BLE sensor check)
"""
from datetime import datetime, timedelta
from typing import Dict, Optional
from . import climate_persistence, persistence, lcrs_engine, advice

# Crop maturity periods (days from planting to harvest)
CROP_MATURITY = {
    'maize': {
        'short_season': 90,
        'medium_season': 120,
        'long_season': 150,
        'default': 120
    },
    'potatoes': {
        'early': 70,
        'mid': 90,
        'late': 120,
        'default': 90
    },
    'beans': {
        'bush': 60,
        'climbing': 75,
        'default': 65
    },
    'rice': {
        'short': 90,
        'medium': 120,
        'long': 150,
        'default': 120
    },
    'cassava': {
        'default': 365  # 12 months
    },
    'sorghum': {
        'default': 120
    }
}

def get_crop_maturity_days(crop: str, variety: str = None) -> int:
    """Get maturity period for crop/variety"""
    crop_lower = crop.lower()
    
    if crop_lower not in CROP_MATURITY:
        return 120  # Default fallback
    
    maturity_data = CROP_MATURITY[crop_lower]
    
    if variety and variety.lower() in maturity_data:
        return maturity_data[variety.lower()]
    
    return maturity_data.get('default', 120)

def predict_harvest_date(planting_date: str, crop: str, variety: str = None) -> Dict:
    """
    Predict harvest date based on planting date and crop maturity.
    
    Returns:
    {
        'predicted_date': str (ISO date),
        'harvest_window_start': str,
        'harvest_window_end': str,
        'maturity_days': int
    }
    """
    planting = datetime.fromisoformat(planting_date)
    maturity_days = get_crop_maturity_days(crop, variety)
    
    # Harvest window is typically +/- 7 days
    harvest_date = planting + timedelta(days=maturity_days)
    window_start = harvest_date - timedelta(days=7)
    window_end = harvest_date + timedelta(days=7)
    
    return {
        'predicted_date': harvest_date.isoformat(),
        'harvest_window_start': window_start.isoformat(),
        'harvest_window_end': window_end.isoformat(),
        'maturity_days': maturity_days
    }

def check_harvest_weather(harvest_date: str, location: dict) -> Dict:
    """
    Check weather forecast for harvest period.
    
    Returns:
    {
        'conditions': 'dry' | 'wet' | 'uncertain',
        'rain_probability': float (0-1),
        'advice': str,
        'icon': str
    }
    """
    harvest = datetime.fromisoformat(harvest_date)
    now = datetime.utcnow()
    
    # Calculate which month harvest falls in
    months_ahead = (harvest.year - now.year) * 12 + (harvest.month - now.month)
    
    # Get seasonal risk for that month
    forecast_risk = lcrs_engine.estimate_weather_forecast_risk(months_ahead)
    
    # Get recent rain reports for location
    rain_factor = lcrs_engine.calculate_crowdsourced_rain_factor(location, days=14)
    
    # Determine harvest conditions
    if forecast_risk < 0.3 and rain_factor < 0.4:
        conditions = 'dry'
        rain_prob = 0.2
        advice = "Good for sun drying! Harvest and spread crops in open air."
        icon = "☀️"
    elif forecast_risk > 0.6 or rain_factor > 0.7:
        conditions = 'wet'
        rain_prob = 0.8
        advice = "High rain risk! Prepare covered drying area or mechanical dryer."
        icon = "🌧️"
    else:
        conditions = 'uncertain'
        rain_prob = 0.5
        advice = "Mixed conditions. Have backup covered drying plan ready."
        icon = "⛅"
    
    return {
        'conditions': conditions,
        'rain_probability': round(rain_prob, 2),
        'advice': advice,
        'icon': icon
    }

def check_storage_readiness(farmer_id: str, sensor_id: str = None) -> Dict:
    """
    Check if storage facility is ready for new harvest via BLE sensor data.
    
    Returns:
    {
        'ready': bool,
        'temperature': float,
        'humidity': float,
        'issues': [str],
        'recommendations': [str]
    }
    """
    # Try to find farmer's sensor
    if not sensor_id:
        # Get most recent sensor reading for any of farmer's sensors
        # In production, link farmer to their sensors
        sensor_id = f"default_sensor_{farmer_id}"
    
    readings = persistence.get_readings(sensor_id, limit=1)
    
    if not readings:
        return {
            'ready': None,
            'temperature': None,
            'humidity': None,
            'issues': ['No storage sensor data available'],
            'recommendations': ['Install BLE sensor in storage to monitor conditions']
        }
    
    latest = readings[-1]
    temp = latest.get('temperature')
    hum = latest.get('humidity')
    
    issues = []
    recommendations = []
    
    # Check temperature (ideal: 10-25°C for most crops)
    if temp and temp > 30:
        issues.append(f"Temperature too high ({temp}°C)")
        recommendations.append("Cool storage before bringing in harvest")
    elif temp and temp < 5:
        issues.append(f"Temperature too low ({temp}°C)")
        recommendations.append("Warm storage to prevent condensation")
    
    # Check humidity (ideal: 50-70% for grains)
    if hum and hum > 75:
        issues.append(f"Humidity too high ({hum}%)")
        recommendations.append("Increase ventilation to reduce moisture")
    elif hum and hum < 40:
        issues.append(f"Humidity too low ({hum}%)")
        recommendations.append("Monitor for excessive drying")
    
    ready = len(issues) == 0
    
    return {
        'ready': ready,
        'temperature': temp,
        'humidity': hum,
        'issues': issues,
        'recommendations': recommendations
    }

def generate_harvest_alert(farmer_id: str, field_id: str, planting_date: str, 
                          crop: str, variety: str, location: dict, 
                          sensor_id: str = None, language: str = 'en') -> Dict:
    """
    Generate comprehensive harvest alert with weather and storage check.
    
    Returns:
    {
        'harvest_prediction': dict,
        'weather_forecast': dict,
        'storage_status': dict,
        'alert_message': str,
        'alert_level': 'info' | 'warning' | 'critical',
        'action_items': [str]
    }
    """
    # Predict harvest date
    harvest_pred = predict_harvest_date(planting_date, crop, variety)
    
    # Check weather forecast
    weather = check_harvest_weather(harvest_pred['predicted_date'], location)
    
    # Check storage readiness
    storage = check_storage_readiness(farmer_id, sensor_id)
    
    # Generate alert message
    alert_level = 'info'
    action_items = []
    
    # Weather-based message
    if weather['conditions'] == 'dry':
        weather_msg = f"✅ GOOD NEWS: Your {crop} will be ready during a predicted {weather['icon']} dry spell. Perfect for sun drying!"
        action_items.append("Prepare open drying area")
    elif weather['conditions'] == 'wet':
        weather_msg = f"🛑 HARVEST RISK: Your {crop} is ready during predicted {weather['icon']} peak rain. Prepare for covered drying."
        alert_level = 'warning'
        action_items.append("Arrange covered drying space NOW")
        action_items.append("Consider renting mechanical dryer")
    else:
        weather_msg = f"⚠️ HARVEST FORECAST: Your {crop} will be ready around {harvest_pred['predicted_date'][:10]}. {weather['advice']}"
        action_items.append("Monitor weather closely")
    
    # Storage-based message
    if storage['ready'] is False:
        storage_msg = f"\n\n🏠 STORAGE NOT READY: {', '.join(storage['issues'])}. Fix BEFORE harvest!"
        alert_level = 'critical'
        action_items.extend(storage['recommendations'])
    elif storage['ready'] is True:
        storage_msg = f"\n\n✅ STORAGE READY: Temperature {storage['temperature']}°C, Humidity {storage['humidity']}% - Ideal conditions!"
    else:
        storage_msg = "\n\n📦 STORAGE CHECK: Install BLE sensor to monitor storage conditions."
        action_items.append("Set up storage monitoring")
    
    alert_message = weather_msg + storage_msg
    
    # Save prediction
    climate_persistence.save_harvest_prediction(
        farmer_id, field_id, planting_date, crop,
        harvest_pred['predicted_date'],
        weather, storage
    )
    
    return {
        'harvest_prediction': harvest_pred,
        'weather_forecast': weather,
        'storage_status': storage,
        'alert_message': alert_message,
        'alert_level': alert_level,
        'action_items': action_items
    }
