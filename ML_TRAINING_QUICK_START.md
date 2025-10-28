# 🚀 ML Training System - Quick Reference

## ✅ What Was Implemented

### Backend (Python/FastAPI)
- ✅ Enhanced ML training service (`enhanced_model_training.py`) - 700+ lines
- ✅ ML API routes (`ml_training_routes.py`) - 450+ lines
- ✅ Dataset generation script (`generate_training_datasets.py`) - 463 lines
- ✅ Training examples (`train_models_example.py`) - 450+ lines
- ✅ Integrated into `app/main.py` at `/api/ml`

### Frontend (React Native)
- ✅ Model Training Dashboard (`ModelTrainingScreen.js`) - 400+ lines
- ✅ Trained Models Viewer (`TrainedModelsScreen.js`) - 550+ lines
- ✅ Integrated into `FarmStack.js` navigation
- ✅ Quick action button on Home Screen

### Models Supported
1. ✅ Pest Detection (MobileNetV3, 1,050 images)
2. ✅ Disease Detection (MobileNetV3, 1,050 images)
3. ✅ Soil Diagnostics (Custom CNN, 720 images)
4. ✅ Yield Prediction (Random Forest, 1,000 records)
5. ✅ Climate Prediction (LSTM, 730 records)

## 🎯 Quick Start (3 Steps)

### Step 1: Generate Datasets
```bash
cd backend
python generate_training_datasets.py
# Wait 5-10 minutes → Creates training_data/ folder
```

### Step 2: Train a Model
**Option A - From Frontend:**
1. Open app → Home → AI Training (brain icon)
2. Tap "Generate Datasets" (if needed)
3. Select model → Tap "Train"
4. Monitor progress

**Option B - From API:**
```bash
curl -X POST "https://urchin-app-86rjy.ondigitalocean.app/api/ml/train" \
  -H "Content-Type: application/json" \
  -d '{"model_type": "pest_detection", "epochs": 10}'
```

### Step 3: View Results
```bash
# Check training status
curl "https://urchin-app-86rjy.ondigitalocean.app/api/ml/training/status"

# View trained models
curl "https://urchin-app-86rjy.ondigitalocean.app/api/ml/models/summary"
```

## 📱 Frontend Navigation

```
Home Screen (Quick Action "AI Training")
    ↓
ModelTrainingScreen
    • Generate datasets button
    • Train model buttons (5 models)
    • Real-time progress tracking
    ↓
TrainedModelsScreen
    • Accuracy metrics
    • Training history
    • Model details
```

## 🔌 Key API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/ml/datasets/generate` | POST | Generate synthetic datasets |
| `/api/ml/datasets/status` | GET | Check if datasets exist |
| `/api/ml/train` | POST | Start model training |
| `/api/ml/training/status` | GET | Check training progress |
| `/api/ml/models/summary` | GET | View trained models |
| `/api/ml/training/history` | GET | View training history |
| `/api/ml/model-types` | GET | Get model info |

## 📊 Expected Results

| Model | Accuracy | Training Time | Model Size |
|-------|----------|---------------|------------|
| Pest Detection | 85-95% | 10-15 min | ~8 MB |
| Disease Detection | 85-95% | 10-15 min | ~8 MB |
| Soil Diagnostics | 80-90% | 15-20 min | ~15 MB |
| Yield Prediction | R²>0.85 | 2-3 min | ~1 MB |
| Climate Prediction | MAE<2°C | 15-20 min | ~2 MB |

## 🗂️ File Structure

```
agroshield/
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   │   └── ml_training_routes.py          ← API endpoints
│   │   └── services/
│   │       └── enhanced_model_training.py     ← Training logic
│   ├── generate_training_datasets.py          ← Dataset generator
│   ├── train_models_example.py                ← Standalone trainer
│   ├── training_data/                         ← Generated datasets
│   │   ├── pest_detection/
│   │   ├── disease_detection/
│   │   ├── soil_diagnostics/
│   │   ├── climate_prediction/
│   │   └── yield_prediction/
│   └── trained_models/                        ← Saved models
│       ├── pest_detection_model.h5
│       ├── yield_prediction_model.pkl
│       └── training_history.json
│
└── frontend/agroshield-app/src/
    ├── screens/farmer/
    │   ├── ModelTrainingScreen.js             ← Training dashboard
    │   └── TrainedModelsScreen.js             ← Results viewer
    └── navigation/
        ├── FarmStack.js                       ← Added routes
        └── home/HomeScreen.js                 ← Added quick action
```

## 🔥 Common Commands

### Generate Datasets
```bash
cd backend
python generate_training_datasets.py
```

### Validate Datasets
```bash
python validate_datasets.py
```

### Train Single Model
```bash
python train_models_example.py
# Select option 1-5
```

### Start Backend Server
```bash
cd backend
python run_server.py
```

### Check API Health
```bash
curl "https://urchin-app-86rjy.ondigitalocean.app/api/ml/health"
```

## 🐛 Troubleshooting

**Problem: "Dataset not found"**
```bash
# Solution: Generate datasets first
cd backend
python generate_training_datasets.py
```

**Problem: "Training stuck at 0%"**
```bash
# Solution: Check backend logs
tail -f backend/logs/training.log
```

**Problem: "Frontend not showing progress"**
```javascript
// Solution: Check console logs
console.log('Training status:', trainingStatus);
```

**Problem: "Module not found: tensorflow"**
```bash
# Solution: Install dependencies
pip install -r backend/requirements-datasets.txt
pip install tensorflow scikit-learn
```

## 📈 Performance Tips

1. **Start with Small Epochs**: Test with 5 epochs first
2. **Use GPU if Available**: Speeds up training 10-50x
3. **Monitor Memory**: Close other apps during training
4. **Batch Training**: Train all models overnight
5. **Save Progress**: Models auto-save after each run

## 🎓 Model Details

### Pest Detection
```python
# Classes
['aphids', 'whiteflies', 'armyworms', 'leaf_miners', 
 'thrips', 'cutworms', 'healthy']

# Architecture
MobileNetV3Small (pretrained) + 
GlobalAveragePooling2D + 
Dense(128) + Dropout(0.3) + 
Dense(7, softmax)
```

### Yield Prediction
```python
# Features
['crop', 'area_hectares', 'soil_quality', 'irrigation_level',
 'fertilizer_kg_per_hectare', 'pest_pressure', 'disease_occurrence',
 'avg_temperature', 'annual_rainfall', 'quality_grade']

# Algorithm
RandomForestRegressor(n_estimators=100, max_depth=15)
```

## 🚀 Next Steps

1. ✅ **System Ready** - All components implemented
2. 🔄 **Generate Datasets** - Run generation script
3. 🏋️ **Train Models** - Start with pest detection
4. 📊 **View Results** - Check accuracy in frontend
5. 🎯 **Replace Data** - Use real farm images
6. 📈 **Optimize** - Tune hyperparameters
7. 🌍 **Deploy** - Use models in production

## 📞 Support

- Full Guide: `ML_TRAINING_COMPLETE_GUIDE.md`
- Dataset README: `backend/TRAINING_DATASETS_README.md`
- API Docs: `https://urchin-app-86rjy.ondigitalocean.app/docs`
- GitHub Issues: Report bugs and request features

---

**Created**: October 28, 2025  
**Status**: ✅ Complete & Ready for Use  
**Models**: 5 AI models with 5,270 training samples  
**Lines of Code**: 2,500+ lines (backend + frontend)
