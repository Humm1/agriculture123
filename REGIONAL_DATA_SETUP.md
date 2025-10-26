# Regional Data Integration Setup Guide

## Overview
This guide explains how to set up real-time regional data integration for AgroShield, replacing all hardcoded JSON data with live weather, satellite, and market information.

## 🌍 Data Sources Integrated

### 1. **Weather Data**
- **OpenWeatherMap** (Primary): https://openweathermap.org/api
  - Current weather conditions
  - 7-day forecast
  - Weather alerts
  - Free tier: 1,000 calls/day
  
- **WeatherAPI** (Fallback): https://www.weatherapi.com
  - Real-time weather
  - 7-day forecast
  - Free tier: 1,000,000 calls/month

### 2. **Climate & Satellite Data**
- **NASA POWER** (FREE): https://power.larc.nasa.gov
  - Historical climate data (30+ years)
  - Temperature, precipitation, humidity
  - Wind speed, solar radiation
  - Satellite-derived data
  - No API key required!

### 3. **Market Price Data**
- **WFP VAM Food Prices API**: https://api.wfp.org/vam-data-bridges/
  - Global food prices
  - Kenya market coverage
  - Public data, rate-limited
  
- **Regional estimates**: Based on seasonal patterns and market locations

### 4. **Pest Outbreak Detection**
- Community reports (from app database)
- Weather-based risk models
- Real-time alerts

---

## 🔑 API Keys Setup

### Step 1: OpenWeatherMap
1. Go to https://home.openweathermap.org/users/sign_up
2. Create a free account
3. Navigate to API keys section
4. Copy your API key
5. Add to `.env` file:
   ```
   OPENWEATHER_API_KEY=your_api_key_here
   ```

### Step 2: WeatherAPI (Fallback)
1. Go to https://www.weatherapi.com/signup.aspx
2. Create a free account
3. Copy your API key from dashboard
4. Add to `.env` file:
   ```
   WEATHERAPI_KEY=your_api_key_here
   ```

### Step 3: NASA POWER (No Key Required!)
- NASA POWER is completely free for agricultural applications
- No registration required
- No API key needed
- Just works! 🎉

### Step 4: Sentinel Hub (Optional - Advanced Satellite Imagery)
1. Go to https://www.sentinel-hub.com
2. Create account
3. Create OAuth client
4. Add to `.env`:
   ```
   SENTINEL_CLIENT_ID=your_client_id
   SENTINEL_CLIENT_SECRET=your_client_secret
   ```

---

## 📝 Environment Variables

Create a `.env` file in `backend/` directory:

```bash
# Weather APIs
OPENWEATHER_API_KEY=your_openweathermap_key_here
WEATHERAPI_KEY=your_weatherapi_key_here

# Satellite (Optional)
SENTINEL_CLIENT_ID=your_sentinel_client_id
SENTINEL_CLIENT_SECRET=your_sentinel_client_secret

# No keys needed for:
# - NASA POWER (free public API)
# - WFP VAM (public data)
```

Update `regional_data_service.py` to load environment variables:

```python
import os
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_CONFIG = {
    "api_key": os.getenv("OPENWEATHER_API_KEY"),
    "base_url": "https://api.openweathermap.org/data/2.5",
    "onecall_url": "https://api.openweathermap.org/data/3.0/onecall"
}

WEATHERAPI_CONFIG = {
    "api_key": os.getenv("WEATHERAPI_KEY"),
    "base_url": "https://api.weatherapi.com/v1"
}

SENTINEL_CONFIG = {
    "client_id": os.getenv("SENTINEL_CLIENT_ID"),
    "client_secret": os.getenv("SENTINEL_CLIENT_SECRET"),
    "base_url": "https://services.sentinel-hub.com"
}
```

---

## 🚀 Installation & Setup

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure APIs
```bash
# Create .env file
cp .env.example .env

# Edit .env and add your API keys
nano .env
```

### 3. Test API Connections
```bash
# Start backend server
uvicorn app.main:app --reload

# Test health endpoint
curl http://localhost:8000/api/regional/health
```

### 4. Update Frontend
In your mobile app, add API call on login:

```javascript
// Mobile app: Call on user login
async function onUserLogin(userId) {
  try {
    // Fetch comprehensive regional data
    const response = await fetch(
      `https://your-api.com/api/regional/comprehensive/${userId}`
    );
    const data = await response.json();
    
    // Store in app state
    setRegionalData(data);
    
    // Display to user
    console.log("Weather:", data.weather.current);
    console.log("Market Prices:", data.market.prices);
    console.log("Pest Alerts:", data.pest_alerts);
    
  } catch (error) {
    console.error("Failed to fetch regional data:", error);
  }
}
```

---

## 📡 API Endpoints

### Get Comprehensive Regional Data (Login)
```bash
GET /api/regional/comprehensive/{user_id}
```
Returns: weather, climate, satellite, market prices, pest alerts

### Get Weather Only
```bash
GET /api/regional/weather?lat=-1.2921&lon=36.8219
```

### Get Market Prices
```bash
GET /api/regional/market-prices?lat=-1.2921&lon=36.8219
```

### Get Pest Alerts
```bash
GET /api/regional/pest-alerts?lat=-1.2921&lon=36.8219
```

### Get Climate History
```bash
GET /api/regional/climate-history?lat=-1.2921&lon=36.8219&days_back=30
```

### Get Satellite Data
```bash
GET /api/regional/satellite?lat=-1.2921&lon=36.8219
```

### Update User Location
```bash
POST /api/regional/update-user-location
Body: {
  "user_id": "user123",
  "lat": -1.2921,
  "lon": 36.8219
}
```

### Check API Health
```bash
GET /api/regional/health
```

### Get Data Sources Info
```bash
GET /api/regional/data-sources
```

---

## 🧪 Testing with Postman

### 1. Import Collection
Create a Postman collection with these requests:

**Test 1: Health Check**
```
GET http://localhost:8000/api/regional/health
```

**Test 2: Get Weather**
```
GET http://localhost:8000/api/regional/weather?lat=-1.2921&lon=36.8219
```

**Test 3: Get Comprehensive Data**
```
GET http://localhost:8000/api/regional/comprehensive/test_user_123
```

### 2. Expected Responses

**Weather Response:**
```json
{
  "current": {
    "temperature": 24.5,
    "humidity": 65,
    "wind_speed": 3.2,
    "description": "partly cloudy",
    "rain_1h": 0
  },
  "forecast": [
    {
      "date": "2025-10-25",
      "temp_min": 18,
      "temp_max": 28,
      "rain": 2.5,
      "description": "light rain"
    }
  ]
}
```

**Market Prices Response:**
```json
{
  "nearest_market": "Nairobi",
  "distance_km": 12.5,
  "prices": {
    "maize": {
      "price_kes_per_kg": 48,
      "market": "Nairobi",
      "last_updated": "2025-10-24"
    },
    "beans": {
      "price_kes_per_kg": 125,
      "market": "Nairobi"
    }
  }
}
```

---

## 🔄 Data Update Frequencies

| Data Type | Update Frequency | Cache Duration |
|-----------|------------------|----------------|
| Weather Current | Hourly | 30 minutes |
| Weather Forecast | 6 hours | 30 minutes |
| Climate History | Daily | 24 hours |
| Satellite Data | Daily | 24 hours |
| Market Prices | Weekly | 6 hours |
| Pest Alerts | Real-time | 1 hour |

---

## 🎯 Integration Points

### 1. **Login Flow**
```
User Login → Fetch Regional Data → Cache in App → Display Dashboard
```

### 2. **Premium Features Integration**
- **Yield Forecasting**: Uses real weather + market prices
- **Market Alerts**: Uses live market data from multiple cities
- **What-If Analysis**: Weather-adjusted predictions

### 3. **Pest Detection**
- Weather-based outbreak risk
- Community reports integration
- Real-time alerts

### 4. **Planting Calendar**
- NASA POWER climate data
- Historical rainfall patterns
- Optimal planting windows

---

## 🐛 Troubleshooting

### Issue: "Weather data unavailable"
**Solution:**
1. Check API key in `.env`
2. Verify API key is active on OpenWeatherMap dashboard
3. Check free tier limits (1,000 calls/day)
4. Fallback to WeatherAPI automatically

### Issue: "Market data fetch error"
**Solution:**
1. WFP API may be rate-limited
2. System falls back to regional estimates
3. Check internet connection
4. Verify lat/lon coordinates are valid

### Issue: "NASA POWER timeout"
**Solution:**
1. NASA API can be slow (10-30 seconds)
2. Increase timeout in regional_data_service.py
3. Use cached data for repeat requests
4. Consider pre-fetching for known locations

### Issue: "Pest alerts empty"
**Solution:**
1. No community reports in area yet
2. Weather-based alerts still work
3. Encourage farmers to report treatments

---

## 📊 Performance Optimization

### 1. **Caching Strategy**
```python
# Implement Redis caching for frequently accessed data
from functools import lru_cache
from datetime import datetime, timedelta

@lru_cache(maxsize=100)
def get_cached_weather(lat: float, lon: float, cache_key: str):
    # Cache weather data for 30 minutes
    return regional_data_service.get_weather_data(lat, lon)
```

### 2. **Parallel API Calls**
Already implemented in `get_comprehensive_data()` using `asyncio.gather()`

### 3. **Fallback Chain**
```
OpenWeatherMap → WeatherAPI → Cached Data → Default Values
```

---

## 🔒 Security Best Practices

1. **Never commit .env file**
   ```bash
   # Add to .gitignore
   echo ".env" >> .gitignore
   ```

2. **Use environment variables in production**
   ```bash
   # Heroku
   heroku config:set OPENWEATHER_API_KEY=your_key
   
   # AWS
   aws ssm put-parameter --name OPENWEATHER_API_KEY --value your_key
   ```

3. **Rate limiting**
   ```python
   # Add rate limiting middleware
   from slowapi import Limiter
   
   limiter = Limiter(key_func=get_remote_address)
   
   @app.get("/api/regional/weather")
   @limiter.limit("30/minute")
   async def get_weather():
       ...
   ```

---

## 📈 Monitoring & Analytics

### Track API Usage
```python
# Add logging to regional_data_service.py
import logging

logging.info(f"Weather API call: {lat},{lon} - Status: {response.status_code}")
```

### Monitor API Health
```bash
# Set up cron job to check API health every 5 minutes
*/5 * * * * curl http://your-api.com/api/regional/health
```

### Alert on Failures
```python
# Send alert if APIs are down
if health_status["overall_status"] != "operational":
    send_admin_alert("Regional APIs degraded")
```

---

## 🎓 Next Steps

1. ✅ **Get API keys** (OpenWeatherMap + WeatherAPI)
2. ✅ **Configure .env file**
3. ✅ **Test endpoints** with Postman
4. ✅ **Update mobile app** to call `/comprehensive/{user_id}` on login
5. ✅ **Monitor API usage** in production
6. ✅ **Set up alerts** for API failures
7. 🔜 **Add Sentinel Hub** for advanced satellite imagery (optional)
8. 🔜 **Integrate more market APIs** (EAGC, local markets)

---

## 📞 Support & Resources

- **OpenWeatherMap Docs**: https://openweathermap.org/api
- **NASA POWER Docs**: https://power.larc.nasa.gov/docs/
- **WFP VAM API**: https://docs.api.wfp.org
- **Sentinel Hub Docs**: https://docs.sentinel-hub.com

---

## 💡 Pro Tips

1. **Cache aggressively**: Weather data doesn't change every second
2. **Use NASA POWER**: It's free and very reliable
3. **Fallback gracefully**: Always have default values
4. **Pre-fetch on login**: Don't wait for user to request data
5. **Show data freshness**: Display "Last updated: 5 minutes ago"
6. **Handle offline mode**: Cache last successful response

---

**🎉 That's it! Your AgroShield backend now uses real-time regional data instead of hardcoded JSON!**
