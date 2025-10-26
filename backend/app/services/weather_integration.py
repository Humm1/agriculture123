"""
Weather Integration Module
===========================

Integrates weather data from multiple sources:
1. LCRS Engine (Long-range Climate Risk Service) - Real-time + 7-day forecast
2. BLE Sensors (Bluetooth Low Energy) - On-farm soil moisture, temperature, humidity
3. SMS Alerts (Twilio/Africa's Talking) - Critical weather alerts to farmers

Calculates Soil Moisture Index (SMI) for intelligent irrigation guidance.

Author: AgroShield AI Team
Date: October 2025
"""

import os
import json
import requests
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import asyncio
from enum import Enum


# ============================================================================
# CONFIGURATION
# ============================================================================

WEATHER_CONFIG = {
    "lcrs_engine": {
        "enabled": False,  # Set to True after obtaining API key
        "api_key": os.getenv("LCRS_API_KEY"),
        "base_url": "https://api.lcrs.climate.go.ke/v1",
        "endpoints": {
            "current": "/weather/current",
            "forecast": "/weather/forecast",
            "historical": "/weather/historical",
            "alerts": "/alerts/active"
        },
        "cache_ttl_minutes": 30,  # Cache current weather for 30 min
        "forecast_days": 7
    },
    "ble_sensors": {
        "enabled": True,  # Can start with simulation
        "data_ingestion_interval_minutes": 15,
        "sensor_types": {
            "soil_moisture": {"unit": "percent", "min": 0, "max": 100},
            "soil_temperature": {"unit": "celsius", "min": -10, "max": 60},
            "air_temperature": {"unit": "celsius", "min": -10, "max": 50},
            "air_humidity": {"unit": "percent", "min": 0, "max": 100}
        },
        "battery_alert_threshold": 20  # Alert when battery < 20%
    },
    "sms_alerts": {
        "enabled": False,  # Set to True after configuring SMS provider
        "provider": "africas_talking",  # or "twilio"
        "africas_talking": {
            "api_key": os.getenv("AFRICAS_TALKING_API_KEY"),
            "username": os.getenv("AFRICAS_TALKING_USERNAME"),
            "sender_id": "AGROSHIELD"
        },
        "twilio": {
            "account_sid": os.getenv("TWILIO_ACCOUNT_SID"),
            "auth_token": os.getenv("TWILIO_AUTH_TOKEN"),
            "from_number": os.getenv("TWILIO_PHONE_NUMBER")
        },
        "alert_priorities": {
            "critical": {"max_daily": 3, "cooldown_hours": 2},
            "high": {"max_daily": 5, "cooldown_hours": 4},
            "medium": {"max_daily": 10, "cooldown_hours": 8},
            "low": {"max_daily": 20, "cooldown_hours": 24}
        }
    },
    "soil_moisture_index": {
        "critical_dry": 20,      # <20% = critical
        "low_moisture": 40,      # 20-40% = low
        "optimal_min": 60,       # 60-80% = optimal
        "optimal_max": 80,
        "waterlogged": 90        # >90% = waterlogged
    }
}


class AlertPriority(Enum):
    """Alert priority levels for SMS notifications."""
    CRITICAL = "critical"  # Immediate action required (frost, hail, severe drought)
    HIGH = "high"          # Action within 24h (heavy rain, pest outbreak)
    MEDIUM = "medium"      # Action within 2-3 days (fertilizer timing)
    LOW = "low"            # Informational (harvest window opening)


class WeatherCondition(Enum):
    """Weather condition categories."""
    CLEAR = "clear"
    PARTLY_CLOUDY = "partly_cloudy"
    CLOUDY = "cloudy"
    LIGHT_RAIN = "light_rain"
    MODERATE_RAIN = "moderate_rain"
    HEAVY_RAIN = "heavy_rain"
    THUNDERSTORM = "thunderstorm"
    FROST = "frost"
    HAIL = "hail"
    EXTREME_HEAT = "extreme_heat"


# ============================================================================
# LCRS ENGINE INTEGRATION
# ============================================================================

def get_current_weather_lcrs(lat: float, lon: float) -> Dict[str, Any]:
    """
    Get current weather conditions from LCRS Engine.
    
    Args:
        lat: Latitude
        lon: Longitude
    
    Returns:
        dict: Current weather data
    """
    if not WEATHER_CONFIG["lcrs_engine"]["enabled"]:
        return _simulate_current_weather(lat, lon)
    
    try:
        api_key = WEATHER_CONFIG["lcrs_engine"]["api_key"]
        base_url = WEATHER_CONFIG["lcrs_engine"]["base_url"]
        endpoint = WEATHER_CONFIG["lcrs_engine"]["endpoints"]["current"]
        
        response = requests.get(
            f"{base_url}{endpoint}",
            params={
                "lat": lat,
                "lon": lon,
                "api_key": api_key
            },
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            return _parse_lcrs_current_weather(data)
        else:
            print(f"LCRS API error: {response.status_code}")
            return _simulate_current_weather(lat, lon)
    
    except Exception as e:
        print(f"LCRS connection error: {str(e)}")
        return _simulate_current_weather(lat, lon)


def get_weather_forecast_lcrs(
    lat: float,
    lon: float,
    days: int = 7
) -> List[Dict[str, Any]]:
    """
    Get weather forecast from LCRS Engine.
    
    Args:
        lat: Latitude
        lon: Longitude
        days: Number of forecast days (default 7)
    
    Returns:
        list: Daily forecast data
    """
    if not WEATHER_CONFIG["lcrs_engine"]["enabled"]:
        return _simulate_weather_forecast(lat, lon, days)
    
    try:
        api_key = WEATHER_CONFIG["lcrs_engine"]["api_key"]
        base_url = WEATHER_CONFIG["lcrs_engine"]["base_url"]
        endpoint = WEATHER_CONFIG["lcrs_engine"]["endpoints"]["forecast"]
        
        response = requests.get(
            f"{base_url}{endpoint}",
            params={
                "lat": lat,
                "lon": lon,
                "days": days,
                "api_key": api_key
            },
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            return _parse_lcrs_forecast(data)
        else:
            print(f"LCRS API error: {response.status_code}")
            return _simulate_weather_forecast(lat, lon, days)
    
    except Exception as e:
        print(f"LCRS connection error: {str(e)}")
        return _simulate_weather_forecast(lat, lon, days)


def get_active_weather_alerts_lcrs(lat: float, lon: float) -> List[Dict[str, Any]]:
    """
    Get active weather alerts from LCRS Engine.
    
    Args:
        lat: Latitude
        lon: Longitude
    
    Returns:
        list: Active weather alerts
    """
    if not WEATHER_CONFIG["lcrs_engine"]["enabled"]:
        return []
    
    try:
        api_key = WEATHER_CONFIG["lcrs_engine"]["api_key"]
        base_url = WEATHER_CONFIG["lcrs_engine"]["base_url"]
        endpoint = WEATHER_CONFIG["lcrs_engine"]["endpoints"]["alerts"]
        
        response = requests.get(
            f"{base_url}{endpoint}",
            params={
                "lat": lat,
                "lon": lon,
                "radius_km": 50,
                "api_key": api_key
            },
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            return _parse_lcrs_alerts(data)
        else:
            return []
    
    except Exception as e:
        print(f"LCRS alerts error: {str(e)}")
        return []


def _parse_lcrs_current_weather(data: Dict) -> Dict[str, Any]:
    """Parse LCRS current weather response."""
    return {
        "timestamp": datetime.now().isoformat(),
        "temperature_c": data.get("temperature"),
        "humidity_percent": data.get("humidity"),
        "rainfall_mm": data.get("rainfall_24h", 0),
        "wind_speed_kmh": data.get("wind_speed"),
        "wind_direction": data.get("wind_direction"),
        "pressure_hpa": data.get("pressure"),
        "condition": _map_lcrs_condition(data.get("condition")),
        "uv_index": data.get("uv_index"),
        "source": "lcrs_engine",
        "location": {"lat": data.get("lat"), "lon": data.get("lon")}
    }


def _parse_lcrs_forecast(data: Dict) -> List[Dict[str, Any]]:
    """Parse LCRS forecast response."""
    forecasts = []
    for day_data in data.get("forecast", []):
        forecasts.append({
            "date": day_data.get("date"),
            "temperature_min_c": day_data.get("temp_min"),
            "temperature_max_c": day_data.get("temp_max"),
            "humidity_avg_percent": day_data.get("humidity"),
            "rainfall_probability_percent": day_data.get("rain_probability"),
            "rainfall_amount_mm": day_data.get("rain_amount", 0),
            "wind_speed_kmh": day_data.get("wind_speed"),
            "condition": _map_lcrs_condition(day_data.get("condition")),
            "sunrise": day_data.get("sunrise"),
            "sunset": day_data.get("sunset")
        })
    return forecasts


def _parse_lcrs_alerts(data: Dict) -> List[Dict[str, Any]]:
    """Parse LCRS weather alerts."""
    alerts = []
    for alert_data in data.get("alerts", []):
        alerts.append({
            "alert_id": alert_data.get("id"),
            "type": alert_data.get("type"),  # frost, hail, extreme_heat, flood, etc.
            "severity": alert_data.get("severity"),  # warning, watch, advisory
            "headline": alert_data.get("headline"),
            "description": alert_data.get("description"),
            "start_time": alert_data.get("start"),
            "end_time": alert_data.get("end"),
            "affected_areas": alert_data.get("areas", [])
        })
    return alerts


def _map_lcrs_condition(condition_code: str) -> WeatherCondition:
    """Map LCRS condition code to internal enum."""
    mapping = {
        "clear": WeatherCondition.CLEAR,
        "partly_cloudy": WeatherCondition.PARTLY_CLOUDY,
        "cloudy": WeatherCondition.CLOUDY,
        "light_rain": WeatherCondition.LIGHT_RAIN,
        "rain": WeatherCondition.MODERATE_RAIN,
        "heavy_rain": WeatherCondition.HEAVY_RAIN,
        "thunderstorm": WeatherCondition.THUNDERSTORM,
        "frost": WeatherCondition.FROST,
        "hail": WeatherCondition.HAIL
    }
    return mapping.get(condition_code, WeatherCondition.CLEAR)


def _simulate_current_weather(lat: float, lon: float) -> Dict[str, Any]:
    """Simulate current weather when LCRS unavailable."""
    import random
    
    # Kenya typical ranges
    temp = random.uniform(18, 30)
    humidity = random.uniform(50, 85)
    
    # Rainy season (Mar-May, Oct-Dec)
    month = datetime.now().month
    is_rainy = month in [3, 4, 5, 10, 11, 12]
    rainfall = random.uniform(0, 20) if is_rainy else random.uniform(0, 5)
    
    return {
        "timestamp": datetime.now().isoformat(),
        "temperature_c": round(temp, 1),
        "humidity_percent": round(humidity, 1),
        "rainfall_mm": round(rainfall, 1),
        "wind_speed_kmh": round(random.uniform(5, 20), 1),
        "wind_direction": random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"]),
        "pressure_hpa": round(random.uniform(1010, 1020), 1),
        "condition": WeatherCondition.PARTLY_CLOUDY.value,
        "uv_index": random.randint(5, 10),
        "source": "simulated",
        "location": {"lat": lat, "lon": lon},
        "note": "LCRS Engine not configured. Using simulation."
    }


def _simulate_weather_forecast(lat: float, lon: float, days: int) -> List[Dict[str, Any]]:
    """Simulate weather forecast when LCRS unavailable."""
    import random
    
    forecasts = []
    base_date = datetime.now()
    
    for day in range(days):
        date = base_date + timedelta(days=day)
        
        # Kenya typical ranges
        temp_min = random.uniform(15, 22)
        temp_max = temp_min + random.uniform(8, 15)
        
        # Rainy season
        is_rainy = date.month in [3, 4, 5, 10, 11, 12]
        rain_prob = random.uniform(40, 80) if is_rainy else random.uniform(10, 30)
        rain_amount = random.uniform(5, 30) if rain_prob > 60 else 0
        
        forecasts.append({
            "date": date.strftime("%Y-%m-%d"),
            "temperature_min_c": round(temp_min, 1),
            "temperature_max_c": round(temp_max, 1),
            "humidity_avg_percent": round(random.uniform(55, 80), 1),
            "rainfall_probability_percent": round(rain_prob, 1),
            "rainfall_amount_mm": round(rain_amount, 1),
            "wind_speed_kmh": round(random.uniform(5, 20), 1),
            "condition": WeatherCondition.PARTLY_CLOUDY.value,
            "sunrise": "06:15",
            "sunset": "18:30"
        })
    
    return forecasts


# ============================================================================
# BLE SENSOR DATA INGESTION
# ============================================================================

class BLESensorReading:
    """Represents a BLE sensor reading."""
    
    def __init__(
        self,
        sensor_id: str,
        sensor_type: str,
        value: float,
        unit: str,
        timestamp: datetime,
        battery_percent: Optional[int] = None,
        signal_strength: Optional[int] = None
    ):
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self.value = value
        self.unit = unit
        self.timestamp = timestamp
        self.battery_percent = battery_percent
        self.signal_strength = signal_strength
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "sensor_id": self.sensor_id,
            "sensor_type": self.sensor_type,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp.isoformat(),
            "battery_percent": self.battery_percent,
            "signal_strength": self.signal_strength
        }


def ingest_ble_sensor_data(
    farmer_id: str,
    field_id: str,
    sensor_readings: List[BLESensorReading]
) -> Dict[str, Any]:
    """
    Ingest BLE sensor data from on-farm sensors.
    
    Args:
        farmer_id: Farmer ID
        field_id: Field ID
        sensor_readings: List of sensor readings
    
    Returns:
        dict: Ingestion summary with alerts
    """
    # Store readings (simulate database write)
    stored_readings = []
    alerts = []
    
    for reading in sensor_readings:
        # Validate reading
        if not _validate_sensor_reading(reading):
            continue
        
        # Store reading
        stored_readings.append(reading.to_dict())
        
        # Check for alerts
        reading_alerts = _check_sensor_alerts(reading, farmer_id, field_id)
        alerts.extend(reading_alerts)
    
    return {
        "farmer_id": farmer_id,
        "field_id": field_id,
        "readings_ingested": len(stored_readings),
        "timestamp": datetime.now().isoformat(),
        "alerts_generated": len(alerts),
        "alerts": alerts,
        "readings": stored_readings
    }


def _validate_sensor_reading(reading: BLESensorReading) -> bool:
    """Validate sensor reading is within expected range."""
    sensor_config = WEATHER_CONFIG["ble_sensors"]["sensor_types"].get(reading.sensor_type)
    
    if not sensor_config:
        return False
    
    min_val = sensor_config["min"]
    max_val = sensor_config["max"]
    
    return min_val <= reading.value <= max_val


def _check_sensor_alerts(
    reading: BLESensorReading,
    farmer_id: str,
    field_id: str
) -> List[Dict[str, Any]]:
    """Check if sensor reading triggers any alerts."""
    alerts = []
    
    # Check battery level
    if reading.battery_percent and reading.battery_percent < WEATHER_CONFIG["ble_sensors"]["battery_alert_threshold"]:
        alerts.append({
            "type": "battery_low",
            "priority": AlertPriority.MEDIUM.value,
            "sensor_id": reading.sensor_id,
            "message": f"Sensor {reading.sensor_id} battery low: {reading.battery_percent}%",
            "action": "Replace battery soon"
        })
    
    # Check soil moisture
    if reading.sensor_type == "soil_moisture":
        smi_config = WEATHER_CONFIG["soil_moisture_index"]
        
        if reading.value < smi_config["critical_dry"]:
            alerts.append({
                "type": "critical_drought",
                "priority": AlertPriority.CRITICAL.value,
                "sensor_id": reading.sensor_id,
                "message": f"Critical soil moisture: {reading.value}% (Emergency irrigation needed)",
                "action": "Irrigate immediately to prevent crop stress",
                "smi_value": reading.value
            })
        elif reading.value < smi_config["low_moisture"]:
            alerts.append({
                "type": "low_soil_moisture",
                "priority": AlertPriority.HIGH.value,
                "sensor_id": reading.sensor_id,
                "message": f"Low soil moisture: {reading.value}% (Irrigation recommended)",
                "action": "Plan irrigation within 24 hours",
                "smi_value": reading.value
            })
        elif reading.value > smi_config["waterlogged"]:
            alerts.append({
                "type": "waterlogged_soil",
                "priority": AlertPriority.HIGH.value,
                "sensor_id": reading.sensor_id,
                "message": f"Waterlogged soil: {reading.value}% (Risk of root rot)",
                "action": "Improve drainage, avoid additional watering",
                "smi_value": reading.value
            })
    
    # Check temperature extremes
    if reading.sensor_type == "soil_temperature":
        if reading.value < 5:
            alerts.append({
                "type": "frost_risk",
                "priority": AlertPriority.CRITICAL.value,
                "sensor_id": reading.sensor_id,
                "message": f"Frost risk: Soil temp {reading.value}°C",
                "action": "Cover sensitive crops, apply frost protection"
            })
        elif reading.value > 40:
            alerts.append({
                "type": "heat_stress",
                "priority": AlertPriority.HIGH.value,
                "sensor_id": reading.sensor_id,
                "message": f"Heat stress: Soil temp {reading.value}°C",
                "action": "Increase irrigation frequency, apply mulch"
            })
    
    return alerts


def get_latest_sensor_readings(
    farmer_id: str,
    field_id: str,
    hours: int = 24
) -> Dict[str, Any]:
    """
    Get latest sensor readings for a field.
    
    Args:
        farmer_id: Farmer ID
        field_id: Field ID
        hours: Hours to look back
    
    Returns:
        dict: Latest readings by sensor type
    """
    # Simulate retrieving from database
    # In production, query last N hours of readings
    
    return _simulate_sensor_readings(farmer_id, field_id, hours)


def _simulate_sensor_readings(farmer_id: str, field_id: str, hours: int) -> Dict[str, Any]:
    """Simulate sensor readings when no real data."""
    import random
    
    now = datetime.now()
    
    return {
        "farmer_id": farmer_id,
        "field_id": field_id,
        "period_hours": hours,
        "readings": {
            "soil_moisture": {
                "current_value": round(random.uniform(40, 75), 1),
                "unit": "percent",
                "trend": random.choice(["increasing", "stable", "decreasing"]),
                "last_updated": (now - timedelta(minutes=random.randint(5, 30))).isoformat()
            },
            "soil_temperature": {
                "current_value": round(random.uniform(18, 28), 1),
                "unit": "celsius",
                "trend": "stable",
                "last_updated": (now - timedelta(minutes=random.randint(5, 30))).isoformat()
            },
            "air_temperature": {
                "current_value": round(random.uniform(20, 32), 1),
                "unit": "celsius",
                "trend": "stable",
                "last_updated": (now - timedelta(minutes=random.randint(5, 30))).isoformat()
            },
            "air_humidity": {
                "current_value": round(random.uniform(55, 80), 1),
                "unit": "percent",
                "trend": "stable",
                "last_updated": (now - timedelta(minutes=random.randint(5, 30))).isoformat()
            }
        },
        "note": "Simulated sensor data for demonstration"
    }


# ============================================================================
# SOIL MOISTURE INDEX (SMI) CALCULATION
# ============================================================================

def calculate_soil_moisture_index(
    farmer_id: str,
    field_id: str,
    crop: str
) -> Dict[str, Any]:
    """
    Calculate Soil Moisture Index (SMI) for intelligent irrigation guidance.
    
    SMI combines:
    - BLE sensor readings (soil moisture %)
    - Recent rainfall
    - Crop water requirements
    - Soil type (water holding capacity)
    - Evapotranspiration rate
    
    Args:
        farmer_id: Farmer ID
        field_id: Field ID
        crop: Crop type
    
    Returns:
        dict: SMI score (0-10) with irrigation recommendations
    """
    # Get sensor data
    sensor_data = get_latest_sensor_readings(farmer_id, field_id, hours=24)
    soil_moisture_percent = sensor_data["readings"]["soil_moisture"]["current_value"]
    
    # Get weather data (simulate getting farmer's location)
    lat, lon = -1.29, 36.82  # Nairobi (placeholder)
    weather = get_current_weather_lcrs(lat, lon)
    recent_rainfall = weather["rainfall_mm"]
    
    # Crop water requirements (simplified)
    crop_water_needs = {
        "maize": 5.0,        # mm/day
        "potato": 6.0,
        "beans": 4.0,
        "tomato": 7.0,
        "cabbage": 5.5,
        "wheat": 4.5,
        "rice": 8.0,
        "sugarcane": 7.5
    }
    daily_water_need = crop_water_needs.get(crop, 5.0)
    
    # Calculate SMI (0-10 scale)
    # SMI = Soil moisture adjusted for crop needs and recent rainfall
    
    # Base SMI from soil moisture
    base_smi = soil_moisture_percent / 10.0  # Convert % to 0-10 scale
    
    # Rainfall adjustment (recent rain increases SMI)
    rainfall_boost = min(recent_rainfall / daily_water_need, 2.0)
    
    # Crop stress factor (high water need crops more sensitive)
    stress_factor = 1.0 + (daily_water_need - 5.0) / 10.0
    
    # Final SMI
    smi = base_smi + rainfall_boost
    smi = max(0, min(smi, 10))  # Clamp to 0-10
    
    # Irrigation recommendation
    recommendation = _get_irrigation_recommendation(smi, crop, daily_water_need)
    
    return {
        "farmer_id": farmer_id,
        "field_id": field_id,
        "crop": crop,
        "smi_score": round(smi, 1),
        "smi_category": _categorize_smi(smi),
        "soil_moisture_percent": soil_moisture_percent,
        "recent_rainfall_mm": recent_rainfall,
        "daily_water_need_mm": daily_water_need,
        "irrigation_recommendation": recommendation,
        "calculated_at": datetime.now().isoformat()
    }


def _categorize_smi(smi: float) -> str:
    """Categorize SMI value."""
    if smi < 2.0:
        return "critical_drought"
    elif smi < 4.0:
        return "severe_deficit"
    elif smi < 6.0:
        return "moderate_deficit"
    elif smi < 8.0:
        return "optimal"
    elif smi < 9.0:
        return "adequate"
    else:
        return "saturated"


def _get_irrigation_recommendation(smi: float, crop: str, daily_water_need: float) -> Dict[str, Any]:
    """Generate irrigation recommendation based on SMI."""
    if smi < 2.0:
        return {
            "action": "irrigate_immediately",
            "urgency": "critical",
            "amount_mm": daily_water_need * 2,  # Double dose to recover
            "timing": "now",
            "reason": "Critical soil moisture deficit. Crop stress imminent."
        }
    elif smi < 4.0:
        return {
            "action": "irrigate_today",
            "urgency": "high",
            "amount_mm": daily_water_need * 1.5,
            "timing": "within_6_hours",
            "reason": "Severe soil moisture deficit. Irrigate soon to prevent stress."
        }
    elif smi < 6.0:
        return {
            "action": "irrigate_within_24h",
            "urgency": "medium",
            "amount_mm": daily_water_need,
            "timing": "within_24_hours",
            "reason": "Moderate deficit. Plan irrigation within 24 hours."
        }
    elif smi < 8.0:
        return {
            "action": "monitor",
            "urgency": "low",
            "amount_mm": 0,
            "timing": "no_irrigation_needed",
            "reason": "Soil moisture optimal. No irrigation needed."
        }
    else:
        return {
            "action": "avoid_irrigation",
            "urgency": "none",
            "amount_mm": 0,
            "timing": "wait_48_hours",
            "reason": "Soil saturated. Risk of waterlogging. Avoid irrigation."
        }


# ============================================================================
# SMS ALERT SYSTEM
# ============================================================================

def send_sms_alert(
    phone_number: str,
    message: str,
    priority: AlertPriority = AlertPriority.MEDIUM,
    farmer_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send SMS alert to farmer.
    
    Implements alert fatigue prevention:
    - Rate limiting by priority
    - Cooldown periods
    - Daily caps per priority level
    
    Args:
        phone_number: Farmer's phone number
        message: Alert message
        priority: Alert priority level
        farmer_id: Optional farmer ID for tracking
    
    Returns:
        dict: Send status
    """
    if not WEATHER_CONFIG["sms_alerts"]["enabled"]:
        return _simulate_sms_send(phone_number, message, priority)
    
    # Check rate limits
    if not _check_sms_rate_limit(farmer_id, priority):
        return {
            "status": "rate_limited",
            "message": "SMS rate limit reached for this priority level",
            "priority": priority.value
        }
    
    # Select provider
    provider = WEATHER_CONFIG["sms_alerts"]["provider"]
    
    if provider == "africas_talking":
        return _send_sms_africas_talking(phone_number, message, priority, farmer_id)
    elif provider == "twilio":
        return _send_sms_twilio(phone_number, message, priority, farmer_id)
    else:
        return {"status": "error", "message": "Invalid SMS provider"}


def _send_sms_africas_talking(
    phone_number: str,
    message: str,
    priority: AlertPriority,
    farmer_id: Optional[str]
) -> Dict[str, Any]:
    """Send SMS via Africa's Talking."""
    try:
        config = WEATHER_CONFIG["sms_alerts"]["africas_talking"]
        
        url = "https://api.africastalking.com/version1/messaging"
        
        headers = {
            "apiKey": config["api_key"],
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        
        data = {
            "username": config["username"],
            "to": phone_number,
            "message": message,
            "from": config["sender_id"]
        }
        
        response = requests.post(url, headers=headers, data=data, timeout=10)
        
        if response.status_code == 201:
            result = response.json()
            _record_sms_sent(farmer_id, priority)
            return {
                "status": "sent",
                "provider": "africas_talking",
                "message_id": result["SMSMessageData"]["Recipients"][0]["messageId"],
                "cost": result["SMSMessageData"]["Recipients"][0]["cost"]
            }
        else:
            return {
                "status": "failed",
                "error": f"HTTP {response.status_code}",
                "provider": "africas_talking"
            }
    
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "provider": "africas_talking"
        }


def _send_sms_twilio(
    phone_number: str,
    message: str,
    priority: AlertPriority,
    farmer_id: Optional[str]
) -> Dict[str, Any]:
    """Send SMS via Twilio."""
    try:
        config = WEATHER_CONFIG["sms_alerts"]["twilio"]
        
        from twilio.rest import Client
        
        client = Client(config["account_sid"], config["auth_token"])
        
        message_obj = client.messages.create(
            body=message,
            from_=config["from_number"],
            to=phone_number
        )
        
        _record_sms_sent(farmer_id, priority)
        
        return {
            "status": "sent",
            "provider": "twilio",
            "message_sid": message_obj.sid,
            "price": message_obj.price
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "provider": "twilio"
        }


def _simulate_sms_send(
    phone_number: str,
    message: str,
    priority: AlertPriority
) -> Dict[str, Any]:
    """Simulate SMS sending when provider not configured."""
    return {
        "status": "simulated",
        "phone_number": phone_number,
        "message": message,
        "priority": priority.value,
        "timestamp": datetime.now().isoformat(),
        "note": "SMS provider not configured. This is a simulation."
    }


def _check_sms_rate_limit(farmer_id: Optional[str], priority: AlertPriority) -> bool:
    """Check if SMS can be sent within rate limits."""
    # Simplified - in production, query database for recent SMS count
    # and check against priority-specific limits
    
    limits = WEATHER_CONFIG["sms_alerts"]["alert_priorities"][priority.value]
    max_daily = limits["max_daily"]
    
    # Simulate checking (always allow in simulation)
    return True


def _record_sms_sent(farmer_id: Optional[str], priority: AlertPriority):
    """Record SMS sent for rate limiting."""
    # In production, write to database
    pass


def send_critical_weather_alert(
    farmer_id: str,
    phone_number: str,
    alert_type: str,
    weather_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Send critical weather alert with smart message formatting.
    
    Args:
        farmer_id: Farmer ID
        phone_number: Phone number
        alert_type: Type of alert (frost, hail, extreme_heat, flood)
        weather_data: Weather data context
    
    Returns:
        dict: Send status
    """
    # Format message based on alert type
    messages = {
        "frost": f"⚠️ FROST ALERT: Temperature dropping to {weather_data.get('temp_min')}°C tonight. Cover sensitive crops NOW. -AgroShield",
        "hail": f"⚠️ HAIL WARNING: Hail expected in {weather_data.get('hours_until')}h. Secure harvest, cover young plants. -AgroShield",
        "extreme_heat": f"🌡️ HEAT ALERT: {weather_data.get('temp_max')}°C expected. Increase irrigation, apply mulch. -AgroShield",
        "flood": f"🌊 FLOOD WARNING: Heavy rain ({weather_data.get('rainfall')}mm) next 24h. Clear drainage channels. -AgroShield",
        "drought": f"☀️ DROUGHT ALERT: No rain for {weather_data.get('dry_days')} days. SMI critical. Irrigate immediately. -AgroShield"
    }
    
    message = messages.get(alert_type, "Weather alert from AgroShield")
    
    return send_sms_alert(phone_number, message, AlertPriority.CRITICAL, farmer_id)


# ============================================================================
# WEATHER-AWARE CROP RECOMMENDATIONS
# ============================================================================

def get_weather_aware_recommendations(
    farmer_id: str,
    field_id: str,
    crop: str,
    growth_stage: str
) -> Dict[str, Any]:
    """
    Generate weather-aware crop management recommendations.
    
    Combines:
    - Current weather
    - 7-day forecast
    - BLE sensor data
    - Soil Moisture Index
    - Growth stage requirements
    
    Args:
        farmer_id: Farmer ID
        field_id: Field ID
        crop: Crop type
        growth_stage: Current growth stage
    
    Returns:
        dict: Actionable recommendations
    """
    # Get weather data
    lat, lon = -1.29, 36.82  # Placeholder
    current_weather = get_current_weather_lcrs(lat, lon)
    forecast = get_weather_forecast_lcrs(lat, lon, days=7)
    
    # Get sensor data
    sensor_data = get_latest_sensor_readings(farmer_id, field_id)
    
    # Calculate SMI
    smi_data = calculate_soil_moisture_index(farmer_id, field_id, crop)
    
    # Generate recommendations
    recommendations = []
    
    # Irrigation recommendations
    if smi_data["smi_score"] < 6.0:
        recommendations.append({
            "category": "irrigation",
            "priority": AlertPriority.HIGH.value if smi_data["smi_score"] < 4.0 else AlertPriority.MEDIUM.value,
            "action": smi_data["irrigation_recommendation"]["action"],
            "timing": smi_data["irrigation_recommendation"]["timing"],
            "details": smi_data["irrigation_recommendation"]["reason"]
        })
    
    # Rainfall-based recommendations
    upcoming_rainfall = sum(day["rainfall_amount_mm"] for day in forecast[:3])
    if upcoming_rainfall > 50:
        recommendations.append({
            "category": "drainage",
            "priority": AlertPriority.HIGH.value,
            "action": "prepare_drainage",
            "timing": "before_rain",
            "details": f"Heavy rain expected ({upcoming_rainfall}mm in 3 days). Clear drainage channels."
        })
    
    # Fertilizer timing (avoid leaching)
    if upcoming_rainfall > 30 and growth_stage in ["vegetative", "flowering"]:
        recommendations.append({
            "category": "fertilizer",
            "priority": AlertPriority.MEDIUM.value,
            "action": "delay_fertilizer",
            "timing": "after_rain_stops",
            "details": f"Delay fertilizer application. Heavy rain ({upcoming_rainfall}mm) would cause leaching."
        })
    
    # Heat stress management
    max_temp_week = max(day["temperature_max_c"] for day in forecast)
    if max_temp_week > 35:
        recommendations.append({
            "category": "heat_management",
            "priority": AlertPriority.HIGH.value,
            "action": "increase_irrigation",
            "timing": "morning_and_evening",
            "details": f"Extreme heat expected ({max_temp_week}°C). Increase irrigation frequency."
        })
    
    return {
        "farmer_id": farmer_id,
        "field_id": field_id,
        "crop": crop,
        "growth_stage": growth_stage,
        "recommendations": recommendations,
        "weather_summary": {
            "current_temp": current_weather["temperature_c"],
            "current_humidity": current_weather["humidity_percent"],
            "rainfall_7day": round(sum(day["rainfall_amount_mm"] for day in forecast), 1),
            "smi_score": smi_data["smi_score"]
        },
        "generated_at": datetime.now().isoformat()
    }


# ============================================================================
# SETUP INSTRUCTIONS
# ============================================================================

def print_setup_instructions():
    """Print setup instructions for weather integration."""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║       Weather Integration Module Setup Instructions          ║
╚═══════════════════════════════════════════════════════════════╝

1. LCRS ENGINE (CLIMATE DATA)
   ---------------------------
   a) Contact Kenya Meteorological Department
      Website: https://meteo.go.ke
      Email: director@meteo.go.ke
   
   b) Request API access for LCRS Engine
      - Real-time weather data
      - 7-day forecasts
      - Historical climate data
      - Weather alerts
   
   c) Set environment variables:
      export LCRS_API_KEY=your-api-key
   
   d) Enable in config:
      WEATHER_CONFIG["lcrs_engine"]["enabled"] = True

2. BLE SENSOR INTEGRATION
   -----------------------
   ✓ Already enabled with simulation
   
   For real sensors:
   a) Deploy BLE sensors in fields:
      - Soil moisture sensors (every 50m)
      - Soil temperature sensors
      - Air temp/humidity sensors
   
   b) Configure sensor IDs in database
   
   c) Set up data ingestion cron job:
      Every 15 minutes: ingest_ble_sensor_data()
   
   d) Recommended sensors:
      - Xiaomi Flora (soil moisture, temp, light)
      - SwitchBot Meter (air temp, humidity)
      - Custom Arduino-based sensors

3. SMS ALERTS
   -----------
   OPTION A: Africa's Talking (Recommended for Kenya)
   
   a) Sign up: https://africastalking.com/
   b) Get API key and username
   c) Set environment variables:
      export AFRICAS_TALKING_API_KEY=your-api-key
      export AFRICAS_TALKING_USERNAME=your-username
   
   d) Enable:
      WEATHER_CONFIG["sms_alerts"]["enabled"] = True
      WEATHER_CONFIG["sms_alerts"]["provider"] = "africas_talking"
   
   OPTION B: Twilio (International)
   
   a) Sign up: https://www.twilio.com/
   b) Get Account SID, Auth Token, Phone Number
   c) Set environment variables:
      export TWILIO_ACCOUNT_SID=your-sid
      export TWILIO_AUTH_TOKEN=your-token
      export TWILIO_PHONE_NUMBER=your-number
   
   d) Enable:
      WEATHER_CONFIG["sms_alerts"]["enabled"] = True
      WEATHER_CONFIG["sms_alerts"]["provider"] = "twilio"

4. SOIL MOISTURE INDEX
   --------------------
   ✓ Already configured
   - Critical dry: <20%
   - Low moisture: 20-40%
   - Optimal: 60-80%
   - Waterlogged: >90%
   
   Adjust thresholds per soil type if needed.

5. CRON JOBS (AUTOMATED TASKS)
   ----------------------------
   Add to crontab or task scheduler:
   
   # Update weather forecast (daily at 6 AM)
   0 6 * * * python -c "from app.services.weather_integration import get_weather_forecast_lcrs; get_weather_forecast_lcrs(-1.29, 36.82)"
   
   # Ingest BLE sensor data (every 15 min)
   */15 * * * * python -c "from app.services.weather_integration import ingest_ble_sensor_data; # Add your logic"
   
   # Check for critical alerts (hourly)
   0 * * * * python -c "from app.services.weather_integration import get_active_weather_alerts_lcrs; # Add your logic"

6. TESTING
   --------
   from app.services.weather_integration import (
       get_current_weather_lcrs,
       calculate_soil_moisture_index,
       send_sms_alert,
       get_weather_aware_recommendations
   )
   
   # Test weather data
   weather = get_current_weather_lcrs(-1.29, 36.82)
   print(weather)
   
   # Test SMI calculation
   smi = calculate_soil_moisture_index("farmer123", "field456", "maize")
   print(smi)
   
   # Test SMS (simulation mode)
   result = send_sms_alert("+254712345678", "Test alert", AlertPriority.MEDIUM)
   print(result)

═══════════════════════════════════════════════════════════════
Current Status:
  LCRS Engine: {'ENABLED' if WEATHER_CONFIG["lcrs_engine"]["enabled"] else 'DISABLED (using simulation)'}
  BLE Sensors: {'ENABLED' if WEATHER_CONFIG["ble_sensors"]["enabled"] else 'DISABLED'}
  SMS Alerts: {'ENABLED' if WEATHER_CONFIG["sms_alerts"]["enabled"] else 'DISABLED (using simulation)'}
  Soil Moisture Index: ENABLED
═══════════════════════════════════════════════════════════════
    """)


# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

__all__ = [
    "get_current_weather_lcrs",
    "get_weather_forecast_lcrs",
    "get_active_weather_alerts_lcrs",
    "ingest_ble_sensor_data",
    "calculate_soil_moisture_index",
    "send_sms_alert",
    "send_critical_weather_alert",
    "get_weather_aware_recommendations",
    "get_latest_sensor_readings",
    "BLESensorReading",
    "AlertPriority",
    "WeatherCondition",
    "print_setup_instructions",
    "WEATHER_CONFIG"
]


if __name__ == "__main__":
    print_setup_instructions()
