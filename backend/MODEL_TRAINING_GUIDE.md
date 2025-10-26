# Supabase-Integrated Model Training System

## Overview
This system automatically fetches prediction data from your Supabase database and uses it to continuously improve your AI models for pest detection, disease detection, and storage assessment.

## 🏗️ Architecture

```
┌─────────────────┐
│   Supabase DB   │
│  (Predictions)  │
└────────┬────────┘
         │
         │ Fetch Data
         ▼
┌─────────────────────┐
│ Data Collection     │
│ Service             │
│ - Pest predictions  │
│ - Disease predictions│
│ - Storage predictions│
└────────┬────────────┘
         │
         │ Prepare Training Data
         ▼
┌─────────────────────┐
│ Model Training      │
│ Service             │
│ - Download images   │
│ - Preprocess data   │
│ - Train models      │
│ - Evaluate          │
└────────┬────────────┘
         │
         │ Save Models
         ▼
┌─────────────────────┐
│ Trained Models      │
│ - pest_detection.h5 │
│ - disease_detection.h5│
│ - storage_assessment.h5│
└─────────────────────┘
```

## 📋 Prerequisites

### 1. Install Dependencies

Add to `backend/requirements.txt`:
```txt
supabase-py==2.3.4
tensorflow==2.15.0
pandas==2.1.4
numpy==1.26.2
pillow==10.1.0
requests==2.31.0
```

Install:
```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create/update `backend/.env`:
```env
# Supabase Configuration
SUPABASE_URL=https://rwspbvgmmxabglptljkg.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_KEY=your-service-role-key-here  # Important: Use service role key for backend

# API Configuration
API_BASE_URL=https://urchin-app-86rjy.ondigitalocean.app
```

**⚠️ Security Note:** 
- Use **Service Role Key** in backend (has full database access)
- Use **Anon Key** in frontend (restricted by RLS policies)
- Never commit keys to git!

## 🚀 Quick Start

### 1. Run Data Collection Script

Test data fetching:
```bash
cd backend
python -m app.services.data_collection
```

Expected output:
```
📊 Fetching pest predictions from last 30 days...
✅ Fetched 150 pest predictions
📊 Fetching disease predictions from last 30 days...
✅ Fetched 75 disease predictions
...
```

### 2. Check Training Data Availability

```bash
curl http://localhost:8000/api/model-training/data-stats
```

Response:
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
    }
  }
}
```

### 3. Start Model Training

#### Via API:
```bash
# Train pest detection model
curl -X POST "http://localhost:8000/api/model-training/train" \
  -H "Content-Type: application/json" \
  -d '{
    "model_type": "pest",
    "min_samples_per_class": 10,
    "validation_split": 0.2,
    "epochs": 10
  }'
```

#### Via Python Script:
```bash
cd backend
python -m app.services.model_training pest
```

#### Train all models:
```bash
python -m app.services.model_training all
```

### 4. Check Training Status

```bash
curl http://localhost:8000/api/model-training/training-status
```

### 5. View Model Performance

```bash
curl http://localhost:8000/api/model-training/model-performance
```

## 📊 API Endpoints

### Data Statistics

#### GET `/api/model-training/data-stats`
Get statistics about available training data

**Response:**
```json
{
  "success": true,
  "statistics": {
    "total_predictions": {...},
    "confirmed_training_data": {...},
    "data_quality": {
      "pest_confirmation_rate": "30.00%",
      "disease_confirmation_rate": "40.00%",
      "storage_confirmation_rate": "40.00%"
    }
  }
}
```

#### GET `/api/model-training/data-distribution`
Get distribution of detected pests, diseases, etc.

#### GET `/api/model-training/model-performance`
Get current model accuracy metrics

### Model Training

#### POST `/api/model-training/train`
Start model training

**Request Body:**
```json
{
  "model_type": "pest|disease|storage|all",
  "min_samples_per_class": 10,
  "validation_split": 0.2,
  "epochs": 10
}
```

#### GET `/api/model-training/training-status`
Check current training progress

#### GET `/api/model-training/training-history`
View past training runs

**Optional Query Parameter:**
- `model_type`: Filter by specific model type

### Data Export

#### POST `/api/model-training/export-training-data`
Export training data to file

**Query Parameters:**
- `prediction_type`: pest|disease|storage
- `format`: csv|json|parquet

#### POST `/api/model-training/export-all-data`
Export all training datasets

### Model Evaluation

#### POST `/api/model-training/evaluate`
Evaluate trained model

**Query Parameter:**
- `model_type`: pest|disease|storage

## 🔄 How It Works

### 1. Data Collection Flow

```python
from app.services.data_collection import DataCollectionService

service = DataCollectionService()

# Fetch predictions from Supabase
pest_data = service.fetch_pest_training_data()
# Returns: {"image_urls": [...], "labels": [...], "metadata": [...]}

# Get performance metrics
metrics = service.get_model_performance_metrics()
# Shows accuracy based on user feedback
```

### 2. Model Training Flow

```python
from app.services.model_training import ModelTrainingService

service = ModelTrainingService()

# Train model with Supabase data
results = service.train_pest_detection_model(
    min_samples_per_class=10,
    validation_split=0.2
)

# Model is saved to backend/models/pest_detection_YYYYMMDD_HHMMSS.h5
```

### 3. User Feedback Loop

When users interact with predictions:

1. **User uploads image** → AI makes prediction
2. **Prediction stored** in Supabase with image URL
3. **User confirms/corrects** → `user_confirmed` and `actual_pest` fields updated
4. **Data collection service** fetches confirmed predictions
5. **Model training** uses corrected labels
6. **Improved model** deployed to production

## 📈 Continuous Improvement Cycle

```
┌─────────────────────────────────────────────┐
│                                             │
│  1. Users upload images                     │
│     ↓                                       │
│  2. AI makes predictions                    │
│     ↓                                       │
│  3. Predictions stored in Supabase          │
│     ↓                                       │
│  4. Users provide feedback                  │
│     ↓                                       │
│  5. System collects confirmed data          │
│     ↓                                       │
│  6. Retrain models weekly/monthly          │
│     ↓                                       │
│  7. Deploy improved models                  │
│     ↓                                       │
│  8. Better predictions for users  ──────────┘
│                                             
└─────────────────────────────────────────────┘
```

## 🎯 Training Best Practices

### Minimum Data Requirements

- **Pest Detection**: 10+ samples per pest type
- **Disease Detection**: 10+ samples per disease
- **Storage Assessment**: 10+ samples per condition level

### Recommended Training Schedule

- **Initial Training**: When you have 100+ confirmed samples
- **Regular Retraining**: Monthly or when 50+ new samples collected
- **Emergency Retraining**: When accuracy drops below 80%

### Data Quality Checks

Before training, verify:
```bash
# Check data stats
curl http://localhost:8000/api/model-training/data-stats

# Check distribution
curl http://localhost:8000/api/model-training/data-distribution

# Check performance metrics
curl http://localhost:8000/api/model-training/model-performance
```

Ensure:
- ✅ At least 10 samples per class
- ✅ Balanced distribution (no class dominates)
- ✅ User confirmation rate > 20%
- ✅ Current model accuracy > 70%

## 🔧 Integrating with Main API

Update `backend/main.py`:

```python
from fastapi import FastAPI
from app.routes import model_training_routes

app = FastAPI()

# Include model training routes
app.include_router(model_training_routes.router)

# Other routes...
```

## 📝 Scheduled Training (Optional)

### Using Cron (Linux/Mac)

Add to crontab:
```bash
# Train models every Sunday at 2 AM
0 2 * * 0 cd /path/to/backend && python -m app.services.model_training all

# Check data quality daily
0 8 * * * curl http://localhost:8000/api/model-training/data-stats
```

### Using Task Scheduler (Windows)

Create a scheduled task:
```powershell
$action = New-ScheduledTaskAction -Execute 'python' -Argument '-m app.services.model_training all' -WorkingDirectory 'C:\path\to\backend'
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 2am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "AgroShield Model Training"
```

## 🐛 Troubleshooting

### Issue: "No training data available"

**Solution:**
1. Check Supabase connection:
   ```python
   from app.services.data_collection import DataCollectionService
   service = DataCollectionService()
   print(service.supabase.table('pest_predictions').select('count').execute())
   ```

2. Verify predictions exist in database
3. Check that users are confirming predictions

### Issue: "Not enough samples per class"

**Solution:**
- Lower `min_samples_per_class` parameter
- Wait for more user feedback
- Encourage users to confirm predictions

### Issue: "Model training fails"

**Solution:**
1. Check TensorFlow installation:
   ```bash
   python -c "import tensorflow as tf; print(tf.__version__)"
   ```

2. Verify image URLs are accessible
3. Check disk space for model files
4. Review logs in `backend/training_logs/`

### Issue: "Supabase connection timeout"

**Solution:**
1. Verify `SUPABASE_SERVICE_KEY` is correct
2. Check network connectivity
3. Verify Supabase project is active

## 📊 Monitoring & Metrics

### Key Metrics to Track

1. **Data Collection**:
   - Total predictions per day/week
   - User confirmation rate
   - Data quality score

2. **Model Performance**:
   - Training accuracy
   - Validation accuracy
   - Test accuracy (on new data)
   - Confidence scores

3. **System Health**:
   - API response times
   - Training duration
   - Storage usage

### Logging

Training logs are saved to:
- `backend/training_logs/pest_detection_training_YYYYMMDD_HHMMSS.json`
- `backend/training_logs/disease_detection_training_YYYYMMDD_HHMMSS.json`
- `backend/training_logs/storage_assessment_training_YYYYMMDD_HHMMSS.json`

Each log contains:
- Training/validation accuracy
- Loss values
- Class distribution
- Model configuration
- Timestamp

## 🚀 Production Deployment

### 1. Environment Setup

```bash
# Production environment variables
export SUPABASE_SERVICE_KEY="prod-service-key"
export MODEL_TRAINING_ENABLED=true
export AUTO_RETRAIN_SCHEDULE="0 2 * * 0"  # Weekly Sunday 2 AM
```

### 2. Deploy to DigitalOcean

Your app is already deployed. Just add the new endpoint:

```bash
# The model training routes will be available at:
https://urchin-app-86rjy.ondigitalocean.app/api/model-training/
```

### 3. Monitor Training

Set up monitoring dashboard to track:
- Training completion status
- Model accuracy trends
- Data collection rate
- System resource usage

## 📚 Next Steps

1. **Integrate into main app**:
   - Add model training routes to FastAPI
   - Update requirements.txt
   - Redeploy backend

2. **Start collecting data**:
   - Ensure predictions are being stored
   - Encourage user feedback
   - Monitor data quality

3. **First training run**:
   - Wait for 100+ confirmed samples
   - Run initial training
   - Evaluate results
   - Deploy improved model

4. **Set up automation**:
   - Schedule weekly retraining
   - Set up monitoring alerts
   - Create backup strategy for models

## ✅ Success Checklist

- [ ] Dependencies installed
- [ ] Environment variables configured
- [ ] Supabase connection tested
- [ ] Data collection working
- [ ] API endpoints accessible
- [ ] Training script runs successfully
- [ ] Models saved correctly
- [ ] Performance metrics calculated
- [ ] Scheduled training configured
- [ ] Monitoring dashboard set up

Your AI models will now continuously improve as users interact with the system! 🎉
