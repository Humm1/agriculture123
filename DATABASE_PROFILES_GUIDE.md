# 🗄️ Enhanced Database Setup - Farmer & Buyer Profiles

## ✅ What Was Added:

### 1. **Additional Profile Fields**

#### **Farmer-Specific Fields:**
- `farm_size` (DECIMAL) - Farm size in acres
- `crops_grown` (TEXT[]) - Array of crops they grow
- `farming_experience` (INTEGER) - Years of farming experience

#### **Buyer-Specific Fields:**
- `company_name` (TEXT) - Company/business name
- `business_type` (TEXT) - Type: retailer, wholesaler, processor, exporter
- `buying_capacity` (DECIMAL) - Monthly buying capacity in tons

### 2. **Database Indexes**
- Index on `user_type` for fast filtering
- Index on `county` for location-based queries
- Index on `email` for quick lookups
- Unique constraint on email

### 3. **Enhanced Trigger Function**
- Validates `user_type` is either 'farmer' or 'buyer'
- Defaults to 'farmer' if invalid
- Extracts all metadata from registration
- Handles conflicts with UPDATE instead of error

### 4. **Verification Queries**
- View all profiles with user types
- Count users by type (farmer vs buyer)
- Check table structure

---

## 🚀 How to Apply This Setup:

### Step 1: **Run the Updated SQL Script**

1. Go to **Supabase Dashboard** → **SQL Editor**
2. Click **"New Query"**
3. Copy **ALL** the contents of `SUPABASE_DATABASE_SETUP.sql`
4. Paste into the editor
5. Click **"Run"** (or Ctrl+Enter)

### Step 2: **Verify the Setup**

After running the script, you should see results showing:
- ✅ Table created successfully
- ✅ Profiles table exists
- ✅ List of current profiles (if any)
- ✅ Count by user type

### Step 3: **Check the Table Structure**

1. Go to **Table Editor** → **profiles**
2. You should now see these columns:

#### **Common Fields (All Users):**
- `id` - User ID (UUID)
- `email` - Email address
- `user_type` - **'farmer' or 'buyer'** ⭐
- `full_name` - Full name
- `phone_number` - Phone number
- `location` - General location
- `county` - County
- `subcounty` - Sub-county
- `village` - Village
- `latitude` - GPS latitude
- `longitude` - GPS longitude
- `created_at` - Registration date
- `updated_at` - Last update

#### **Farmer-Only Fields:**
- `farm_size` - Farm size in acres
- `crops_grown` - Array of crops
- `farming_experience` - Years of experience

#### **Buyer-Only Fields:**
- `company_name` - Company name
- `business_type` - Business type
- `buying_capacity` - Buying capacity

---

## 🔍 How Profiles Work:

### **When User Registers:**

1. **User fills registration form** and selects "Farmer" or "Buyer"
2. **App calls Supabase signup** with metadata:
   ```javascript
   {
     user_type: 'farmer', // or 'buyer'
     full_name: 'John Doe',
     phone_number: '+1234567890',
     county: 'Nairobi',
     ...
   }
   ```
3. **Trigger automatically creates profile** in `profiles` table
4. **Profile includes user_type** from metadata

### **When User Logs In:**

1. **Auth system verifies credentials**
2. **App fetches user profile** from `profiles` table
3. **Checks `user_type` field**:
   - If `user_type === 'farmer'` → Show Farmer Dashboard
   - If `user_type === 'buyer'` → Show Buyer Dashboard

---

## 🧪 Testing the Setup:

### **Test 1: Register New Farmer**

1. Register with:
   - User Type: **Farmer**
   - Email: `testfarmer@example.com`
   - Fill other required fields

2. Check Supabase:
   - Go to **Table Editor** → **profiles**
   - Find the new user
   - Verify `user_type` = **'farmer'**

3. Log in and verify:
   - Should see **Farmer Dashboard** 🚜
   - Check console: `user_type: "farmer"`

### **Test 2: Register New Buyer**

1. Register with:
   - User Type: **Buyer**
   - Email: `testbuyer@example.com`
   - Fill other required fields

2. Check Supabase:
   - Go to **Table Editor** → **profiles**
   - Find the new user
   - Verify `user_type` = **'buyer'**

3. Log in and verify:
   - Should see **Buyer Dashboard** 🛒
   - Check console: `user_type: "buyer"`

---

## 📊 Checking User Types in Database:

### **View All Users by Type:**

Run this query in Supabase SQL Editor:

```sql
SELECT 
  email,
  user_type,
  full_name,
  county,
  created_at
FROM public.profiles
ORDER BY user_type, created_at DESC;
```

### **Count Farmers vs Buyers:**

```sql
SELECT 
  user_type,
  COUNT(*) as total_users
FROM public.profiles
GROUP BY user_type;
```

Expected result:
```
user_type | total_users
----------|------------
farmer    | 5
buyer     | 3
```

### **Fix Wrong User Type:**

If a user has the wrong type, update it:

```sql
UPDATE public.profiles
SET user_type = 'farmer'  -- or 'buyer'
WHERE email = 'user@example.com';
```

---

## 🎯 Dashboard Routing Logic:

The app uses this logic to determine which dashboard to show:

```javascript
// In AuthContext
isFarmer: profile?.user_type === 'farmer'
isBuyer: profile?.user_type === 'buyer'

// In RootNavigator
{() => (isFarmer ? <FarmerTabs /> : <BuyerTabs />)}
```

**Key Points:**
- ✅ `user_type` **MUST** be set correctly during registration
- ✅ Database trigger should automatically set it from metadata
- ✅ Profile fetch should return the correct `user_type`
- ✅ Dashboard routing checks `profile.user_type`

---

## 🔧 Troubleshooting:

### **Issue 1: User Type Not Set**

**Symptom:** Profile exists but `user_type` is NULL

**Solution:**
```sql
-- Check if trigger exists
SELECT * FROM pg_trigger 
WHERE tgname = 'on_auth_user_created';

-- If missing, re-run the setup SQL script
```

### **Issue 2: Wrong Dashboard After Login**

**Debug Steps:**
1. Check browser console for: `📋 Profile loaded: { user_type: "..." }`
2. Verify in Supabase Table Editor: What is the actual `user_type`?
3. If mismatch:
   ```sql
   UPDATE profiles SET user_type = 'farmer' WHERE email = 'user@example.com';
   ```

### **Issue 3: Duplicate Users**

**Symptom:** "duplicate key value violates unique constraint"

**Solution:**
```sql
-- Delete duplicate profile
DELETE FROM profiles WHERE id = 'user-uuid';

-- User can now re-register
```

---

## ✅ Final Checklist:

Before testing registration:

- [ ] Run the updated `SUPABASE_DATABASE_SETUP.sql` in Supabase SQL Editor
- [ ] Verify `profiles` table has all the new fields
- [ ] Confirm trigger `on_auth_user_created` exists
- [ ] Check RLS policies are enabled
- [ ] Restart Expo app: `npx expo start --clear --web`
- [ ] Open browser console (F12) to see logs
- [ ] Test register as farmer
- [ ] Test register as buyer
- [ ] Verify each goes to correct dashboard

---

## 📝 What Happens Now:

1. **Register as Farmer** → `user_type: 'farmer'` → Farmer Dashboard 🚜
2. **Register as Buyer** → `user_type: 'buyer'` → Buyer Dashboard 🛒
3. **Database stores user_type** correctly
4. **Login checks user_type** and routes accordingly
5. **Can extend with more fields** per user type in future

---

Ready to test! Run the updated SQL script in Supabase, restart your app, and try registering both types of users. 🚀
