# AgroShield Deployment Guide: Phase 1 & 2 Integration

**Complete implementation guide for model training and API configuration**

---

## 📋 Table of Contents

1. [Phase 1: Model Training (2-4 weeks)](#phase-1-model-training)
2. [Phase 2: API Configuration (1 week)](#phase-2-api-configuration)
3. [Phase 3: Integration Testing (2 weeks)](#phase-3-integration-testing)
4. [Phase 4: Production Deployment (1 week)](#phase-4-production-deployment)
5. [Troubleshooting](#troubleshooting)
6. [Resources](#resources)

---

## Phase 1: Model Training (2-4 weeks)

### Overview

Train 4 AI models for AgroShield's Predictive, Context-Aware Agriculture (PCA) system:

1. **Plant Health Detection** (MobileNet V3) - Edge deployment
2. **Soil Diagnostics** (EfficientNet B0) - Edge deployment
3. **Climate Prediction** (LSTM) - Cloud deployment
4. **Spoilage Prediction** (Time-series) - Cloud deployment

---

### 1.1 Plant Health Detection Model

**Target**: >88% accuracy on 10 disease classes

#### Dataset Requirements

```
data/plant_diseases/
  ├── healthy/ (500+ images)
  ├── late_blight/ (500+ images)
  ├── early_blight/ (500+ images)
  ├── bacterial_wilt/ (500+ images)
  ├── powdery_mildew/ (500+ images)
  ├── leaf_rust/ (500+ images)
  ├── fall_armyworm/ (500+ images)
  ├── maize_streak_virus/ (500+ images)
  ├── anthracnose/ (500+ images)
  └── fusarium_wilt/ (500+ images)
```

**Total**: 5,000+ images minimum

#### Data Collection Sources

1. **Kenya Agricultural Research Institute (KARI)**
   - Contact: info@kalro.org
   - Request: Disease image dataset for research

2. **CGIAR Research Centers**
   - PlantVillage dataset: https://plantvillage.psu.edu/
   - International Potato Center (CIP)
   - International Maize and Wheat Improvement Center (CIMMYT)

3. **Field Collection**
   - Partner with local agricultural extension officers
   - Photograph symptomatic plants in farmer fields
   - Ensure proper labeling and GPS tagging

4. **Data Augmentation**
   - Rotation, flipping, zoom (handled automatically by training script)
   - Color jittering for lighting variations

#### Image Requirements

- **Format**: JPG, PNG
- **Resolution**: Minimum 224×224 pixels (higher resolution will be resized)
- **Lighting**: Well-lit, clear disease symptoms
- **Background**: Natural field conditions (not lab-controlled)
- **Diversity**: Multiple growth stages, weather conditions, time of day

#### Training Script

```bash
# Install dependencies
pip install tensorflow>=2.14.0 matplotlib pandas

# Run training
python backend/app/ml/train_plant_health_model.py
```

**Expected Output**:
```
models/plant_health/
  ├── best_model.keras (Keras model)
  ├── plant_health_model.tflite (TFLite model ~5 MB)
  ├── model_metadata.json
  ├── MODEL_CARD.md
  ├── training_curves.png
  └── logs/ (TensorBoard logs)
```

#### Validation Metrics

- **Validation Accuracy**: ≥88%
- **Top-3 Accuracy**: ≥95%
- **Inference Time**: ≤150ms (on mobile CPU)
- **Model Size**: ≤10 MB

#### Training Timeline

| Task | Duration |
|------|----------|
| Dataset collection | 1-2 weeks |
| Data preprocessing | 2 days |
| Model training | 6-12 hours |
| Validation & tuning | 2-3 days |
| TFLite conversion | 1 hour |

---

### 1.2 Soil Diagnostics Model

**Target**: >80% accuracy on NPK deficiency classification

#### Dataset Requirements

```
data/soil_images/
  ├── images/
  │   ├── soil_001.jpg
  │   ├── soil_002.jpg
  │   └── ... (500+ images)
  └── labels.csv
```

**labels.csv format**:
```csv
image_path,nitrogen_ppm,phosphorus_ppm,potassium_ppm
soil_001.jpg,45,18,250
soil_002.jpg,15,8,120
soil_003.jpg,55,30,280
...
```

#### Data Collection

1. **Partner with Soil Testing Labs**
   - Kenya Soil Survey
   - Agricultural university labs
   - Private soil testing services

2. **Collection Protocol**:
   - Take soil sample photo (consistent lighting, angle)
   - Send sample to lab for NPK analysis
   - Correlate lab results with photo

3. **Minimum Samples**: 500+ correlated samples

#### NPK Classification Ranges

```python
CONFIG = {
    "npk_ranges": {
        "nitrogen": {"low": 20, "medium": 40, "high": 60},  # ppm
        "phosphorus": {"low": 10, "medium": 25, "high": 40},  # ppm
        "potassium": {"low": 100, "medium": 200, "high": 300}  # ppm
    }
}
```

#### Training

```bash
python backend/app/ml/train_soil_diagnostics_model.py
```

**Expected Output**:
```
models/soil_diagnostics/
  ├── best_model.keras
  ├── soil_diagnostics_model.tflite (~4 MB)
  ├── model_metadata.json
  └── MODEL_CARD.md
```

---

### 1.3 Climate Prediction Model

**Target**: MAE <2°C for temperature, <15% for rainfall

#### Dataset Requirements

**Historical weather data** (10+ years):
```csv
date,temperature_c,humidity_percent,rainfall_mm,pressure_hpa,wind_speed_kmh
2014-01-01,25.3,65,2.5,1013,12
2014-01-02,26.1,62,0,1012,10
...
```

**Minimum**: 3,650 days (10 years) of daily weather data

#### Data Sources

1. **Kenya Meteorological Department**
   - Contact: info@meteo.go.ke
   - Request: Historical weather data for specific locations

2. **NOAA (National Oceanic and Atmospheric Administration)**
   - Global Historical Climatology Network
   - https://www.ncei.noaa.gov/

3. **OpenWeatherMap Historical Data**
   - Paid historical weather API
   - https://openweathermap.org/history

#### Training

```bash
python backend/app/ml/train_climate_prediction_model.py
```

**Model Architecture**:
- 3 stacked LSTM layers (128, 64, 32 units)
- Input: 30 days of weather history
- Output: 7-day forecast (temperature, rainfall)

**Expected Output**:
```
models/climate_prediction/
  ├── best_lstm_model.keras
  ├── lstm_metadata.json
  └── MODEL_CARD.md
```

**Note**: LSTM model runs on cloud (not converted to TFLite)

---

### 1.4 TensorFlow Lite Optimization

After training, convert models to TFLite for mobile deployment:

```python
# Already integrated in training scripts
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()
```

**Optimizations Applied**:
- Dynamic range quantization (8-bit weights)
- ~75% size reduction
- 2-3x faster inference on mobile

#### Mobile Deployment Example (Android)

```kotlin
// Load TFLite model
val tfliteModel = loadModelFile("plant_health_model.tflite")
val interpreter = Interpreter(tfliteModel)

// Preprocess image
val inputBuffer = preprocessImage(bitmap) // [1, 224, 224, 3]

// Run inference
val outputBuffer = Array(1) { FloatArray(10) } // 10 classes
interpreter.run(inputBuffer, outputBuffer)

// Get prediction
val predictedClass = outputBuffer[0].indices.maxByOrNull { outputBuffer[0][it] }
val confidence = outputBuffer[0][predictedClass!!]
```

---

## Phase 2: API Configuration (1 week)

### Overview

Obtain API keys from 5 services to enable context-aware recommendations.

---

### 2.1 CGIAR Plant Health Database

**Purpose**: Disease treatment database from international research

**Application Process**:

1. **Contact**: research@cgiar.org

2. **Email Template**:
```
Subject: API Access Request for AgroShield Agricultural Platform

Dear CGIAR Research Team,

I am developing AgroShield, an AI-powered agricultural advisory 
platform for Kenyan smallholder farmers. Our system provides:
- Plant disease detection (MobileNet V3 with >88% accuracy)
- Context-aware treatment recommendations
- Real-time farmer guidance via SMS

I would like to request API access to the CGIAR Plant Health 
Database to enhance our disease treatment recommendations with 
internationally recognized research data.

Project details:
- Target users: 50,000+ Kenyan smallholder farmers
- Use case: Disease identification and treatment guidance
- Expected API usage: ~1,000 requests/day
- Non-commercial research project

Thank you for considering this request.

Best regards,
[Your Name]
[Organization]
[Contact Information]
```

3. **Expected Timeline**: 1-2 weeks approval

4. **Configuration**:
```bash
export CGIAR_API_KEY="your_api_key_here"
```

---

### 2.2 KEPHIS API

**Purpose**: Kenya-registered agricultural products and pesticides

**Application Process**:

1. Visit: https://www.kephis.go.ke/
2. Navigate to: Developer Portal
3. Register account with:
   - Organization name
   - Business registration number
   - Use case description
   - Expected request volume

4. **Expected Timeline**: 3-5 business days

5. **Configuration**:
```bash
export KEPHIS_API_KEY="your_api_key_here"
```

---

### 2.3 OpenWeatherMap

**Purpose**: Real-time weather data and 7-day forecasts

**Application Process**:

1. Visit: https://openweathermap.org/api
2. Click "Sign Up" → Create account
3. Navigate to: API Keys section
4. Copy default API key (auto-generated)

**Plans**:
- **Free**: 1,000 calls/day (testing)
- **Startup**: $40/month, 100,000 calls/day (production)

**Test Command**:
```bash
curl "https://api.openweathermap.org/data/2.5/weather?lat=-1.286389&lon=36.817223&appid=YOUR_KEY"
```

**Expected Response**:
```json
{
  "weather": [{"main": "Clear", "description": "clear sky"}],
  "main": {"temp": 298.15, "humidity": 65},
  "wind": {"speed": 3.5}
}
```

**Configuration**:
```bash
export OPENWEATHERMAP_API_KEY="your_api_key_here"
```

---

### 2.4 Hugging Face

**Purpose**: Multilingual NLP for Swahili SMS generation

**Application Process**:

1. Visit: https://huggingface.co/
2. Sign up (email/GitHub/Google)
3. Navigate to: Settings → Access Tokens
4. Create token:
   - Name: "AgroShield"
   - Role: "Read" (sufficient for inference)
5. Copy token (save securely)

**Models to Use**:
- **Translation**: `Helsinki-NLP/opus-mt-en-sw` (English → Swahili)
- **Summarization**: `facebook/bart-large-cnn`

**Test Script**:
```python
import requests

url = "https://api-inference.huggingface.co/models/Helsinki-NLP/opus-mt-en-sw"
headers = {"Authorization": "Bearer YOUR_TOKEN"}
payload = {"inputs": "The plant has late blight disease."}

response = requests.post(url, headers=headers, json=payload)
print(response.json())
# Output: [{"translation_text": "Mmea una ugonjwa wa late blight."}]
```

**Configuration**:
```bash
export HUGGINGFACE_TOKEN="your_token_here"
```

---

### 2.5 FAO SoilGrids

**Purpose**: Global soil property data (pH, organic carbon, texture)

**No API Key Needed** - Public service!

**Endpoint**: https://rest.isric.org/soilgrids/v2.0/

**Test Request**:
```bash
curl "https://rest.isric.org/soilgrids/v2.0/properties/query?lat=-1.286389&lon=36.817223&property=phh2o&depth=0-5cm"
```

**Response**:
```json
{
  "properties": {
    "phh2o": {
      "mean": 6.2,
      "uncertainty": 0.5
    }
  }
}
```

---

### 2.6 API Validation

After obtaining all keys, run validation script:

```bash
python backend/app/config/api_config.py
```

**Expected Output**:
```
============================================================
API KEY VALIDATION
============================================================
✓ cgiar: API key valid - access granted
✓ kephis: API key valid - access granted
✓ openweathermap: API key valid - Nairobi weather retrieved
✓ huggingface: Token valid - translation model accessible
✓ fao_soilgrids: Public service (no key needed)

============================================================
VALIDATION SUMMARY
============================================================
Valid APIs: 5/5
✓ All API keys configured and valid!
```

---

## Phase 3: Integration Testing (2 weeks)

### 3.1 End-to-End Testing

Test complete workflow from image capture to farmer SMS:

```bash
# Run integration tests
pytest tests/test_tensorflow_integration.py -v

# Run with coverage
pytest tests/test_tensorflow_integration.py --cov=app/services --cov-report=html
```

**Test Scenarios**:
1. ✅ Upload plant image → Disease detection → Treatment recommendations
2. ✅ Check weather → Combine with disease → Timing guidance
3. ✅ Detect outbreak nearby → Contagion risk → Alert farmers
4. ✅ Generate Swahili SMS → Send via Africa's Talking
5. ✅ Offline mode (no internet) → TFLite inference only

---

### 3.2 Performance Benchmarking

```python
# Inference speed test
python -m pytest tests/test_tensorflow_integration.py::test_inference_speed
```

**Targets**:
- TFLite inference: <150ms
- API response: <2s
- End-to-end workflow: <5s

---

### 3.3 Accuracy Validation

Test with real farmer photos:

```bash
python backend/app/ml/validate_model.py \
  --model models/plant_health/plant_health_model.tflite \
  --test_images data/validation_set/ \
  --ground_truth data/validation_labels.csv
```

**Expected Metrics**:
- Accuracy: ≥88%
- Precision: ≥85%
- Recall: ≥80%
- F1-Score: ≥82%

---

## Phase 4: Production Deployment (1 week)

### 4.1 Mobile App Integration

**Android Deployment**:

1. Copy TFLite models to app:
```bash
cp models/plant_health/plant_health_model.tflite \
   android/app/src/main/assets/
cp models/soil_diagnostics/soil_diagnostics_model.tflite \
   android/app/src/main/assets/
```

2. Update Android code:
```kotlin
// Load models
val plantHealthModel = loadModelFile("plant_health_model.tflite")
val soilModel = loadModelFile("soil_diagnostics_model.tflite")

// Initialize interpreters
val plantHealthInterpreter = Interpreter(plantHealthModel)
val soilInterpreter = Interpreter(soilModel)
```

3. Test on devices:
   - Low-end: ~200ms inference
   - Mid-range: ~100ms inference
   - High-end: ~50ms inference

---

### 4.2 Backend Deployment

**Deploy FastAPI backend**:

```bash
# Build Docker image
docker build -t agroshield-backend:latest .

# Run container
docker run -d \
  -p 8000:8000 \
  -e CGIAR_API_KEY=$CGIAR_API_KEY \
  -e KEPHIS_API_KEY=$KEPHIS_API_KEY \
  -e OPENWEATHERMAP_API_KEY=$OPENWEATHERMAP_API_KEY \
  -e HUGGINGFACE_TOKEN=$HUGGINGFACE_TOKEN \
  agroshield-backend:latest
```

**Cloud Deployment Options**:
- AWS EC2 / Elastic Beanstalk
- Google Cloud Run
- Azure App Service
- DigitalOcean Droplets

---

### 4.3 Model Updates

**Continuous Improvement**:

1. Collect farmer feedback
2. Retrain models quarterly with new data
3. A/B test new model versions
4. Deploy via OTA (Over-The-Air) updates

---

## Troubleshooting

### Model Training Issues

**Problem**: Low accuracy (<88%)
**Solutions**:
- Collect more diverse training data
- Increase augmentation intensity
- Train for more epochs
- Try different learning rates

**Problem**: Overfitting (high train, low val accuracy)
**Solutions**:
- Increase dropout (0.3 → 0.5)
- Add L2 regularization
- Reduce model complexity
- Collect more training data

**Problem**: Slow inference (>150ms)
**Solutions**:
- Use GPU delegate on mobile
- Reduce input resolution (224 → 192)
- Apply more aggressive quantization
- Use MobileNet V3 Small (not Large)

---

### API Issues

**Problem**: "Invalid API Key"
**Solutions**:
- Check for typos in key
- Verify key is active
- Confirm correct environment variable name

**Problem**: "Rate Limit Exceeded"
**Solutions**:
- Implement request caching (30 min)
- Upgrade API plan
- Use multiple API keys (round-robin)

**Problem**: "Connection Timeout"
**Solutions**:
- Increase timeout (10s → 30s)
- Implement retry logic (3 attempts)
- Fall back to simulation mode

---

## Resources

### Documentation
- TensorFlow Lite: https://www.tensorflow.org/lite
- Keras: https://keras.io/
- FastAPI: https://fastapi.tiangolo.com/

### Datasets
- PlantVillage: https://plantvillage.psu.edu/
- CGIAR: https://www.cgiar.org/
- NOAA Weather: https://www.ncei.noaa.gov/

### API Documentation
- OpenWeatherMap: https://openweathermap.org/api
- Hugging Face: https://huggingface.co/docs
- CGIAR: Contact research@cgiar.org
- KEPHIS: https://www.kephis.go.ke/

### Contact
- Email: support@agroshield.ke
- Issues: github.com/agroshield/agroshield/issues

---

## Completion Checklist

### Phase 1: Model Training
- [ ] Collected 5,000+ plant disease images (500+ per class)
- [ ] Trained MobileNet V3 plant health model (>88% accuracy)
- [ ] Trained EfficientNet B0 soil diagnostics model (>80% accuracy)
- [ ] Trained LSTM climate prediction model (MAE <2°C)
- [ ] Converted models to TFLite (plant health, soil diagnostics)
- [ ] Validated inference speed (<150ms on mobile)
- [ ] Generated model cards and metadata

### Phase 2: API Configuration
- [ ] CGIAR API key obtained (research@cgiar.org)
- [ ] KEPHIS API key obtained (kephis.go.ke/developers)
- [ ] OpenWeatherMap API key created
- [ ] Hugging Face token generated
- [ ] All keys validated with test requests
- [ ] Configuration saved to config/api_keys.json
- [ ] Environment variables configured

### Phase 3: Integration Testing
- [ ] End-to-end tests passing (90% coverage)
- [ ] Performance benchmarks met (<5s total)
- [ ] Accuracy validated on real farmer photos
- [ ] Offline mode tested (TFLite only)
- [ ] SMS generation tested (Swahili output)

### Phase 4: Production Deployment
- [ ] TFLite models deployed to mobile app
- [ ] Backend deployed to cloud server
- [ ] API keys configured in production
- [ ] Monitoring dashboard active
- [ ] User feedback collection enabled

---

**🎉 Congratulations! AgroShield is production-ready!**

Total timeline: **5-7 weeks**
- Phase 1: 2-4 weeks
- Phase 2: 1 week (parallel with Phase 1)
- Phase 3: 2 weeks
- Phase 4: 1 week

---

*Generated: October 2025*  
*Version: 1.0*  
*AgroShield AI Platform - Empowering Kenyan Farmers*
