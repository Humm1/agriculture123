-- AgroShield Supabase Database Setup
-- Run this SQL in your Supabase SQL Editor (Database → SQL Editor → New Query)

-- 1. Create profiles table
CREATE TABLE IF NOT EXISTS public.profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT NOT NULL,
  user_type TEXT NOT NULL CHECK (user_type IN ('farmer', 'buyer')),
  full_name TEXT,
  phone_number TEXT,
  location TEXT,
  county TEXT,
  subcounty TEXT,
  village TEXT,
  latitude DOUBLE PRECISION,
  longitude DOUBLE PRECISION,
  
  -- Farmer-specific fields
  farm_size DECIMAL(10,2), -- in acres
  crops_grown TEXT[], -- array of crop types
  farming_experience INTEGER, -- years of experience
  
  -- Buyer-specific fields
  company_name TEXT,
  business_type TEXT, -- 'retailer', 'wholesaler', 'processor', 'exporter'
  buying_capacity DECIMAL(10,2), -- monthly capacity in tons
  
  -- Common fields
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  -- Indexes for better performance
  CONSTRAINT unique_email UNIQUE(email)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_profiles_user_type ON public.profiles(user_type);
CREATE INDEX IF NOT EXISTS idx_profiles_county ON public.profiles(county);
CREATE INDEX IF NOT EXISTS idx_profiles_email ON public.profiles(email);

-- 2. Enable Row Level Security (RLS)
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- 3. Create RLS policies (drop existing ones first to avoid conflicts)
DROP POLICY IF EXISTS "Users can read own profile" ON public.profiles;
CREATE POLICY "Users can read own profile" ON public.profiles
  FOR SELECT
  USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can update own profile" ON public.profiles;
CREATE POLICY "Users can update own profile" ON public.profiles
  FOR UPDATE
  USING (auth.uid() = id);

DROP POLICY IF EXISTS "Anyone can insert profile" ON public.profiles;
CREATE POLICY "Anyone can insert profile" ON public.profiles
  FOR INSERT
  WITH CHECK (true);

-- 4. Create function to automatically create profile on user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
DECLARE
  v_user_type TEXT;
BEGIN
  -- Extract user_type from metadata, default to 'farmer' if not specified
  v_user_type := COALESCE(NEW.raw_user_meta_data->>'user_type', 'farmer');
  
  -- Ensure user_type is valid
  IF v_user_type NOT IN ('farmer', 'buyer') THEN
    v_user_type := 'farmer';
  END IF;
  
  -- Insert profile with user_type
  INSERT INTO public.profiles (
    id, 
    email, 
    user_type,
    full_name,
    phone_number,
    location,
    county,
    subcounty,
    village,
    created_at
  )
  VALUES (
    NEW.id,
    NEW.email,
    v_user_type,
    COALESCE(NEW.raw_user_meta_data->>'full_name', ''),
    COALESCE(NEW.raw_user_meta_data->>'phone_number', ''),
    COALESCE(NEW.raw_user_meta_data->>'location', ''),
    COALESCE(NEW.raw_user_meta_data->>'county', ''),
    COALESCE(NEW.raw_user_meta_data->>'subcounty', ''),
    COALESCE(NEW.raw_user_meta_data->>'village', ''),
    NOW()
  )
  ON CONFLICT (id) DO UPDATE SET
    user_type = EXCLUDED.user_type,
    full_name = EXCLUDED.full_name,
    phone_number = EXCLUDED.phone_number,
    location = EXCLUDED.location,
    county = EXCLUDED.county,
    subcounty = EXCLUDED.subcounty,
    village = EXCLUDED.village,
    updated_at = NOW();
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 5. Create trigger to call the function on signup
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_new_user();

-- 6. Create updated_at trigger function
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 7. Create trigger for updated_at
DROP TRIGGER IF EXISTS set_updated_at ON public.profiles;
CREATE TRIGGER set_updated_at
  BEFORE UPDATE ON public.profiles
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_updated_at();

-- 8. Grant permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON public.profiles TO anon, authenticated;

-- Verify setup
SELECT 
  tablename,
  schemaname
FROM pg_tables
WHERE tablename = 'profiles';

-- View all profiles with user types (for debugging)
SELECT 
  id,
  email,
  user_type,
  full_name,
  county,
  created_at
FROM public.profiles
ORDER BY created_at DESC;

-- Count users by type
SELECT 
  user_type,
  COUNT(*) as count
FROM public.profiles
GROUP BY user_type;
