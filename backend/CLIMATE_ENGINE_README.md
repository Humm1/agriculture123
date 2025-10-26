# 🌍 Climate Engine Documentation

## Overview

The **Climate Engine** is AgroShield's core decision-making system that fuses hyper-local data to provide farmers with:

- **Localized Climate Risk Scores (LCRS)** - 3-month climate forecasts
- **Optimal Planting Windows** - When to plant based on season and risk
- **Late Planting Alerts** - Alternative crop suggestions when late
- **Crop Diversification Plans** - Risk-hedging strategies
- **Harvest Predictions** - When to harvest with weather forecasts
- **Storage Readiness Checks** - Link harvest to storage conditions

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIMATE ENGINE CORE                      │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌────────────────┐    ┌──────────────┐
│  LCRS ENGINE  │    │ PLANTING       │    │   HARVEST    │
│               │───▶│ WINDOW CALC    │───▶│  PREDICTION  │
│  - Weather    │    │                │    │              │
│  - Soil       │    │ - Optimal      │    │ - Weather    │
│  - Crowdsource│    │ - Late alerts  │    │ - Storage    │
└───────────────┘    │ - Alternatives │    │   check      │
                     └────────────────┘    └──────────────┘
```

### Data Sources

1. **Crowdsourced Rain Reports** - Farmers report rainfall in their area
2. **Soil Moisture Reports** - Farmers report soil condition (dry/damp/saturated)
3. **Seasonal Weather Patterns** - Historical rainfall patterns (in production: national met service API)
4. **BLE Storage Sensors** - Temperature & humidity from storage facilities
5. **Planting Records** - Track what farmers plant and when

---

## API Endpoints

### 1. Crowdsourced Data Collection

#### POST `/api/climate/rain_report`
Submit rainfall observation from the field.

**Request:**
```json
{
  "farmer_id": "farmer_001",
  "location": {"lat": -1.2921, "lon": 36.8219},
  "amount": "moderate"
}
```

**Amount values:** `none`, `light`, `moderate`, `heavy`

**Response:**
```json
{
  "submitted": true,
  "message": "Thank you for reporting rainfall!"
}
```

---

#### POST `/api/climate/soil_report`
Submit soil moisture observation.

**Request:**
```json
{
  "farmer_id": "farmer_001",
  "field_id": "field_001",
  "moisture_level": "damp"
}
```

**Moisture levels:** `dry`, `damp`, `saturated`

**Response:**
```json
{
  "submitted": true,
  "soil_moisture_index": 60,
  "message": "Soil condition recorded: damp (SMI: 60%)"
}
```

---

### 2. LCRS (Localized Climate Risk Score)

#### POST `/api/climate/lcrs/calculate`
Calculate climate risk score for the next 3 months.

**Request:**
```json
{
  "farmer_id": "farmer_001",
  "field_id": "field_001",
  "location": {"lat": -1.2921, "lon": 36.8219},
  "forecast_months": 3
}
```

**Response:**
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

**Risk Levels:**
- **0-30**: Low risk (favorable conditions)
- **31-60**: Moderate risk (normal variability)
- **61-100**: High risk (drought/flood likely)

---

### 3. Planting Window & Alerts

#### GET `/api/climate/planting_window/{crop}`
Get optimal planting window for a crop.

**Query params:** `lat`, `lon` (optional)

**Response:**
```json
{
  "start_date": "2025-10-01T00:00:00",
  "end_date": "2025-10-31T00:00:00",
  "rationale": "Optimal for short_rains season based on historical rainfall patterns",
  "confidence": 0.8
}
```

---

#### POST `/api/climate/planting/check_status`
Check if farmer is on time, early, or late for planting.

**Request:**
```json
{
  "farmer_id": "farmer_001",
  "field_id": "field_001",
  "crop": "maize",
  "location": {"lat": -1.2921, "lon": 36.8219}
}
```

**Response (On Time):**
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

---

#### POST `/api/climate/planting/record`
Record when farmer plants a crop.

**Request:**
```json
{
  "farmer_id": "farmer_001",
  "field_id": "field_001",
  "crop": "maize",
  "planting_date": "2025-10-24T00:00:00",
  "variety": "short_season",
  "area_hectares": 2.5
}
```

---

### 4. Crop Diversification

#### POST `/api/climate/diversification/plan`
Generate crop diversification plan based on climate risk.

**Request:**
```json
{
  "farmer_id": "farmer_001",
  "field_id": "field_001",
  "location": {"lat": -1.2921, "lon": 36.8219},
  "total_area_hectares": 5.0
}
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

### 5. Harvest Prediction & Alerts

#### POST `/api/climate/harvest/predict`
Generate harvest prediction with weather forecast and storage check.

**Request:**
```json
{
  "farmer_id": "farmer_001",
  "field_id": "field_001",
  "planting_date": "2025-10-24T00:00:00",
  "crop": "maize",
  "variety": "short_season",
  "location": {"lat": -1.2921, "lon": 36.8219},
  "sensor_id": "ble_sensor_001",
  "language": "en"
}
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

---

#### GET `/api/climate/harvest/calendar/{farmer_id}`
Get harvest calendar showing all upcoming harvests.

**Response:**
```json
{
  "count": 2,
  "calendar": [
    {
      "field_id": "field_001",
      "crop": "maize",
      "variety": "short_season",
      "planting_date": "2025-10-24T00:00:00",
      "harvest_date": "2026-01-22T00:00:00",
      "harvest_window": {
        "start": "2026-01-15T00:00:00",
        "end": "2026-01-29T00:00:00"
      },
      "maturity_days": 90
    },
    {
      "field_id": "field_002",
      "crop": "beans",
      "variety": "bush",
      "planting_date": "2025-11-01T00:00:00",
      "harvest_date": "2025-12-31T00:00:00",
      "harvest_window": {
        "start": "2025-12-24T00:00:00",
        "end": "2026-01-07T00:00:00"
      },
      "maturity_days": 60
    }
  ]
}
```

---

### 6. Farmer Dashboard

#### GET `/api/climate/dashboard/{farmer_id}`
Get comprehensive farmer dashboard with all climate data.

**Query params:** `field_id` (optional)

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
    "plantings": [...]
  },
  "upcoming_harvests": {
    "count": 2,
    "predictions": [...]
  },
  "latest_soil_report": {
    "moisture_level": "damp",
    "ts": "2025-10-24T10:00:00Z"
  }
}
```

---

## Key Features

### 🌦️ Hyper-Local Data Fusion

Combines multiple data sources:
- **Official meteorological data** (seasonal patterns)
- **Crowdsourced rain reports** (real-time local observations)
- **Soil Moisture Index** (farmer ground-truth)
- **Historical climate patterns**

### 📅 Optimal Planting Windows

Calculates ideal planting dates based on:
- Crop requirements
- Seasonal rainfall patterns
- Current soil conditions
- Climate risk level

### ⏰ Late Planting Alerts

Provides actionable advice when farmer is late:
- "You are 15 days late - switch to fast-maturing beans"
- Suggests alternative crops (cassava, sorghum for very late)
- Recommends drought-resistant varieties

### 🌾 Crop Diversification

Risk-hedging strategies based on LCRS:
- **Low risk**: 90% primary crop, 10% diversification
- **Moderate risk**: 70% primary, 20% drought-tolerant, 10% quick-maturing
- **High risk**: 50% primary, 30% cassava, 20% sorghum

### 🌾 Harvest Prediction

Links production to preservation:
- Predicts harvest date based on planting + maturity period
- Checks weather forecast for harvest window
- **Automatically checks storage readiness via BLE sensors**
- Provides action items (prepare drying area, fix storage, etc.)

---

## Farmer Workflow

```
1. 📍 LOCATION & SETUP
   └─ Farmer registers location and fields

2. 🌧️ CROWDSOURCE DATA
   ├─ Report rain: "Moderate rain today"
   └─ Report soil: "My soil feels damp"

3. 📊 CALCULATE LCRS
   └─ Get 3-month climate risk score: 27.1 (low risk)

4. 🌱 CHECK PLANTING WINDOW
   ├─ "✅ IDEAL TIME: Plant maize now!"
   └─ OR "⚠️ LATE: Switch to beans or cassava"

5. 📝 RECORD PLANTING
   └─ "Planted 2.5 hectares of short-season maize on Oct 24"

6. 🌾 GET DIVERSIFICATION PLAN
   └─ "Plant 90% maize, 10% beans (low risk year)"

7. 📅 HARVEST PREDICTION
   ├─ "Harvest ready in 90 days (Jan 22)"
   ├─ Weather: "☀️ Dry spell - good for sun drying"
   └─ Storage: "✅ READY: 22°C, 65% humidity"

8. 🏠 STORAGE CHECK
   └─ BLE sensor automatically checks storage before harvest
```

---

## Testing

Run comprehensive tests:

```bash
python backend/tests/test_climate_engine.py
```

**Test Coverage:**
- ✅ LCRS calculation
- ✅ Soil moisture indexing
- ✅ Planting window detection
- ✅ Late planting alerts
- ✅ Alternative crop suggestions
- ✅ Diversification plans
- ✅ Harvest date prediction
- ✅ Weather forecast checking
- ✅ Storage readiness validation
- ✅ Full farmer workflow integration

---

## Data Storage

All climate data persisted in `backend/app/data/`:

```
├── rain_reports.json          # Crowdsourced rainfall
├── soil_reports.json           # Farmer soil observations
├── lcrs_scores.json            # Calculated risk scores
├── planting_records.json       # When farmers plant
└── harvest_predictions.json    # Predicted harvest dates
```

---

## Future Enhancements

- [ ] Integrate with national meteorological service APIs
- [ ] Add satellite soil moisture data (Sentinel, SMAP)
- [ ] Weather station network integration
- [ ] Machine learning for yield prediction
- [ ] Pest outbreak prediction based on weather
- [ ] Market price forecasting linked to harvest
- [ ] Community weather alerts (SMS broadcast)
- [ ] Crop insurance integration

---

## Configuration

No special configuration needed! The system works out-of-the-box with sensible defaults for East Africa.

For other regions:
- Update seasonal patterns in `lcrs_engine.py`
- Adjust crop maturity periods in `harvest_prediction.py`
- Customize planting windows in `planting_window.py`

---

## Support

See also:
- `SYSTEM_FLOW_DIAGRAM.md` - Visual diagrams
- `MOBILE_INTEGRATION_GUIDE.md` - Mobile app integration
- `BLE_STORAGE_README.md` - BLE sensor setup

---

**🌍 Climate Engine - Empowering farmers with data-driven decisions! 🌾**
