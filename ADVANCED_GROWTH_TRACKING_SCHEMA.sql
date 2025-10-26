-- ============================================================
-- ADVANCED GROWTH TRACKING DATABASE SCHEMA
-- Comprehensive plant growth monitoring with AI analysis
-- ============================================================

-- Drop existing tables if they exist
DROP TABLE IF EXISTS scheduled_events CASCADE;
DROP TABLE IF EXISTS harvest_forecasts CASCADE;
DROP TABLE IF EXISTS pest_disease_diagnoses CASCADE;
DROP TABLE IF EXISTS growth_logs CASCADE;
DROP TABLE IF EXISTS digital_plots CASCADE;

-- ============================================================
-- 1. DIGITAL PLOTS TABLE
-- Stores plot/field profiles with initial setup data
-- ============================================================

CREATE TABLE digital_plots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    
    -- Plot identification
    plot_name VARCHAR(200) NOT NULL,
    crop_name VARCHAR(100) NOT NULL,
    
    -- Initial setup
    initial_image_url TEXT NOT NULL,
    planting_date TIMESTAMP NOT NULL,
    setup_completed_at TIMESTAMP DEFAULT NOW(),
    
    -- Location (crucial for regional predictions)
    location JSONB NOT NULL,  -- {"latitude": X, "longitude": Y}
    
    -- Soil analysis
    soil_image_url TEXT,
    soil_analysis JSONB,  -- Complete soil analysis data
    /*
    soil_analysis structure:
    {
        "soil_type": "Clay Loam",
        "texture": "Medium to fine",
        "organic_matter": "Moderate",
        "ph_range": "6.0-7.0",
        "ph_description": "Neutral",
        "moisture_level": "Moderate",
        "water_retention": "Good",
        "drainage": "Moderate",
        "color_metrics": {"hue": 25.5, "saturation": 120, "value": 140},
        "structure_score": 250.5,
        "recommendations": ["Add compost...", "Improve drainage..."],
        "confidence": 0.78,
        "analysis_method": "computer_vision_cnn"
    }
    */
    
    -- Plot details
    area_size DECIMAL(10, 2),  -- Square meters
    notes TEXT,
    
    -- Demo/Real plot flag
    is_demo BOOLEAN DEFAULT FALSE,  -- Demo plots are editable templates, can be converted to real plots
    
    -- Status
    status VARCHAR(50) DEFAULT 'active',  -- active, harvested, abandoned
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_digital_plots_user_id ON digital_plots(user_id);
CREATE INDEX idx_digital_plots_status ON digital_plots(status);
CREATE INDEX idx_digital_plots_planting_date ON digital_plots(planting_date);
CREATE INDEX idx_digital_plots_location ON digital_plots USING GIN (location);
CREATE INDEX idx_digital_plots_is_demo ON digital_plots(is_demo);
CREATE INDEX idx_digital_plots_user_crop ON digital_plots(user_id, crop_name);

-- ============================================================
-- 2. GROWTH LOGS TABLE
-- Regular check-ins with comprehensive AI health analysis
-- ============================================================

CREATE TABLE growth_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plot_id UUID NOT NULL REFERENCES digital_plots(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    
    -- Log details
    log_type VARCHAR(50) NOT NULL,  -- initial_setup, regular_checkin, milestone, harvest
    timestamp TIMESTAMP DEFAULT NOW(),
    
    -- Images (multiple photos focusing on different parts)
    image_urls TEXT[] NOT NULL,  -- Array of image URLs
    notes TEXT,
    
    -- AI Health Analysis
    health_analysis JSONB NOT NULL,
    /*
    health_analysis structure:
    {
        "overall_health_score": 85,  -- 1-100
        "health_grade": "B+",  -- Letter grade
        "chlorophyll_index": 0.75,  -- 0-1 scale
        "nitrogen_status": "Adequate",  -- Adequate, Moderate, Deficient
        "nitrogen_description": "Healthy green color...",
        "water_stress": "None",  -- None, Moderate, High
        "water_description": "Leaves appear turgid...",
        "growth_stage": "Vegetative",  -- Seedling, Early Vegetative, Vegetative, Reproductive
        "biomarkers": {
            "green_coverage_percent": 65.5,
            "yellow_coverage_percent": 5.2,
            "brown_coverage_percent": 2.1,
            "avg_green_value": 155.3,
            "edge_density": 0.08,
            "chlorophyll_estimate": 75.0
        },
        "alerts": [
            {
                "severity": "high",  -- low, moderate, high
                "type": "nutrient_deficiency",
                "message": "⚠️ Nitrogen Deficiency: Yellowing leaves..."
            }
        ],
        "confidence": 0.82,
        "timestamp": "2025-10-26T..."
    }
    */
    
    -- Growth Comparison (vs previous log)
    growth_comparison JSONB,
    /*
    growth_comparison structure:
    {
        "is_first_log": false,
        "days_since_last_log": 7,
        "health_score_change": 5.2,
        "chlorophyll_change": 0.05,
        "growth_rate_per_day": 0.74,
        "trend": "improving",  -- improving, declining, stable
        "trend_emoji": "📈",
        "comparison_summary": "📈 Health improving by 5.2 points over 7 days"
    }
    */
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_growth_logs_plot_id ON growth_logs(plot_id);
CREATE INDEX idx_growth_logs_user_id ON growth_logs(user_id);
CREATE INDEX idx_growth_logs_timestamp ON growth_logs(timestamp DESC);
CREATE INDEX idx_growth_logs_log_type ON growth_logs(log_type);
CREATE INDEX idx_growth_logs_health_analysis ON growth_logs USING GIN (health_analysis);

-- ============================================================
-- 3. PEST/DISEASE DIAGNOSES TABLE
-- Comprehensive pest and disease diagnosis with regional risk
-- ============================================================

CREATE TABLE pest_disease_diagnoses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plot_id UUID NOT NULL REFERENCES digital_plots(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    
    -- Diagnosis details
    image_url TEXT NOT NULL,
    location JSONB NOT NULL,
    
    -- Detection results
    diagnosis JSONB NOT NULL,
    /*
    diagnosis structure:
    {
        "detected_issues": [
            {
                "type": "disease",  -- disease or pest
                "name": "Early Blight",
                "confidence": 0.75,
                "severity": "moderate",  -- low, moderate, high
                "affected_area_pct": 12.5,
                "symptoms": ["Dark spots with concentric rings", "Leaf yellowing"],
                "fungal_pathogen": true
            }
        ],
        "primary_concern": {...},
        "severity_level": "moderate"  -- none, low, moderate, high, critical
    }
    */
    
    -- Regional Intelligence
    regional_intelligence JSONB,
    /*
    regional_intelligence structure:
    {
        "status": "analyzed",
        "radius_km": 25,
        "nearby_plots_monitored": 12,
        "active_regional_threats": [
            {
                "threat": "Hornworms",
                "reports_count": 3,
                "avg_distance_km": 12,
                "trend": "increasing",
                "risk_level": "high"
            }
        ],
        "risk_level": "high",  -- low, moderate, high
        "alerts": [
            "⚠️ Alert: Hornworms reported by 3 growers within 15 miles..."
        ],
        "weather_factors": {
            "humidity": "high",
            "temperature": "favorable_for_fungi",
            "forecast": "Continue monitoring..."
        }
    }
    */
    
    -- Impact Assessment
    impact_assessment JSONB,
    /*
    impact_assessment structure:
    {
        "severity": "moderate",
        "yield_impact_percentage": "15-25%",
        "quality_impact": "Moderate",
        "photosynthesis_reduction": "20%",
        "detailed_explanations": [
            "🍂 Early Blight will cause leaves to die off..."
        ],
        "time_to_significant_damage": "11 days if untreated"
    }
    */
    
    -- Treatment Plan
    treatment_plan JSONB,
    /*
    treatment_plan structure:
    {
        "treatments": [
            {
                "priority": "urgent",  -- urgent, moderate, routine
                "category": "fungicide",
                "product": "Copper-based fungicide",
                "application": {
                    "method": "Spray thoroughly...",
                    "frequency": "Every 7-10 days",
                    "timing": "Early morning or evening",
                    "coverage": "Apply until runoff"
                },
                "best_practices": [
                    "💧 Water at the base...",
                    "✂️ Remove infected leaves..."
                ],
                "products": {
                    "chemical": ["Bonide Copper Fungicide"],
                    "organic": ["Neem oil concentrate"]
                },
                "expected_results": "Symptoms should stop spreading within 7-10 days"
            }
        ],
        "priority_order": ["urgent", "moderate", "routine"],
        "estimated_cost": "$30-60",
        "treatment_timeline": "Start immediately - continue for 2-3 weeks",
        "monitoring": "Take photos weekly to track improvement"
    }
    */
    
    -- Status tracking
    treatment_applied BOOLEAN DEFAULT FALSE,
    treatment_applied_at TIMESTAMP,
    outcome TEXT,  -- User-reported outcome
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_diagnoses_plot_id ON pest_disease_diagnoses(plot_id);
CREATE INDEX idx_diagnoses_user_id ON pest_disease_diagnoses(user_id);
CREATE INDEX idx_diagnoses_location ON pest_disease_diagnoses USING GIN (location);
CREATE INDEX idx_diagnoses_created_at ON pest_disease_diagnoses(created_at DESC);

-- ============================================================
-- 4. HARVEST FORECASTS TABLE
-- AI-powered harvest timing and quality predictions
-- ============================================================

CREATE TABLE harvest_forecasts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plot_id UUID NOT NULL REFERENCES digital_plots(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    
    -- Forecast data
    harvest_forecast JSONB NOT NULL,
    /*
    harvest_forecast structure:
    {
        "estimated_date": "2025-12-15",
        "window": {
            "earliest": "2025-12-10",
            "latest": "2025-12-20"
        },
        "days_until_harvest": 50,
        "note": "Estimated Harvest: December 10-20. This is on time based on excellent growing conditions."
    }
    */
    
    quality_prediction JSONB NOT NULL,
    /*
    quality_prediction structure:
    {
        "score": "B+",  -- A+ to C-
        "percentage": 82,
        "description": "Good quality - Standard market grade",
        "current_status": "Current Predicted Quality: B+",
        "improvement_potential": "You can improve to A by treating diseases..."
    }
    */
    
    -- Recommendations for improvement
    recommendations JSONB,
    /*
    recommendations structure:
    [
        {
            "priority": "high",
            "action": "Address detected pest issues",
            "potential_gain": "+10-15% quality score"
        }
    ]
    */
    
    -- Actual harvest data (filled in later)
    actual_harvest_date DATE,
    actual_quality_score VARCHAR(10),
    actual_yield_kg DECIMAL(10, 2),
    harvest_notes TEXT,
    
    -- Metadata
    forecast_generated_at TIMESTAMP DEFAULT NOW(),
    confidence DECIMAL(3, 2) DEFAULT 0.80
);

-- Indexes
CREATE INDEX idx_forecasts_plot_id ON harvest_forecasts(plot_id);
CREATE INDEX idx_forecasts_user_id ON harvest_forecasts(user_id);
CREATE INDEX idx_forecasts_estimated_date ON harvest_forecasts((harvest_forecast->>'estimated_date'));


CREATE TABLE scheduled_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plot_id UUID NOT NULL REFERENCES digital_plots(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    
    -- Event details
    event_type VARCHAR(50) NOT NULL,  -- farm_practice, photo_reminder, treatment_application, urgent_practice, alert_action
    practice_name VARCHAR(200) NOT NULL,
    practice_key VARCHAR(100),  -- Links to calendar_generator practice keys
    
    -- Scheduling
    scheduled_date TIMESTAMP NOT NULL,
    original_date TIMESTAMP,  -- If adjusted by weather
    days_after_planting INTEGER,
    
    -- Description and methods
    description TEXT,
    local_methods JSONB,  -- Array of local farming methods
    commercial_methods JSONB,  -- Array of commercial methods
    
    -- Treatment-specific details
    treatment_details JSONB,
    /*
    treatment_details structure:
    {
        "product": "Copper-based fungicide",
        "method": "Spray thoroughly...",
        "timing": "Early morning",
        "coverage": "Apply until runoff",
        "application_number": 1,
        "total_applications": 3
    }
    */
    
    -- Photo reminder details
    photo_focus_areas JSONB,  -- ["leaves", "stems", "fruit"]
    
    -- Soil-specific recommendations
    soil_recommendations JSONB,
    
    -- Best practices
    best_practices JSONB,  -- Array of best practice strings
    
    -- Priority and status
    priority VARCHAR(20) DEFAULT 'moderate',  -- urgent, high, moderate, low
    status VARCHAR(50) DEFAULT 'scheduled',  -- scheduled, in_progress, completed, skipped, cancelled
    
    -- Completion tracking
    completed_date TIMESTAMP,
    completion_notes TEXT,
    completion_images JSONB,  -- Array of image URLs showing completed work
    
    -- Labor tracking
    estimated_labor_hours DECIMAL(5, 2),
    actual_labor_hours DECIMAL(5, 2),
    
    -- Source tracking
    source VARCHAR(50),  -- auto_generated, health_analysis, diagnosis, user_created, weather_adjusted
    health_trigger TEXT,  -- What health condition triggered this event
    diagnosis_trigger TEXT,  -- What diagnosis triggered this event
    
    -- Weather adjustment tracking
    adjustment_reason TEXT,
    adjusted_at TIMESTAMP,
    
    -- Reminders
    reminders_enabled BOOLEAN DEFAULT TRUE,
    reminder_days_before INTEGER DEFAULT 1,
    reminder_sent BOOLEAN DEFAULT FALSE,
    reminder_sent_at TIMESTAMP,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_scheduled_events_plot_id ON scheduled_events(plot_id);
CREATE INDEX idx_scheduled_events_user_id ON scheduled_events(user_id);
CREATE INDEX idx_scheduled_events_scheduled_date ON scheduled_events(scheduled_date);
CREATE INDEX idx_scheduled_events_status ON scheduled_events(status);
CREATE INDEX idx_scheduled_events_event_type ON scheduled_events(event_type);
CREATE INDEX idx_scheduled_events_priority ON scheduled_events(priority);
CREATE INDEX idx_scheduled_events_source ON scheduled_events(source);

CREATE INDEX idx_scheduled_events_user_status_date ON scheduled_events(user_id, status, scheduled_date);
CREATE INDEX idx_scheduled_events_plot_status_date ON scheduled_events(plot_id, status, scheduled_date);


ALTER TABLE digital_plots ENABLE ROW LEVEL SECURITY;
ALTER TABLE growth_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE pest_disease_diagnoses ENABLE ROW LEVEL SECURITY;
ALTER TABLE harvest_forecasts ENABLE ROW LEVEL SECURITY;

-- Digital Plots Policies
CREATE POLICY "Users can view their own plots"
    ON digital_plots FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own plots"
    ON digital_plots FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own plots"
    ON digital_plots FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own plots"
    ON digital_plots FOR DELETE
    USING (auth.uid() = user_id);

-- Growth Logs Policies
CREATE POLICY "Users can view their own logs"
    ON growth_logs FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own logs"
    ON growth_logs FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own logs"
    ON growth_logs FOR UPDATE
    USING (auth.uid() = user_id);

-- Pest/Disease Diagnoses Policies
CREATE POLICY "Users can view their own diagnoses"
    ON pest_disease_diagnoses FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own diagnoses"
    ON pest_disease_diagnoses FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own diagnoses"
    ON pest_disease_diagnoses FOR UPDATE
    USING (auth.uid() = user_id);

-- Harvest Forecasts Policies
CREATE POLICY "Users can view their own forecasts"
    ON harvest_forecasts FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own forecasts"
    ON harvest_forecasts FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own forecasts"
    ON harvest_forecasts FOR UPDATE
    USING (auth.uid() = user_id);

-- Scheduled Events Policies
CREATE POLICY "Users can view their own events"
    ON scheduled_events FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own events"
    ON scheduled_events FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own events"
    ON scheduled_events FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own events"
    ON scheduled_events FOR DELETE
    USING (auth.uid() = user_id);

-- ============================================================
-- FUNCTIONS AND TRIGGERS
-- ============================================================

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add trigger to digital_plots
CREATE TRIGGER update_digital_plots_updated_at
    BEFORE UPDATE ON digital_plots
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add trigger to scheduled_events
CREATE TRIGGER update_scheduled_events_updated_at
    BEFORE UPDATE ON scheduled_events
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to calculate average health score for a plot
CREATE OR REPLACE FUNCTION get_plot_average_health(plot_uuid UUID)
RETURNS DECIMAL AS $$
DECLARE
    avg_health DECIMAL;
BEGIN
    SELECT AVG((health_analysis->>'overall_health_score')::INTEGER)
    INTO avg_health
    FROM growth_logs
    WHERE plot_id = plot_uuid
    AND health_analysis IS NOT NULL;
    
    RETURN COALESCE(avg_health, 0);
END;
$$ LANGUAGE plpgsql;

-- Function to get latest health score for a plot
CREATE OR REPLACE FUNCTION get_plot_latest_health(plot_uuid UUID)
RETURNS INTEGER AS $$
DECLARE
    latest_health INTEGER;
BEGIN
    SELECT (health_analysis->>'overall_health_score')::INTEGER
    INTO latest_health
    FROM growth_logs
    WHERE plot_id = plot_uuid
    AND health_analysis IS NOT NULL
    ORDER BY timestamp DESC
    LIMIT 1;
    
    RETURN COALESCE(latest_health, 0);
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- SAMPLE DATA FOR TESTING
-- ============================================================

-- Note: Insert sample data after user profiles are created
-- This schema provides the foundation for comprehensive growth tracking

-- ============================================================
-- SCHEMA SUMMARY
-- ============================================================

/*
This schema implements a comprehensive growth tracking system with:

1. DIGITAL PLOT SETUP
   - Plot profiles with crop and location data
   - AI-powered soil analysis
   - Initial planting documentation

2. REGULAR CHECK-INS
   - Growth logs with multiple images
   - AI health analysis (health score, chlorophyll, nitrogen, water stress)
   - Growth rate tracking vs previous logs
   - Biomarker monitoring

3. PEST & DISEASE DIAGNOSIS
   - AI detection of pests and diseases
   - Regional risk assessment (nearby plots)
   - Impact assessment on yield and quality
   - Comprehensive treatment plans

4. HARVEST FORECASTING
   - Predicted harvest dates
   - Quality score predictions (A+ to C-)
   - Yield estimates
   - Recommendations for improvement

All with row-level security for multi-tenant privacy.
*/
