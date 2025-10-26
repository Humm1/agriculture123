-- ============================================================================
-- AI-POWERED PLOT ANALYTICS & DISEASE PREDICTION SYSTEM
-- Multi-image upload, disease detection, weather analysis, fertilizer recommendations
-- ============================================================================

-- ============================================================================
-- 1. PLOT DATASETS TABLE
-- Stores multiple images and sensor data per plot for AI training/analysis
-- ============================================================================

CREATE TABLE IF NOT EXISTS plot_datasets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plot_id UUID REFERENCES digital_plots(id) ON DELETE CASCADE,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    
    -- Image/Data Information
    file_url TEXT NOT NULL,
    file_type TEXT NOT NULL DEFAULT 'image', -- image, sensor_data, soil_sample
    data_category TEXT NOT NULL, -- leaf, stem, fruit, soil, whole_plant, aerial
    
    -- Metadata
    captured_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    gps_location JSONB, -- {lat, lng, accuracy}
    weather_conditions JSONB, -- {temp, humidity, rainfall} at capture time
    growth_stage TEXT, -- seedling, vegetative, flowering, fruiting, harvest
    
    -- Labels for training
    disease_label TEXT, -- User-labeled or AI-detected disease
    health_status TEXT, -- healthy, stressed, diseased, pest_damage
    confidence_score FLOAT, -- AI confidence (0-1)
    
    -- Analysis status
    analyzed BOOLEAN DEFAULT false,
    analysis_results JSONB, -- AI analysis output
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_plot_datasets_plot_id ON plot_datasets(plot_id);
CREATE INDEX idx_plot_datasets_user_id ON plot_datasets(user_id);
CREATE INDEX idx_plot_datasets_category ON plot_datasets(data_category);
CREATE INDEX idx_plot_datasets_analyzed ON plot_datasets(analyzed);
CREATE INDEX idx_plot_datasets_captured ON plot_datasets(captured_at DESC);

-- ============================================================================
-- 2. AI PREDICTIONS TABLE
-- Stores disease predictions, weather impact forecasts, yield estimates
-- ============================================================================

CREATE TABLE IF NOT EXISTS ai_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plot_id UUID REFERENCES digital_plots(id) ON DELETE CASCADE,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    dataset_id UUID REFERENCES plot_datasets(id) ON DELETE SET NULL,
    
    -- Prediction Type
    prediction_type TEXT NOT NULL, -- disease, pest, weather_impact, yield, harvest_timing
    
    -- Disease/Pest Detection
    disease_name TEXT,
    disease_severity TEXT, -- low, medium, high, critical
    affected_area_percentage FLOAT, -- % of plant affected
    pest_type TEXT,
    
    -- Predictions
    confidence_score FLOAT NOT NULL, -- 0-1
    risk_level TEXT, -- low, medium, high
    progression_forecast JSONB, -- {days_to_spread: 7, spread_rate: 0.15}
    
    -- Recommendations
    treatment_recommendations JSONB[], -- [{method, cost, effectiveness}]
    preventive_measures TEXT[],
    
    -- Weather Impact
    weather_risk_factors JSONB, -- {high_humidity: true, temp_stress: false}
    optimal_conditions JSONB,
    
    -- Metadata
    model_version TEXT,
    prediction_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE, -- Prediction validity
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ai_predictions_plot_id ON ai_predictions(plot_id);
CREATE INDEX idx_ai_predictions_type ON ai_predictions(prediction_type);
CREATE INDEX idx_ai_predictions_date ON ai_predictions(prediction_date DESC);
CREATE INDEX idx_ai_predictions_risk ON ai_predictions(risk_level);

-- ============================================================================
-- 3. CROP HEALTH METRICS TABLE
-- Real-time health tracking and scoring
-- ============================================================================

CREATE TABLE IF NOT EXISTS crop_health_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plot_id UUID REFERENCES digital_plots(id) ON DELETE CASCADE,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    
    -- Health Scores (0-100)
    overall_health_score FLOAT NOT NULL,
    leaf_health_score FLOAT,
    stem_health_score FLOAT,
    root_health_score FLOAT,
    fruit_health_score FLOAT,
    
    -- Indicators
    vigor_index FLOAT, -- Plant vigor/strength
    stress_indicators JSONB, -- {water_stress: 0.3, nutrient_deficiency: 0.1}
    disease_pressure FLOAT, -- Overall disease risk (0-1)
    pest_pressure FLOAT,
    
    -- Growth Metrics
    growth_rate FLOAT, -- cm/day or similar
    leaf_area_index FLOAT,
    chlorophyll_content FLOAT,
    
    -- Environmental Factors
    weather_stress_score FLOAT,
    soil_quality_score FLOAT,
    
    -- Comparison
    vs_optimal_percentage FLOAT, -- How close to optimal health
    vs_previous_week FLOAT, -- Change from last week
    
    measured_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_crop_health_plot_id ON crop_health_metrics(plot_id);
CREATE INDEX idx_crop_health_measured ON crop_health_metrics(measured_at DESC);

-- ============================================================================
-- 4. FERTILIZER RECOMMENDATIONS TABLE
-- Cost-effective organic vs inorganic fertilizer analysis
-- ============================================================================

CREATE TABLE IF NOT EXISTS fertilizer_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plot_id UUID REFERENCES digital_plots(id) ON DELETE CASCADE,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    
    -- Nutrient Requirements
    nitrogen_needed FLOAT, -- kg/hectare
    phosphorus_needed FLOAT,
    potassium_needed FLOAT,
    micronutrients_needed JSONB, -- {zinc: 2, iron: 1}
    
    -- Organic Options
    organic_options JSONB[], -- [{name, type, quantity, cost, availability}]
    organic_total_cost FLOAT,
    organic_application_method TEXT,
    organic_effectiveness_score FLOAT, -- 0-1
    
    -- Inorganic Options
    inorganic_options JSONB[], -- [{name, npk_ratio, quantity, cost}]
    inorganic_total_cost FLOAT,
    inorganic_application_method TEXT,
    inorganic_effectiveness_score FLOAT,
    
    -- Comparison
    cost_difference FLOAT, -- Organic - Inorganic
    recommended_method TEXT, -- organic, inorganic, hybrid
    reasoning TEXT,
    
    -- Application Schedule
    application_schedule JSONB[], -- [{date, type, amount}]
    expected_results JSONB, -- {yield_increase: 15, health_improvement: 20}
    
    -- Local Availability
    local_suppliers JSONB[], -- [{name, location, contact, prices}]
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    valid_until TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_fertilizer_plot_id ON fertilizer_recommendations(plot_id);
CREATE INDEX idx_fertilizer_created ON fertilizer_recommendations(created_at DESC);

-- ============================================================================
-- 5. WEATHER ANALYSIS TABLE
-- Weather impact on crop health and predictions
-- ============================================================================

CREATE TABLE IF NOT EXISTS weather_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plot_id UUID REFERENCES digital_plots(id) ON DELETE CASCADE,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    
    -- Current Weather Impact
    current_conditions JSONB, -- {temp, humidity, rainfall, wind}
    stress_factors JSONB, -- {heat_stress: true, drought: false}
    optimal_variance JSONB, -- How far from optimal
    
    -- Forecasted Impact (7-14 days)
    forecast_data JSONB[],
    risk_periods JSONB[], -- [{date_range, risk_type, severity}]
    
    -- Disease Risk from Weather
    disease_risk_score FLOAT, -- 0-1 based on weather conditions
    favorable_diseases TEXT[], -- Diseases likely to occur
    
    -- Recommendations
    weather_adjustments JSONB, -- {irrigation: "increase", shade: "required"}
    protective_measures TEXT[],
    
    -- Historical Correlation
    historical_impact JSONB, -- Past weather patterns vs yield
    
    analysis_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_weather_plot_id ON weather_analysis(plot_id);
CREATE INDEX idx_weather_analysis_date ON weather_analysis(analysis_date DESC);

-- ============================================================================
-- 6. DISEASE TRACKING TIMELINE
-- Historical disease progression and treatment effectiveness
-- ============================================================================

CREATE TABLE IF NOT EXISTS disease_timeline (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plot_id UUID REFERENCES digital_plots(id) ON DELETE CASCADE,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    prediction_id UUID REFERENCES ai_predictions(id) ON DELETE CASCADE,
    
    -- Disease Information
    disease_name TEXT NOT NULL,
    detection_date TIMESTAMP WITH TIME ZONE NOT NULL,
    current_severity TEXT, -- low, medium, high, critical, resolved
    
    -- Progression
    progression_history JSONB[], -- [{date, severity, area_affected}]
    spread_rate FLOAT, -- % increase per day
    
    -- Treatment Applied
    treatments_applied JSONB[], -- [{date, method, cost, notes}]
    treatment_effectiveness FLOAT, -- 0-1
    
    -- Outcome
    resolution_date TIMESTAMP WITH TIME ZONE,
    resolution_method TEXT,
    total_cost FLOAT,
    yield_impact_percentage FLOAT, -- % yield loss
    
    -- Lessons Learned
    notes TEXT,
    preventive_actions_for_future TEXT[],
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_disease_timeline_plot_id ON disease_timeline(plot_id);
CREATE INDEX idx_disease_timeline_disease ON disease_timeline(disease_name);
CREATE INDEX idx_disease_timeline_detection ON disease_timeline(detection_date DESC);

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

ALTER TABLE plot_datasets ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE crop_health_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE fertilizer_recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE weather_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE disease_timeline ENABLE ROW LEVEL SECURITY;

-- Plot Datasets Policies
CREATE POLICY "Users view own datasets" ON plot_datasets FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users insert own datasets" ON plot_datasets FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users update own datasets" ON plot_datasets FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users delete own datasets" ON plot_datasets FOR DELETE USING (auth.uid() = user_id);

-- AI Predictions Policies
CREATE POLICY "Users view own predictions" ON ai_predictions FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users insert own predictions" ON ai_predictions FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Crop Health Policies
CREATE POLICY "Users view own health metrics" ON crop_health_metrics FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users insert own health metrics" ON crop_health_metrics FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Fertilizer Policies
CREATE POLICY "Users view own fertilizer recs" ON fertilizer_recommendations FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users insert own fertilizer recs" ON fertilizer_recommendations FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Weather Analysis Policies
CREATE POLICY "Users view own weather analysis" ON weather_analysis FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users insert own weather analysis" ON weather_analysis FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Disease Timeline Policies
CREATE POLICY "Users view own disease timeline" ON disease_timeline FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users insert own disease timeline" ON disease_timeline FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users update own disease timeline" ON disease_timeline FOR UPDATE USING (auth.uid() = user_id);

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function: Get complete plot analytics
CREATE OR REPLACE FUNCTION get_plot_analytics(plot_uuid UUID)
RETURNS JSON AS $$
DECLARE
    result JSON;
BEGIN
    SELECT json_build_object(
        'plot_info', (SELECT row_to_json(p.*) FROM digital_plots p WHERE p.id = plot_uuid),
        'latest_health', (
            SELECT row_to_json(h.*)
            FROM crop_health_metrics h
            WHERE h.plot_id = plot_uuid
            ORDER BY h.measured_at DESC
            LIMIT 1
        ),
        'active_diseases', (
            SELECT COALESCE(json_agg(d.*), '[]'::json)
            FROM disease_timeline d
            WHERE d.plot_id = plot_uuid AND d.resolution_date IS NULL
        ),
        'recent_predictions', (
            SELECT COALESCE(json_agg(p.*), '[]'::json)
            FROM ai_predictions p
            WHERE p.plot_id = plot_uuid
            ORDER BY p.prediction_date DESC
            LIMIT 5
        ),
        'fertilizer_plan', (
            SELECT row_to_json(f.*)
            FROM fertilizer_recommendations f
            WHERE f.plot_id = plot_uuid
            ORDER BY f.created_at DESC
            LIMIT 1
        ),
        'weather_impact', (
            SELECT row_to_json(w.*)
            FROM weather_analysis w
            WHERE w.plot_id = plot_uuid
            ORDER BY w.analysis_date DESC
            LIMIT 1
        ),
        'dataset_count', (
            SELECT COUNT(*) FROM plot_datasets WHERE plot_id = plot_uuid
        )
    ) INTO result;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function: Get disease progression summary
CREATE OR REPLACE FUNCTION get_disease_progression(plot_uuid UUID, disease TEXT)
RETURNS JSON AS $$
DECLARE
    result JSON;
BEGIN
    SELECT json_build_object(
        'disease_name', disease,
        'timeline', (
            SELECT COALESCE(json_agg(d.* ORDER BY d.detection_date DESC), '[]'::json)
            FROM disease_timeline d
            WHERE d.plot_id = plot_uuid AND d.disease_name = disease
        ),
        'total_cost', (
            SELECT COALESCE(SUM(total_cost), 0)
            FROM disease_timeline
            WHERE plot_id = plot_uuid AND disease_name = disease
        ),
        'effectiveness_avg', (
            SELECT COALESCE(AVG(treatment_effectiveness), 0)
            FROM disease_timeline
            WHERE plot_id = plot_uuid AND disease_name = disease
        )
    ) INTO result;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function: Get fertilizer cost comparison
CREATE OR REPLACE FUNCTION compare_fertilizer_costs(plot_uuid UUID)
RETURNS JSON AS $$
DECLARE
    result JSON;
BEGIN
    SELECT json_build_object(
        'organic', (
            SELECT COALESCE(AVG(organic_total_cost), 0)
            FROM fertilizer_recommendations
            WHERE plot_id = plot_uuid
        ),
        'inorganic', (
            SELECT COALESCE(AVG(inorganic_total_cost), 0)
            FROM fertilizer_recommendations
            WHERE plot_id = plot_uuid
        ),
        'recommended_method', (
            SELECT recommended_method
            FROM fertilizer_recommendations
            WHERE plot_id = plot_uuid
            ORDER BY created_at DESC
            LIMIT 1
        ),
        'savings_potential', (
            SELECT COALESCE(AVG(ABS(cost_difference)), 0)
            FROM fertilizer_recommendations
            WHERE plot_id = plot_uuid
        )
    ) INTO result;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- VIEWS FOR ANALYTICS
-- ============================================================================

-- View: Plot Health Summary
CREATE OR REPLACE VIEW plot_health_summary AS
SELECT 
    p.id as plot_id,
    p.plot_name,
    p.crop_name,
    h.overall_health_score,
    h.disease_pressure,
    h.pest_pressure,
    h.vs_optimal_percentage,
    (SELECT COUNT(*) FROM disease_timeline d WHERE d.plot_id = p.id AND d.resolution_date IS NULL) as active_diseases,
    h.measured_at as last_measured
FROM digital_plots p
LEFT JOIN LATERAL (
    SELECT * FROM crop_health_metrics
    WHERE plot_id = p.id
    ORDER BY measured_at DESC
    LIMIT 1
) h ON true;

GRANT SELECT ON plot_health_summary TO authenticated;

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Auto-update disease timeline when new prediction is made
CREATE OR REPLACE FUNCTION create_disease_timeline_from_prediction()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.prediction_type = 'disease' AND NEW.disease_name IS NOT NULL THEN
        INSERT INTO disease_timeline (
            plot_id,
            user_id,
            prediction_id,
            disease_name,
            detection_date,
            current_severity,
            progression_history
        ) VALUES (
            NEW.plot_id,
            NEW.user_id,
            NEW.id,
            NEW.disease_name,
            NEW.prediction_date,
            NEW.disease_severity,
            jsonb_build_array(
                jsonb_build_object(
                    'date', NEW.prediction_date,
                    'severity', NEW.disease_severity,
                    'area_affected', NEW.affected_area_percentage
                )
            )
        )
        ON CONFLICT DO NOTHING;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_create_disease_timeline ON ai_predictions;
CREATE TRIGGER trigger_create_disease_timeline
    AFTER INSERT ON ai_predictions
    FOR EACH ROW
    EXECUTE FUNCTION create_disease_timeline_from_prediction();

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE plot_datasets IS 'Multi-image and sensor data storage for AI training and analysis';
COMMENT ON TABLE ai_predictions IS 'AI-generated predictions for diseases, pests, weather impact, and yields';
COMMENT ON TABLE crop_health_metrics IS 'Real-time crop health scoring and monitoring';
COMMENT ON TABLE fertilizer_recommendations IS 'Cost-effective fertilizer recommendations (organic vs inorganic)';
COMMENT ON TABLE weather_analysis IS 'Weather impact analysis and forecasting for crop health';
COMMENT ON TABLE disease_timeline IS 'Historical disease tracking and treatment effectiveness';
