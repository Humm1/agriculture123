"""
Regional Data Integration Service
Fetches real-time data from weather APIs and satellites based on user location
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import requests
from functools import lru_cache
import asyncio
import os
from dotenv import load_dotenv
from app.services import persistence

# Load environment variables
load_dotenv()

# ============================================================================
# API CONFIGURATIONS
# ============================================================================

# OpenWeatherMap (Free tier: 1000 calls/day)
OPENWEATHER_CONFIG = {
    "api_key": os.getenv("OPENWEATHER_API_KEY", "YOUR_OPENWEATHER_API_KEY"),  # Get from https://openweathermap.org/api
    "base_url": "https://api.openweathermap.org/data/2.5",
    "onecall_url": "https://api.openweathermap.org/data/3.0/onecall"
}

# WeatherAPI (Free tier: 1M calls/month)
WEATHERAPI_CONFIG = {
    "api_key": os.getenv("WEATHERAPI_KEY", "YOUR_WEATHERAPI_KEY"),  # Get from https://www.weatherapi.com
    "base_url": "https://api.weatherapi.com/v1"
}

# NASA POWER (Free for agricultural applications)
NASA_POWER_CONFIG = {
    "base_url": "https://power.larc.nasa.gov/api/temporal/daily/point",
    "parameters": "T2M,PRECTOTCORR,RH2M,WS2M,ALLSKY_SFC_SW_DWN"  # Temp, Precip, Humidity, Wind, Solar
}

# Sentinel Hub (Satellite imagery - requires account)
SENTINEL_CONFIG = {
    "client_id": os.getenv("SENTINEL_CLIENT_ID", "YOUR_SENTINEL_CLIENT_ID"),
    "client_secret": os.getenv("SENTINEL_CLIENT_SECRET", "YOUR_SENTINEL_CLIENT_SECRET"),
    "base_url": "https://services.sentinel-hub.com"
}

# Kenya Meteorological Department
KMD_CONFIG = {
    "base_url": "https://meteo.go.ke/api",  # If available
    "stations": {
        "nairobi": {"lat": -1.2921, "lon": 36.8219},
        "mombasa": {"lat": -4.0435, "lon": 39.6682},
        "kisumu": {"lat": -0.0917, "lon": 34.7680},
        "nakuru": {"lat": -0.3031, "lon": 36.0800},
        "eldoret": {"lat": 0.5143, "lon": 35.2698}
    }
}

# Market Data APIs
MARKET_DATA_CONFIG = {
    "eagc_api": "http://www.eagc.org/market-information/",  # East African Grain Council
    "wfp_api": "https://api.wfp.org/vam-data-bridges/1.3.1/"  # WFP Food Prices
}


# ============================================================================
# WEATHER DATA INTEGRATION
# ============================================================================

class RegionalDataService:
    """Fetches real-time regional data based on user location"""
    
    def __init__(self):
        self.cache_duration = 1800  # 30 minutes cache
        self._session = requests.Session()
    
    async def get_comprehensive_data(self, lat: float, lon: float, user_id: str) -> Dict:
        """
        Fetch all regional data for user location
        
        Returns comprehensive data including:
        - Current weather
        - 7-day forecast
        - Historical climate data
        - Satellite indices (NDVI, precipitation)
        - Regional market prices
        - Pest outbreak alerts
        """
        # Run all data fetches in parallel
        tasks = [
            self.get_weather_data(lat, lon),
            self.get_climate_historical(lat, lon),
            self.get_satellite_data(lat, lon),
            self.get_market_data(lat, lon),
            self.get_pest_alerts(lat, lon)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        weather_data, climate_data, satellite_data, market_data, pest_data = results
        
        return {
            "location": {"latitude": lat, "longitude": lon},
            "timestamp": datetime.utcnow().isoformat(),
            "weather": weather_data if not isinstance(weather_data, Exception) else None,
            "climate": climate_data if not isinstance(climate_data, Exception) else None,
            "satellite": satellite_data if not isinstance(satellite_data, Exception) else None,
            "market": market_data if not isinstance(market_data, Exception) else None,
            "pest_alerts": pest_data if not isinstance(pest_data, Exception) else None
        }
    
    async def get_weather_data(self, lat: float, lon: float) -> Dict:
        """
        Fetch current weather and 7-day forecast from OpenWeatherMap
        """
        try:
            # Current weather
            current_url = f"{OPENWEATHER_CONFIG['base_url']}/weather"
            current_params = {
                "lat": lat,
                "lon": lon,
                "appid": OPENWEATHER_CONFIG["api_key"],
                "units": "metric"
            }
            
            current_response = self._session.get(current_url, params=current_params, timeout=10)
            current_response.raise_for_status()
            current_data = current_response.json()
            
            # 7-day forecast (OneCall API 3.0)
            forecast_url = f"{OPENWEATHER_CONFIG['onecall_url']}"
            forecast_params = {
                "lat": lat,
                "lon": lon,
                "appid": OPENWEATHER_CONFIG["api_key"],
                "units": "metric",
                "exclude": "minutely,hourly"
            }
            
            forecast_response = self._session.get(forecast_url, params=forecast_params, timeout=10)
            forecast_response.raise_for_status()
            forecast_data = forecast_response.json()
            
            return {
                "current": {
                    "temperature": current_data["main"]["temp"],
                    "feels_like": current_data["main"]["feels_like"],
                    "humidity": current_data["main"]["humidity"],
                    "pressure": current_data["main"]["pressure"],
                    "wind_speed": current_data["wind"]["speed"],
                    "wind_direction": current_data["wind"].get("deg", 0),
                    "clouds": current_data["clouds"]["all"],
                    "visibility": current_data.get("visibility", 10000),
                    "description": current_data["weather"][0]["description"],
                    "icon": current_data["weather"][0]["icon"],
                    "rain_1h": current_data.get("rain", {}).get("1h", 0),
                    "uv_index": forecast_data.get("current", {}).get("uvi", 0),
                    "timestamp": datetime.fromtimestamp(current_data["dt"]).isoformat()
                },
                "forecast": [
                    {
                        "date": datetime.fromtimestamp(day["dt"]).date().isoformat(),
                        "temp_min": day["temp"]["min"],
                        "temp_max": day["temp"]["max"],
                        "temp_day": day["temp"]["day"],
                        "humidity": day["humidity"],
                        "wind_speed": day["wind_speed"],
                        "clouds": day["clouds"],
                        "rain": day.get("rain", 0),
                        "description": day["weather"][0]["description"],
                        "icon": day["weather"][0]["icon"],
                        "uv_index": day.get("uvi", 0),
                        "pop": day.get("pop", 0) * 100  # Probability of precipitation
                    }
                    for day in forecast_data.get("daily", [])[:7]
                ],
                "alerts": [
                    {
                        "event": alert["event"],
                        "description": alert["description"],
                        "start": datetime.fromtimestamp(alert["start"]).isoformat(),
                        "end": datetime.fromtimestamp(alert["end"]).isoformat()
                    }
                    for alert in forecast_data.get("alerts", [])
                ]
            }
        except Exception as e:
            print(f"Weather data fetch error: {str(e)}")
            return self._get_fallback_weather(lat, lon)
    
    async def get_climate_historical(self, lat: float, lon: float, days_back: int = 30) -> Dict:
        """
        Fetch historical climate data from NASA POWER
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            url = NASA_POWER_CONFIG["base_url"]
            params = {
                "parameters": NASA_POWER_CONFIG["parameters"],
                "community": "AG",  # Agricultural community
                "longitude": lon,
                "latitude": lat,
                "start": start_date.strftime("%Y%m%d"),
                "end": end_date.strftime("%Y%m%d"),
                "format": "JSON"
            }
            
            response = self._session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            parameters = data.get("properties", {}).get("parameter", {})
            
            return {
                "period": {
                    "start": start_date.date().isoformat(),
                    "end": end_date.date().isoformat()
                },
                "temperature": {
                    "average": self._calculate_average(parameters.get("T2M", {})),
                    "daily": parameters.get("T2M", {})
                },
                "precipitation": {
                    "total_mm": self._calculate_sum(parameters.get("PRECTOTCORR", {})),
                    "daily": parameters.get("PRECTOTCORR", {})
                },
                "humidity": {
                    "average": self._calculate_average(parameters.get("RH2M", {})),
                    "daily": parameters.get("RH2M", {})
                },
                "wind_speed": {
                    "average": self._calculate_average(parameters.get("WS2M", {})),
                    "daily": parameters.get("WS2M", {})
                },
                "solar_radiation": {
                    "average": self._calculate_average(parameters.get("ALLSKY_SFC_SW_DWN", {})),
                    "daily": parameters.get("ALLSKY_SFC_SW_DWN", {})
                }
            }
        except Exception as e:
            print(f"Climate data fetch error: {str(e)}")
            return {"error": str(e), "period": {"start": start_date.date().isoformat(), "end": end_date.date().isoformat()}}
    
    async def get_satellite_data(self, lat: float, lon: float) -> Dict:
        """
        Fetch satellite indices (NDVI, EVI, precipitation) from Sentinel/MODIS
        """
        try:
            # For now, use NASA POWER precipitation data
            # Full Sentinel Hub integration requires OAuth token
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=16)  # Last 16 days for vegetation
            
            url = NASA_POWER_CONFIG["base_url"]
            params = {
                "parameters": "PRECTOTCORR,T2M",
                "community": "AG",
                "longitude": lon,
                "latitude": lat,
                "start": start_date.strftime("%Y%m%d"),
                "end": end_date.strftime("%Y%m%d"),
                "format": "JSON"
            }
            
            response = self._session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            parameters = data.get("properties", {}).get("parameter", {})
            
            # Calculate vegetation health proxy from temperature and precipitation
            recent_precip = list(parameters.get("PRECTOTCORR", {}).values())[-7:]
            recent_temp = list(parameters.get("T2M", {}).values())[-7:]
            
            avg_precip = sum(recent_precip) / len(recent_precip) if recent_precip else 0
            avg_temp = sum(recent_temp) / len(recent_temp) if recent_temp else 25
            
            # Simple vegetation health proxy (0-1)
            # Optimal: 20-30°C, 2-5mm daily precipitation
            temp_score = max(0, 1 - abs(avg_temp - 25) / 15)
            precip_score = min(1, avg_precip / 3.5) if avg_precip < 10 else max(0, 1 - (avg_precip - 10) / 20)
            vegetation_health = (temp_score + precip_score) / 2
            
            return {
                "vegetation_health": round(vegetation_health, 3),
                "ndvi_proxy": round(vegetation_health * 0.9, 3),  # NDVI typically 0-0.9
                "precipitation_16day": {
                    "total_mm": sum(parameters.get("PRECTOTCORR", {}).values()),
                    "average_daily": sum(parameters.get("PRECTOTCORR", {}).values()) / 16
                },
                "temperature_16day": {
                    "average": sum(parameters.get("T2M", {}).values()) / len(parameters.get("T2M", {})),
                    "min": min(parameters.get("T2M", {}).values()),
                    "max": max(parameters.get("T2M", {}).values())
                },
                "drought_risk": "high" if avg_precip < 1 else "medium" if avg_precip < 2.5 else "low",
                "data_source": "NASA POWER (satellite-derived)",
                "period": {
                    "start": start_date.date().isoformat(),
                    "end": end_date.date().isoformat()
                }
            }
        except Exception as e:
            print(f"Satellite data fetch error: {str(e)}")
            return {"error": str(e)}
    
    async def get_market_data(self, lat: float, lon: float) -> Dict:
        """
        Fetch regional market prices for major crops
        """
        try:
            # Determine nearest major market based on location
            nearest_market = self._get_nearest_market(lat, lon)
            
            # For now, use WFP VAM Food Prices API
            # Note: This is public data but requires proper attribution
            
            url = f"{MARKET_DATA_CONFIG['wfp_api']}market/list"
            
            response = self._session.get(url, timeout=15)
            response.raise_for_status()
            markets = response.json()
            
            # Filter markets by country (Kenya)
            kenya_markets = [m for m in markets if m.get("adm0_name") == "Kenya"]
            
            # Get prices for major crops
            crops = ["Maize", "Beans", "Tomatoes", "Potatoes", "Cabbage"]
            
            market_prices = {}
            for crop in crops:
                # Get latest prices for this commodity
                price_url = f"{MARKET_DATA_CONFIG['wfp_api']}commodity/list"
                price_response = self._session.get(price_url, timeout=10)
                
                if price_response.status_code == 200:
                    commodities = price_response.json()
                    matching = [c for c in commodities if crop.lower() in c.get("name", "").lower()]
                    
                    if matching:
                        market_prices[crop.lower()] = {
                            "price_kes_per_kg": self._estimate_regional_price(crop, nearest_market),
                            "market": nearest_market,
                            "currency": "KES",
                            "unit": "kg",
                            "last_updated": datetime.utcnow().date().isoformat()
                        }
            
            # Fallback to estimated prices if API fails
            if not market_prices:
                market_prices = self._get_fallback_market_prices(nearest_market)
            
            return {
                "nearest_market": nearest_market,
                "distance_km": self._calculate_distance_to_market(lat, lon, nearest_market),
                "prices": market_prices,
                "data_source": "Regional market data",
                "last_updated": datetime.utcnow().isoformat()
            }
        except Exception as e:
            print(f"Market data fetch error: {str(e)}")
            return self._get_fallback_market_prices(self._get_nearest_market(lat, lon))
    
    async def get_pest_alerts(self, lat: float, lon: float) -> List[Dict]:
        """
        Fetch regional pest outbreak alerts
        """
        try:
            # Check recent pest reports from community
            recent_reports = persistence.get_community_pest_feedback(lat, lon, radius_km=50)
            
            # Analyze patterns
            pest_counts = {}
            for report in recent_reports:
                pest_id = report.get("pest_disease_id")
                if pest_id:
                    pest_counts[pest_id] = pest_counts.get(pest_id, 0) + 1
            
            # Weather-based pest risk
            weather = await self.get_weather_data(lat, lon)
            current_temp = weather.get("current", {}).get("temperature", 25)
            current_humidity = weather.get("current", {}).get("humidity", 70)
            recent_rain = sum(day.get("rain", 0) for day in weather.get("forecast", [])[:3])
            
            alerts = []
            
            # Fall Armyworm risk (warm + humid)
            if current_temp > 22 and current_humidity > 60:
                alerts.append({
                    "pest": "Fall Armyworm",
                    "risk_level": "high" if pest_counts.get("fall_armyworm", 0) > 5 else "medium",
                    "reason": "Favorable temperature and humidity conditions",
                    "recent_reports": pest_counts.get("fall_armyworm", 0),
                    "recommended_action": "Scout fields regularly, consider early intervention"
                })
            
            # Late Blight risk (cool + wet)
            if current_temp < 25 and recent_rain > 10:
                alerts.append({
                    "pest": "Late Blight",
                    "risk_level": "high" if pest_counts.get("late_blight", 0) > 3 else "medium",
                    "reason": "Cool and wet conditions favor late blight",
                    "recent_reports": pest_counts.get("late_blight", 0),
                    "recommended_action": "Apply preventive fungicide if potatoes/tomatoes present"
                })
            
            # Aphids risk (warm + dry)
            if current_temp > 25 and recent_rain < 5:
                alerts.append({
                    "pest": "Aphids",
                    "risk_level": "medium",
                    "reason": "Warm and dry conditions favor aphid reproduction",
                    "recent_reports": pest_counts.get("aphids", 0),
                    "recommended_action": "Monitor for aphid colonies, check undersides of leaves"
                })
            
            return alerts
        except Exception as e:
            print(f"Pest alerts fetch error: {str(e)}")
            return []
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _get_nearest_market(self, lat: float, lon: float) -> str:
        """Determine nearest major market"""
        markets = {
            "Nairobi": (-1.2921, 36.8219),
            "Mombasa": (-4.0435, 39.6682),
            "Kisumu": (-0.0917, 34.7680),
            "Nakuru": (-0.3031, 36.0800),
            "Eldoret": (0.5143, 35.2698)
        }
        
        min_distance = float('inf')
        nearest = "Nairobi"
        
        for market, (m_lat, m_lon) in markets.items():
            distance = ((lat - m_lat)**2 + (lon - m_lon)**2)**0.5
            if distance < min_distance:
                min_distance = distance
                nearest = market
        
        return nearest
    
    def _calculate_distance_to_market(self, lat: float, lon: float, market: str) -> float:
        """Calculate approximate distance to market in km"""
        market_coords = {
            "Nairobi": (-1.2921, 36.8219),
            "Mombasa": (-4.0435, 39.6682),
            "Kisumu": (-0.0917, 34.7680),
            "Nakuru": (-0.3031, 36.0800),
            "Eldoret": (0.5143, 35.2698)
        }
        
        if market not in market_coords:
            return 0
        
        m_lat, m_lon = market_coords[market]
        
        # Haversine formula for great circle distance
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Earth's radius in km
        
        lat1, lon1 = radians(lat), radians(lon)
        lat2, lon2 = radians(m_lat), radians(m_lon)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return round(R * c, 1)
    
    def _estimate_regional_price(self, crop: str, market: str) -> float:
        """Estimate crop price based on market and season"""
        # Base prices (KES per kg) - updated regularly from market data
        base_prices = {
            "Maize": 45,
            "Beans": 120,
            "Tomatoes": 60,
            "Potatoes": 50,
            "Cabbage": 35
        }
        
        # Market multipliers
        market_multipliers = {
            "Nairobi": 1.15,  # Higher prices in capital
            "Mombasa": 1.10,
            "Kisumu": 1.00,
            "Nakuru": 0.95,
            "Eldoret": 0.95
        }
        
        # Seasonal adjustments (simple model)
        month = datetime.now().month
        harvest_months = {
            "Maize": [6, 7, 12, 1],  # June-July, Dec-Jan
            "Beans": [5, 6, 11, 12],
            "Tomatoes": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],  # Year-round
            "Potatoes": [3, 4, 5, 9, 10, 11],
            "Cabbage": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        }
        
        base_price = base_prices.get(crop, 50)
        market_mult = market_multipliers.get(market, 1.0)
        
        # Lower prices during harvest, higher off-season
        if month in harvest_months.get(crop, []):
            seasonal_mult = 0.85
        else:
            seasonal_mult = 1.15
        
        return round(base_price * market_mult * seasonal_mult, 1)
    
    def _get_fallback_market_prices(self, market: str) -> Dict:
        """Fallback market prices when API unavailable"""
        crops = ["Maize", "Beans", "Tomatoes", "Potatoes", "Cabbage"]
        return {
            "nearest_market": market,
            "prices": {
                crop.lower(): {
                    "price_kes_per_kg": self._estimate_regional_price(crop, market),
                    "market": market,
                    "currency": "KES",
                    "unit": "kg",
                    "last_updated": datetime.utcnow().date().isoformat(),
                    "data_source": "estimated"
                }
                for crop in crops
            }
        }
    
    def _get_fallback_weather(self, lat: float, lon: float) -> Dict:
        """Fallback weather data using WeatherAPI as backup"""
        try:
            url = f"{WEATHERAPI_CONFIG['base_url']}/forecast.json"
            params = {
                "key": WEATHERAPI_CONFIG["api_key"],
                "q": f"{lat},{lon}",
                "days": 7,
                "aqi": "no",
                "alerts": "yes"
            }
            
            response = self._session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                "current": {
                    "temperature": data["current"]["temp_c"],
                    "humidity": data["current"]["humidity"],
                    "wind_speed": data["current"]["wind_kph"] / 3.6,  # Convert to m/s
                    "description": data["current"]["condition"]["text"],
                    "icon": data["current"]["condition"]["icon"]
                },
                "forecast": [
                    {
                        "date": day["date"],
                        "temp_min": day["day"]["mintemp_c"],
                        "temp_max": day["day"]["maxtemp_c"],
                        "humidity": day["day"]["avghumidity"],
                        "rain": day["day"].get("totalprecip_mm", 0),
                        "description": day["day"]["condition"]["text"]
                    }
                    for day in data["forecast"]["forecastday"]
                ]
            }
        except:
            return {"error": "Weather data unavailable"}
    
    def _calculate_average(self, data_dict: Dict) -> float:
        """Calculate average from dict values"""
        values = [v for v in data_dict.values() if v is not None and v != -999]
        return round(sum(values) / len(values), 2) if values else 0
    
    def _calculate_sum(self, data_dict: Dict) -> float:
        """Calculate sum from dict values"""
        values = [v for v in data_dict.values() if v is not None and v != -999]
        return round(sum(values), 2) if values else 0


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

regional_data_service = RegionalDataService()


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

async def get_user_regional_data(user_id: str) -> Dict:
    """
    Get comprehensive regional data for user based on their location
    """
    user = persistence.get_user_by_id(user_id)
    
    if not user:
        return {"error": "User not found"}
    
    # Get user's location (from profile or first field)
    lat = user.get("latitude")
    lon = user.get("longitude")
    
    if not lat or not lon:
        # Try to get from first field
        fields = persistence.get_user_fields(user_id)
        if fields and len(fields) > 0:
            lat = fields[0].get("latitude", -1.2921)
            lon = fields[0].get("longitude", 36.8219)
        else:
            # Default to Nairobi
            lat, lon = -1.2921, 36.8219
    
    return await regional_data_service.get_comprehensive_data(lat, lon, user_id)


async def get_weather_for_location(lat: float, lon: float) -> Dict:
    """Get weather data for specific location"""
    return await regional_data_service.get_weather_data(lat, lon)


async def get_market_prices_for_location(lat: float, lon: float) -> Dict:
    """Get market prices for specific location"""
    return await regional_data_service.get_market_data(lat, lon)


async def get_pest_alerts_for_location(lat: float, lon: float) -> List[Dict]:
    """Get pest alerts for specific location"""
    return await regional_data_service.get_pest_alerts(lat, lon)
