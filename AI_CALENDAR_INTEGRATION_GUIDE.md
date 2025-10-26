# 📅 AI Calendar Integration in Growth Tracker

## Overview

The **AI Calendar System** is now fully integrated with the **Growth Tracker**! When you create a digital plot or log plant health, the system automatically schedules and adjusts farm practices based on:

- 🌱 Planting date and crop type
- 🌡️ Weather forecasts
- 🔬 Soil analysis results
- ❤️ Plant health conditions
- 🐛 Pest/disease diagnoses

---

## 🚀 How It Works

### **1. Auto-Schedule Full Season Calendar (Plot Creation)**

When a farmer creates a digital plot:

```
User Actions:
1. Uploads initial photo
2. Selects planting date
3. Enters location
4. Uploads soil image

↓ AI MAGIC ↓

System Automatically Schedules:
✅ Weeding events (2-3 times based on crop)
✅ Fertilizer applications (soil-specific)
✅ Pest scouting (weekly during critical stages)
✅ Disease monitoring
✅ Photo check-in reminders
✅ Harvest window
```

**Example: Tomato Plot**
```
Planting Date: Oct 26, 2025
Auto-Scheduled Events:
- Nov 9: First Weeding (14 days after planting)
- Nov 16: First Top-Dress Fertilizer (21 days)
- Nov 23: Pest Scouting Start (28 days)
- Nov 30: Photo Check-in - Vegetative Stage
- Dec 7: Second Weeding (42 days)
- Dec 21: Second Top-Dress Fertilizer (56 days)
- Jan 18-28: Harvest Window (84-94 days)
```

---

### **2. Dynamic Event Updates (Health Analysis)**

When farmers log plant health, AI adjusts the calendar:

```
Health Analysis Detects:
- ⚠️ Nitrogen Deficiency

↓ AI RESPONSE ↓

System Automatically:
1. Schedules "Emergency Nitrogen Application" in 2 days
2. Provides local methods (manure, compost tea)
3. Provides commercial methods (CAN, Urea)
4. Sets priority to HIGH
```

**Triggers:**
| Health Condition | Auto-Scheduled Event | When |
|-----------------|---------------------|------|
| Nitrogen Deficiency | Emergency Nitrogen Application | 2 days |
| High Water Stress | Irrigation Reminder | Immediate |
| Health Declining >10 pts | Emergency Health Check | 1 day |
| Yellowing Detected | Nutrient Check | 3 days |

---

### **3. Smart Treatment Scheduling (Pest/Disease Diagnosis)**

When pests or diseases are detected, AI creates a complete treatment schedule:

```
Diagnosis: Early Blight (Moderate Severity)

↓ AI TREATMENT PLAN ↓

Auto-Scheduled Events:
1. "Copper Fungicide - Application 1/3" (Immediate - URGENT)
   - Method: Spray thoroughly on leaves
   - Frequency: Every 7-10 days
   
2. "Copper Fungicide - Application 2/3" (7 days later)
   - Same treatment, scheduled automatically

3. "Copper Fungicide - Application 3/3" (14 days later)
   - Final application

4. "Treatment Effectiveness Check" (17 days later)
   - Photo reminder to evaluate results
```

**Treatment Schedule includes:**
- ✅ Multiple application dates
- ✅ Local and commercial product options
- ✅ Best practices (watering, leaf removal)
- ✅ Follow-up monitoring
- ✅ Estimated costs

---

### **4. Weather-Adjusted Timing**

AI continuously monitors weather and adjusts event dates:

```
Original Schedule:
- Weeding: Nov 15

Weather Forecast:
- Heavy rain expected Nov 14-16
- Soil will be waterlogged

↓ AI ADJUSTMENT ↓

Updated Schedule:
- Weeding: Nov 18 (delayed 3 days)
- Reason: "Heavy rainfall expected. Soil too wet for weeding."
```

**Adjustments Made For:**
- 🌧️ Rain forecasts (delays weeding, adjusts fertilizer)
- 🌡️ Temperature extremes (adjusts pest scouting)
- 💧 Soil moisture (from BLE sensors if available)

---

## 📊 Database Schema

### **scheduled_events Table**

```sql
CREATE TABLE scheduled_events (
    id UUID PRIMARY KEY,
    plot_id UUID REFERENCES digital_plots,
    user_id UUID REFERENCES profiles,
    
    -- Event details
    event_type VARCHAR(50),  -- farm_practice, photo_reminder, treatment_application, urgent_practice
    practice_name VARCHAR(200),  -- "First Weeding", "Emergency Nitrogen Application"
    scheduled_date TIMESTAMP,
    
    -- Methods and guidance
    description TEXT,
    local_methods JSONB,  -- Local farming methods
    commercial_methods JSONB,  -- Commercial products
    best_practices JSONB,  -- Best practices array
    
    -- Treatment-specific
    treatment_details JSONB,  -- Product, method, timing
    
    -- Soil recommendations
    soil_recommendations JSONB,  -- Soil-specific adjustments
    
    -- Priority and status
    priority VARCHAR(20),  -- urgent, high, moderate, low
    status VARCHAR(50),  -- scheduled, completed, in_progress, skipped
    
    -- Completion tracking
    completed_date TIMESTAMP,
    completion_notes TEXT,
    actual_labor_hours DECIMAL,
    
    -- Source tracking
    source VARCHAR(50),  -- auto_generated, health_analysis, diagnosis, user_created
    health_trigger TEXT,  -- What health issue triggered this
    
    -- Weather adjustments
    adjustment_reason TEXT,
    original_date TIMESTAMP,
    
    -- Reminders
    reminders_enabled BOOLEAN,
    reminder_days_before INTEGER
);
```

---

## 🔌 API Endpoints

### **Get Plot Calendar**

```http
GET /api/advanced-growth/calendar/{plot_id}
```

**Response:**
```json
{
  "success": true,
  "plot_id": "abc-123",
  "total_events": 12,
  "grouped_events": {
    "farm_practices": [
      {
        "id": "event-1",
        "practice_name": "First Weeding",
        "scheduled_date": "2025-11-09T08:00:00",
        "days_after_planting": 14,
        "status": "scheduled",
        "priority": "moderate",
        "local_methods": ["Hand weeding with jembe", "Slash weeds with panga"],
        "commercial_methods": ["Pre-emergence herbicide (Atrazine)"],
        "estimated_labor_hours": 8
      }
    ],
    "photo_reminders": [...],
    "treatment_applications": [...]
  }
}
```

---

### **Get Upcoming Events (Dashboard View)**

```http
GET /api/advanced-growth/calendar/user/{user_id}/upcoming?days_ahead=7
```

**Perfect for "What's Next" dashboard section**

**Response:**
```json
{
  "success": true,
  "days_ahead": 7,
  "total_events": 5,
  "events_by_date": {
    "2025-10-27": [
      {
        "practice_name": "Photo Check-in - Week 1",
        "plot_name": "North Tomato Field",
        "crop_name": "Tomato",
        "priority": "moderate"
      }
    ],
    "2025-10-29": [
      {
        "practice_name": "Emergency Nitrogen Application",
        "plot_name": "South Bean Plot",
        "priority": "high",
        "health_trigger": "Nitrogen Deficiency: Yellowing leaves detected"
      }
    ]
  }
}
```

---

### **Complete an Event**

```http
PUT /api/advanced-growth/calendar/event/{event_id}/complete
```

**Request:**
```json
{
  "completion_notes": "Weeded entire plot, removed all visible weeds",
  "actual_labor_hours": 6.5,
  "completion_images": [
    "https://...supabase.co/storage/weeding_complete.jpg"
  ]
}
```

---

### **Reschedule an Event**

```http
PUT /api/advanced-growth/calendar/event/{event_id}/reschedule
```

**Request:**
```json
{
  "new_date": "2025-11-18T08:00:00",
  "reason": "Heavy rain expected, soil too wet"
}
```

---

### **Create Custom Event**

```http
POST /api/advanced-growth/calendar/event/custom
```

**Request:**
```json
{
  "plot_id": "abc-123",
  "user_id": "user-456",
  "practice_name": "Pruning Tomato Suckers",
  "scheduled_date": "2025-11-15T08:00:00",
  "description": "Remove suckers to improve air circulation",
  "priority": "moderate"
}
```

---

## 🎯 Integration Flow

### **Flow 1: Plot Creation → Full Calendar**

```mermaid
User Creates Plot
    ↓
advanced_growth_tracking.py
    ↓
create_digital_plot()
    ↓
CALLS: growth_calendar_integration.py
    ↓
schedule_full_season_calendar()
    ↓
calendar_generator.py (generates base calendar)
    ↓
INSERTS: scheduled_events table
    ↓
Returns calendar with 10-15 auto-scheduled events
```

---

### **Flow 2: Health Log → Dynamic Updates**

```mermaid
User Logs Health
    ↓
advanced_growth_tracking.py
    ↓
create_growth_log()
    ↓
analyze_plant_health_comprehensive()
    ↓
DETECTS: Nitrogen Deficiency
    ↓
CALLS: growth_calendar_integration.py
    ↓
update_events_from_health_analysis()
    ↓
INSERTS: New "Emergency Nitrogen Application" event
    ↓
Farmer receives notification: "Urgent: Apply nitrogen within 2 days"
```

---

### **Flow 3: Diagnosis → Treatment Schedule**

```mermaid
User Submits Diagnosis Image
    ↓
advanced_growth_routes.py
    ↓
POST /diagnosis/comprehensive
    ↓
diagnose_pest_disease_regional()
    ↓
DETECTS: Early Blight
    ↓
GENERATES: Treatment Plan (3 applications)
    ↓
CALLS: growth_calendar_integration.py
    ↓
schedule_treatment_from_diagnosis()
    ↓
INSERTS: 4 events (3 treatments + 1 follow-up check)
    ↓
Farmer sees complete treatment timeline
```

---

## 📱 Frontend Integration

### **Example: Upcoming Events Widget**

```javascript
// Get upcoming events for dashboard
const getUpcomingEvents = async (userId) => {
  const response = await fetch(
    `${API_URL}/api/advanced-growth/calendar/user/${userId}/upcoming?days_ahead=7`
  );
  const data = await response.json();
  
  // Display in "What's Next" section
  return data.events_by_date;
};

// Display calendar for specific plot
const getPlotCalendar = async (plotId) => {
  const response = await fetch(
    `${API_URL}/api/advanced-growth/calendar/${plotId}`
  );
  const data = await response.json();
  
  return data.grouped_events;
};

// Mark event complete
const completeEvent = async (eventId, notes, hours) => {
  const response = await fetch(
    `${API_URL}/api/advanced-growth/calendar/event/${eventId}/complete`,
    {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        completion_notes: notes,
        actual_labor_hours: hours
      })
    }
  );
  
  return await response.json();
};
```

---

### **Example: Calendar View Component**

```jsx
import React, { useEffect, useState } from 'react';
import { View, Text, FlatList } from 'react-native';

const PlotCalendar = ({ plotId }) => {
  const [events, setEvents] = useState([]);
  
  useEffect(() => {
    fetch(`${API_URL}/api/advanced-growth/calendar/${plotId}`)
      .then(res => res.json())
      .then(data => {
        setEvents(data.grouped_events.farm_practices);
      });
  }, [plotId]);
  
  return (
    <View>
      <Text style={{fontSize: 20, fontWeight: 'bold'}}>
        Scheduled Farm Practices
      </Text>
      
      <FlatList
        data={events}
        keyExtractor={item => item.id}
        renderItem={({item}) => (
          <View style={{padding: 10, borderBottom: '1px solid #ddd'}}>
            <Text style={{fontWeight: 'bold'}}>
              {item.practice_name}
            </Text>
            <Text>
              📅 {new Date(item.scheduled_date).toLocaleDateString()}
            </Text>
            <Text>
              ⏱️ Est. {item.estimated_labor_hours} hours
            </Text>
            <Text>
              {item.description}
            </Text>
            
            {item.priority === 'urgent' && (
              <Text style={{color: 'red', fontWeight: 'bold'}}>
                ⚠️ URGENT
              </Text>
            )}
          </View>
        )}
      />
    </View>
  );
};

export default PlotCalendar;
```

---

## ✅ Benefits

### **For Farmers:**
1. ✅ **Never Miss Critical Tasks** - Auto-scheduled reminders
2. ✅ **Smart Timing** - Weather-adjusted dates
3. ✅ **Complete Guidance** - Local and commercial methods
4. ✅ **Treatment Plans** - Step-by-step pest/disease management
5. ✅ **Labor Planning** - Estimated hours for each task

### **For the System:**
1. ✅ **Reactive Intelligence** - Responds to health changes
2. ✅ **Proactive Prevention** - Schedules before problems occur
3. ✅ **Regional Learning** - Uses nearby farm data
4. ✅ **Continuous Optimization** - Adjusts based on conditions

---

## 🚦 Priority System

| Priority | When Used | Visual Indicator |
|---------|-----------|------------------|
| **URGENT** | Pest outbreak, severe deficiency, immediate treatment | 🔴 Red badge |
| **HIGH** | Health declining, upcoming critical window | 🟠 Orange badge |
| **MODERATE** | Standard practices (weeding, fertilizer) | 🟡 Yellow badge |
| **LOW** | Optional improvements, future planning | 🟢 Green badge |

---

## 🔄 Event Lifecycle

```
SCHEDULED → IN_PROGRESS → COMPLETED
     ↓            ↓
  SKIPPED    CANCELLED
```

**Status Tracking:**
- `scheduled` - Waiting to be done
- `in_progress` - Farmer started work
- `completed` - Done, with completion notes
- `skipped` - Farmer decided not to do
- `cancelled` - No longer needed

---

## 📈 Analytics & Insights

The system tracks:

1. **Completion Rate** - % of scheduled events completed on time
2. **Labor Accuracy** - Estimated vs actual hours
3. **Treatment Effectiveness** - Health improvement after treatments
4. **Weather Impact** - How many events were weather-adjusted

This data feeds back into AI models to improve future scheduling!

---

## 🎉 Summary

**The AI Calendar Integration transforms growth tracking from passive monitoring to active farm management!**

🌱 **Create plot** → Full season calendar auto-generated  
❤️ **Log health** → Events adjusted based on plant condition  
🐛 **Diagnose pest** → Complete treatment schedule created  
🌦️ **Weather changes** → Dates automatically adjusted  

**Result:** Farmers get a personalized, intelligent farm management assistant that ensures they never miss critical tasks and always work at the optimal time! 🚀
