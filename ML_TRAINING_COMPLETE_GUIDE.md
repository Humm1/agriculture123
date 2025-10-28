# AI Model Training System - Complete Guide

## 🎯 Overview

The AgroShield AI Model Training System enables farmers and administrators to train custom AI models using synthetic or real-world data. The system supports 5 different AI models across various agricultural use cases.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND (React Native)                 │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │ ModelTraining    │         │ TrainedModels    │         │
│  │ Screen           │────────▶│ Screen           │         │
│  └──────────────────┘         └──────────────────┘         │
└─────────────────────────────────────────────────────────────┘
                         │
                         │ HTTPS API Calls
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  BACKEND (FastAPI + Python)                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  /api/ml Routes (ml_training_routes.py)              │  │
│  │  • POST /datasets/generate                           │  │
│  │  • GET /datasets/status                              │  │
│  │  • POST /train                                       │  │
│  │  • GET /training/status                              │  │
│  │  • GET /models/summary                               │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                    │
│                         ▼                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  EnhancedModelTrainingService                        │  │
│  │  (enhanced_model_training.py)                        │  │
│  │  • train_pest_detection_model()                      │  │
│  │  • train_disease_detection_model()                   │  │
│  │  • train_soil_diagnostics_model()                    │  │
│  │  • train_yield_prediction_model()                    │  │
│  │  • train_climate_prediction_model()                  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    TRAINING DATA & MODELS                    │
│  ┌─────────────────┐           ┌──────────────────┐        │
│  │ training_data/  │           │ trained_models/  │        │
│  │ • pest_detection│           │ • .h5 files      │        │
│  │ • disease_...   │────────▶  │ • .pkl files     │        │
│  │ • soil_...      │           │ • .json metadata │        │
│  │ • climate.csv   │           │                  │        │
│  │ • yield.csv     │           │                  │        │
│  └─────────────────┘           └──────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## 📊 Supported Models

### 1. Pest Detection
- **Type**: Image Classification (CNN)
- **Algorithm**: MobileNetV3 + Transfer Learning
- **Input**: RGB image (224x224)
- **Output**: 7 pest classes + healthy
- **Classes**: aphids, whiteflies, armyworms, leaf_miners, thrips, cutworms, healthy
- **Dataset**: 1,050 synthetic images
- **Expected Accuracy**: 85-95%

### 2. Disease Detection
- **Type**: Image Classification (CNN)
- **Algorithm**: MobileNetV3 + Transfer Learning
- **Input**: RGB image (224x224)
- **Output**: 7 disease classes + healthy
- **Classes**: early_blight, late_blight, leaf_curl, powdery_mildew, rust, bacterial_spot, healthy
- **Dataset**: 1,050 synthetic images
- **Expected Accuracy**: 85-95%

### 3. Soil Diagnostics
- **Type**: Image Classification (CNN)
- **Algorithm**: Custom CNN (3 Conv layers)
- **Input**: RGB image (224x224)
- **Output**: 6 soil types
- **Classes**: sandy, loamy, clay, silty, peaty, chalky
- **Dataset**: 720 synthetic images
- **Expected Accuracy**: 80-90%

### 4. Yield Prediction
- **Type**: Regression (Tabular Data)
- **Algorithm**: Random Forest Regressor
- **Input**: 14 features (area, soil quality, irrigation, fertilizer, climate, etc.)
- **Output**: Yield in tons/hectare
- **Dataset**: 1,000 synthetic records
- **Expected Performance**: R² > 0.85, RMSE < 2.0 tons/ha

### 5. Climate Prediction
- **Type**: Time Series Forecasting (LSTM)
- **Algorithm**: LSTM Neural Network
- **Input**: 30-day historical weather data (10 features)
- **Output**: 7-day temperature forecast
- **Dataset**: 730 daily records (2 years)
- **Expected Performance**: MAE < 2°C

## 🚀 Quick Start Guide

### Step 1: Generate Training Datasets

**From Frontend:**
1. Navigate to Home → AI Training (brain icon)
2. Tap "Generate Datasets" button
3. Wait 5-10 minutes for completion

**From Backend Terminal:**
```bash
cd backend
python generate_training_datasets.py
```

**Expected Output:**
- Creates `backend/training_data/` directory
- Generates 5,270 images and CSV files (~120MB)
- Total time: 5-10 minutes

### Step 2: Validate Datasets (Optional)

```bash
cd backend
python validate_datasets.py
```

### Step 3: Train Models

**From Frontend:**
1. Go to AI Training screen
2. Select a model (e.g., "Pest Detection")
3. Tap "Train" button
4. Monitor progress in real-time
5. View results when complete

**From Backend API:**
```bash
curl -X POST "https://urchin-app-86rjy.ondigitalocean.app/api/ml/train" \
  -H "Content-Type: application/json" \
  -d '{
    "model_type": "pest_detection",
    "epochs": 10
  }'
```

**Training Times:**
- Pest Detection: 10-15 minutes (10 epochs)
- Disease Detection: 10-15 minutes (10 epochs)
- Soil Diagnostics: 15-20 minutes (15 epochs)
- Yield Prediction: 2-3 minutes
- Climate Prediction: 15-20 minutes (20 epochs)

### Step 4: View Trained Models

**From Frontend:**
1. Tap "View Trained Models & Performance"
2. See accuracy metrics, training history
3. View model details and file sizes

**From Backend API:**
```bash
curl "https://urchin-app-86rjy.ondigitalocean.app/api/ml/models/summary"
```

## 📱 Frontend Screens

### ModelTrainingScreen.js
**Location**: `frontend/agroshield-app/src/screens/farmer/ModelTrainingScreen.js`

**Features:**
- Real-time training progress updates (polls every 5 seconds)
- Dataset generation trigger
- Model training trigger for each model type
- Visual progress bars
- Training status indicators

**Key Components:**
```javascript
// Generate datasets
handleGenerateDatasets()

// Start training
handleStartTraining(modelType)

// Poll status
useEffect(() => {
  const interval = setInterval(() => {
    if (trainingStatus?.status?.is_training) {
      fetchTrainingStatus();
    }
  }, 5000);
}, []);
```

### TrainedModelsScreen.js
**Location**: `frontend/agroshield-app/src/screens/farmer/TrainedModelsScreen.js`

**Features:**
- Display all trained models with accuracy metrics
- Training history timeline
- Model file sizes and paths
- Expandable model details
- Performance grading (Excellent, Good, Fair, etc.)

**Metrics Displayed:**
- Validation Accuracy (for classification models)
- R² Score (for regression models)
- Number of training samples
- Model file size
- Last training date

## 🔌 Backend API Endpoints

### Base URL
```
https://urchin-app-86rjy.ondigitalocean.app/api/ml
```

### 1. Generate Datasets
```http
POST /datasets/generate
Content-Type: application/json

{
  "force_regenerate": false
}
```

**Response:**
```json
{
  "success": true,
  "message": "Dataset generation started in background",
  "estimated_time": "5-10 minutes",
  "output_dir": "/path/to/training_data"
}
```

### 2. Check Dataset Status
```http
GET /datasets/status
```

**Response:**
```json
{
  "success": true,
  "all_datasets_ready": true,
  "datasets": {
    "pest_detection": {
      "available": true,
      "type": "image_dataset",
      "num_images": 1050,
      "path": "/path/to/pest_detection"
    }
  }
}
```

### 3. Start Training
```http
POST /train
Content-Type: application/json

{
  "model_type": "pest_detection",
  "epochs": 10
}
```

**Valid model_type values:**
- `pest_detection`
- `disease_detection`
- `soil_diagnostics`
- `yield_prediction`
- `climate_prediction`

**Response:**
```json
{
  "success": true,
  "message": "Training started for pest_detection",
  "model_type": "pest_detection",
  "epochs": 10,
  "started_at": "2025-10-28T10:30:00"
}
```

### 4. Check Training Status
```http
GET /training/status
```

**Response (Training Active):**
```json
{
  "success": true,
  "status": {
    "is_training": true,
    "current_model": "pest_detection",
    "progress": 45,
    "message": "Training for 10 epochs...",
    "start_time": "2025-10-28T10:30:00"
  }
}
```

**Response (Training Complete):**
```json
{
  "success": true,
  "status": {
    "is_training": false,
    "current_model": null,
    "progress": 100,
    "message": "Pest detection training completed!",
    "results": {
      "model_type": "pest_detection",
      "final_val_accuracy": 0.9234,
      "training_samples": 840,
      "validation_samples": 210
    }
  }
}
```

### 5. Get Models Summary
```http
GET /models/summary
```

**Response:**
```json
{
  "success": true,
  "total_models": 3,
  "summary": {
    "pest_detection": {
      "model_file": {
        "path": "/models/pest_detection_model.h5",
        "size_mb": 8.5,
        "modified": "2025-10-28T11:00:00"
      },
      "performance": {
        "accuracy": 0.9234,
        "trained_at": "2025-10-28T11:00:00",
        "training_samples": 840
      },
      "training_runs": 2
    }
  }
}
```

### 6. Get Training History
```http
GET /training/history?model_type=pest_detection
```

**Response:**
```json
{
  "success": true,
  "history": [
    {
      "model_type": "pest_detection",
      "timestamp": "2025-10-28T11:00:00",
      "results": {
        "final_accuracy": 0.8912,
        "final_val_accuracy": 0.9234,
        "epochs": 10,
        "num_classes": 7
      }
    }
  ],
  "total_runs": 1
}
```

### 7. Get Model Types Info
```http
GET /model-types
```

**Response:**
```json
{
  "success": true,
  "model_types": {
    "pest_detection": {
      "description": "Identifies pest types in crop images",
      "input": "RGB image (224x224)",
      "output": "7 pest classes + healthy",
      "algorithm": "MobileNetV3 + Transfer Learning",
      "dataset_size": "1,050 images"
    }
  }
}
```

## 🛠️ Technical Implementation

### Backend Files Created

1. **`backend/app/services/enhanced_model_training.py`** (700+ lines)
   - `EnhancedModelTrainingService` class
   - Training methods for all 5 models
   - Status tracking and history management
   - Model saving and loading

2. **`backend/app/routes/ml_training_routes.py`** (450+ lines)
   - All API endpoints
   - Background task management
   - Request/response models
   - Error handling

3. **`backend/generate_training_datasets.py`** (463 lines)
   - Synthetic dataset generation
   - PIL-based image creation
   - CSV generation for tabular data
   - Metadata tracking

4. **`backend/train_models_example.py`** (450+ lines)
   - Standalone training examples
   - Interactive CLI for model selection
   - Complete training workflows

### Frontend Files Created

1. **`frontend/agroshield-app/src/screens/farmer/ModelTrainingScreen.js`** (400+ lines)
   - Main training dashboard
   - Dataset generation UI
   - Model training triggers
   - Real-time progress tracking

2. **`frontend/agroshield-app/src/screens/farmer/TrainedModelsScreen.js`** (550+ lines)
   - Model performance dashboard
   - Training history timeline
   - Expandable model cards
   - Accuracy visualization

### Integration Points

**Navigation (`FarmStack.js`):**
```javascript
import ModelTrainingScreen from '../screens/farmer/ModelTrainingScreen';
import TrainedModelsScreen from '../screens/farmer/TrainedModelsScreen';

<Stack.Screen name="ModelTraining" component={ModelTrainingScreen} />
<Stack.Screen name="TrainedModels" component={TrainedModelsScreen} />
```

**Main App (`app/main.py`):**
```python
from app.routes import ml_training_routes

app.include_router(ml_training_routes.router)  # /api/ml
```

**Home Screen Quick Action:**
```javascript
<QuickActionButton
  icon="brain"
  label="AI Training"
  color="#9C27B0"
  onPress={() => navigation.navigate('FarmTab', { screen: 'ModelTraining' })}
/>
```

## 📈 Performance Optimization

### Backend

**Async Training:**
- Uses FastAPI BackgroundTasks for non-blocking training
- Training runs in separate threads
- Status polling every 5 seconds from frontend

**Model Caching:**
- Trained models saved to disk (.h5, .pkl)
- Class mappings saved as JSON
- Training history persisted

**Resource Management:**
- TensorFlow verbose=0 to reduce output
- Batch processing for image loading
- Validation splits to prevent overfitting

### Frontend

**Status Polling:**
```javascript
useEffect(() => {
  const interval = setInterval(() => {
    if (trainingStatus?.status?.is_training) {
      fetchTrainingStatus();
    }
  }, 5000);
  return () => clearInterval(interval);
}, [trainingStatus?.status?.is_training]);
```

**Efficient Rendering:**
- RefreshControl for pull-to-refresh
- Conditional rendering based on status
- ActivityIndicators for loading states

## 🔒 Security & Best Practices

1. **API Authentication**: Add JWT/OAuth to endpoints
2. **Rate Limiting**: Prevent abuse of expensive training operations
3. **Input Validation**: Pydantic models validate all requests
4. **Error Handling**: Try-catch blocks with user-friendly messages
5. **Resource Limits**: Set max epochs, timeout for training
6. **Storage Quotas**: Monitor disk space for models

## 🐛 Troubleshooting

### Dataset Generation Fails
```bash
# Check if script exists
ls backend/generate_training_datasets.py

# Run manually
cd backend
python generate_training_datasets.py
```

### Training Stuck at 0%
- Check backend logs for errors
- Verify datasets exist: `GET /api/ml/datasets/status`
- Restart backend server

### Frontend Not Showing Progress
- Ensure polling is active (check console logs)
- Verify API endpoint accessibility
- Check CORS configuration

### Model Accuracy Too Low
- Increase epochs (10 → 20+)
- Use data augmentation
- Collect more real-world data
- Fine-tune hyperparameters

## 📚 Next Steps

1. **Real-World Data**: Replace synthetic datasets with actual farm images
2. **Transfer Learning**: Use pre-trained models from TensorFlow Hub
3. **Hyperparameter Tuning**: Add UI for adjusting learning rate, batch size
4. **Model Versioning**: Track multiple versions of same model
5. **A/B Testing**: Compare model performance on real predictions
6. **Edge Deployment**: Export to TensorFlow Lite for mobile inference
7. **Continuous Learning**: Retrain models with new user data

## 🎓 Learning Resources

- [TensorFlow Documentation](https://www.tensorflow.org/guide)
- [Keras API Reference](https://keras.io/api/)
- [Scikit-learn User Guide](https://scikit-learn.org/stable/user_guide.html)
- [FastAPI Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- [React Navigation](https://reactnavigation.org/docs/getting-started)

## 📝 License & Credits

Built for AgroShield AI Platform
Training system implements state-of-the-art deep learning for agriculture
Uses open-source libraries: TensorFlow, Keras, scikit-learn, FastAPI, React Native
