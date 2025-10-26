# AgroShield Database Integration Guide

## Overview
This guide explains how to integrate the complete database schema with your AgroShield backend API for storing predictions, user data, and marketplace information.

## 📋 Table of Contents
1. [Database Setup](#database-setup)
2. [Backend Integration](#backend-integration)
3. [API Endpoints for Data Storage](#api-endpoints)
4. [Prediction Storage Flow](#prediction-storage-flow)
5. [Testing](#testing)

---

## 🗄️ Database Setup

### Step 1: Run the SQL Script

1. **Open Supabase Dashboard**
   - Go to: https://supabase.com/dashboard
   - Select your project: `rwspbvgmmxabglptljkg`

2. **Execute the Schema**
   - Navigate to: SQL Editor (left sidebar)
   - Create new query
   - Copy entire content from `COMPLETE_DATABASE_SCHEMA.sql`
   - Click "Run" or press `Ctrl+Enter`

3. **Verify Creation**
   ```sql
   -- Check all tables
   SELECT table_name 
   FROM information_schema.tables 
   WHERE table_schema = 'public' 
   ORDER BY table_name;
   
   -- Should show:
   -- climate_predictions
   -- crop_listings
   -- disease_predictions
   -- farm_intelligence_reports
   -- notifications
   -- orders
   -- pest_predictions
   -- profiles
   -- ratings_reviews
   -- storage_predictions
   ```

### Step 2: Verify RLS Policies

```sql
-- Check policies are active
SELECT tablename, policyname, cmd 
FROM pg_policies 
WHERE schemaname = 'public';
```

---

## 🔌 Backend Integration

### Update Backend Requirements

Add Supabase client to your backend:

```bash
cd backend
pip install supabase
```

### Create Supabase Client in Backend

**File: `backend/app/config/supabase.py`**

```python
import os
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://rwspbvgmmxabglptljkg.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "your-service-role-key-here")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_supabase_client():
    """Get Supabase client instance"""
    return supabase
```

**⚠️ Important:** Use the **Service Role Key** (not anon key) for backend operations. Find it in:
- Supabase Dashboard → Settings → API → Service Role Key

---

## 🔗 API Endpoints for Data Storage

### 1. Pest Prediction Storage

**File: `backend/app/routes/pest_detection.py`**

```python
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.config.supabase import get_supabase_client
import uuid
from datetime import datetime

router = APIRouter()

@router.post("/api/pest-detection")
async def detect_pest(
    image: UploadFile = File(...),
    farmer_id: str = None,
    crop_type: str = None,
    location: str = None,
    latitude: float = None,
    longitude: float = None
):
    supabase = get_supabase_client()
    
    try:
        # 1. Upload image to Supabase Storage
        file_ext = image.filename.split('.')[-1]
        file_name = f"pest_{uuid.uuid4()}.{file_ext}"
        file_path = f"pest_images/{file_name}"
        
        image_bytes = await image.read()
        
        storage_response = supabase.storage.from_('predictions').upload(
            path=file_path,
            file=image_bytes,
            file_options={"content-type": image.content_type}
        )
        
        # Get public URL
        image_url = supabase.storage.from_('predictions').get_public_url(file_path)
        
        # 2. Run AI prediction
        prediction_result = await run_pest_detection_model(image_bytes)
        
        # 3. Store prediction in database
        prediction_data = {
            "id": str(uuid.uuid4()),
            "farmer_id": farmer_id,
            "image_url": image_url,
            "image_metadata": {
                "original_filename": image.filename,
                "size": len(image_bytes),
                "content_type": image.content_type
            },
            "pest_detected": prediction_result['pest_name'],
            "confidence_score": prediction_result['confidence'],
            "severity": calculate_severity(prediction_result['confidence']),
            "alternative_predictions": prediction_result.get('alternatives', []),
            "treatment_recommendations": get_treatment_recommendations(
                prediction_result['pest_name']
            ),
            "preventive_measures": get_preventive_measures(
                prediction_result['pest_name']
            ),
            "crop_affected": crop_type,
            "farm_location": location,
            "latitude": latitude,
            "longitude": longitude,
            "created_at": datetime.utcnow().isoformat()
        }
        
        db_response = supabase.table('pest_predictions').insert(prediction_data).execute()
        
        return {
            "success": True,
            "prediction": prediction_result,
            "prediction_id": prediction_data['id'],
            "image_url": image_url,
            "recommendations": {
                "treatments": prediction_data['treatment_recommendations'],
                "prevention": prediction_data['preventive_measures']
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def calculate_severity(confidence: float) -> str:
    """Calculate severity based on confidence"""
    if confidence >= 0.9:
        return "critical"
    elif confidence >= 0.75:
        return "high"
    elif confidence >= 0.5:
        return "moderate"
    else:
        return "low"

def get_treatment_recommendations(pest_name: str) -> list:
    """Get treatment recommendations for detected pest"""
    treatments = {
        "aphids": [
            "Apply neem oil spray (5ml per liter of water)",
            "Introduce natural predators like ladybugs",
            "Use insecticidal soap spray",
            "Remove heavily infested plant parts"
        ],
        "whiteflies": [
            "Apply yellow sticky traps",
            "Spray with neem oil solution",
            "Use reflective mulch to deter whiteflies",
            "Introduce parasitic wasps"
        ],
        # Add more pests...
    }
    return treatments.get(pest_name.lower(), ["Consult agricultural extension officer"])

def get_preventive_measures(pest_name: str) -> list:
    """Get preventive measures"""
    return [
        "Regular crop monitoring and inspection",
        "Maintain field hygiene by removing plant debris",
        "Practice crop rotation",
        "Use resistant crop varieties",
        "Implement integrated pest management (IPM)"
    ]

async def run_pest_detection_model(image_bytes: bytes):
    """Run your AI model - integrate your existing model here"""
    # This is where you integrate your TensorFlow/PyTorch model
    # Return format: {"pest_name": "Aphids", "confidence": 0.95, "alternatives": [...]}
    pass
```

### 2. Disease Prediction Storage

**File: `backend/app/routes/disease_detection.py`**

```python
@router.post("/api/disease-detection")
async def detect_disease(
    image: UploadFile = File(...),
    farmer_id: str = None,
    crop_type: str = None,
    growth_stage: str = None,
    weather_temp: float = None,
    weather_humidity: float = None
):
    supabase = get_supabase_client()
    
    try:
        # Similar structure to pest detection
        file_path = f"disease_images/{uuid.uuid4()}.{image.filename.split('.')[-1]}"
        image_bytes = await image.read()
        
        # Upload image
        supabase.storage.from_('predictions').upload(file_path, image_bytes)
        image_url = supabase.storage.from_('predictions').get_public_url(file_path)
        
        # Run disease detection model
        prediction = await run_disease_detection_model(image_bytes)
        
        # Store in database
        disease_data = {
            "id": str(uuid.uuid4()),
            "farmer_id": farmer_id,
            "image_url": image_url,
            "disease_detected": prediction['disease_name'],
            "confidence_score": prediction['confidence'],
            "severity": calculate_severity(prediction['confidence']),
            "crop_affected": crop_type,
            "growth_stage": growth_stage,
            "weather_conditions": {
                "temperature": weather_temp,
                "humidity": weather_humidity
            },
            "treatment_recommendations": get_disease_treatments(prediction['disease_name']),
            "preventive_measures": get_disease_prevention(prediction['disease_name']),
            "contagion_risk": calculate_contagion_risk(prediction['disease_name']),
            "created_at": datetime.utcnow().isoformat()
        }
        
        supabase.table('disease_predictions').insert(disease_data).execute()
        
        return {
            "success": True,
            "prediction": prediction,
            "disease_id": disease_data['id'],
            "recommendations": disease_data['treatment_recommendations']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 3. Storage Condition Assessment

**File: `backend/app/routes/storage_assessment.py`**

```python
@router.post("/api/storage-assessment")
async def assess_storage(
    image: UploadFile = File(...),
    farmer_id: str = None,
    crop_stored: str = None,
    storage_type: str = None,
    storage_duration: int = None,
    quantity: float = None,
    temperature: float = None,
    humidity: float = None
):
    supabase = get_supabase_client()
    
    try:
        # Upload image
        file_path = f"storage_images/{uuid.uuid4()}.{image.filename.split('.')[-1]}"
        image_bytes = await image.read()
        
        supabase.storage.from_('predictions').upload(file_path, image_bytes)
        image_url = supabase.storage.from_('predictions').get_public_url(file_path)
        
        # Run storage assessment model
        assessment = await run_storage_assessment_model(image_bytes)
        
        # Calculate predictions
        shelf_life = calculate_shelf_life(
            assessment['condition'], 
            storage_type, 
            crop_stored
        )
        
        # Store in database
        storage_data = {
            "id": str(uuid.uuid4()),
            "farmer_id": farmer_id,
            "image_url": image_url,
            "storage_condition": assessment['condition'],
            "confidence_score": assessment['confidence'],
            "issues_detected": assessment.get('issues', []),
            "risk_level": assessment['risk_level'],
            "estimated_shelf_life": shelf_life,
            "spoilage_risk_percentage": calculate_spoilage_risk(assessment),
            "immediate_actions": get_immediate_actions(assessment['issues']),
            "improvements_needed": get_improvements(assessment),
            "crop_stored": crop_stored,
            "storage_type": storage_type,
            "storage_duration": storage_duration,
            "quantity_stored": quantity,
            "temperature": temperature,
            "humidity": humidity,
            "created_at": datetime.utcnow().isoformat()
        }
        
        supabase.table('storage_predictions').insert(storage_data).execute()
        
        return {
            "success": True,
            "assessment": assessment,
            "storage_id": storage_data['id'],
            "shelf_life_days": shelf_life,
            "actions_needed": storage_data['immediate_actions']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 4. User Profile Management

**File: `backend/app/routes/profiles.py`**

```python
@router.get("/api/profile/{user_id}")
async def get_profile(user_id: str):
    supabase = get_supabase_client()
    
    response = supabase.table('profiles').select("*").eq('id', user_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return response.data[0]

@router.put("/api/profile/{user_id}")
async def update_profile(user_id: str, profile_data: dict):
    supabase = get_supabase_client()
    
    response = supabase.table('profiles').update(profile_data).eq('id', user_id).execute()
    
    return {"success": True, "profile": response.data[0]}

@router.get("/api/farmer-stats/{farmer_id}")
async def get_farmer_statistics(farmer_id: str):
    supabase = get_supabase_client()
    
    # Use the database function we created
    response = supabase.rpc('get_farmer_stats', {'farmer_id': farmer_id}).execute()
    
    return response.data[0] if response.data else {}
```

### 5. Marketplace Listings

**File: `backend/app/routes/marketplace.py`**

```python
@router.post("/api/listings")
async def create_listing(
    farmer_id: str,
    crop_name: str,
    quantity: float,
    price_per_unit: float,
    quality_grade: str = None,
    is_organic: bool = False,
    available_from: str = None,
    images: list = None
):
    supabase = get_supabase_client()
    
    listing_data = {
        "id": str(uuid.uuid4()),
        "farmer_id": farmer_id,
        "crop_name": crop_name,
        "quantity": quantity,
        "price_per_unit": price_per_unit,
        "quality_grade": quality_grade,
        "is_organic": is_organic,
        "available_from": available_from,
        "images": images,
        "status": "available",
        "created_at": datetime.utcnow().isoformat()
    }
    
    response = supabase.table('crop_listings').insert(listing_data).execute()
    
    return {"success": True, "listing": response.data[0]}

@router.get("/api/listings")
async def get_listings(
    crop_name: str = None,
    status: str = "available",
    limit: int = 50
):
    supabase = get_supabase_client()
    
    query = supabase.table('crop_listings').select("*, profiles(*)")
    
    if crop_name:
        query = query.eq('crop_name', crop_name)
    
    query = query.eq('status', status).limit(limit)
    
    response = query.execute()
    
    return {"listings": response.data}
```

---

## 📊 Prediction Storage Flow

### Complete Flow for Image Upload → Prediction → Storage

```
1. Frontend (React Native)
   ↓ Upload image with metadata
   
2. Backend API (/api/pest-detection)
   ↓ Receive image
   
3. Supabase Storage
   ↓ Store image → Get public URL
   
4. AI Model
   ↓ Run prediction on image
   
5. Database (pest_predictions table)
   ↓ Store: image_url, prediction, confidence, recommendations
   
6. Response to Frontend
   ↓ Return: prediction + recommendations + image_url
   
7. Display to User
   ✓ Show prediction with visual feedback
```

### Example Complete Request/Response

**Request:**
```bash
POST https://urchin-app-86rjy.ondigitalocean.app/api/pest-detection
Content-Type: multipart/form-data

image: [binary data]
farmer_id: "550e8400-e29b-41d4-a716-446655440000"
crop_type: "Tomatoes"
location: "Nairobi, Kenya"
latitude: -1.286389
longitude: 36.817223
```

**Response:**
```json
{
  "success": true,
  "prediction": {
    "pest_name": "Aphids",
    "confidence": 0.94,
    "alternatives": [
      {"pest": "Whiteflies", "confidence": 0.05},
      {"pest": "Thrips", "confidence": 0.01}
    ]
  },
  "prediction_id": "123e4567-e89b-12d3-a456-426614174000",
  "image_url": "https://rwspbvgmmxabglptljkg.supabase.co/storage/v1/object/public/predictions/pest_images/pest_123.jpg",
  "recommendations": {
    "treatments": [
      "Apply neem oil spray (5ml per liter of water)",
      "Introduce natural predators like ladybugs",
      "Use insecticidal soap spray"
    ],
    "prevention": [
      "Regular crop monitoring and inspection",
      "Maintain field hygiene",
      "Practice crop rotation"
    ]
  }
}
```

---

## 🧪 Testing

### 1. Test Database Connection

```python
# backend/test_db_connection.py
from app.config.supabase import get_supabase_client

def test_connection():
    supabase = get_supabase_client()
    
    # Test query
    response = supabase.table('profiles').select("*").limit(1).execute()
    
    print("✓ Database connected successfully!")
    print(f"  Found {len(response.data)} profiles")

if __name__ == "__main__":
    test_connection()
```

### 2. Test Image Upload

```python
def test_image_upload():
    supabase = get_supabase_client()
    
    # Upload test image
    with open("test_image.jpg", "rb") as f:
        response = supabase.storage.from_('predictions').upload(
            'test/test.jpg',
            f,
            {"content-type": "image/jpeg"}
        )
    
    url = supabase.storage.from_('predictions').get_public_url('test/test.jpg')
    print(f"✓ Image uploaded: {url}")
```

### 3. Test Prediction Storage

```python
def test_prediction_storage():
    supabase = get_supabase_client()
    
    test_data = {
        "id": str(uuid.uuid4()),
        "farmer_id": "test-farmer-id",
        "image_url": "https://example.com/test.jpg",
        "pest_detected": "Test Pest",
        "confidence_score": 0.95,
        "severity": "high"
    }
    
    response = supabase.table('pest_predictions').insert(test_data).execute()
    print(f"✓ Prediction stored: {response.data[0]['id']}")
```

---

## 🔐 Setup Supabase Storage Bucket

1. **Create Storage Bucket**
   - Go to: Supabase Dashboard → Storage
   - Click: "New bucket"
   - Name: `predictions`
   - Public: ✓ Make public
   - Click: "Create bucket"

2. **Set Storage Policies**
   ```sql
   -- Allow authenticated users to upload
   CREATE POLICY "Authenticated users can upload"
   ON storage.objects FOR INSERT
   TO authenticated
   WITH CHECK (bucket_id = 'predictions');
   
   -- Allow public read access
   CREATE POLICY "Public read access"
   ON storage.objects FOR SELECT
   TO public
   USING (bucket_id = 'predictions');
   ```

---

## 📝 Environment Variables

Add to your backend `.env` file:

```env
# Supabase Configuration
SUPABASE_URL=https://rwspbvgmmxabglptljkg.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...(service-role-key)

# API Configuration
API_BASE_URL=https://urchin-app-86rjy.ondigitalocean.app
```

**⚠️ Security Note:** 
- Use **Service Role Key** in backend (has admin privileges)
- Use **Anon Key** in frontend (restricted by RLS policies)

---

## 🚀 Deployment Checklist

- [ ] Run `COMPLETE_DATABASE_SCHEMA.sql` in Supabase
- [ ] Create `predictions` storage bucket
- [ ] Set storage policies for uploads
- [ ] Add Supabase credentials to backend `.env`
- [ ] Install `supabase` Python package in backend
- [ ] Update backend routes to use Supabase client
- [ ] Test image upload functionality
- [ ] Test prediction storage
- [ ] Verify RLS policies work correctly
- [ ] Test frontend → backend → database flow

---

## 📚 Additional Resources

- **Supabase Python Docs:** https://supabase.com/docs/reference/python
- **Storage API:** https://supabase.com/docs/guides/storage
- **Row Level Security:** https://supabase.com/docs/guides/auth/row-level-security
- **PostgREST API:** https://postgrest.org/en/stable/

---

## 🆘 Troubleshooting

### Issue: "relation 'profiles' does not exist"
**Solution:** Run the complete SQL schema script first

### Issue: "permission denied for table"
**Solution:** Check RLS policies are correctly set up

### Issue: "storage bucket not found"
**Solution:** Create the `predictions` bucket in Supabase Storage

### Issue: "invalid input syntax for type uuid"
**Solution:** Ensure you're passing string UUIDs, not integers

---

## ✅ Next Steps

1. **Run the SQL script** in Supabase
2. **Create storage bucket** for images
3. **Update backend** with Supabase integration code
4. **Test endpoints** with Postman/Thunder Client
5. **Connect frontend** to new endpoints
6. **Deploy to DigitalOcean** with new environment variables

Your database is now ready to store all predictions, user data, and marketplace information! 🎉
