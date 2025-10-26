-- ============================================================================
-- PLOT CREATION & MANAGEMENT SCHEMA
-- Manual plot creation with image upload support
-- ============================================================================

-- The digital_plots table already exists from ADVANCED_GROWTH_TRACKING_SCHEMA.sql
-- This schema adds support for manual plot creation and image management

-- ============================================================================
-- PLOT IMAGES TABLE
-- Stores multiple images per plot (initial, progress, harvest, etc.)
-- ============================================================================

CREATE TABLE IF NOT EXISTS plot_images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plot_id UUID REFERENCES digital_plots(id) ON DELETE CASCADE,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    image_url TEXT NOT NULL,
    image_type TEXT NOT NULL DEFAULT 'progress', -- initial, progress, soil, pest, harvest
    description TEXT,
    captured_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb, -- Additional image metadata
    
    -- Indexes
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_plot_images_plot_id ON plot_images(plot_id);
CREATE INDEX IF NOT EXISTS idx_plot_images_user_id ON plot_images(user_id);
CREATE INDEX IF NOT EXISTS idx_plot_images_type ON plot_images(image_type);
CREATE INDEX IF NOT EXISTS idx_plot_images_captured_at ON plot_images(captured_at DESC);

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) FOR PLOT IMAGES
-- ============================================================================

ALTER TABLE plot_images ENABLE ROW LEVEL SECURITY;

-- Users can view their own plot images
CREATE POLICY "Users can view own plot images"
    ON plot_images FOR SELECT
    USING (auth.uid() = user_id);

-- Users can insert their own plot images
CREATE POLICY "Users can insert own plot images"
    ON plot_images FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Users can update their own plot images
CREATE POLICY "Users can update own plot images"
    ON plot_images FOR UPDATE
    USING (auth.uid() = user_id);

-- Users can delete their own plot images
CREATE POLICY "Users can delete own plot images"
    ON plot_images FOR DELETE
    USING (auth.uid() = user_id);

-- ============================================================================
-- PLOT CREATION VALIDATION FUNCTION
-- ============================================================================

CREATE OR REPLACE FUNCTION validate_plot_creation()
RETURNS TRIGGER AS $$
BEGIN
    -- Ensure crop_name is provided
    IF NEW.crop_name IS NULL OR NEW.crop_name = '' THEN
        RAISE EXCEPTION 'Crop name is required';
    END IF;
    
    -- Ensure plot_name is provided
    IF NEW.plot_name IS NULL OR NEW.plot_name = '' THEN
        RAISE EXCEPTION 'Plot name is required';
    END IF;
    
    -- Ensure planting_date is not in the future
    IF NEW.planting_date > CURRENT_TIMESTAMP THEN
        RAISE EXCEPTION 'Planting date cannot be in the future';
    END IF;
    
    -- Ensure area_size is positive if provided
    IF NEW.area_size IS NOT NULL AND NEW.area_size <= 0 THEN
        RAISE EXCEPTION 'Area size must be positive';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach validation trigger to digital_plots
DROP TRIGGER IF EXISTS validate_plot_creation_trigger ON digital_plots;
CREATE TRIGGER validate_plot_creation_trigger
    BEFORE INSERT OR UPDATE ON digital_plots
    FOR EACH ROW
    EXECUTE FUNCTION validate_plot_creation();

-- ============================================================================
-- PLOT STATISTICS VIEW
-- Aggregate statistics for user's plots
-- ============================================================================

CREATE OR REPLACE VIEW user_plot_statistics AS
SELECT 
    user_id,
    COUNT(DISTINCT id) as total_plots,
    COUNT(DISTINCT crop_name) as unique_crops,
    SUM(area_size) as total_area,
    COUNT(CASE WHEN setup_completed_at IS NOT NULL THEN 1 END) as completed_plots,
    COUNT(CASE WHEN setup_completed_at IS NULL THEN 1 END) as incomplete_plots,
    MIN(planting_date) as earliest_planting,
    MAX(planting_date) as latest_planting
FROM digital_plots
GROUP BY user_id;

-- Grant access to view
GRANT SELECT ON user_plot_statistics TO authenticated;

-- ============================================================================
-- FUNCTION: Get plot with images and events
-- ============================================================================

CREATE OR REPLACE FUNCTION get_plot_complete_details(plot_uuid UUID)
RETURNS JSON AS $$
DECLARE
    result JSON;
BEGIN
    SELECT json_build_object(
        'plot', (SELECT row_to_json(p.*) FROM digital_plots p WHERE p.id = plot_uuid),
        'images', (
            SELECT COALESCE(json_agg(i.*), '[]'::json)
            FROM plot_images i
            WHERE i.plot_id = plot_uuid
            ORDER BY i.captured_at DESC
        ),
        'events', (
            SELECT COALESCE(json_agg(e.*), '[]'::json)
            FROM scheduled_events e
            WHERE e.plot_id = plot_uuid
            ORDER BY e.scheduled_date ASC
        ),
        'logs', (
            SELECT COALESCE(json_agg(l.*), '[]'::json)
            FROM growth_logs l
            WHERE l.plot_id = plot_uuid
            ORDER BY l.timestamp DESC
            LIMIT 10
        )
    ) INTO result;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================================

COMMENT ON TABLE plot_images IS 'Stores multiple images per plot for tracking growth progress';
COMMENT ON COLUMN plot_images.image_type IS 'Type of image: initial, progress, soil, pest, harvest';
COMMENT ON COLUMN plot_images.metadata IS 'Additional metadata like GPS coordinates, weather conditions, etc.';
COMMENT ON FUNCTION get_plot_complete_details IS 'Returns complete plot details with images, events, and logs';
