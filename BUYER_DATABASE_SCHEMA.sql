-- =====================================================
-- AGROSHIELD BUYER-FOCUSED DATABASE SCHEMA
-- =====================================================
-- Complete database schema for the Buyer side of AgroShield
-- This includes all tables, policies, triggers, and functions
-- specifically designed for buyer operations
-- =====================================================

-- =====================================================
-- 1. BUYER PROFILES TABLE (Enhanced)
-- =====================================================

CREATE TABLE IF NOT EXISTS buyer_profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT UNIQUE NOT NULL,
  full_name TEXT NOT NULL,
  phone_number TEXT,
  
  -- Company Information
  company_name TEXT NOT NULL,
  business_type TEXT NOT NULL CHECK (business_type IN (
    'retailer', 'wholesaler', 'processor', 'restaurant', 
    'hotel', 'supermarket', 'food_service', 'export', 'other'
  )),
  business_registration_number TEXT,
  tax_id TEXT,
  
  -- Business Details
  buying_capacity DECIMAL(10, 2), -- kg per month
  preferred_crops TEXT[], -- crops they regularly buy
  buying_frequency TEXT CHECK (buying_frequency IN ('daily', 'weekly', 'bi-weekly', 'monthly', 'seasonal')),
  minimum_order_quantity DECIMAL(10, 2), -- kg
  maximum_order_quantity DECIMAL(10, 2), -- kg
  
  -- Location & Delivery
  primary_address TEXT,
  delivery_addresses JSONB[], -- [{name: 'Warehouse 1', address: '...', lat: x, lng: y}]
  latitude DECIMAL(10, 8),
  longitude DECIMAL(11, 8),
  delivery_zones TEXT[], -- areas they operate in
  
  -- Payment & Credit
  payment_methods TEXT[], -- ['cash', 'mobile_money', 'bank_transfer', 'credit_terms']
  credit_limit DECIMAL(10, 2), -- if offering credit
  credit_terms_days INTEGER, -- payment terms in days
  bank_account_details JSONB, -- {bank_name, account_number, account_name}
  
  -- Certifications & Requirements
  required_certifications TEXT[], -- certifications they require from farmers
  quality_standards TEXT[], -- quality standards they follow
  organic_only BOOLEAN DEFAULT FALSE,
  accepts_seasonal_produce BOOLEAN DEFAULT TRUE,
  
  -- Profile & Verification
  profile_image_url TEXT,
  company_logo_url TEXT,
  business_license_url TEXT,
  is_verified BOOLEAN DEFAULT FALSE,
  verification_documents TEXT[],
  verification_status TEXT DEFAULT 'pending' CHECK (verification_status IN ('pending', 'verified', 'rejected')),
  verified_at TIMESTAMPTZ,
  
  -- Rating & Reviews
  rating DECIMAL(3, 2) DEFAULT 0.00,
  total_ratings INTEGER DEFAULT 0,
  total_orders INTEGER DEFAULT 0,
  successful_orders INTEGER DEFAULT 0,
  cancelled_orders INTEGER DEFAULT 0,
  
  -- Business Hours & Contact
  business_hours JSONB, -- {monday: {open: '08:00', close: '17:00'}, ...}
  contact_person TEXT,
  contact_phone TEXT,
  contact_email TEXT,
  website_url TEXT,
  
  -- Preferences
  notification_preferences JSONB, -- {email: true, sms: true, push: true}
  preferred_language TEXT DEFAULT 'en',
  currency TEXT DEFAULT 'KES',
  
  -- Status
  account_status TEXT DEFAULT 'active' CHECK (account_status IN ('active', 'suspended', 'inactive', 'banned')),
  
  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  last_login_at TIMESTAMPTZ
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_buyer_profiles_business_type ON buyer_profiles(business_type);
CREATE INDEX IF NOT EXISTS idx_buyer_profiles_location ON buyer_profiles(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_buyer_profiles_verification_status ON buyer_profiles(verification_status);
CREATE INDEX IF NOT EXISTS idx_buyer_profiles_account_status ON buyer_profiles(account_status);

-- =====================================================
-- 2. BUYER ORDERS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS buyer_orders (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  order_number TEXT UNIQUE NOT NULL,
  
  -- Parties
  buyer_id UUID NOT NULL REFERENCES buyer_profiles(id) ON DELETE CASCADE,
  farmer_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  listing_id UUID REFERENCES crop_listings(id) ON DELETE SET NULL,
  
  -- Order Details
  crop_name TEXT NOT NULL,
  crop_variety TEXT,
  quantity DECIMAL(10, 2) NOT NULL,
  unit TEXT NOT NULL DEFAULT 'kg',
  price_per_unit DECIMAL(10, 2) NOT NULL,
  total_amount DECIMAL(10, 2) NOT NULL,
  
  -- Quality Requirements
  quality_grade_required TEXT,
  organic_required BOOLEAN DEFAULT FALSE,
  certification_required TEXT[],
  
  -- Status Tracking
  status TEXT DEFAULT 'pending' CHECK (status IN (
    'pending', 'confirmed', 'preparing', 'ready_for_pickup', 
    'in_transit', 'delivered', 'completed', 'cancelled', 'disputed', 'refunded'
  )),
  
  -- Delivery Information
  delivery_method TEXT CHECK (delivery_method IN ('pickup', 'buyer_delivery', 'farmer_delivery', 'third_party')),
  delivery_address TEXT NOT NULL,
  delivery_address_details JSONB, -- {name, address, phone, coordinates}
  preferred_delivery_date DATE,
  actual_delivery_date DATE,
  delivery_time_window TEXT, -- e.g., '08:00-12:00'
  delivery_notes TEXT,
  delivery_contact_name TEXT,
  delivery_contact_phone TEXT,
  
  -- Tracking Information
  tracking_number TEXT,
  delivery_partner TEXT,
  estimated_arrival TIMESTAMPTZ,
  actual_arrival TIMESTAMPTZ,
  
  -- Payment Details
  payment_status TEXT DEFAULT 'unpaid' CHECK (payment_status IN (
    'unpaid', 'partial', 'paid', 'refunded', 'pending_verification'
  )),
  payment_method TEXT CHECK (payment_method IN (
    'cash', 'mobile_money', 'bank_transfer', 'card', 'credit_terms', 'check'
  )),
  payment_reference TEXT,
  payment_date TIMESTAMPTZ,
  payment_amount DECIMAL(10, 2),
  payment_due_date DATE,
  
  -- Additional Costs
  delivery_fee DECIMAL(10, 2) DEFAULT 0.00,
  tax_amount DECIMAL(10, 2) DEFAULT 0.00,
  discount_amount DECIMAL(10, 2) DEFAULT 0.00,
  final_amount DECIMAL(10, 2),
  
  -- Order Fulfillment
  confirmed_at TIMESTAMPTZ,
  confirmed_by UUID REFERENCES buyer_profiles(id),
  prepared_at TIMESTAMPTZ,
  dispatched_at TIMESTAMPTZ,
  delivered_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  
  -- Cancellation & Disputes
  cancelled_at TIMESTAMPTZ,
  cancelled_by UUID, -- buyer or farmer id
  cancellation_reason TEXT,
  dispute_raised_at TIMESTAMPTZ,
  dispute_reason TEXT,
  dispute_status TEXT CHECK (dispute_status IN ('pending', 'resolved', 'escalated')),
  dispute_resolution TEXT,
  
  -- Quality Inspection
  inspection_required BOOLEAN DEFAULT FALSE,
  inspection_completed BOOLEAN DEFAULT FALSE,
  inspection_date TIMESTAMPTZ,
  inspection_notes TEXT,
  quality_accepted BOOLEAN,
  
  -- Invoice & Receipt
  invoice_number TEXT,
  invoice_url TEXT,
  receipt_url TEXT,
  
  -- Notes & Communication
  buyer_notes TEXT,
  farmer_notes TEXT,
  internal_notes TEXT,
  
  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_buyer_orders_buyer ON buyer_orders(buyer_id);
CREATE INDEX IF NOT EXISTS idx_buyer_orders_farmer ON buyer_orders(farmer_id);
CREATE INDEX IF NOT EXISTS idx_buyer_orders_status ON buyer_orders(status);
CREATE INDEX IF NOT EXISTS idx_buyer_orders_payment_status ON buyer_orders(payment_status);
CREATE INDEX IF NOT EXISTS idx_buyer_orders_delivery_date ON buyer_orders(preferred_delivery_date);
CREATE INDEX IF NOT EXISTS idx_buyer_orders_created ON buyer_orders(created_at);

-- =====================================================
-- 3. BUYER SAVED LISTINGS (Favorites/Watchlist)
-- =====================================================

CREATE TABLE IF NOT EXISTS buyer_saved_listings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  buyer_id UUID NOT NULL REFERENCES buyer_profiles(id) ON DELETE CASCADE,
  listing_id UUID NOT NULL REFERENCES crop_listings(id) ON DELETE CASCADE,
  
  -- Save Details
  notes TEXT,
  target_price DECIMAL(10, 2), -- buyer's desired price
  notify_on_price_drop BOOLEAN DEFAULT TRUE,
  notify_on_availability BOOLEAN DEFAULT TRUE,
  
  -- Metadata
  saved_at TIMESTAMPTZ DEFAULT NOW(),
  
  UNIQUE(buyer_id, listing_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_buyer_saved_listings_buyer ON buyer_saved_listings(buyer_id);
CREATE INDEX IF NOT EXISTS idx_buyer_saved_listings_listing ON buyer_saved_listings(listing_id);

-- =====================================================
-- 4. BUYER SEARCH HISTORY
-- =====================================================

CREATE TABLE IF NOT EXISTS buyer_search_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  buyer_id UUID NOT NULL REFERENCES buyer_profiles(id) ON DELETE CASCADE,
  
  -- Search Details
  search_query TEXT,
  search_filters JSONB, -- {crop_name, location, price_range, quality, etc.}
  results_count INTEGER,
  
  -- Metadata
  searched_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_buyer_search_history_buyer ON buyer_search_history(buyer_id);
CREATE INDEX IF NOT EXISTS idx_buyer_search_history_date ON buyer_search_history(searched_at);

-- =====================================================
-- 5. BUYER PRICE ALERTS
-- =====================================================

CREATE TABLE IF NOT EXISTS buyer_price_alerts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  buyer_id UUID NOT NULL REFERENCES buyer_profiles(id) ON DELETE CASCADE,
  
  -- Alert Criteria
  crop_name TEXT NOT NULL,
  target_price DECIMAL(10, 2) NOT NULL,
  alert_type TEXT CHECK (alert_type IN ('below', 'above', 'equals')),
  
  -- Geographic Criteria
  location TEXT,
  max_distance_km DECIMAL(10, 2), -- from buyer's location
  
  -- Quality Criteria
  min_quality_grade TEXT,
  organic_only BOOLEAN DEFAULT FALSE,
  
  -- Alert Status
  is_active BOOLEAN DEFAULT TRUE,
  triggered BOOLEAN DEFAULT FALSE,
  triggered_at TIMESTAMPTZ,
  
  -- Notification
  notification_sent BOOLEAN DEFAULT FALSE,
  notification_sent_at TIMESTAMPTZ,
  
  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  expires_at TIMESTAMPTZ
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_buyer_price_alerts_buyer ON buyer_price_alerts(buyer_id);
CREATE INDEX IF NOT EXISTS idx_buyer_price_alerts_crop ON buyer_price_alerts(crop_name);
CREATE INDEX IF NOT EXISTS idx_buyer_price_alerts_active ON buyer_price_alerts(is_active);

-- =====================================================
-- 6. BUYER PAYMENT HISTORY
-- =====================================================

CREATE TABLE IF NOT EXISTS buyer_payment_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  buyer_id UUID NOT NULL REFERENCES buyer_profiles(id) ON DELETE CASCADE,
  order_id UUID REFERENCES buyer_orders(id) ON DELETE SET NULL,
  
  -- Payment Details
  amount DECIMAL(10, 2) NOT NULL,
  payment_method TEXT NOT NULL,
  payment_reference TEXT,
  transaction_id TEXT,
  
  -- Payment Provider Details
  payment_provider TEXT, -- mpesa, stripe, bank, etc.
  provider_transaction_id TEXT,
  provider_response JSONB,
  
  -- Status
  status TEXT DEFAULT 'pending' CHECK (status IN (
    'pending', 'completed', 'failed', 'refunded', 'cancelled'
  )),
  
  -- Timestamps
  initiated_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  failed_at TIMESTAMPTZ,
  failure_reason TEXT
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_buyer_payment_history_buyer ON buyer_payment_history(buyer_id);
CREATE INDEX IF NOT EXISTS idx_buyer_payment_history_order ON buyer_payment_history(order_id);
CREATE INDEX IF NOT EXISTS idx_buyer_payment_history_status ON buyer_payment_history(status);

-- =====================================================
-- 7. BUYER DELIVERY ADDRESSES
-- =====================================================

CREATE TABLE IF NOT EXISTS buyer_delivery_addresses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  buyer_id UUID NOT NULL REFERENCES buyer_profiles(id) ON DELETE CASCADE,
  
  -- Address Details
  address_name TEXT NOT NULL, -- e.g., 'Main Warehouse', 'Store #1'
  address_line1 TEXT NOT NULL,
  address_line2 TEXT,
  city TEXT,
  state_province TEXT,
  postal_code TEXT,
  country TEXT DEFAULT 'Kenya',
  
  -- Coordinates
  latitude DECIMAL(10, 8),
  longitude DECIMAL(11, 8),
  
  -- Contact
  contact_person TEXT,
  contact_phone TEXT,
  
  -- Delivery Instructions
  delivery_instructions TEXT,
  access_restrictions TEXT,
  
  -- Status
  is_default BOOLEAN DEFAULT FALSE,
  is_active BOOLEAN DEFAULT TRUE,
  
  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_buyer_delivery_addresses_buyer ON buyer_delivery_addresses(buyer_id);
CREATE INDEX IF NOT EXISTS idx_buyer_delivery_addresses_default ON buyer_delivery_addresses(is_default);

-- =====================================================
-- 8. BUYER PURCHASE REQUESTS (Custom Orders)
-- =====================================================

CREATE TABLE IF NOT EXISTS buyer_purchase_requests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  request_number TEXT UNIQUE NOT NULL,
  buyer_id UUID NOT NULL REFERENCES buyer_profiles(id) ON DELETE CASCADE,
  
  -- Request Details
  crop_name TEXT NOT NULL,
  crop_variety TEXT,
  quantity_needed DECIMAL(10, 2) NOT NULL,
  unit TEXT DEFAULT 'kg',
  
  -- Budget & Pricing
  budget_per_unit DECIMAL(10, 2),
  total_budget DECIMAL(10, 2),
  price_negotiable BOOLEAN DEFAULT TRUE,
  
  -- Quality Requirements
  quality_grade TEXT,
  organic_required BOOLEAN DEFAULT FALSE,
  certifications_required TEXT[],
  
  -- Delivery Requirements
  needed_by_date DATE NOT NULL,
  delivery_location TEXT,
  delivery_method_preferred TEXT,
  
  -- Additional Requirements
  requirements_description TEXT,
  sample_required BOOLEAN DEFAULT FALSE,
  inspection_required BOOLEAN DEFAULT FALSE,
  
  -- Status
  status TEXT DEFAULT 'open' CHECK (status IN (
    'open', 'matched', 'negotiating', 'confirmed', 'completed', 'expired', 'cancelled'
  )),
  
  -- Responses
  total_responses INTEGER DEFAULT 0,
  
  -- Visibility
  is_public BOOLEAN DEFAULT TRUE, -- visible to all farmers
  invited_farmers UUID[], -- specific farmers invited
  
  -- Expiry
  expires_at TIMESTAMPTZ,
  
  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_buyer_purchase_requests_buyer ON buyer_purchase_requests(buyer_id);
CREATE INDEX IF NOT EXISTS idx_buyer_purchase_requests_status ON buyer_purchase_requests(status);
CREATE INDEX IF NOT EXISTS idx_buyer_purchase_requests_crop ON buyer_purchase_requests(crop_name);
CREATE INDEX IF NOT EXISTS idx_buyer_purchase_requests_needed_date ON buyer_purchase_requests(needed_by_date);

-- =====================================================
-- 9. FARMER RESPONSES TO PURCHASE REQUESTS
-- =====================================================

CREATE TABLE IF NOT EXISTS purchase_request_responses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  request_id UUID NOT NULL REFERENCES buyer_purchase_requests(id) ON DELETE CASCADE,
  farmer_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  
  -- Response Details
  offered_quantity DECIMAL(10, 2) NOT NULL,
  offered_price_per_unit DECIMAL(10, 2) NOT NULL,
  total_offered_price DECIMAL(10, 2) NOT NULL,
  
  -- Availability
  available_from DATE,
  can_deliver BOOLEAN DEFAULT FALSE,
  delivery_cost DECIMAL(10, 2),
  
  -- Message
  message TEXT,
  
  -- Status
  status TEXT DEFAULT 'pending' CHECK (status IN (
    'pending', 'accepted', 'rejected', 'countered', 'withdrawn'
  )),
  
  -- Timestamps
  responded_at TIMESTAMPTZ DEFAULT NOW(),
  reviewed_at TIMESTAMPTZ,
  
  UNIQUE(request_id, farmer_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_purchase_request_responses_request ON purchase_request_responses(request_id);
CREATE INDEX IF NOT EXISTS idx_purchase_request_responses_farmer ON purchase_request_responses(farmer_id);
CREATE INDEX IF NOT EXISTS idx_purchase_request_responses_status ON purchase_request_responses(status);

-- =====================================================
-- 10. BUYER REVIEWS FOR FARMERS
-- =====================================================

CREATE TABLE IF NOT EXISTS buyer_farmer_reviews (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  buyer_id UUID NOT NULL REFERENCES buyer_profiles(id) ON DELETE CASCADE,
  farmer_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  order_id UUID REFERENCES buyer_orders(id) ON DELETE SET NULL,
  
  -- Overall Rating
  rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
  review_text TEXT,
  
  -- Detailed Ratings
  product_quality_rating INTEGER CHECK (product_quality_rating >= 1 AND product_quality_rating <= 5),
  packaging_rating INTEGER CHECK (packaging_rating >= 1 AND packaging_rating <= 5),
  communication_rating INTEGER CHECK (communication_rating >= 1 AND communication_rating <= 5),
  delivery_timeliness_rating INTEGER CHECK (delivery_timeliness_rating >= 1 AND delivery_timeliness_rating <= 5),
  value_for_money_rating INTEGER CHECK (value_for_money_rating >= 1 AND value_for_money_rating <= 5),
  
  -- Recommendations
  would_buy_again BOOLEAN,
  recommended_to_others BOOLEAN,
  
  -- Images
  review_images TEXT[], -- photos of received products
  
  -- Farmer Response
  farmer_response TEXT,
  farmer_responded_at TIMESTAMPTZ,
  
  -- Moderation
  is_verified_purchase BOOLEAN DEFAULT TRUE,
  is_flagged BOOLEAN DEFAULT FALSE,
  flag_reason TEXT,
  is_visible BOOLEAN DEFAULT TRUE,
  
  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  UNIQUE(buyer_id, order_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_buyer_farmer_reviews_buyer ON buyer_farmer_reviews(buyer_id);
CREATE INDEX IF NOT EXISTS idx_buyer_farmer_reviews_farmer ON buyer_farmer_reviews(farmer_id);
CREATE INDEX IF NOT EXISTS idx_buyer_farmer_reviews_rating ON buyer_farmer_reviews(rating);

-- =====================================================
-- 11. BUYER NOTIFICATIONS
-- =====================================================

CREATE TABLE IF NOT EXISTS buyer_notifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  buyer_id UUID NOT NULL REFERENCES buyer_profiles(id) ON DELETE CASCADE,
  
  -- Notification Details
  type TEXT NOT NULL CHECK (type IN (
    'new_listing', 'price_drop', 'order_confirmed', 'order_preparing',
    'order_dispatched', 'order_delivered', 'payment_received',
    'review_received', 'purchase_request_response', 'dispute_update',
    'farmer_message', 'system_update', 'promotion'
  )),
  title TEXT NOT NULL,
  message TEXT NOT NULL,
  
  -- Related Entities
  related_entity_type TEXT, -- order, listing, request, etc.
  related_entity_id UUID,
  
  -- Rich Content
  image_url TEXT,
  action_url TEXT,
  action_text TEXT,
  
  -- Status
  is_read BOOLEAN DEFAULT FALSE,
  read_at TIMESTAMPTZ,
  
  -- Priority
  priority TEXT DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
  
  -- Delivery
  sent_via TEXT[], -- ['push', 'email', 'sms']
  
  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  expires_at TIMESTAMPTZ
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_buyer_notifications_buyer ON buyer_notifications(buyer_id);
CREATE INDEX IF NOT EXISTS idx_buyer_notifications_read ON buyer_notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_buyer_notifications_type ON buyer_notifications(type);
CREATE INDEX IF NOT EXISTS idx_buyer_notifications_created ON buyer_notifications(created_at DESC);

-- =====================================================
-- 12. BUYER ANALYTICS & INSIGHTS
-- =====================================================

CREATE TABLE IF NOT EXISTS buyer_analytics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  buyer_id UUID NOT NULL REFERENCES buyer_profiles(id) ON DELETE CASCADE,
  
  -- Period
  period_type TEXT CHECK (period_type IN ('daily', 'weekly', 'monthly', 'yearly')),
  period_start DATE NOT NULL,
  period_end DATE NOT NULL,
  
  -- Order Statistics
  total_orders INTEGER DEFAULT 0,
  completed_orders INTEGER DEFAULT 0,
  cancelled_orders INTEGER DEFAULT 0,
  total_spent DECIMAL(12, 2) DEFAULT 0.00,
  average_order_value DECIMAL(10, 2) DEFAULT 0.00,
  
  -- Product Statistics
  top_crops JSONB, -- [{crop: 'Tomatoes', quantity: 500, spend: 50000}, ...]
  total_quantity_purchased DECIMAL(10, 2) DEFAULT 0.00,
  
  -- Supplier Statistics
  total_suppliers INTEGER DEFAULT 0,
  top_suppliers JSONB, -- [{farmer_id, name, orders_count, total_spent}, ...]
  
  -- Quality Metrics
  average_product_rating DECIMAL(3, 2),
  quality_issues_count INTEGER DEFAULT 0,
  
  -- Financial
  total_savings DECIMAL(10, 2), -- from discounts, deals
  average_price_per_kg DECIMAL(10, 2),
  
  -- Delivery
  on_time_delivery_rate DECIMAL(5, 2), -- percentage
  average_delivery_time_hours DECIMAL(6, 2),
  
  -- Generated Insights
  insights JSONB, -- AI-generated insights
  recommendations JSONB, -- purchasing recommendations
  
  -- Metadata
  generated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_buyer_analytics_buyer ON buyer_analytics(buyer_id);
CREATE INDEX IF NOT EXISTS idx_buyer_analytics_period ON buyer_analytics(period_start, period_end);

-- =====================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE buyer_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE buyer_orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE buyer_saved_listings ENABLE ROW LEVEL SECURITY;
ALTER TABLE buyer_search_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE buyer_price_alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE buyer_payment_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE buyer_delivery_addresses ENABLE ROW LEVEL SECURITY;
ALTER TABLE buyer_purchase_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE purchase_request_responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE buyer_farmer_reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE buyer_notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE buyer_analytics ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Buyers can read own profile" ON buyer_profiles;
DROP POLICY IF EXISTS "Buyers can update own profile" ON buyer_profiles;
DROP POLICY IF EXISTS "Buyers can insert own profile" ON buyer_profiles;
DROP POLICY IF EXISTS "Farmers can view buyer profiles" ON buyer_profiles;

DROP POLICY IF EXISTS "Buyers can view own orders" ON buyer_orders;
DROP POLICY IF EXISTS "Buyers can create orders" ON buyer_orders;
DROP POLICY IF EXISTS "Buyers can update own orders" ON buyer_orders;
DROP POLICY IF EXISTS "Farmers can view their orders" ON buyer_orders;

DROP POLICY IF EXISTS "Buyers can manage saved listings" ON buyer_saved_listings;
DROP POLICY IF EXISTS "Buyers can view own search history" ON buyer_search_history;
DROP POLICY IF EXISTS "Buyers can manage price alerts" ON buyer_price_alerts;
DROP POLICY IF EXISTS "Buyers can view payment history" ON buyer_payment_history;
DROP POLICY IF EXISTS "Buyers can manage delivery addresses" ON buyer_delivery_addresses;
DROP POLICY IF EXISTS "Buyers can manage purchase requests" ON buyer_purchase_requests;
DROP POLICY IF EXISTS "Farmers can view public purchase requests" ON buyer_purchase_requests;
DROP POLICY IF EXISTS "Farmers can respond to requests" ON purchase_request_responses;
DROP POLICY IF EXISTS "Buyers can view responses" ON purchase_request_responses;
DROP POLICY IF EXISTS "Buyers can create reviews" ON buyer_farmer_reviews;
DROP POLICY IF EXISTS "Public can view reviews" ON buyer_farmer_reviews;
DROP POLICY IF EXISTS "Buyers can view own notifications" ON buyer_notifications;
DROP POLICY IF EXISTS "Buyers can view own analytics" ON buyer_analytics;

-- BUYER PROFILES POLICIES
CREATE POLICY "Buyers can read own profile"
  ON buyer_profiles FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "Buyers can update own profile"
  ON buyer_profiles FOR UPDATE
  USING (auth.uid() = id);

CREATE POLICY "Buyers can insert own profile"
  ON buyer_profiles FOR INSERT
  WITH CHECK (auth.uid() = id);

CREATE POLICY "Farmers can view buyer profiles"
  ON buyer_profiles FOR SELECT
  USING (is_verified = true AND account_status = 'active');

-- BUYER ORDERS POLICIES
CREATE POLICY "Buyers can view own orders"
  ON buyer_orders FOR SELECT
  USING (auth.uid() = buyer_id);

CREATE POLICY "Buyers can create orders"
  ON buyer_orders FOR INSERT
  WITH CHECK (auth.uid() = buyer_id);

CREATE POLICY "Buyers can update own orders"
  ON buyer_orders FOR UPDATE
  USING (auth.uid() = buyer_id);

CREATE POLICY "Farmers can view their orders"
  ON buyer_orders FOR SELECT
  USING (auth.uid() = farmer_id);

-- SAVED LISTINGS POLICIES
CREATE POLICY "Buyers can manage saved listings"
  ON buyer_saved_listings FOR ALL
  USING (auth.uid() = buyer_id);

-- SEARCH HISTORY POLICIES
CREATE POLICY "Buyers can view own search history"
  ON buyer_search_history FOR ALL
  USING (auth.uid() = buyer_id);

-- PRICE ALERTS POLICIES
CREATE POLICY "Buyers can manage price alerts"
  ON buyer_price_alerts FOR ALL
  USING (auth.uid() = buyer_id);

-- PAYMENT HISTORY POLICIES
CREATE POLICY "Buyers can view payment history"
  ON buyer_payment_history FOR SELECT
  USING (auth.uid() = buyer_id);

-- DELIVERY ADDRESSES POLICIES
CREATE POLICY "Buyers can manage delivery addresses"
  ON buyer_delivery_addresses FOR ALL
  USING (auth.uid() = buyer_id);

-- PURCHASE REQUESTS POLICIES
CREATE POLICY "Buyers can manage purchase requests"
  ON buyer_purchase_requests FOR ALL
  USING (auth.uid() = buyer_id);

CREATE POLICY "Farmers can view public purchase requests"
  ON buyer_purchase_requests FOR SELECT
  USING (is_public = true OR auth.uid() = ANY(invited_farmers));

-- PURCHASE REQUEST RESPONSES POLICIES
CREATE POLICY "Farmers can respond to requests"
  ON purchase_request_responses FOR INSERT
  WITH CHECK (auth.uid() = farmer_id);

CREATE POLICY "Buyers can view responses"
  ON purchase_request_responses FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM buyer_purchase_requests
      WHERE id = request_id AND buyer_id = auth.uid()
    )
  );

-- REVIEWS POLICIES
CREATE POLICY "Buyers can create reviews"
  ON buyer_farmer_reviews FOR INSERT
  WITH CHECK (auth.uid() = buyer_id);

CREATE POLICY "Public can view reviews"
  ON buyer_farmer_reviews FOR SELECT
  USING (is_visible = true);

-- NOTIFICATIONS POLICIES
CREATE POLICY "Buyers can view own notifications"
  ON buyer_notifications FOR SELECT
  USING (auth.uid() = buyer_id);

CREATE POLICY "Buyers can update own notifications"
  ON buyer_notifications FOR UPDATE
  USING (auth.uid() = buyer_id);

-- ANALYTICS POLICIES
CREATE POLICY "Buyers can view own analytics"
  ON buyer_analytics FOR SELECT
  USING (auth.uid() = buyer_id);

-- =====================================================
-- TRIGGERS AND FUNCTIONS
-- =====================================================

-- Function to create buyer profile after signup
CREATE OR REPLACE FUNCTION handle_new_buyer()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.raw_user_meta_data->>'user_type' = 'buyer' THEN
    INSERT INTO public.buyer_profiles (
      id, 
      email, 
      full_name, 
      company_name, 
      business_type
    )
    VALUES (
      NEW.id,
      NEW.email,
      NEW.raw_user_meta_data->>'full_name',
      NEW.raw_user_meta_data->>'company_name',
      COALESCE(NEW.raw_user_meta_data->>'business_type', 'retailer')
    );
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger for new buyer creation
DROP TRIGGER IF EXISTS on_auth_buyer_created ON auth.users;
CREATE TRIGGER on_auth_buyer_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION handle_new_buyer();

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_buyer_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at triggers
DROP TRIGGER IF EXISTS update_buyer_profiles_updated_at ON buyer_profiles;
CREATE TRIGGER update_buyer_profiles_updated_at
  BEFORE UPDATE ON buyer_profiles
  FOR EACH ROW EXECUTE FUNCTION update_buyer_updated_at();

DROP TRIGGER IF EXISTS update_buyer_orders_updated_at ON buyer_orders;
CREATE TRIGGER update_buyer_orders_updated_at
  BEFORE UPDATE ON buyer_orders
  FOR EACH ROW EXECUTE FUNCTION update_buyer_updated_at();

DROP TRIGGER IF EXISTS update_buyer_delivery_addresses_updated_at ON buyer_delivery_addresses;
CREATE TRIGGER update_buyer_delivery_addresses_updated_at
  BEFORE UPDATE ON buyer_delivery_addresses
  FOR EACH ROW EXECUTE FUNCTION update_buyer_updated_at();

-- Function to generate order number
CREATE OR REPLACE FUNCTION generate_buyer_order_number()
RETURNS TRIGGER AS $$
BEGIN
  NEW.order_number = 'BO-' || TO_CHAR(NOW(), 'YYYYMMDD') || '-' || LPAD(nextval('buyer_orders_sequence')::TEXT, 6, '0');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create sequence for buyer order numbers
CREATE SEQUENCE IF NOT EXISTS buyer_orders_sequence START 1;

-- Trigger for buyer order number generation
DROP TRIGGER IF EXISTS generate_buyer_order_number_trigger ON buyer_orders;
CREATE TRIGGER generate_buyer_order_number_trigger
  BEFORE INSERT ON buyer_orders
  FOR EACH ROW EXECUTE FUNCTION generate_buyer_order_number();

-- Function to generate purchase request number
CREATE OR REPLACE FUNCTION generate_purchase_request_number()
RETURNS TRIGGER AS $$
BEGIN
  NEW.request_number = 'PR-' || TO_CHAR(NOW(), 'YYYYMMDD') || '-' || LPAD(nextval('purchase_requests_sequence')::TEXT, 6, '0');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create sequence for purchase requests
CREATE SEQUENCE IF NOT EXISTS purchase_requests_sequence START 1;

-- Trigger for purchase request number generation
DROP TRIGGER IF EXISTS generate_purchase_request_number_trigger ON buyer_purchase_requests;
CREATE TRIGGER generate_purchase_request_number_trigger
  BEFORE INSERT ON buyer_purchase_requests
  FOR EACH ROW EXECUTE FUNCTION generate_purchase_request_number();

-- Function to update buyer stats after order
CREATE OR REPLACE FUNCTION update_buyer_order_stats()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.status = 'completed' AND OLD.status != 'completed' THEN
    UPDATE buyer_profiles
    SET 
      total_orders = total_orders + 1,
      successful_orders = successful_orders + 1
    WHERE id = NEW.buyer_id;
  ELSIF NEW.status = 'cancelled' AND OLD.status != 'cancelled' THEN
    UPDATE buyer_profiles
    SET cancelled_orders = cancelled_orders + 1
    WHERE id = NEW.buyer_id;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for buyer stats update
DROP TRIGGER IF EXISTS update_buyer_stats_trigger ON buyer_orders;
CREATE TRIGGER update_buyer_stats_trigger
  AFTER UPDATE ON buyer_orders
  FOR EACH ROW EXECUTE FUNCTION update_buyer_order_stats();

-- =====================================================
-- UTILITY FUNCTIONS FOR BACKEND
-- =====================================================

-- Function to get buyer dashboard stats
CREATE OR REPLACE FUNCTION get_buyer_dashboard_stats(p_buyer_id UUID)
RETURNS TABLE (
  total_orders INTEGER,
  pending_orders INTEGER,
  completed_orders INTEGER,
  total_spent DECIMAL,
  active_price_alerts INTEGER,
  saved_listings INTEGER,
  unread_notifications INTEGER
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    (SELECT COUNT(*)::INTEGER FROM buyer_orders WHERE buyer_id = p_buyer_id),
    (SELECT COUNT(*)::INTEGER FROM buyer_orders WHERE buyer_id = p_buyer_id AND status IN ('pending', 'confirmed', 'preparing')),
    (SELECT COUNT(*)::INTEGER FROM buyer_orders WHERE buyer_id = p_buyer_id AND status = 'completed'),
    (SELECT COALESCE(SUM(final_amount), 0) FROM buyer_orders WHERE buyer_id = p_buyer_id AND status = 'completed'),
    (SELECT COUNT(*)::INTEGER FROM buyer_price_alerts WHERE buyer_id = p_buyer_id AND is_active = true),
    (SELECT COUNT(*)::INTEGER FROM buyer_saved_listings WHERE buyer_id = p_buyer_id),
    (SELECT COUNT(*)::INTEGER FROM buyer_notifications WHERE buyer_id = p_buyer_id AND is_read = false);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to search available listings for buyer
CREATE OR REPLACE FUNCTION search_listings_for_buyer(
  p_buyer_id UUID,
  p_crop_name TEXT DEFAULT NULL,
  p_max_price DECIMAL DEFAULT NULL,
  p_organic_only BOOLEAN DEFAULT FALSE,
  p_max_distance_km DECIMAL DEFAULT NULL
)
RETURNS TABLE (
  listing_id UUID,
  crop_name TEXT,
  quantity DECIMAL,
  price_per_unit DECIMAL,
  farmer_name TEXT,
  farmer_rating DECIMAL,
  distance_km DECIMAL
) AS $$
DECLARE
  v_buyer_lat DECIMAL;
  v_buyer_lng DECIMAL;
BEGIN
  -- Get buyer's coordinates
  SELECT latitude, longitude INTO v_buyer_lat, v_buyer_lng
  FROM buyer_profiles
  WHERE id = p_buyer_id;
  
  RETURN QUERY
  SELECT 
    cl.id,
    cl.crop_name,
    cl.quantity,
    cl.price_per_unit,
    p.full_name,
    p.rating,
    CASE 
      WHEN v_buyer_lat IS NOT NULL AND cl.latitude IS NOT NULL THEN
        (6371 * acos(cos(radians(v_buyer_lat)) * cos(radians(cl.latitude)) * 
        cos(radians(cl.longitude) - radians(v_buyer_lng)) + 
        sin(radians(v_buyer_lat)) * sin(radians(cl.latitude))))
      ELSE NULL
    END AS distance
  FROM crop_listings cl
  JOIN profiles p ON p.id = cl.farmer_id
  WHERE cl.status = 'available'
    AND (p_crop_name IS NULL OR cl.crop_name ILIKE '%' || p_crop_name || '%')
    AND (p_max_price IS NULL OR cl.price_per_unit <= p_max_price)
    AND (NOT p_organic_only OR cl.is_organic = true)
  HAVING (p_max_distance_km IS NULL OR distance <= p_max_distance_km OR distance IS NULL)
  ORDER BY distance NULLS LAST, cl.price_per_unit ASC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- Check all buyer tables created
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name LIKE '%buyer%'
ORDER BY table_name;

-- Count buyers
SELECT COUNT(*) as total_buyers
FROM buyer_profiles;

-- =====================================================
-- COMPLETION MESSAGE
-- =====================================================
-- Buyer database schema setup complete!
-- This schema includes:
-- ✓ Enhanced buyer profiles with business details
-- ✓ Order management with full lifecycle tracking
-- ✓ Saved listings and favorites
-- ✓ Search history and price alerts
-- ✓ Payment history and multiple delivery addresses
-- ✓ Purchase requests (RFQ) system
-- ✓ Farmer responses to purchase requests
-- ✓ Review and rating system
-- ✓ Notifications
-- ✓ Analytics and insights
-- ✓ Complete RLS policies
-- ✓ Automated triggers and functions
-- =====================================================
