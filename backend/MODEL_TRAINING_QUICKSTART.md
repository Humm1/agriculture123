# Model Training Quick Reference

## 🚀 Quick Commands

### Setup & Installation
```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Run setup verification
python setup_model_training.py

# Set environment variable (Windows CMD)
set SUPABASE_SERVICE_KEY=your-service-role-key-here

# Set environment variable (PowerShell)
$env:SUPABASE_SERVICE_KEY="your-service-role-key-here"
```

### Start Server
```bash
# Start backend server
python run_server.py

# Server will run at: http://localhost:8000
# API docs: http://localhost:8000/docs
```

### Check System Status
```bash
# Check available training data
curl http://localhost:8000/api/model-training/data-stats

# Check data distribution
curl http://localhost:8000/api/model-training/data-distribution

# Check model performance
curl http://localhost:8000/api/model-training/model-performance

# Health check
curl http://localhost:8000/api/model-training/health
```

### Train Models
```bash
# Train pest detection model
curl -X POST "http://localhost:8000/api/model-training/train" ^
  -H "Content-Type: application/json" ^
  -d "{\"model_type\": \"pest\", \"epochs\": 10}"

# Train disease detection model
curl -X POST "http://localhost:8000/api/model-training/train" ^
  -H "Content-Type: application/json" ^
  -d "{\"model_type\": \"disease\", \"epochs\": 10}"

# Train storage assessment model
curl -X POST "http://localhost:8000/api/model-training/train" ^
  -H "Content-Type: application/json" ^
  -d "{\"model_type\": \"storage\", \"epochs\": 10}"

# Train all models
curl -X POST "http://localhost:8000/api/model-training/train" ^
  -H "Content-Type: application/json" ^
  -d "{\"model_type\": \"all\", \"epochs\": 10}"
```

### Monitor Training
```bash
# Check training status
curl http://localhost:8000/api/model-training/training-status

# View training history
curl http://localhost:8000/api/model-training/training-history

# View specific model history
curl "http://localhost:8000/api/model-training/training-history?model_type=pest"
```

### Export Data
```bash
# Export pest training data to CSV
curl -X POST "http://localhost:8000/api/model-training/export-training-data?prediction_type=pest&format=csv"

# Export disease data to JSON
curl -X POST "http://localhost:8000/api/model-training/export-training-data?prediction_type=disease&format=json"

# Export all data
curl -X POST "http://localhost:8000/api/model-training/export-all-data?format=csv"
```

### Evaluate Models
```bash
# Evaluate pest detection model
curl -X POST "http://localhost:8000/api/model-training/evaluate?model_type=pest"

# Evaluate disease detection model
curl -X POST "http://localhost:8000/api/model-training/evaluate?model_type=disease"
```

## 📊 API Response Examples

### Data Stats Response
```json
{
  "success": true,
  "statistics": {
    "total_predictions": {
      "pest": 150,
      "disease": 75,
      "storage": 50,
      "total": 275
    },
    "confirmed_training_data": {
      "pest": 45,
      "disease": 30,
      "storage": 20,
      "total": 95
    },
    "data_quality": {
      "pest_confirmation_rate": "30.00%",
      "disease_confirmation_rate": "40.00%",
      "storage_confirmation_rate": "40.00%"
    },
    "date_range": {
      "oldest_prediction": "2024-11-01T10:30:00",
      "newest_prediction": "2024-12-15T14:20:00"
    }
  }
}
```

### Training Status Response
```json
{
  "success": true,
  "training_status": {
    "is_training": true,
    "model_type": "pest",
    "progress": "Training in progress...",
    "started_at": "2024-12-15T15:00:00",
    "current_epoch": 5,
    "total_epochs": 10,
    "estimated_time_remaining": "5 minutes"
  }
}
```

### Model Performance Response
```json
{
  "success": true,
  "performance": {
    "pest_detection": {
      "total_predictions": 150,
      "confirmed_predictions": 45,
      "accuracy": "85.50%",
      "most_common_pests": ["Aphids", "Whiteflies", "Caterpillars"]
    },
    "disease_detection": {
      "total_predictions": 75,
      "confirmed_predictions": 30,
      "accuracy": "82.30%",
      "most_common_diseases": ["Late Blight", "Powdery Mildew"]
    },
    "storage_assessment": {
      "total_predictions": 50,
      "confirmed_predictions": 20,
      "accuracy": "88.00%"
    }
  }
}
```

## 🐍 Python Script Examples

### Check Data Availability
```python
from app.services.data_collection import DataCollectionService

service = DataCollectionService()

# Get statistics
metrics = service.get_model_performance_metrics()
print(f"Total predictions: {metrics['total_predictions']}")
print(f"Pest accuracy: {metrics['pest_detection']['accuracy']}")

# Get pest distribution
distribution = service.get_pest_distribution()
print(f"Pest types: {distribution}")
```

### Train Model
```python
from app.services.model_training import ModelTrainingService

service = ModelTrainingService()

# Train pest detection model
results = service.train_pest_detection_model(
    min_samples_per_class=10,
    validation_split=0.2,
    epochs=10,
    batch_size=32
)

print(f"Training completed!")
print(f"Final accuracy: {results['val_accuracy'][-1]}")
print(f"Model saved to: {results['model_path']}")
```

### Export Training Data
```python
from app.services.data_collection import DataCollectionService

service = DataCollectionService()

# Export to CSV
file_path = service.export_training_dataset(
    prediction_type='pest',
    format='csv'
)
print(f"Data exported to: {file_path}")
```

## 📝 Training Configuration

### Recommended Settings

**Initial Training** (100-500 samples):
```json
{
  "model_type": "pest",
  "min_samples_per_class": 10,
  "validation_split": 0.2,
  "epochs": 10,
  "batch_size": 32,
  "learning_rate": 0.001
}
```

**Regular Retraining** (500-1000 samples):
```json
{
  "model_type": "pest",
  "min_samples_per_class": 15,
  "validation_split": 0.15,
  "epochs": 15,
  "batch_size": 64,
  "learning_rate": 0.0005
}
```

**Production Training** (1000+ samples):
```json
{
  "model_type": "pest",
  "min_samples_per_class": 20,
  "validation_split": 0.15,
  "epochs": 20,
  "batch_size": 128,
  "learning_rate": 0.0001
}
```

## 🔧 Troubleshooting

### Error: "No training data available"
```bash
# Check if predictions exist
curl http://localhost:8000/api/model-training/data-stats

# Verify Supabase connection
python -c "from app.services.data_collection import DataCollectionService; print(DataCollectionService().supabase)"
```

### Error: "Not enough samples per class"
```bash
# Lower the minimum samples requirement
curl -X POST "http://localhost:8000/api/model-training/train" ^
  -H "Content-Type: application/json" ^
  -d "{\"model_type\": \"pest\", \"min_samples_per_class\": 5, \"epochs\": 10}"
```

### Error: "TensorFlow not found"
```bash
# Install TensorFlow
pip install tensorflow==2.15.0

# Verify installation
python -c "import tensorflow as tf; print(tf.__version__)"
```

### Error: "SUPABASE_SERVICE_KEY not set"
```bash
# Windows CMD
set SUPABASE_SERVICE_KEY=your-key-here

# PowerShell
$env:SUPABASE_SERVICE_KEY="your-key-here"

# Or add to .env file
echo SUPABASE_SERVICE_KEY=your-key-here >> .env
```

## 📁 File Locations

- **Models**: `backend/models/`
- **Training Logs**: `backend/training_logs/`
- **Uploaded Images**: `backend/uploads/`
- **Services**: `backend/app/services/`
- **API Routes**: `backend/app/routes/model_training_routes.py`

## 🔐 Security

### Environment Variables Required
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_KEY=your-service-role-key-here
```

**Important**: 
- Use **Service Role Key** in backend (full database access)
- Use **Anon Key** in frontend (restricted by RLS policies)
- Never commit keys to version control

## 📞 Support

For detailed documentation, see:
- `MODEL_TRAINING_GUIDE.md` - Complete setup guide
- `http://localhost:8000/docs` - Interactive API documentation
- `backend/app/services/data_collection.py` - Data collection code
- `backend/app/services/model_training.py` - Model training code

## ✅ Pre-Training Checklist

Before training models, verify:
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Environment variables set (SUPABASE_SERVICE_KEY)
- [ ] Supabase connection working
- [ ] At least 100 predictions in database
- [ ] At least 10 confirmed predictions per class
- [ ] User confirmation rate > 20%
- [ ] Backend server running
- [ ] Models directory exists

## 🎯 Success Metrics

Track these metrics after each training:
- **Training Accuracy**: Should be > 90%
- **Validation Accuracy**: Should be > 80%
- **Confirmation Rate**: Should increase over time
- **Model Size**: Should be < 100 MB
- **Inference Time**: Should be < 2 seconds

## 🔄 Continuous Improvement Cycle

```
Week 1: Collect user feedback (100+ samples)
Week 2: Train initial models
Week 3: Deploy and monitor accuracy
Week 4: Collect more feedback
Week 5: Retrain with larger dataset
Week 6: Compare accuracy improvements
```

Repeat monthly for continuous improvement!
