# ML Models Frontend Integration Guide

## Overview
The trained ML models are now fully connected to both frontend and backend through a centralized model management system.

## Backend Integration

### Model Manager (`backend/app/services/model_manager.py`)
Centralized singleton service that manages all 8 AI models:

```python
from app.services.model_manager import get_model_manager

# Get model manager instance
model_manager = get_model_manager()

# Load a model
model = model_manager.get_model("pest_detection")

# Get all models status
status = model_manager.list_available_models()

# Get system overview
overview = model_manager.get_system_status()
```

**Available Models:**
1. `pest_detection` - Identifies 7 common agricultural pests
2. `disease_detection` - Classifies 15 crop diseases
3. `soil_diagnostics` - Analyzes 10 soil health metrics
4. `yield_prediction` - Predicts crop yields
5. `climate_prediction` - Forecasts climate conditions
6. `storage_assessment` - Monitors stored crop quality
7. `plant_health` - Overall plant health assessment
8. `ai_calendar` - Smart farming calendar predictions

### API Endpoints (`/api/models/*`)

**1. System Status**
```bash
GET /api/models/status
```
Returns complete system status including all models, training data, and paths.

**2. List All Models**
```bash
GET /api/models/list
```
Returns list of all 8 models with availability status.

**3. Get Model Info**
```bash
GET /api/models/{model_name}/info
```
Returns detailed information about a specific model.

**4. Load Model**
```bash
POST /api/models/{model_name}/load
```
Manually loads a model into memory.

**5. Unload Model**
```bash
POST /api/models/{model_name}/unload
```
Unloads a model from memory to free resources.

**6. Training Data Status**
```bash
GET /api/models/training-data/status
```
Returns information about available training datasets.

**7. Health Check**
```bash
GET /api/models/health
```
Quick health check for the models system.

## Frontend Integration

### Service Layer (`frontend/.../services/mlModelsService.js`)

```javascript
import mlModelsService from './services/mlModelsService';

// Get all models status
const status = await mlModelsService.getModelsStatus();

// List available models
const models = await mlModelsService.listModels();

// Get specific model info
const pestModel = await mlModelsService.getModelInfo('pest_detection');

// Load a model
await mlModelsService.loadModel('pest_detection');

// Health check
const health = await mlModelsService.healthCheck();

// Get feature availability
const features = await mlModelsService.getFeatureAvailability();
```

### React Hooks (`frontend/.../hooks/useModelsStatus.js`)

**1. useModelsStatus Hook**
```javascript
import { useModelsStatus } from './hooks/useModelsStatus';

function MyComponent() {
  const { status, loading, error, refresh } = useModelsStatus();
  
  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;
  
  return (
    <View>
      <Text>Available Models: {status.summary.models_available}</Text>
      <Text>Loaded Models: {status.summary.models_loaded}</Text>
      <Button title="Refresh" onPress={refresh} />
    </View>
  );
}
```

**2. useModelInfo Hook**
```javascript
import { useModelInfo } from './hooks/useModelsStatus';

function PestDetectionScreen() {
  const { info, loading, error, loadModel } = useModelInfo('pest_detection');
  
  return (
    <View>
      {info && (
        <>
          <Text>Model: {info.name}</Text>
          <Text>Status: {info.loaded ? 'Ready' : 'Not Loaded'}</Text>
          <Text>Classes: {info.numClasses}</Text>
          {!info.loaded && (
            <Button title="Load Model" onPress={loadModel} />
          )}
        </>
      )}
    </View>
  );
}
```

**3. useFeatureAvailability Hook**
```javascript
import { useFeatureAvailability } from './hooks/useModelsStatus';

function FeaturesScreen() {
  const { features, loading } = useFeatureAvailability();
  
  return (
    <View>
      <Feature 
        name="Pest Detection" 
        available={features.pestDetection} 
      />
      <Feature 
        name="Disease Detection" 
        available={features.diseaseDetection} 
      />
      <Feature 
        name="Soil Diagnostics" 
        available={features.soilDiagnostics} 
      />
      {/* ... other features */}
    </View>
  );
}
```

## Usage Examples

### Example 1: Check Model Before Prediction
```javascript
// In your component
const handlePestDetection = async (image) => {
  try {
    // Check if model is available
    const modelInfo = await mlModelsService.getModelInfo('pest_detection');
    
    if (!modelInfo.available) {
      Alert.alert('Model Not Available', 'Pest detection model is not installed.');
      return;
    }
    
    if (!modelInfo.loaded) {
      // Load model first
      await mlModelsService.loadModel('pest_detection');
    }
    
    // Now make prediction
    const result = await pestDetectionService.predict(image);
    // ... handle result
    
  } catch (error) {
    console.error('Prediction failed:', error);
  }
};
```

### Example 2: Feature Flags Based on Model Availability
```javascript
function AppNavigator() {
  const { features, loading } = useFeatureAvailability();
  
  if (loading) return <LoadingScreen />;
  
  return (
    <Stack.Navigator>
      {features.pestDetection && (
        <Stack.Screen name="PestDetection" component={PestDetectionScreen} />
      )}
      {features.diseaseDetection && (
        <Stack.Screen name="DiseaseDetection" component={DiseaseScreen} />
      )}
      {features.soilDiagnostics && (
        <Stack.Screen name="SoilDiagnostics" component={SoilScreen} />
      )}
      {/* Only show features that have models available */}
    </Stack.Navigator>
  );
}
```

### Example 3: System Status Dashboard
```javascript
function AdminDashboard() {
  const { status, loading, refresh } = useModelsStatus();
  
  return (
    <ScrollView>
      <Card>
        <Title>ML Models Status</Title>
        <Text>Total Models: {status?.summary.total_models}</Text>
        <Text>Available: {status?.summary.models_available}</Text>
        <Text>Loaded: {status?.summary.models_loaded}</Text>
      </Card>
      
      <Card>
        <Title>Individual Models</Title>
        {Object.entries(status?.models || {}).map(([name, info]) => (
          <View key={name}>
            <Text>{name}</Text>
            <Text>Status: {info.available ? 'Available' : 'Not Found'}</Text>
            <Text>Loaded: {info.loaded ? 'Yes' : 'No'}</Text>
          </View>
        ))}
      </Card>
      
      <Button title="Refresh Status" onPress={refresh} />
    </ScrollView>
  );
}
```

## Testing Integration

### Backend Test
```bash
# Start backend
cd backend
python run_dev.py

# Test endpoints
curl http://localhost:8000/api/models/status
curl http://localhost:8000/api/models/list
curl http://localhost:8000/api/models/pest_detection/info
```

### Frontend Test
```bash
# Run integration test
node test_model_integration.js

# Expected output:
# [1/6] Testing health check... [PASS]
# [2/6] Listing all models... [PASS]
# [3/6] Getting system status... [PASS]
# [4/6] Getting pest detection model info... [PASS]
# [5/6] Getting training data status... [PASS]
# [6/6] Testing model loading... [PASS]
# ALL TESTS PASSED
```

## Model Loading Strategy

### Lazy Loading (Default)
Models are loaded only when first requested:
```python
# Backend automatically loads on first prediction
model = model_manager.get_model("pest_detection")  # Loads if not already loaded
```

### Preloading (Optional)
Load models at startup for faster predictions:
```python
# In backend startup
@app.on_event("startup")
async def preload_models():
    model_manager = get_model_manager()
    model_manager.get_model("pest_detection")
    model_manager.get_model("disease_detection")
```

### Frontend Preloading
```javascript
// Load critical models when app starts
useEffect(() => {
  const preloadModels = async () => {
    await mlModelsService.loadModel('pest_detection');
    await mlModelsService.loadModel('disease_detection');
  };
  preloadModels();
}, []);
```

## Training Data Integration

All trained models use data from two sources:

### 1. Public API Data (`training_data_public/`)
- PlantVillage: 54,000+ disease images
- iNaturalist: 500+ pest observations
- FAO SoilGrids: Global soil data
- OpenWeatherMap: Climate data
- GBIF: Species occurrences

### 2. Synthetic Data (`training_data/`)
- Generated by `generate_training_datasets.py`
- Augmented and labeled data
- Covers edge cases and rare scenarios

### Check Training Data Status
```javascript
const trainingStatus = await mlModelsService.getTrainingDataStatus();
console.log(trainingStatus.syntheticData.total_files);
console.log(trainingStatus.publicData.total_files);
```

## Error Handling

### Backend Error Handling
```python
try:
    model = model_manager.get_model("pest_detection")
except FileNotFoundError:
    # Model file not found
    return {"error": "Model not trained yet"}
except Exception as e:
    # Loading error
    return {"error": f"Failed to load model: {str(e)}"}
```

### Frontend Error Handling
```javascript
try {
  const result = await mlModelsService.getModelInfo('pest_detection');
} catch (error) {
  if (error.message.includes('not found')) {
    // Model not available
    Alert.alert('Feature Unavailable', 'This AI feature is not yet available.');
  } else {
    // Network or other error
    Alert.alert('Error', 'Failed to connect to AI service.');
  }
}
```

## Performance Optimization

### Memory Management
```python
# Unload unused models to free memory
model_manager.unload_model("storage_assessment")

# Backend automatically caches loaded models
# Second call to get_model() returns cached instance
```

### Batch Predictions
```python
# Use batch prediction for multiple images
results = []
for image in images:
    result = await predict_pest(image)
    results.append(result)
```

### Frontend Caching
```javascript
// Cache model status for 5 minutes
const [cachedStatus, setCachedStatus] = useState(null);
const [cacheTime, setCacheTime] = useState(null);

const getStatus = async () => {
  const now = Date.now();
  if (cachedStatus && cacheTime && now - cacheTime < 300000) {
    return cachedStatus;
  }
  
  const status = await mlModelsService.getModelsStatus();
  setCachedStatus(status);
  setCacheTime(now);
  return status;
};
```

## Next Steps

1. **Train Models**: Run `python backend/master_train_models.py --all` to train all models
2. **Verify Backend**: Start backend and test `/api/models/status`
3. **Test Frontend**: Run `node test_model_integration.js`
4. **Update UI**: Add model status indicators to your app screens
5. **Deploy**: Follow deployment guide to push to production

## Troubleshooting

**Problem**: Models showing as "not available"
- **Solution**: Run training pipeline: `python backend/master_train_models.py --all`

**Problem**: Frontend can't connect to models API
- **Solution**: Check `API_BASE_URL` in `frontend/src/services/config.js`

**Problem**: Model loading fails
- **Solution**: Check model files exist in `backend/trained_models/`

**Problem**: Out of memory errors
- **Solution**: Unload unused models or increase system RAM

## Support

For issues or questions:
1. Check model status: `GET /api/models/status`
2. Review logs in `backend/app.log`
3. Verify training data exists in `training_data/` and `training_data_public/`
