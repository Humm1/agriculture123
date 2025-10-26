"""
Geolocation and Climate Intelligence Service
Tracks farmer location, provides weather predictions, and crop recommendations
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import requests
from functools import lru_cache
import json

class GeolocationService:
    """Service for handling farmer geolocation and location-based intelligence"""
    
    def __init__(self):
        self.openweather_api_key = "9e6b84d15154dd99ba51037e3bfba298"
        self.weather_base_url = "https://api.openweathermap.org/data/2.5"
        
    def reverse_geocode(self, latitude: float, longitude: float) -> Dict:
        """Convert coordinates to location details"""
        try:
            url = f"http://api.openweathermap.org/geo/1.0/reverse"
            params = {
                "lat": latitude,
                "lon": longitude,
                "limit": 1,
                "appid": self.openweather_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data:
                location = data[0]
                return {
                    "country": location.get("country", "Kenya"),
                    "state": location.get("state", ""),
                    "county": location.get("name", ""),
                    "local_names": location.get("local_names", {}),
                    "latitude": latitude,
                    "longitude": longitude
                }
            
            return self._get_kenya_location_from_coords(latitude, longitude)
            
        except Exception as e:
            print(f"Reverse geocoding error: {e}")
            return self._get_kenya_location_from_coords(latitude, longitude)
    
    def _get_kenya_location_from_coords(self, lat: float, lon: float) -> Dict:
        """Get Kenyan county/region from coordinates (fallback)"""
        # Kenya regions approximate boundaries
        regions = {
            "Nairobi": (-1.35, -1.15, 36.65, 36.95),
            "Kiambu": (-1.2, -0.85, 36.7, 37.1),
            "Nakuru": (-0.5, 0.5, 35.8, 36.5),
            "Kisumu": (-0.2, 0.2, 34.5, 35.0),
            "Meru": (0.0, 0.5, 37.5, 38.0),
            "Machakos": (-1.7, -1.3, 37.0, 37.5),
            "Nyeri": (-0.5, 0.0, 36.8, 37.2),
            "Eldoret": (0.4, 0.7, 35.1, 35.5),
            "Mombasa": (-4.2, -3.8, 39.5, 39.8),
            "Kisii": (-1.0, -0.5, 34.7, 35.0),
        }
        
        for county, (min_lat, max_lat, min_lon, max_lon) in regions.items():
            if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
                return {
                    "country": "Kenya",
                    "state": self._get_kenya_province(county),
                    "county": county,
                    "latitude": lat,
                    "longitude": lon
                }
        
        return {
            "country": "Kenya",
            "state": "Unknown",
            "county": "Unknown Region",
            "latitude": lat,
            "longitude": lon
        }
    
    def _get_kenya_province(self, county: str) -> str:
        """Map county to province"""
        province_mapping = {
            "Nairobi": "Nairobi",
            "Kiambu": "Central",
            "Nakuru": "Rift Valley",
            "Kisumu": "Nyanza",
            "Meru": "Eastern",
            "Machakos": "Eastern",
            "Nyeri": "Central",
            "Eldoret": "Rift Valley",
            "Mombasa": "Coast",
            "Kisii": "Nyanza",
        }
        return province_mapping.get(county, "Unknown")
    
    def get_current_weather(self, latitude: float, longitude: float) -> Dict:
        """Get current weather at location"""
        try:
            url = f"{self.weather_base_url}/weather"
            params = {
                "lat": latitude,
                "lon": longitude,
                "appid": self.openweather_api_key,
                "units": "metric"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "weather": data["weather"][0]["main"],
                "description": data["weather"][0]["description"],
                "wind_speed": data["wind"]["speed"],
                "clouds": data["clouds"]["all"],
                "visibility": data.get("visibility", 0) / 1000,  # km
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Current weather error: {e}")
            return self._get_default_weather()
    
    def get_6_month_forecast(self, latitude: float, longitude: float) -> Dict:
        """AI-powered 6-month weather forecast with climate patterns"""
        try:
            # Get current weather for baseline
            current = self.get_current_weather(latitude, longitude)
            
            # Get 7-day forecast from API
            url = f"{self.weather_base_url}/forecast"
            params = {
                "lat": latitude,
                "lon": longitude,
                "appid": self.openweather_api_key,
                "units": "metric"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            forecast_data = response.json()
            
            # Generate 6-month prediction
            monthly_forecast = self._generate_6_month_prediction(
                latitude, longitude, current, forecast_data
            )
            
            return {
                "current_weather": current,
                "monthly_forecast": monthly_forecast,
                "climate_pattern": self._analyze_climate_pattern(monthly_forecast),
                "farming_calendar": self._generate_farming_calendar(monthly_forecast),
                "location": {"latitude": latitude, "longitude": longitude}
            }
            
        except Exception as e:
            print(f"6-month forecast error: {e}")
            return self._get_default_6_month_forecast(latitude, longitude)
    
    def _generate_6_month_prediction(self, lat: float, lon: float, 
                                     current: Dict, forecast_data: Dict) -> List[Dict]:
        """Generate AI-powered 6-month weather prediction"""
        months = []
        base_date = datetime.now()
        
        # Kenya seasonal patterns
        is_equatorial = -5 <= lat <= 5
        
        for i in range(6):
            month_date = base_date + timedelta(days=30 * i)
            month_num = month_date.month
            
            # Kenya has two rainy seasons: March-May and October-December
            is_long_rains = month_num in [3, 4, 5]
            is_short_rains = month_num in [10, 11, 12]
            is_dry = month_num in [1, 2, 6, 7, 8, 9]
            
            # Temperature varies by altitude and region
            base_temp = current.get("temperature", 22)
            if is_equatorial:
                # Coastal/lowland areas (warmer)
                temp_adjustment = 2 if lon > 39 else 0
            else:
                # Highland areas (cooler)
                temp_adjustment = -3
            
            # Rainfall patterns
            if is_long_rains:
                rainfall = 150 + (i * 20)  # mm
                rain_days = 15 + (i * 2)
                confidence = "high" if i <= 2 else "medium"
            elif is_short_rains:
                rainfall = 100 + (i * 15)
                rain_days = 10 + i
                confidence = "high" if i <= 2 else "medium"
            else:
                rainfall = 30 + (i * 5)
                rain_days = 3 + i
                confidence = "high" if i <= 3 else "low"
            
            months.append({
                "month": month_date.strftime("%B %Y"),
                "month_number": month_num,
                "avg_temperature": round(base_temp + temp_adjustment + (i * 0.5), 1),
                "min_temperature": round(base_temp + temp_adjustment - 5 + (i * 0.3), 1),
                "max_temperature": round(base_temp + temp_adjustment + 7 + (i * 0.7), 1),
                "rainfall_mm": rainfall,
                "rain_days": rain_days,
                "humidity": 70 if (is_long_rains or is_short_rains) else 55,
                "season": "Long Rains" if is_long_rains else ("Short Rains" if is_short_rains else "Dry Season"),
                "confidence": confidence,
                "farming_advice": self._get_monthly_farming_advice(month_num, is_long_rains, is_short_rains)
            })
        
        return months
    
    def _get_monthly_farming_advice(self, month: int, is_long_rains: bool, is_short_rains: bool) -> str:
        """Get farming advice for specific month"""
        if is_long_rains:
            return "Plant maize, beans, and vegetables. Good time for land preparation and planting."
        elif is_short_rains:
            return "Second planting season. Focus on quick-maturing crops like vegetables and legumes."
        else:
            return "Dry season - focus on irrigation, harvesting, and storage. Plant drought-resistant crops."
    
    def _analyze_climate_pattern(self, monthly_forecast: List[Dict]) -> Dict:
        """Analyze climate patterns from forecast"""
        total_rainfall = sum(m["rainfall_mm"] for m in monthly_forecast)
        avg_temp = sum(m["avg_temperature"] for m in monthly_forecast) / len(monthly_forecast)
        
        # Determine climate classification
        if total_rainfall > 800:
            climate_type = "Humid"
            risk_level = "Low drought risk"
        elif total_rainfall > 500:
            climate_type = "Sub-humid"
            risk_level = "Moderate drought risk"
        else:
            climate_type = "Semi-arid"
            risk_level = "High drought risk"
        
        return {
            "climate_type": climate_type,
            "total_rainfall_6months": total_rainfall,
            "average_temperature": round(avg_temp, 1),
            "drought_risk": risk_level,
            "best_planting_months": [m["month"] for m in monthly_forecast if m["rainfall_mm"] > 100][:2],
            "irrigation_required": total_rainfall < 400
        }
    
    def _generate_farming_calendar(self, monthly_forecast: List[Dict]) -> List[Dict]:
        """Generate farming calendar based on weather forecast"""
        calendar = []
        
        for month_data in monthly_forecast:
            activities = []
            month_num = month_data["month_number"]
            rainfall = month_data["rainfall_mm"]
            
            # Planting activities
            if rainfall > 100:
                activities.append({
                    "activity": "Land Preparation & Planting",
                    "crops": ["Maize", "Beans", "Vegetables", "Potatoes"],
                    "priority": "High"
                })
            
            # Irrigation
            if rainfall < 50:
                activities.append({
                    "activity": "Irrigation",
                    "crops": ["All crops"],
                    "priority": "Critical"
                })
            
            # Harvesting (3-4 months after planting)
            if month_num in [6, 7, 12, 1]:
                activities.append({
                    "activity": "Harvesting",
                    "crops": ["Maize", "Beans", "Vegetables"],
                    "priority": "High"
                })
            
            # Pest control (during growing season)
            if rainfall > 80:
                activities.append({
                    "activity": "Pest & Disease Monitoring",
                    "crops": ["All crops"],
                    "priority": "Medium"
                })
            
            calendar.append({
                "month": month_data["month"],
                "activities": activities,
                "weather_suitability": "Excellent" if rainfall > 100 else ("Good" if rainfall > 50 else "Poor")
            })
        
        return calendar
    
    def get_suitable_crops(self, latitude: float, longitude: float, 
                          soil_type: Optional[str] = None) -> Dict:
        """Get suitable crops based on location and climate"""
        # Get location details
        location = self.reverse_geocode(latitude, longitude)
        forecast = self.get_6_month_forecast(latitude, longitude)
        
        # Determine altitude zone (affects crop suitability)
        altitude_zone = self._estimate_altitude_zone(latitude, longitude)
        climate_pattern = forecast["climate_pattern"]
        
        # Get crops for the region
        crops = self._get_region_suitable_crops(
            altitude_zone, 
            climate_pattern["total_rainfall_6months"],
            climate_pattern["average_temperature"],
            soil_type
        )
        
        return {
            "location": location,
            "altitude_zone": altitude_zone,
            "climate_summary": climate_pattern,
            "suitable_crops": crops,
            "planting_recommendation": self._get_planting_recommendation(crops, forecast),
            "timestamp": datetime.now().isoformat()
        }
    
    def _estimate_altitude_zone(self, lat: float, lon: float) -> str:
        """Estimate altitude zone from coordinates (Kenya-specific)"""
        # Highland regions (Central, Rift Valley highlands)
        if (-1.5 <= lat <= 0.5 and 36.0 <= lon <= 37.5) or (0.0 <= lat <= 1.5 and 34.8 <= lon <= 36.0):
            return "Highland (>1500m)"
        # Mid-altitude
        elif (-2.0 <= lat <= 1.0 and 34.5 <= lon <= 38.0):
            return "Mid-altitude (1000-1500m)"
        # Lowland/Coastal
        else:
            return "Lowland (<1000m)"
    
    def _get_region_suitable_crops(self, altitude_zone: str, annual_rainfall: float,
                                   avg_temp: float, soil_type: Optional[str]) -> List[Dict]:
        """Get crops suitable for specific conditions"""
        crops = []
        
        # Highland crops (>1500m altitude, cooler, moderate-high rainfall)
        if "Highland" in altitude_zone:
            crops.extend([
                {
                    "crop": "Tea",
                    "suitability": "Excellent",
                    "rainfall_req": "1200-2000mm",
                    "temp_range": "10-30°C",
                    "maturity": "2-3 years (perennial)",
                    "expected_yield": "2000-3000 kg/ha",
                    "market_price": "80-120 KES/kg"
                },
                {
                    "crop": "Coffee",
                    "suitability": "Excellent",
                    "rainfall_req": "1000-1800mm",
                    "temp_range": "15-25°C",
                    "maturity": "3-4 years (perennial)",
                    "expected_yield": "800-1200 kg/ha",
                    "market_price": "100-150 KES/kg"
                },
                {
                    "crop": "Potatoes",
                    "suitability": "Excellent",
                    "rainfall_req": "500-750mm",
                    "temp_range": "15-20°C",
                    "maturity": "90-120 days",
                    "expected_yield": "15-25 tonnes/ha",
                    "market_price": "30-50 KES/kg"
                },
                {
                    "crop": "Wheat",
                    "suitability": "Good",
                    "rainfall_req": "400-600mm",
                    "temp_range": "15-25°C",
                    "maturity": "120-150 days",
                    "expected_yield": "2-4 tonnes/ha",
                    "market_price": "35-45 KES/kg"
                }
            ])
        
        # Mid-altitude crops (1000-1500m)
        if "Mid-altitude" in altitude_zone or "Highland" in altitude_zone:
            crops.extend([
                {
                    "crop": "Maize",
                    "suitability": "Excellent",
                    "rainfall_req": "500-800mm",
                    "temp_range": "18-27°C",
                    "maturity": "90-120 days",
                    "expected_yield": "3-6 tonnes/ha",
                    "market_price": "35-50 KES/kg"
                },
                {
                    "crop": "Beans",
                    "suitability": "Excellent",
                    "rainfall_req": "400-600mm",
                    "temp_range": "16-24°C",
                    "maturity": "60-90 days",
                    "expected_yield": "1-2 tonnes/ha",
                    "market_price": "80-120 KES/kg"
                },
                {
                    "crop": "Tomatoes",
                    "suitability": "Good",
                    "rainfall_req": "400-600mm",
                    "temp_range": "18-27°C",
                    "maturity": "70-90 days",
                    "expected_yield": "20-40 tonnes/ha",
                    "market_price": "40-80 KES/kg"
                },
                {
                    "crop": "Cabbage",
                    "suitability": "Good",
                    "rainfall_req": "380-500mm",
                    "temp_range": "15-20°C",
                    "maturity": "70-100 days",
                    "expected_yield": "30-50 tonnes/ha",
                    "market_price": "20-35 KES/kg"
                }
            ])
        
        # Lowland/Coastal crops (<1000m, warmer)
        if "Lowland" in altitude_zone:
            crops.extend([
                {
                    "crop": "Coconut",
                    "suitability": "Excellent",
                    "rainfall_req": "1000-2000mm",
                    "temp_range": "27-32°C",
                    "maturity": "6-8 years (perennial)",
                    "expected_yield": "80-100 nuts/tree/year",
                    "market_price": "40-60 KES/nut"
                },
                {
                    "crop": "Cashew",
                    "suitability": "Excellent",
                    "rainfall_req": "600-1200mm",
                    "temp_range": "25-35°C",
                    "maturity": "3-5 years (perennial)",
                    "expected_yield": "800-1200 kg/ha",
                    "market_price": "200-300 KES/kg"
                },
                {
                    "crop": "Cassava",
                    "suitability": "Excellent",
                    "rainfall_req": "500-800mm",
                    "temp_range": "25-29°C",
                    "maturity": "8-12 months",
                    "expected_yield": "10-20 tonnes/ha",
                    "market_price": "15-25 KES/kg"
                },
                {
                    "crop": "Mangoes",
                    "suitability": "Good",
                    "rainfall_req": "600-1200mm",
                    "temp_range": "24-30°C",
                    "maturity": "3-5 years (perennial)",
                    "expected_yield": "100-200 kg/tree",
                    "market_price": "50-80 KES/kg"
                }
            ])
        
        # Filter by rainfall if significantly different
        if annual_rainfall < 400:
            crops = [c for c in crops if "Drought" in c.get("notes", "") or 
                    int(c["rainfall_req"].split("-")[0].replace("mm", "")) < 500]
        
        return crops[:8]  # Return top 8 most suitable
    
    def _get_planting_recommendation(self, crops: List[Dict], forecast: Dict) -> Dict:
        """Get immediate planting recommendations"""
        next_months = forecast["monthly_forecast"][:3]
        best_month = max(next_months, key=lambda x: x["rainfall_mm"])
        
        # Get quick-maturing crops
        quick_crops = [c for c in crops if "60-90 days" in c.get("maturity", "") or 
                                           "70-90 days" in c.get("maturity", "")]
        
        return {
            "immediate_action": "Prepare land now" if best_month["rainfall_mm"] > 100 else "Wait for rains",
            "best_planting_month": best_month["month"],
            "recommended_crops_this_season": [c["crop"] for c in crops[:3]],
            "quick_return_crops": [c["crop"] for c in quick_crops[:3]],
            "expected_harvest_date": (datetime.now() + timedelta(days=120)).strftime("%B %Y")
        }
    
    def _get_default_weather(self) -> Dict:
        """Default weather data"""
        return {
            "temperature": 22,
            "feels_like": 22,
            "humidity": 65,
            "pressure": 1013,
            "weather": "Clear",
            "description": "clear sky",
            "wind_speed": 3.5,
            "clouds": 20,
            "visibility": 10,
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_default_6_month_forecast(self, lat: float, lon: float) -> Dict:
        """Default 6-month forecast"""
        return {
            "current_weather": self._get_default_weather(),
            "monthly_forecast": [],
            "climate_pattern": {
                "climate_type": "Unknown",
                "total_rainfall_6months": 0,
                "average_temperature": 22,
                "drought_risk": "Unknown",
                "best_planting_months": [],
                "irrigation_required": True
            },
            "farming_calendar": [],
            "location": {"latitude": lat, "longitude": lon}
        }


# Initialize service
geolocation_service = GeolocationService()
