# Crop Lifecycle Calendar System - Complete Guide

## Overview

The **Crop Lifecycle Calendar System** is an intelligent agricultural planning tool that generates comprehensive farming calendars based on crop growth stages and lifespan. It integrates AI capabilities to optimize scheduling, resource planning, and risk management.

## Key Features

### 1. **Stage-Based Scheduling**
- Automatically generates practices for each growth stage
- From germination to harvest
- Stage-specific monitoring and interventions

### 2. **AI-Powered Optimization**
- Weather-adjusted scheduling
- Optimal timing for fertilizer application
- Harvest window refinement using photo analysis

### 3. **Resource Planning**
- Labor hour estimation
- Cost projections
- Input requirements by stage
- Equipment needs

### 4. **Risk Management**
- Stage-specific risk alerts
- Pest and disease monitoring schedules
- AI detection integration

## Architecture

### Backend Components

**1. Crop Lifecycle Calendar (`crop_lifecycle_calendar.py`)**
```python
from app.services.crop_lifecycle_calendar import get_lifecycle_calendar

calendar = get_lifecycle_calendar()
result = calendar.generate_lifecycle_calendar(
    crop="maize",
    variety="h614",
    planting_date="2024-03-15",
    plot_id="plot_001"
)
```

**2. Growth Models (`growth_model.py`)**
- Defines crop-specific growth stages
- Critical practices per stage
- Water requirements
- Maturity timelines

**3. AI Intelligence (`ai_calendar_intelligence.py`)**
- Weather-based date adjustments
- Fertilizer timing optimization
- Harvest window refinement

### API Endpoints

Base URL: `/api/ai-calendar`

#### Generate Lifecycle Calendar
```
POST /lifecycle/generate
```

**Request:**
```json
{
  "crop": "maize",
  "variety": "h614",
  "planting_date": "2024-03-15T00:00:00Z",
  "plot_id": "plot_001",
  "location": {
    "latitude": -1.286389,
    "longitude": 36.817223
  },
  "soil_type": "clay_loam"
}
```

**Response:**
```json
{
  "success": true,
  "calendar": {
    "plot_id": "plot_001",
    "crop": "maize",
    "variety": "h614",
    "planting_date": "2024-03-15T00:00:00Z",
    "maturity_days": 120,
    "expected_harvest_date": "2024-07-13T00:00:00Z",
    "ai_enabled": true,
    "stages": [
      {
        "stage": "germination",
        "name": "Germination",
        "start_date": "2024-03-15T00:00:00Z",
        "end_date": "2024-03-22T00:00:00Z",
        "duration_days": 7,
        "dap_start": 0,
        "dap_end": 7,
        "practices": [
          {
            "practice": "soil_moisture_check",
            "description": "Check soil moisture daily",
            "frequency": "daily"
          }
        ],
        "monitoring": {
          "parameters": ["soil_temperature", "soil_moisture", "seed_emergence_rate"],
          "frequency": "weekly",
          "ai_analysis": true,
          "ai_features": {
            "plant_health_scoring": true,
            "pest_detection": true,
            "disease_detection": true,
            "growth_rate_analysis": true
          }
        }
      }
    ],
    "practices": [
      {
        "practice_id": "plot_001_first_weeding_20",
        "practice": "first_weeding",
        "description": "First weeding to control early weed competition in maize",
        "scheduled_date": "2024-04-04T00:00:00Z",
        "dap": 20,
        "priority": "high",
        "estimated_hours": 8.0,
        "estimated_cost": 50.0,
        "status": "pending",
        "ai_optimized": true
      }
    ],
    "milestones": [
      {
        "milestone": "planting",
        "name": "Planting Complete",
        "date": "2024-03-15T00:00:00Z",
        "dap": 0,
        "icon": "🌱"
      },
      {
        "milestone": "flowering",
        "name": "First Flowering",
        "date": "2024-05-29T00:00:00Z",
        "dap": 75,
        "icon": "🌸"
      }
    ],
    "resource_plan": {
      "total_labor_hours": 120,
      "total_estimated_cost": 850.0,
      "inputs_needed": ["fertilizer", "pesticides", "storage_materials"],
      "equipment_needed": ["hoe", "sprayer", "harvesting_tools"]
    },
    "risk_calendar": [
      {
        "stage": "vegetative",
        "stage_name": "Vegetative Growth",
        "risk_period_start": "2024-03-29T00:00:00Z",
        "risks": ["armyworm", "stalk_borer", "drought_stress"],
        "monitoring_frequency": "weekly",
        "ai_detection_available": true
      }
    ]
  },
  "ai_features_enabled": true
}
```

#### Get Current Growth Stage
```
GET /lifecycle/{plot_id}/current-stage?planting_date=2024-03-15
```

**Response:**
```json
{
  "success": true,
  "plot_id": "plot_001",
  "days_since_planting": 45,
  "current_stage": {
    "stage_key": "vegetative",
    "name": "Vegetative Growth",
    "dap_range": [14, 55]
  },
  "planting_date": "2024-03-15"
}
```

#### Get Upcoming Practices
```
GET /lifecycle/practices/upcoming?plot_id=plot_001&planting_date=2024-03-15&crop=maize&variety=h614&days_ahead=14
```

**Response:**
```json
{
  "success": true,
  "plot_id": "plot_001",
  "days_ahead": 14,
  "practices_count": 2,
  "practices": [
    {
      "practice_id": "plot_001_second_weeding_40",
      "practice": "second_weeding",
      "description": "Second weeding during critical growth period",
      "scheduled_date": "2024-04-24T00:00:00Z",
      "dap": 40,
      "priority": "medium",
      "estimated_hours": 8.0,
      "estimated_cost": 50.0,
      "days_until": 5,
      "ai_optimized": true
    }
  ],
  "ai_enabled": true
}
```

#### Get Crop Milestones
```
GET /lifecycle/milestones/{plot_id}?crop=maize&variety=h614&planting_date=2024-03-15
```

#### Get Resource Plan
```
GET /lifecycle/resources/{plot_id}?crop=maize&variety=h614&planting_date=2024-03-15
```

#### Get Risk Calendar
```
GET /lifecycle/risks/{plot_id}?crop=maize&variety=h614&planting_date=2024-03-15
```

#### Get AI Features Status
```
GET /features/ai-status
```

**Response:**
```json
{
  "success": true,
  "features": {
    "lifecycle_calendar": true,
    "ai_scheduling": true,
    "weather_optimization": true,
    "pest_detection": true,
    "disease_detection": true,
    "plant_health_monitoring": true,
    "yield_prediction": true
  },
  "summary": {
    "total_features": 7,
    "available_features": 7,
    "percentage_ready": 100.0
  },
  "message": "7/7 AI calendar features available"
}
```

#### Get Supported Crops
```
GET /crops/supported
```

**Response:**
```json
{
  "success": true,
  "crops_count": 3,
  "crops": [
    {
      "crop_id": "maize",
      "crop_name": "Maize",
      "varieties": [
        {
          "variety_id": "h614",
          "name": "H614 (Hybrid)",
          "maturity_days": 120,
          "stages_count": 7
        },
        {
          "variety_id": "short_season",
          "name": "Short Season Variety",
          "maturity_days": 90,
          "stages_count": 7
        }
      ],
      "default_variety": "short_season"
    }
  ]
}
```

## Growth Stages by Crop

### Maize (H614 - 120 days)

| Stage | Days After Planting | Key Practices |
|-------|---------------------|---------------|
| **Germination** | 0-7 | Soil moisture check, bird protection |
| **Emergence** | 7-14 | Emergence count, gap filling |
| **Vegetative** | 14-55 | Weeding (20, 40 DAP), fertilizer (30, 55 DAP) |
| **Tasseling** | 55-65 | Water management, pollination support |
| **Silking** | 60-70 | Critical irrigation, disease monitoring |
| **Grain Fill** | 70-100 | Nutrient boost, bird scaring |
| **Maturity** | 100-120 | Harvest timing, storage preparation |

### Beans (KAT B1 - 75 days)

| Stage | Days After Planting | Key Practices |
|-------|---------------------|---------------|
| **Germination** | 0-5 | Moisture monitoring |
| **Emergence** | 5-10 | Seedling count |
| **Vegetative** | 10-35 | Weeding (14, 30 DAP), fertilizer (14 DAP) |
| **Flowering** | 35-50 | Pollination, irrigation |
| **Pod Formation** | 45-60 | Pest control |
| **Pod Filling** | 55-70 | Water management |
| **Maturity** | 70-75 | Harvest timing |

### Potatoes (Shangi - 90 days)

| Stage | Days After Planting | Key Practices |
|-------|---------------------|---------------|
| **Sprouting** | 0-14 | Soil preparation |
| **Emergence** | 14-21 | Plant count |
| **Vegetative** | 21-45 | Weeding (25, 45 DAP), fertilizer (21, 42 DAP) |
| **Tuber Initiation** | 35-50 | Earthing up (30, 50 DAP) |
| **Tuber Bulking** | 50-80 | Blight monitoring, irrigation |
| **Maturity** | 80-90 | Harvest preparation |

## AI Features

### 1. AI Scheduling
Uses `ai_calendar` model to predict optimal practice timing based on:
- Current growth stage
- Weather conditions
- Soil type
- Historical data

### 2. Weather Optimization
Adjusts practice dates using `ai_calendar_intelligence.adjust_practice_date_with_weather()`:
- Avoids rainy days for fertilizer application
- Optimizes irrigation scheduling
- Adjusts for temperature extremes

### 3. Pest & Disease Detection
Integrates with:
- `pest_detection` model
- `disease_detection` model
- Provides early warning in risk calendar

### 4. Plant Health Monitoring
Uses `plant_health` model to:
- Score overall plant health (0-100)
- Track growth rate vs expected
- Alert on stress indicators

### 5. Yield Prediction
Uses `yield_prediction` model to:
- Forecast harvest quantity
- Refine harvest window
- Optimize market timing

## Stage-Specific Practices

### Germination Stage
**Duration:** 5-8 days
**Critical Factors:** Soil temperature, moisture, oxygen
**Practices:**
- Daily soil moisture check
- Bird protection measures
- Temperature monitoring

**Monitoring Parameters:**
- Soil temperature (15-30°C optimal)
- Soil moisture (field capacity)
- Seed emergence rate (target >90%)

### Vegetative Stage
**Duration:** Varies by crop (14-70 days)
**Critical Factors:** Nutrients, water, weed competition
**Practices:**
- First weeding (14-25 DAP)
- Second weeding (30-50 DAP)
- Fertilizer application (20-55 DAP)
- Pest scouting (weekly)

**Monitoring Parameters:**
- Plant height
- Leaf count and color
- Stem diameter
- Pest incidence

### Flowering/Reproductive Stage
**Duration:** 15-40 days
**Critical Factors:** Pollination, water stress, diseases
**Practices:**
- Critical irrigation period
- Pollination support
- Disease monitoring (twice weekly)

**Monitoring Parameters:**
- Flower count
- Pollination success rate
- Water stress signs
- Disease symptoms

### Maturity/Harvest Stage
**Duration:** 10-30 days
**Critical Factors:** Harvest timing, quality, storage
**Practices:**
- Maturity monitoring (daily)
- Harvest preparation
- Storage arrangement

**Monitoring Parameters:**
- Grain moisture content
- Color changes
- Lodging percentage

## Resource Planning

### Labor Requirements by Stage
- **Germination:** 2 hours/acre
- **Vegetative:** 15 hours/acre (weeding, fertilizer)
- **Flowering:** 5 hours/acre (monitoring)
- **Maturity:** 25 hours/acre (harvesting)

### Input Requirements
- **Fertilizers:** Base (planting) + Top-dress (2-3 applications)
- **Pesticides:** As needed based on scouting
- **Storage Materials:** Bags, moisture meters, storage chemicals

### Equipment Needed
- **Planting:** Planter or hoe
- **Weeding:** Hoe
- **Fertilizer Application:** Spreader
- **Pest Control:** Sprayer
- **Harvesting:** Sickle, combine (large scale)

## Risk Management

### Pest Risks by Stage
**Maize:**
- Germination: Seed rot, birds
- Vegetative: Armyworm, stalk borer
- Flowering: Aphids
- Grain fill: Storage pests

**Beans:**
- Vegetative: Aphids, leaf miners
- Flowering: Thrips
- Pod formation: Pod borers

**Potatoes:**
- Vegetative: Aphids, cutworms
- Tuber initiation: Early blight
- Tuber bulking: Late blight, tuber moth

### Disease Risks
**Common Diseases by Crop:**
- Maize: Gray leaf spot, rust, stalk rot
- Beans: Anthracnose, common blight
- Potatoes: Late blight, early blight, bacterial wilt

### Monitoring Frequency
- **High Risk Stages:** Daily or twice weekly
- **Medium Risk:** Weekly
- **Low Risk:** Bi-weekly

**AI Detection:** Available for all stages when models are trained

## Frontend Integration

### Example: React Native Component

```javascript
import { useState, useEffect } from 'react';
import axios from 'axios';

function CropCalendarScreen({ plotId, crop, variety, plantingDate }) {
  const [calendar, setCalendar] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    loadCalendar();
  }, []);
  
  const loadCalendar = async () => {
    try {
      const response = await axios.post(
        `${API_URL}/ai-calendar/lifecycle/generate`,
        {
          crop,
          variety,
          planting_date: plantingDate,
          plot_id: plotId
        }
      );
      
      setCalendar(response.data.calendar);
    } catch (error) {
      console.error('Error loading calendar:', error);
    } finally {
      setLoading(false);
    }
  };
  
  if (loading) return <LoadingSpinner />;
  
  return (
    <ScrollView>
      {/* Current Stage */}
      <StageCard stage={getCurrentStage(calendar)} />
      
      {/* Upcoming Practices */}
      <UpcomingPractices practices={getUpcomingPractices(calendar)} />
      
      {/* Milestones Timeline */}
      <MilestonesTimeline milestones={calendar.milestones} />
      
      {/* Resource Plan */}
      <ResourcePlan resources={calendar.resource_plan} />
      
      {/* Risk Alerts */}
      <RiskAlerts risks={calendar.risk_calendar} />
    </ScrollView>
  );
}
```

## Testing

### Backend Test
```bash
# Start backend
python backend/run_dev.py

# Generate calendar
curl -X POST http://localhost:8000/api/ai-calendar/lifecycle/generate \
  -H "Content-Type: application/json" \
  -d '{
    "crop": "maize",
    "variety": "h614",
    "planting_date": "2024-03-15T00:00:00Z",
    "plot_id": "test_plot_001"
  }'

# Get AI features status
curl http://localhost:8000/api/ai-calendar/features/ai-status

# Get supported crops
curl http://localhost:8000/api/ai-calendar/crops/supported
```

## Best Practices

### 1. Calendar Generation
- Generate calendar immediately after planting
- Include location data for AI optimization
- Update if planting date changes

### 2. Practice Execution
- Mark practices as complete when done
- Update if dates need adjustment
- Document why practices were skipped

### 3. Monitoring
- Follow stage-specific monitoring frequency
- Use AI tools for photo analysis
- Document observations

### 4. Resource Planning
- Review resource plan at season start
- Procure inputs in advance
- Schedule labor early

## Troubleshooting

**Q: Calendar shows incorrect dates**
A: Verify planting date format (ISO 8601)

**Q: AI features not working**
A: Check `/features/ai-status` endpoint to see which models are available

**Q: Crop not supported**
A: Use `/crops/supported` to see available crops and varieties

**Q: Practices not showing**
A: Ensure crop variety is correctly specified

## Next Steps

1. **Train AI Models** - Enable all AI features
2. **Add Location Data** - Improve weather optimization
3. **Track Progress** - Mark practices as complete
4. **Monitor Growth** - Upload photos for AI analysis
5. **Adjust Schedule** - Update based on actual conditions

---

**The Crop Lifecycle Calendar transforms farming from reactive to proactive management!** 🌾
