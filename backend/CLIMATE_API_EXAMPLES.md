# Climate Engine API Examples

## Overview
Test the Climate Engine API endpoints with these examples. Replace `localhost:8000` with your server URL.

---

## 1. Crowdsourced Data Collection

### Submit Rain Report
```bash
curl -X POST http://localhost:8000/api/climate/rain_report ^
  -H "Content-Type: application/json" ^
  -d "{\"farmer_id\":\"farmer_001\",\"location\":{\"lat\":-1.2921,\"lon\":36.8219},\"amount\":\"moderate\"}"
```

### Get Recent Rain Reports
```bash
curl "http://localhost:8000/api/climate/rain_reports?days=7&lat=-1.2921&lon=36.8219"
```

### Submit Soil Moisture Report
```bash
curl -X POST http://localhost:8000/api/climate/soil_report ^
  -H "Content-Type: application/json" ^
  -d "{\"farmer_id\":\"farmer_001\",\"field_id\":\"field_001\",\"moisture_level\":\"damp\"}"
```

### Get Latest Soil Report
```bash
curl http://localhost:8000/api/climate/soil_report/farmer_001/field_001
```

---

## 2. LCRS (Climate Risk Score)

### Calculate LCRS
```bash
curl -X POST http://localhost:8000/api/climate/lcrs/calculate ^
  -H "Content-Type: application/json" ^
  -d "{\"farmer_id\":\"farmer_001\",\"field_id\":\"field_001\",\"location\":{\"lat\":-1.2921,\"lon\":36.8219},\"forecast_months\":3}"
```

**Expected Response:**
```json
{
  "score": 27.1,
  "risk_level": "low",
  "factors": {
    "rain_adequacy": 0.65,
    "soil_moisture": 0.85,
    "seasonal_forecast": 0.3,
    "drought_risk": 0.24,
    "flood_risk": 0.12
  },
  "recommendations": [
    "Conditions favorable for planting"
  ],
  "valid_until": "2026-01-24T10:00:00Z"
}
```

### Get Cached LCRS
```bash
curl http://localhost:8000/api/climate/lcrs/farmer_001/field_001
```

---

## 3. Planting Window & Alerts

### Get Optimal Planting Window
```bash
curl "http://localhost:8000/api/climate/planting_window/maize?lat=-1.2921&lon=36.8219"
```

**Response:**
```json
{
  "start_date": "2025-10-01T00:00:00",
  "end_date": "2025-10-31T00:00:00",
  "rationale": "Optimal for short_rains season based on historical rainfall patterns",
  "confidence": 0.8
}
```

### Check Planting Status
```bash
curl -X POST http://localhost:8000/api/climate/planting/check_status ^
  -H "Content-Type: application/json" ^
  -d "{\"farmer_id\":\"farmer_001\",\"field_id\":\"field_001\",\"crop\":\"maize\",\"location\":{\"lat\":-1.2921,\"lon\":36.8219}}"
```

**Response (Optimal):**
```json
{
  "status": "optimal",
  "days_difference": 0,
  "message": "✅ IDEAL TIME: You are within the optimal planting window for maize. Plant now for best results!",
  "alternative_crops": [],
  "diversification_advice": null
}
```

**Response (Late):**
```json
{
  "status": "late",
  "days_difference": 15,
  "message": "⚠️ LATE: You are 15 days past optimal window. Consider fast-maturing maize varieties or switch to: beans, cowpeas, amaranth",
  "alternative_crops": ["beans", "cowpeas", "amaranth"],
  "diversification_advice": "🌾 RISK HEDGE: Dedicate 20% of land to drought-tolerant cassava or sorghum to reduce crop failure risk."
}
```

### Record Planting
```bash
curl -X POST http://localhost:8000/api/climate/planting/record ^
  -H "Content-Type: application/json" ^
  -d "{\"farmer_id\":\"farmer_001\",\"field_id\":\"field_001\",\"crop\":\"maize\",\"planting_date\":\"2025-10-24T00:00:00\",\"variety\":\"short_season\",\"area_hectares\":2.5}"
```

### Get Active Plantings
```bash
curl http://localhost:8000/api/climate/planting/active/farmer_001
```

---

## 4. Crop Diversification

### Get Diversification Plan
```bash
curl -X POST http://localhost:8000/api/climate/diversification/plan ^
  -H "Content-Type: application/json" ^
  -d "{\"farmer_id\":\"farmer_001\",\"field_id\":\"field_001\",\"location\":{\"lat\":-1.2921,\"lon\":36.8219},\"total_area_hectares\":5.0}"
```

**Response (Low Risk):**
```json
{
  "primary_crop": {
    "crop": "maize",
    "percentage": 90,
    "area_hectares": 4.5
  },
  "diversification_crops": [
    {
      "crop": "beans",
      "percentage": 10,
      "area_hectares": 0.5
    }
  ],
  "rationale": "Low climate risk allows focus on primary income crop with minimal diversification."
}
```

**Response (High Risk):**
```json
{
  "primary_crop": {
    "crop": "maize",
    "percentage": 50,
    "area_hectares": 2.5
  },
  "diversification_crops": [
    {
      "crop": "cassava",
      "percentage": 30,
      "area_hectares": 1.5
    },
    {
      "crop": "sorghum",
      "percentage": 20,
      "area_hectares": 1.0
    }
  ],
  "rationale": "🚨 HIGH RISK YEAR: Maximize drought-resistant crops (cassava, sorghum) to ensure food security even if rains fail."
}
```

---

## 5. Harvest Prediction

### Generate Harvest Prediction
```bash
curl -X POST http://localhost:8000/api/climate/harvest/predict ^
  -H "Content-Type: application/json" ^
  -d "{\"farmer_id\":\"farmer_001\",\"field_id\":\"field_001\",\"planting_date\":\"2025-10-24T00:00:00\",\"crop\":\"maize\",\"variety\":\"short_season\",\"location\":{\"lat\":-1.2921,\"lon\":36.8219},\"sensor_id\":\"ble_sensor_001\",\"language\":\"en\"}"
```

**Response (Good Conditions):**
```json
{
  "harvest_prediction": {
    "predicted_date": "2026-01-22T00:00:00",
    "harvest_window_start": "2026-01-15T00:00:00",
    "harvest_window_end": "2026-01-29T00:00:00",
    "maturity_days": 90
  },
  "weather_forecast": {
    "conditions": "dry",
    "rain_probability": 0.2,
    "advice": "Good for sun drying! Harvest and spread crops in open air.",
    "icon": "☀️"
  },
  "storage_status": {
    "ready": true,
    "temperature": 22,
    "humidity": 65,
    "issues": [],
    "recommendations": []
  },
  "alert_message": "✅ GOOD NEWS: Your maize will be ready during a predicted ☀️ dry spell. Perfect for sun drying!\n\n✅ STORAGE READY: Temperature 22°C, Humidity 65% - Ideal conditions!",
  "alert_level": "info",
  "action_items": ["Prepare open drying area"]
}
```

**Response (Risky Conditions):**
```json
{
  "harvest_prediction": {
    "predicted_date": "2026-01-22T00:00:00",
    "harvest_window_start": "2026-01-15T00:00:00",
    "harvest_window_end": "2026-01-29T00:00:00",
    "maturity_days": 90
  },
  "weather_forecast": {
    "conditions": "wet",
    "rain_probability": 0.8,
    "advice": "High rain risk! Prepare covered drying area or mechanical dryer.",
    "icon": "🌧️"
  },
  "storage_status": {
    "ready": false,
    "temperature": 32,
    "humidity": 85,
    "issues": [
      "Temperature too high (32°C)",
      "Humidity too high (85%)"
    ],
    "recommendations": [
      "Cool storage before bringing in harvest",
      "Increase ventilation to reduce moisture"
    ]
  },
  "alert_message": "🛑 HARVEST RISK: Your maize is ready during predicted 🌧️ peak rain. Prepare for covered drying.\n\n🏠 STORAGE NOT READY: Temperature too high (32°C), Humidity too high (85%). Fix BEFORE harvest!",
  "alert_level": "critical",
  "action_items": [
    "Arrange covered drying space NOW",
    "Consider renting mechanical dryer",
    "Cool storage before bringing in harvest",
    "Increase ventilation to reduce moisture"
  ]
}
```

### Get Harvest Calendar
```bash
curl http://localhost:8000/api/climate/harvest/calendar/farmer_001
```

### Get All Harvest Predictions
```bash
curl http://localhost:8000/api/climate/harvest/predictions/farmer_001
```

---

## 6. Farmer Dashboard

### Get Complete Dashboard
```bash
curl "http://localhost:8000/api/climate/dashboard/farmer_001?field_id=field_001"
```

**Response:**
```json
{
  "lcrs": {
    "score": 27.1,
    "risk_level": "low",
    "factors": {...},
    "recommendations": [...]
  },
  "active_plantings": {
    "count": 2,
    "plantings": [
      {
        "crop": "maize",
        "planting_date": "2025-10-24T00:00:00",
        "variety": "short_season",
        "area_hectares": 2.5,
        "field_id": "field_001"
      }
    ]
  },
  "upcoming_harvests": {
    "count": 1,
    "predictions": [...]
  },
  "latest_soil_report": {
    "moisture_level": "damp",
    "ts": "2025-10-24T10:00:00Z"
  }
}
```

---

## Complete Workflow Example

Run these commands in sequence to test the full farmer workflow:

```bash
# 1. Submit soil report
curl -X POST http://localhost:8000/api/climate/soil_report ^
  -H "Content-Type: application/json" ^
  -d "{\"farmer_id\":\"demo_farmer\",\"field_id\":\"demo_field\",\"moisture_level\":\"damp\"}"

# 2. Submit rain report
curl -X POST http://localhost:8000/api/climate/rain_report ^
  -H "Content-Type: application/json" ^
  -d "{\"farmer_id\":\"demo_farmer\",\"location\":{\"lat\":-1.2921,\"lon\":36.8219},\"amount\":\"moderate\"}"

# 3. Calculate LCRS
curl -X POST http://localhost:8000/api/climate/lcrs/calculate ^
  -H "Content-Type: application/json" ^
  -d "{\"farmer_id\":\"demo_farmer\",\"field_id\":\"demo_field\",\"location\":{\"lat\":-1.2921,\"lon\":36.8219},\"forecast_months\":3}"

# 4. Check planting status
curl -X POST http://localhost:8000/api/climate/planting/check_status ^
  -H "Content-Type: application/json" ^
  -d "{\"farmer_id\":\"demo_farmer\",\"field_id\":\"demo_field\",\"crop\":\"maize\",\"location\":{\"lat\":-1.2921,\"lon\":36.8219}}"

# 5. Record planting
curl -X POST http://localhost:8000/api/climate/planting/record ^
  -H "Content-Type: application/json" ^
  -d "{\"farmer_id\":\"demo_farmer\",\"field_id\":\"demo_field\",\"crop\":\"maize\",\"planting_date\":\"2025-10-24T00:00:00\",\"variety\":\"short_season\",\"area_hectares\":2.5}"

# 6. Get diversification plan
curl -X POST http://localhost:8000/api/climate/diversification/plan ^
  -H "Content-Type: application/json" ^
  -d "{\"farmer_id\":\"demo_farmer\",\"field_id\":\"demo_field\",\"location\":{\"lat\":-1.2921,\"lon\":36.8219},\"total_area_hectares\":5.0}"

# 7. Generate harvest prediction
curl -X POST http://localhost:8000/api/climate/harvest/predict ^
  -H "Content-Type: application/json" ^
  -d "{\"farmer_id\":\"demo_farmer\",\"field_id\":\"demo_field\",\"planting_date\":\"2025-10-24T00:00:00\",\"crop\":\"maize\",\"variety\":\"short_season\",\"location\":{\"lat\":-1.2921,\"lon\":36.8219},\"language\":\"en\"}"

# 8. Get dashboard
curl "http://localhost:8000/api/climate/dashboard/demo_farmer?field_id=demo_field"
```

---

## Batch Test Script

Save this as `test_climate_api.bat`:

```batch
@echo off
echo ============================================
echo AgroShield Climate Engine API Test
echo ============================================
echo.

SET BASE=http://localhost:8000/api/climate
SET FARMER=demo_farmer
SET FIELD=demo_field
SET LAT=-1.2921
SET LON=36.8219

echo [1/8] Submitting soil report...
curl -X POST %BASE%/soil_report -H "Content-Type: application/json" -d "{\"farmer_id\":\"%FARMER%\",\"field_id\":\"%FIELD%\",\"moisture_level\":\"damp\"}"
echo.
echo.

echo [2/8] Submitting rain report...
curl -X POST %BASE%/rain_report -H "Content-Type: application/json" -d "{\"farmer_id\":\"%FARMER%\",\"location\":{\"lat\":%LAT%,\"lon\":%LON%},\"amount\":\"moderate\"}"
echo.
echo.

echo [3/8] Calculating LCRS...
curl -X POST %BASE%/lcrs/calculate -H "Content-Type: application/json" -d "{\"farmer_id\":\"%FARMER%\",\"field_id\":\"%FIELD%\",\"location\":{\"lat\":%LAT%,\"lon\":%LON%},\"forecast_months\":3}"
echo.
echo.

echo [4/8] Checking planting status...
curl -X POST %BASE%/planting/check_status -H "Content-Type: application/json" -d "{\"farmer_id\":\"%FARMER%\",\"field_id\":\"%FIELD%\",\"crop\":\"maize\",\"location\":{\"lat\":%LAT%,\"lon\":%LON%}}"
echo.
echo.

echo [5/8] Recording planting...
curl -X POST %BASE%/planting/record -H "Content-Type: application/json" -d "{\"farmer_id\":\"%FARMER%\",\"field_id\":\"%FIELD%\",\"crop\":\"maize\",\"planting_date\":\"2025-10-24T00:00:00\",\"variety\":\"short_season\",\"area_hectares\":2.5}"
echo.
echo.

echo [6/8] Getting diversification plan...
curl -X POST %BASE%/diversification/plan -H "Content-Type: application/json" -d "{\"farmer_id\":\"%FARMER%\",\"field_id\":\"%FIELD%\",\"location\":{\"lat\":%LAT%,\"lon\":%LON%},\"total_area_hectares\":5.0}"
echo.
echo.

echo [7/8] Generating harvest prediction...
curl -X POST %BASE%/harvest/predict -H "Content-Type: application/json" -d "{\"farmer_id\":\"%FARMER%\",\"field_id\":\"%FIELD%\",\"planting_date\":\"2025-10-24T00:00:00\",\"crop\":\"maize\",\"variety\":\"short_season\",\"location\":{\"lat\":%LAT%,\"lon\":%LON%},\"language\":\"en\"}"
echo.
echo.

echo [8/8] Getting farmer dashboard...
curl "%BASE%/dashboard/%FARMER%?field_id=%FIELD%"
echo.
echo.

echo ============================================
echo Test complete!
echo ============================================
pause
```

Run with: `test_climate_api.bat`

---

## Notes

- All endpoints return JSON
- Dates should be in ISO 8601 format: `2025-10-24T00:00:00`
- Coordinates are in decimal degrees (lat/lon)
- Replace `localhost:8000` with your backend URL
- For production, use HTTPS
