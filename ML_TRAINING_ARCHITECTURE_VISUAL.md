# 🎨 ML Training System - Visual Architecture

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                         AGROSHIELD ML PIPELINE                       │
└──────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      PHASE 1: USER INTERACTION                      │
└─────────────────────────────────────────────────────────────────────┘

    📱 React Native App
        │
        │ 1. User uploads crop image
        ↓
    🖼️ Image Upload
        │
        │ 2. Image stored in Supabase Storage
        ↓
    ☁️ Supabase Storage (https://...supabase.co/storage/...)
        │
        │ 3. AI makes prediction
        ↓
    🤖 Current AI Model
        │
        │ 4. Prediction returned
        ↓
    📊 Result Display
        │
        │ 5. User confirms or corrects
        ↓
    ✅ User Feedback

┌─────────────────────────────────────────────────────────────────────┐
│                      PHASE 2: DATA STORAGE                          │
└─────────────────────────────────────────────────────────────────────┘

    ✅ User Feedback
        │
        │ 6. Store prediction + feedback
        ↓
    🗄️ Supabase PostgreSQL
        │
        ├── pest_predictions
        │   ├── id
        │   ├── image_url: "https://...supabase.co/storage/pest_123.jpg"
        │   ├── predicted_pest: "Aphids"
        │   ├── confidence: 0.85
        │   ├── user_confirmed: true
        │   ├── actual_pest: "Aphids" (or corrected)
        │   └── created_at
        │
        ├── disease_predictions
        │   └── (similar structure)
        │
        └── storage_predictions
            └── (similar structure)

┌─────────────────────────────────────────────────────────────────────┐
│                    PHASE 3: DATA COLLECTION                         │
└─────────────────────────────────────────────────────────────────────┘

    🗄️ Supabase PostgreSQL
        │
        │ 7. Data Collection Service fetches
        ↓
    📊 DataCollectionService
        │
        ├── fetch_pest_predictions()
        │   ├── Filter: user_confirmed = true
        │   ├── Filter: confidence > 0.7
        │   ├── Filter: last 90 days
        │   └── Result: 150 predictions
        │
        ├── fetch_pest_training_data()
        │   ├── Extract image URLs
        │   ├── Extract labels (actual_pest)
        │   ├── Format for training
        │   └── Result: {"image_urls": [...], "labels": [...]}
        │
        └── get_model_performance_metrics()
            ├── Calculate accuracy from feedback
            ├── Analyze pest distribution
            └── Result: {"accuracy": "85.5%", ...}

┌─────────────────────────────────────────────────────────────────────┐
│                    PHASE 4: MODEL TRAINING                          │
└─────────────────────────────────────────────────────────────────────┘

    📊 Training Data {"image_urls": [...], "labels": [...]}
        │
        │ 8. Model Training Service processes
        ↓
    🧠 ModelTrainingService
        │
        ├── download_and_preprocess_images()
        │   ├── Download from Supabase Storage
        │   ├── Resize to 224x224
        │   ├── Normalize pixel values
        │   └── Result: NumPy arrays
        │
        ├── build_classification_model()
        │   ├── Load MobileNetV2 (pretrained)
        │   ├── Add custom classification layers
        │   ├── Compile with Adam optimizer
        │   └── Result: TensorFlow model
        │
        ├── train_pest_detection_model()
        │   ├── Split train/validation (80/20)
        │   ├── Data augmentation (rotation, flip, zoom)
        │   ├── Train for 10 epochs
        │   ├── Early stopping callback
        │   ├── Model checkpoint callback
        │   └── Result: Trained model
        │
        └── Save Model
            ├── Path: models/pest_detection_20241215_150000.h5
            ├── Log: training_logs/pest_detection_training_20241215_150000.json
            └── Metrics: accuracy, loss, val_accuracy, val_loss

┌─────────────────────────────────────────────────────────────────────┐
│                    PHASE 5: MODEL DEPLOYMENT                        │
└─────────────────────────────────────────────────────────────────────┘

    💾 Trained Model (pest_detection_20241215_150000.h5)
        │
        │ 9. Deploy to production
        ↓
    🚀 Production API
        │
        ├── Load new model
        ├── Replace old model
        └── Start using for predictions
            │
            │ 10. Better predictions
            ↓
        📱 React Native App
            │
            │ 11. More accurate results
            ↓
        👨‍🌾 Happy Users
            │
            │ 12. More feedback (loop back to Phase 1)
            └─────────────────────────────────────┐
                                                   │
┌──────────────────────────────────────────────────┘
│  CONTINUOUS IMPROVEMENT LOOP
└────────────────────────────────────────────────────────────────────┐
                                                                     │
    Better predictions → More user trust → More feedback            │
         ↓                                                          │
    More confirmed data → Better training → Better models           │
         ↓                                                          │
    Cycle repeats weekly/monthly ──────────────────────────────────┘
```

## 📊 Data Flow Details

### 1. Prediction Storage Schema

```sql
CREATE TABLE pest_predictions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES profiles(id),
    image_url TEXT NOT NULL,              -- Supabase Storage URL
    predicted_pest VARCHAR(100),
    confidence DECIMAL(3,2),
    user_confirmed BOOLEAN DEFAULT FALSE, -- Key: User validates
    actual_pest VARCHAR(100),             -- Key: Corrected value
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 2. Training Data Format

```python
# Input from Supabase
[
    {
        "id": "uuid-1",
        "image_url": "https://...supabase.co/storage/pest_001.jpg",
        "predicted_pest": "Aphids",
        "user_confirmed": true,
        "actual_pest": "Aphids"
    },
    {
        "id": "uuid-2",
        "image_url": "https://...supabase.co/storage/pest_002.jpg",
        "predicted_pest": "Whiteflies",
        "user_confirmed": true,
        "actual_pest": "Whiteflies"
    },
    # ... 150 more samples
]

# Formatted for training
{
    "image_urls": [
        "https://...supabase.co/storage/pest_001.jpg",
        "https://...supabase.co/storage/pest_002.jpg",
        # ... 150 more URLs
    ],
    "labels": [
        "Aphids",
        "Whiteflies",
        # ... 150 more labels
    ],
    "metadata": [
        {"id": "uuid-1", "confidence": 0.85, "confirmed_at": "..."},
        {"id": "uuid-2", "confidence": 0.92, "confirmed_at": "..."},
        # ... 150 more metadata
    ]
}
```

### 3. Model Architecture

```
Input: 224x224x3 RGB Image
    ↓
┌────────────────────────────────────┐
│   MobileNetV2 Base                 │
│   (Pretrained on ImageNet)         │
│   - 53 convolutional layers        │
│   - Frozen weights (transfer learn)│
└────────────────────────────────────┘
    ↓
┌────────────────────────────────────┐
│   Global Average Pooling 2D        │
│   - Reduces spatial dimensions     │
└────────────────────────────────────┘
    ↓
┌────────────────────────────────────┐
│   Dense Layer (256 neurons)        │
│   - ReLU activation                │
│   - Batch Normalization            │
│   - Dropout (0.5)                  │
└────────────────────────────────────┘
    ↓
┌────────────────────────────────────┐
│   Dense Layer (128 neurons)        │
│   - ReLU activation                │
│   - Dropout (0.3)                  │
└────────────────────────────────────┘
    ↓
┌────────────────────────────────────┐
│   Output Layer (N classes)         │
│   - Softmax activation             │
│   - N = number of pest types       │
└────────────────────────────────────┘
    ↓
Output: Class probabilities [0.1, 0.7, 0.2, ...]
         (Predicted pest: max probability)
```

## 🔄 API Request Flow

### Training Request

```
Client/Script
    │
    │ POST /api/model-training/train
    │ {
    │   "model_type": "pest",
    │   "min_samples_per_class": 10,
    │   "validation_split": 0.2,
    │   "epochs": 10
    │ }
    ↓
FastAPI Router (model_training_routes.py)
    │
    │ 1. Validate request
    │ 2. Check if already training
    ↓
Background Task Started
    │
    ├── DataCollectionService.fetch_pest_training_data()
    │   └── Returns: {"image_urls": [...], "labels": [...]}
    │
    ├── ModelTrainingService.train_pest_detection_model()
    │   ├── Download images from URLs
    │   ├── Preprocess images
    │   ├── Build model
    │   ├── Train model (10 epochs)
    │   └── Save model file
    │
    └── Update training_status
        └── {"is_training": false, "completed_at": "..."}
```

### Monitoring Request

```
Client/Script
    │
    │ GET /api/model-training/training-status
    ↓
FastAPI Router
    │
    │ Return global training_status
    ↓
Response
{
    "success": true,
    "training_status": {
        "is_training": true,
        "model_type": "pest",
        "progress": "Training epoch 5/10...",
        "started_at": "2024-12-15T15:00:00",
        "current_epoch": 5,
        "total_epochs": 10
    }
}
```

## 📈 Performance Metrics Flow

```
Supabase Database
    │
    │ All predictions with feedback
    ↓
DataCollectionService.get_model_performance_metrics()
    │
    ├── Query: SELECT * FROM pest_predictions WHERE user_confirmed = true
    ├── Calculate: accuracy = correct_predictions / total_confirmed
    ├── Analyze: pest_distribution = COUNT(actual_pest) GROUP BY actual_pest
    └── Seasonal: pattern_analysis by month/season
        ↓
    Performance Report
    {
        "pest_detection": {
            "total_predictions": 150,
            "confirmed_predictions": 45,
            "correct_predictions": 38,
            "accuracy": "84.44%",
            "most_common_pests": [
                {"pest": "Aphids", "count": 15},
                {"pest": "Whiteflies", "count": 12},
                {"pest": "Caterpillars", "count": 10}
            ],
            "seasonal_patterns": {
                "Spring": {"Aphids": 8, "Whiteflies": 4},
                "Summer": {"Caterpillars": 6, "Beetles": 3}
            }
        }
    }
```

## 🛠️ Service Interaction Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      MAIN APPLICATION                       │
│                     (backend/app/main.py)                   │
└─────────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
            ↓               ↓               ↓
┌────────────────┐  ┌──────────────┐  ┌────────────────┐
│  Predict API   │  │ Training API │  │   Other APIs   │
│ /api/predict   │  │ /api/model-  │  │ /api/farms     │
│                │  │  training    │  │ /api/climate   │
└────────────────┘  └──────────────┘  └────────────────┘
                            │
            ┌───────────────┼───────────────┐
            ↓               ↓               ↓
┌────────────────┐  ┌──────────────┐  ┌────────────────┐
│ Data Collection│  │ Model Training│  │   Supabase     │
│    Service     │←→│    Service    │←→│    Client      │
│ data_collection│  │model_training│  │                │
│       .py      │  │      .py     │  │  (Database)    │
└────────────────┘  └──────────────┘  └────────────────┘
         ↑                   ↑                  ↑
         │                   │                  │
         │                   └──────────────────┤
         │                                      │
         └──────────────────────────────────────┘
                     Data Flow
```

## 🎯 Complete Workflow Example

### Week 1-2: Data Collection
```
Day 1: 10 users → 50 predictions → 10 confirmed (20%)
Day 2: 15 users → 75 predictions → 15 confirmed (20%)
...
Day 14: 20 users → 100 predictions → 20 confirmed (20%)

Total: 150 predictions, 45 confirmed (30%)
Distribution: Aphids(15), Whiteflies(12), Caterpillars(10), Others(8)
```

### Week 3: First Training
```
1. Check readiness:
   GET /api/model-training/data-stats
   ✅ 45 confirmed samples
   ✅ 15 samples for Aphids (>10)
   ✅ 12 samples for Whiteflies (>10)
   ✅ 10 samples for Caterpillars (>10)

2. Start training:
   POST /api/model-training/train
   {
     "model_type": "pest",
     "min_samples_per_class": 10,
     "epochs": 10
   }

3. Monitor progress:
   GET /api/model-training/training-status
   Progress: Epoch 1/10... Epoch 2/10... [Complete]

4. Check results:
   GET /api/model-training/training-history
   {
     "accuracy": 0.92,
     "val_accuracy": 0.85,
     "model_path": "models/pest_detection_20241215_150000.h5"
   }
```

### Week 4: Deployment & Monitoring
```
1. Deploy trained model to production
2. Monitor new predictions accuracy
3. Collect more feedback
4. Plan next retraining
```

## 🎨 Directory Structure Visual

```
agroshield/
│
├── 📄 ML_TRAINING_IMPLEMENTATION_SUMMARY.md  ← YOU ARE HERE
├── 📄 IMPLEMENTATION_CHECKLIST.md
├── 📄 ML_TRAINING_ARCHITECTURE_VISUAL.md
│
└── backend/
    │
    ├── app/
    │   ├── main.py  ← Routes registered here
    │   │
    │   ├── services/
    │   │   ├── data_collection.py      ← Fetch from Supabase
    │   │   └── model_training.py       ← Train TensorFlow models
    │   │
    │   └── routes/
    │       └── model_training_routes.py ← API endpoints
    │
    ├── models/                         ← Trained models saved here
    │   ├── pest_detection_20241215_150000.h5
    │   ├── disease_detection_20241215_160000.h5
    │   └── storage_assessment_20241215_170000.h5
    │
    ├── training_logs/                  ← Training logs saved here
    │   ├── pest_detection_training_20241215_150000.json
    │   └── ...
    │
    ├── 📄 MODEL_TRAINING_GUIDE.md       ← Complete guide
    ├── 📄 MODEL_TRAINING_QUICKSTART.md  ← Quick reference
    ├── 🐍 setup_model_training.py       ← Setup verification
    └── ⚡ test_model_training.bat        ← Interactive test
```

## 🚀 Quick Start Visual Guide

```
STEP 1: Install Dependencies
┌──────────────────────────────────┐
│ cd backend                       │
│ pip install -r requirements.txt │
└──────────────────────────────────┘
        ↓
STEP 2: Configure Environment
┌──────────────────────────────────┐
│ Create .env file:                │
│ SUPABASE_SERVICE_KEY=your-key    │
└──────────────────────────────────┘
        ↓
STEP 3: Verify Setup
┌──────────────────────────────────┐
│ python setup_model_training.py   │
│ ✅ All checks passed!            │
└──────────────────────────────────┘
        ↓
STEP 4: Start Server
┌──────────────────────────────────┐
│ python run_server.py             │
│ 🚀 Server running at :8000       │
└──────────────────────────────────┘
        ↓
STEP 5: Test Endpoints
┌──────────────────────────────────┐
│ test_model_training.bat          │
│ OR curl http://localhost:8000... │
└──────────────────────────────────┘
        ↓
STEP 6: Wait for Data
┌──────────────────────────────────┐
│ Collect user feedback            │
│ Wait for 100+ confirmed samples  │
└──────────────────────────────────┘
        ↓
STEP 7: Start Training
┌──────────────────────────────────┐
│ POST /api/model-training/train   │
│ Monitor progress                 │
│ Deploy trained model             │
└──────────────────────────────────┘
```

---

**🎉 You now have a complete visual understanding of the ML training system!**

See `IMPLEMENTATION_CHECKLIST.md` for step-by-step setup instructions.
