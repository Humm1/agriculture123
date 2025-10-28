# Growth Tracking AI Calendar Integration

## Overview

The AI Calendar features have been fully integrated into the Growth Tracking system, providing farmers with intelligent, stage-based crop management throughout the growing season.

## Architecture

### Backend Integration

#### New API Endpoints (Growth Tracking Routes)

All endpoints are prefixed with `/api/advanced-growth/growth/`

1. **POST `/{plot_id}/lifecycle-calendar`**
   - Generates complete AI-powered lifecycle calendar for a plot
   - Returns stages, practices, milestones, resources, and risks
   - AI-optimized based on weather, location, and crop model

2. **GET `/{plot_id}/current-stage`**
   - Returns current growth stage information
   - Includes progress percentage and days since planting
   - Lists stage-specific practices and monitoring parameters

3. **GET `/{plot_id}/upcoming-practices`**
   - Returns practices for next N days (default: 7)
   - AI-optimized scheduling with priority levels
   - Includes labor hours and cost estimates

4. **GET `/{plot_id}/milestones`**
   - Returns key milestones: planting, emergence, flowering, harvest
   - With dates and DAP (Days After Planting)

5. **GET `/{plot_id}/resource-plan`**
   - Complete season resource requirements
   - Labor hours, costs, inputs, equipment needed

6. **GET `/{plot_id}/risk-calendar`**
   - Stage-specific pest and disease risks
   - AI detection availability status
   - Monitoring frequency recommendations

7. **GET `/calendar/ai-status`**
   - AI features availability check
   - Returns which AI models are ready
   - Percentage of features operational

### Frontend Integration

#### Services Layer

**`growthLifecycleCalendar.js`**
```javascript
import * as growthCalendarService from '../services/growthLifecycleCalendar';

// Generate full calendar
const calendar = await growthCalendarService.generateLifecycleCalendar(plotId);

// Get current stage
const stage = await growthCalendarService.getCurrentGrowthStage(plotId);

// Get upcoming practices
const practices = await growthCalendarService.getUpcomingPractices(plotId, 7);
```

#### React Hook

**`useGrowthLifecycleCalendar.js`**
```javascript
import { useGrowthLifecycleCalendar } from '../hooks/useGrowthLifecycleCalendar';

function MyComponent({ plotId }) {
  const {
    calendar,
    currentStage,
    upcomingPractices,
    milestones,
    resourcePlan,
    riskCalendar,
    aiStatus,
    loading,
    error,
    loadAllData
  } = useGrowthLifecycleCalendar(plotId);

  return (
    // Use the data...
  );
}
```

#### UI Components

**`GrowthCalendarCards.js`** - Ready-to-use React Native components:

1. **CurrentStageCard** - Shows current growth stage with progress bar
2. **UpcomingPracticesCard** - Lists next practices with AI indicators
3. **MilestonesTimeline** - Visual timeline of key events
4. **AICalendarBadge** - Shows AI features availability
5. **ResourceSummaryCard** - Season resource overview
6. **RiskAlertsCard** - Current and upcoming risks

```javascript
import {
  CurrentStageCard,
  UpcomingPracticesCard,
  MilestonesTimeline,
  AICalendarBadge,
  ResourceSummaryCard,
  RiskAlertsCard
} from '../components/growth/GrowthCalendarCards';

// In your growth tracking screen:
<CurrentStageCard 
  currentStage={currentStage} 
  daysSincePlanting={daysSincePlanting} 
/>

<UpcomingPracticesCard 
  practices={upcomingPractices} 
  onViewAll={() => navigation.navigate('AllPractices')} 
/>

<MilestonesTimeline milestones={milestones} />

<AICalendarBadge aiStatus={aiStatus} />

<ResourceSummaryCard resourcePlan={resourcePlan} />

<RiskAlertsCard 
  riskCalendar={riskCalendar} 
  currentDap={daysSincePlanting} 
/>
```

## Features Integrated

### 1. Lifecycle-Based Calendar
- Automatic calendar generation based on crop growth models
- 7 growth stages: Germination → Emergence → Vegetative → Flowering → Fruiting → Maturity
- Stage-specific practices with exact DAP scheduling

### 2. Current Stage Tracking
- Real-time growth stage identification
- Progress tracking with percentage complete
- Stage-specific practice recommendations
- Monitoring parameters (soil moisture, nutrients, etc.)

### 3. Intelligent Practice Scheduling
- AI-optimized practice dates
- Weather-adjusted timing
- Priority levels (High/Medium/Low)
- Labor hours and cost estimates
- ✨ AI indicator for optimized practices

### 4. Milestones Timeline
- Visual timeline of major events
- Planting → Emergence → Flowering → Harvest
- Past/present/future indicators
- DAP tracking

### 5. Resource Planning
- Season-long resource requirements
- Total labor hours estimate
- Cost projections
- Inputs needed (fertilizers, pesticides, etc.)
- Equipment requirements

### 6. Risk Calendar
- Stage-specific pest and disease risks
- AI detection availability
- Monitoring frequency recommendations
- Early warning system

### 7. AI Feature Status
- Real-time AI capabilities check
- Feature availability badges
- Percentage ready indicator
- Available features:
  - ✨ Lifecycle Calendar
  - 🐛 Pest Detection
  - 🦠 Disease Detection
  - 🌿 Health Monitoring
  - 📊 Yield Prediction

## Integration with Existing Growth Tracking

### How It Works

1. **Plot Creation**: When a farmer creates a digital plot, crop and variety are stored
2. **Calendar Generation**: Calendar is auto-generated based on crop growth model
3. **Current Stage**: System calculates current stage from planting date
4. **Practice Alerts**: Upcoming practices shown in "What's Next" section
5. **AI Optimization**: If AI models available, practices are optimized for weather/conditions
6. **Risk Monitoring**: Farmers get alerts for stage-specific pests/diseases

### Data Flow

```
Digital Plot Created
    ↓
Crop & Variety Selected (e.g., Maize H614)
    ↓
Lifecycle Calendar Generated
    ↓
Growth Stages Calculated (based on planting date)
    ↓
Current Stage Identified (Days Since Planting)
    ↓
Practices Scheduled (AI-optimized if available)
    ↓
Risks Identified (based on current stage)
    ↓
Farmer Receives Alerts & Recommendations
```

## Supported Crops

### Maize (3 varieties)
- **H614** (120 days)
  - Stages: Germination → Emergence → Vegetative → Tasseling → Silking → Grain Fill → Maturity
  - Critical Practices: 2 weedings, 2 top dressings, pest scouting
  
- **Short Season** (90 days)
  - Faster maturity for regions with shorter growing seasons
  
- **Long Season** (150 days)
  - For regions with extended rainfall

### Beans (2 varieties)
- **Kat B1** (75 days)
  - Stages: Germination → Vegetative → Flowering → Pod Formation → Pod Filling → Maturity
  
- **Climbing Beans** (90 days)
  - Requires staking support

### Potatoes (2 varieties)
- **Shangi** (90 days)
  - Stages: Sprouting → Vegetative → Tuber Initiation → Tuber Bulking → Maturity
  
- **Dutch Robjin** (105 days)
  - Longer maturity period

## AI Optimization Features

### Weather-Based Adjustments
- Practice dates adjusted based on rainfall forecasts
- Irrigation scheduling optimized
- Harvest window refinement

### Pest & Disease Detection
- AI models identify pests from images
- Early detection alerts
- Treatment recommendations

### Plant Health Monitoring
- Health score (0-100)
- Growth stage validation
- Stress indicators

### Yield Prediction
- Expected harvest date
- Yield estimates based on growth progress
- Quality predictions

## Usage Examples

### Example 1: Get Current Stage and Practices

```javascript
import { useGrowthLifecycleCalendar } from '../hooks/useGrowthLifecycleCalendar';

function GrowthDashboard({ plotId }) {
  const {
    currentStage,
    upcomingPractices,
    loading
  } = useGrowthLifecycleCalendar(plotId);

  if (loading) return <ActivityIndicator />;

  return (
    <View>
      <CurrentStageCard 
        currentStage={currentStage}
        daysSincePlanting={calculateDays(plantingDate)}
      />
      
      <UpcomingPracticesCard 
        practices={upcomingPractices}
        onViewAll={() => {/* navigate */}}
      />
    </View>
  );
}
```

### Example 2: Display Milestones

```javascript
function MilestonesScreen({ plotId }) {
  const { milestones } = useGrowthLifecycleCalendar(plotId);

  return (
    <MilestonesTimeline milestones={milestones} />
  );
}
```

### Example 3: Resource Planning

```javascript
function ResourcesScreen({ plotId }) {
  const { resourcePlan } = useGrowthLifecycleCalendar(plotId);

  return (
    <ResourceSummaryCard resourcePlan={resourcePlan} />
  );
}
```

### Example 4: Risk Monitoring

```javascript
function RiskAlertsScreen({ plotId, daysSincePlanting }) {
  const { riskCalendar } = useGrowthLifecycleCalendar(plotId);

  return (
    <RiskAlertsCard 
      riskCalendar={riskCalendar}
      currentDap={daysSincePlanting}
    />
  );
}
```

## Testing

### Backend API Testing

```bash
# Test lifecycle calendar generation
curl -X POST http://localhost:8000/api/advanced-growth/growth/{plot_id}/lifecycle-calendar

# Test current stage
curl http://localhost:8000/api/advanced-growth/growth/{plot_id}/current-stage

# Test upcoming practices
curl http://localhost:8000/api/advanced-growth/growth/{plot_id}/upcoming-practices?days_ahead=14

# Test AI status
curl http://localhost:8000/api/advanced-growth/growth/calendar/ai-status
```

### Frontend Testing

```javascript
// Test the hook
import { renderHook, act } from '@testing-library/react-hooks';
import { useGrowthLifecycleCalendar } from '../hooks/useGrowthLifecycleCalendar';

test('loads calendar data', async () => {
  const { result, waitForNextUpdate } = renderHook(() => 
    useGrowthLifecycleCalendar('test-plot-id')
  );

  await waitForNextUpdate();

  expect(result.current.calendar).toBeDefined();
  expect(result.current.currentStage).toBeDefined();
});
```

## Benefits for Farmers

### 1. **Never Miss Critical Tasks**
- Automated scheduling of all farm practices
- Timely reminders for weeding, fertilizing, pest control
- AI-optimized timing for best results

### 2. **Better Resource Planning**
- Know exact labor requirements upfront
- Budget planning with cost estimates
- Order inputs at the right time

### 3. **Proactive Risk Management**
- Stage-specific pest/disease alerts
- Early warning before problems occur
- AI-powered detection when issues arise

### 4. **Improved Yields**
- Follow scientifically-proven practices
- Optimal timing for all interventions
- Weather-optimized scheduling

### 5. **Knowledge Transfer**
- Learn best practices for each growth stage
- Understand crop development
- Build farming expertise

## Future Enhancements

1. **Multi-Plot Coordination**
   - Coordinate practices across multiple plots
   - Optimize labor allocation
   - Batch similar tasks

2. **Community Insights**
   - See what other farmers are doing at this stage
   - Regional best practices
   - Success stories

3. **Market Integration**
   - Match harvest dates with market prices
   - Plan harvest for peak demand
   - Connect with buyers early

4. **Advanced AI**
   - Soil nutrient predictions
   - Disease spread modeling
   - Optimal planting date recommendations

5. **Voice Alerts**
   - Audio reminders for practices
   - Voice-guided instructions
   - Multi-language support

## Technical Notes

### Dependencies

**Backend:**
- `crop_lifecycle_calendar.py` - Calendar generation service
- `ai_calendar_intelligence.py` - AI optimization engine
- `growth_model.py` - Crop growth models (CROP_GROWTH_MODELS)
- `model_manager.py` - Centralized AI model management

**Frontend:**
- React Native
- Axios for API calls
- React Hooks for state management

### Performance Considerations

- Calendar generation is cached per plot
- AI models loaded once at startup
- Lightweight API responses (< 50KB)
- Optimistic UI updates

### Error Handling

- Graceful degradation if AI models unavailable
- Fallback to rule-based calendar if lifecycle service fails
- Clear error messages for users
- Retry logic for network failures

## Support

For issues or questions:
1. Check API status: `/growth/calendar/ai-status`
2. Verify plot has crop and planting_date set
3. Check backend logs for model loading errors
4. Ensure crop is in CROP_GROWTH_MODELS

---

**Integration Status**: ✅ Complete
**AI Features**: 7/7 Available
**Supported Crops**: 3 (Maize, Beans, Potatoes)
**Varieties**: 7 total
**API Endpoints**: 7 new endpoints added
**UI Components**: 6 ready-to-use components
**Documentation**: Complete

The AI Calendar is now fully integrated with Growth Tracking! 🌱✨
