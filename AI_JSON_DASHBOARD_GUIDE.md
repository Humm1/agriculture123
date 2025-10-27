# AI Analysis JSON Dashboard

## Overview
Comprehensive JSON-based dashboard system for displaying soil health analysis and pest/disease detection data with both visual and raw JSON views.

## Features

### 🌱 Soil Health Analysis Dashboard
- **Fertility Score**: 0-10 scale with visual progress bar
- **pH Level**: Soil acidity/alkalinity measurement (4.5-8.5)
- **Soil Type**: Classification (sandy, loamy, clay, etc.)
- **NPK Nutrients**: Nitrogen, Phosphorus, Potassium levels (low/medium/high)
- **Moisture Content**: Percentage measurement
- **Organic Matter**: Percentage estimation
- **Recommendations**: AI-generated soil improvement suggestions

#### JSON Structure - Soil Health
```json
{
  "fertility_score": 7.5,
  "ph_estimate": 6.8,
  "soil_type": "loamy",
  "soil_color": {
    "hue": "brown",
    "munsell_approximation": "10YR 4/3"
  },
  "texture": {
    "primary": "loam",
    "sand_percentage": 40,
    "silt_percentage": 40,
    "clay_percentage": 20
  },
  "nutrients": {
    "nitrogen": "medium",
    "phosphorus": "high",
    "potassium": "medium"
  },
  "moisture_content": 35,
  "organic_matter_estimate": 4.2,
  "recommendations": [
    "Maintain current fertility levels with organic compost",
    "Monitor pH regularly to ensure optimal range"
  ]
}
```

### 🐛 Pest & Disease Detection Dashboard
- **Health Status**: healthy/at_risk/infected
- **Risk Level**: low/moderate/high/critical
- **Growth Stage**: seedling/vegetative/flowering/fruiting/mature
- **Health Metrics**: Overall score, vigor, yellowing %, browning %
- **Detected Pests**: Name, severity, coverage, treatment, economic impact
- **Detected Diseases**: Name, severity, pathogen type, symptoms, spread risk
- **Predictions**: Future issues with likelihood and timeframe
- **Immediate Actions**: Critical tasks to perform now

#### JSON Structure - Pest & Disease
```json
{
  "health_status": "at_risk",
  "confidence": 0.87,
  "risk_level": "moderate",
  "growth_stage": {
    "stage": "vegetative",
    "maturity": "45% developed",
    "days_to_harvest": 60
  },
  "health_metrics": {
    "health_score": 72,
    "vigor": "moderate",
    "yellowing_percentage": 15,
    "browning_percentage": 5,
    "spot_count": 12
  },
  "detected_pests": [
    {
      "name": "Aphids",
      "scientific_name": "Aphidoidea",
      "severity": "moderate",
      "confidence": 0.85,
      "coverage_percentage": 20,
      "lifecycle_stage": "nymphs and adults",
      "treatment": "Apply neem oil spray (5ml/L) every 3 days",
      "immediate_action": "Spray affected areas with water to dislodge aphids",
      "economic_impact": "moderate"
    }
  ],
  "detected_diseases": [
    {
      "name": "Early Blight",
      "scientific_name": "Alternaria solani",
      "pathogen_type": "fungal",
      "severity": "low",
      "confidence": 0.78,
      "affected_area_percentage": 8,
      "spread_risk": "moderate",
      "symptoms": [
        "Dark brown spots with concentric rings",
        "Lower leaves affected first",
        "Yellowing around spots"
      ],
      "treatment": "Apply copper-based fungicide every 7 days",
      "prevention": "Improve air circulation, avoid overhead watering"
    }
  ],
  "predictions": [
    {
      "issue": "Late Blight outbreak",
      "likelihood": "high",
      "timeframe": "2-3 weeks",
      "reason": "High humidity and moderate aphid infestation creating favorable conditions",
      "prevention": "Apply preventive fungicide, reduce leaf wetness"
    }
  ],
  "immediate_actions": [
    "Remove heavily infested leaves",
    "Apply organic pesticide within 24 hours",
    "Set up sticky traps for aphid monitoring"
  ]
}
```

## Implementation

### In GrowthTrackingScreen.js

The JSON dashboard is integrated directly into the plot details view with toggle buttons:

```javascript
// State management
const [showSoilJSON, setShowSoilJSON] = useState(false);
const [showPestJSON, setShowPestJSON] = useState(false);

// Toggle button for Soil Health
<TouchableOpacity 
  style={styles.jsonToggleButton}
  onPress={() => setShowSoilJSON(!showSoilJSON)}
>
  <MaterialCommunityIcons 
    name={showSoilJSON ? "code-json" : "code-braces"} 
    size={20} 
    color="#2196F3" 
  />
  <Text style={styles.jsonToggleText}>
    {showSoilJSON ? 'Hide' : 'Show'} JSON
  </Text>
</TouchableOpacity>

// JSON Display
{showSoilJSON && (
  <View style={styles.jsonDashboard}>
    <View style={styles.jsonHeader}>
      <MaterialCommunityIcons name="code-json" size={24} color="#4CAF50" />
      <Text style={styles.jsonHeaderText}>Soil Health Analysis - JSON Data</Text>
    </View>
    <ScrollView horizontal style={styles.jsonScrollContainer}>
      <Text style={styles.jsonText}>
        {JSON.stringify(soilAnalysis, null, 2)}
      </Text>
    </ScrollView>
    <View style={styles.jsonFooter}>
      <Text style={styles.jsonFooterText}>
        🌱 Fertility: {soilAnalysis.fertility_score}/10 | 
        🧪 pH: {soilAnalysis.ph_estimate} | 
        🏞️ Type: {soilAnalysis.soil_type}
      </Text>
    </View>
  </View>
)}
```

### Standalone Component

For advanced use cases, use the `AIAnalysisDashboard` component:

```javascript
import AIAnalysisDashboard from '../components/AIAnalysisDashboard';

// In your render method
<AIAnalysisDashboard 
  soilAnalysis={soilData}
  pestAnalysis={pestData}
/>
```

## Styling

The JSON dashboard uses a dark theme for code display:

- **Background**: #1E1E1E (VS Code dark theme)
- **Text**: #D4D4D4 (light gray for readability)
- **Borders**: #4CAF50 (green accent for soil) or #FF5722 (red accent for pests)
- **Font**: Monospace (Courier on iOS, monospace on Android)
- **Max Height**: 400px with horizontal scroll for wide JSON

## Usage Scenarios

### 1. Farmer Dashboard
- Quick toggle between visual charts and raw JSON data
- Export JSON for record-keeping
- Share analysis with agricultural extension officers

### 2. Developer Testing
- Verify AI model outputs
- Debug analysis algorithms
- Compare expected vs actual JSON structure

### 3. Research & Training
- Study AI model patterns
- Collect training data samples
- Validate detection accuracy

### 4. API Integration
- Copy JSON for external system integration
- Export data to third-party analytics platforms
- Generate reports from raw analysis data

## Benefits

### ✅ Transparency
- Farmers see exactly what the AI detected
- No "black box" - all data is visible
- Build trust through full disclosure

### ✅ Debugging
- Developers can verify model outputs
- Easy to spot incorrect classifications
- Quick identification of edge cases

### ✅ Education
- Learn about plant health metrics
- Understand pest/disease characteristics
- See scientific names and proper identification

### ✅ Integration
- Raw JSON ready for external systems
- Easy data export for record-keeping
- Compatible with agricultural management software

## Future Enhancements

1. **Copy to Clipboard**: One-tap JSON copying
2. **Export Options**: PDF, CSV, or JSON file download
3. **Historical Comparison**: Compare analysis over time
4. **Sharing**: Send analysis to agronomists or consultants
5. **Filtering**: Show only specific sections of JSON
6. **Search**: Find specific values within JSON structure
7. **Diff View**: Compare before/after analysis
8. **AI Explanations**: Natural language interpretation of JSON values

## API Response Format

The dashboard expects analysis data from:
- `GET /api/advanced-growth/plots/{plot_id}` with `ai_analysis` field in images

### Expected Structure
```json
{
  "success": true,
  "plot": {...},
  "images": [
    {
      "id": "img_123",
      "image_url": "https://...",
      "image_type": "crop_health",
      "ai_analysis": {
        "soil_health": { /* soil JSON structure */ },
        "pest_disease_scan": { /* pest JSON structure */ }
      }
    }
  ]
}
```

## Testing

### Test Soil Analysis Display
1. Upload plot image (soil type)
2. Navigate to Growth Tracking
3. Select plot with soil analysis
4. Click "Show JSON" on Soil Health section
5. Verify JSON displays correctly
6. Check footer shows fertility/pH/type

### Test Pest Detection Display
1. Upload plot image (crop with issues)
2. Navigate to Growth Tracking
3. Select plot with pest analysis
4. Click "Show JSON" on Disease & Pest section
5. Verify JSON displays correctly
6. Check footer shows counts and actions

## Related Files

- **Frontend**: `frontend/agroshield-app/src/screens/farmer/GrowthTrackingScreen.js`
- **Component**: `frontend/agroshield-app/src/components/AIAnalysisDashboard.js`
- **Backend**: `backend/app/services/soil_health_ai.py` (580 lines)
- **Backend**: `backend/app/services/pest_disease_ai.py` (850+ lines)
- **API**: `backend/app/routes/advanced_growth_routes.py` (lines 380-500)

## Support

For issues or questions about the JSON dashboard:
1. Check console logs for data structure
2. Verify `ai_analysis` field exists in plot images
3. Ensure backend AI models are running
4. Validate JSON structure matches expected format
