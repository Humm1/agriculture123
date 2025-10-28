# 🎓 AgroShield ML Training System - Complete Guide

## 📋 Overview

This system trains 7 AI models using **real agricultural data from public APIs** combined with synthetic datasets:

### Models Trained:
1. **Pest Detection** - Identifies 7 common agricultural pests
2. **Disease Detection** - Detects 38 plant disease classes
3. **Soil Diagnostics** - Classifies 6 Kenyan soil types
4. **Yield Prediction** - Predicts crop yields based on conditions
5. **Climate Prediction** - Forecasts weather patterns
6. **Storage Assessment** - Evaluates crop storage conditions
7. **Plant Health** - Overall plant health monitoring

---

## 🌍 Data Sources (All FREE & Public)

### Real-World Data (Public APIs):
| Source | Data Type | Samples | API Key Required? |
|--------|-----------|---------|-------------------|
| **PlantVillage** | Disease images | 54,000+ | ✅ Kaggle account (free) |
| **iNaturalist** | Pest observations | 500+ | ❌ No (public API) |
| **FAO SoilGrids** | Soil properties | Global coverage | ❌ No (public API) |
| **OpenWeatherMap** | Climate data | Unlimited | ✅ Free tier (1,000/day) |
| **GBIF** | Species distribution | 2 billion records | ❌ No (public API) |

### Synthetic Data:
- Pest detection: 1,050 images (7 classes)
- Disease detection: 1,400 images (10 classes)
- Soil diagnostics: 1,050 images (6 types)
- Yield prediction: 1,000 records
- Climate prediction: 3,650 timesteps (10 years)

**Total Dataset**: 50,000+ images + 10,000+ tabular records

---

## 🚀 Quick Start (3 Steps)

### Option 1: No API Keys (Start Immediately)

```bash
cd backend
python master_train_models.py --train-all --skip-collection
```

This uses synthetic data only. Training completes in **10-20 minutes**.

### Option 2: With Public API Data (Recommended)

```bash
# Step 1: Get free API keys (2 minutes)
# - OpenWeatherMap: https://openweathermap.org/api
# - Kaggle: https://www.kaggle.com/settings (API section)

# Step 2: Set environment variables
set OPENWEATHER_API_KEY=your_key_here  # Windows
export OPENWEATHER_API_KEY=your_key_here  # Linux/Mac

# Step 3: Run full pipeline
python master_train_models.py --collect-data --train-all
```

This collects real data + trains models. Takes **30-60 minutes** total.

---

## 📦 Installation

### 1. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt

# Additional packages for training
pip install aiohttp kaggle pillow pandas numpy scikit-learn tensorflow
```

### 2. Setup Kaggle (Optional - for PlantVillage dataset)

```bash
# Get API token from: https://www.kaggle.com/settings
# Download kaggle.json

# Windows:
mkdir %USERPROFILE%\.kaggle
move kaggle.json %USERPROFILE%\.kaggle\

# Linux/Mac:
mkdir ~/.kaggle
mv kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

### 3. Get OpenWeatherMap Key (Optional - for climate data)

1. Visit: https://openweathermap.org/api
2. Sign up (free)
3. Get API key from dashboard
4. Add to `.env` file:
   ```env
   OPENWEATHER_API_KEY=your_key_here
   ```

---

## 📖 Usage Guide

### Run Complete Pipeline

```bash
# Full pipeline: collect data + train all models
python master_train_models.py --collect-data --train-all

# Use existing data (skip collection)
python master_train_models.py --train-all --skip-collection
```

### Individual Steps

```bash
# Step 1: Collect public API data only
python collect_public_api_data.py --all

# Step 2: Generate synthetic data only
python generate_training_datasets.py

# Step 3: Train models only
python train_models_example.py
```

### Train Specific Model

```bash
python master_train_models.py --model pest_detection
python master_train_models.py --model yield_prediction
```

---

## 📊 What You'll Get

### Trained Models (in `trained_models/`)
```
pest_detection_mobilenet_v3.h5        (15-20 MB)
disease_detection_efficientnet.h5     (20-25 MB)
soil_diagnostics_custom_cnn.h5        (10-15 MB)
yield_prediction_rf.pkl               (5-10 MB)
climate_prediction_lstm.h5            (8-12 MB)
storage_assessment_cnn.h5             (12-18 MB)
plant_health_mobilenet.h5             (15-20 MB)
```

### Training Data (in `training_data/` and `training_data_public/`)
```
training_data/
├── pest_detection/
│   ├── aphids/           (150 images)
│   ├── whiteflies/       (150 images)
│   ├── armyworms/        (150 images)
│   └── ...
├── disease_detection/
├── soil_diagnostics/
├── yield_prediction/
└── climate_prediction/

training_data_public/
├── plantvillage_diseases/    (54,000+ images from Kaggle)
├── inaturalist_pests/        (500+ pest observations)
├── soil_data/                (FAO SoilGrids data)
└── climate_data/             (OpenWeatherMap data)
```

### Training Logs (in `training_logs/`)
```
training_report_20251028_143022.json
validation_report_20251028_145533.json
pest_detection_training_log.json
```

---

## 🎯 Performance Metrics

### Expected Accuracies:
| Model | Accuracy/Score | Training Time |
|-------|---------------|---------------|
| Pest Detection | 85-92% | 5-10 min |
| Disease Detection | 87-94% | 8-15 min |
| Soil Diagnostics | 82-88% | 4-8 min |
| Yield Prediction | R² 0.75-0.85 | 2-5 min |
| Climate Prediction | MAE 1.5-2.5°C | 10-15 min |
| Storage Assessment | 80-87% | 5-10 min |
| Plant Health | 84-91% | 6-12 min |

**Total Training Time**: 40-75 minutes (depending on hardware)

---

## 🔧 Configuration

### Environment Variables (.env)
```env
# Required for climate data
OPENWEATHER_API_KEY=your_key_here

# Optional: Supabase (for storing training results)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_service_key
```

### Training Parameters (in scripts)
```python
# pest_detection
epochs = 10
batch_size = 32
learning_rate = 0.001

# yield_prediction
n_estimators = 100
max_depth = 15

# climate_prediction
lstm_units = 64
sequence_length = 30
```

---

## 📁 Project Structure

```
backend/
├── master_train_models.py           # 🎯 Main orchestrator
├── collect_public_api_data.py       # 🌍 Public API data collector
├── generate_training_datasets.py    # 🎨 Synthetic data generator
├── train_models_example.py          # 🎓 Model training script
│
├── API_KEYS_SETUP_GUIDE.md         # 🔐 How to get free API keys
├── TRAINING_WITH_PUBLIC_DATA.md    # 📖 This file
│
├── app/
│   ├── services/
│   │   ├── model_training.py       # Training service
│   │   ├── data_collection.py      # Supabase data fetching
│   │   └── ml_inference.py         # Model loading & prediction
│   └── routes/
│       └── ml_training_routes.py   # FastAPI endpoints
│
├── training_data/                   # Synthetic datasets
├── training_data_public/            # Public API datasets
├── trained_models/                  # Saved models (.h5, .pkl)
└── training_logs/                   # Training reports
```

---

## 🐛 Troubleshooting

### Issue: "No module named 'tensorflow'"
```bash
pip install tensorflow==2.15.0
```

### Issue: "Kaggle API not found"
```bash
pip install kaggle
# Then setup kaggle.json as shown above
```

### Issue: "Permission denied on kaggle.json"
```bash
chmod 600 ~/.kaggle/kaggle.json  # Linux/Mac
```

### Issue: "OpenWeatherMap API error"
- Check your API key is valid
- Free tier limit: 1,000 calls/day
- Get new key: https://openweathermap.org/api

### Issue: "Out of memory during training"
```python
# Reduce batch size in training scripts
batch_size = 16  # Instead of 32
```

### Issue: "Training takes too long"
```python
# Reduce epochs
epochs = 5  # Instead of 10

# Or train specific models only
python master_train_models.py --model pest_detection
```

---

## 📚 API Documentation

### Free Public APIs Used:

1. **iNaturalist API** (No key required)
   - Endpoint: `https://api.inaturalist.org/v1/observations`
   - Docs: https://api.inaturalist.org/v1/docs/
   - Rate limit: Unlimited (public)

2. **FAO SoilGrids API** (No key required)
   - Endpoint: `https://rest.isric.org/soilgrids/v2.0`
   - Docs: https://www.isric.org/explore/soilgrids/faq-soilgrids
   - Rate limit: Unlimited (public)

3. **GBIF API** (No key required)
   - Endpoint: `https://api.gbif.org/v1`
   - Docs: https://www.gbif.org/developer/summary
   - Rate limit: Unlimited (public)

4. **OpenWeatherMap API** (Free tier: 1,000/day)
   - Endpoint: `https://api.openweathermap.org/data/2.5`
   - Docs: https://openweathermap.org/api
   - Signup: https://home.openweathermap.org/users/sign_up

5. **PlantVillage Dataset** (via Kaggle)
   - Dataset: https://www.kaggle.com/datasets/abdallahalidev/plantvillage-dataset
   - Size: 54,000+ images, 38 disease classes
   - Signup: https://www.kaggle.com/

---

## 🎓 Next Steps After Training

### 1. Test Models
```python
from app.services.ml_inference import ModelInferenceService

service = ModelInferenceService()
prediction = service.predict_pest(image_path="test_image.jpg")
print(prediction)
```

### 2. Deploy to Backend
```bash
# Models are auto-loaded by FastAPI server
python run_server.py

# Test prediction endpoint
curl -X POST http://localhost:8000/api/advanced-growth/analyze-growth \
  -F "image=@test_image.jpg" \
  -F "plot_id=123"
```

### 3. Monitor Performance
- Track prediction accuracy
- Collect user feedback
- Retrain with real farm data

### 4. Continuous Improvement
```bash
# Collect new data from Supabase
python -m app.services.data_collection

# Retrain models with user feedback
python -m app.services.model_training
```

---

## 🤝 Contributing

### Add New Data Source
1. Edit `collect_public_api_data.py`
2. Add new collector class
3. Update `collect_all_data()` function

### Add New Model
1. Edit `generate_training_datasets.py` (add synthetic data)
2. Edit `train_models_example.py` (add training function)
3. Update `master_train_models.py` (add to pipeline)

---

## 📄 License & Data Attribution

### Code
- AgroShield backend: MIT License

### Datasets
- **PlantVillage**: CC BY 4.0 (attribution required)
- **iNaturalist**: CC BY-NC 4.0 (non-commercial)
- **FAO SoilGrids**: CC BY 4.0 (attribution required)
- **GBIF**: CC0 / CC BY (varies by record)

**Attribution Example**:
```
Plant disease images from PlantVillage Dataset (Penn State University)
Pest observations from iNaturalist (Community Science Platform)
Soil data from ISRIC SoilGrids (FAO)
```

---

## 📞 Support

### Documentation
- Main README: `../README.md`
- API Setup: `API_KEYS_SETUP_GUIDE.md`
- Model Training: `ML_TRAINING_IMPLEMENTATION_SUMMARY.md`

### Issues
- Check `training_logs/` for error details
- Review console output during training
- Enable debug mode: `export DEBUG=1`

---

## ✅ Quick Checklist

Before training:
- [ ] Python 3.8+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] At least 5GB free disk space
- [ ] (Optional) OpenWeatherMap API key set
- [ ] (Optional) Kaggle CLI configured

To start training:
```bash
python master_train_models.py --collect-data --train-all
```

Expected time: **30-60 minutes**  
Expected output: **7 trained models** in `trained_models/`

---

**Last Updated**: October 28, 2025  
**Version**: 1.0.0  
**Maintainer**: AgroShield AI Team
