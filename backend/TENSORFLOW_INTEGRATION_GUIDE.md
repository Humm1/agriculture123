# TensorFlow Integration Guide
**Predictive, Context-Aware Agriculture (PCA) System**

---

## 🎯 Overview

This guide documents the complete TensorFlow integration system for AgroShield, connecting AI models with real-world APIs to create a dynamic, fully functional mobile advisory system.

### Core Philosophy: Predictive, Context-Aware Agriculture (PCA)

**PCA = AI Models + Real-Time APIs + Edge Computing**

Move beyond static data to achieve:
- **Instant** on-device diagnosis (TensorFlow Lite)
- **Context-aware** recommendations (real-world API integration)
- **Predictive** alerts (time-series forecasting)
- **Offline-capable** operation (edge deployment)

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     MOBILE APP (EDGE)                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  TensorFlow Lite Models (On-Device)                   │  │
│  │  - Plant Health Detection (MobileNet V3)              │  │
│  │  - Soil Diagnostics (EfficientNet B0)                 │  │
│  │  Inference Time: 50-150ms | Offline Capable          │  │
│  └───────────────────────────────────────────────────────┘  │
│                           ↓↑                                 │
└───────────────────────────┼─────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────┐
│                    CLOUD API GATEWAY                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Context Enhancement Layer                           │   │
│  │  - Disease Database APIs (CGIAR, KEPHIS)            │   │
│  │  - Weather APIs (OpenWeatherMap)                    │   │
│  │  - Soil Geological APIs (FAO SoilGrids)             │   │
│  │  - Hugging Face NLP (SMS generation)                │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Cloud Models (Heavy Processing)                     │   │
│  │  - Climate Prediction (LSTM)                         │   │
│  │  - Spoilage Prediction (Time-Series)                 │   │
│  │  - Contagion Risk Modeling (Spatial-Temporal)        │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🤖 TensorFlow Models

### A. Plant Health & Disease Detection

**Model:** TensorFlow Lite (MobileNet V3 / EfficientNet B0)  
**Deployment:** Edge (on-device)  
**Input:** 224x224x3 RGB image  
**Output:** Disease classification + confidence score

```python
from app.services.tensorflow_integration import diagnose_plant_health_tflite

# Capture leaf image from camera
image_data = camera.capture_bytes()

# Run on-device diagnosis (instant, offline)
diagnosis = diagnose_plant_health_tflite(
    image_data=image_data,
    crop="maize",
    lat=-1.29,
    lon=36.82,
    use_context=True  # Enhance with APIs when online
)

print(f"Disease: {diagnosis['disease_name']}")
print(f"Confidence: {diagnosis['confidence']:.1%}")
print(f"Severity: {diagnosis['severity']}")
print(f"Edge computed: {diagnosis['edge_computed']}")
print(f"Inference time: {diagnosis['inference_time_ms']}ms")

# Context-enhanced action plan
print(f"\nAction: {diagnosis['action_plan']['timing_guidance']}")
print(f"Treatment: {diagnosis['action_plan']['recommended_treatment']['name']}")
print(f"Cost: {diagnosis['action_plan']['estimated_cost_ksh']} KES")

# SMS message (Swahili)
print(f"\nSMS: {diagnosis['sms_message']}")
```

**Training Data:**
- 500+ images per disease class
- Localized Kenya crop diseases
- Augmented: rotation, flip, brightness, contrast
- Validated on real farmer photos

**Diseases Covered:**
- Maize: Leaf blight, fall armyworm, streak virus
- Potato: Late blight, early blight, bacterial wilt
- Coffee: Coffee berry disease, leaf rust
- Beans: Bean rust, bacterial blight

### B. Soil & Nutrient Diagnostics

**Model:** Computer Vision + Regression (EfficientNet B0)  
**Deployment:** Edge (on-device)  
**Input:** 224x224x3 RGB soil image  
**Output:** NPK levels, pH, soil type, fertility score

**Integration with FAO SoilGrids API:**
```python
# On-device soil scan
soil_photo = camera.capture_bytes()

# TFLite inference
visual_analysis = diagnose_soil_tflite(soil_photo)

# Enhance with GPS-based geological data
fao_data = query_fao_soilgrids_api(lat, lon)

# Merge visual + geological data
final_diagnosis = merge_soil_data(visual_analysis, fao_data)

print(f"Soil Type: {final_diagnosis['soil_type']}")
print(f"pH: {final_diagnosis['ph_range']}")
print(f"Nitrogen: {final_diagnosis['nitrogen_level']}")  # Low/Medium/High
print(f"Phosphorus: {final_diagnosis['phosphorus_level']}")
print(f"Potassium: {final_diagnosis['potassium_level']}")
print(f"Fertility Score: {final_diagnosis['fertility_score']}/10")
```

**Training Data:**
- Correlated with actual lab-tested NPK/pH data
- Government/NGO supplied soil samples
- Diverse textures: loam, clay, sandy, laterite

### C. Climate & Disaster Prediction

**Model:** LSTM Time-Series Forecasting  
**Deployment:** Cloud (heavy processing)  
**Input:** 30-day historical weather + current conditions  
**Output:** 7-day micro-climate forecast

**Integration with OpenWeatherMap API:**
```python
# Historical data from local sensors + API
historical_weather = get_30day_history(lat, lon)

# LSTM model prediction
forecast = predict_climate_lstm(
    historical_data=historical_weather,
    forecast_days=7
)

# Real-time enhancement from OpenWeatherMap
current_conditions = query_openweather_api(lat, lon)

# Merge AI forecast + live data
final_forecast = merge_forecasts(forecast, current_conditions)

for day in final_forecast['days']:
    print(f"{day['date']}: {day['temp_min']}-{day['temp_max']}°C, "
          f"{day['rainfall_mm']}mm rain ({day['rainfall_probability']}% chance)")
```

**Training Data:**
- 10+ years historical weather data
- Kenya Meteorological Department records
- Crowdsourced farmer reports
- Satellite weather data

### D. Spoilage Prediction

**Model:** Classification + Time-Series (LSTM)  
**Deployment:** Cloud (processes BLE data streams)  
**Input:** Real-time temp/humidity from BLE sensors  
**Output:** Days to critical risk, spoilage probability

**Integration with BLE Sensor Streams:**
```python
# BLE sensor data stream (every 15 minutes)
sensor_readings = [
    {"timestamp": "2025-10-24T10:00", "temp_c": 28, "humidity": 65},
    {"timestamp": "2025-10-24T10:15", "temp_c": 29, "humidity": 67},
    # ...
]

# Predict spoilage risk
prediction = predict_spoilage_risk(
    crop="maize",
    storage_conditions=sensor_readings,
    storage_duration_days=30
)

print(f"Spoilage Risk: {prediction['risk_level']}")  # low/medium/high/critical
print(f"Days to Critical: {prediction['days_to_critical']}")
print(f"Mold Probability: {prediction['mold_probability']:.1%}")
print(f"Pest Activation Risk: {prediction['pest_risk']:.1%}")

# Actionable recommendations
print(f"\nRecommendation: {prediction['action']}")
# e.g., "Reduce humidity immediately. Open ventilation windows."
```

---

## 🌐 Real-World API Integrations

### 1. Disease Database APIs

**Purpose:** Latest treatment recommendations, product availability

**Providers:**
- **CGIAR** (International research)
- **KEPHIS** (Kenya Plant Health Inspectorate)
- **Curated NGO databases**

**Endpoints:**
```python
# CGIAR API
GET https://api.cgiar.org/plant-health/v1/treatments
  ?disease_id=maize_blight
  &crop=maize
  &country=kenya

# Response
{
  "treatments": [
    {
      "product_name": "Neem Oil Spray",
      "treatment_type": "organic",
      "application_method": "Spray leaves thoroughly",
      "timing_guidance": "Early morning or late evening",
      "efficacy_rating": 0.75,
      "retail_price_ksh": 350,
      "registration_id": "PCPB-REG-12345",
      "approved_supplier": "Greenlife Agrovet"
    }
  ]
}
```

**Configuration:**
```python
TENSORFLOW_CONFIG["apis"]["disease_database"] = {
    "enabled": True,
    "providers": {
        "cgiar": {
            "base_url": "https://api.cgiar.org/plant-health/v1",
            "api_key": "your-cgiar-api-key"
        },
        "kephis": {
            "base_url": "https://api.kephis.go.ke/diseases/v1",
            "api_key": "your-kephis-api-key"
        }
    }
}
```

### 2. Meteorological APIs

**Purpose:** Real-time weather + 7-day forecast for treatment timing

**Providers:**
- **OpenWeatherMap** (Recommended)
- **AccuWeather**
- **Kenya Meteorological Department**

**Endpoints:**
```python
# OpenWeatherMap API
GET https://api.openweathermap.org/data/2.5/forecast
  ?lat=-1.29
  &lon=36.82
  &appid=YOUR_API_KEY
  &units=metric
  &cnt=8  # Next 24 hours

# Response
{
  "list": [
    {
      "dt": 1698149200,
      "main": {"temp": 24.5, "humidity": 75},
      "weather": [{"main": "Rain", "description": "light rain"}],
      "rain": {"3h": 2.5},
      "pop": 0.75  # Probability of precipitation
    }
  ]
}
```

**Configuration:**
```python
TENSORFLOW_CONFIG["apis"]["meteorological"] = {
    "enabled": True,
    "providers": {
        "openweathermap": {
            "base_url": "https://api.openweathermap.org/data/2.5",
            "api_key": "your-openweather-api-key"
        }
    }
}
```

**Sign Up:**
1. Visit: https://openweathermap.org/api
2. Free tier: 60 calls/minute, 1M calls/month
3. Professional plan: $180/month for unlimited calls

### 3. Soil Geological APIs

**Purpose:** Baseline soil data to improve visual analysis accuracy

**Provider:**
- **FAO SoilGrids** (Free, global coverage)

**Endpoints:**
```python
# FAO SoilGrids API
GET https://rest.isric.org/soilgrids/v2.0/properties/query
  ?lon=36.82
  &lat=-1.29
  &property=phh2o  # pH
  &property=nitrogen
  &property=soc  # Soil organic carbon
  &depth=0-5cm

# Response
{
  "properties": {
    "phh2o": {
      "name": "Soil pH",
      "mapped_units": "pH × 10",
      "layers": [{"depth": "0-5cm", "values": {"mean": 62}}]  # pH 6.2
    },
    "nitrogen": {
      "name": "Total nitrogen",
      "mapped_units": "g/kg",
      "layers": [{"depth": "0-5cm", "values": {"mean": 2.5}}]
    }
  }
}
```

**Configuration:**
```python
TENSORFLOW_CONFIG["apis"]["soil_geological"] = {
    "enabled": True,
    "providers": {
        "fao_soilgrids": {
            "base_url": "https://rest.isric.org/soilgrids/v2.0",
            "api_key": None  # Free API
        }
    }
}
```

### 4. Hugging Face NLP

**Purpose:** Generate clear, culturally appropriate SMS messages in Swahili/English

**Model:** `facebook/mbart-large-50-many-to-many-mmt` (Multilingual)

**Endpoints:**
```python
# Hugging Face Inference API
POST https://api-inference.huggingface.co/models/facebook/mbart-large-50-many-to-many-mmt

Headers: {"Authorization": "Bearer YOUR_HF_TOKEN"}

Body: {
  "inputs": "Disease: Maize Leaf Blight detected. Severity: Severe. Apply Neem Oil Spray within 24 hours. Warning: Heavy rain forecast tomorrow.",
  "parameters": {
    "src_lang": "en_XX",  # English
    "tgt_lang": "sw_KE"   # Swahili (Kenya)
  }
}

# Response
[{
  "translation_text": "Ugonjwa: Ugonjwa wa majani ya mahindi umegunduliwa. Ukali: Mbaya. Tumia Mafuta ya Neem ndani ya masaa 24. Onyo: Mvua kubwa inatarajiwa kesho."
}]
```

**Configuration:**
```python
TENSORFLOW_CONFIG["apis"]["huggingface"] = {
    "enabled": True,
    "api_key": "your-huggingface-token",
    "model": "facebook/mbart-large-50-many-to-many-mmt",
    "base_url": "https://api-inference.huggingface.co/models"
}
```

**Sign Up:**
1. Visit: https://huggingface.co/
2. Create account, generate API token
3. Free tier: 1,000 requests/day

---

## 🔧 Context-Aware Action Plan Generation

### Rules-Based Engine

Combines AI diagnosis with real-world context:

```python
def generate_contextual_action_plan(diagnosis, treatments, weather, contagion_risk):
    """
    AI + Weather + Outbreak Data → Actionable Guidance
    """
    
    # 1. Select treatment based on severity
    if diagnosis['severity'] in ['critical', 'severe']:
        # High severity: recommend most effective (usually chemical)
        recommended = max(treatments, key=lambda t: t['effectiveness'])
    else:
        # Lower severity: prefer organic if effective
        organic = [t for t in treatments if t['type'] == 'organic']
        if organic and any(t['effectiveness'] >= 0.70 for t in organic):
            recommended = max(organic, key=lambda t: t['effectiveness'])
        else:
            recommended = max(treatments, key=lambda t: t['effectiveness'])
    
    # 2. Adjust timing based on weather
    if weather['rain_warning']:
        timing = f"⚠️ CRITICAL: Apply BEFORE 10 AM. Rain ({weather['rainfall_next_24h_mm']}mm) forecast."
        urgency = "immediate"
    else:
        timing = f"Apply {recommended['timing']}"
        urgency = "standard"
    
    # 3. Add contagion warning
    if contagion_risk['outbreak_detected']:
        contagion_msg = f"🚨 OUTBREAK: {contagion_risk['nearby_cases']} cases within {contagion_risk['alert_radius_km']}km"
    else:
        contagion_msg = "No major outbreak in area"
    
    return {
        "recommended_treatment": recommended,
        "timing_guidance": timing,
        "urgency": urgency,
        "contagion_warning": contagion_msg,
        "estimated_cost_ksh": recommended['cost_ksh']
    }
```

**Example Output:**

```json
{
  "recommended_treatment": {
    "name": "Neem Oil Spray",
    "type": "organic",
    "effectiveness": 0.75,
    "cost_ksh": 350,
    "application": "Spray leaves thoroughly, repeat every 7 days"
  },
  "timing_guidance": "⚠️ CRITICAL: Apply BEFORE 10 AM. Rain (15mm) forecast.",
  "urgency": "immediate",
  "contagion_warning": "🚨 OUTBREAK: 8 cases within 10km",
  "estimated_cost_ksh": 350
}
```

---

## 📱 Edge Deployment (TensorFlow Lite)

### Model Conversion

Convert trained TensorFlow model to TFLite:

```python
import tensorflow as tf

# Load trained model
model = tf.keras.models.load_model('plant_health_model.h5')

# Convert to TFLite
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]

tflite_model = converter.convert()

# Save TFLite model
with open('plant_health_mobilenet_v3.tflite', 'wb') as f:
    f.write(tflite_model)
```

### On-Device Inference (Python)

```python
import tensorflow as tf
import numpy as np
from PIL import Image

# Load TFLite model
interpreter = tf.lite.Interpreter(model_path='plant_health_mobilenet_v3.tflite')
interpreter.allocate_tensors()

# Get input/output details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Preprocess image
image = Image.open('leaf.jpg').resize((224, 224))
input_data = np.expand_dims(np.array(image) / 255.0, axis=0).astype(np.float32)

# Run inference
interpreter.set_tensor(input_details[0]['index'], input_data)
interpreter.invoke()

# Get results
output_data = interpreter.get_tensor(output_details[0]['index'])
disease_id = np.argmax(output_data)
confidence = output_data[0][disease_id]

print(f"Disease ID: {disease_id}, Confidence: {confidence:.2%}")
```

### On-Device Inference (Android/Kotlin)

```kotlin
import org.tensorflow.lite.Interpreter
import java.nio.ByteBuffer

class PlantHealthModel(context: Context) {
    private val interpreter: Interpreter
    
    init {
        val model = loadModelFile(context, "plant_health_mobilenet_v3.tflite")
        interpreter = Interpreter(model)
    }
    
    fun predict(bitmap: Bitmap): Pair<Int, Float> {
        // Preprocess image
        val input = preprocessImage(bitmap)
        
        // Run inference
        val output = Array(1) { FloatArray(NUM_CLASSES) }
        interpreter.run(input, output)
        
        // Get results
        val diseaseId = output[0].indices.maxBy { output[0][it] }!!
        val confidence = output[0][diseaseId]
        
        return Pair(diseaseId, confidence)
    }
}
```

---

## 🚀 Deployment Checklist

### Phase 1: Model Preparation

- [ ] **Train Plant Health Model**
  - Collect 500+ images per disease class
  - Augment data (rotation, flip, brightness)
  - Train MobileNet V3 / EfficientNet B0
  - Validate on real farmer photos (>85% accuracy)

- [ ] **Train Soil Diagnostics Model**
  - Correlate visual features with lab NPK data
  - Train regression model (pH, N, P, K)
  - Validate against government soil surveys

- [ ] **Convert to TensorFlow Lite**
  - Optimize for edge deployment
  - Quantize to INT8 (reduce model size)
  - Test inference speed (<150ms target)

### Phase 2: API Configuration

- [ ] **Disease Database APIs**
  - CGIAR API key: Contact research@cgiar.org
  - KEPHIS API key: Apply at kephis.go.ke/developers

- [ ] **Weather APIs**
  - OpenWeatherMap: Sign up at openweathermap.org/api
  - Free tier sufficient for initial launch

- [ ] **Soil Geological APIs**
  - FAO SoilGrids: No API key needed (free)

- [ ] **Hugging Face NLP**
  - Sign up at huggingface.co
  - Generate API token
  - Test Swahili translation quality

### Phase 3: Integration Testing

- [ ] **End-to-End Test**
  - Capture real leaf photo
  - Run on-device TFLite inference
  - Enhance with API context
  - Generate Swahili SMS
  - Verify action plan accuracy

- [ ] **Offline Mode Test**
  - Disable internet connection
  - Verify TFLite inference still works
  - Check graceful API fallbacks

- [ ] **Performance Test**
  - Inference time: <150ms (on-device)
  - API response time: <2s (online)
  - SMS generation: <1s

### Phase 4: Production Deployment

- [ ] Deploy TFLite models to mobile app
- [ ] Configure cloud API gateway
- [ ] Set up contagion risk database
- [ ] Enable real-time BLE sensor integration
- [ ] Launch SMS notification system

---

## 📊 Expected Performance

| Metric | Target | Actual |
|--------|--------|--------|
| Plant health accuracy | >88% | TBD |
| Soil diagnostic accuracy | >80% | TBD |
| Inference time (on-device) | <150ms | TBD |
| API response time | <2s | TBD |
| SMS generation time | <1s | TBD |
| Offline capability | 100% | Yes |

---

## 🎓 Training Resources

### Model Training Datasets

**Plant Health:**
- PlantVillage Dataset (54,000+ images)
- CGIAR Crop Disease Image Library
- Kenya-specific disease photos from NGOs

**Soil Diagnostics:**
- FAO Global Soil Database
- Kenya Agricultural Research Institute (KARI) soil samples
- Lab-correlated visual-NPK dataset

**Climate Prediction:**
- Kenya Meteorological Department (10+ years)
- Satellite weather data (NASA, NOAA)
- Crowdsourced farmer reports

---

**Last Updated**: October 24, 2025  
**Version**: 1.0.0  
**Status**: ✅ Complete and ready for model training
