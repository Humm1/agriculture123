-- =====================================================
-- AGROSHIELD COMPLETE DATABASE SCHEMA
-- =====================================================
-- This script creates all tables, policies, triggers, and functions
-- for the AgroShield application including:
-- - User profiles (farmers and buyers)
-- - Crop listings and marketplace
-- - Predictions (pest, disease, storage, climate)
-- - Orders and transactions
-- - Farm intelligence and analytics
-- =====================================================

-- =====================================================
-- 1. USER PROFILES TABLE
-- =====================================================

-- Drop existing table if needed (be careful in production!)
-- DROP TABLE IF EXISTS profiles CASCADE;

CREATE TABLE IF NOT EXISTS profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT UNIQUE NOT NULL,
  full_name TEXT,
  phone_number TEXT,
  location TEXT,
  latitude DECIMAL(10, 8),
  longitude DECIMAL(11, 8),
  user_type TEXT NOT NULL CHECK (user_type IN ('farmer', 'buyer')),
  
  -- Farmer-specific fields
  farm_size DECIMAL(10, 2), -- in acres/hectares
  crops_grown TEXT[], -- array of crop names
  farming_experience INTEGER, -- years of experience
  farm_name TEXT,
  farming_methods TEXT[], -- e.g., organic, conventional, permaculture
  
  -- Buyer-specific fields
  company_name TEXT,
  business_type TEXT, -- e.g., retailer, wholesaler, processor, restaurant
  buying_capacity DECIMAL(10, 2), -- in kg/tons per month
  preferred_crops TEXT[], -- array of crop names they buy
  business_registration_number TEXT,
  
  -- Common fields
  profile_image_url TEXT,
  is_verified BOOLEAN DEFAULT FALSE,
  verification_documents TEXT[], -- URLs to verification documents
  rating DECIMAL(3, 2) DEFAULT 0.00, -- average rating out of 5
  total_ratings INTEGER DEFAULT 0,
  
  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_profiles_user_type ON profiles(user_type);
CREATE INDEX IF NOT EXISTS idx_profiles_location ON profiles(location);
CREATE INDEX IF NOT EXISTS idx_profiles_email ON profiles(email);

-- =====================================================
-- 2. CROP LISTINGS TABLE (Farmer's produce for sale)
-- =====================================================

CREATE TABLE IF NOT EXISTS crop_listings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  farmer_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  
  -- Crop details
  crop_name TEXT NOT NULL,
  crop_variety TEXT,
  quantity DECIMAL(10, 2) NOT NULL, -- in kg
  unit TEXT DEFAULT 'kg', -- kg, tons, bags, etc.
  price_per_unit DECIMAL(10, 2) NOT NULL,
  
  -- Quality and certification
  quality_grade TEXT, -- A, B, C or Premium, Standard, Economy
  is_organic BOOLEAN DEFAULT FALSE,
  certifications TEXT[], -- array of certification names
  
  -- Availability
  available_from DATE,
  available_until DATE,
  harvest_date DATE,
  status TEXT DEFAULT 'available' CHECK (status IN ('available', 'reserved', 'sold', 'expired')),
  
  -- Location
  location TEXT,
  latitude DECIMAL(10, 8),
  longitude DECIMAL(11, 8),
  
  -- Images and description
  images TEXT[], -- array of image URLs
  description TEXT,
  
  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_crop_listings_farmer ON crop_listings(farmer_id);
CREATE INDEX IF NOT EXISTS idx_crop_listings_crop_name ON crop_listings(crop_name);
CREATE INDEX IF NOT EXISTS idx_crop_listings_status ON crop_listings(status);
CREATE INDEX IF NOT EXISTS idx_crop_listings_available_from ON crop_listings(available_from);

-- =====================================================
-- 3. ORDERS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS orders (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  order_number TEXT UNIQUE NOT NULL,
  
  -- Parties
  buyer_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  farmer_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  listing_id UUID NOT NULL REFERENCES crop_listings(id) ON DELETE CASCADE,
  
  -- Order details
  quantity DECIMAL(10, 2) NOT NULL,
  unit TEXT NOT NULL,
  price_per_unit DECIMAL(10, 2) NOT NULL,
  total_amount DECIMAL(10, 2) NOT NULL,
  
  -- Status tracking
  status TEXT DEFAULT 'pending' CHECK (status IN (
    'pending', 'confirmed', 'preparing', 'ready_for_pickup', 
    'in_transit', 'delivered', 'completed', 'cancelled', 'disputed'
  )),
  
  -- Delivery details
  delivery_method TEXT, -- pickup, delivery, shipping
  delivery_address TEXT,
  delivery_date DATE,
  delivery_notes TEXT,
  
  -- Payment
  payment_status TEXT DEFAULT 'unpaid' CHECK (payment_status IN (
    'unpaid', 'partial', 'paid', 'refunded'
  )),
  payment_method TEXT, -- cash, mobile_money, bank_transfer, card
  payment_reference TEXT,
  
  -- Tracking
  confirmed_at TIMESTAMPTZ,
  delivered_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  cancelled_at TIMESTAMPTZ,
  cancellation_reason TEXT,
  
  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_orders_buyer ON orders(buyer_id);
CREATE INDEX IF NOT EXISTS idx_orders_farmer ON orders(farmer_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_order_number ON orders(order_number);

-- =====================================================
-- 4. PEST PREDICTIONS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS pest_predictions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  farmer_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  
  -- Image data
  image_url TEXT NOT NULL,
  image_metadata JSONB, -- original filename, size, etc.
  
  -- Prediction results
  pest_detected TEXT NOT NULL,
  confidence_score DECIMAL(5, 4) NOT NULL, -- 0.0000 to 1.0000
  severity TEXT CHECK (severity IN ('low', 'moderate', 'high', 'critical')),
  
  -- Additional predictions (if model returns multiple)
  alternative_predictions JSONB, -- [{pest: 'name', confidence: 0.85}, ...]
  
  -- Recommendations
  treatment_recommendations TEXT[],
  preventive_measures TEXT[],
  estimated_damage TEXT,
  
  -- Context
  crop_affected TEXT,
  farm_location TEXT,
  latitude DECIMAL(10, 8),
  longitude DECIMAL(11, 8),
  
  -- User feedback (for model improvement)
  user_confirmed BOOLEAN,
  user_feedback TEXT,
  actual_pest TEXT, -- if user corrects the prediction
  
  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_pest_predictions_farmer ON pest_predictions(farmer_id);
CREATE INDEX IF NOT EXISTS idx_pest_predictions_pest ON pest_predictions(pest_detected);
CREATE INDEX IF NOT EXISTS idx_pest_predictions_date ON pest_predictions(created_at);

-- =====================================================
-- 5. DISEASE PREDICTIONS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS disease_predictions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  farmer_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  
  -- Image data
  image_url TEXT NOT NULL,
  image_metadata JSONB,
  
  -- Prediction results
  disease_detected TEXT NOT NULL,
  confidence_score DECIMAL(5, 4) NOT NULL,
  severity TEXT CHECK (severity IN ('low', 'moderate', 'high', 'critical')),
  
  -- Additional predictions
  alternative_predictions JSONB,
  
  -- Recommendations
  treatment_recommendations TEXT[],
  preventive_measures TEXT[],
  estimated_yield_loss TEXT,
  contagion_risk TEXT, -- low, medium, high
  
  -- Context
  crop_affected TEXT,
  growth_stage TEXT, -- seedling, vegetative, flowering, fruiting
  farm_location TEXT,
  latitude DECIMAL(10, 8),
  longitude DECIMAL(11, 8),
  
  -- Environmental context
  weather_conditions JSONB, -- temperature, humidity, rainfall
  
  -- User feedback
  user_confirmed BOOLEAN,
  user_feedback TEXT,
  actual_disease TEXT,
  treatment_applied TEXT,
  treatment_effectiveness TEXT, -- worked, partially_worked, did_not_work
  
  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_disease_predictions_farmer ON disease_predictions(farmer_id);
CREATE INDEX IF NOT EXISTS idx_disease_predictions_disease ON disease_predictions(disease_detected);
CREATE INDEX IF NOT EXISTS idx_disease_predictions_date ON disease_predictions(created_at);

-- =====================================================
-- 6. STORAGE PREDICTIONS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS storage_predictions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  farmer_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  
  -- Image data
  image_url TEXT NOT NULL,
  image_metadata JSONB,
  
  -- Storage assessment
  storage_condition TEXT NOT NULL CHECK (storage_condition IN (
    'excellent', 'good', 'fair', 'poor', 'critical'
  )),
  confidence_score DECIMAL(5, 4) NOT NULL,
  
  -- Detected issues
  issues_detected TEXT[], -- mold, pests, moisture, temperature, ventilation
  risk_level TEXT CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),
  
  -- Predictions
  estimated_shelf_life INTEGER, -- in days
  spoilage_risk_percentage DECIMAL(5, 2),
  quality_degradation_rate TEXT, -- slow, moderate, fast
  
  -- Recommendations
  immediate_actions TEXT[],
  improvements_needed TEXT[],
  optimal_storage_conditions JSONB, -- {temperature: 20, humidity: 60, ventilation: 'good'}
  
  -- Context
  crop_stored TEXT,
  storage_type TEXT, -- warehouse, silo, cold_storage, open_air
  storage_duration INTEGER, -- days already in storage
  quantity_stored DECIMAL(10, 2),
  
  -- Environmental readings (if available)
  temperature DECIMAL(5, 2),
  humidity DECIMAL(5, 2),
  
  -- User feedback
  user_confirmed BOOLEAN,
  user_feedback TEXT,
  actual_outcome TEXT,
  
  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_storage_predictions_farmer ON storage_predictions(farmer_id);
CREATE INDEX IF NOT EXISTS idx_storage_predictions_condition ON storage_predictions(storage_condition);
CREATE INDEX IF NOT EXISTS idx_storage_predictions_date ON storage_predictions(created_at);

-- =====================================================
-- 7. CLIMATE PREDICTIONS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS climate_predictions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  farmer_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  
  -- Location
  location TEXT NOT NULL,
  latitude DECIMAL(10, 8) NOT NULL,
  longitude DECIMAL(11, 8) NOT NULL,
  
  -- Prediction period
  prediction_date DATE NOT NULL,
  prediction_range TEXT, -- daily, weekly, monthly, seasonal
  
  -- Weather predictions
  temperature_min DECIMAL(5, 2),
  temperature_max DECIMAL(5, 2),
  temperature_avg DECIMAL(5, 2),
  precipitation_mm DECIMAL(7, 2),
  precipitation_probability DECIMAL(5, 2), -- percentage
  humidity DECIMAL(5, 2),
  wind_speed DECIMAL(5, 2),
  
  -- Agricultural insights
  frost_risk BOOLEAN,
  drought_risk TEXT CHECK (drought_risk IN ('none', 'low', 'moderate', 'high', 'severe')),
  flood_risk TEXT CHECK (flood_risk IN ('none', 'low', 'moderate', 'high', 'severe')),
  heat_stress_risk BOOLEAN,
  
  -- Crop-specific recommendations
  crop_type TEXT,
  planting_favorable BOOLEAN,
  irrigation_needed BOOLEAN,
  irrigation_amount DECIMAL(7, 2), -- in mm or liters
  harvest_conditions TEXT, -- excellent, good, fair, poor
  
  -- Recommendations
  farming_activities_recommended TEXT[],
  precautions TEXT[],
  
  -- Data source
  data_source TEXT, -- open-meteo, weather_api, etc.
  confidence_level TEXT CHECK (confidence_level IN ('low', 'medium', 'high')),
  
  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_climate_predictions_farmer ON climate_predictions(farmer_id);
CREATE INDEX IF NOT EXISTS idx_climate_predictions_location ON climate_predictions(location);
CREATE INDEX IF NOT EXISTS idx_climate_predictions_date ON climate_predictions(prediction_date);

-- =====================================================
-- 8. FARM INTELLIGENCE REPORTS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS farm_intelligence_reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  farmer_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  
  -- Report details
  report_type TEXT NOT NULL CHECK (report_type IN (
    'weekly_summary', 'monthly_summary', 'seasonal_analysis', 
    'pest_alert', 'disease_outbreak', 'market_opportunity'
  )),
  title TEXT NOT NULL,
  summary TEXT,
  
  -- Analytics data
  total_predictions INTEGER,
  pest_detections INTEGER,
  disease_detections INTEGER,
  storage_assessments INTEGER,
  
  -- Insights
  top_threats TEXT[],
  recommended_actions TEXT[],
  market_insights JSONB,
  weather_patterns JSONB,
  
  -- Trends
  pest_trend TEXT, -- increasing, stable, decreasing
  disease_trend TEXT,
  yield_forecast JSONB,
  
  -- Report content
  detailed_analysis TEXT,
  charts_data JSONB, -- data for generating charts
  
  -- Metadata
  report_period_start DATE,
  report_period_end DATE,
  generated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_farm_intelligence_farmer ON farm_intelligence_reports(farmer_id);
CREATE INDEX IF NOT EXISTS idx_farm_intelligence_type ON farm_intelligence_reports(report_type);
CREATE INDEX IF NOT EXISTS idx_farm_intelligence_date ON farm_intelligence_reports(generated_at);

-- =====================================================
-- 9. RATINGS AND REVIEWS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS ratings_reviews (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Parties involved
  reviewer_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  reviewee_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  order_id UUID REFERENCES orders(id) ON DELETE SET NULL,
  
  -- Rating
  rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
  review_text TEXT,
  
  -- Categories (optional detailed ratings)
  quality_rating INTEGER CHECK (quality_rating >= 1 AND quality_rating <= 5),
  communication_rating INTEGER CHECK (communication_rating >= 1 AND communication_rating <= 5),
  timeliness_rating INTEGER CHECK (timeliness_rating >= 1 AND timeliness_rating <= 5),
  
  -- Response
  response_text TEXT,
  responded_at TIMESTAMPTZ,
  
  -- Moderation
  is_flagged BOOLEAN DEFAULT FALSE,
  flag_reason TEXT,
  is_verified BOOLEAN DEFAULT FALSE, -- verified purchase/transaction
  
  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_ratings_reviewer ON ratings_reviews(reviewer_id);
CREATE INDEX IF NOT EXISTS idx_ratings_reviewee ON ratings_reviews(reviewee_id);
CREATE INDEX IF NOT EXISTS idx_ratings_order ON ratings_reviews(order_id);

-- =====================================================
-- 10. NOTIFICATIONS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS notifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  
  -- Notification details
  type TEXT NOT NULL CHECK (type IN (
    'order_received', 'order_confirmed', 'order_delivered',
    'payment_received', 'new_listing', 'price_alert',
    'pest_alert', 'disease_alert', 'weather_alert',
    'message', 'rating_received', 'system_update'
  )),
  title TEXT NOT NULL,
  message TEXT NOT NULL,
  
  -- Related entities
  related_entity_type TEXT, -- order, listing, prediction, etc.
  related_entity_id UUID,
  
  -- Status
  is_read BOOLEAN DEFAULT FALSE,
  read_at TIMESTAMPTZ,
  
  -- Action
  action_url TEXT, -- deep link to specific screen
  action_text TEXT,
  
  -- Priority
  priority TEXT DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
  
  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(type);
CREATE INDEX IF NOT EXISTS idx_notifications_date ON notifications(created_at);

-- =====================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE crop_listings ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE pest_predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE disease_predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE storage_predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE climate_predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE farm_intelligence_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE ratings_reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can read own profile" ON profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON profiles;
DROP POLICY IF EXISTS "Users can insert own profile" ON profiles;
DROP POLICY IF EXISTS "Public profiles are viewable by everyone" ON profiles;

DROP POLICY IF EXISTS "Farmers can create listings" ON crop_listings;
DROP POLICY IF EXISTS "Farmers can update own listings" ON crop_listings;
DROP POLICY IF EXISTS "Everyone can view available listings" ON crop_listings;
DROP POLICY IF EXISTS "Farmers can delete own listings" ON crop_listings;

DROP POLICY IF EXISTS "Buyers can create orders" ON orders;
DROP POLICY IF EXISTS "Users can view own orders" ON orders;
DROP POLICY IF EXISTS "Users can update own orders" ON orders;

DROP POLICY IF EXISTS "Farmers can create predictions" ON pest_predictions;
DROP POLICY IF EXISTS "Farmers can view own predictions" ON pest_predictions;
DROP POLICY IF EXISTS "Farmers can update own predictions" ON pest_predictions;

DROP POLICY IF EXISTS "Farmers can create disease predictions" ON disease_predictions;
DROP POLICY IF EXISTS "Farmers can view own disease predictions" ON disease_predictions;
DROP POLICY IF EXISTS "Farmers can update own disease predictions" ON disease_predictions;

DROP POLICY IF EXISTS "Farmers can create storage predictions" ON storage_predictions;
DROP POLICY IF EXISTS "Farmers can view own storage predictions" ON storage_predictions;
DROP POLICY IF EXISTS "Farmers can update own storage predictions" ON storage_predictions;

DROP POLICY IF EXISTS "Farmers can create climate predictions" ON climate_predictions;
DROP POLICY IF EXISTS "Farmers can view own climate predictions" ON climate_predictions;

DROP POLICY IF EXISTS "Farmers can view own reports" ON farm_intelligence_reports;

DROP POLICY IF EXISTS "Users can create reviews" ON ratings_reviews;
DROP POLICY IF EXISTS "Users can view reviews" ON ratings_reviews;

DROP POLICY IF EXISTS "Users can view own notifications" ON notifications;
DROP POLICY IF EXISTS "Users can update own notifications" ON notifications;

-- PROFILES POLICIES
CREATE POLICY "Users can read own profile"
  ON profiles FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
  ON profiles FOR UPDATE
  USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile"
  ON profiles FOR INSERT
  WITH CHECK (auth.uid() = id);

CREATE POLICY "Public profiles are viewable by everyone"
  ON profiles FOR SELECT
  USING (true); -- Allow all authenticated users to view profiles

-- CROP LISTINGS POLICIES
CREATE POLICY "Farmers can create listings"
  ON crop_listings FOR INSERT
  WITH CHECK (auth.uid() = farmer_id);

CREATE POLICY "Farmers can update own listings"
  ON crop_listings FOR UPDATE
  USING (auth.uid() = farmer_id);

CREATE POLICY "Everyone can view available listings"
  ON crop_listings FOR SELECT
  USING (true);

CREATE POLICY "Farmers can delete own listings"
  ON crop_listings FOR DELETE
  USING (auth.uid() = farmer_id);

-- ORDERS POLICIES
CREATE POLICY "Buyers can create orders"
  ON orders FOR INSERT
  WITH CHECK (auth.uid() = buyer_id);

CREATE POLICY "Users can view own orders"
  ON orders FOR SELECT
  USING (auth.uid() = buyer_id OR auth.uid() = farmer_id);

CREATE POLICY "Users can update own orders"
  ON orders FOR UPDATE
  USING (auth.uid() = buyer_id OR auth.uid() = farmer_id);

-- PEST PREDICTIONS POLICIES
CREATE POLICY "Farmers can create predictions"
  ON pest_predictions FOR INSERT
  WITH CHECK (auth.uid() = farmer_id);

CREATE POLICY "Farmers can view own predictions"
  ON pest_predictions FOR SELECT
  USING (auth.uid() = farmer_id);

CREATE POLICY "Farmers can update own predictions"
  ON pest_predictions FOR UPDATE
  USING (auth.uid() = farmer_id);

-- DISEASE PREDICTIONS POLICIES
CREATE POLICY "Farmers can create disease predictions"
  ON disease_predictions FOR INSERT
  WITH CHECK (auth.uid() = farmer_id);

CREATE POLICY "Farmers can view own disease predictions"
  ON disease_predictions FOR SELECT
  USING (auth.uid() = farmer_id);

CREATE POLICY "Farmers can update own disease predictions"
  ON disease_predictions FOR UPDATE
  USING (auth.uid() = farmer_id);

-- STORAGE PREDICTIONS POLICIES
CREATE POLICY "Farmers can create storage predictions"
  ON storage_predictions FOR INSERT
  WITH CHECK (auth.uid() = farmer_id);

CREATE POLICY "Farmers can view own storage predictions"
  ON storage_predictions FOR SELECT
  USING (auth.uid() = farmer_id);

CREATE POLICY "Farmers can update own storage predictions"
  ON storage_predictions FOR UPDATE
  USING (auth.uid() = farmer_id);

-- CLIMATE PREDICTIONS POLICIES
CREATE POLICY "Farmers can create climate predictions"
  ON climate_predictions FOR INSERT
  WITH CHECK (auth.uid() = farmer_id);

CREATE POLICY "Farmers can view own climate predictions"
  ON climate_predictions FOR SELECT
  USING (auth.uid() = farmer_id);

-- FARM INTELLIGENCE REPORTS POLICIES
CREATE POLICY "Farmers can view own reports"
  ON farm_intelligence_reports FOR SELECT
  USING (auth.uid() = farmer_id);

-- RATINGS AND REVIEWS POLICIES
CREATE POLICY "Users can create reviews"
  ON ratings_reviews FOR INSERT
  WITH CHECK (auth.uid() = reviewer_id);

CREATE POLICY "Users can view reviews"
  ON ratings_reviews FOR SELECT
  USING (true);

-- NOTIFICATIONS POLICIES
CREATE POLICY "Users can view own notifications"
  ON notifications FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can update own notifications"
  ON notifications FOR UPDATE
  USING (auth.uid() = user_id);

-- =====================================================
-- TRIGGERS AND FUNCTIONS
-- =====================================================

-- Function to automatically create profile after user signup
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  -- Extract user_type from raw_user_meta_data
  IF NEW.raw_user_meta_data->>'user_type' IS NULL THEN
    RAISE EXCEPTION 'user_type is required in signup metadata';
  END IF;

  INSERT INTO public.profiles (id, email, user_type, full_name)
  VALUES (
    NEW.id,
    NEW.email,
    NEW.raw_user_meta_data->>'user_type',
    NEW.raw_user_meta_data->>'full_name'
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger for new user creation
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION handle_new_user();

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at trigger to relevant tables
DROP TRIGGER IF EXISTS update_profiles_updated_at ON profiles;
CREATE TRIGGER update_profiles_updated_at
  BEFORE UPDATE ON profiles
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_crop_listings_updated_at ON crop_listings;
CREATE TRIGGER update_crop_listings_updated_at
  BEFORE UPDATE ON crop_listings
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_orders_updated_at ON orders;
CREATE TRIGGER update_orders_updated_at
  BEFORE UPDATE ON orders
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_ratings_reviews_updated_at ON ratings_reviews;
CREATE TRIGGER update_ratings_reviews_updated_at
  BEFORE UPDATE ON ratings_reviews
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to update user rating after new review
CREATE OR REPLACE FUNCTION update_user_rating()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE profiles
  SET 
    rating = (
      SELECT AVG(rating)::DECIMAL(3,2)
      FROM ratings_reviews
      WHERE reviewee_id = NEW.reviewee_id
    ),
    total_ratings = (
      SELECT COUNT(*)
      FROM ratings_reviews
      WHERE reviewee_id = NEW.reviewee_id
    )
  WHERE id = NEW.reviewee_id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for rating updates
DROP TRIGGER IF EXISTS on_rating_created ON ratings_reviews;
CREATE TRIGGER on_rating_created
  AFTER INSERT ON ratings_reviews
  FOR EACH ROW EXECUTE FUNCTION update_user_rating();

-- Function to generate order number
CREATE OR REPLACE FUNCTION generate_order_number()
RETURNS TRIGGER AS $$
BEGIN
  NEW.order_number = 'ORD-' || TO_CHAR(NOW(), 'YYYYMMDD') || '-' || LPAD(nextval('orders_sequence')::TEXT, 6, '0');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create sequence for order numbers
CREATE SEQUENCE IF NOT EXISTS orders_sequence START 1;

-- Trigger for order number generation
DROP TRIGGER IF EXISTS generate_order_number_trigger ON orders;
CREATE TRIGGER generate_order_number_trigger
  BEFORE INSERT ON orders
  FOR EACH ROW EXECUTE FUNCTION generate_order_number();

-- =====================================================
-- UTILITY FUNCTIONS FOR BACKEND
-- =====================================================

-- Function to get user profile with type
CREATE OR REPLACE FUNCTION get_user_profile(user_id UUID)
RETURNS TABLE (
  id UUID,
  email TEXT,
  full_name TEXT,
  user_type TEXT,
  phone_number TEXT,
  location TEXT,
  farm_name TEXT,
  company_name TEXT,
  rating DECIMAL,
  is_verified BOOLEAN
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    p.id,
    p.email,
    p.full_name,
    p.user_type,
    p.phone_number,
    p.location,
    p.farm_name,
    p.company_name,
    p.rating,
    p.is_verified
  FROM profiles p
  WHERE p.id = user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get farmer statistics
CREATE OR REPLACE FUNCTION get_farmer_stats(farmer_id UUID)
RETURNS TABLE (
  total_listings INTEGER,
  active_listings INTEGER,
  total_orders INTEGER,
  completed_orders INTEGER,
  total_predictions INTEGER,
  pest_count INTEGER,
  disease_count INTEGER,
  storage_count INTEGER,
  average_rating DECIMAL
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    (SELECT COUNT(*)::INTEGER FROM crop_listings WHERE farmer_id = farmer_id),
    (SELECT COUNT(*)::INTEGER FROM crop_listings WHERE farmer_id = farmer_id AND status = 'available'),
    (SELECT COUNT(*)::INTEGER FROM orders WHERE farmer_id = farmer_id),
    (SELECT COUNT(*)::INTEGER FROM orders WHERE farmer_id = farmer_id AND status = 'completed'),
    (SELECT COUNT(*)::INTEGER FROM pest_predictions WHERE farmer_id = farmer_id) +
    (SELECT COUNT(*)::INTEGER FROM disease_predictions WHERE farmer_id = farmer_id) +
    (SELECT COUNT(*)::INTEGER FROM storage_predictions WHERE farmer_id = farmer_id),
    (SELECT COUNT(*)::INTEGER FROM pest_predictions WHERE farmer_id = farmer_id),
    (SELECT COUNT(*)::INTEGER FROM disease_predictions WHERE farmer_id = farmer_id),
    (SELECT COUNT(*)::INTEGER FROM storage_predictions WHERE farmer_id = farmer_id),
    (SELECT rating FROM profiles WHERE id = farmer_id);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- SAMPLE DATA (Optional - for testing)
-- =====================================================

-- Note: Uncomment below to insert sample data for testing
-- This should only be run in development/testing environments

/*
-- Sample Farmer Profile (requires existing auth.users entry)
INSERT INTO profiles (id, email, full_name, user_type, farm_name, farm_size, crops_grown, location)
VALUES (
  'sample-uuid-1', -- Replace with actual UUID from auth.users
  'farmer@test.com',
  'John Farmer',
  'farmer',
  'Green Valley Farm',
  50.5,
  ARRAY['Tomatoes', 'Cabbage', 'Maize'],
  'Nairobi, Kenya'
);

-- Sample Buyer Profile
INSERT INTO profiles (id, email, full_name, user_type, company_name, business_type, buying_capacity)
VALUES (
  'sample-uuid-2', -- Replace with actual UUID from auth.users
  'buyer@test.com',
  'Jane Buyer',
  'buyer',
  'Fresh Mart Ltd',
  'retailer',
  1000.00
);
*/

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- Check all tables created
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Check RLS policies
SELECT schemaname, tablename, policyname 
FROM pg_policies 
WHERE schemaname = 'public'
ORDER BY tablename, policyname;

-- Count users by type
SELECT user_type, COUNT(*) as count
FROM profiles
GROUP BY user_type;

-- =====================================================
-- COMPLETION MESSAGE
-- =====================================================
-- Database schema setup complete!
-- Next steps:
-- 1. Run this script in your Supabase SQL Editor
-- 2. Verify all tables are created
-- 3. Test RLS policies with different user types
-- 4. Update backend API to use these tables
-- 5. Test image upload and prediction storage
-- =====================================================
