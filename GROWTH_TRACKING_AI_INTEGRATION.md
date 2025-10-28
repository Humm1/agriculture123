# Growth Tracking AI Integration Guide

## Overview
The growth tracking feature now has full integration with the centralized ML models system, providing AI-powered analysis for soil, plant health, pests, diseases, yield prediction, and more.

## Architecture

### Backend Integration

**Service Layer** (`backend/app/services/advanced_growth_tracking.py`):
- Connected to centralized `MLModelManager`
- Lazy loads models on-demand
- Falls back to rule-based analysis if models unavailable

**API Endpoints** (`backend/app/routes/advanced_growth_routes.py`):
- Base URL: `/api/advanced-growth/ai`
- 4 new endpoints for AI feature management

### Frontend Integration

**Service Layer** (`frontend/.../services/growthTrackingAI.js`):
- Wrapper for growth tracking AI API calls
- Feature availability checking
- Model loading management

**React Hooks** (`frontend/.../hooks/useGrowthAI.js`):
- `useGrowthAIStatus()` - Overall AI status
- `useFeatureAvailable(feature)` - Check single feature
- `useFeatureInfo(feature)` - Detailed feature info
- `useAvailableFeatures()` - List all available features
- `useGrowthFeatureFlags()` - UI feature flags

## API Endpoints

### 1. Get AI Models Status
```bash
GET /api/advanced-growth/ai/models/status
```

**Response:**
```json
{
  "success": true,
  "models_available": true,
  "features": {
    "soil_analysis": true,
    "plant_health": true,
    "pest_detection": true,
    "disease_detection": true,
    "yield_prediction": false,
    "growth_prediction": true,
    "storage_assessment": false
  },
  "summary": {
    "total_features": 7,
    "available_features": 5,
    "percentage_ready": 71.4
  },
  "message": "5/7 AI features available"
}
```

### 2. Get Feature Info
```bash
GET /api/advanced-growth/ai/models/{feature}/info
```

**Supported Features:**
- `soil_analysis`
- `plant_health`
- `pest_detection`
- `disease_detection`
- `yield_prediction`
- `growth_prediction`
- `storage_assessment`

**Response:**
```json
{
  "success": true,
  "feature": "pest_detection",
  "model_name": "pest_detection",
  "available": true,
  "loaded": false,
  "type": "tensorflow",
  "description": "Identifies 7 common agricultural pests",
  "capabilities": [
    "Identify 7+ common agricultural pests",
    "Severity assessment (Low/Medium/High)",
    "Confidence scoring",
    "Treatment recommendations",
    "Regional risk factors"
  ]
}
```

### 3. Load Feature Model
```bash
POST /api/advanced-growth/ai/models/{feature}/load
```

Preloads a model into memory for faster predictions.

**Response:**
```json
{
  "success": true,
  "feature": "pest_detection",
  "model_name": "pest_detection",
  "loaded": true,
  "message": "Model loaded successfully for pest_detection"
}
```

### 4. Get Available Features
```bash
GET /api/advanced-growth/ai/features/available
```

Quick endpoint to check which features are ready.

**Response:**
```json
{
  "success": true,
  "available_features": [
    "soil_analysis",
    "plant_health",
    "pest_detection",
    "disease_detection",
    "growth_prediction"
  ],
  "count": 5,
  "percentage_ready": 71.4
}
```

## Frontend Usage

### Example 1: Check AI Status on Screen Load

```javascript
import { useGrowthAIStatus } from '../hooks/useGrowthAI';

function GrowthTrackingScreen() {
  const { status, loading, error } = useGrowthAIStatus();
  
  if (loading) return <LoadingSpinner />;
  
  return (
    <View>
      <Text>AI Features Ready: {status.summary.percentage_ready}%</Text>
      <Text>
        {status.summary.available_features}/{status.summary.total_features} features available
      </Text>
      
      {status.features.soil_analysis && (
        <Button title="Analyze Soil" onPress={handleSoilAnalysis} />
      )}
      
      {status.features.pest_detection && (
        <Button title="Detect Pests" onPress={handlePestDetection} />
      )}
    </View>
  );
}
```

### Example 2: Feature Flags for Conditional UI

```javascript
import { useGrowthFeatureFlags } from '../hooks/useGrowthAI';

function PlotActionsMenu({ plotId }) {
  const { flags, loading } = useGrowthFeatureFlags();
  
  return (
    <View>
      {flags.canAnalyzeSoil && (
        <ActionButton 
          icon="🌱"
          title="Soil Analysis"
          onPress={() => analyzeSoil(plotId)}
        />
      )}
      
      {flags.canCheckHealth && (
        <ActionButton 
          icon="🌿"
          title="Health Check"
          onPress={() => checkHealth(plotId)}
        />
      )}
      
      {flags.canDetectPests && (
        <ActionButton 
          icon="🐛"
          title="Pest Detection"
          onPress={() => detectPests(plotId)}
        />
      )}
      
      {flags.canPredictYield && (
        <ActionButton 
          icon="📊"
          title="Yield Forecast"
          onPress={() => predictYield(plotId)}
        />
      )}
      
      {!flags.aiEnabled && (
        <Text style={styles.notice}>
          AI features not available - using rule-based analysis
        </Text>
      )}
    </View>
  );
}
```

### Example 3: Load Model Before Analysis

```javascript
import { useFeatureInfo } from '../hooks/useGrowthAI';

function PestDetectionScreen() {
  const { info, loading, loadModel } = useFeatureInfo('pest_detection');
  const [analyzing, setAnalyzing] = useState(false);
  
  const handleDetectPests = async (image) => {
    try {
      // Load model if not already loaded
      if (info && !info.loaded) {
        await loadModel();
      }
      
      setAnalyzing(true);
      // Now perform detection
      const result = await pestDetectionAPI.analyze(image);
      // ... handle result
    } finally {
      setAnalyzing(false);
    }
  };
  
  return (
    <View>
      {info && (
        <>
          <Text>Model: {info.modelName}</Text>
          <Text>Status: {info.loaded ? 'Ready' : 'Not Loaded'}</Text>
          <Text>Capabilities:</Text>
          {info.capabilities.map(cap => (
            <Text key={cap}>• {cap}</Text>
          ))}
        </>
      )}
      
      <Button 
        title="Detect Pests" 
        onPress={() => handleDetectPests(selectedImage)}
        disabled={!info?.available || analyzing}
      />
    </View>
  );
}
```

### Example 4: Display Feature Capabilities

```javascript
import { useAvailableFeatures } from '../hooks/useGrowthAI';
import growthTrackingAI from '../services/growthTrackingAI';

function AIFeaturesScreen() {
  const { features, percentageReady, loading } = useAvailableFeatures();
  
  return (
    <ScrollView>
      <Card>
        <Title>AI Features Status</Title>
        <ProgressBar value={percentageReady} />
        <Text>{percentageReady}% Ready</Text>
      </Card>
      
      {features.map(feature => {
        const display = growthTrackingAI.getFeatureDisplay(feature);
        return (
          <Card key={feature}>
            <View style={styles.featureRow}>
              <Text style={styles.icon}>{display.icon}</Text>
              <View style={styles.featureInfo}>
                <Text style={styles.title}>{display.title}</Text>
                <Text style={styles.description}>{display.description}</Text>
              </View>
              <Badge text="Available" color="green" />
            </View>
          </Card>
        );
      })}
    </ScrollView>
  );
}
```

### Example 5: Smart Feature Detection

```javascript
import growthTrackingAI from '../services/growthTrackingAI';

async function handleImageUpload(plotId, imageUri) {
  // Check what features are available
  const status = await growthTrackingAI.getModelsStatus();
  
  const analyses = [];
  
  // Soil analysis
  if (status.features.soil_analysis) {
    analyses.push(analyzeSoil(imageUri));
  }
  
  // Plant health
  if (status.features.plant_health) {
    analyses.push(analyzeHealth(imageUri));
  }
  
  // Pest detection
  if (status.features.pest_detection) {
    analyses.push(detectPests(imageUri));
  }
  
  // Disease detection
  if (status.features.disease_detection) {
    analyses.push(detectDiseases(imageUri));
  }
  
  // Run all available analyses in parallel
  const results = await Promise.all(analyses);
  
  return {
    image_uri: imageUri,
    plot_id: plotId,
    analyses: results,
    ai_powered: status.available
  };
}
```

## Feature Capabilities

### Soil Analysis
- Soil type classification (Clay, Sandy, Loam, etc.)
- Texture analysis (Fine, Medium, Coarse)
- pH range estimation
- Organic matter content
- Moisture level detection
- Color-based nutrient indicators

### Plant Health
- Overall health score (0-100)
- Growth stage detection
- Stress indicators
- Leaf color analysis
- Canopy coverage estimation
- Vigor assessment

### Pest Detection
- Identify 7+ common agricultural pests
- Severity assessment (Low/Medium/High)
- Confidence scoring
- Treatment recommendations
- Regional risk factors

### Disease Detection
- Classify 15+ crop diseases
- Early warning detection
- Symptom pattern recognition
- Spread prediction
- Treatment protocols

### Yield Prediction
- Harvest date forecasting
- Expected yield estimation
- Quality predictions
- Market timing recommendations
- Weather impact analysis

### Growth Prediction
- Growth stage progression
- Optimal care scheduling
- Calendar event automation
- Resource planning
- Milestone tracking

### Storage Assessment
- Quality degradation monitoring
- Shelf life estimation
- Storage condition recommendations
- Spoilage risk detection

## Backend Usage

### Using Models in Growth Tracking Service

```python
from app.services.advanced_growth_tracking import AdvancedGrowthTrackingService

service = AdvancedGrowthTrackingService(supabase_client)

# Models are automatically loaded via model manager
# Service will use AI if available, fallback to rule-based if not

# Soil analysis (uses soil_diagnostics model)
soil_result = await service.analyze_soil_ai(image_url)

# Health check (uses plant_health model)
health_result = await service.analyze_health(plot_id, image_urls)

# Pest detection (uses pest_detection model)
pest_result = await service.diagnose_pest_disease(plot_id, image_url, location)
```

### Checking Model Availability

```python
from app.services.model_manager import get_model_manager

model_manager = get_model_manager()

# Check if specific model is available
pest_model = model_manager.get_model("pest_detection")
if pest_model:
    # AI-powered pest detection available
    pass
else:
    # Use rule-based fallback
    pass

# Get all models status
models = model_manager.list_available_models()
if models["soil_diagnostics"]["available"]:
    # Soil analysis AI ready
    pass
```

## Training Models

To enable all AI features, train the models:

```bash
# Train all models
cd backend
python master_train_models.py --all

# Or train specific models
python master_train_models.py --models pest_detection disease_detection soil_diagnostics
```

## Testing Integration

### Backend Test
```bash
# Start backend
cd backend
python run_dev.py

# Test AI status
curl http://localhost:8000/api/advanced-growth/ai/models/status

# Test specific feature
curl http://localhost:8000/api/advanced-growth/ai/models/pest_detection/info

# Get available features
curl http://localhost:8000/api/advanced-growth/ai/features/available
```

### Frontend Test
```javascript
import growthTrackingAI from './services/growthTrackingAI';

// Test in console or component
const testAI = async () => {
  const status = await growthTrackingAI.getModelsStatus();
  console.log('AI Status:', status);
  
  const features = await growthTrackingAI.getAvailableFeatures();
  console.log('Available Features:', features);
  
  if (features.features.includes('pest_detection')) {
    const info = await growthTrackingAI.getFeatureInfo('pest_detection');
    console.log('Pest Detection Info:', info);
  }
};
```

## Error Handling

### Backend Graceful Degradation
```python
# Service automatically falls back to rule-based analysis
if self.model_manager:
    try:
        model = self.model_manager.get_model("pest_detection")
        # Use AI model
    except Exception as e:
        print(f"AI unavailable: {e}")
        # Use rule-based fallback
else:
    # Use rule-based fallback
```

### Frontend Error Handling
```javascript
const { status, error } = useGrowthAIStatus();

if (error) {
  // Model manager unavailable - use rule-based features
  return <RuleBasedInterface />;
}

if (!status.available) {
  // No models trained yet
  return (
    <Message>
      AI features not yet available.
      Contact admin to train models.
    </Message>
  );
}

// AI features available
return <AIEnhancedInterface features={status.features} />;
```

## Performance Optimization

### Preload Critical Models
```javascript
// In app initialization
useEffect(() => {
  const preloadModels = async () => {
    // Preload most-used features
    await growthTrackingAI.loadFeatureModel('pest_detection');
    await growthTrackingAI.loadFeatureModel('disease_detection');
    await growthTrackingAI.loadFeatureModel('plant_health');
  };
  
  preloadModels();
}, []);
```

### Cache Status Results
```javascript
const [cachedStatus, setCachedStatus] = useState(null);
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

const getStatus = async () => {
  if (cachedStatus && Date.now() - cachedStatus.timestamp < CACHE_DURATION) {
    return cachedStatus.data;
  }
  
  const status = await growthTrackingAI.getModelsStatus();
  setCachedStatus({
    data: status,
    timestamp: Date.now()
  });
  
  return status;
};
```

## Deployment Checklist

- [ ] Train all ML models: `python master_train_models.py --all`
- [ ] Verify models exist in `backend/trained_models/`
- [ ] Test backend: `curl /api/advanced-growth/ai/models/status`
- [ ] Update frontend API config with correct base URL
- [ ] Test frontend hooks in development
- [ ] Add loading states for AI features
- [ ] Implement fallback UI for unavailable features
- [ ] Add error boundaries around AI components
- [ ] Test with and without models available
- [ ] Monitor model loading performance
- [ ] Document which features require which models

## Troubleshooting

**Problem**: All features showing as unavailable
- **Solution**: Train models with `python master_train_models.py --all`

**Problem**: Models available but not loading
- **Solution**: Check `backend/trained_models/` permissions and file existence

**Problem**: Frontend can't connect to AI endpoints
- **Solution**: Verify `API_BASE_URL` in frontend config points to backend

**Problem**: Feature flags not updating
- **Solution**: Call `refresh()` from hooks or clear component cache

**Problem**: Slow model loading
- **Solution**: Use preloading strategy or enable lazy loading

## Next Steps

1. **Train Models**: Run training pipeline to enable AI features
2. **Update UI**: Add AI status indicators to growth tracking screens
3. **Add Badges**: Show "AI-Powered" badges on available features
4. **User Education**: Add tooltips explaining AI capabilities
5. **Monitor Usage**: Track which AI features are most used
6. **Iterate**: Improve models based on user feedback

## Support

For issues:
1. Check AI status: `GET /api/advanced-growth/ai/models/status`
2. Review backend logs for model loading errors
3. Verify training data exists in `training_data/` and `training_data_public/`
4. Test with simple curl commands before debugging frontend
